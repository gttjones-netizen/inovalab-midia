"""Cura do concreto — zoom contínuo real (mundo único em mm, detalhes aparecem por escala)."""
import math, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cura as C
from cura import (W0, H0, OUTW, OUTH, FPS, clamp, sm, ease, eout, lerp, tb, B, VD, checker,
                  ptext, tag, counter, brackets, YEL, WHITE, PIX)

def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

# ---------------- world (mm). P = (0,0) is the zoom target ----------------
SLAB_T, SLAB_B = -48.0, 72.0
BARS = [(x, y) for x in range(-450, 451, 100) for y in (-18.0, 42.0)]
BAR_R = 5.0
UM = 1e-3; NM = 1e-6
GR_R = 16 * UM                        # special cement grain G* (its surface touches P)
GSTAR = (-GR_R, 0.0)
CSH_H = 1.4 * NM                      # C-S-H layer spacing

def hrng(*k): return random.Random(hash(k) & 0xffffffff)

# rocks (brita) precomputed
def make_rocks():
    r = random.Random(17); rocks = []
    for _ in range(6000):
        if len(rocks) >= 140: break
        R = r.uniform(5, 11)
        x = r.uniform(-420, 420); y = r.uniform(SLAB_T + R + 2, SLAB_B - R - 2)
        if math.hypot(x, y) < R + 7: continue
        if any(math.hypot(x - bx, y - by) < R + BAR_R + 2 for bx, by in BARS): continue
        if any(math.hypot(x - a, y - b) < R + rb + 1.5 for a, b, rb, _ in rocks): continue
        n = r.randint(7, 9)
        prof = [(i / n * 2 * math.pi + r.uniform(-0.2, 0.2), r.uniform(0.72, 1.05)) for i in range(n)]
        rocks.append((x, y, R, prof))
    return rocks
ROCKS = make_rocks()

def in_rock(x, y, pad=0.0):
    for a, b, R, _ in ROCKS:
        if abs(x - a) < R + pad and abs(y - b) < R + pad and math.hypot(x - a, y - b) < R * 0.9 + pad: return True
    return False

SAND_CELL = 2.6
def sand_in_cell(i, j):
    r = hrng('s', i, j); out = []
    for _ in range(1 if r.random() < 0.6 else 0):
        R = r.uniform(0.3, 1.1)
        x = (i + r.uniform(0.15, 0.85)) * SAND_CELL; y = (j + r.uniform(0.15, 0.85)) * SAND_CELL
        if math.hypot(x, y) < R + 0.5: continue
        if not (SLAB_T + R < y < SLAB_B - R): continue
        n = 7; prof = [(k / n * 2 * math.pi, r.uniform(0.8, 1.05)) for k in range(n)]
        out.append((x, y, R, prof))
    return out

CEM_CELL = 0.04
def cem_raw(i, j):
    r = hrng('c', i, j)
    if r.random() < 0.15: return None
    R = r.uniform(5, 13) * UM
    x = (i + r.uniform(0.25, 0.75)) * CEM_CELL; y = (j + r.uniform(0.25, 0.75)) * CEM_CELL
    n = 9; prof = [(k / n * 2 * math.pi + r.uniform(-0.15, 0.15), r.uniform(0.82, 1.06)) for k in range(n)]
    return (x, y, R, prof, r.random())
_CC = {}
def cem_in_cell(i, j):
    if (i, j) in _CC: return _CC[(i, j)]
    g = cem_raw(i, j); out = []
    if g:
        x, y, R = g[0], g[1], g[2]
        ok = math.hypot(x - GSTAR[0], y - GSTAR[1]) > R + GR_R + 12 * UM
        for di, dj in ((-1, 0), (0, -1), (-1, -1), (1, -1)):
            h = cem_raw(i + di, j + dj)
            if h and math.hypot(x - h[0], y - h[1]) < R + h[2] + 2 * UM: ok = False
        if ok: out.append(g)
    if len(_CC) > 200000: _CC.clear()
    _CC[(i, j)] = out
    return out

WAT_CELL = 0.9 * NM
def wat_in_cell(i, j):
    r = hrng('w', i, j)
    if r.random() < 0.55: return []
    return [((i + r.uniform(0.2, 0.8)) * WAT_CELL, (j + r.uniform(0.2, 0.8)) * WAT_CELL, r.uniform(0, 6.28))]

# ---------------- state over time ----------------
def state(t):
    return dict(
        wet=1.0 - 0.8 * sm(t, tb(11), tb(13)),
        ett=ease(sm(t, tb(17.5), tb(21))),
        csh=ease(sm(t, tb(20), tb(27))),
        port=sm(t, tb(23.5), tb(27)),
        hyd=sm(t, tb(18), tb(37)),
        pore=sm(t, tb(25), tb(37)),
        dense=sm(t, tb(28), tb(37)),
    )

