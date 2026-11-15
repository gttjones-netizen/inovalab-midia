from lib import *

TL = json.load(open("timeline.json"))
CH = ["c%d" % i for i in range(10)]
def OFF(k): return TL[k]["offset"]
def DUR(k): return TL[k]["dur"]
def S(k, i): return TL[k]["sents"][i]["start"] - OFF(k)
def E(k, i): return TL[k]["sents"][i]["end"] - OFF(k)
def F(k, sub, d=0.0):
    for s in TL[k]["sents"]:
        if sub in s["raw"]: return s["start"] - OFF(k) + d
    raise KeyError(sub)

TITLES = {"c1": "1 · O TAMANHO DO PROBLEMA", "c2": "2 · O QUE TEM EMBAIXO DA PRAIA", "c3": "3 · POUCAS GROSSAS OU MUITAS FINAS?",
          "c4": "4 · COMO NASCE UMA ESTACA DE 40 m", "c5": "5 · A CONTA QUE ASSUSTA", "c6": "6 · O BLOCO E AS 1.600 t DE GELO",
          "c7": "7 · SANTOS x BALNEÁRIO CAMBORIÚ", "c8": "8 · O QUE ISSO MUDA NO SEU PROJETO", "c9": ""}

class Ctx:
    def __init__(s): s.labels = []; s.cam = (LW / 2, LH / 2, 1.0); s.shake = 0; s.mode = None; s.flash = False
    def L(s, text, x, y, size=70, col=WHITE, t=0, t0=0, t1=1e9, w=900, sw=None, box=None, anchor="mm"):
        if t0 <= t < t1:
            k = 0.7 + 0.3 * ease((t - t0) / 0.14)
            s.labels.append((text, x, y, size * k, col, w, sw if sw is not None else max(3, int(size * 0.09)), box, anchor))

DARK = (16, 18, 24, 215)
ROCK = texmap((84, 86, 98), 10, 21)
SEDI = texmap((156, 134, 98), 10, 22)
GROUT = texmap((178, 180, 186), 6, 23)
GLASS = texmap((60, 104, 150), 10, 24, 400, 120)
PEB = texmap((128, 128, 126), 26, 25)
PILE = (198, 200, 206)

def tex(img, T, x0, y0, x1, y1):
    x0 = max(0, int(x0)); y0 = max(0, int(y0)); x1 = min(LW, int(x1)); y1 = min(LH, int(y1))
    if x1 > x0 and y1 > y0:
        img[y0:y1, x0:x1] = T[np.ix_(np.arange(y0, y1) % T.shape[0], np.arange(x0, x1) % T.shape[1])]

def box(img, x0, y0, x1, y1, col):
    x0 = max(0, int(x0)); y0 = max(0, int(y0)); x1 = min(LW, int(x1)); y1 = min(LH, int(y1))
    if x1 > x0 and y1 > y0: img[y0:y1, x0:x1] = col

def skytower(img, x, yb, h, w=16, crown=True, lean=0.0):
    h = int(h); yb = int(yb)
    for i in range(h):
        y = yb - 1 - i
        if y < 0 or y >= LH: continue
        k = i / max(h, 1)
        ww = w if (k < 0.82 or not crown) else max(2, int(w * (1 - (k - 0.82) / 0.18 * 0.8)))
        x0 = int(round(x - ww / 2 + lean * k * k)); a = max(0, x0); b = min(LW, x0 + ww)
        if b <= a: continue
        row = GLASS[y % 400, np.arange(a, b) % 120].astype(np.int16)
        if i % 5 == 4: row = row + 50
        img[y, a:b] = np.clip(row, 0, 255)
        img[y, a] = (30, 50, 80); img[y, b - 1] = (30, 50, 80)

def bld(img, x, yb, h, w, col=(170, 176, 186)):
    box(img, x, yb - h, x + w, yb, col)
    for y in range(int(yb - h) + 2, int(yb) - 1, 4):
        for xx in range(int(x) + 1, int(x + w) - 1, 3): box(img, xx, y, xx + 1, y + 2, (70, 84, 110))

