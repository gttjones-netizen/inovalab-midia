import math, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cura as C
from cura import (W0, H0, OUTW, OUTH, FPS, B, checker, dpoly, drect, dell, ptext, tag, PIX,
                  clamp, sm, ease, eout, lerp, WHITE)

NB = 56
VD = NB * B
PIXB = ImageFont.truetype('fontsource-pixelify-sans-5.3.0/package/files/pixelify-sans-latin-700-normal.woff2', 26)

# ---------- palette ----------
MINT, MINTL = (156, 220, 200), (176, 232, 214)
CO1, CO2, COO = (214, 210, 202), (202, 198, 190), (92, 88, 86)
COSH, COHI = (178, 174, 168), (236, 234, 228)
REC1, REC2 = (150, 144, 138), (136, 130, 124)
ST1, ST2, STO, STH = (150, 178, 216), (124, 152, 196), (46, 62, 100), (226, 238, 252)
RU1, RU2, RUO, RUD = (240, 132, 44), (210, 96, 32), (112, 44, 18), (160, 66, 24)
PR1, PR2, PRO, PRH = (138, 104, 244), (114, 82, 218), (56, 36, 138), (198, 180, 255)
MO1, MO2, MOO = (232, 224, 206), (220, 212, 194), (150, 142, 124)
SKY1, SKY2 = (150, 206, 242), (140, 199, 238)
WAT, WATH = (52, 132, 255), (210, 232, 255)
OXY, OXYO, HYD = (236, 60, 70), (120, 20, 34), (246, 246, 250)
TE1, TE2 = (34, 98, 108), (30, 90, 101)

def punch(b):
    f = b % 1.0
    return 1 + (0.075 if int(b) % 4 == 0 else 0.04) * math.exp(-6 * f)

def stepk(b, b0, n):
    if b < b0: return 0.0
    x = b - b0
    return clamp((math.floor(x) + eout(min(1.0, (x % 1.0) * 2.5))) / n)

def dot(d, X, Y, q, fill):
    X = int(X); Y = int(Y); d.rectangle([X, Y, X + max(0, int(q) - 1), Y + max(0, int(q) - 1)], fill=fill)

def mkP(s, cx, cy):
    return lambda x, y: (108 + (x - cx) * s, 192 + (y - cy) * s)

def irr(cx, cy, r, seed, n=9, amp=0.28):
    rr = random.Random(seed)
    return [(cx + r * (1 + rr.uniform(-amp, amp)) * math.cos(2 * math.pi * i / n),
             cy + r * (1 + rr.uniform(-amp, amp)) * math.sin(2 * math.pi * i / n)) for i in range(n)]

BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32
BAYT = np.tile(BAY, (H0 // 4, W0 // 4))[..., None]
def dissolve(a, b_, k):
    if k <= 0: return a
    if k >= 1: return b_
    return Image.fromarray(np.where(k > BAYT, np.asarray(b_), np.asarray(a)).astype(np.uint8))

def sphere(img, d, x, y, r, c1, c2, o):
    dell(img, [x - r, y - r, x + r, y + r], c1, c2, o)
    if r >= 3:
        hr = max(1, r * 0.22)
        d.ellipse([x - r * 0.45 - hr, y - r * 0.45 - hr, x - r * 0.45 + hr, y - r * 0.45 + hr], fill=(255, 255, 255))

# =====================================================================
# PILLAR (front view). world units ~ mm/2
# =====================================================================
_r = random.Random(5)
PORES = [(_r.uniform(-36, 36), _r.uniform(-126, 130)) for _ in range(90)]
HAIR = [(5 + _r.uniform(-2.2, 2.2), y) for y in range(-42, 43, 6)]
CHUNK = [(-12, -44), (4, -51), (20, -41), (25, -12), (21, 22), (14, 46), (-2, 51), (-14, 35), (-18, 0)]
DRIPS = [(-1, -22, 70, 1.2), (3, 6, 120, 1.8), (7, -34, 60, 1.2), (9, 30, 95, 1.5), (5, 40, 150, 1.2), (12, 14, 50, 1)]
RBUMP = [(_r.uniform(-1, 1), _r.uniform(1.8, 3.4)) for _ in range(60)]
RECDOT = [(_r.uniform(-20, 26), _r.uniform(-52, 52)) for _ in range(70)]
HT, HB = -52.0, 52.0

def pillar(b, s, cx, cy, st):
    P = mkP(s, cx, cy)
    img = Image.new('RGB', (W0, H0), MINT); d = ImageDraw.Draw(img)
    for g in range(-480, 481, 40):
        x = P(g, 0)[0]; y = P(0, g + 10)[1]
        if 0 <= x < W0: d.line([(x, 0), (x, H0)], fill=MINTL)
        if 0 <= y < H0: d.line([(0, y), (W0, y)], fill=MINTL)
    xl, yt = P(-38, -128); xr, yb = P(38, 132)
    # floor and beam
    if yb < H0:
        drect(img, (-2, yb, W0 + 2, H0 + 2), (120, 184, 168), (110, 174, 158)); d.line([(0, yb), (W0, yb)], fill=(60, 110, 100))
    if yt > 0:
        drect(img, (-2, -2, W0 + 2, yt), (196, 192, 186), (184, 180, 174)); d.line([(0, yt), (W0, yt)], fill=COO)
    for i in range(st.get('rainbg', 0)):
        u = (b * 1.1 + i * 0.137) % 1.0; X = (i * 53) % 260 - 20 - u * 30; Y = u * (H0 + 40) - 20 + (i * 71) % 60 - 30
        d.line([(X, Y), (X - 2, Y + 7)], fill=(226, 246, 250))
    # pillar
    drect(img, (xl, yt, xr, yb), CO1, CO2)
    xs = P(26, 0)[0]; drect(img, (xs, yt, xr, yb), COSH, (168, 164, 158))
    xh = P(-34, 0)[0]; d.rectangle([xl, yt, xh, yb], fill=COHI)
    for g in range(-96, 131, 64):
        y = P(0, g)[1]
        if 0 <= y < H0: d.line([(xl, y), (xr, y)], fill=(188, 184, 176))
    pr = max(1, int(s * 0.5))
    for (x, y) in PORES:
        X, Y = P(x, y)
        if -2 < X < W0 and -2 < Y < H0: dot(d, X, Y, pr, (176, 172, 164))
    d.line([(xl, yt), (xl, yb)], fill=COO); d.line([(xr, yt), (xr, yb)], fill=COO)
    # water running down the face
    for i in range(st.get('wet', 0)):
        u = (b * 0.55 + i * 0.37) % 1.0
        x = 5 + (i % 3 - 1) * 2.5; y = -128 + u * 128 if i % 2 == 0 else -90 + u * 90
        X, Y = P(x, y); L = max(3, 4 * s)
        d.rectangle([X, Y - L, X + max(1, s * 0.6), Y], fill=WAT); d.point((X, Y - L), fill=WATH)
    # rust stain
    sk = st.get('stain', 0)
    if sk > 0:
        for (x, y0, L, w) in DRIPS:
            X0, Y0 = P(x, y0); X1, Y1 = P(x + w, y0 + L * sk * 0.55); X2, Y2 = P(x + w * 0.5, y0 + L * sk)
            d.rectangle([X0, Y0, max(X0, X1), max(Y0, Y1)], fill=(222, 146, 92))
            m = Image.new('L', img.size, 0); ImageDraw.Draw(m).rectangle([X0, Y1, max(X0, X2), max(Y1, Y2)], fill=255)
            img.paste(checker((222, 146, 92), CO2, W0, H0), (0, 0), m)
    # hairline crack
    ck = st.get('crack', 0)
    if ck > 0 and not st.get('hole'):
        n = len(HAIR); mid = n // 2; reach = ck * mid
        pts = [P(*HAIR[i]) for i in range(n) if abs(i - mid) <= reach + 0.01]
        if len(pts) > 1:
            w = max(2, int(s * 0.9))
            d.line(pts, fill=(52, 44, 44), width=w)
    bk = st.get('big', 0)
    if bk > 0 and not st.get('hole'):
        pts = [P(*p) for p in CHUNK] + [P(*CHUNK[0])]
        n = max(2, int(len(pts) * bk + 0.5))
        d.line(pts[:n], fill=(52, 44, 44), width=max(1, int(s * 0.6)))
    # hole with rebar
    if st.get('hole'):
        clean, prim, mort = st.get('clean', 0), st.get('prim', 0), st.get('mort', 0)
        lay = img.copy(); ld = ImageDraw.Draw(lay)
        hp = [P(*p) for p in CHUNK]
        dpoly(lay, hp, REC1, REC2)
        for (x, y) in RECDOT:
            X, Y = P(x, y); ld.rectangle([X, Y, X + pr, Y + pr], fill=(118, 112, 108))
        yc = HT + clean * (HB - HT); yp = HT + prim * (HB - HT)
        def bar(x0, x1, y0, y1, vert):
            # zones along y: primer / steel / rust
            for (a, e, kind) in ((y0, min(y1, yp), 'p'), (max(y0, yp), min(y1, yc), 's'), (max(y0, yc), y1, 'r')):
                if e <= a: continue
                c1, c2, o, h = {'p': (PR1, PR2, PRO, PRH), 's': (ST1, ST2, STO, STH), 'r': (RU1, RU2, RUO, RU1)}[kind]
                g = 1.6 if kind == 'r' else 0
                A = P(x0 - (g if vert else 0), a - (0 if vert else g)); E = P(x1 + (g if vert else 0), e + (0 if vert else g))
                drect(lay, (A[0], A[1], E[0], E[1]), c1, c2, o)
                if kind != 'r':
                    if vert:
                        hx = P(x0 + 1.6, 0)[0]; ld.line([(hx, A[1] + 1), (hx, E[1] - 1)], fill=h, width=max(1, int(s * 0.5)))
                        yy = math.ceil(a / 7) * 7
                        while yy < e - 3:
                            p0 = P(x0 + 0.5, yy + 3); p1 = P(x1 - 0.5, yy)
                            if p0[1] < E[1]: ld.line([p0, p1], fill=o)
                            yy += 7
                    else:
                        hy = P(0, y0 + 0.8)[1]; ld.line([(A[0] + 1, hy), (E[0] - 1, hy)], fill=h)
                else:
                    if vert:
                        k = 0; yy = a
                        while yy < e:
                            j, rr = RBUMP[int(yy - HT) % 60]
                            X, Y = P((x0 - 1.5) if k % 2 == 0 else (x1 + 1.5), yy); R = rr * s * 0.75
                            dell(lay, [X - R, Y - R, X + R, Y + R], RU1, RU2, RUO)
                            X2, Y2 = P((x0 + x1) / 2 + j * 2.5, yy + 2); ld.rectangle([X2, Y2, X2 + pr, Y2 + pr], fill=RUD)
                            yy += 5; k += 1
        bar(-24, 30, -24, -21, False); bar(-24, 30, 22, 25, False)
        bar(1.5, 8.5, HT - 2, HB + 2, True)
        if mort > 0:
            ym = HB - mort * (HB - HT)
            A = P(-30, ym); E = P(34, HB + 6)
            drect(lay, (A[0], A[1], E[0], E[1]), MO1, MO2)
            if mort < 1: ld.line([(A[0], A[1]), (E[0], A[1])], fill=MOO, width=max(1, int(s * 0.5)))
        m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(hp, fill=255)
        img.paste(lay, (0, 0), m)
        d.polygon(hp, outline=MOO if mort >= 1 else (60, 52, 50))
        if mort < 1 and s > 1.6:
            d.line([hp[0], hp[1], hp[2]], fill=(60, 52, 50), width=2)
    # falling chunk
    cf = st.get('chunk')
    if cf is not None:
        dx, dy = cf
        cp = [P(x + dx, y + dy) for (x, y) in CHUNK]
        if min(p[1] for p in cp) < H0 + 5:
            dpoly(img, cp, CO1, CO2, COO)
    # tools
    tl = st.get('tool')
    if tl:
        kind, tx, ty = tl; X, Y = P(tx, ty); u = s / 3.0
        if kind == 'brush':
            drect(img, (X + 8 * u, Y - 5 * u, X + 70 * u, Y + 5 * u), (236, 160, 86), (218, 140, 70), (120, 70, 30))
            drect(img, (X - 22 * u, Y - 9 * u, X + 26 * u, Y + 9 * u), (206, 130, 64), (188, 112, 52), (110, 62, 26))
            for i in range(-20, 25, 5):
                d.line([(X + i * u, Y + 9 * u), (X + (i - 2) * u, Y + 19 * u)], fill=(232, 236, 240), width=max(1, int(u)))
                d.line([(X + i * u, Y - 9 * u), (X + (i + 2) * u, Y - 19 * u)], fill=(190, 198, 208), width=max(1, int(u)))
            for i in range(12):
                ph = (b * 2.3 + i * 0.173) % 1.0; a = i * 2.4
                px = X + math.cos(a) * ph * 46 * u; py = Y + math.sin(a) * ph * 30 * u + ph * ph * 40 * u
                d.rectangle([px, py, px + 2, py + 2], fill=RU1 if i % 2 else RUD)
        elif kind == 'paint':
            dpoly(img, [(X + 14 * u, Y - 20 * u), (X + 60 * u, Y - 78 * u), (X + 68 * u, Y - 70 * u), (X + 24 * u, Y - 12 * u)], (236, 160, 86), (218, 140, 70), (120, 70, 30))
            dpoly(img, [(X + 4 * u, Y - 30 * u), (X + 16 * u, Y - 22 * u), (X + 26 * u, Y - 10 * u), (X + 30 * u, Y + 2 * u), (X + 12 * u, Y - 8 * u)], (206, 214, 224), (180, 190, 204), (80, 90, 110))
            dpoly(img, [(X - 16 * u, Y + 6 * u), (X + 4 * u, Y - 30 * u), (X + 30 * u, Y + 2 * u), (X + 2 * u, Y + 14 * u)], PR1, PR2, PRO)
        elif kind == 'trowel':
            dpoly(img, [(X - 44 * u, Y), (X + 30 * u, Y - 12 * u), (X + 30 * u, Y + 10 * u)], (214, 224, 236), (188, 200, 216), (70, 84, 108))
            drect(img, (X + 30 * u, Y - 5 * u, X + 46 * u, Y + 3 * u), (150, 160, 176), (130, 140, 158), (70, 84, 108))
            drect(img, (X + 46 * u, Y - 8 * u, X + 84 * u, Y + 6 * u), (236, 160, 86), (218, 140, 70), (120, 70, 30))
    # sparkles
    for i in range(st.get('spark', 0)):
        rr = random.Random(i * 7 + int(b * 2)); X, Y = P(rr.uniform(-34, 34), rr.uniform(-110, 110))
        L = 2 + (i + int(b * 2)) % 3
        d.line([(X - L, Y), (X + L, Y)], fill=(255, 255, 255)); d.line([(X, Y - L), (X, Y + L)], fill=(255, 255, 255))
    return img, P

# =====================================================================
# SECTION (horizontal cut, face up). units mm
# =====================================================================
BX, BY, BR = 0.0, 44.0, 8.0
_r = random.Random(11)
STONES = []
for _ in range(1400):
    x, y, r = _r.uniform(-150, 150), _r.uniform(5, 250), _r.uniform(3, 9.5)
    if math.hypot(x - BX, y - BY) < r + 17: continue
    if 20 < y + r and y - r < 30: continue
    if abs(x) < r + 3 and y - r < 36: continue
    if any(math.hypot(x - a, y - c) < r + e + 1.2 for (a, c, e, _, _) in STONES): continue
    STONES.append((x, y, r, _r.randrange(10 ** 6), _r.randrange(3)))
STCOL = [((152, 174, 208), (136, 158, 194), (70, 86, 120)), ((186, 170, 158), (170, 154, 142), (96, 80, 70)), ((210, 198, 164), (196, 184, 150), (116, 104, 72))]
SAND = [(_r.uniform(-150, 150), _r.uniform(2, 250)) for _ in range(900)]
SHAIR = [(_r.uniform(-1.3, 1.3), y) for y in np.linspace(0, 35.5, 9)]
WEDGE = [[(-7, 40), (-13, 30), (-17, 21), (-24, 11), (-28, 0)], [(7, 40), (12, 31), (19, 20), (22, 10), (29, 0)]]
RRN = [_r.uniform(0.6, 1.35) for _ in range(40)]

def section(b, s, cx, cy, st):
    P = mkP(s, cx, cy)
    img = checker(SKY1, SKY2, W0, H0).copy(); d = ImageDraw.Draw(img)
    ys = P(0, 0)[1]
    for i in range(st.get('rain', 0)):
        u = (b * 0.9 + i * 0.313) % 1.0; x = -60 + (i * 37) % 120
        X, Y = P(x - u * 6, -70 + u * 70)
        if Y < ys - 2: d.line([(X, Y), (X - 1, Y - 5)], fill=WATH)
    drect(img, (-2, ys, W0 + 2, H0 + 2), CO1, CO2)
    if s > 0.6:
        pr = max(1, int(s * 0.45))
        for (x, y) in SAND:
            X, Y = P(x, y)
            if 0 <= X < W0 and ys <= Y < H0: dot(d, X, Y, pr, (182, 176, 166))
    for (x, y, r, sd, c) in STONES:
        X, Y = P(x, y); R = r * s * 1.3
        if X + R < 0 or X - R > W0 or Y + R < 0 or Y - R > H0: continue
        c1, c2, o = STCOL[c]
        if R < 1.5: d.rectangle([X, Y, X + 1, Y + 1], fill=c2)
        else:
            dpoly(img, [P(*p) for p in irr(x, y, r, sd)], c1, c2, o)
            if R > 5: d.line([P(x - r * 0.5, y - r * 0.35), P(x - r * 0.1, y - r * 0.55)], fill=(255, 255, 255))
    d.line([(0, ys), (W0, ys)], fill=COO, width=max(1, int(s * 0.3)))
    rust = st.get('rust', 0)
    # stirrup
    A = P(-200, 22.5); E = P(200, 27.5)
    if rust > 0.5:
        drect(img, (A[0], A[1] - 0.25 * rust * s, E[0], E[1] + 0.25 * rust * s), RU1, RU2, RUO)
    drect(img, (A[0], A[1], E[0], E[1]), ST1, ST2, STO)
    d.line([(0, A[1] + max(1, s * 0.9)), (W0, A[1] + max(1, s * 0.9))], fill=STH)
    # cracks
    if st.get('hair', 1) > 0:
        d.line([P(*p) for p in SHAIR], fill=(52, 44, 44), width=max(1, int(s * 0.45)))
    ck = st.get('crk', 0)
    if ck > 0:
        for wl in WEDGE:
            n = ck * (len(wl) - 1); pts = [P(*wl[i]) for i in range(int(n) + 1)]
            if int(n) < len(wl) - 1:
                f = n - int(n); a, e = wl[int(n)], wl[int(n) + 1]
                pts.append(P(a[0] + (e[0] - a[0]) * f, a[1] + (e[1] - a[1]) * f))
            if len(pts) > 1: d.line(pts, fill=(52, 44, 44), width=max(1, int(s * (0.5 + 0.5 * ck))))
    # rust ring + steel
    if rust > 0:
        n = len(RRN)
        pts = [P(BX + (BR + rust * RRN[i]) * math.cos(2 * math.pi * i / n), BY + (BR + rust * RRN[i]) * math.sin(2 * math.pi * i / n)) for i in range(n)]
        dpoly(img, pts, RU1, RU2, RUO)
        for i in range(0, n, 3):
            rr = BR + rust * RRN[i] * 0.55; X, Y = P(BX + rr * math.cos(2 * math.pi * i / n), BY + rr * math.sin(2 * math.pi * i / n))
            q = max(1, int(s * 0.5)); d.rectangle([X, Y, X + q, Y + q], fill=RUD)
    rs = BR - 0.22 * rust
    A = P(BX - rs, BY - rs); E = P(BX + rs, BY + rs)
    col = st.get('steel', 's')
    c1, c2, o = (PR1, PR2, PRO) if col == 'p' else (ST1, ST2, STO)
    dell(img, [A[0], A[1], E[0], E[1]], c1, c2, o)
    R = rs * s
    if R < 400: d.arc([A[0] + R * 0.22, A[1] + R * 0.22, E[0] - R * 0.22, E[1] - R * 0.22], 195, 255, fill=STH, width=max(1, int(R / 7)))
    pk = st.get('ring', 0)
    if pk > 0:
        rp = (BR + 1.6) * s; X, Y = P(BX, BY)
        for i in range(24):
            if (i + int(b * 4)) % 24 < 24 * pk and i % 2 == 0:
                d.arc([X - rp, Y - rp, X + rp, Y + rp], i * 15, i * 15 + 13, fill=(110, 255, 196), width=max(1, int(s * 0.5)))
    # intruders: water + oxygen along the hairline
    for i in range(st.get('intr', 0)):
        u = (b * 0.5 + i / max(1, st['intr'])) % 1.0
        if u < 0.35:
            k = u / 0.35; x = lerp((i * 29) % 50 - 25, SHAIR[0][0], k); y = lerp(-34, 0, k)
        else:
            k = (u - 0.35) / 0.65 * (len(SHAIR) - 1); j = min(int(k), len(SHAIR) - 2); f = k - j
            x = lerp(SHAIR[j][0], SHAIR[j + 1][0], f); y = lerp(SHAIR[j][1], SHAIR[j + 1][1], f)
        X, Y = P(x, y); q = max(1.5, s * 0.75)
        if i % 2 == 0:
            d.polygon([(X, Y - 2 * q), (X + q, Y), (X, Y + q), (X - q, Y)], fill=WAT, outline=(10, 40, 120)); d.point((X, Y - 1), fill=WATH)
        else:
            for sx in (-1, 1): d.ellipse([X + sx * q * 0.8 - q, Y - q, X + sx * q * 0.8 + q, Y + q], fill=OXY, outline=OXYO)
    # push arrows
    ak = st.get('arrows', 0)
    if ak > 0:
        pu = (b % 1.0)
        for ang in (-150, -90, -30):
            a = math.radians(ang); r0 = BR + rust + 2 + pu * 2; r1 = r0 + 6
            p0 = P(BX + r0 * math.cos(a), BY + r0 * math.sin(a)); p1 = P(BX + r1 * math.cos(a), BY + r1 * math.sin(a))
            d.line([p0, p1], fill=(0, 0, 0), width=3); d.line([p0, p1], fill=(255, 255, 255), width=1)
            for da in (-0.5, 0.5):
                p2 = P(BX + (r1 - 2.5) * math.cos(a + da * 0.35), BY + (r1 - 2.5) * math.sin(a + da * 0.35))
                d.line([p1, p2], fill=(255, 255, 255), width=1)
    return img, P

# =====================================================================
# MOLECULES
# =====================================================================
SITES = [0, -3, 3, -1, 2, -4]
FLOAT = [('w', -70, -150), ('o', 52, -168), ('w', 64, -96), ('o', -30, -205), ('w', -84, -70), ('o', 86, -40), ('w', 10, -120), ('o', -88, -118), ('w', 30, -62), ('w', -40, -30)]
def water(img, d, X, Y, s, ang=0.0):
    r = 5.5 * s
    for sg in (-1, 1):
        a = ang + sg * 0.95 - math.pi / 2
        sphere(img, d, X + math.cos(a) * r * 1.25, Y + math.sin(a) * r * 1.25, r * 0.62, HYD, (222, 226, 236), (90, 96, 120))
    sphere(img, d, X, Y, r, OXY, (212, 44, 58), OXYO)
def oxy2(img, d, X, Y, s, ang=0.0):
    r = 5.5 * s
    for sg in (-1, 1):
        sphere(img, d, X + sg * math.cos(ang) * r * 0.85, Y + sg * math.sin(ang) * r * 0.85, r, OXY, (212, 44, 58), OXYO)

def molec(b, s, cx, cy):
    P = mkP(s, cx, cy)
    img = checker(TE1, TE2, W0, H0).copy(); d = ImageDraw.Draw(img)
    for i in range(-6, 12):
        X, Y = P(-300, -260 + i * 60); X2, Y2 = P(300, -330 + i * 60)
        d.line([(X, Y), (X2, Y2)], fill=(40, 108, 118))
    a = 20.0; r = 9.6 * s
    conv = {}
    for e, si in enumerate(SITES):
        if b >= 22 + e: conv[si] = b - (22 + e)
    xmin = cx - 108 / s - a; xmax = cx + 108 / s + a; ymax = cy + 192 / s + a
    j = 0
    while j * a * 0.866 < ymax:
        y = j * a * 0.866; off = 0.5 * a * (j % 2)
        i0 = int(math.floor((xmin - off) / a)); i1 = int(math.ceil((xmax - off) / a))
        for i in range(i0, i1 + 1):
            if j == 0 and i in conv: continue
            X, Y = P(i * a + off, y)
            if r < 1.6: d.rectangle([X, Y, X + 1, Y + 1], fill=ST1 if (i + j) % 2 else ST2)
            else: sphere(img, d, X, Y, r, ST1, ST2, STO)
        j += 1
    for k, (kind, x, y) in enumerate(FLOAT):
        X, Y = P(x + 7 * math.sin(b * 1.3 + k * 1.7), y + 6 * math.cos(b * 1.1 + k))
        (water if kind == 'w' else oxy2)(img, d, X, Y, s, b * 0.6 + k)
    last = None
    for e, si in enumerate(SITES):
        be = 22 + e; x = si * a
        if be - 1 <= b < be:
            u = ease(b - (be - 1))
            X, Y = P(lerp(x - 70, x - 8, u), lerp(-170, -17, u)); water(img, d, X, Y, s, b * 3)
            X, Y = P(lerp(x + 80, x + 9, u), lerp(-190, -19, u)); oxy2(img, d, X, Y, s, b * 3)
        elif b >= be:
            k = eout(sm(b, be, be + 0.4)); yy = -7 * k
            for (ox, oy, rr, c) in ((-12, -11, 6, 'o'), (12, -11, 6, 'o'), (0, -19, 6, 'o'), (-17, -20, 3.6, 'h'), (17, -20, 3.6, 'h'), (-9, -29, 7.5, 'f'), (9, -31, 7.5, 'f'), (0, -42, 5.5, 'o')):
                X, Y = P(x + ox * (0.5 + 0.5 * k), yy + oy * k)
                if c == 'o': sphere(img, d, X, Y, rr * s, OXY, (212, 44, 58), OXYO)
                elif c == 'h': sphere(img, d, X, Y, rr * s, HYD, (222, 226, 236), (90, 96, 120))
                else: sphere(img, d, X, Y, rr * s, RU1, RU2, RUO)
            X, Y = P(x, yy); sphere(img, d, X, Y, r, RU1, RU2, RUO)
            fl = b - be
            if fl < 0.4:
                R = (8 + 60 * fl) * s; d.ellipse([X - R, Y - R - 10 * s, X + R, Y + R - 10 * s], outline=(255, 255, 255))
            last = (x, yy - 30)
    return img, P, last

# =====================================================================
def hud(d, rustf, protf):
    for i, (lab, f, col) in enumerate((('FERRUGEM', rustf, RU1), ('PROTEÇÃO', protf, (110, 255, 196)))):
        y = 52 + i * 13
        ptext(d, 8, y, lab)
        d.rectangle([66, y + 3, 118, y + 9], fill=(22, 26, 40), outline=(0, 0, 0))
        if f > 0.02: d.rectangle([67, y + 4, 67 + int(50 * clamp(f)), y + 8], fill=col)

def tg(d, b, b0, b1, s, tx, ty, o):
    if b0 <= b < b1:
        w = PIX.getlength(s); tx = clamp(tx, 5, W0 - 5 - w)
        tag(d, s, tx, ty, o[0], o[1], min(sm(b, b0, b0 + 0.5) + 0.05, 1.0))

def rust_at(b): return 5.0 * stepk(b, 12, 8)

def frame(t, tags=True):
    b = t / B; pu = punch(b)
    hudon = False; rustf = 0; protf = 1
    if b < 7.3:
        if b < 4: s = lerp(1.22, 1.32, b / 4) * pu
        else: s = 10 ** lerp(math.log10(1.32), math.log10(16), ease(sm(b, 4, 8))) * pu
        sh = 2.0 * math.exp(-5 * (b % 1.0)) if 1 <= b < 4 else 0
        rr = random.Random(int(t * 60))
        st = dict(crack=0.25 + 0.75 * stepk(b, 1, 3), wet=7, rainbg=26)
        img, P = pillar(b, s, 5 + rr.uniform(-1, 1) * sh / s, rr.uniform(-1, 1) * sh / s, st)
        if tags:
            d = ImageDraw.Draw(img)
            tg(d, b, 1.3, 4.0, 'TRINCA', 150, 150, P(7, -8))
            tg(d, b, 2.3, 4.0, 'ÁGUA DA CHUVA', 20, 100, P(4, -70))
    if 6.0 <= b < 21.8:
        if b < 8: s = 10 ** lerp(math.log10(0.8), math.log10(2.6), ease(sm(b, 5.6, 8))) * pu; c = (0, 31)
        elif b < 20: s = lerp(2.6, 2.9, (b - 8) / 12) * pu; c = (0, 31)
        else:
            k = ease(sm(b, 20, 22)); s = 10 ** lerp(math.log10(2.9), math.log10(60), k) * pu; c = (lerp(0, 0, k), lerp(31, BY - BR - 0.3, eout(k)))
        rust = rust_at(b)
        st = dict(rust=rust, ring=1 - sm(b, 10.6, 12), intr=10 if b < 20 else 0, rain=8,
                  crk=stepk(b, 16, 4), arrows=1 if 15.5 <= b < 20 else 0)
        im2, P = section(b, s, c[0], c[1], st)
        if tags and 8 <= b < 20:
            d = ImageDraw.Draw(im2)
            tg(d, b, 8.3, 10.4, 'ÁGUA + AR ENTRAM', 100, 78, P(0, 4))
            tg(d, b, 8.3, 10.4, 'AÇO', 160, 290, P(3, 48))
            tg(d, b, 10.6, 12.4, 'A PROTEÇÃO SOME', 60, 300, P(-6, 51.5))
            tg(d, b, 12.6, 15.6, 'FERRUGEM', 140, 300, P(8, 53))
            tg(d, b, 16.2, 19.7, 'INCHA E RACHA', 12, 300, P(-17, 21))
        img = im2 if b >= 7.3 else dissolve(img, im2, sm(b, 6.0, 7.3))
        hudon = b >= 7.3; rustf = rust / 5; protf = 1 - sm(b, 10.6, 12)
    if 20.8 <= b < 29.3:
        if b < 22: s = 10 ** lerp(math.log10(0.3), 0, ease(sm(b, 20.4, 22))) * pu
        elif b < 28: s = lerp(1.0, 1.12, (b - 22) / 6) * pu
        else: s = 10 ** lerp(math.log10(1.12), math.log10(0.28), ease(sm(b, 28, 29.6))) * pu
        im3, P, last = molec(b, s, 0, -40)
        if tags and 22 <= b < 28:
            d = ImageDraw.Draw(im3)
            tg(d, b, 22.2, 24.4, 'FERRO', 150, 322, P(50, 52))
            tg(d, b, 22.2, 24.4, 'ÁGUA', 14, 78, P(-70, -150))
            tg(d, b, 22.2, 24.4, 'OXIGÊNIO', 140, 60, P(52, -168))
            if last: tg(d, b, 24.6, 27.8, 'VIRA FERRUGEM', 10, 110, P(last[0], last[1]))
        img = im3 if b >= 21.8 else dissolve(img, im3, sm(b, 20.8, 21.8))
        hudon = True; rustf = 1; protf = 0
    if b >= 28.4:
        hole = b >= 30
        if b < 30: s = 10 ** lerp(math.log10(12), math.log10(2.2), ease(sm(b, 28.2, 30))) * pu
        elif b < 46: s = lerp(2.2, 3.0, eout(sm(b, 30, 32.5))) * pu
        elif b < 48: s = 10 ** lerp(math.log10(3.0), math.log10(1.25), ease(sm(b, 46, 48))) * pu
        else: s = lerp(1.25, 1.15, (b - 48) / 8) * pu
        clean = stepk(b, 34, 4); prim = stepk(b, 38, 4); mort = stepk(b, 42, 4)
        st = dict(crack=1, stain=1 - sm(b, 46, 47.5), big=1, hole=hole, clean=clean, prim=prim, mort=mort)
        if hole:
            tt = (b - 30) * B; st['chunk'] = (14 * tt, 420 * tt * tt)
        wob = math.sin(b * 2 * math.pi)
        if 34 <= b < 38: st['tool'] = ('brush', 5 + 5 * math.sin(b * 4 * math.pi), HT + clean * 104 - 4 + 3 * wob)
        elif 38 <= b < 42: st['tool'] = ('paint', 5 + 2 * math.sin(b * 4 * math.pi), HT + prim * 104 - 3)
        elif 42 <= b < 46: st['tool'] = ('trowel', 2 + 9 * math.sin(b * 2 * math.pi), HB - mort * 104)
        if b >= 48: st['spark'] = 6; st['wet'] = 0
        sh = 4.0 * math.exp(-4 * (b - 30)) if 30 <= b < 31 else 0
        rr = random.Random(int(t * 60))
        im4, P = pillar(b, s, 5 + rr.uniform(-1, 1) * sh / s, rr.uniform(-1, 1) * sh / s, st)
        d = ImageDraw.Draw(im4)
        if tags:
            tg(d, b, 30.3, 31.9, 'O CONCRETO SOLTA', 30, 84, P(-10, -44))
            tg(d, b, 32.1, 33.9, 'AÇO ENFERRUJADO', 16, 325, P(4, 38))
            if 'tool' in st:
                tg(d, b, 34.3, 37.8, 'LIMPA A FERRUGEM', 14, 325 if clean < 0.5 else 84, P(st['tool'][1] - 6, st['tool'][2]))
                tg(d, b, 38.3, 41.8, 'PRIMER PROTEGE O AÇO', 8, 325 if prim < 0.5 else 84, P(5, HT + prim * 104 - 12) if prim > 0.5 else P(5, HT + prim * 104 + 2))
                tg(d, b, 42.3, 45.8, 'ARGAMASSA NOVA', 16, 84 if mort < 0.6 else 325, P(-8, HB - mort * 104 + 8))
            if b >= 48:
                k = eout(sm(b, 48, 48.35)); y = 104 - 10 * (1 - k)
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        d.text((108 + dx, y + dy), 'PROTEGIDA', font=PIXB, fill=(0, 0, 0), anchor='mm', fontmode='1')
                d.text((108, y), 'PROTEGIDA', font=PIXB, fill=(255, 255, 255), anchor='mm', fontmode='1')
        img = im4 if b >= 29.3 else dissolve(img, im4, sm(b, 28.4, 29.3))
        hudon = True; rustf = 1 - clean; protf = 0.5 * prim + 0.5 * mort
    if hudon and tags: hud(ImageDraw.Draw(img), rustf, protf)
    return img.resize((OUTW, OUTH), Image.NEAREST)

def capa():
    img, _ = section(18.3, 3.3, 0, 36, dict(rust=5, ring=0, intr=10, rain=8, crk=1, arrows=1))
    out = img.resize((OUTW, OUTH), Image.NEAREST)
    d = ImageDraw.Draw(out, 'RGBA'); d.rectangle([0, 0, OUTW, OUTH], fill=(0, 0, 0, 40))
    t1 = Image.new('RGBA', (1300, 400), (0, 0, 0, 0)); dt = ImageDraw.Draw(t1)
    dt.rectangle([0, 20, 1300, 380], fill=(8, 8, 10, 235))
    dt.text((650, 130), 'FERRUGEM', font=ImageFont.truetype(C.MONT % 900, 150), fill=(245, 190, 45), stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    dt.text((650, 290), 'NA ARMADURA', font=ImageFont.truetype(C.MONT % 900, 100), fill=(255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0), anchor='mm')
    t1 = t1.rotate(4, expand=True, resample=Image.BICUBIC)
    out.paste(t1, (540 - t1.size[0] // 2, 520 - t1.size[1] // 2), t1)
    return out.convert('RGB')

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
        cp = capa(); cp.save('capa-ferrugem.png')
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', 'ferrugem_noaudio.mp4'], stdin=subprocess.PIPE)
        for _ in range(2): p.stdin.write(cp.tobytes())
        for n in range(int(VD * FPS)):
            p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); print('done', VD)
