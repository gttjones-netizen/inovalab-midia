import math, json, random, subprocess, os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
OUT = (22, 20, 26)
FD = '/home/claude/package/files/'
_fc = {}
def F(w, s):
    k = (w, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + f'montserrat-latin-{w}-normal.woff2', s)
    return _fc[k]

YEL = (245, 190, 45); WHITE = (255, 255, 255); RED = (226, 52, 44); BLUE = (64, 150, 235)
GREEN = (60, 185, 85); LBLUE = (140, 210, 255)

def ease(x):
    x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def eout(x):
    x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def clamp(x, a=0, b=1): return max(a, min(b, x))

# ---------------- primitives ----------------
def ell(d, cx, cy, rx, ry, fill, ow=7):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=OUT if ow else None, width=ow)
def rect(d, x0, y0, x1, y1, fill, ow=7, r=0):
    if r: d.rounded_rectangle([x0, y0, x1, y1], r, fill=fill, outline=OUT if ow else None, width=ow)
    else: d.rectangle([x0, y0, x1, y1], fill=fill, outline=OUT if ow else None, width=ow)
def poly(d, pts, fill, ow=7):
    pts = [(float(x), float(y)) for x, y in pts]
    d.polygon(pts, fill=fill)
    if ow: d.line(pts + [pts[0]], fill=OUT, width=ow, joint='curve')
def line(d, pts, fill=OUT, w=7):
    d.line([(float(x), float(y)) for x, y in pts], fill=fill, width=w, joint='curve')
def rot(pts, ang, cx, cy):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

def arrow(d, x0, y0, x1, y1, col, w=22, head=46):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0)
    if L < 5: return
    head = min(head, L * 0.6)
    bx, by = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    shaft = [(x0 + px * w / 2, y0 + py * w / 2), (bx + px * w / 2, by + py * w / 2), (bx + px * head * .6, by + py * head * .6), (x1, y1),
             (bx - px * head * .6, by - py * head * .6), (bx - px * w / 2, by - py * w / 2), (x0 - px * w / 2, y0 - py * w / 2)]
    poly(d, shaft, col, 6)

