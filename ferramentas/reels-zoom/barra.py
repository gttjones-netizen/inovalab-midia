import math, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
import cura as C
from cura import (W0, H0, OUTW, OUTH, FPS, B, checker, dpoly, drect, dell, ptext, tag, PIX,
                  clamp, sm, ease, eout, lerp, WHITE, counter)
from ferrugem import punch, stepk, dissolve, PIXB, MINT, MINTL, ST1, ST2, STO, STH

NB = 56
VD = NB * B
G = 0.02          # grain ~20 um (mm)
LAM = 3.0e-4      # pearlite lamella spacing ~0.3 um
A = 2.866e-7      # alpha-iron lattice parameter 0.2866 nm
S0 = 15.0
DSL = 1.5e-4      # dislocation spacing ~150 nm
L0 = math.log10(S0)

FER_A = np.array([216, 230, 248.]); FER_B = np.array([186, 205, 236.])
PEA = np.array([132, 118, 190.]); CEM = np.array([78, 60, 142.]); BND = np.array([70, 86, 128.])
AVG = 0.68 * (FER_A + FER_B) / 2 + 0.32 * PEA

def hsh(i, j, salt):
    x = (i.astype(np.int64) * 374761393 + j.astype(np.int64) * 668265263 + salt * 1013904223) & 0xFFFFFFFF
    x = ((x ^ (x >> 13)) * 1274126177) & 0xFFFFFFFF
    x = x ^ (x >> 16)
    return x / 4294967296.0

def voronoi(X, Y):
    u = X / G; v = Y / G
    iu = np.floor(u).astype(np.int64); iv = np.floor(v).astype(np.int64)
    d1 = np.full(u.shape, 9.0); d2 = np.full(u.shape, 9.0)
    c1i = np.zeros_like(iu); c1j = np.zeros_like(iu); c2i = np.zeros_like(iu); c2j = np.zeros_like(iu)
    s1x = np.zeros_like(u); s1y = np.zeros_like(u); s2x = np.zeros_like(u); s2y = np.zeros_like(u)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ci = iu + di; cj = iv + dj
            sx = ci + 0.12 + 0.76 * hsh(ci, cj, 1); sy = cj + 0.12 + 0.76 * hsh(ci, cj, 2)
            d = np.hypot(u - sx, v - sy)
            a = d < d1; b_ = (~a) & (d < d2)
            d2 = np.where(a, d1, np.where(b_, d, d2))
            c2i = np.where(a, c1i, np.where(b_, ci, c2i)); c2j = np.where(a, c1j, np.where(b_, cj, c2j))
            s2x = np.where(a, s1x, np.where(b_, sx, s2x)); s2y = np.where(a, s1y, np.where(b_, sy, s2y))
            d1 = np.where(a, d, d1); c1i = np.where(a, ci, c1i); c1j = np.where(a, cj, c1j)
            s1x = np.where(a, sx, s1x); s1y = np.where(a, sy, s1y)
    return c1i, c1j, d1, c2i, c2j, d2, s1x, s1y, s2x, s2y

def is_pearl(ci, cj): return hsh(ci, cj, 3) < 0.32

