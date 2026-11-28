import math, random, sys, subprocess, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W0, H0 = 216, 384
OUTW, OUTH = 1080, 1920
FPS = 30
CFG = json.load(open('cfg.json')) if os.path.exists('cfg.json') else {}
BPM = CFG.get('bpm', 117.45)
OFF = CFG.get('offset', 0.0)      # time of first beat in the music
B = 60.0 / BPM
NBEATS = 55
VD = OFF + NBEATS * B
def tb(b): return OFF + b * B

PIX = ImageFont.truetype('fontsource-pixelify-sans-5.3.0/package/files/pixelify-sans-latin-700-normal.woff2', 11)
MONT = 'mont/files/montserrat-latin-%d-normal.woff2'


NAVY = (14, 24, 46)
_CK = {}
def checker(c1, c2, w=W0, h=600):
    k = (c1, c2, w, h)
    if k not in _CK:
        yy, xx = np.mgrid[0:h, 0:w]
        m = ((xx + yy) % 2 == 0)[..., None]
        _CK[k] = Image.fromarray(np.where(m, np.array(c1, np.uint8), np.array(c2, np.uint8)).astype(np.uint8))
    return _CK[k]
_HT = {}
def hatch(c1, c2, w=W0, h=600, step=4):
    k = (c1, c2, w, h, step)
    if k not in _HT:
        yy, xx = np.mgrid[0:h, 0:w]
        m = (((xx + yy) % step) < 2)[..., None]
        _HT[k] = Image.fromarray(np.where(m, np.array(c1, np.uint8), np.array(c2, np.uint8)).astype(np.uint8))
    return _HT[k]
def dpoly(img, pts, c1, c2, outline=None, pat='chk'):
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    src = checker(c1, c2, img.size[0], img.size[1]) if pat == 'chk' else hatch(c1, c2, img.size[0], img.size[1])
    img.paste(src, (0, 0), m)
    if outline: ImageDraw.Draw(img).polygon(pts, outline=outline)
def drect(img, box, c1, c2, outline=None, pat='chk'):
    x0, y0, x1, y1 = box
    dpoly(img, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], c1, c2, outline, pat)
def dell(img, box, c1, c2, outline=None):
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).ellipse(box, fill=255)
    img.paste(checker(c1, c2, img.size[0], img.size[1]), (0, 0), m)
    if outline: ImageDraw.Draw(img).ellipse(box, outline=outline)
_SR = random.Random(21)
STARS = [(_SR.uniform(0, W0), _SR.uniform(0, 600)) for _ in range(28)]
def navy_bg(h=H0, t=0.0):
    img = Image.new('RGB', (W0, h), NAVY)
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate(STARS):
        if y < h and (i + int(t * 2)) % 7 != 0:
            d.rectangle([x, y, x + 1, y + 1], fill=(200, 210, 230))
    return img
def sheen(d, cx, cy, r, ang0=200, ang1=250):
    d.arc([cx - r, cy - r, cx + r, cy + r], ang0, ang1, fill=(255, 255, 255), width=max(1, int(r / 6)))

def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def sm(t, a, b): return clamp((t - a) / (b - a)) if b != a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k

WHITE = (235, 240, 238); YEL = (240, 200, 70); TEAL = (40, 150, 138); TEAL2 = (26, 78, 76)

def grid_bg_old(col=(8, 17, 19), line=(17, 34, 37), step=16, off=(0, 0)):
    img = Image.new('RGB', (W0, H0), col)
    d = ImageDraw.Draw(img)
    for x in range(-step + off[0] % step, W0, step): d.line([(x, 0), (x, H0)], fill=line)
    for y in range(-step + off[1] % step, H0, step): d.line([(0, y), (W0, y)], fill=line)
    return img

def ptext(d, x, y, s, fill=WHITE, anchor='la'):
    # 1px black outline pixel text
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        d.text((x + dx, y + dy), s, font=PIX, fill=(0, 0, 0), fontmode='1', anchor=anchor)
    d.text((x, y), s, font=PIX, fill=fill, fontmode='1', anchor=anchor)