# ---------------- camera timeline: log10(scale px/mm) ----------------
S0 = 0.6
LZ = [(4, math.log10(S0)), (8, 0.7), (12, 0.85), (17, 3.15), (27, 3.42), (32, 7.25), (37, 7.32), (45, math.log10(S0))]
def logs(t):
    b = (t - C.OFF) / B
    if b <= LZ[0][0]: return LZ[0][1]
    for (b0, z0), (b1, z1) in zip(LZ, LZ[1:]):
        if b0 <= b <= b1:
            k = (b - b0) / (b1 - b0)
            if abs(z1 - z0) > 0.5:
                k = k * k * (3 - 2 * k) * 0.5 + k * 0.5
            return z0 + (z1 - z0) * k
    return LZ[-1][1]


# ---------------- vectorized procedural layers (no popping) ----------------
M32 = np.uint64(0xffffffff)
def vh(i, j, salt):
    h = (i.astype(np.uint64) * np.uint64(0x9E3779B1)) ^ (j.astype(np.uint64) * np.uint64(0x85EBCA77)) ^ np.uint64(salt * 0x27D4EB2F)
    h &= M32
    h ^= h >> np.uint64(15); h = (h * np.uint64(0x2C1B3C6D)) & M32
    h ^= h >> np.uint64(12); h = (h * np.uint64(0x297A2D39)) & M32
    h ^= h >> np.uint64(15)
    return h.astype(np.float64) / 4294967296.0

def cells(vx0, vx1, vy0, vy1, cell, pad=1, maxn=900000):
    i0, i1 = int(math.floor(vx0 / cell)) - pad, int(math.floor(vx1 / cell)) + pad
    j0, j1 = int(math.floor(vy0 / cell)) - pad, int(math.floor(vy1 / cell)) + pad
    if (i1 - i0 + 1) * (j1 - j0 + 1) > maxn: return None
    I, J = np.meshgrid(np.arange(i0, i1 + 1, dtype=np.int64), np.arange(j0, j1 + 1, dtype=np.int64))
    return I.ravel(), J.ravel()

def gen_sand(I, J):
    u0, u1, u2, u3, u4 = (vh(I, J, k) for k in (11, 12, 13, 14, 15))
    R = 0.3 + 0.8 * u1
    x = (I + 0.15 + 0.7 * u2) * SAND_CELL; y = (J + 0.15 + 0.7 * u3) * SAND_CELL
    ok = (u0 < 0.6) & (np.hypot(x, y) > R + 0.5) & (y > SLAB_T + R) & (y < SLAB_B - R)
    return x[ok], y[ok], R[ok], u4[ok]

def cem_raw_v(I, J):
    u0, u1, u2, u3, u4 = (vh(I, J, k) for k in (21, 22, 23, 24, 25))
    R = (5 + 8 * u1) * UM
    x = (I + 0.25 + 0.5 * u2) * CEM_CELL; y = (J + 0.25 + 0.5 * u3) * CEM_CELL
    return u0 >= 0.15, x, y, R, u4

def gen_cem(I, J):
    p, x, y, R, sd = cem_raw_v(I, J)
    ok = p & (np.hypot(x - GSTAR[0], y - GSTAR[1]) > R + GR_R + 12 * UM) & (y > SLAB_T) & (y < SLAB_B)
    for di, dj in ((-1, 0), (0, -1), (-1, -1), (1, -1)):
        pn, xn, yn, Rn, _ = cem_raw_v(I + di, J + dj)
        ok &= ~(pn & (np.hypot(x - xn, y - yn) < R + Rn + 2 * UM))
    return x[ok], y[ok], R[ok], sd[ok]

def gen_wat(I, J):
    u0, u1, u2, u3 = (vh(I, J, k) for k in (31, 32, 33, 34))
    x = (I + 0.2 + 0.6 * u1) * WAT_CELL; y = (J + 0.2 + 0.6 * u2) * WAT_CELL
    ok = u0 >= 0.55
    return x[ok], y[ok], u3[ok] * 6.28

def specks(arr, sx, sy, rp, col, fade=1.0):
    """sub-pixel objects: accumulate covered area per pixel and blend"""
    m = (sx >= 0) & (sx < W0) & (sy >= 0) & (sy < H0)
    if not m.any(): return
    px = sx[m].astype(np.int64); py = sy[m].astype(np.int64)
    a = np.minimum(1.0, math.pi * rp[m] ** 2) * fade
    cov = np.zeros((H0, W0))
    np.add.at(cov, (py, px), a)
    cov = np.minimum(cov, 1.0)[..., None]
    arr[:] = arr * (1 - cov) + np.array(col, np.float64) * cov