# ---- pick the target point P: inside a ferrite grain, ~0.45 um from a pearlite grain ----
def find_P():
    xs = np.linspace(50 * G, 56 * G, 900); X, Y = np.meshgrid(xs, xs)
    c1i, c1j, d1, c2i, c2j, d2, s1x, s1y, s2x, s2y = voronoi(X, Y)
    bd = (d2 - d1) * G * 0.5
    ok = (~is_pearl(c1i, c1j)) & is_pearl(c2i, c2j) & (bd > 4.0e-4) & (bd < 5.0e-4)
    # keep away from triple points: boundary direction must be stable in a neighbourhood
    lab = c2i * 7919 + c2j
    same = (ndimage.maximum_filter(lab, 25) == ndimage.minimum_filter(lab, 25))
    lab1 = c1i * 7919 + c1j
    same &= (ndimage.maximum_filter(lab1, 9) == ndimage.minimum_filter(lab1, 9)) | True
    idx = np.argwhere(ok & same)
    k = idx[len(idx) // 2]
    px, py = X[k[0], k[1]], Y[k[0], k[1]]
    nx, ny = s2x[k[0], k[1]] - s1x[k[0], k[1]], s2y[k[0], k[1]] - s1y[k[0], k[1]]
    n = math.hypot(nx, ny)
    return px, py, nx / n, ny / n, bd[k[0], k[1]]
PX, PY, NX, NY, PBD = find_P()
CBX, CBY = -1.5, 1.0     # bar centre relative to P (mm)
RB, RING = 5.0, 0.9

YY, XX = np.mgrid[0:H0, 0:W0]
DITH = (((XX + YY) % 2) * -7.0)[..., None]

def mixc(a, b, k):
    if np.isscalar(k): return a + (b - a) * k
    return a + (b - a) * k[..., None]

def atoms(X, Y, st):
    u = X / (A * (1 + st.get('eps', 0))); v = Y / A
    u = np.where(v < 0.25, u - st.get('slip', 0), u)
    col = np.empty(u.shape + (3,)); col[:] = (86, 110, 164)
    du2 = u - 0.5 - np.rint(u - 0.5); dv2 = v - 0.5 - np.rint(v - 0.5); r2 = np.hypot(du2, dv2)
    col[r2 < 0.34] = (60, 80, 132); col[r2 < 0.28] = (136, 162, 210)
    col[(r2 < 0.28) & (du2 + dv2 > 0.12)] = (116, 142, 196)
    col[np.hypot(du2 + 0.1, dv2 + 0.1) < 0.07] = (214, 228, 248)
    du = u - np.rint(u); dv = v - np.rint(v); r = np.hypot(du, dv)
    col[r < 0.34] = (44, 60, 100); col[r < 0.28] = (208, 226, 250)
    col[(r < 0.28) & (du + dv > 0.12)] = (176, 198, 236)
    col[np.hypot(du + 0.1, dv + 0.1) < 0.075] = (255, 255, 255)
    fu = np.floor(u); rv = np.rint(v)
    hc = hsh(fu.astype(np.int64), rv.astype(np.int64), 9) < 0.035
    dx = u - fu - 0.5; rc = np.hypot(dx, dv)
    col[hc & (rc < 0.17)] = (20, 20, 30); col[hc & (rc < 0.13)] = (58, 58, 74)
    col[hc & (np.hypot(dx + 0.04, dv + 0.04) < 0.04)] = (170, 170, 190)
    return col

def field(s, cx, cy, st):
    X = cx + (XX - 108 + 0.5) / s; Y = cy + (YY - 192 + 0.5) / s
    r = np.hypot(X - CBX, Y - CBY); th = np.arctan2(Y - CBY, X - CBX)
    Rb = RB + 0.4 * np.exp(-((np.abs(np.abs(th) - math.pi / 2)) / 0.16) ** 2)
    kB = sm(G * s, 0.7, 3.0); kC = sm(LAM * s, 1.2, 4.0); kD = sm(A * s, 4.0, 9.0)
    if kB > 0:
        c1i, c1j, d1, c2i, c2j, d2, *_ = voronoi(X + PX, Y + PY)
        t = hsh(c1i, c1j, 4); pearl = is_pearl(c1i, c1j)
        fer = FER_A + (FER_B - FER_A) * t[..., None]
        pea = PEA * (0.9 + 0.2 * t[..., None])
        if kC > 0:
            ang = math.pi * hsh(c1i, c1j, 5); ca, sa = np.cos(ang), np.sin(ang)
            xr = (X + PX) - (c1i * G); yr = (Y + PY) - (c1j * G)
            w = (xr * ca + yr * sa) / LAM + 0.5 * np.sin((-xr * sa + yr * ca) / LAM * 0.21 + 6.28 * t)
            cem = (w - np.floor(w)) < 0.36
            pea = mixc(pea, np.where(cem[..., None], CEM, FER_A), kC)
        kL = sm(DSL * s, 6, 20) * (1 - sm(A * s, 1.0, 2.5))
        if kL > 0:
            u = (X + PX) / DSL; v = (Y + PY) / DSL; iu = np.floor(u).astype(np.int64); iv = np.floor(v).astype(np.int64)
            dm = np.full(u.shape, 9.0)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ci = iu + di; cj = iv + dj
                    sx = ci + hsh(ci, cj, 11); sy = cj + hsh(ci, cj, 12); a_ = math.pi * hsh(ci, cj, 13); hl = 0.15 + 0.3 * hsh(ci, cj, 14)
                    ca_, sa_ = np.cos(a_), np.sin(a_); rx = u - sx; ry = v - sy
                    tt = np.clip(rx * ca_ + ry * sa_, -hl, hl)
                    bow = 0.08 * np.cos(tt / hl * 1.57)
                    dm = np.minimum(dm, np.hypot(rx - tt * ca_ + bow * sa_, ry - tt * sa_ - bow * ca_))
            fer = np.where((dm * DSL * s < 0.75)[..., None], mixc(fer, np.array([118, 138, 196.]), kL), fer)
        if kD > 0:
            at = atoms(X, Y, st)
            fer = mixc(fer, at, kD)
        grain = np.where(pearl[..., None], pea, fer)
        bw = (d2 - d1) * G * s * 0.5
        grain = np.where((bw < 0.8)[..., None], mixc(grain, BND, sm(G * s, 2.0, 5.0) * (1 - 0.6 * kD)), grain)
        steel = mixc(np.broadcast_to(AVG, grain.shape), grain, kB)
    else:
        steel = np.empty(X.shape + (3,)); steel[:] = AVG
    km = 1 - sm(math.log10(s), 1.5, 2.6)
    if km > 0:
        ring = np.clip((r - (Rb - RING)) / 0.12, 0, 1)
        steel = mixc(steel, steel * 0.74 + np.array([0, 8, 30.]), ring)
        saw = np.sin((X * 0.94 + Y * 0.34) / 0.16 * 2 * math.pi) > 0.72
        steel = steel - (saw * 9.0 * km)[..., None]
        steel = steel + (16 * km * np.clip((-(X - CBX) - (Y - CBY)) / 7, -1, 1))[..., None]
        bg = np.empty(X.shape + (3,)); bg[:] = MINT
        gl = (np.abs(X - np.rint(X / 5) * 5) * s < 0.6) | (np.abs(Y - np.rint(Y / 5) * 5) * s < 0.6)
        bg[gl] = MINTL
        sh = np.hypot(X - CBX - 0.5, Y - CBY - 0.6) < RB + 0.2
        bg[sh] = (120, 186, 168)
        out = np.where((r < Rb)[..., None], steel, bg)
        out[np.abs(r - Rb) * s < 0.9] = (40, 56, 96)
    else:
        out = steel
    out = out + DITH * (1 - 0.7 * kD)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

# ---------------- camera ----------------
LZ = [(4.5, L0), (9, 3.5), (14, 3.58), (18, 5.0), (22, 5.06), (27, 7.85), (39.5, 7.9), (47.5, L0), (56, L0)]
def logs(b):
    if b <= LZ[0][0]: return LZ[0][1]
    for (b0, l0), (b1, l1) in zip(LZ, LZ[1:]):
        if b <= b1: return lerp(l0, l1, ease((b - b0) / (b1 - b0)))
    return LZ[-1][1]
def camera(s):
    w = min(1.0, (S0 / s)) ** 1.4
    bump = math.exp(-((math.log10(s) - 5.0) / 0.8) ** 2) * PBD
    return CBX * w + NX * bump, CBY * w + NY * bump

_TP = {}
def find(key, s, c, kind, rect):
    """screen pixel (x,y) deep inside a region of the given kind"""
    if key in _TP: return _TP[key]
    X = c[0] + (XX - 108 + 0.5) / s; Y = c[1] + (YY - 192 + 0.5) / s
    c1i, c1j, d1, c2i, c2j, d2, *_ = voronoi(X + PX, Y + PY)
    pearl = is_pearl(c1i, c1j); t = hsh(c1i, c1j, 4)
    if kind == 'fer': m = ~pearl & ((d2 - d1) * G * s * 0.5 > 3)
    elif kind == 'pea': m = pearl & ((d2 - d1) * G * s * 0.5 > 3)
    else:
        ang = math.pi * hsh(c1i, c1j, 5); xr = (X + PX) - c1i * G; yr = (Y + PY) - c1j * G
        w = (xr * np.cos(ang) + yr * np.sin(ang)) / LAM + 0.5 * np.sin((-xr * np.sin(ang) + yr * np.cos(ang)) / LAM * 0.21 + 6.28 * t)
        cem = (w - np.floor(w)) < 0.36
        m = pearl & (cem if kind == 'cem' else ~cem)
    mm = np.zeros_like(m); x0, y0, x1, y1 = rect; mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    dt = ndimage.distance_transform_edt(mm)
    k = np.unravel_index(np.argmax(dt), dt.shape)
    _TP[key] = (X[k], Y[k]); return _TP[key]

def carbon_pt():
    for rad in range(1, 8):
        for i in range(-rad, rad + 1):
            for j in range(-rad, rad + 1):
                if j > 0 and hsh(np.array([i]), np.array([j]), 9)[0] < 0.035 and abs(i) < 5:
                    return ((i + 0.5) * A, j * A)
    return (0.5 * A, A)
CARB = carbon_pt()

# ---------------- side scenes ----------------
def bench(b):
    img = Image.new('RGB', (W0, H0), MINT); d = ImageDraw.Draw(img)
    for g in range(0, W0, 36): d.line([(g + 8, 0), (g + 8, H0)], fill=MINTL)
    for g in range(0, H0, 36): d.line([(0, g + 10), (W0, g + 10)], fill=MINTL)
    drect(img, (-2, 252, W0 + 2, H0 + 2), (236, 170, 100), (222, 154, 86)); d.line([(0, 252), (W0, 252)], fill=(120, 70, 30), width=2)
    for y in range(270, H0, 22): d.line([(0, y), (W0, y)], fill=(206, 140, 76))
    drect(img, (14, 204, 76, 252), (150, 162, 184), (132, 144, 168), (60, 70, 96))
    drect(img, (22, 176, 40, 206), (176, 188, 208), (156, 168, 190), (60, 70, 96))
    drect(img, (52, 176, 70, 206), (176, 188, 208), (156, 168, 190), (60, 70, 96))
    return img, d

def barseg(img, d, x0, x1, y0, dy=0):
    drect(img, (x0, y0 + dy, x1, y0 + 14 + dy), ST1, ST2, STO)
    d.line([(x0 + 1, y0 + 3 + dy), (x1 - 1, y0 + 3 + dy)], fill=STH)
    x = x0 + 4 - (x0 % 8)
    while x < x1 - 5:
        if x > x0: d.line([(x, y0 + 12 + dy), (x + 5, y0 + 2 + dy)], fill=STO)
        x += 8

def saw(b):
    img, d = bench(b)
    cut = 150; fall = b >= 3
    barseg(img, d, 30, cut - (1 if fall else 0), 186)
    if fall:
        tt = (b - 3) * B; barseg(img, d, cut + 2, 222, 186, int(420 * tt * tt))
    else: barseg(img, d, cut, 222, 186)
    yc = 138 + 15 * (b / 3) + 1.5 * math.sin(b * 2 * math.pi) if not fall else 153 - 60 * eout(sm(b, 3, 4))
    R = 50
    dell(img, [cut - R, yc - R, cut + R, yc + R], (120, 132, 156), (104, 116, 142), (40, 50, 76))
    for k in range(12):
        a = b * 9 + k * math.pi / 6
        d.line([(cut + math.cos(a) * 14, yc + math.sin(a) * 14), (cut + math.cos(a) * (R - 3), yc + math.sin(a) * (R - 3))], fill=(86, 98, 126))
    dell(img, [cut - 12, yc - 12, cut + 12, yc + 12], (244, 150, 60), (226, 128, 44), (120, 60, 20))
    d.pieslice([cut - R - 5, yc - R - 5, cut + R + 5, yc + R + 5], 180, 360, fill=(244, 150, 60), outline=(120, 60, 20))
    d.pieslice([cut - R + 12, yc - R + 12, cut + R - 12, yc + R - 12], 180, 360, fill=(226, 128, 44))
    drect(img, (cut + 30, yc - 64, cut + 80, yc - 52), (60, 70, 96), (50, 60, 84), (30, 36, 56))
    if not fall or b < 3.25:
        f = b % 1.0; n = int(50 + 60 * math.exp(-4 * f))
        for i in range(n):
            ph = (b * 3.1 + i * 0.0731) % 1.0; a = math.pi + 0.5 + (i * 0.61 % 1.0) * 1.3 - 0.75
            v = 80 + (i * 37 % 70)
            x = cut - 2 + math.cos(a) * v * ph; y = 190 + math.sin(a) * v * ph * 0.7 + 70 * ph * ph
            c = (255, 250, 200) if ph < 0.3 else (255, 214, 80) if ph < 0.65 else (250, 140, 50)
            d.rectangle([x, y, x + (3 if ph < 0.5 else 2), y + (2 if ph < 0.5 else 1)], fill=c)
        d.ellipse([cut - 6, 183, cut + 6, 193], fill=(255, 250, 210))
    return img, d

def bend(b):
    img, d = bench(b)
    phi = math.radians(90) * stepk(b, 49, 3)
    cx, cy, rp = 122, 176, 10; rc = rp + 7
    pts = [(30, 193), (cx, 193)]
    n = 10
    for i in range(1, n + 1):
        a = phi * i / n; pts.append((cx + rc * math.sin(a), cy + rc * math.cos(a)))
    ex, ey = pts[-1]; L = 78
    pts.append((ex + L * math.cos(phi), ey - L * math.sin(phi)))
    d.line(pts, fill=STO, width=16, joint='curve'); d.line(pts, fill=ST1, width=12, joint='curve')
    hp = [(x - 3 * math.sin(0), y - 3) for (x, y) in pts[:2]]
    d.line([(30, 189), (cx, 189)], fill=STH)
    for k in range(4, int(L), 9):
        qx = ex + k * math.cos(phi); qy = ey - k * math.sin(phi)
        d.line([(qx - 5 * math.sin(phi), qy - 5 * math.cos(phi)), (qx + 5 * math.sin(phi) + 3 * math.cos(phi), qy + 5 * math.cos(phi) - 3 * math.sin(phi))], fill=STO)
    for x in range(36, cx - 4, 8): d.line([(x, 198), (x + 5, 188)], fill=STO)
    dell(img, [cx - rp, cy - rp, cx + rp, cy + rp], (244, 150, 60), (226, 128, 44), (120, 60, 20))
    d.rectangle([cx - 3, cy - 3, cx - 1, cy - 1], fill=(255, 230, 190))
    rx = ex + 30 * math.cos(phi) + 15 * math.sin(phi); ry = ey - 30 * math.sin(phi) + 15 * math.cos(phi)
    dell(img, [rx - 8, ry - 8, rx + 8, ry + 8], (176, 188, 208), (156, 168, 190), (60, 70, 96))
    drect(img, (14, 204, 76, 252), (150, 162, 184), (132, 144, 168), (60, 70, 96))
    drect(img, (22, 176, 40, 206), (176, 188, 208), (156, 168, 190), (60, 70, 96))
    drect(img, (52, 176, 70, 206), (176, 188, 208), (156, 168, 190), (60, 70, 96))
    return img, d

# ---------------- HUD ----------------
def zoomtxt(s):
    v = s / S0
    if v < 1.5: return 'ZOOM 1x'
    k = math.floor(math.log10(v)); m = v / 10 ** k; m = 5 if m >= 5 else 2 if m >= 2 else 1
    return 'ZOOM ' + '{:,}'.format(int(m * 10 ** k)).replace(',', '.') + 'x'
SB = [(10, '1 cm'), (1, '1 mm'), (0.1, '0,1 mm'), (0.01, '10 µm'), (1e-3, '1 µm'), (1e-4, '0,1 µm'), (1e-5, '10 nm'), (1e-6, '1 nm')]
def scale_bar(d, s):
    for L, t in SB:
        if L * s <= 90:
            w = L * s; x, y = 8, 338
            d.rectangle([x - 1, y - 1, x + w + 1, y + 3], fill=(0, 0, 0)); d.rectangle([x, y, x + w, y + 2], fill=(255, 255, 255))
            ptext(d, x, y - 14, t); return

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

def zoomframe(b, tags=True):
    s0 = 10 ** logs(b); s = s0 * punch(b)
    c = camera(s0)
    st = dict(eps=0.035 * sm(b, 31, 33) + 0.008 * math.exp(-5 * (b % 1.0)) * (b >= 31), slip=stepk(b, 33, 6) * 1.0)
    img = field(s, c[0], c[1], st)
    P = lambda x, y: (108 + (x - c[0]) * s, 192 + (y - c[1]) * s)
    d = ImageDraw.Draw(img)
    if not tags: return img
    if b < 9:
        tg(d, b, 4.4, 6.0, 'BARRA CA-50 CORTADA', 20, 84, P(CBX - 2, CBY - RB + 0.3))
        tg(d, b, 5.0, 6.6, 'CASCA MAIS DURA', 90, 310, P(CBX + 2.5, CBY + RB - 0.45))
    if 9 <= b < 14.2:
        s9 = 10 ** 3.5; c9 = camera(s9)
        tg(d, b, 9.3, 14.0, 'GRÃOS DE FERRO', 110, 84, P(*find('g1', s9, c9, 'fer', (70, 100, 200, 180))))
        tg(d, b, 10.6, 14.0, 'FERRO + CARBONO', 12, 306, P(*find('g2', s9, c9, 'pea', (20, 200, 200, 290))))
    if 18 <= b < 22.2:
        s18 = 10 ** 5.0; c18 = camera(s18)
        tg(d, b, 18.3, 22.0, 'LÂMINAS DURAS', 14, 84, P(*find('l1', s18, c18, 'cem', (10, 110, 206, 290))))
        tg(d, b, 19.3, 22.0, 'FERRO MACIO', 120, 306, P(*find('l2', s18, c18, 'fer', (10, 110, 206, 290))))
    if 27 <= b < 40:
        tg(d, b, 27.3, 30.6, 'ÁTOMOS DE FERRO', 16, 84, P(-2 * A, -3 * A))
        tg(d, b, 28.3, 30.6, 'CARBONO', 140, 306, P(*CARB))
        if 31 <= b < 39.5:
            ph = (b % 1.0); o = 4 * math.exp(-4 * ph)
            for sx, x0 in ((-1, 40), (1, 176)):
                y = 150 if sx < 0 else 234
                d.line([(x0, y), (x0 + sx * (22 + o), y)], fill=(0, 0, 0), width=5); d.line([(x0, y), (x0 + sx * (22 + o), y)], fill=(255, 255, 255), width=3)
                tipx = x0 + sx * (30 + o)
                d.polygon([(tipx, y), (tipx - sx * 9, y - 7), (tipx - sx * 9, y + 7)], fill=(255, 255, 255), outline=(0, 0, 0))
        if 31.2 <= b < 33.2: ptext(d, 108, 84, 'PUXANDO A BARRA', anchor='ma')
        if 33.3 <= b < 36.6: ptext(d, 108, 84, 'OS ÁTOMOS ESCORREGAM', anchor='ma')
        if 36.8 <= b < 39.5: ptext(d, 108, 84, 'MAS NÃO SE SOLTAM', anchor='ma')
    counter(d, zoomtxt(s0)); scale_bar(d, s)
    return img

def frame(t, tags=True):
    b = t / B
    if b < 3.2:
        img, d = saw(b)
        if tags: tg(d, b, 0.4, 3.0, 'BARRA DE AÇO CA-50', 14, 110, (60, 186))
    elif b < 4.3:
        a, _ = saw(b); img = dissolve(a, zoomframe(b, tags), sm(b, 3.3, 4.3))
    elif b < 47.6:
        img = zoomframe(b, tags)
    else:
        e, d = bend(b)
        if tags and b >= 52: bigword(d, ['DOBRA', 'SEM QUEBRAR'], 292, eout(sm(b, 52, 52.35)))
        if b >= 52:
            for i in range(6):
                rr = random.Random(i * 7 + int(b * 2)); x, y = rr.uniform(100, 200), rr.uniform(120, 230); L = 2 + (i + int(b * 2)) % 3
                d.line([(x - L, y), (x + L, y)], fill=(255, 255, 255)); d.line([(x, y - L), (x, y + L)], fill=(255, 255, 255))
        img = e if b >= 48.6 else dissolve(zoomframe(b, tags), e, sm(b, 47.6, 48.6))
    return img.resize((OUTW, OUTH), Image.NEAREST)

def capa():
    s = 10 ** 3.62; c = camera(s)
    out = field(s, c[0], c[1], {}).resize((OUTW, OUTH), Image.NEAREST)
    d = ImageDraw.Draw(out, 'RGBA'); d.rectangle([0, 0, OUTW, OUTH], fill=(0, 0, 0, 40))
    t1 = Image.new('RGBA', (1300, 400), (0, 0, 0, 0)); dt = ImageDraw.Draw(t1)
    dt.rectangle([0, 20, 1300, 380], fill=(8, 8, 10, 235))
    dt.text((650, 130), 'POR DENTRO', font=ImageFont.truetype(C.MONT % 900, 136), fill=(245, 190, 45), stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    dt.text((650, 290), 'DO AÇO CA-50', font=ImageFont.truetype(C.MONT % 900, 104), fill=(255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0), anchor='mm')
    t1 = t1.rotate(4, expand=True, resample=Image.BICUBIC)
    out = out.convert('RGB'); out.paste(t1, (540 - t1.size[0] // 2, 520 - t1.size[1] // 2), t1)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        bs = [float(x) for x in sys.argv[2].split(',')]
        ims = [frame(x * B) for x in bs]
        cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 270, rows * 492), (255, 255, 255)); dd = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            sheet.paste(im.resize((270, 480), Image.NEAREST), ((k % cols) * 270, (k // cols) * 492))
            dd.text(((k % cols) * 270 + 4, (k // cols) * 492 + 481), 'b%.2f' % bs[k], fill=(0, 0, 0))
        sheet.save(sys.argv[3])
    else:
        cp = capa(); cp.save('capa-barra.png')
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', 'barra_noaudio.mp4'], stdin=subprocess.PIPE)
        for _ in range(2): p.stdin.write(cp.tobytes())
        for n in range(int(VD * FPS)):
            p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); print('done', VD)