def tag(d, s, tx, ty, ox, oy, k=1.0):
    """label text at tx,ty (top-left) with leader line to object ox,oy"""
    if k <= 0: return
    n = max(1, int(len(s) * clamp(k * 2.5)))
    ptext(d, tx, ty, s[:n])
    if k > 0.3:
        w = PIX.getlength(s)
        sx = tx + w / 2 if abs(ox - (tx + w / 2)) < w else (tx if ox < tx else tx + w)
        sy = ty + 12 if oy > ty else ty - 1
        d.line([(sx, sy), (ox, oy)], fill=(0, 0, 0), width=3)
        d.line([(sx, sy), (ox, oy)], fill=WHITE, width=1)

def counter(d, s):
    x, y = 8, 10
    for k in (0, 5):
        d.polygon([(x + k, y), (x + k + 4, y + 3), (x + k, y + 6)], fill=WHITE, outline=(0, 0, 0))
    ptext(d, x + 13, y - 3, s)

def brackets(d, cx, cy, r, col=WHITE):
    L = max(4, r // 3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * r, cy + sy * r
            d.line([(x, y), (x - sx * L, y)], fill=col)
            d.line([(x, y), (x, y - sy * L)], fill=col)

def cam(img, cx, cy, z, shake=0.0, t=0.0):
    w = img.size[0] / z * (W0 / img.size[0]) if False else W0 / z
    h = H0 / z
    if shake:
        r = random.Random(int(t * 60)); cx += r.uniform(-1, 1) * shake; cy += r.uniform(-1, 1) * shake
    cx = clamp(cx, w / 2, img.size[0] - w / 2); cy = clamp(cy, h / 2, img.size[1] - h / 2)
    return img.resize((W0, H0), Image.NEAREST, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))

def slice_tr(prev, nxt, k):
    """reference transition: a horizontal band with the next scene opens in the middle, then expands"""
    out = prev.copy()
    if k < 0.45: hh = H0 * 0.42
    else: hh = lerp(H0 * 0.42, H0, ease((k - 0.45) / 0.55))
    y0 = int(H0 / 2 - hh / 2); y1 = int(H0 / 2 + hh / 2)
    out.paste(nxt.crop((0, y0, W0, y1)), (0, y0))
    d = ImageDraw.Draw(out)
    if y0 > 0: d.line([(0, y0 - 1), (W0, y0 - 1)], fill=(200, 210, 210), width=2)
    if y1 < H0: d.line([(0, y1), (W0, y1)], fill=(200, 210, 210), width=2)
    return out

# ---------------- palette ----------------
CONC1, CONC2, CONCO = (186, 182, 176), (170, 166, 160), (104, 100, 96)
CURE1, CURE2 = (214, 212, 208), (200, 198, 194)
WOOD1, WOOD2, WOODO = (236, 160, 86), (218, 140, 70), (132, 78, 36)
GLS1, GLS2, GLSO = (206, 220, 238), (172, 192, 218), (96, 116, 150)
REB, REBO, REBH = (226, 72, 60), (118, 28, 30), (255, 160, 140)
SLAB_TOP, SLAB_BOT = 176, 232

def rebar(d, x, y, r=3):
    d.ellipse([x - r, y - r, x + r, y + r], fill=REB, outline=REBO)
    d.point((x - 1, y - 1), fill=REBH)