def prof_of(seed, n=9, lo=0.82, hi=1.06):
    r = random.Random(int(seed * 1e9))
    return [(k / n * 2 * math.pi + r.uniform(-0.15, 0.15), r.uniform(lo, hi)) for k in range(n)]

# ---------------- renderer ----------------
_gr = random.Random(8)
GSTAR_PROF = []
for k in range(120):
    a = k / 120 * 2 * math.pi
    a2 = (a + math.pi) % (2 * math.pi) - math.pi
    q = 1.0 if abs(a2) < 0.45 else 1.0 + 0.07 * math.sin(a * 5 + 1) + 0.04 * math.sin(a * 11)
    GSTAR_PROF.append((a, q))
STAR_R = random.Random(21)
STARS = [(STAR_R.uniform(0, W0), STAR_R.uniform(0, H0)) for _ in range(30)]

def render(t, s, st, cx=0.0, cy=0.0):
    img = Image.new('RGB', (W0, H0), (14, 24, 46))
    d = ImageDraw.Draw(img)
    def S(x, y): return ((x - cx) * s + W0 / 2, (y - cy) * s + H0 / 2)
    vx0, vx1 = cx - W0 / 2 / s, cx + W0 / 2 / s
    vy0, vy1 = cy - H0 / 2 / s, cy + H0 / 2 / s
    for i, (x, y) in enumerate(STARS):
        if (i + int(t * 2)) % 7: d.rectangle([x, y, x + 1, y + 1], fill=(200, 210, 230))
    # background = average colour of everything still too small to see
    kc = clamp((0.009 * s - 0.25) / 3.0)
    mixc = mix((182, 176, 166), (204, 202, 198), st['dense'])
    paste = mix((172, 168, 160), (200, 198, 192), st['dense'])
    pore = mix((56, 132, 226), (178, 170, 160), st['pore'])
    ks = clamp((0.6 * s - 0.3) / 3.0)
    bg = mix(mix(mixc, paste, ks), pore, kc)
    bg2 = tuple(max(0, v - 12) for v in bg)
    sy0 = S(0, SLAB_T)[1]; sy1 = S(0, SLAB_B)[1]
    slab_vis = sy1 > 0 and sy0 < H0
    if slab_vis:
        m = Image.new('L', (W0, H0), 0)
        ImageDraw.Draw(m).rectangle([0, max(-5, sy0), W0, min(H0 + 5, sy1)], fill=255)
        img.paste(checker(bg, bg2, W0, H0), (0, 0), m)
        if -5 < sy0 < H0: d.line([(0, sy0), (W0, sy0)], fill=mix(bg, (255, 255, 255), 0.35))
        fy0, fy1 = sy1, S(0, SLAB_B + 16)[1]
        if fy0 < H0:
            m2 = Image.new('L', (W0, H0), 0); ImageDraw.Draw(m2).rectangle([0, fy0, W0, fy1], fill=255)
            img.paste(checker(C.WOOD1, C.WOOD2, W0, H0), (0, 0), m2)
            d.line([(0, fy1), (W0, fy1)], fill=C.WOODO)
            for px in (-120.0, 380.0):
                a = S(px - 9, SLAB_B + 16); b2 = S(px + 9, SLAB_B + 600)
                if a[1] < H0 and b2[0] > 0 and a[0] < W0:
                    m3 = Image.new('L', (W0, H0), 0); ImageDraw.Draw(m3).rectangle([a[0], a[1], b2[0], b2[1]], fill=255)
                    img.paste(C.hatch(C.GLS1, C.GLS2, W0, H0), (0, 0), m3)
                    d.rectangle([a[0], a[1], b2[0], b2[1]], outline=C.GLSO)

    def poly(sxc, syc, rp, prof, fill, outline=None, hl=False, dith=None, k=1.0):
        if sxc + rp * 1.1 < 0 or sxc - rp * 1.1 > W0 or syc + rp * 1.1 < 0 or syc - rp * 1.1 > H0: return
        f = mix(bg, fill, k)
        pts = [(sxc + rp * q * math.cos(a), syc + rp * q * math.sin(a)) for a, q in prof]
        if dith and rp > 10:
            mm = Image.new('L', (W0, H0), 0); ImageDraw.Draw(mm).polygon(pts, fill=255)
            img.paste(checker(f, mix(f, dith, k), W0, H0), (0, 0), mm)
            if outline: d.polygon(pts, outline=outline)
        else:
            d.polygon(pts, fill=f, outline=(mix(f, outline, clamp((rp - 2) / 3)) if outline else None))
        if hl and rp > 5:
            d.arc([sxc - rp * 0.6, syc - rp * 0.6, sxc + rp * 0.6, syc + rp * 0.6], 195, 250,
                  fill=mix(f, (255, 255, 255), clamp((rp - 5) / 4)), width=max(1, int(rp / 9)))

    def layer_objects(xs, ys, Rs, seeds, fill, outline, dith, hl, rim=None, fade=1.0, nprof=9):
        """draw a population at any size: specks (<1px) -> dots -> shapes. Never pops."""
        if len(xs) == 0: return
        sx = (xs - cx) * s + W0 / 2; sy = (ys - cy) * s + H0 / 2; rp = Rs * s
        small = rp < 0.75
        if small.any():
            arr = np.asarray(img).astype(np.float64)
            specks(arr, sx[small], sy[small], rp[small], fill, fade)
            img.paste(Image.fromarray(arr.astype(np.uint8)))
        mid = (~small) & (rp < 2.2) & (sx > -3) & (sx < W0 + 3) & (sy > -3) & (sy < H0 + 3)
        for x, y, r_ in zip(sx[mid], sy[mid], rp[mid]):
            k = clamp(0.55 + (r_ - 0.75) / 3) * fade
            d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=mix(bg, fill, k))
        big = (rp >= 2.2) & (sx + rp > -2) & (sx - rp < W0 + 2) & (sy + rp > -2) & (sy - rp < H0 + 2)
        for x, y, r_, sd in zip(sx[big], sy[big], rp[big], seeds[big]):
            pr = prof_of(sd, nprof)
            if rim is not None and rim[0] > 0:
                poly(x, y, r_, pr, rim[1], rim[2], k=fade)
                r_ = r_ * (1 - 0.3 * rim[0])
            poly(x, y, r_, pr, fill, outline, hl=hl, dith=dith, k=fade * clamp(0.85 + (r_ - 2.2) / 6))

    # ---------- molecular water (around P) ----------
    hpx = CSH_H * s
    csh_len = 12 * UM * st['csh']
    band = (0.0, -3 * UM, csh_len, 3 * UM)
    if 0.14 * NM * s > 0.05:
        cc = cells(vx0, vx1, vy0, vy1, WAT_CELL)
        if cc is not None:
            x, y, ang = gen_wat(*cc)
            keep = (x > 0) & ~((x < csh_len) & (np.abs(y) < 3 * UM))
            x, y, ang = x[keep], y[keep], ang[keep]
            x = x + 0.08 * NM * np.sin(t * 3 + ang); y = y + 0.08 * NM * np.cos(t * 2.3 + ang)
            rp = 0.14 * NM * s
            fadew = clamp((rp - 0.05) / 0.5)
            if rp < 0.8:
                arr = np.asarray(img).astype(np.float64)
                specks(arr, (x - cx) * s + W0 / 2, (y - cy) * s + H0 / 2, np.full(len(x), rp), (232, 72, 64), fadew)
                img.paste(Image.fromarray(arr.astype(np.uint8)))
            else:
                for xx, yy, aa in zip(x, y, ang):
                    water(d, S(xx, yy), rp, aa + t)
    # ---------- cement level ----------
    if 0.009 * s > 0.03:
        cc = cells(vx0, vx1, vy0, vy1, CEM_CELL)
        fade_c = clamp((0.009 * s - 0.03) / 0.4)
        if cc is not None:
            gx, gy, gR, gs = gen_cem(*cc)
        else:
            gx = gy = gR = gs = np.zeros(0)
        # hydration products, only where grains are resolved
        fade = 1 - clamp((s - 3e4) / 2e5)
        rp_all = gR * s
        sel = rp_all > 2.5
        prods = list(zip(gx[sel], gy[sel], gR[sel], gs[sel])) + [(GSTAR[0], GSTAR[1], GR_R, 0.5)]
        for X, Y, R, sd in prods:
            sxc, syc = S(X, Y); rp = R * s
            if sxc + rp * 3 < 0 or sxc - rp * 3 > W0 or syc + rp * 3 < 0 or syc - rp * 3 > H0: continue
            kk = clamp((rp - 2.5) / 6) * fade
            r = random.Random(int(sd * 1e6))
            if st['csh'] > 0 and kk > 0:
                col = mix(bg, (246, 240, 222), kk)
                for q in range(36):
                    a = q / 36 * 2 * math.pi + r.uniform(-0.06, 0.06)
                    if X == GSTAR[0] and abs(a) < 0.5: continue
                    L = (R + (3 + 9 * r.random()) * UM * st['csh']) * s
                    d.line([(sxc + rp * 0.85 * math.cos(a), syc + rp * 0.85 * math.sin(a)), (sxc + L * math.cos(a), syc + L * math.sin(a))], fill=col)
            if st['ett'] > 0 and kk > 0:
                for q in range(9):
                    a = r.uniform(0, 6.28)
                    if X == GSTAR[0] and abs(a) < 0.5: continue
                    L = (2 + 4 * r.random()) * UM * st['ett'] * s
                    x0, y0 = sxc + rp * math.cos(a), syc + rp * math.sin(a)
                    x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
                    if L > 0.8:
                        d.line([(x0, y0), (x1, y1)], fill=mix(bg, (150, 104, 20), kk), width=3 if L > 3 else 1)
                        d.line([(x0, y0), (x1, y1)], fill=mix(bg, (255, 212, 70), kk), width=1)
            if st['port'] > 0 and kk > 0 and r.random() < 0.5:
                a = r.uniform(0, 6.28); dd = rp + (6 + 4 * r.random()) * UM * s
                px, py = sxc + dd * math.cos(a), syc + dd * math.sin(a)
                ss = 5 * UM * s * eout(st['port'])
                if ss > 1:
                    hexp = [(px + ss * math.cos(k * math.pi / 3), py + ss * math.sin(k * math.pi / 3)) for k in range(6)]
                    d.polygon(hexp, fill=mix(bg, (232, 240, 250), kk), outline=mix(bg, (120, 146, 190), kk))
        # C-S-H bundle at P (fibres -> stripes -> layers -> atoms)
        if csh_len > 0:
            bx0, by0 = S(band[0], band[1]); bx1, by1 = S(band[2], band[3])
            if bx1 > 0 and bx0 < W0 and by1 > 0 and by0 < H0 and (bx1 - bx0) > 0.3:
                cream = (240, 232, 206)
                if hpx < 2.5:
                    ytop, ybot = max(-2, by0), min(H0 + 2, by1)
                    yy = ytop; k = 0
                    while yy <= ybot:
                        yw = cy + (yy - H0 / 2) / s
                        q = int(math.floor(yw / (CSH_H * 4))) if hpx > 0.25 else int(math.floor(yw / (0.25 * UM)))
                        rl = random.Random(q * 7919 + 13)
                        tipf = 0.55 + 0.45 * rl.random()
                        prof_k = 1 - (abs(yw) / (3 * UM)) ** 2
                        L = csh_len * tipf * max(0.2, prof_k)
                        xe = S(L, 0)[0]
                        col = cream if k % 2 == 0 else (214, 204, 176)
                        if xe > bx0: d.line([(max(-2, bx0), yy), (min(W0 + 2, xe), yy)], fill=mix(bg, col, clamp((xe - bx0) / 4)))
                        yy += 1 if hpx < 1.2 else 2
                        k += 1
                else:
                    d.rectangle([max(-2, bx0), max(-2, by0), min(W0 + 2, bx1), min(H0 + 2, by1)], fill=mix((70, 120, 200), (150, 150, 160), st['pore'] * 0.6))
                    layers(d, S, s, t, vy0, vy1, max(0.0, vx0), min(csh_len, vx1), hpx)
        # grains (all sizes)
        layer_objects(gx, gy, gR, gs, (112, 100, 136), (42, 34, 60), (98, 88, 122), True,
                      rim=(st['hyd'], (232, 214, 182), (150, 124, 90)), fade=fade_c)
        # special grain G*
        sxc, syc = S(*GSTAR); rp = GR_R * s
        if rp > 0.3:
            if rp < 2.2:
                d.ellipse([sxc - rp, syc - rp, sxc + rp, syc + rp], fill=mix(bg, (112, 100, 136), fade_c * 0.8))
            else:
                poly(sxc, syc, rp, GSTAR_PROF, (112, 100, 136), (42, 34, 60), hl=True, dith=(98, 88, 122), k=fade_c)
        # atomic lattice inside G*, fading in
        lat = 0.5 * NM; lp = lat * s
        if lp > 1.2:
            ka = clamp((lp - 1.2) / 4)
            xs0 = math.floor(vx0 / lat); xs1 = math.floor(min(0.0, vx1) / lat)
            ys0 = math.floor(vy0 / lat); ys1 = math.floor(vy1 / lat)
            if (xs1 - xs0) * (ys1 - ys0) < 6000:
                for i in range(xs0, xs1 + 1):
                    for j in range(ys0, ys1 + 1):
                        x, y = S(i * lat + (lat / 2 if j % 2 else 0), j * lat)
                        rr = max(0.5, lp * 0.18)
                        c = (140, 128, 170) if (i + j) % 3 else (180, 120, 120)
                        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=mix((112, 100, 136), c, ka))
    # ---------- sand ----------
    if slab_vis:
        cc = cells(vx0, vx1, vy0, vy1, SAND_CELL)
        if cc is not None:
            x, y, R, sd = gen_sand(*cc)
            layer_objects(x, y, R, sd, (244, 200, 92), (150, 108, 40), (232, 186, 80), True, nprof=7)
    # ---------- rocks ----------
    for x, y, R, prof in ROCKS:
        sxc, syc = S(x, y); rp = R * s
        if rp < 0.5: continue
        poly(sxc + 1, syc + 1.5, rp, prof, (86, 78, 74))
        poly(sxc, syc, rp, prof, (146, 158, 182), (66, 74, 98), hl=True, dith=(132, 144, 168))
    # ---------- rebars ----------
    for bx, by in BARS:
        sxc, syc = S(bx, by); rp = BAR_R * s
        if sxc + rp < 0 or sxc - rp > W0 or syc + rp < 0 or syc - rp > H0: continue
        d.ellipse([sxc - rp, syc - rp, sxc + rp, syc + rp], fill=C.REB, outline=C.REBO)
        if rp > 4:
            for q in range(10):
                a = q / 10 * 2 * math.pi
                d.line([(sxc + rp * 0.85 * math.cos(a), syc + rp * 0.85 * math.sin(a)), (sxc + rp * math.cos(a), syc + rp * math.sin(a))], fill=C.REBO)
            d.arc([sxc - rp * 0.6, syc - rp * 0.6, sxc + rp * 0.6, syc + rp * 0.6], 200, 250, fill=C.REBH, width=max(1, int(rp / 6)))
    return img, S

