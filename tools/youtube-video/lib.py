import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, PX, FPS = 1920, 1080, 5, 30
LW, LH = W // PX, H // PX      # 384 x 216
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "montserrat-latin-%d-normal.woff2")
_fc = {}
def font(w, s):
    k = (w, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(F % w, max(6, int(s)))
    return _fc[k]
YEL = (245, 190, 45); WHITE = (255, 255, 255); BLK = (0, 0, 0)
RED = (230, 50, 40); GRN = (60, 200, 80); BLUE = (80, 160, 255); LBLUE = (140, 200, 255); ORANGE = (240, 130, 30)
GREY = (150, 150, 150)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def seg(t, a, b): return eio((t - a) / max(b - a, 1e-6))

def texmap(base, var, seed, h=LH, w=LW):
    r = random.Random(seed); m = np.zeros((h, w, 3), np.uint8)
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            c = np.array(base) + r.randint(-var, var)
            m[y:y+4, x:x+4] = np.clip(c, 0, 255)
            m[y + r.randint(0, 3), x + r.randint(0, 3)] = np.clip(c - 18, 0, 255)
    return m
GRASS = texmap((86, 170, 60), 14, 4)
TOPS = texmap((120, 84, 52), 12, 3)
SILT = texmap((138, 118, 92), 10, 13)
SILT_S = texmap((112, 104, 100), 10, 14)
CLAY = texmap((112, 122, 138), 10, 5)
CLAY2 = texmap((80, 86, 98), 8, 6)
SAND = texmap((196, 170, 110), 12, 7)
SANDB = texmap((222, 200, 140), 10, 17)
MARB = texmap((232, 228, 216), 8, 8, 400, 120)
STONE = texmap((176, 168, 155), 10, 2)
CONC = texmap((150, 150, 148), 12, 1)
SEA = texmap((40, 110, 170), 10, 9)

def sky(img, night=0.0, sunset=0.0, y1=LH):
    for y in range(y1):
        k = y / LH
        c = np.array((110 + 60 * k, 170 + 45 * k, 235 + 10 * k))
        n = np.array((20, 26, 60)); s = np.array((250, 150 - 60 * (1 - k), 90 + 60 * k))
        c = c * (1 - sunset) + s * sunset
        img[y, :] = np.clip(c * (1 - night) + n * night, 0, 255).astype(np.uint8)
    for cx, cy, w in [(30, 28, 30), (240, 20, 40), (330, 44, 22), (150, 50, 18)]:
        col = np.array((245, 248, 252)) * (1 - night * 0.7)
        img[cy:cy+4, cx:cx+w] = col; img[cy-4:cy, cx+4:cx+w-6] = col

def blank(col=(20, 24, 32)):
    a = np.zeros((LH, LW, 3), np.uint8); a[:] = col; return a

# ---------------- tower ----------------
def tower_sprite(floors, fh=15, tw=36, curve=0.0, tint=None):
    """curve: banana offset per floor (px). floors up to 8 (8 = bell chamber)."""
    floors = max(0.0, min(8.0, floors))
    full = int(floors); part = floors - full
    hgt = 10 + 7 * fh + 14 + 6
    wpad = 30
    a = np.zeros((hgt, tw + 2 * wpad, 4), np.uint8)
    yb = hgt
    def band(y0, y1, x0, x1, arch=True):
        y0 = max(0, y0)
        if y1 <= y0: return
        h = y1 - y0
        a[y0:y1, x0:x1, :3] = MARB[(y0 % 300):(y0 % 300) + h, (x0 % 60):(x0 % 60) + (x1 - x0)]
        a[y0:y1, x0:x1, 3] = 255
        a[y0:y0+2, x0-1:x1+1, :3] = (205, 198, 182); a[y0:y0+2, x0-1:x1+1, 3] = 255
        if arch and h > 8:
            for ax in range(x0 + 2, x1 - 3, 6):
                a[y0 + 5:y1 - 2, ax:ax + 3, :3] = (70, 70, 78)
                a[y0 + 4, ax + 1, :3] = (70, 70, 78)
    x0 = wpad; x1 = wpad + tw
    if floors <= 0: return Image.fromarray(a), wpad + tw // 2
    band(yb - 10, yb, x0 - 1, x1 + 1, arch=False); yb -= 10
    n = min(full, 7) if full >= 1 else 0
    for i in range(1, n + 1 if full < 8 else 7):
        off = int(round(curve * i))
        band(yb - fh, yb, x0 + off, x1 + off); yb -= fh
    if full >= 8:
        off = int(round(curve * 7.5))
        band(yb - 12, yb, x0 + 7 + off, x1 - 7 + off); yb -= 12
        a[yb - 3:yb, x0 + 9 + off:x1 - 9 + off, :3] = (190, 120, 80); a[yb - 3:yb, x0 + 9 + off:x1 - 9 + off, 3] = 255
    elif part > 0 and 1 <= full < 7:
        hh = int(fh * part); off = int(round(curve * (full + 1)))
        band(yb - hh, yb, x0 + off, x1 + off, arch=False)
    if tint is not None:
        m = a[:, :, 3] > 0
        a[m, :3] = (a[m, :3] * 0.5 + np.array(tint) * 0.5).astype(np.uint8)
    return Image.fromarray(a), wpad + tw // 2

def draw_tower(img, x, ybase, floors, theta, fh=15, tw=36, curve=0.0, tint=None, alpha=1.0):
    sp, cx = tower_sprite(floors, fh, tw, curve, tint)
    bb = sp.getbbox()
    if not bb: return
    sp = sp.crop((0, bb[1], sp.width, sp.height))
    w, hh = sp.size
    pad = Image.new("RGBA", (w + 2 * hh, 2 * hh), (0, 0, 0, 0))
    pad.paste(sp, (hh, 0))
    rot = pad.rotate(-theta, resample=Image.NEAREST, center=(hh + cx, hh))
    if alpha < 1:
        al = np.array(rot); al[:, :, 3] = (al[:, :, 3] * alpha).astype(np.uint8); rot = Image.fromarray(al)
    b = Image.fromarray(img).convert("RGBA")
    b.alpha_composite(rot, (int(x - (hh + cx)), int(ybase + 1 - hh)))
    img[:] = np.array(b.convert("RGB"))

def foundation(img, x, y, theta, w=26, d=8):
    pil = Image.fromarray(img); dr = ImageDraw.Draw(pil)
    c, s = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    def P(dx, dy): return (x + dx * c - dy * s, y + dx * s + dy * c)
    dr.polygon([P(-w, 0), P(w, 0), P(w, d), P(-w, d)], fill=(120, 116, 110), outline=(50, 50, 50))
    img[:] = np.array(pil)

# --------------- ground/soil ----------------
def ground_strip(img, gy, x0=0, x1=LW, dip=None):
    for x in range(x0, x1):
        g = gy + (int(round(dip(x))) if dip else 0)
        img[g:g + 3, x] = GRASS[g:g + 3, x]
        img[g + 3:LH, x] = TOPS[g + 3:LH, x]

def soil_section(img, gy, xc, layers, dip_amp=0.0, south_dark=0.0, consol=0.0, water=0.0, t=0.0, wobble=0.0):
    """layers: list of (name, bottom_y). Horizon A silts, B clay, C sand."""
    xs = np.arange(LW)
    dip = dip_amp * np.exp(-((xs - xc) / 40.0) ** 2)
    yA, yB = layers
    r = random.Random(11)
    for x in range(LW):
        d = dip[x]
        g = gy + int(round(d * 0.4))
        img[g:g + 3, x] = GRASS[g:g + 3, x]
        a_bot = yA + int(round(d)) + int(wobble * math.sin(x * 0.15 + t * 6))
        k = clamp((x - xc + 10) / 60.0) * south_dark
        img[g + 3:a_bot, x] = (SILT[g + 3:a_bot, x] * (1 - k) + SILT_S[g + 3:a_bot, x] * k).astype(np.uint8)
        b_bot = yB
        img[a_bot:b_bot, x] = (CLAY[a_bot:b_bot, x] * (1 - consol) + CLAY2[a_bot:b_bot, x] * consol).astype(np.uint8)
        img[b_bot:LH, x] = SAND[b_bot:LH, x]
    if water > 0:
        for i in range(60):
            x = r.randint(2, LW - 6); y = r.randint(yA + 4, yB - 4)
            if r.random() < water * (1 - consol): img[y:y + 2, x:x + 3] = (90, 150, 230)

def bloquinho(img, x, feet, pose="idle", eyes="normal", scale=1, flip=False, helmet=(245, 130, 30), vest=(245, 200, 30)):
    s = scale
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil)
    def R(x0, y0, x1, y1, c):
        if flip: x0, x1 = -x1, -x0
        d.rectangle([x + x0 * s, feet + y0 * s, x + x1 * s - 1, feet + y1 * s - 1], fill=c)
    R(-4, -9, -1, 0, (90, 90, 95)); R(1, -9, 4, 0, (90, 90, 95))
    R(-5, -2, -1, 0, (50, 40, 35)); R(1, -2, 5, 0, (50, 40, 35))
    R(-5, -19, 5, -9, vest); R(-5, -14, 5, -12, (210, 215, 220))
    skin = (225, 180, 140)
    if pose == "push":
        R(-13, -19, -5, -16, vest); R(-15, -20, -13, -15, skin); R(-13, -15, -5, -12, vest); R(-15, -16, -13, -11, skin)
    elif pose == "thumb":
        R(-7, -18, -5, -11, vest); R(5, -18, 9, -15, vest); R(8, -21, 10, -15, skin)
    elif pose == "up":
        R(-7, -26, -5, -17, vest); R(5, -26, 7, -17, vest); R(-7, -28, -5, -26, skin); R(5, -28, 7, -26, skin)
    elif pose == "point":
        R(5, -18, 13, -15, vest); R(13, -18, 15, -15, skin); R(-7, -18, -5, -11, vest)
    elif pose == "shrug":
        R(-9, -20, -5, -17, vest); R(5, -20, 9, -17, vest); R(-11, -22, -9, -19, skin); R(9, -22, 11, -19, skin)
    else:
        R(-7, -18, -5, -11, vest); R(5, -18, 7, -11, vest); R(-7, -11, -5, -9, skin); R(5, -11, 7, -9, skin)
    R(-5, -29, 5, -19, skin)
    if eyes == "wide":
        R(-4, -27, -1, -23, WHITE); R(1, -27, 4, -23, WHITE); R(-3, -26, -2, -24, BLK); R(2, -26, 3, -24, BLK); R(-1, -22, 1, -20, (120, 40, 40))
    elif eyes == "sweat":
        R(-4, -26, -2, -24, WHITE); R(2, -26, 4, -24, WHITE); R(-3, -26, -2, -25, BLK); R(3, -26, 4, -25, BLK)
        R(-2, -21, 2, -20, (120, 60, 50)); R(6, -30, 7, -27, (120, 190, 255))
    else:
        R(-4, -26, -2, -24, WHITE); R(2, -26, 4, -24, WHITE); R(-3, -26, -2, -25, BLK); R(3, -26, 4, -25, BLK); R(-2, -21, 2, -20, (120, 60, 50))
    R(-6, -32, 6, -29, helmet); R(-4, -34, 4, -32, helmet); R(-7, -30, 7, -29, tuple(max(0, c - 25) for c in helmet))
    img[:] = np.array(pil)