def real_scene(t, fill, cured=False, props_k=0.0, load_k=-1.0, pour=True):
    img = navy_bg(t=t)
    d = ImageDraw.Draw(img)
    # escoras (glass-blue hatched like the reference)
    for i, x in enumerate((44, 108, 172)):
        kk = clamp(props_k * 3 - i)
        dy = int(260 * kk * kk)
        if dy < 220:
            drect(img, [x - 5, SLAB_BOT + 10 + dy, x + 5, 400 + dy], GLS1, GLS2, GLSO, pat='hatch')
            drect(img, [x - 12, SLAB_BOT + 6 + dy, x + 12, SLAB_BOT + 11 + dy], GLS1, GLS2, GLSO)
            drect(img, [x - 12, 372 + dy, x + 12, 378 + dy], GLS1, GLS2, GLSO)
    if props_k < 0.95:
        fk = clamp(props_k * 3 - 2.2)
        oy = int(220 * fk * fk)
        drect(img, [6, SLAB_BOT + oy, 210, SLAB_BOT + 7 + oy], WOOD1, WOOD2, WOODO)
    drect(img, [2, SLAB_TOP - 14, 9, SLAB_BOT + 7], WOOD1, WOOD2, WOODO)
    drect(img, [207, SLAB_TOP - 14, 214, SLAB_BOT + 7], WOOD1, WOOD2, WOODO)
    lvl = int(lerp(SLAB_BOT, SLAB_TOP, fill))
    if lvl < SLAB_BOT:
        pts = [(9, SLAB_BOT)]
        for x in range(9, 208, 4):
            wob = 0 if cured else 2 * math.sin(x / 9 + t * 7) * (1 - fill * 0.3)
            pts.append((x, lvl + wob))
        pts.append((207, SLAB_BOT))
        c1, c2 = (CURE1, CURE2) if cured else (CONC1, CONC2)
        dpoly(img, pts, c1, c2)
        d.line(pts[1:-1], fill=(236, 236, 232) if cured else (214, 212, 206))
        r = random.Random(7)
        for k in range(90):
            x = r.uniform(12, 204); y = r.uniform(lvl + 3, SLAB_BOT - 2)
            d.rectangle([x, y, x + 1, y + 1], fill=(150, 146, 140) if k % 2 else (128, 132, 146))
    for x in range(20, 204, 14):
        rebar(d, x, SLAB_BOT - 10); rebar(d, x, SLAB_TOP + 10)
    d.line([(9, SLAB_TOP + 10), (207, SLAB_TOP + 10)], fill=REB)
    d.line([(9, SLAB_BOT - 10), (207, SLAB_BOT - 10)], fill=REB)
    for x in range(20, 204, 14):
        rebar(d, x, SLAB_BOT - 10); rebar(d, x, SLAB_TOP + 10)
    if pour:
        hx = 118 + 4 * math.sin(t * 3)
        path = [(240, 26), (172, 38), (hx, 78), (hx, 120)]
        d.line(path, fill=(26, 30, 44), width=14)
        d.line(path, fill=(84, 96, 124), width=10)
        d.line([(p[0] - 2, p[1]) for p in path], fill=(130, 146, 178), width=2)
        r = random.Random(int(t * 30))
        for k in range(30):
            y = r.uniform(122, lvl)
            x = hx + r.uniform(-4, 4) * (y - 120) / 60
            d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=CONC1, outline=CONCO)
        vx = 60 + 2 * math.sin(t * 60)
        d.line([(vx, 30), (vx, lvl + 18)], fill=(26, 30, 44), width=4)
        d.line([(vx, 30), (vx, lvl + 18)], fill=(84, 96, 124), width=2)
        d.rectangle([vx - 4, lvl + 6, vx + 4, lvl + 24], fill=(250, 200, 60), outline=(120, 84, 10))
        d.line([(vx - 2, lvl + 8), (vx - 2, lvl + 20)], fill=(255, 240, 170))
        for k in range(3):
            rr = 5 + ((t * 8 + k / 3) % 1) * 12
            d.arc([vx - rr, lvl - rr / 3, vx + rr, lvl + rr / 3], 180, 360, fill=(255, 255, 255))
    if load_k >= 0:
        k = eout(clamp(load_k / 0.35))
        bounce = 0 if load_k < 0.35 else -4 * math.sin(clamp((load_k - 0.35) / 0.25) * math.pi) * (load_k < 0.6)
        py = lerp(-90, SLAB_TOP - 54, k) + bounce
        drect(img, [56, py + 46, 160, py + 54], WOOD1, WOOD2, WOODO)
        for row in range(4):
            for col in range(5):
                x0 = 58 + col * 20; y0 = py + 46 - (row + 1) * 11
                drect(img, [x0, y0, x0 + 18, y0 + 10], (236, 112, 74), (220, 98, 62), (120, 44, 28))
                d.rectangle([x0 + 4, y0 + 3, x0 + 7, y0 + 7], fill=(150, 56, 36))
                d.rectangle([x0 + 11, y0 + 3, x0 + 14, y0 + 7], fill=(150, 56, 36))
                d.line([(x0 + 1, y0 + 1), (x0 + 8, y0 + 1)], fill=(255, 170, 130))
    return img