def water(d, p, r, a):
    x, y = p
    if r < 0.8: return
    d.ellipse([x - r, y - r, x + r, y + r], fill=(232, 72, 64), outline=(110, 24, 24))
    for aa in (a, a + 1.82):
        hx, hy = x + r * 1.25 * math.cos(aa), y + r * 1.25 * math.sin(aa)
        rr = r * 0.6
        d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], fill=(245, 245, 250), outline=(120, 120, 140))

def layers(d, S, s, t, vy0, vy1, x0w, x1w, hpx):
    k0 = int(math.floor(vy0 / CSH_H)) - 1; k1 = int(math.floor(vy1 / CSH_H)) + 1
    k0 = max(k0, int(-3 * UM / CSH_H)); k1 = min(k1, int(3 * UM / CSH_H))
    if k1 - k0 > 400: return
    sx0 = S(x0w, 0)[0]; sx1 = S(x1w, 0)[0]
    for k in range(k0, k1 + 1):
        y = k * CSH_H
        ys = S(0, y)[1]
        th = max(1, hpx * 0.18)
        d.rectangle([sx0, ys - th / 2, sx1, ys + th / 2], fill=(250, 214, 96), outline=(150, 110, 30) if th > 2 else None)
        if hpx > 9:
            step = CSH_H * 0.55
            i0 = int(math.floor(x0w / step)); i1 = int(math.floor(x1w / step))
            if i1 - i0 > 300: continue
            tri = hpx * 0.2
            for i in range(i0, i1 + 1):
                xs = S(i * step, 0)[0]
                for sgn in (-1, 1):
                    yb = ys + sgn * th / 2
                    pts = [(xs - tri * 0.55, yb), (xs + tri * 0.55, yb), (xs, yb + sgn * tri)]
                    d.polygon(pts, fill=(70, 150, 240), outline=(24, 60, 130))
                    ox, oy = xs, yb + sgn * tri
                    rr = max(1, tri * 0.18)
                    d.ellipse([ox - rr, oy - rr, ox + rr, oy + rr], fill=(232, 72, 64))
                if i % 2 == 0:
                    rr = max(1, th * 0.45)
                    d.ellipse([xs - rr, ys - rr, xs + rr, ys + rr], fill=(255, 236, 150), outline=(150, 110, 30))
            # interlayer water
            wstep = CSH_H * 1.1
            j0 = int(math.floor(x0w / wstep)); j1 = int(math.floor(x1w / wstep))
            for i in range(j0, j1 + 1):
                xw = i * wstep + 0.3 * CSH_H + 0.05 * CSH_H * math.sin(t * 4 + i + k)
                water(d, S(xw, y + CSH_H * 0.5), 0.12 * NM * s, i * 0.7 + k + t)
        elif hpx > 4:
            d.line([(sx0, ys + hpx * 0.5), (sx1, ys + hpx * 0.5)], fill=(90, 140, 210))