def text_c(d, x, y, s, font, fill=WHITE, stroke=8, sc=OUT, anchor='mm'):
    d.text((x, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=sc, anchor=anchor)

def label(d, x, y, s, size=54, fill=WHITE, bg=(20, 20, 26)):
    f = F(800, size); bb = d.textbbox((x, y), s, font=f, anchor='mm')
    d.rounded_rectangle([bb[0] - 18, bb[1] - 12, bb[2] + 18, bb[3] + 12], 14, fill=bg, outline=OUT, width=5)
    d.text((x, y), s, font=f, fill=fill, anchor='mm')

# ---------------- backgrounds ----------------
def sky(d, night=False, top=0, bot=1250):
    cols = [(110, 190, 245), (140, 205, 250), (170, 220, 252)] if not night else [(20, 24, 60), (30, 36, 80), (44, 50, 100)]
    n = len(cols); h = (bot - top) / n
    for i, c in enumerate(cols): d.rectangle([0, top + i * h, W, top + (i + 1) * h + 1], fill=c)

def cloud(d, x, y, s=1.0):
    for dx, dy, r in [(-70, 10, 55), (0, -15, 70), (75, 8, 55), (20, 25, 60)]:
        ell(d, x + dx * s, y + dy * s, r * s, r * s * .8, (255, 255, 255), 0)
    d.arc([x - 140 * s, y - 85 * s, x + 140 * s, y + 70 * s], 180, 360, fill=OUT, width=6)

def ground(d, y=1250, grass=(95, 175, 70), soil=(150, 70, 45)):
    d.rectangle([0, y, W, H], fill=soil)
    d.rectangle([0, y, W, y + 40], fill=grass); d.line([(0, y), (W, y)], fill=OUT, width=7)

def house(d, x, y, w=520, h=560, ang=0, pivot=None, crack=0, col=(250, 225, 170), roof=(200, 70, 55), cr_side=1, small=False):
    """sobrado: x,y = bottom-left on ground; ang rotation around pivot"""
    pv = pivot or (x, y)
    ow = 5 if small else 7
    def R(pts): return rot(pts, ang, *pv)
    body = [(x, y), (x + w, y), (x + w, y - h), (x, y - h)]
    poly(d, R(body), col, ow)
    poly(d, R([(x - w * .08, y - h), (x + w * 1.08, y - h), (x + w * .5, y - h - h * .38)]), roof, ow)
    # floors line
    line(d, R([(x, y - h / 2), (x + w, y - h / 2)]), OUT, 4 if small else 5)
    for fx in (.18, .62):
        for fy in (.12, .62):
            wx, wy = x + w * fx, y - h + h * fy
            poly(d, R([(wx, wy), (wx + w * .2, wy), (wx + w * .2, wy + h * .22), (wx, wy + h * .22)]), (130, 200, 240), ow)
    # door
    poly(d, R([(x + w * .44, y), (x + w * .56, y), (x + w * .56, y - h * .3), (x + w * .44, y - h * .3)]), (140, 85, 50), ow)
    if crack > 0:
        # diagonal crack from window corner rising toward cr_side
        sx = x + w * (.38 if cr_side > 0 else .62); sy = y - h * .05
        pts = [(sx, sy)]
        n = 9
        for i in range(1, n + 1):
            pts.append((sx + cr_side * w * .5 * i / n + (12 if i % 2 else -12), sy - h * .62 * i / n))
        k = max(2, int(len(pts) * min(1, crack)))
        line(d, R(pts[:k]), OUT, 9 if not small else 6)

def nelsao_house(d, x, y, level, s=0.45):
    w, h = 520 * s, 560 * s
    house(d, x, y, w, h, crack=0, col=(205, 230, 200), roof=(90, 110, 160), small=True)
    if level > 0:
        sx, sy = x + w * .3, y - h * .08
        pts = [(sx, sy)]
        for i in range(1, 8):
            pts.append((sx + w * .45 * i / 7 + (7 if i % 2 else -7), sy - h * .75 * i / 7))
        k = max(2, int(len(pts) * min(1, level / 5)))
        line(d, pts[:k], OUT, 4 + level)

def soil_section(d, y0=700, y1=1700, boundary=None, labels=True, firm=(110, 60, 40), soft=(200, 95, 60)):
    """boundary(x)-> y of firm layer top"""
    d.rectangle([0, y0, W, y1], fill=firm)
    if boundary is None: boundary = lambda x: y0 + 300
    pts = [(0, y0)] + [(x, boundary(x)) for x in range(0, W + 1, 40)] + [(W, y0)]
    d.polygon(pts, fill=soft)
    line(d, [(x, boundary(x)) for x in range(0, W + 1, 40)], OUT, 6)
    rnd = random.Random(3)
    for i in range(70):  # pores
        px = rnd.randint(10, W - 10); py = rnd.randint(y0 + 10, y1)
        if py < boundary(px) - 12: ell(d, px, py, 7, 5, (160, 70, 45), 0)
        elif py > boundary(px) + 15: ell(d, px, py, 9, 6, (90, 48, 32), 0)
    d.rectangle([0, y0 - 30, W, y0], fill=(95, 175, 70)); d.line([(0, y0), (W, y0)], fill=OUT, width=7)

# ---------------- characters ----------------
CH = {
 'VAL': dict(skin=(250, 200, 160), shirt=(200, 50, 50), pants=(60, 80, 140), hat='cap', hatc=(40, 90, 170), stache=True, plaid=True),
 'NEL': dict(skin=(205, 140, 95), shirt=(245, 245, 245), pants=(70, 110, 70), hat=None, bald=True, belly=True, tank=True),
 'CID': dict(skin=(245, 195, 165), shirt=(150, 80, 170), pants=(150, 80, 170), hat='bun', hatc=(90, 55, 40), glasses=True, dress=True),
 'BLQ': dict(skin=(250, 205, 165), shirt=(250, 210, 40), pants=(120, 120, 128), hat='helmet', hatc=(245, 120, 30), vest=True),
}

def char(d, who, x, y, s=1.0, mouth=0.0, eyes='normal', arm='down', arm2=None, prop=None, flip=False, rotdeg=0, look=0):
    """x,y = feet center. cutout style. returns head center"""
    s = s * 1.25
    c = CH[who]; S = lambda v: v * s
    hr = S(118); bw = S(120 if not c.get('belly') else 140); bh = S(170)
    fy = y; legy = fy - S(40)
    bodyt = legy - bh; hy = bodyt - hr * .55
    sg = -1 if flip else 1
    # legs/feet
    for lx in (-S(48), S(48)):
        rect(d, x + lx - S(26), legy - S(10), x + lx + S(26), fy - S(8), c['pants'], max(3, int(5 * s)))
        ell(d, x + lx + sg * S(10), fy - S(6), S(40), S(16), OUT, 0)
    # body
    if c.get('dress'):
        poly(d, [(x - bw * .8, bodyt + S(20)), (x + bw * .8, bodyt + S(20)), (x + bw * 1.05, legy + S(5)), (x - bw * 1.05, legy + S(5))], c['shirt'], max(3, int(6 * s)))
    else:
        d.rounded_rectangle([x - bw, bodyt, x + bw, legy + S(5)], int(S(60)), fill=c['shirt'], outline=OUT, width=max(3, int(6 * s)))
    if c.get('plaid'):
        for i in range(-2, 3):
            d.line([(x + i * S(42), bodyt + S(15)), (x + i * S(42), legy)], fill=(140, 30, 30), width=max(2, int(6 * s)))
        for j in range(1, 4):
            d.line([(x - bw + S(12), bodyt + j * S(40)), (x + bw - S(12), bodyt + j * S(40))], fill=(140, 30, 30), width=max(2, int(6 * s)))
    if c.get('tank'):
        ell(d, x - bw * .78, bodyt + S(28), S(26), S(28), c['skin'], 0); ell(d, x + bw * .78, bodyt + S(28), S(26), S(28), c['skin'], 0)
    if c.get('belly'):
        d.arc([x - bw * .7, bodyt + S(40), x + bw * .7, legy + S(20)], 20, 160, fill=OUT, width=max(2, int(5 * s)))
    if c.get('vest'):
        d.rectangle([x - bw + S(8), bodyt + S(95), x + bw - S(8), bodyt + S(120)], fill=(210, 215, 220))
        d.line([(x, bodyt + S(10)), (x, legy)], fill=OUT, width=max(2, int(4 * s)))
    # arms
    def drawarm(side, kind):
        sx = x + side * bw * .92; sy = bodyt + S(55)
        if kind == 'down': ex, ey = sx + side * S(30), sy + S(95)
        elif kind == 'up': ex, ey = sx + side * S(45), sy - S(120)
        elif kind == 'point': ex, ey = sx + side * S(125), sy - S(20)
        elif kind == 'hold': ex, ey = sx + side * S(70), sy + S(40)
        elif kind == 'face': ex, ey = x + side * S(30), hy + S(10)
        elif kind == 'cross': ex, ey = x - side * S(35), sy + S(35)
        elif kind == 'phone': ex, ey = sx + side * S(40), hy + S(30)
        else: ex, ey = kind
        line(d, [(sx, sy), (ex, ey)], c['shirt'] if not c.get('tank') else c['skin'], int(S(34)))
        d.line([(sx, sy), (ex, ey)], fill=OUT, width=max(2, int(S(4))))
        ell(d, ex, ey, S(25), S(25), c['skin'] if who != 'BLQ' else (240, 240, 240), max(3, int(5 * s)))
        return ex, ey
    hl = drawarm(-sg, arm2 or 'down')
    hrp = drawarm(sg, arm)
    # head
    ell(d, x, hy, hr, hr * .92, c['skin'], max(3, int(7 * s)))
    hat = c.get('hat')
    if hat == 'cap':
        d.chord([x - hr * .98, hy - hr * 1.0, x + hr * .98, hy + hr * .35], 180, 360, fill=c['hatc'], outline=OUT, width=max(3, int(6 * s)))
        poly(d, [(x + sg * hr * .2, hy - hr * .3), (x + sg * hr * 1.35, hy - hr * .26), (x + sg * hr * 1.3, hy - hr * .12), (x + sg * hr * .2, hy - hr * .14)], c['hatc'], max(3, int(5 * s)))
    elif hat == 'helmet':
        d.chord([x - hr * 1.05, hy - hr * 1.1, x + hr * 1.05, hy + hr * .25], 180, 360, fill=c['hatc'], outline=OUT, width=max(3, int(6 * s)))
        rect(d, x - hr * 1.2, hy - hr * .5, x + hr * 1.2, hy - hr * .36, c['hatc'], max(3, int(5 * s)))
        rect(d, x - hr * .12, hy - hr * 1.12, x + hr * .12, hy - hr * .5, (255, 160, 70), 0)
    elif hat == 'bun':
        d.chord([x - hr * 1.0, hy - hr * .98, x + hr * 1.0, hy + hr * .3], 180, 360, fill=c['hatc'], outline=OUT, width=max(3, int(6 * s)))
        ell(d, x, hy - hr * 1.02, hr * .38, hr * .3, c['hatc'], max(3, int(5 * s)))
    if c.get('bald'):
        for k in (-1, 1): ell(d, x + k * hr * .92, hy - hr * .05, hr * .14, hr * .3, (60, 45, 35), 0)
    # eyes
    ey = hy - hr * .12
    for k in (-1, 1):
        ex = x + k * hr * .3 + look * S(6)
        if eyes == 'closed' or (eyes == 'wink' and k == 1):
            d.line([(ex - S(26), ey), (ex + S(26), ey)], fill=OUT, width=max(2, int(6 * s)))
            continue
        r = S(38) if eyes == 'wide' else S(30)
        ell(d, ex, ey, r, r * 1.1, WHITE, max(2, int(5 * s)))
        pr = S(8) if eyes == 'wide' else S(10)
        ell(d, ex + look * S(12) + (k * -S(4) if eyes == 'cross' else 0), ey + S(2), pr, pr, OUT, 0)
        if eyes == 'angry':
            d.line([(ex - k * S(30), ey - S(40)), (ex + k * S(28), ey - S(22))], fill=OUT, width=max(2, int(8 * s)))
        if eyes == 'roll':
            ell(d, ex, ey + S(2), r * .95, r * 1.05, WHITE, 0); ell(d, ex, ey - S(18), pr, pr, OUT, 0)
    if c.get('glasses'):
        for k in (-1, 1): d.ellipse([x + k * hr * .3 - S(40), ey - S(40), x + k * hr * .3 + S(40), ey + S(40)], outline=OUT, width=max(2, int(6 * s)))
    if c.get('stache'):
        poly(d, [(x - S(55), hy + S(38)), (x, hy + S(22)), (x + S(55), hy + S(38)), (x + S(40), hy + S(52)), (x, hy + S(40)), (x - S(40), hy + S(52))], (90, 55, 35), max(2, int(4 * s)))
    # mouth
    my = hy + S(62)
    if mouth > 0.08:
        mh = S(10 + 34 * mouth)
        d.chord([x - S(34), my - mh * .3, x + S(34), my + mh], 0, 180, fill=(110, 20, 30), outline=OUT, width=max(2, int(5 * s)))
    else:
        d.line([(x - S(26), my), (x + S(26), my)], fill=OUT, width=max(2, int(5 * s)))
    if who == 'NEL' and prop != 'boia':
        d.line([(x + S(26), my), (x + S(70), my - S(10))], fill=(230, 200, 140), width=max(2, int(6 * s)))
    # props
    hx, hyy = hrp
    if prop == 'espeto':
        line(d, [(hx, hyy), (hx + sg * S(40), hyy - S(170))], (150, 150, 150), int(S(8)))
        for i in range(3): ell(d, hx + sg * S(13 + i * 9), hyy - S(55 + i * 40), S(20), S(16), (150, 60, 40), 3)
    elif prop == 'cavadeira':
        line(d, [(hx, hyy - S(160)), (hx, hyy + S(140))], (150, 100, 60), int(S(14)))
        poly(d, [(hx - S(30), hyy + S(130)), (hx + S(30), hyy + S(130)), (hx + S(20), hyy + S(200)), (hx - S(20), hyy + S(200))], (160, 160, 170), 4)
    elif prop == 'makita':
        rect(d, hx - S(40), hyy - S(30), hx + S(70), hyy + S(20), (30, 140, 150), 5, r=int(S(10)))
        ell(d, hx + sg * S(110), hyy - S(5), S(55), S(55), (200, 200, 205), 5)
        ell(d, hx + sg * S(110), hyy - S(5), S(10), S(10), OUT, 0)
    elif prop == 'celular' or prop == 'telefone':
        rect(d, hx - S(18), hyy - S(40), hx + S(18), hyy + S(20), (40, 40, 50), 4, r=int(S(6)))
    elif prop == 'guardanapo':
        poly(d, [(hx - S(60), hyy - S(70)), (hx + S(60), hyy - S(80)), (hx + S(70), hyy + S(20)), (hx - S(55), hyy + S(30))], (250, 250, 240), 4)
        d.line([(hx - S(40), hyy - S(20)), (hx + S(40), hyy - S(20))], fill=(60, 60, 200), width=4)
        d.rectangle([hx - S(20), hyy - S(20), hx + S(20), hyy + S(5)], outline=(60, 60, 200), width=4)
    elif prop == 'cabo':
        line(d, [(hx, hyy), (hx + sg * S(120), hyy - S(80)), (hx + sg * S(220), hyy + S(20))], (60, 120, 220), int(S(16)))
    elif prop == 'boia':
        d.ellipse([x - S(170), legy - S(60), x + S(170), legy + S(40)], fill=(240, 90, 120), outline=OUT, width=6)
        d.ellipse([x - S(100), legy - S(35), x + S(100), legy + S(15)], fill=(70, 160, 230), outline=OUT, width=5)
    return x, hy

# ---------------- captions ----------------
def build_blocks(words):
    """words: list of dict w,s,e (abs times) -> blocks list of list"""
    blocks = []; cur = []
    for w in words:
        t = w['w'].upper().replace('...', '')
        cand = ' '.join([x['t'] for x in cur] + [t])
        if cur and (len(cur) >= 3 or len(cand) > 16):
            blocks.append(cur); cur = []
        cur.append(dict(t=t, s=w['s'], e=w['e']))
        if re.search(r'[.!?,:]$', t): blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    return blocks

def draw_caption(d, blocks, t, keys=(), water=(), y=1480):
    cur = None
    for i, b in enumerate(blocks):
        nxt = blocks[i + 1][0]['s'] if i + 1 < len(blocks) else b[-1]['e'] + 0.35
        if b[0]['s'] <= t < min(nxt, b[-1]['e'] + 0.6): cur = b; break
    if not cur: return
    f = F(800, 78)
    shown = [w for w in cur if w['s'] <= t]
    if not shown: return
    txt = [re.sub(r'[,.:!?]+$', '', w['t']) for w in cur]
    full = ' '.join(txt); tw = d.textlength(full, font=f)
    x = W / 2 - tw / 2
    for w, tx in zip(cur, txt):
        wl = d.textlength(tx + ' ', font=f)
        if w['s'] <= t:
            k = clamp((t - w['s']) / 0.12); sc = 0.7 + 0.3 * eout(k)
            fs = F(800, max(10, int(78 * sc)))
            base = re.sub(r'[^A-ZÀ-Ü0-9×÷]', '', tx)
            col = LBLUE if any(base.startswith(q) for q in water) else (YEL if any(base.startswith(q) for q in keys) else WHITE)
            d.text((x + d.textlength(tx, font=f) / 2, y), tx, font=fs, fill=col, stroke_width=7, stroke_fill=OUT, anchor='mm')
        x += wl

# ---------------- audio helpers ----------------
def envelope(wav_path, dur_frames):
    import wave
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', wav_path, '-ac', '1', '-ar', '12000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(r, dtype=np.int16).astype(np.float32) / 32768
    n = 12000 // FPS
    fr = [float(np.sqrt(np.mean(a[i * n:(i + 1) * n] ** 2))) if i * n < len(a) else 0 for i in range(dur_frames)]
    return fr