# ---------------- corte da laje (camadas, estilo da referência) ----------------
def xray_scene(t, bar=-1.0, fck=0.0):
    img = navy_bg(t=t)
    d = ImageDraw.Draw(img)
    y0, y1 = 150, 236
    # wavy concrete layers
    pts = [(0, y1)] + [(x, y0 + 2 * math.sin(x / 14)) for x in range(0, W0 + 4, 4)] + [(W0, y1)]
    dpoly(img, pts, CONC1, CONC2, CONCO)
    for yy, c in ((y0 + 26, (196, 192, 186)), (y0 + 52, (160, 156, 150))):
        d.line([(x, yy + 2 * math.sin(x / 11 + yy)) for x in range(0, W0 + 4, 4)], fill=c)
    r = random.Random(2)
    for k in range(120):
        x = r.uniform(0, W0); y = r.uniform(y0 + 4, y1 - 3)
        d.rectangle([x, y, x + 1, y + 1], fill=(128, 132, 146) if k % 2 else (150, 146, 140))
    d.line([(0, y0 + 14), (W0, y0 + 14)], fill=REB); d.line([(0, y1 - 14), (W0, y1 - 14)], fill=REB)
    for x in range(14, 216, 22):
        rebar(d, x, y1 - 14, 4); rebar(d, x, y0 + 14, 4)
    drect(img, [-2, y1, W0 + 2, y1 + 9], WOOD1, WOOD2, WOODO)
    for x in (40, 108, 176):
        drect(img, [x - 5, y1 + 10, x + 5, 400], GLS1, GLS2, GLSO, pat='hatch')
    if bar >= 0:
        bx0, bx1, by = 30, 186, 300
        d.rectangle([bx0 - 1, by - 1, bx1 + 1, by + 11], fill=(0, 0, 0))
        drect(img, [bx0, by, bx1, by + 10], (40, 56, 90), (34, 48, 80))
        if bar > 0:
            drect(img, [bx0 + 1, by + 1, bx0 + 1 + int((bx1 - bx0 - 2) * bar), by + 9], (252, 206, 70), (240, 186, 50))
            d.line([(bx0 + 2, by + 2), (bx0 + 1 + int((bx1 - bx0 - 4) * bar), by + 2)], fill=(255, 240, 170))
        ptext(d, bx0, by - 16, 'RESISTÊNCIA')
    return img

# ---------------- meso: concrete section ----------------
MW, MH = W0, H0 + 160
def make_meso():
    r = random.Random(9)
    rocks = []
    tries = 0
    while len(rocks) < 16 and tries < 4000:
        tries += 1
        cx, cy, R = r.uniform(10, MW - 10), r.uniform(10, MH - 10), r.uniform(15, 27)
        if all(math.hypot(cx - a, cy - b) > R + rb + 8 for a, b, rb, _ in rocks):
            n = r.randint(6, 8)
            pts = []
            for i in range(n):
                ang = i / n * 2 * math.pi + r.uniform(-0.25, 0.25)
                rr = R * r.uniform(0.7, 1.05)
                pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
            rocks.append((cx, cy, R, pts))
    sand = []
    while len(sand) < 150:
        x, y, s = r.uniform(0, MW), r.uniform(0, MH), r.choice([2, 3, 3, 4])
        if all(math.hypot(x - a, y - b) > R + 3 for a, b, R, _ in rocks): sand.append((x, y, s))
    drops = [(r.uniform(0, MW), r.uniform(0, MH), r.choice([2, 3])) for _ in range(70)]
    return rocks, sand, drops