# ---------------- scale bar ----------------
def scale_bar(d, s):
    target = 50 / s  # mm for ~50 px
    units = [(10, '1 cm'), (5, '5 mm'), (1, '1 mm'), (0.5, '0,5 mm'), (0.1, '0,1 mm'), (0.05, '50 µm'), (0.01, '10 µm'), (0.005, '5 µm'),
             (0.001, '1 µm'), (5e-4, '500 nm'), (1e-4, '100 nm'), (5e-5, '50 nm'), (1e-5, '10 nm'), (5e-6, '5 nm'), (1e-6, '1 nm')]
    for v, lab in units:
        if v <= target * 1.6:
            L = v * s
            x0, y0 = 10, 360
            d.rectangle([x0 - 1, y0 - 1, x0 + L + 1, y0 + 3], fill=(0, 0, 0))
            d.rectangle([x0, y0, x0 + L, y0 + 2], fill=WHITE)
            ptext(d, x0, y0 - 14, lab.replace('µ', 'u') if False else lab)
            return

def clock(t):
    b = (t - C.OFF) / B
    seq = [(2, 'HORA 0'), (10.5, 'HORA 1'), (12, 'HORA 2'), (17, 'HORA 6'), (20, 'HORA 12'), (23, 'DIA 1'),
           (26, 'DIA 3'), (31, 'DIA 5'), (37, 'DIA 7'), (40, 'DIA 14'), (43, 'DIA 21'), (45.5, 'DIA 28')]
    lab = None
    for bb, s_ in seq:
        if b >= bb: lab = s_
    return lab

