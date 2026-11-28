import math, random, sys, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cura as C
from cura import (W0, H0, OUTW, OUTH, FPS, B, checker, dpoly, drect, dell, ptext, tag, PIX,
                  clamp, sm, ease, eout, lerp, WHITE)
from ferrugem import punch, stepk, dissolve, PIXB, MINT, MINTL

NB = 56
VD = NB * B
NF = int(VD * FPS)
R = 78.0                       # drum inner radius (logical px)
G = 2600.0                     # gravity px/s2  (R = 0.3 m)
SUB = 5
OR1, OR2, ORO = (246, 152, 60), (228, 130, 44), (120, 60, 20)
IN1, IN2 = (196, 206, 222), (182, 192, 210)
PAD1, PAD2, PADO = (150, 164, 190), (132, 146, 174), (56, 68, 98)
FR1, FR2, FRO = (96, 132, 210), (80, 114, 192), (36, 52, 104)
STONE = [((150, 172, 208), (72, 88, 122)), ((184, 168, 156), (98, 82, 72)), ((206, 196, 164), (118, 106, 74))]
SAND, CEMC, WATC = (238, 196, 84), (150, 128, 196), (52, 132, 255)
CONC = (138, 138, 132)

# ---------------- time ----------------
def rate(b):
    """simulation speed: 1 = normal, slow motion between beats 24 and 34"""
    return 1 - 0.87 * (sm(b, 23.6, 24.4) - sm(b, 33.6, 34.4))
def W(f): return 0.45 * f + 0.55 * (1 - math.exp(-3.2 * f)) / (1 - math.exp(-3.2))
def pulse(b): return math.floor(b) + W(b - math.floor(b))

# ---------------- particle simulation ----------------
rs = random.Random(3)
KIND = ['st'] * 46 + ['sa'] * 110 + ['ce'] * 90 + ['wa'] * 50
N = len(KIND)
RAD = np.array([{'st': 4.6, 'sa': 2.5, 'ce': 2.1, 'wa': 2.2}[k] + rs.uniform(-0.3, 0.5) for k in KIND])
SEED = [rs.randrange(10 ** 6) for _ in KIND]
NPAD = 3; PADL = 0.40 * R

def simulate():
    if os.path.exists('bet_sim.npz'):
        z = np.load('bet_sim.npz'); return z['pos'], z['th']
    rng = np.random.default_rng(4)
    # layered start: stones at the bottom, then sand, cement, water
    x = np.zeros((N, 2))
    order = {'st': 0, 'sa': 1, 'ce': 2, 'wa': 3}
    for i, k in enumerate(KIND):
        lev = order[k]
        yy = R - 8 - lev * 13 - rng.uniform(0, 12); half = math.sqrt(max(4.0, (R - 4) ** 2 - yy ** 2))
        x[i] = (rng.uniform(-half, half), yy)
    v = np.zeros((N, 2)); rsum = RAD[:, None] + RAD[None, :]; eye = np.eye(N, dtype=bool)
    pos = np.zeros((NF, N, 2)); ths = np.zeros(NF)
    th = 0.0
    pre = 50
    for fr in range(-pre, NF):
        b = max(0.0, fr / FPS / B); r = rate(b) if fr >= 0 else 1.0
        dtf = (1 / FPS) * r; dt = dtf / SUB
        for sstep in range(SUB):
            if fr >= 0:
                b0 = (fr + sstep / SUB) / FPS / B; b1 = (fr + (sstep + 1) / SUB) / FPS / B
                dth = math.radians(60) * (pulse(b1) - pulse(b0)) * rate(b0)
            else: dth = 0.0
            om = dth / dt
            th += dth
            v[:, 1] += G * dt
            x += v * dt
            for it in range(2):
                # particles
                diff = x[:, None, :] - x[None, :, :]; dist = np.sqrt((diff ** 2).sum(-1)) + 1e-9
                ov = np.clip(rsum - dist, 0, None); ov[eye] = 0
                corr = (diff / dist[..., None] * (ov * 0.5)[..., None]).sum(1) * 0.55
                x += corr; v += corr * (FPS * SUB) * 0.25
                # paddles
                for k in range(NPAD):
                    a = th + 2 * math.pi * k / NPAD; u = np.array([math.cos(a), math.sin(a)])
                    tpar = np.clip(x @ u, R - PADL, R); c = tpar[:, None] * u[None, :]
                    dv = x - c; dd = np.sqrt((dv ** 2).sum(-1)) + 1e-9
                    hit = dd < RAD + 2.0
                    if hit.any():
                        n = dv[hit] / dd[hit, None]
                        x[hit] = c[hit] + n * (RAD[hit] + 2.0)[:, None]
                        vp = om * np.stack([-c[hit][:, 1], c[hit][:, 0]], 1)
                        vr = v[hit] - vp; vn = (vr * n).sum(-1); neg = vn < 0
                        vr[neg] -= vn[neg, None] * n[neg]; vr *= 0.75
                        v[hit] = vp + vr
                # wall
                d = np.sqrt((x ** 2).sum(-1)) + 1e-9; over = d - (R - RAD); hit = over > 0
                if hit.any():
                    n = x[hit] / d[hit, None]
                    x[hit] -= n * over[hit, None]
                    vn = (v[hit] * n).sum(-1); pos_ = vn > 0
                    vv = v[hit]; vv[pos_] -= vn[pos_, None] * n[pos_]
                    wt = om * R * np.stack([-n[:, 1], n[:, 0]], 1)
                    vt = vv - (vv * n).sum(-1)[:, None] * n
                    vv += 0.35 * (wt - vt)
                    v[hit] = vv
            sp = np.sqrt((v ** 2).sum(-1)); big = sp > 900
            v[big] *= (900 / sp[big])[:, None]
            v *= 0.999
        if fr >= 0: pos[fr] = x; ths[fr] = th
    np.savez('bet_sim.npz', pos=pos, th=ths)
    return pos, ths