ROCKS, SAND, DROPS = make_meso()

def meso_scene(t, wet=1.0, dense=0.0):
    c1 = tuple(int(lerp(a, b, dense)) for a, b in zip((214, 186, 150), (206, 202, 194)))
    c2 = tuple(int(lerp(a, b, dense)) for a, b in zip((198, 170, 134), (192, 188, 180)))
    img = checker(c1, c2, MW, MH).copy()
    d = ImageDraw.Draw(img)
    # paste waves (like the skin layers)
    for yy in range(20, MH, 46):
        d.line([(x, yy + 3 * math.sin(x / 13 + yy)) for x in range(0, MW + 4, 4)], fill=tuple(int(v * 0.9) for v in c2))
    for x, y, s in SAND:
        d.ellipse([x - s, y - s, x + s, y + s], fill=(244, 200, 92), outline=(168, 122, 46))
        d.point((x - s / 2, y - s / 2), fill=(255, 238, 170))
    for cx, cy, R, pts in ROCKS:
        dpoly(img, [(x + 1, y + 2) for x, y in pts], (90, 80, 76), (80, 70, 66))
        dpoly(img, pts, (146, 158, 182), (132, 144, 168), (66, 74, 98))
        hl = [(lerp(cx, x, 0.5) - 3, lerp(cy, y, 0.5) - 3) for x, y in pts]
        dpoly(img, hl, (176, 188, 210), (166, 178, 200))
        sheen(d, cx, cy, R * 0.6)
    if wet > 0:
        for x, y, s in DROPS[:int(len(DROPS) * wet)]:
            d.ellipse([x - s, y - s, x + s, y + s], fill=(70, 160, 240), outline=(30, 90, 170))
            d.point((x - 1, y - 1), fill=(255, 255, 255))
    return img

# ---------------- micro: hydration ----------------
def make_micro():
    r = random.Random(11)
    grains = []
    tries = 0
    while len(grains) < 22 and tries < 6000:
        tries += 1
        cx, cy, R = r.uniform(8, W0 - 8), r.uniform(8, H0 + 60), r.uniform(10, 17)
        if all(math.hypot(cx - a, cy - b) > R + rb + 14 for a, b, rb, *_ in grains):
            n = 9
            prof = [r.uniform(0.86, 1.08) for _ in range(n)]
            ett = [(r.uniform(0, 2 * math.pi), r.uniform(0.6, 1.0)) for _ in range(10)]
            csh = [(i / 44 * 2 * math.pi + r.uniform(-0.05, 0.05), r.uniform(0.6, 1.0)) for i in range(44)]
            grains.append((cx, cy, R, prof, ett, csh))
    plates = [(r.uniform(10, W0 - 10), r.uniform(10, H0 + 50), r.uniform(5, 9)) for _ in range(18)]
    return grains, plates
GRAINS, PLATES = make_micro()
MICRO_H = H0 + 80