T_ZS = tb(2); T_ZE = tb(49)

def frame(t):
    st = state(t)
    b = (t - C.OFF) / B
    ov = Image.new('RGBA', (W0, H0), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if t < T_ZS:
        k = clamp(t / T_ZS)
        out = C.cam(C.real_scene(t, lerp(0.55, 0.8, k)), 108, 190, 1.3)
    elif t < T_ZE:
        s = 10 ** logs(t)
        out, S = render(t, s, st)
        counter(d, clock(t))
        scale_bar(d, s)
        if b < 4.5:
            brackets(d, 108, 192, int(lerp(30, 14, sm(t, tb(2), tb(4.5)))))
            tag(d, 'CONCRETO', 14, 70, 96, 182, sm(t, tb(2.1), tb(2.6)))
            bx, by = S(100, -18)
            tag(d, 'AÇO', 160, 90, bx, by, sm(t, tb(2.6), tb(3.1)))
        elif 8 <= b < 12.6:
            rk = min(ROCKS, key=lambda r: abs(S(r[0], r[1])[0] - 50) + abs(S(r[0], r[1])[1] - 110))
            p = S(rk[0], rk[1])
            tag(d, 'BRITA', 12, 60, p[0], p[1], sm(t, tb(8.2), tb(8.7)))
            best = None
            sc_ = 10 ** logs(t)
            cc = cells(-W0 / 2 / sc_, W0 / 2 / sc_, -H0 / 2 / sc_, H0 / 2 / sc_, SAND_CELL)
            if cc is not None:
                xs_, ys_, Rs_, _ = gen_sand(*cc)
                for x, y in zip(xs_, ys_):
                    q = S(x, y)
                    if 0 < q[0] < W0 and 0 < q[1] < H0:
                        dd = abs(q[0] - 165) + abs(q[1] - 270)
                        if best is None or dd < best[0]: best = (dd, q)
            if best: tag(d, 'AREIA', 150, 310, best[1][0], best[1][1], sm(t, tb(9), tb(9.5)))
            if b < 11.8: tag(d, 'ÁGUA + CIMENTO', 70, 150, 108, 190, sm(t, tb(10), tb(10.5)))
            else: tag(d, 'PEGA', 92, 150, 108, 190, sm(t, tb(11.8), tb(12.1)))
        elif 17 <= b < 27:
            gx, gy = S(*GSTAR)
            if b < 19.5:
                tag(d, 'GRÃO DE CIMENTO', 14, 56, gx - 10, gy - GR_R * s * 0.7, sm(t, tb(17.2), tb(17.7)))
                tag(d, 'ÁGUA', 150, 320, 175, 300, sm(t, tb(18), tb(18.5)))
            elif b < 22:
                tag(d, 'ETRINGITA', 14, 70, gx - GR_R * s * 0.7, gy - GR_R * s * 1.05, sm(t, tb(19.6), tb(20.1)))
            elif b < 24.8:
                ex, ey = S(6 * UM, 0)
                tag(d, 'C-S-H', 140, 70, ex, ey, sm(t, tb(22.2), tb(22.7)))
                if b > 23: ptext(d, 140, 84, 'A "COLA"', fill=YEL)
            else:
                tag(d, 'PORTLANDITA', 14, 320, 60, 290, sm(t, tb(25), tb(25.5)))
        elif 32 <= b < 37:
            hp = CSH_H * s
            if b < 33.8:
                tag(d, 'GRÃO', 10, 46, 20, 120, sm(t, tb(32.1), tb(32.6)))
                tag(d, 'C-S-H', 130, 46, 150, 104, sm(t, tb(32.6), tb(33.1)))
            elif b < 35.4:
                y0 = S(0, 0)[1]
                tag(d, 'SILICATO', 120, 46, S(1.65 * NM, 0)[0], y0 - hp * 0.25, sm(t, tb(33.8), tb(34.3)))
                tag(d, 'CÁLCIO', 30, 320, S(1.1 * NM, 0)[0], y0, sm(t, tb(34.1), tb(34.6)))
            else:
                p = S(0.3 * CSH_H + 1.1 * CSH_H * 1, CSH_H * 0.5)
                tag(d, 'ÁGUA PRESA', 110, 320, p[0], p[1], sm(t, tb(35.4), tb(35.9)))
        if b >= 45:
            val = clamp(0.6 + 0.4 * ease(sm(t, tb(45), tb(46.5))))
            bx0, bx1, by = 30, 186, 300
            d.rectangle([bx0 - 1, by - 1, bx1 + 1, by + 11], fill=(0, 0, 0, 255))
            d.rectangle([bx0, by, bx1, by + 10], fill=(40, 56, 90, 255))
            d.rectangle([bx0 + 1, by + 1, bx0 + 1 + int((bx1 - bx0 - 2) * val), by + 9], fill=(252, 206, 70, 255))
            ptext(d, bx0, by - 16, 'RESISTÊNCIA')
            if b >= 46.5: ptext(d, 160, by - 16, 'FCK', fill=YEL)
    else:
        pk = sm(t, T_ZE + 0.15, T_ZE + 2.2 * B)
        lk = (t - tb(51.5)) / (2.5 * B) if t >= tb(51.5) else -1
        shake = 1.5 if 0.3 < lk < 0.5 else 0
        out = C.cam(C.real_scene(t, 1.0, cured=True, props_k=pk, load_k=lk, pour=False), 108, 190, 1.3, shake, t)
    big = out.resize((OUTW, OUTH), Image.NEAREST)
    o2 = ov.resize((OUTW, OUTH), Image.NEAREST)
    big.paste(o2, (0, 0), o2)
    return big

def capa():
    st = dict(wet=0, ett=1, csh=0.8, port=0.6, pore=0.3, hyd=0.5, dense=0)
    img, _ = render(0.0, 10 ** 3.35, st)
    out = img.resize((OUTW, OUTH), Image.NEAREST)
    d = ImageDraw.Draw(out, 'RGBA'); d.rectangle([0, 0, OUTW, OUTH], fill=(0, 0, 0, 70))
    t1 = Image.new('RGBA', (1300, 440), (0, 0, 0, 0)); dt = ImageDraw.Draw(t1)
    dt.rectangle([0, 30, 1300, 410], fill=(8, 8, 10, 235))
    dt.text((650, 140), '28 DIAS', font=ImageFont.truetype(C.MONT % 900, 150), fill=(245, 190, 45), stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    dt.text((650, 300), 'POR DENTRO', font=ImageFont.truetype(C.MONT % 900, 130), fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0), anchor='mm')
    t1 = t1.rotate(4, expand=True, resample=Image.BICUBIC)
    out.paste(t1, (540 - t1.size[0] // 2, 760 - t1.size[1] // 2), t1)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        ts = [float(x) for x in sys.argv[2].split(',')]
        ims = [capa()] + [frame(x) for x in ts]
        cols = 8; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 270, rows * 500), (255, 255, 255))
        dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im.resize((270, 480)), ((k % cols) * 270, (k // cols) * 500))
            dd.text(((k % cols) * 270 + 4, (k // cols) * 500 + 482), 'capa' if k == 0 else '%.2f' % ts[k - 1], fill=(0, 0, 0))
        sheet.save(sys.argv[3]); print(VD)
    else:
        cp = capa(); cp.save('capa.png')
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', 'video_noaudio.mp4'], stdin=subprocess.PIPE)
        for _ in range(2): p.stdin.write(cp.tobytes())
        for n in range(int(VD * FPS)):
            p.stdin.write(frame(n / FPS).tobytes())
            if n % 150 == 0: print(n, flush=True)
        p.stdin.close(); p.wait(); print('done', VD)