POS, TH = simulate()

def irr(r, seed, n=7):
    rr = random.Random(seed)
    return [(r * (1 + rr.uniform(-0.25, 0.25)) * math.cos(2 * math.pi * i / n), r * (1 + rr.uniform(-0.25, 0.25)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
SHAPE = [irr(RAD[i], SEED[i]) if KIND[i] == 'st' else None for i in range(N)]

def mixcol(a, b_, k): return tuple(int(a[i] + (b_[i] - a[i]) * k) for i in range(3))

# ---------------- front view ----------------
def front(fr, s, phi, cx=0.0, cy=0.0, mix=0.0):
    b = fr / FPS / B; th = TH[fr]
    cp, sp = math.cos(phi), math.sin(phi)
    def T(x, y):
        x -= cx; y -= cy
        return (108 + (x * cp + y * sp) * s, 200 + (-x * sp + y * cp) * s)
    img = Image.new('RGB', (W0, H0), MINT); d = ImageDraw.Draw(img)
    for g in range(-320, 321, 40):
        d.line([T(g, -320), T(g, 320)], fill=MINTL); d.line([T(-320, g), T(320, g)], fill=MINTL)
    # ground + frame
    dpoly(img, [T(-400, 150), T(400, 150), T(400, 500), T(-400, 500)], (236, 170, 100), (222, 154, 86))
    d.line([T(-400, 150), T(400, 150)], fill=(120, 70, 30), width=2)
    for sx in (-1, 1):
        dpoly(img, [T(sx * 58, 40), T(sx * 72, 40), T(sx * 108, 150), T(sx * 92, 150)], FR1, FR2, FRO)
        X, Y = T(sx * 100, 138); rw = 15 * s
        dell(img, [X - rw, Y - rw, X + rw, Y + rw], (70, 76, 96), (58, 64, 84), (24, 28, 44))
        d.ellipse([X - rw * 0.35, Y - rw * 0.35, X + rw * 0.35, Y + rw * 0.35], fill=(200, 206, 220))
    dpoly(img, [T(-96, 96), T(96, 96), T(96, 106), T(-96, 106)], FR1, FR2, FRO)
    # ring gear teeth + rim
    X0, Y0 = T(0, 0)
    for k in range(30):
        a = th + k * math.pi / 15
        p = [T((R + 9) * math.cos(a - 0.06), (R + 9) * math.sin(a - 0.06)), T((R + 16) * math.cos(a - 0.045), (R + 16) * math.sin(a - 0.045)),
             T((R + 16) * math.cos(a + 0.045), (R + 16) * math.sin(a + 0.045)), T((R + 9) * math.cos(a + 0.06), (R + 9) * math.sin(a + 0.06))]
        d.polygon(p, fill=(70, 82, 112), outline=(30, 38, 62))
    ro = (R + 11) * s; dell(img, [X0 - ro, Y0 - ro, X0 + ro, Y0 + ro], OR1, OR2, ORO)
    ri = R * s; dell(img, [X0 - ri, Y0 - ri, X0 + ri, Y0 + ri], IN1, IN2, (90, 100, 126))
    # weld marks on the back wall rotate with the drum
    for k in range(6):
        a = th + k * math.pi / 3
        d.line([T(14 * math.cos(a), 14 * math.sin(a)), T(30 * math.cos(a), 30 * math.sin(a))], fill=(160, 172, 194))
    rb = 10 * s; dell(img, [X0 - rb, Y0 - rb, X0 + rb, Y0 + rb], PAD1, PAD2, PADO)
    # paddles
    for k in range(NPAD):
        a = th + 2 * math.pi * k / NPAD; ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        p = [T(R * ux + 3 * nx, R * uy + 3 * ny), T((R - PADL) * ux + 2 * nx, (R - PADL) * uy + 2 * ny),
             T((R - PADL) * ux - 2 * nx, (R - PADL) * uy - 2 * ny), T(R * ux - 3 * nx, R * uy - 3 * ny)]
        dpoly(img, p, PAD1, PAD2, PADO)
    # particles
    x = POS[fr]
    for i in np.argsort([{'ce': 0, 'wa': 1, 'sa': 2, 'st': 3}[k] for k in KIND], kind='stable'):
        k = KIND[i]; X, Y = T(x[i, 0], x[i, 1]); r = RAD[i] * s
        if k == 'st':
            c1, o = STONE[SEED[i] % 3]; c1 = mixcol(c1, (150, 152, 158), 0.45 * mix)
            pts = [(X + (px * cp + py * sp) * s, Y + (-px * sp + py * cp) * s) for (px, py) in SHAPE[i]]
            d.polygon(pts, fill=c1, outline=o); d.point((X - r * 0.3, Y - r * 0.3), fill=(255, 255, 255))
        else:
            base = {'sa': SAND, 'ce': CEMC, 'wa': WATC}[k]
            g = (CONC[0] - 8 + SEED[i] % 16, CONC[1] - 8 + SEED[i] % 16, CONC[2] - 8 + SEED[i] % 16)
            col = mixcol(base, g, clamp(mix * (1.5 if k == 'wa' else 1.0)))
            q = r * (1 + 0.35 * mix)
            d.ellipse([X - q, Y - q, X + q, Y + q], fill=col)
            if k == 'wa' and mix < 0.5: d.point((X - 1, Y - 1), fill=(220, 236, 255))
    # front lip
    d.ellipse([X0 - ri, Y0 - ri, X0 + ri, Y0 + ri], outline=(90, 100, 126))
    d.arc([X0 - ro + 3, Y0 - ro + 3, X0 + ro - 3, Y0 + ro - 3], 200 - math.degrees(phi), 250 - math.degrees(phi), fill=(255, 226, 180), width=max(1, int(2 * s)))
    return img, d, T

# ---------------- side view ----------------
def side(b, tilt, th, throws=True, pour=0.0, fill=0.0):
    img = Image.new('RGB', (W0, H0), MINT); d = ImageDraw.Draw(img)
    for g in range(0, W0, 36): d.line([(g + 8, 0), (g + 8, H0)], fill=MINTL)
    for g in range(0, H0, 36): d.line([(0, g + 10), (W0, g + 10)], fill=MINTL)
    drect(img, (-2, 290, W0 + 2, H0 + 2), (236, 170, 100), (222, 154, 86)); d.line([(0, 290), (W0, 290)], fill=(120, 70, 30), width=2)
    px, py = 96, 196      # pivot
    # frame
    dpoly(img, [(px - 6, py), (px + 6, py), (px + 44, 290), (px + 30, 290)], FR1, FR2, FRO)
    dpoly(img, [(px - 6, py), (px + 6, py), (px - 30, 290), (px - 44, 290)], FR1, FR2, FRO)
    drect(img, (px - 62, 268, px + 40, 276), FR1, FR2, FRO)
    dell(img, [px - 76, 262, px - 48, 290], (70, 76, 96), (58, 64, 84), (24, 28, 44)); d.ellipse([px - 66, 272, px - 58, 280], fill=(200, 206, 220))
    drect(img, (px - 58, 226, px - 26, 262), (96, 196, 130), (80, 178, 114), (30, 90, 56))     # motor
    ptext(d, px - 56, 236, 'M')
    ca, sa = math.cos(tilt), math.sin(tilt)
    def L(u, v): return (px + u * ca - v * sa, py - u * sa - v * ca)      # u along axis (mouth +), v across
    body = [(-52, -30), (-58, 0), (-52, 30), (-10, 46), (20, 46), (52, 28), (52, -28), (20, -46), (-10, -46)]
    dpoly(img, [L(u, v) for u, v in body], OR1, OR2, ORO)
    # ribs moving across = rotation
    for k in range(6):
        a = th + k * math.pi / 3
        if math.cos(a) > 0:
            v = 44 * math.sin(a); d.line([L(-8, v), L(18, v)], fill=ORO)
            d.line([L(18, v), L(50, v * 0.62)], fill=ORO); d.line([L(-8, v), L(-50, v * 0.66)], fill=ORO)
    dpoly(img, [L(-12, -49), L(-2, -49), L(-2, 49), L(-12, 49)], (70, 82, 112), (58, 70, 98), (30, 38, 62))
    for k in range(12):
        a = th * 1.0 + k * math.pi / 6
        if math.cos(a) > 0:
            v = 47 * math.sin(a); d.line([L(-12, v), L(-2, v)], fill=(150, 164, 190))
    dpoly(img, [L(52, -28), L(57, -26), L(57, 26), L(52, 28)], (255, 196, 120), OR1, ORO)
    mouth = L(56, 0)
    if throws:
        seq = [(1, 'st', 'BRITA'), (2, 'st', None), (3, 'sa', 'AREIA'), (4, 'sa', None), (5, 'ce', 'CIMENTO'), (6, 'wa', 'ÁGUA')]
        for (bb, kind, lab) in seq:
            u = (b - (bb - 0.55)) / 0.9
            if 0 <= u <= 1:
                sx, sy = 216, 150
                for i in range(16):
                    uu = clamp(u - i * 0.012); rr = random.Random(bb * 100 + i)
                    x = lerp(sx, mouth[0], uu) + rr.uniform(-5, 5) * (1 - uu); y = lerp(sy, mouth[1], uu) - 70 * math.sin(math.pi * uu) + rr.uniform(-5, 5)
                    if kind == 'st':
                        c1, o = STONE[i % 3]; d.polygon([(x - 3, y), (x, y - 3), (x + 3, y - 1), (x + 2, y + 3), (x - 2, y + 3)], fill=c1, outline=o)
                    else:
                        col = {'sa': SAND, 'ce': CEMC, 'wa': WATC}[kind]; d.rectangle([x, y, x + 2, y + 2], fill=col)
                # shovel / bucket
                hx = lerp(226, 196, eout(clamp(u * 2))); hy = lerp(190, 150, eout(clamp(u * 2)))
                if kind == 'wa': dpoly(img, [(hx - 10, hy - 8), (hx + 8, hy - 12), (hx + 12, hy + 6), (hx - 6, hy + 10)], (120, 190, 255), (96, 168, 240), (20, 60, 140))
                else:
                    d.line([(hx, hy), (hx + 30, hy + 26)], fill=(120, 70, 30), width=3)
                    dpoly(img, [(hx - 10, hy - 6), (hx + 4, hy - 10), (hx + 8, hy + 4), (hx - 6, hy + 8)], (206, 214, 228), (184, 194, 210), (70, 84, 108))
            if lab and bb - 0.3 <= b < bb + 1.0:
                w = PIX.getlength(lab); ptext(d, mouth[0] + 6, mouth[1] - 44 - (bb % 2) * 0, lab)
    if pour > 0 or fill > 0:
        bx = 150   # wheelbarrow
        dpoly(img, [(bx - 6, 248), (bx + 58, 248), (bx + 46, 276), (bx + 6, 276)], (96, 196, 130), (80, 178, 114), (30, 90, 56))
        dell(img, [bx + 16, 270, bx + 38, 292], (70, 76, 96), (58, 64, 84), (24, 28, 44))
        d.line([(bx + 56, 250), (bx + 76, 240)], fill=(30, 90, 56), width=3)
        if fill > 0:
            h = 16 * fill
            dpoly(img, [(bx - 2, 250), (bx + 54, 250), (bx + 50, 250 - h * 0.6), (bx + 26, 250 - h), (bx + 4, 250 - h * 0.5)], (176, 174, 168), (160, 158, 152), (90, 88, 84))
        if pour > 0:
            mx, my = mouth
            ph = b % 1.0; wdt = 7 + 5 * math.exp(-4 * ph)
            pts = [(mx, my - 4), (mx + 8, my + 10), (bx + 26 + wdt, 250 - 16 * fill), (bx + 26 - wdt, 250 - 16 * fill), (mx - 6, my + 12)]
            dpoly(img, pts, (176, 174, 168), (160, 158, 152), (90, 88, 84))
            for i in range(10):
                u = (b * 2 + i * 0.1) % 1.0; x = lerp(mx, bx + 26, u) + (i % 3 - 1) * 2; y = lerp(my + 6, 248 - 16 * fill, u * u)
                c1, o = STONE[i % 3]; d.rectangle([x, y, x + 2, y + 2], fill=c1)
    return img, d, mouth

# ---------------- HUD ----------------
def hud(d, f):
    ptext(d, 8, 52, 'MISTURA')
    d.rectangle([58, 55, 122, 61], fill=(22, 26, 40), outline=(0, 0, 0))
    if f > 0.02: d.rectangle([59, 56, 59 + int(62 * clamp(f)), 60], fill=mixcol(SAND, (190, 190, 186), f))
def tg(d, b, b0, b1, s, tx, ty, o):
    if b0 <= b < b1:
        w = PIX.getlength(s); tx = clamp(tx, 5, W0 - 5 - w)
        tag(d, s, tx, ty, o[0], o[1], min(sm(b, b0, b0 + 0.5) + 0.05, 1.0))
def bigword(d, lines, y, k):
    for i, s in enumerate(lines):
        yy = y + i * 28 - 10 * (1 - k)
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                d.text((108 + dx, yy + dy), s, font=PIXB, fill=(0, 0, 0), anchor='mm', fontmode='1')
        d.text((108, yy), s, font=PIXB, fill=(255, 255, 255) if i == 0 else (255, 214, 80), anchor='mm', fontmode='1')

def thb(b):
    f = b * B * FPS; i = int(clamp(f, 0, NF - 1)); return TH[i]
TRACK = {k: next(i for i in range(N) if KIND[i] == k and SEED[i] % 7 == 0) for k in ('st', 'sa', 'ce')}

def frontframe(fr, tags=True):
    b = fr / FPS / B; th = TH[fr]
    slow = sm(b, 23.6, 24.6) - sm(b, 33.4, 34.4)
    s = (1.0 + 0.32 * slow) * (1 + (punch(b) - 1) * (1 - 0.6 * slow))
    phi = 0.0
    if 16 <= b < 22: phi = th - thb(16)
    if 40 <= b < 46: phi = th - thb(40)
    mix = sm(b, 8, 45)
    img, d, T = front(fr, s, phi, 0, 6 * slow, mix)
    if tags:
        if 8.3 <= b < 11.5: ptext(d, 108, 84, 'O TAMBOR GIRA', anchor='ma')
        if 16.3 <= b < 21.6: ptext(d, 108, 84, 'GIRANDO JUNTO', anchor='ma')
        if 24.4 <= b < 33.6: ptext(d, 108, 330, 'CÂMERA LENTA', (255, 214, 80), anchor='ma')
        k = int(((th + 0.6) % (2 * math.pi)) // (2 * math.pi / 3))
        # paddle on the rising side (left half going up)
        best = None
        for q in range(NPAD):
            a = th + 2 * math.pi * q / NPAD; px_, py_ = (R - PADL * 0.6) * math.cos(a), (R - PADL * 0.6) * math.sin(a)
            sc = -px_ if True else 0
            if best is None or abs(math.atan2(py_, px_) - math.pi) < best[0] or abs(math.atan2(py_, px_) + math.pi) < best[0]:
                dd = min(abs(math.atan2(py_, px_) - math.pi), abs(math.atan2(py_, px_) + math.pi)); best = (dd, px_, py_) if best is None or dd < best[0] else best
        tg(d, b, 24.6, 27.4, 'A PÁ LEVANTA', 10, 84, T(best[1], best[2]))
        x = POS[fr]; air = (np.hypot(x[:, 0], x[:, 1]) < R - 14) & (x[:, 1] < 20)
        ap = x[air].mean(0) if air.sum() > 3 else np.array([0, -10.0])
        tg(d, b, 27.6, 30.4, 'E DEIXA CAIR', 110, 84, T(ap[0], ap[1]))
        if 30.6 <= b < 33.4:
            trk = sorted([(T(*x[TRACK[k]]), n) for k, n in (('st', 'BRITA'), ('sa', 'AREIA'), ('ce', 'CIMENTO'))])
            for (pt, n), tx, ty, t0 in zip(trk, (10, 84, 160), (84, 100, 84), (30.6, 30.9, 31.2)):
                tg(d, b, t0, 33.4, n, tx, ty, pt)
        if 35 <= b < 39.5: ptext(d, 108, 84, 'TUDO VIRA UMA MASSA', anchor='ma')
        if 40.3 <= b < 45.6: ptext(d, 108, 84, 'CAI E MISTURA DE NOVO', anchor='ma')
        hud(d, mix)
    return img

def frame(fr, tags=True):
    b = fr / FPS / B
    if b < 7.2:
        img, d, m = side(b, math.radians(38), b * math.radians(60) * 0 + math.radians(60) * pulse(b))
        if tags and b < 1.2: ptext(d, 108, 84, 'COMO A BETONEIRA MISTURA', anchor='ma')
        if tags and 6.6 <= b: tg(d, b, 6.6, 8, 'MOTOR', 20, 320, (54, 250))
    elif b < 8.2:
        a, d, m = side(b, math.radians(38), math.radians(60) * pulse(b), throws=False)
        img = dissolve(a, frontframe(fr, tags), sm(b, 7.2, 8.2))
    elif b < 47.4:
        img = frontframe(fr, tags)
    else:
        tilt = math.radians(lerp(38, -28, ease(sm(b, 48.4, 50))))
        pour = 1.0 if 50 <= b < 55 else 0.0; fill = sm(b, 50, 55)
        e, d, m = side(b, tilt, math.radians(60) * pulse(b), throws=False, pour=pour, fill=max(fill, 0.001))
        if tags and b >= 52:
            bigword(d, ['CONCRETO', 'PRONTO'], 84, eout(sm(b, 52, 52.35)))
        img = e if b >= 48.4 else dissolve(frontframe(fr, tags), e, sm(b, 47.4, 48.4))
    return img.resize((OUTW, OUTH), Image.NEAREST)

def capa():
    fr = int(20 * B * FPS)
    img, d, T = front(fr, 1.25, 0.0, 0, 0, 0.3)
    out = img.resize((OUTW, OUTH), Image.NEAREST)
    dd = ImageDraw.Draw(out, 'RGBA'); dd.rectangle([0, 0, OUTW, OUTH], fill=(0, 0, 0, 30))
    t1 = Image.new('RGBA', (1300, 400), (0, 0, 0, 0)); dt = ImageDraw.Draw(t1)
    dt.rectangle([0, 20, 1300, 380], fill=(8, 8, 10, 235))
    dt.text((650, 130), 'POR DENTRO', font=ImageFont.truetype(C.MONT % 900, 136), fill=(245, 190, 45), stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    dt.text((650, 290), 'DA BETONEIRA', font=ImageFont.truetype(C.MONT % 900, 104), fill=(255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0), anchor='mm')
    t1 = t1.rotate(4, expand=True, resample=Image.BICUBIC)
    out = out.convert('RGB'); out.paste(t1, (540 - t1.size[0] // 2, 430 - t1.size[1] // 2), t1)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        bs = [float(x) for x in sys.argv[2].split(',')]
        ims = [frame(int(x * B * FPS)) for x in bs]
        cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 270, rows * 492), (255, 255, 255)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im.resize((270, 480), Image.NEAREST), ((k % cols) * 270, (k // cols) * 492))
            dd.text(((k % cols) * 270 + 4, (k // cols) * 492 + 481), 'b%.2f' % bs[k], fill=(0, 0, 0))
        sheet.save(sys.argv[3])
    else:
        cp = capa(); cp.save('capa-betoneira.png')
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', 'betoneira_noaudio.mp4'], stdin=subprocess.PIPE)
        for _ in range(2): p.stdin.write(cp.tobytes())
        for n in range(NF):
            p.stdin.write(frame(n).tobytes())
        p.stdin.close(); p.wait(); print('done', VD)