def micro_scene(t, ett=0.0, csh=0.0, port=0.0, pore=0.0, hyd=0.0):
    c1 = tuple(int(lerp(a, b, pore)) for a, b in zip((56, 132, 226), (176, 166, 156)))
    c2 = tuple(int(lerp(a, b, pore)) for a, b in zip((44, 116, 208), (164, 154, 144)))
    img = checker(c1, c2, W0, MICRO_H).copy()
    d = ImageDraw.Draw(img)
    r = random.Random(int(t * 5))
    for k in range(int(30 * (1 - pore))):
        x = r.uniform(0, W0); y = r.uniform(0, MICRO_H)
        d.rectangle([x, y, x + 1, y + 1], fill=(170, 214, 255))
    if csh > 0:
        for cx, cy, R, prof, et, cs in GRAINS:
            for ang, lk in cs:
                L = R + 4 + 17 * csh * lk
                w = 0.15 * math.sin(ang * 7 + 3)
                x1 = cx + L * math.cos(ang + w); y1 = cy + L * math.sin(ang + w)
                d.line([(cx + R * 0.8 * math.cos(ang), cy + R * 0.8 * math.sin(ang)), (x1, y1)], fill=(246, 240, 222))
                d.point((x1, y1), fill=(255, 255, 255))
    if port > 0:
        for px, py, s in PLATES:
            ss = s * eout(port)
            if ss < 1.5: continue
            hexp = [(px + ss * math.cos(a), py + ss * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]]
            dpoly(img, hexp, (236, 244, 252), (220, 232, 246), (120, 146, 190))
            d.line([(px - ss * 0.5, py - ss * 0.3), (px - ss * 0.1, py - ss * 0.6)], fill=(255, 255, 255))
    for cx, cy, R, prof, et, cs in GRAINS:
        Rc = R * (1 - 0.35 * hyd)
        ang = [i / 9 * 2 * math.pi for i in range(9)]
        if hyd > 0:
            rim = [(cx + R * prof[i] * math.cos(ang[i]), cy + R * prof[i] * math.sin(ang[i])) for i in range(9)]
            dpoly(img, rim, (232, 214, 182), (220, 200, 168), (150, 124, 90))
        pts = [(cx + Rc * prof[i] * math.cos(ang[i]), cy + Rc * prof[i] * math.sin(ang[i])) for i in range(9)]
        dpoly(img, pts, (112, 100, 136), (98, 88, 122), (42, 34, 60))
        sheen(d, cx, cy, Rc * 0.65)
        if ett > 0:
            for a2, lk in et:
                L = 5 + 8 * ett * lk
                x0 = cx + R * 0.95 * math.cos(a2); y0 = cy + R * 0.95 * math.sin(a2)
                x1 = x0 + L * math.cos(a2); y1 = y0 + L * math.sin(a2)
                d.line([(x0, y0), (x1, y1)], fill=(150, 104, 20), width=3)
                d.line([(x0, y0), (x1, y1)], fill=(255, 212, 70), width=1)
    return img

def find_grain(px, py):
    return min(GRAINS, key=lambda g: math.hypot(g[0] - px, g[1] - py))

# ---------------- timeline ----------------
T_B = tb(2); T_C = tb(7); T_D = tb(18); T_E = tb(37); T_F = tb(43); T_G = tb(49)
TR = B  # transition length