def skyline(img, t, h=170, second=0, lean=0.0, sunset=0.0, city=True):
    sky(img, sunset=sunset); gy = 196
    poly(img, [(250, gy), (300, 150), (340, 138), (384, 150), (384, gy)], (62, 110, 70))
    if city:
        for x, hh, w in [(128, 40, 12), (144, 58, 10), (158, 34, 13), (226, 50, 11), (240, 62, 12), (256, 38, 14), (274, 46, 10)]:
            bld(img, x, gy, hh, w)
    if second: bld(img, 172, gy, second, 13, (150, 160, 176))
    tex(img, SANDB, 96, gy - 1, LW, LH); tex(img, SEA, 0, gy - 2, 100, LH)
    box(img, 96, gy - 2, 100, gy + 1, (240, 240, 235))
    skytower(img, 204, gy, h, 16, lean=lean)

def cut(img, gy=64, ry=172, sea=True):
    sky(img, y1=gy); mid = int(gy + (ry - gy) * 0.45)
    tex(img, SANDB, 0, gy, LW, mid); tex(img, SEDI, 0, mid, LW, ry); tex(img, ROCK, 0, ry, LW, LH)
    box(img, 0, ry, LW, ry + 1, (52, 54, 62))
    if sea:
        for x in range(0, 70): tex(img, SEA, x, gy, x + 1, gy + 2 + int((70 - x) * 0.25))

def PXS(n, a=154, b=230): return [int(a + (b - a) * i / (n - 1)) for i in range(n)]

def cutview(img, gy=64, ry=172, n=13, prog=1.0, block=True, tower=True, sea=True, emb=12, lean=0.0):
    cut(img, gy, ry, sea); yb = gy + 11 if block else gy + 2
    for i, x in enumerate(PXS(n)):
        Lk = clamp(prog * n - i) if prog < 1 else 1.0
        if Lk > 0: box(img, x, yb - 3, x + 2, yb + (ry + emb - yb) * Lk, PILE)
    if block:
        tex(img, CONC, 148, gy + 1, 238, gy + 11); box(img, 148, gy + 1, 238, gy + 2, (90, 90, 92)); box(img, 148, gy + 10, 238, gy + 11, (90, 90, 92))
    if tower: skytower(img, 193, gy + 1, gy + 30, 40, crown=False, lean=lean)

def scale_note(c, t): c.L("ESQUEMA FORA DE ESCALA", 1700, 1040, 22, (225, 225, 225), t, 0, 1e9, w=700, sw=3)