def arrow(img, x0, y0, x1, y1, col, w=2):
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil)
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1 - 5 * math.cos(ang), y1 - 5 * math.sin(ang)
    d.line([x0, y0, hx, hy], fill=(20, 20, 20), width=w + 2)
    pts = [(x1, y1), (hx + 4 * math.sin(ang), hy - 4 * math.cos(ang)), (hx - 4 * math.sin(ang), hy + 4 * math.cos(ang))]
    d.polygon(pts, fill=col, outline=(20, 20, 20))
    d.line([x0, y0, hx, hy], fill=col, width=w)
    img[:] = np.array(pil)

def rect(img, x0, y0, x1, y1, col, outline=None):
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil); d.rectangle([x0, y0, x1, y1], fill=col, outline=outline); img[:] = np.array(pil)

def poly(img, pts, col, outline=None):
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil); d.polygon(pts, fill=col, outline=outline); img[:] = np.array(pil)

def line(img, pts, col, w=1):
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil); d.line(pts, fill=col, width=w); img[:] = np.array(pil)

def ellipse(img, box, col, outline=None, alpha=1.0):
    pil = Image.fromarray(img).convert("RGBA"); ov = Image.new("RGBA", pil.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.ellipse(box, fill=col + (int(255 * alpha),), outline=outline)
    pil.alpha_composite(ov); img[:] = np.array(pil.convert("RGB"))

def dust(img, t, t0, x, y, n=40, seed=0, col=(170, 165, 155), spread=40, dur=1.4):
    dt = t - t0
    if dt < 0 or dt > dur: return
    r = random.Random(seed)
    for i in range(n):
        vx = r.uniform(-spread, spread); vy = r.uniform(-50, -5)
        px = int(x + r.uniform(-30, 30) + vx * dt); py = int(y + vy * dt + 40 * dt * dt)
        sz = r.choice([2, 3, 4]); a = 1 - dt / dur
        if 0 <= px < LW - sz and 0 <= py < LH - sz:
            img[py:py + sz, px:px + sz] = np.array(col) * a + img[py, px] * (1 - a)

def dim(img, k): img[:] = (img * k).astype(np.uint8)

def piazza(img, gy, cathedral=True):
    if cathedral:
        rect(img, 8, gy - 34, 92, gy, (232, 226, 212), (150, 140, 120))
        poly(img, [(8, gy - 34), (50, gy - 50), (92, gy - 34)], (220, 212, 196), (150, 140, 120))
        for x in range(14, 90, 8): rect(img, x, gy - 26, x + 3, gy - 6, (90, 90, 100))
        # baptistery dome
        ellipse(img, (300, gy - 56, 360, gy - 8), (226, 220, 206), (150, 140, 120))
        rect(img, 298, gy - 30, 362, gy, (232, 226, 212), (150, 140, 120))
        for x in range(304, 360, 8): rect(img, x, gy - 24, x + 3, gy - 6, (90, 90, 100))