def scene_at(t):
    """returns logical image (216x384) for time t (no transition)"""
    if t < T_B:
        k = clamp(t / (T_B))
        return cam(real_scene(t, lerp(0.55, 0.8, k)), 108, 190, 1.3)
    if t < T_C:
        k = ease(sm(t, T_B, T_C))
        img = xray_scene(t)
        d = ImageDraw.Draw(img)
        out = cam(img, 108, 193, lerp(1.0, 2.0, k))
        dd = ImageDraw.Draw(out)
        rr = int(lerp(40, 70, k))
        brackets(dd, 108, 193, rr)
        tag(dd, 'LAJE', 20, 80, 70, 160, sm(t, T_B + 0.2, T_B + 0.6))
        for yy in (176, 210):
            dd.line([(180, yy), (186, yy)], fill=YEL)
        return out
    if t < T_D:
        hrs = 'HORA 0' if t < tb(11) else ('HORA 1' if t < tb(14) else 'HORA 2')
        wet = 1.0 if t < tb(14) else lerp(1.0, 0.25, sm(t, tb(14), tb(15.5)))
        img = meso_scene(t, wet=wet)
        scroll = lerp(0, 120, sm(t, T_C, T_D))
        out = img.crop((0, int(scroll), W0, int(scroll) + H0))
        d = ImageDraw.Draw(out)
        counter(d, hrs)
        # labels
        rk = ROCKS[2]
        if t < tb(14):
            tag(d, 'BRITA', 20, 120, rk[0], rk[1] - scroll, sm(t, tb(8), tb(8.6)))
            tag(d, 'AREIA', 130, 210, 150, 240, sm(t, tb(9), tb(9.6)))
            dp = DROPS[5]
            tag(d, 'ÁGUA', 40, 290, 100, 270, sm(t, tb(10), tb(10.6)))
            tag(d, 'PASTA DE CIMENTO', 60, 60, 108, 92, sm(t, tb(11), tb(11.6)))
        else:
            tag(d, 'PEGA', 90, 150, 108, 190, sm(t, tb(14), tb(14.6)))
            brackets(d, 108, 200, int(lerp(70, 30, ease(sm(t, tb(15), T_D)))))
        return out
    if t < T_E:
        b = (t - OFF) / B
        if b < 21: lab = 'HORA 2'
        elif b < 24: lab = 'HORA 6'
        elif b < 27: lab = 'HORA 12'
        elif b < 30: lab = 'DIA 1'
        elif b < 33: lab = 'DIA 3'
        else: lab = 'DIA 5'
        ett = ease(sm(t, tb(20), tb(24)))
        csh = ease(sm(t, tb(24), tb(33.5)))
        port = sm(t, tb(29.5), tb(33))
        pore = sm(t, tb(31), tb(36.5))
        hyd = sm(t, tb(24), tb(37))
        img = micro_scene(t, ett, csh, port, pore, hyd)
        scroll = lerp(0, 70, sm(t, T_D, T_E))
        z = lerp(1.0, 1.12, sm(t, T_D, T_E))
        out = cam(img, 108, H0 / 2 + scroll, z)
        d = ImageDraw.Draw(out)
        counter(d, lab)
        def gpos(i):
            g = GRAINS[i]; return ((g[0] - 108) * z + 108, (g[1] - (H0 / 2 + scroll)) * z + H0 / 2, g)
        def near(tx, ty, kind='grain'):
            best = None
            if kind == 'grain':
                for g in GRAINS:
                    sx = (g[0] - 108) * z + 108; sy = (g[1] - (H0 / 2 + scroll)) * z + H0 / 2
                    if 10 < sx < W0 - 10 and 30 < sy < H0 - 20:
                        dd = math.hypot(sx - tx, sy - ty)
                        if best is None or dd < best[0]: best = (dd, sx, sy, g[2] * z)
            else:
                for p in PLATES:
                    sx = (p[0] - 108) * z + 108; sy = (p[1] - (H0 / 2 + scroll)) * z + H0 / 2
                    if 10 < sx < W0 - 10 and 30 < sy < H0 - 20:
                        dd = math.hypot(sx - tx, sy - ty)
                        if best is None or dd < best[0]: best = (dd, sx, sy, 0)
            return best[1], best[2], best[3]
        if b < 21.5:
            x, y, R = near(60, 110)
            tag(d, 'GRÃO DE CIMENTO', 14, 56, x, y - R * 0.6, sm(t, tb(18.4), tb(19)))
            tag(d, 'ÁGUA', 150, 320, 170, 300, sm(t, tb(19.5), tb(20)))
        elif b < 24.5:
            x, y, R = near(70, 120)
            tag(d, 'ETRINGITA', 20, 70, x + R * 0.7, y - R * 0.7, sm(t, tb(21.2), tb(21.8)))
        elif b < 29.8:
            x, y, R = near(150, 110)
            tag(d, 'C-S-H', 130, 60, x + R * 1.4, y - R * 0.4, sm(t, tb(26), tb(26.6)))
            if b > 27.6: ptext(d, 130, 74, 'A "COLA"', fill=YEL)
        elif b < 33:
            x, y, _ = near(70, 300, 'plate')
            tag(d, 'PORTLANDITA', 14, 330, x, y, sm(t, tb(30.2), tb(30.8)))
        else:
            x, y, R = near(110, 140)
            tag(d, 'POROS FECHANDO', 30, 70, x + R * 1.5, y, sm(t, tb(33.3), tb(33.9)))
        return out
    if t < T_F:
        img = meso_scene(t, wet=0, dense=1.0)
        z = lerp(1.6, 1.0, eout(sm(t, T_E, T_E + 4 * B)))
        out = cam(img, 108, 260, z)
        d = ImageDraw.Draw(out)
        counter(d, 'DIA 7')
        tag(d, 'CONCRETO ENDURECIDO', 20, 300, 100, 250, sm(t, tb(39), tb(39.6)))
        return out
    if t < T_G:
        b = (t - OFF) / B
        lab = 'DIA 7' if b < 44 else ('DIA 14' if b < 45.5 else ('DIA 21' if b < 47 else 'DIA 28'))
        bar = {'DIA 7': 0.0, 'DIA 14': 0.0, 'DIA 21': 0.0, 'DIA 28': 0.0}
        val = clamp(0.55 + 0.45 * ease(sm(t, T_F, tb(47.2))))
        img = xray_scene(t, bar=val)
        z = lerp(2.0, 1.0, eout(sm(t, T_F, T_F + 2 * B)))
        out = cam(img, 108, 220, z)
        d = ImageDraw.Draw(out)
        counter(d, lab)
        if b >= 47:
            k = sm(t, tb(47), tb(47.3))
            if k > 0: ptext(d, 150, 288, 'FCK', fill=YEL)
        return out
    # final real scene
    k = (t - T_G)
    pk = sm(t, T_G + 0.15, T_G + 2.2 * B)
    lk = (t - tb(51.5)) / (2.5 * B) if t >= tb(51.5) else -1
    shake = 1.5 if 0.3 < lk < 0.5 else 0
    img = real_scene(t, 1.0, cured=True, props_k=pk, load_k=lk, pour=False)
    return cam(img, 108, 190, 1.3, shake, t)