def auger(img, x, y0, y1, ph=0.0, w=9, dirt=True):
    for y in range(int(max(0, y0)), int(min(LH, y1))):
        box(img, x - 1, y, x + 1, y + 1, (70, 70, 76))
        o = (y + ph) % 6
        if o < 2:
            sh = 1 if int((y + ph) // 6) % 2 == 0 else -1
            box(img, x - w // 2 + sh, y, x + w // 2 + sh + 1, y + 1, (120, 120, 128))
        elif dirt and o < 4: box(img, x - w // 2 + 1, y, x + w // 2, y + 1, (128, 104, 72)); box(img, x - 1, y, x + 1, y + 1, (70, 70, 76))

def rig(img, x, gy, mast=150):
    box(img, x - 30, gy - 5, x + 8, gy, (40, 40, 44)); box(img, x - 28, gy - 4, x + 6, gy - 1, (80, 80, 86))
    box(img, x - 26, gy - 20, x - 4, gy - 5, (240, 190, 40)); box(img, x - 22, gy - 17, x - 12, gy - 10, (120, 190, 235))
    box(img, x - 4, gy - 12, x + 6, gy - 5, (200, 150, 30))
    box(img, x + 6, gy - mast, x + 10, gy, (210, 160, 34)); box(img, x + 4, gy - mast - 3, x + 16, gy - mast, (60, 60, 66))
    line(img, [(x - 20, gy - 20), (x + 7, gy - mast + 10)], (60, 60, 66), 1)

def cage(img, x, y0, y1, w=8):
    y0 = int(y0); y1 = int(y1)
    box(img, x - w // 2, y0, x - w // 2 + 1, y1, (40, 34, 30)); box(img, x + w // 2, y0, x + w // 2 + 1, y1, (40, 34, 30))
    for y in range(y0 - (y0 % 5), y1, 5):
        if y >= y0: box(img, x - w // 2, y, x + w // 2 + 1, y + 1, (70, 50, 40))

def hole(img, x, gy, depth, w=14, T=None):
    if T is None: box(img, x - w // 2, gy, x + w // 2, gy + depth, (26, 22, 20))
    else: tex(img, T, x - w // 2, gy, x + w // 2, gy + depth)

def house(img, x, gy, w=44, h=22):
    box(img, x, gy - h, x + w, gy, (236, 226, 204)); poly(img, [(x - 4, gy - h), (x + w / 2, gy - h - 14), (x + w + 4, gy - h)], (170, 80, 60), (90, 40, 30))
    box(img, x + 6, gy - 14, x + 14, gy, (110, 78, 54)); box(img, x + 24, gy - 16, x + 36, gy - 7, (120, 190, 235))


def drillbg(img, gy=40, ry=190):
    sky(img, y1=gy); mid = gy + 70
    tex(img, SANDB, 0, gy, LW, mid); tex(img, SEDI, 0, mid, LW, ry); tex(img, ROCK, 0, ry, LW, LH); box(img, 0, ry, LW, ry + 1, (52, 54, 62))


def grid798(img, n, x0=40, y0=28, s=8):
    for i in range(int(n)):
        r, cc = divmod(i, 38); box(img, x0 + cc * s, y0 + r * s, x0 + cc * s + 3, y0 + r * s + 3, PILE)


def blockbg(img, fill=1.0, piles=True):
    gy = 60; sky(img, y1=gy); tex(img, SANDB, 0, gy, LW, 150); tex(img, SEDI, 0, 150, LW, LH)
    box(img, 76, gy, 308, 132, (60, 52, 44))
    if piles:
        for x in PXS(15, 86, 296): box(img, x, 122, x + 3, LH, PILE)
    tex(img, CONC, 80, 130 - 66 * fill, 304, 130)


def housecut(img, gy=90):
    sky(img, y1=gy); tex(img, TOPS, 0, gy, LW, gy + 30); tex(img, SILT, 0, gy + 30, LW, 160); tex(img, CLAY, 0, 160, LW, LH)
    box(img, 0, gy, LW, gy + 2, (86, 170, 60))
    for x in (96, 132): box(img, x, gy, x + 3, gy + 62, PILE); box(img, x - 3, gy, x + 6, gy + 5, (150, 150, 148))
    house(img, 92, gy)


# ================= cenas novas (roteiro v2, 12:45) =================
ASPH = texmap((66, 68, 74), 8, 31)
BOARD = texmap((34, 52, 46), 5, 32)
ICE = (190, 228, 250)

def bottom(c, text, t, t0, t1, col=WHITE, size=44):
    c.L(text, 1040, 965, size, col, t, t0, t1, w=800, box=DARK)

def clockface(c, t, cx, cy, r, speed=40, t0=0, t1=1e9, label=None):
    if t0 <= t < t1: c.labels.append(("__clock__", cx, cy, r, (t - t0) * speed, label))

def fatview(img, n=5, gy=64, ry=172, sea=False, tower=True, th=None, w=8):
    cut(img, gy, ry, sea)
    for x in PXS(n, 158, 222): box(img, x, gy + 8, x + w, ry + 6, PILE)
    tex(img, CONC, 148, gy + 1, 238, gy + 11); box(img, 148, gy + 1, 238, gy + 2, (90, 90, 92))
    if tower: skytower(img, 193, gy + 1, th or gy + 30, 34, crown=True)

def car(img, x, y, col=(200, 60, 50), s=1):
    box(img, x, y - 6 * s, x + 20 * s, y - 2 * s, col); box(img, x + 4 * s, y - 10 * s, x + 15 * s, y - 6 * s, col)
    box(img, x + 6 * s, y - 9 * s, x + 13 * s, y - 6 * s, (150, 200, 235))
    box(img, x + 2 * s, y - 3 * s, x + 6 * s, y, (20, 20, 22)); box(img, x + 14 * s, y - 3 * s, x + 18 * s, y, (20, 20, 22))

def bus(img, x, y, w=96, h=44):
    box(img, x, y - h, x + w, y - 6, (240, 190, 40)); box(img, x, y - h, x + w, y - h + 3, (200, 150, 30))
    for xx in range(int(x) + 6, int(x + w) - 10, 14): box(img, xx, y - h + 8, xx + 10, y - h + 20, (150, 200, 235))
    box(img, x + 10, y - 9, x + 24, y, (20, 20, 22)); box(img, x + w - 26, y - 9, x + w - 12, y, (20, 20, 22))

def icecubes(img, t, t0, x0, x1, y0, y1, n=26, seed=3):
    r = random.Random(seed)
    for i in range(n):
        x = r.randint(x0, x1); ph = r.uniform(0, 1.6); sp = r.uniform(60, 110)
        y = y0 + ((t - t0 + ph) * sp) % max(1, (y1 - y0))
        if t >= t0: box(img, x, y, x + 5, y + 5, ICE); box(img, x, y, x + 5, y + 1, WHITE)

def heat(img, k, cold=0.0, x0=80, x1=304, y0=64, y1=130):
    cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
    for y in range(y0, y1):
        for x in range(x0, x1, 2):
            dd = max(abs(x - cx) / ((x1 - x0) / 2), abs(y - cy) / ((y1 - y0) / 2)); hot = clamp(1.25 - dd * 1.25) * k
            cd = clamp((dd - 0.75) * 4) * cold
            px = img[y, x].astype(float); px = px * (1 - 0.75 * hot) + np.array((235, 70, 30)) * 0.75 * hot
            px = px * (1 - 0.6 * cd) + np.array((70, 150, 235)) * 0.6 * cd; img[y, x:x + 2] = px

def santos_cut(img, gy=64, lean=0.0, sink=0.0, bulb=0.0, x=192):
    sky(img, y1=gy); tex(img, SANDB, 0, gy, LW, 92); tex(img, CLAY, 0, 92, LW, 190); tex(img, ROCK, 0, 190, LW, LH)
    for xx in range(0, 60): tex(img, SEA, xx, gy, xx + 1, gy + 2 + int((60 - xx) * 0.25))
    if bulb > 0: ellipse(img, (x - 46 * bulb, 70, x + 46 * bulb, 70 + 110 * bulb), (230, 60, 40), alpha=0.33)
    box(img, x - 22, gy + 1 + sink, x + 22, gy + 6 + sink, (130, 128, 122))
    skytower(img, x, gy + 2 + sink, 58, 30, crown=False, lean=lean)

def orla(img, leans, gy=176):
    sky(img); tex(img, SANDB, 0, gy, LW, LH); tex(img, SEA, 0, gy + 22, LW, LH); box(img, 0, gy + 21, LW, gy + 23, (240, 240, 235))
    for i, ln in enumerate(leans):
        skytower(img, 44 + i * 44, gy, 62 + (i * 37) % 30, 22, crown=False, lean=ln)

def panel(img, x0, y0, x1, y1): box(img, x0, y0, x1, y1, (16, 18, 24)); box(img, x0 + 1, y0 + 1, x1 - 1, y1 - 1, (30, 34, 44))

def tripod(img, x, gy):
    line(img, [(x - 20, gy), (x, gy - 54)], (90, 90, 96), 2); line(img, [(x + 20, gy), (x, gy - 54)], (90, 90, 96), 2); line(img, [(x, gy), (x, gy - 54)], (60, 60, 66), 1)