def frame(t):
    # transitions at T_C (slice in), T_D (slice in), T_E (slice out), T_B/T_F/T_G hard cuts with flash-less
    for T in (T_C, T_D, T_E):
        if T <= t < T + TR:
            prev = scene_at(T - 1e-3)
            nxt = scene_at(t)
            return slice_tr(prev, nxt, (t - T) / TR)
    return scene_at(t)

def capa():
    img = micro_scene(0, ett=1, csh=0.75, port=0.6, pore=0.4, hyd=0.5)
    out = cam(img, 108, 200, 1.0).resize((OUTW, OUTH), Image.NEAREST)
    d = ImageDraw.Draw(out, 'RGBA')
    d.rectangle([0, 0, OUTW, OUTH], fill=(0, 0, 0, 90))
    t1 = Image.new('RGBA', (1300, 440), (0, 0, 0, 0)); dt = ImageDraw.Draw(t1)
    dt.rectangle([0, 30, 1300, 410], fill=(8, 8, 10, 235))
    f = ImageFont.truetype(MONT % 900, 150)
    dt.text((650, 140), '28 DIAS', font=f, fill=(245, 190, 45), stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    dt.text((650, 300), 'POR DENTRO', font=ImageFont.truetype(MONT % 900, 130), fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0), anchor='mm')
    t1 = t1.rotate(4, expand=True, resample=Image.BICUBIC)
    out.paste(t1, (540 - t1.size[0] // 2, 760 - t1.size[1] // 2), t1)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        ts = [float(x) for x in sys.argv[2].split(',')]
        ims = [capa().resize((216, 384))] + [frame(t) for t in ts]
        cols = 8; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 216 * 2, rows * 400 * 2), (255, 255, 255))
        dd = ImageDraw.Draw(sheet)
        for i, im in enumerate(ims):
            sheet.paste(im.resize((432, 768), Image.NEAREST), ((i % cols) * 432, (i // cols) * 800))
            dd.text(((i % cols) * 432 + 4, (i // cols) * 800 + 772), 'capa' if i == 0 else '%.2f' % ts[i - 1], fill=(0, 0, 0))
        sheet.save(sys.argv[3]); print(VD)
    else:
        c = capa()
        c.save('capa.png')
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', 'video_noaudio.mp4'], stdin=subprocess.PIPE)
        for i in range(2): p.stdin.write(c.tobytes())
        nfr = int(VD * FPS)
        for i in range(nfr):
            p.stdin.write(frame(i / FPS).resize((OUTW, OUTH), Image.NEAREST).tobytes())
        p.stdin.close(); p.wait(); print('done', VD)
