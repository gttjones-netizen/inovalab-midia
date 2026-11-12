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

# ---------------- c0 ----------------
def sc_c0(img, c, t):
    k = "c0"
    if t < S(k, 2):
        h = lerp(30, 176, seg(t, 0, 2.4)); skyline(img, t, h=h)
        bloquinho(img, 120, 196, eyes="wide", pose="point")
        c.cam = (lerp(204, 192, seg(t, 2.0, 5)), lerp(60, 108, seg(t, 2.0, 5)), lerp(1.7, 1.0, seg(t, 2.0, 5)))
        c.L("544 m", 1480, 260, 150, YEL, t, 0.3, S(k, 2))
        c.L("O RESIDENCIAL MAIS ALTO DO MUNDO (PROJETO)", 960, 110, 44, WHITE, t, S(k, 1) + 0.5, S(k, 2), w=800, box=DARK)
        c.L("NO BRASIL · PERTINHO DO MAR", 1480, 400, 44, WHITE, t, S(k, 1) + 4.2, S(k, 2), w=800)
        c.L("EM CIMA DE AREIA", 1340, 930, 50, YEL, t, S(k, 1) + 7.0, S(k, 2))
    elif t < S(k, 5):
        cutview(img); scale_note(c, t)
        z = seg(t, S(k, 3), S(k, 3) + 0.6); c.cam = (lerp(192, 192, z), lerp(108, 130, z), lerp(1.0, 1.7, z))
        if S(k, 3) <= t < S(k, 3) + 0.5: c.shake = 1
        c.L("E AS ESTACAS QUE SEGURAM ISSO?", 960, 120, 56, WHITE, t, S(k, 2), S(k, 3))
        c.L("60 cm", 500, 420, 190, YEL, t, S(k, 3), S(k, 5))
        c.L("MENOS QUE A LARGURA DE UMA PORTA", 960, 930, 46, WHITE, t, S(k, 4), S(k, 5), w=800, box=DARK)
    elif t < S(k, 6):
        cutview(img, prog=seg(t, S(k, 5), S(k, 5) + 5)); scale_note(c, t)
        c.L("PARECE LOUCURA?", 500, 300, 70, WHITE, t, S(k, 5), S(k, 5) + 4.6)
        c.L("798 ESTACAS", 480, 300, 84, YEL, t, S(k, 5) + 4.8, S(k, 6))
        c.L("ROCHA A 40 m", 480, 880, 70, WHITE, t, S(k, 5) + 7.0, S(k, 6))
        c.L("1.600 t DE GELO", 1470, 560, 70, LBLUE, t, S(k, 5) + 9.2, S(k, 6))
        if t >= S(k, 5) + 9.2: icecubes(img, t, S(k, 5) + 9.2, 262, 372, 0, 60, 14)
    else:
        cutview(img); dim(img, 0.4)
        items = [("POR QUE NÃO AFUNDA", S(k, 6) + 2.2), ("FINA x GIGANTE", S(k, 6) + 5.0), ("E A SUA CASA", S(k, 6) + 8.0)]
        for i, (s, t0) in enumerate(items):
            c.L(s, 360 + i * 600, 540, 46, YEL if i % 2 == 0 else WHITE, t, t0, 1e9, box=(20, 24, 32, 230))
        c.L("ATÉ O FIM DO VÍDEO", 960, 300, 60, WHITE, t, S(k, 6), 1e9)

# ---------------- c1 ----------------
def sc_c1(img, c, t):
    k = "c1"
    if t < S(k, 3):
        skyline(img, t, h=lerp(70, 172, seg(t, S(k, 1), S(k, 2) + 2)))
        c.cam = (192, 108, lerp(1.08, 1.0, seg(t, 0, 6)))
        c.L("BALNEÁRIO CAMBORIÚ · SC", 960, 200, 76, YEL, t, 0.3, S(k, 1))
        c.L("JÁ TEM OS PRÉDIOS MAIS ALTOS DO BRASIL", 960, 200, 48, WHITE, t, S(k, 1), S(k, 1) + 3.4, w=800)
        c.L("AGORA QUER O RECORDE MUNDIAL", 960, 200, 52, YEL, t, S(k, 1) + 3.4, S(k, 2))
        c.L("SENNA TOWER", 560, 300, 80, WHITE, t, S(k, 2) + 0.3, S(k, 3))
        c.L("544 m", 560, 430, 120, YEL, t, S(k, 2) + 4.0, S(k, 3)); c.L("PROJETO DIVULGADO", 560, 530, 30, WHITE, t, S(k, 2) + 4.0, S(k, 3), w=800)
    elif t < S(k, 5):
        sky(img); gy = 196; tex(img, SANDB, 0, gy, LW, LH)
        skytower(img, 100, gy, 97 * seg(t, S(k, 3) + 2.0, S(k, 3) + 3.2), 14)
        skytower(img, 192, gy, 112, 16)
        skytower(img, 290, gy, 170 * seg(t, S(k, 4) + 0.2, S(k, 4) + 2.0), 22)
        c.L("SENNA TOWER", 960, 330, 34, WHITE, t, S(k, 3), 1e9, w=800); c.L("544 m", 960, 390, 60, YEL, t, S(k, 3), 1e9)
        c.L("RECORDE ATUAL · NOVA YORK", 500, 410, 30, WHITE, t, S(k, 3) + 3.0, 1e9, w=800); c.L("472 m", 500, 470, 60, WHITE, t, S(k, 3) + 3.0, 1e9)
        c.L("BURJ KHALIFA · DUBAI", 1450, 60, 30, WHITE, t, S(k, 4) + 1.6, 1e9, w=800); c.L("828 m", 1450, 120, 60, WHITE, t, S(k, 4) + 1.6, 1e9)
    elif t < S(k, 10):
        sky(img); gy = 190; tex(img, SANDB, 0, gy, LW, LH); skytower(img, 192, gy, 170, 22)
        p = seg(t, S(k, 6), S(k, 9) + 3)
        arrow(img, 192, 20, 192, 20 + 150 * p + 4, RED, 4)
        sq = int(3 * p); box(img, 150, gy, 234, gy + sq, (150, 120, 70))
        c.L("ALTURA É FÁCIL DE IMAGINAR", 500, 200, 46, WHITE, t, S(k, 5), S(k, 6), w=800)
        c.L("O DIFÍCIL É O PESO", 500, 200, 64, YEL, t, S(k, 6), S(k, 7) + 2.6)
        c.L("130 mil m³", 480, 240, 96, YEL, t, S(k, 7) + 2.6, S(k, 9)); c.L("DE CONCRETO", 480, 330, 36, WHITE, t, S(k, 7) + 2.6, S(k, 9), w=800)
        c.L("28 mil t", 1460, 240, 96, YEL, t, S(k, 7) + 5.6, S(k, 9)); c.L("DE AÇO", 1460, 330, 36, WHITE, t, S(k, 7) + 5.6, S(k, 9), w=800)
        c.L("SÓ O AÇO: QUASE 4 TORRES EIFFEL", 1040, 965, 42, WHITE, t, S(k, 8), S(k, 9), w=800, box=DARK)
        c.L("+300 mil t", 500, 300, 120, YEL, t, S(k, 9) + 2.6, S(k, 10)); c.L("ESTIMATIVA MINHA", 500, 400, 32, WHITE, t, S(k, 9) + 2.6, S(k, 10), w=800)
        if S(k, 9) + 2.6 <= t < S(k, 9) + 3.1: c.shake = 1
    elif t < S(k, 16):
        w0 = S(k, 11); ln = 7 * seg(t, w0, w0 + 1.5) * (0.7 + 0.3 * math.sin(t * 3))
        if t < S(k, 13):
            skyline(img, t, h=172, lean=ln)
            for i in range(4):
                if t >= w0: xx = ((t - w0) * 150 + i * 60) % 190; arrow(img, xx - 16, 34 + i * 16, xx + 6, 34 + i * 16, LBLUE, 2)
            c.L("UM SEGUNDO PROBLEMA", 560, 240, 56, WHITE, t, S(k, 10), w0)
            c.L("O VENTO", 560, 240, 110, LBLUE, t, w0, S(k, 12) + 1)
            c.L("UMA ALAVANCA GIGANTE", 560, 240, 60, YEL, t, S(k, 12) + 1, S(k, 13))
        else:
            cutview(img, lean=10 * (0.75 + 0.25 * math.sin(t * 3))); scale_note(c, t)
            for i in range(3): xx = ((t * 150 + i * 50) % 130); arrow(img, 20 + xx, 14 + i * 14, 42 + xx, 14 + i * 14, LBLUE, 2)
            if t >= S(k, 14):
                arrow(img, 224, 96, 224, 150, RED, 3); arrow(img, 160, 150, 160, 96, BLUE, 3)
            c.L("A BASE TENTA GIRAR", 960, 930, 50, WHITE, t, S(k, 13), S(k, 14), box=DARK)
            c.L("ESMAGA", 1500, 620, 60, RED, t, S(k, 14), S(k, 15)); c.L("LEVANTA", 480, 620, 60, BLUE, t, S(k, 14) + 1.5, S(k, 15))
            c.L("1 · SEGURAR O PESO", 520, 560, 50, YEL, t, S(k, 15) + 3.2, S(k, 16), box=DARK)
            c.L("2 · NÃO DEIXAR TOMBAR", 1420, 560, 50, YEL, t, S(k, 15) + 5.0, S(k, 16), box=DARK)
    else:
        skyline(img, t, h=172); z = seg(t, S(k, 16), S(k, 16) + 1.6)
        c.cam = (lerp(192, 170, z), lerp(108, 186, z), lerp(1.0, 2.6, z))
        c.L("E TUDO ISSO NUM TERRENO DE PRAIA", 960, 300, 54, WHITE, t, S(k, 16), S(k, 17), w=800)
        c.L("QUE TERRENO É ESSE?", 960, 300, 84, YEL, t, S(k, 17), 1e9)

# ---------------- c2 ----------------
def sc_c2(img, c, t):
    k = "c2"; GYc, RY = 64, 172
    if t < S(k, 2):
        sky(img); tex(img, SANDB, 0, 120, LW, LH); tex(img, SEA, 0, 118, 80, LH)
        sk = 34 * seg(t, 2.2, 6.2)
        skytower(img, 200, 121 + sk, 100, 26, crown=False, lean=4 * seg(t, 2.2, 6.2)); tex(img, SANDB, 150, 121, 260, 121 + 60)
        bloquinho(img, 110, 120, eyes="sweat", pose="shrug")
        c.L("“PRÉDIO DE PRAIA FICA NA AREIA”", 960, 150, 54, WHITE, t, 0.4, S(k, 1), w=800)
        c.L("“UM DIA A CIDADE AFUNDA”", 960, 240, 46, WHITE, t, 3.4, S(k, 1), w=800)
        c.L("NÃO É ASSIM", 960, 440, 130, RED, t, S(k, 1), 1e9)
    elif t < S(k, 7):
        cut(img, GYc, RY); scale_note(c, t)
        img[RY:, :] = (img[RY:, :] * 0.12).astype(np.uint8)
        if t >= S(k, 5):
            p = seg(t, S(k, 5) + 1, S(k, 5) + 4.5); q = seg(t, S(k, 6), S(k, 6) + 1.0)
            skytower(img, 193, GYc + 2 + 26 * p, 64, 36, crown=False, lean=3 * p + 9 * q)
            box(img, 150, GYc + 1, 150, GYc + 1, (0, 0, 0))
        c.L("DUAS PARTES BEM DIFERENTES", 960, 130, 56, WHITE, t, S(k, 2), S(k, 3))
        c.L("EM CIMA: SEDIMENTOS", 960, 130, 60, YEL, t, S(k, 3), S(k, 4)); c.L("AREIA E CAMADAS MOLES", 520, 560, 44, WHITE, t, S(k, 3) + 1.5, S(k, 5), w=800)
        c.L("AGUENTA POUCO", 1440, 560, 60, RED, t, S(k, 4), S(k, 5))
        c.L("APOIADO DIRETO: AFUNDA", 500, 140, 48, WHITE, t, S(k, 5) + 1.5, S(k, 6), w=800)
        c.L("E AFUNDA TORTO", 500, 140, 70, RED, t, S(k, 6), S(k, 7))
    elif t < S(k, 11):
        cut(img, GYc, RY); scale_note(c, t)
        rv = seg(t, S(k, 7) + 0.8, S(k, 8) + 0.6); img[RY:, :] = (img[RY:, :] * (0.12 + 0.88 * rv)).astype(np.uint8)
        if t >= S(k, 9):
            arrow(img, 110, GYc + 2, 110, RY - 1, YEL, 2); arrow(img, 110, RY - 2, 110, GYc + 3, YEL, 2)
        if t >= S(k, 10):
            hh = int((RY - GYc) * seg(t, S(k, 10) + 0.5, S(k, 10) + 2.5)); bld(img, 284, GYc + hh, hh, 18, (188, 192, 200))
        c.L("EMBAIXO TEM OUTRA COISA", 960, 130, 56, WHITE, t, S(k, 7), S(k, 8))
        c.L("ROCHA: GRANITO E GNAISSE", 960, 940, 54, YEL, t, S(k, 8) + 0.6, S(k, 11), box=DARK)
        c.L("CENTENAS DE MILHÕES DE ANOS", 960, 130, 46, WHITE, t, S(k, 8) + 2.6, S(k, 9), w=800)
        c.L("~40 m", 360, 590, 96, YEL, t, S(k, 9) + 1.5, S(k, 11))
        c.L("= PRÉDIO DE 13 ANDARES, PRA BAIXO", 1300, 130, 44, WHITE, t, S(k, 10) + 2.0, S(k, 11), w=800)
    elif t < S(k, 15):
        pr = seg(t, S(k, 12) + 1.2, S(k, 12) + 4.6) if t >= S(k, 12) else 0.0
        cutview(img, prog=max(pr, 0.001) if pr < 1 else 1.0, block=t >= S(k, 12) + 3.6, tower=True); scale_note(c, t)
        if t >= S(k, 14):
            for x in (160, 193, 226): arrow(img, x, 90, x, 90 + 86 * seg(t, S(k, 14), S(k, 14) + 1.2), RED, 2)
        c.L("A IDEIA É SIMPLES DE FALAR", 520, 140, 48, WHITE, t, S(k, 11), S(k, 12), w=800)
        c.L("IGNORAR A AREIA", 480, 480, 52, WHITE, t, S(k, 12), S(k, 13))
        c.L("ATRAVESSAR TUDO", 480, 570, 52, WHITE, t, S(k, 12) + 1.6, S(k, 13))
        c.L("ENTREGAR O PESO PRA ROCHA", 480, 660, 44, YEL, t, S(k, 12) + 3.0, S(k, 13), w=800)
        c.L("AREIA = CAMINHO", 1480, 500, 56, WHITE, t, S(k, 13), S(k, 15))
        c.L("ROCHA = APOIO", 1480, 940, 60, YEL, t, S(k, 14), S(k, 15))
    else:
        cutview(img); dim(img, 0.4)
        c.L("SIMPLES DE FALAR.", 960, 220, 56, WHITE, t, S(k, 15), S(k, 17))
        c.L("300 mil t", 620, 470, 110, YEL, t, S(k, 16) + 1.6, S(k, 17)); c.L("ATÉ 40 m DE PROFUNDIDADE?", 1360, 470, 50, WHITE, t, S(k, 16) + 3.2, S(k, 17), w=800)
        c.L("A DECISÃO MAIS CURIOSA DO PROJETO", 960, 480, 60, YEL, t, S(k, 17), 1e9)

# ---------------- c3 ----------------
def sc_c3(img, c, t):
    k = "c3"
    if t < S(k, 2):
        fatview(img, sea=True); scale_note(c, t); bloquinho(img, 100, 64, pose="point")
        c.L("ARRANHA-CÉU = ESTACA ENORME?", 960, 940, 54, WHITE, t, 0.3, S(k, 1), box=DARK)
        c.L("NORMALMENTE, SIM", 960, 940, 60, YEL, t, S(k, 1), 1e9, box=DARK)
    elif t < S(k, 4):
        gy = 96; cut(img, gy, 196, sea=False)
        for x in PXS(5, 158, 222): box(img, x, gy + 8, x + 8, 204, PILE)
        tex(img, CONC, 148, gy + 1, 238, gy + 11); skytower(img, 193, gy + 1, 96, 30)
        a = S(k, 2); scale_note(c, t)
        c.L("BURJ KHALIFA · 828 m", 520, 150, 56, WHITE, t, a + 0.4, S(k, 4))
        c.L("194 ESTACAS ESCAVADAS", 500, 600, 48, YEL, t, a + 3.4, S(k, 4))
        c.L("Ø 1,5 m", 1480, 600, 90, YEL, t, a + 6.6, S(k, 4))
        c.L("~43 m DE COMPRIMENTO", 1480, 720, 40, WHITE, t, a + 9.2, S(k, 4), w=800)
        c.L("LAJE DE 3,70 m", 1480, 440, 44, WHITE, t, a + 12.4, S(k, 4), w=800)
        c.L("FONTE: BAKER ET AL. (SOM), 2013", 1500, 60, 24, (225, 225, 225), t, a + 3.4, S(k, 4), w=700, sw=3)
        if t >= S(k, 3):
            car(img, 60, gy, s=2); box(img, 62, gy + 4, 62 + 38, gy + 10, PILE)
            c.L("QUASE A LARGURA DE UM CARRO", 480, 880, 40, WHITE, t, S(k, 3), S(k, 4), w=800, box=DARK)
    elif t < S(k, 6):
        cutview(img); scale_note(c, t)
        c.L("SENNA TOWER: O CAMINHO OPOSTO", 960, 940, 50, WHITE, t, S(k, 4), S(k, 5), box=DARK)
        c.L("798 ESTACAS", 480, 480, 84, YEL, t, S(k, 5) + 0.4, S(k, 6)); c.L("SÓ NO BLOCO DA TORRE", 480, 570, 32, WHITE, t, S(k, 5) + 1.6, S(k, 6), w=800)
        c.L("Ø 60 cm", 1480, 520, 100, YEL, t, S(k, 5) + 3.8, S(k, 6))
    elif t < S(k, 7):
        img[:] = (24, 28, 36); box(img, 191, 0, 193, LH, (60, 64, 76))
        for i in range(12):
            r, cc = divmod(i, 4); ellipse(img, (40 + cc * 32, 60 + r * 36, 62 + cc * 32, 82 + r * 36), PILE, (90, 90, 96))
        n = int(96 * seg(t, S(k, 6), S(k, 6) + 1.5))
        for i in range(n):
            r, cc = divmod(i, 12); box(img, 212 + cc * 13, 52 + r * 15, 217 + cc * 13, 57 + r * 15, PILE)
        c.L("194 x Ø 1,5 m", 480, 150, 50, WHITE, t, S(k, 6), 1e9); c.L("798 x Ø 60 cm", 1440, 150, 50, YEL, t, S(k, 6), 1e9)
        c.L("4x MAIS ESTACAS", 1440, 940, 50, YEL, t, S(k, 6) + 0.4, 1e9); c.L("VISTA DE CIMA · ESQUEMA", 480, 940, 28, (225, 225, 225), t, S(k, 6), 1e9, w=700)
    elif t < S(k, 8):
        sky(img); tex(img, SANDB, 0, 150, LW, LH); off = (t - S(k, 7)) * 60
        for i in range(40):
            x = int(i * 14 - off % 14); box(img, x, 138, x + 6, 150, PILE); box(img, x, 138, x + 6, 139, (120, 120, 128))
        bloquinho(img, 60, 150, pose="point", eyes="wide")
        c.L("EM FILA: ~30 km", 960, 380, 110, YEL, t, S(k, 7) + 1.2, 1e9)
    elif t < S(k, 10):
        cutview(img); dim(img, 0.4)
        c.L("POR QUE ALGUÉM ESCOLHERIA ISSO?", 960, 440, 64, WHITE, t, S(k, 8), S(k, 9))
        c.L("O MOTIVO: O TIPO DE ESTACA", 960, 440, 68, YEL, t, S(k, 9), 1e9)
    elif t < S(k, 12):
        drillbg(img); dep = 150 * seg(t, S(k, 10), S(k, 12) + 4) * 0.55
        hole(img, 192, 40, dep, w=34); box(img, 176, 40 + 3, 208, 40 + dep, (150, 118, 76))
        for i in range(5): yy = 44 + ((t * 9 + i * 13) % max(4, dep - 6)); box(img, 180 + i * 5, yy, 183 + i * 5, yy + 2, (176, 146, 100))
        rig(img, 150, 40, mast=34); scale_note(c, t)
        clockface(c, t, 1560, 330, 100, 25, S(k, 10), S(k, 12), None)
        c.L("ESTACA ESCAVADA DE GRANDE DIÂMETRO", 960, 940, 44, WHITE, t, S(k, 10), S(k, 11), w=800, box=DARK)
        c.L("LENTA", 1560, 560, 80, RED, t, S(k, 10) + 1.5, S(k, 12))
        c.L("LAMA PRA SEGURAR O FURO", 480, 520, 42, WHITE, t, S(k, 11) + 0.6, S(k, 12), w=800)
        c.L("MUITO RESÍDUO", 480, 610, 42, WHITE, t, S(k, 11) + 3.6, S(k, 12), w=800)
    elif t < S(k, 15):
        drillbg(img); scale_note(c, t)
        if t < S(k, 13):
            dep = 164 * seg(t, S(k, 12) + 0.6, S(k, 12) + 4.6); hole(img, 192, 40, dep); auger(img, 192, -20, 40 + dep, ph=-t * 16, w=13); rig(img, 160, 40, mast=36)
            c.L("ESTACA DE 60 cm: HÉLICE CONTÍNUA", 960, 940, 46, WHITE, t, S(k, 12), S(k, 13), w=800, box=DARK)
            c.L("BEM MAIS RÁPIDO", 1500, 430, 60, YEL, t, S(k, 12) + 3.6, S(k, 13))
        else:
            n = int(12 * seg(t, S(k, 13), S(k, 13) + 2.4))
            for i in range(n): tex(img, GROUT, 40 + i * 27, 40, 46 + i * 27, 204)
            if n < 12: auger(img, 43 + n * 27, -20, 40 + 160 * (((t - S(k, 13)) * 5) % 1), ph=-t * 30, w=9)
            c.L("12 ESTACAS NUM ÚNICO DIA", 960, 320, 76, YEL, t, S(k, 13) + 0.4, S(k, 14))
            c.L("FUNDAÇÃO PREVISTA: 120 DIAS ÚTEIS", 960, 300, 46, WHITE, t, S(k, 14), S(k, 15), w=800)
            c.L("FICOU PRONTA EM 70", 960, 420, 84, YEL, t, S(k, 14) + 3.0, S(k, 15))
    else:
        drillbg(img); tex(img, GROUT, 185, 40, 199, 204); bloquinho(img, 120, 40, pose="thumb" if t < S(k, 17) else "point"); scale_note(c, t)
        z = seg(t, S(k, 19), S(k, 19) + 1.4); c.cam = (192, lerp(108, 120, z), lerp(1.0, 2.4, z))
        if t >= S(k, 19): cage(img, 192, 44, 44 + 150 * z, w=10)
        c.L("PRA QUEM É DA ÁREA", 960, 940, 44, WHITE, t, S(k, 15), S(k, 16), w=800, box=DARK)
        c.L("HÉLICE CONTÍNUA: COMUM EM PRÉDIO NO BRASIL", 960, 940, 42, WHITE, t, S(k, 16), S(k, 17), w=800, box=DARK)
        c.L("A NOVIDADE NÃO É A TÉCNICA", 1420, 420, 46, WHITE, t, S(k, 17), S(k, 18), w=800)
        c.L("É O EXTREMO", 1440, 400, 80, YEL, t, S(k, 18), S(k, 19)); c.L("INÉDITO NESSE PORTE, SEGUNDO A CONSTRUTORA", 1300, 500, 30, WHITE, t, S(k, 18) + 2.5, S(k, 19), w=800)
        c.L("A ESTACA MUDOU POR DENTRO", 960, 940, 52, YEL, t, S(k, 19), 1e9, box=DARK)

# ---------------- c4 ----------------
def sc_c4(img, c, t):
    k = "c4"; X = 192; GY = 40; RY = 190; BOT = RY + 16
    if t < S(k, 3):
        sky(img); tex(img, SANDB, 0, 176, LW, LH); x = int(lerp(430, 210, seg(t, 0.3, 2.6)))
        rig(img, x, 176, mast=150); auger(img, x + 14, 30, 172, ph=t * 12, w=7, dirt=False)
        bloquinho(img, 110, 176, eyes="wide" if t >= S(k, 2) else "normal", pose="point")
        c.L("FUNCIONA ASSIM", 520, 220, 60, WHITE, t, 0.2, S(k, 1) + 2.4)
        c.L("UM SACA-ROLHAS DE AÇO", 520, 220, 54, YEL, t, S(k, 1) + 2.4, S(k, 2))
        c.L("VEIO DA ITÁLIA", 520, 220, 56, WHITE, t, S(k, 2) + 1.2, S(k, 3))
        c.L("87 t", 1560, 300, 140, YEL, t, S(k, 2) + 3.2, S(k, 3))
        c.L("TORRE DE ~36 m", 1520, 450, 54, WHITE, t, S(k, 2) + 5.4, S(k, 3))
    elif t < S(k, 7):
        drillbg(img); scale_note(c, t)
        d1 = (RY - GY) * seg(t, S(k, 3) + 0.2, S(k, 4) - 0.3); d2 = (BOT - RY) * seg(t, S(k, 5), S(k, 5) + 2.4)
        dep = d1 + d2; hole(img, X, GY, dep); auger(img, X, GY - 60, GY + dep, ph=-t * 14, w=13)
        if S(k, 4) - 0.3 <= t < S(k, 4) + 0.3: c.shake = 1
        z = seg(t, S(k, 4), S(k, 5) + 0.5); c.cam = (X, lerp(108, 170, z), lerp(1.0, 2.0, z))
        c.L("ATRAVESSA A AREIA", 480, 300, 54, WHITE, t, S(k, 3), S(k, 4) - 0.3)
        c.L("ENCOSTOU NA ROCHA", 480, 300, 54, YEL, t, S(k, 4) - 0.3, S(k, 5))
        c.L("+5 m DENTRO DA ROCHA", 480, 300, 60, YEL, t, S(k, 5) + 0.6, S(k, 6)); c.L("SEGUNDO O PROJETO DIVULGADO", 480, 390, 28, WHITE, t, S(k, 5) + 0.6, S(k, 6), w=800)
        c.L("É O QUE TRAVA A ESTACA NA PEDRA", 960, 940, 46, WHITE, t, S(k, 6), S(k, 7), w=800, box=DARK)
    elif t < S(k, 14):
        drillbg(img); scale_note(c, t); up = seg(t, S(k, 9), S(k, 11) + 1.0); tip = lerp(BOT, GY, up)
        hole(img, X, GY, BOT - GY); tex(img, GROUT, X - 7, tip, X + 7, BOT); auger(img, X, tip - 190, tip, ph=t * 14, w=13)
        if S(k, 8) <= t < S(k, 12):
            for i in range(3): yy = tip - 40 + ((t * 50 + i * 14) % 38); box(img, X - 1, yy, X + 1, yy + 4, LBLUE)
        c.L("A PARTE ESPERTA", 480, 300, 56, WHITE, t, S(k, 7), S(k, 8))
        c.L("O TRADO É OCO", 480, 300, 64, LBLUE, t, S(k, 8), S(k, 9))
        c.L("INJETA DE BAIXO PRA CIMA", 480, 300, 46, WHITE, t, S(k, 9), S(k, 10), w=800)
        c.L("O FURO NUNCA FICA VAZIO", 480, 300, 48, YEL, t, S(k, 10), S(k, 11), w=800)
        c.L("NÃO DESMORONA", 480, 300, 52, WHITE, t, S(k, 11), S(k, 12)); c.L("SEM LAMA", 480, 390, 52, YEL, t, S(k, 11) + 1.3, S(k, 12))
        if t >= S(k, 12):
            panel(img, 250, 60, 366, 138)
            for i, (nm, d0) in enumerate([("PROFUNDIDADE", 1.6), ("PRESSÃO", 2.6), ("VOLUME", 3.4)]):
                if t >= S(k, 12) + d0:
                    v = 0.55 + 0.35 * math.sin(t * (2 + i) + i); box(img, 258, 70 + i * 22, 258 + int(98 * v), 78 + i * 22, (GRN, YEL, LBLUE)[i])
                    c.L(nm, 1540, 318 + i * 110, 26, WHITE, t, 0, 1e9, w=800, sw=3)
            c.L("MONITORADO POR COMPUTADOR", 480, 300, 42, WHITE, t, S(k, 12), S(k, 13), w=800)
            c.L("HÉLICE CONTÍNUA MONITORADA", 960, 940, 50, YEL, t, S(k, 13), S(k, 14), box=DARK)
    elif t < S(k, 18):
        drillbg(img); tex(img, GROUT, X - 7, GY, X + 7, BOT); scale_note(c, t)
        z = seg(t, S(k, 14), S(k, 14) + 1.2); c.cam = (lerp(192, 230, z), lerp(108, 120, z), lerp(1.0, 1.5, z))
        c.L("NÃO É CONCRETO COMUM", 1380, 300, 46, WHITE, t, S(k, 14), S(k, 15) + 1.6, w=800)
        c.L("GRAUTE DE 90 MPa", 1380, 300, 70, YEL, t, S(k, 15) + 1.6, S(k, 16)); c.L("SEGUNDO O DIVULGADO DA OBRA", 1380, 390, 28, WHITE, t, S(k, 15) + 1.6, S(k, 16), w=800)
        if t >= S(k, 16):
            panel(img, 244, 56, 352, 176)
            g1 = seg(t, S(k, 16) + 2.0, S(k, 16) + 3.0); g2 = seg(t, S(k, 16) + 0.3, S(k, 16) + 1.0) if False else seg(t, S(k, 17) - 1.4, S(k, 17) - 0.2)
            box(img, 262, 168 - 30 * g1, 286, 168, (150, 150, 148)); box(img, 310, 168 - 96 * g2, 334, 168, YEL)
            c.L("CASA", 1370, 880, 30, WHITE, t, S(k, 16) + 2.0, S(k, 18), w=800, sw=3); c.L("25 a 30", 1370, 650, 34, WHITE, t, S(k, 16) + 2.6, S(k, 18), sw=3)
            c.L("SENNA", 1610, 880, 30, YEL, t, S(k, 17) - 1.4, S(k, 18), w=800, sw=3); c.L("90 MPa", 1610, 330, 38, YEL, t, S(k, 17) - 0.4, S(k, 18), sw=3)
            c.L("3x MAIS RESISTENTE", 520, 520, 60, YEL, t, S(k, 17), S(k, 18))
    elif t < S(k, 22):
        drillbg(img); tex(img, GROUT, X - 7, GY, X + 7, BOT); scale_note(c, t)
        if t < S(k, 20):
            if t >= S(k, 19): cage(img, X, GY + 2, GY + 2 + 30 * seg(t, S(k, 19), S(k, 19) + 1.2), w=10)
            c.L("POR ÚLTIMO: A ARMADURA", 480, 300, 48, WHITE, t, S(k, 18), S(k, 19), w=800)
            c.L("HÉLICE COMUM: ARMA SÓ O TOPO", 480, 300, 42, WHITE, t, S(k, 19), S(k, 20), w=800)
        else:
            dn = seg(t, S(k, 20), S(k, 20) + 3.4); cage(img, X, GY + 2, GY + 2 + (BOT - GY - 6) * dn, w=10)
            c.L("AQUI: AÇO ATÉ O FUNDO", 480, 300, 50, YEL, t, S(k, 20), S(k, 21)); c.L("40 m", 480, 420, 100, YEL, t, S(k, 20) + 2.6, S(k, 21))
            c.L("FINA", 1440, 300, 60, WHITE, t, S(k, 21), S(k, 22)); c.L("MATERIAL FORTÍSSIMO", 1440, 400, 48, WHITE, t, S(k, 21) + 1.0, S(k, 22))
            c.L("AÇO ATÉ A ROCHA", 1440, 500, 48, WHITE, t, S(k, 21) + 2.2, S(k, 22))
    else:
        drillbg(img); tex(img, GROUT, X - 7, GY, X + 7, BOT); cage(img, X, GY + 2, BOT - 4, w=10); dim(img, 0.4)
        c.L("POR QUE TANTO EXAGERO?", 960, 400, 76, WHITE, t, S(k, 22), 1e9)
        c.L("A CONTA ASSUSTA", 960, 560, 90, RED, t, S(k, 23) + 2.6, 1e9)

# ---------------- c5 ----------------
def sc_c5(img, c, t):
    k = "c5"; X = 192; GY = 40; RY = 190; BOT = RY + 16
    if t < S(k, 4):
        img[:] = BOARD; box(img, 20, 22, 364, 26, (120, 90, 50)); box(img, 20, 190, 364, 194, (120, 90, 50)); bloquinho(img, 54, 188, pose="point", scale=2)
        c.L("CONTA DE PADARIA", 1100, 220, 76, WHITE, t, 0.3, 1e9)
        c.L("ESTIMATIVA MINHA · NÃO É NÚMERO OFICIAL", 1100, 330, 34, YEL, t, S(k, 1), 1e9, w=800)
        c.L("+300.000 t", 1100, 480, 100, WHITE, t, S(k, 2) + 1.0, 1e9)
        c.L("÷ 798 ESTACAS", 1100, 610, 80, WHITE, t, S(k, 3) + 0.6, 1e9)
        c.L("= 300 a 400 t EM CADA UMA", 1100, 760, 70, YEL, t, S(k, 3) + 3.6, 1e9)
    elif t < S(k, 8):
        if t < S(k, 7):
            img[:] = ASPH; ellipse(img, (152, 68, 232, 148), (110, 110, 116), (30, 30, 34))
            for i in range(-3, 4): line(img, [(160, 108 + i * 9), (224, 108 + i * 9)], (84, 84, 90), 1)
            ellipse(img, (158, 74, 226, 142), (0, 0, 0), (60, 60, 66), alpha=0.0)
            if t >= S(k, 6):
                yy = lerp(-90, 62, ease((t - S(k, 6)) / 0.5)); box(img, 150, yy, 234, yy + 46, (70, 74, 86)); box(img, 150, yy, 234, yy + 3, (110, 114, 126))
                if S(k, 6) + 0.45 <= t < S(k, 6) + 1.0: c.shake = 1
                c.L("300 e TANTAS t", 960, 420, 70, YEL, t, S(k, 6) + 0.5, S(k, 7))
            c.L("AGORA OLHA A ÁREA", 960, 150, 56, WHITE, t, S(k, 4), S(k, 5))
            c.L("Ø 60 cm = UMA TAMPA DE BUEIRO", 960, 150, 56, YEL, t, S(k, 5), S(k, 7))
        else:
            sky(img); tex(img, CONC, 0, 190, LW, LH); wob = 2 * math.sin(t * 5)
            box(img, 182, 172, 202, 176, (150, 100, 50)); box(img, 184, 176, 187, 190, (120, 80, 40)); box(img, 197, 176, 200, 190, (120, 80, 40))
            r = random.Random(5)
            for row in range(9):
                n = 9 - row // 2
                for i in range(n):
                    car(img, int(192 - n * 11 + i * 22 + wob * row / 5), 172 - row * 11, col=(r.randint(120, 230), r.randint(60, 200), r.randint(50, 200)))
            bloquinho(img, 70, 190, eyes="sweat", pose="up")
            c.L("~200 CARROS NUM BANQUINHO", 960, 940, 50, YEL, t, S(k, 7) + 0.3, 1e9, box=DARK)
    elif t < S(k, 14):
        drillbg(img); scale_note(c, t)
        pc = PILE if t < S(k, 13) else None
        if pc: box(img, X - 7, GY, X + 7, BOT, (198, 200, 206) if not (S(k, 11) <= t < S(k, 13) and int(t * 6) % 2 == 0) else (230, 70, 50))
        else: tex(img, GROUT, X - 7, GY, X + 7, BOT)
        z = seg(t, S(k, 8), S(k, 8) + 1.0) * (1 - seg(t, S(k, 10), S(k, 10) + 1.0)); c.cam = (X, lerp(108, 176, z), lerp(1.0, 2.2, z))
        arrow(img, X, GY - 30, X, GY - 2, RED, 3)
        c.L("A ROCHA AGUENTA SEM RECLAMAR", 960, 150, 50, GRN, t, S(k, 8), S(k, 9), w=800)
        c.L("GRANITO: ABSURDAMENTE RESISTENTE", 960, 150, 46, WHITE, t, S(k, 9), S(k, 10), w=800)
        c.L("O ELO FRACO NÃO É O CHÃO", 500, 420, 46, WHITE, t, S(k, 10), S(k, 11), w=800)
        c.L("É A PRÓPRIA ESTACA", 500, 420, 60, RED, t, S(k, 11), S(k, 12))
        c.L("CONCRETO COMUM + SEGURANÇA DA NORMA", 1420, 420, 34, WHITE, t, S(k, 12), S(k, 13), w=800); c.L("NÃO PASSA", 1420, 520, 80, RED, t, S(k, 12) + 2.6, S(k, 13))
        c.L("POR ISSO: GRAUTE DE 90 MPa", 960, 940, 54, YEL, t, S(k, 13), S(k, 14), box=DARK)
    elif t < S(k, 19):
        ln = 9 * seg(t, S(k, 15), S(k, 16)) * (0.8 + 0.2 * math.sin(t * 3)); cutview(img, lean=ln); scale_note(c, t)
        if t >= S(k, 15):
            for i in range(3): xx = ((t * 150 + i * 50) % 130); arrow(img, 20 + xx, 14 + i * 14, 42 + xx, 14 + i * 14, LBLUE, 2)
        if t >= S(k, 16) + 1.5:
            for x in (218, 226): arrow(img, x + 8, 100, x + 8, 150, RED, 2)
        if t >= S(k, 16) + 4.0:
            for x in (146, 154): arrow(img, x - 6, 150, x - 6, 100, BLUE, 2)
        if t >= S(k, 18):
            for x in PXS(13)[:4]: cage(img, x + 1, 76, 182, w=2)
        c.L("E O AÇO ATÉ O FUNDO?", 960, 940, 50, WHITE, t, S(k, 14), S(k, 15), box=DARK)
        c.L("LEMBRA DO VENTO", 520, 220, 60, LBLUE, t, S(k, 15), S(k, 16))
        c.L("MAIS CARGA", 1500, 640, 50, RED, t, S(k, 16) + 1.5, S(k, 17)); c.L("PUXADAS PRA CIMA", 440, 640, 46, BLUE, t, S(k, 16) + 4.0, S(k, 17))
        c.L("CONCRETO: ÓTIMO APERTADO, PÉSSIMO PUXADO", 960, 940, 40, WHITE, t, S(k, 17), S(k, 18), w=800, box=DARK)
        c.L("QUEM SEGURA PUXÃO É O AÇO", 960, 940, 52, YEL, t, S(k, 18), S(k, 19), box=DARK)
    elif t < S(k, 24):
        cutview(img); dim(img, 0.38)
        c.L("CADA DETALHE TEM UM MOTIVO", 960, 170, 58, WHITE, t, S(k, 19), 1e9)
        c.L("FINA", 380, 380, 60, YEL, t, S(k, 20), 1e9); c.L("RÁPIDA E COM CONTROLE", 1160, 380, 44, WHITE, t, S(k, 20) + 0.8, 1e9, w=800)
        c.L("MUITAS", 380, 500, 60, YEL, t, S(k, 21), 1e9); c.L("DIVIDEM A CARGA", 1160, 500, 44, WHITE, t, S(k, 21) + 0.6, 1e9, w=800)
        c.L("FORTÍSSIMA", 380, 620, 60, YEL, t, S(k, 22), 1e9); c.L("QUEM LIMITA É O MATERIAL, NÃO O SOLO", 1160, 620, 38, WHITE, t, S(k, 22) + 1.6, 1e9, w=800)
        c.L("GUARDA ESSA FRASE", 960, 800, 50, WHITE, t, S(k, 23), 1e9, box=(160, 40, 30, 230))
    else:
        cut(img, 64, 172); scale_note(c, t)
        for i, x in enumerate(PXS(13)):
            wv = int(2 * math.sin(t * 5 + i)); box(img, x + wv, 60, x + 2 + wv, 184, PILE)
        if t >= S(k, 26): icecubes(img, t, S(k, 26), 120, 264, 0, 60, 24)
        c.L("798 ESTACAS SOLTAS NÃO SEGURAM NADA", 960, 940, 44, WHITE, t, S(k, 24), S(k, 25), w=800, box=DARK)
        c.L("FALTA A PEÇA QUE JUNTA TUDO", 960, 940, 50, YEL, t, S(k, 25), S(k, 26), box=DARK)
        c.L("O GELO", 960, 480, 150, LBLUE, t, S(k, 26) + 0.5, 1e9)

# ---------------- c6 ----------------
def sc_c6(img, c, t):
    k = "c6"
    if t < S(k, 6):
        blockbg(img, seg(t, 0.6, S(k, 3) + 3.0)); scale_note(c, t)
        if t >= S(k, 4): arrow(img, 320, 128, 320, 66, YEL, 2); arrow(img, 320, 66, 320, 128, YEL, 2)
        if t >= S(k, 5): bus(img, 120, 130, 100, 46)
        c.L("O BLOCO DE FUNDAÇÃO", 960, 150, 64, WHITE, t, 0.3, S(k, 1))
        c.L("AMARRA AS ESTACAS · RECEBE PILARES E NÚCLEO", 960, 150, 40, WHITE, t, S(k, 1) + 1.0, S(k, 2), w=800)
        c.L("1.660 m²", 960, 140, 110, YEL, t, S(k, 2) + 2.2, S(k, 3)); c.L("~4 QUADRAS DE BASQUETE", 960, 240, 40, WHITE, t, S(k, 2) + 4.6, S(k, 3), w=800)
        c.L("7.740 m³ DE CONCRETO", 960, 150, 84, YEL, t, S(k, 3) + 0.8, S(k, 4))
        c.L("+4,5 m", 1775, 400, 56, YEL, t, S(k, 4) + 1.6, S(k, 6)); c.L("ESPESSURA MÉDIA", 1775, 460, 22, WHITE, t, S(k, 4) + 1.6, S(k, 6), w=800)
        c.L("MAIS ALTO QUE UM ÔNIBUS", 960, 150, 56, WHITE, t, S(k, 5), S(k, 6))
    elif t < S(k, 13):
        if S(k, 9) <= t < S(k, 10):
            sky(img); tex(img, SEDI, 0, 150, LW, LH); tex(img, CONC, 40, 140, 344, 150); bloquinho(img, 192, 140, pose="thumb")
            for i in range(6): yy = 138 - ((t * 30 + i * 9) % 40); box(img, 70 + i * 48, yy, 72 + i * 48, yy + 4, (240, 120, 60))
            c.L("VIGA, LAJE: O CALOR VAI EMBORA RÁPIDO", 960, 200, 50, WHITE, t, S(k, 9), S(k, 10), w=800)
        else:
            blockbg(img, 1.0); scale_note(c, t)
            hk = seg(t, S(k, 7), S(k, 8) + 2.0) if t < S(k, 9) else 1.0
            heat(img, hk, 1.0 if t >= S(k, 11) + 2.0 else 0.0)
            cr = S(k, 11) + 4.6
            if t >= cr:
                n = int(8 * seg(t, cr, cr + 1.0)); pts = [(150, 64), (158, 74), (152, 84), (164, 94), (158, 104), (170, 112), (164, 122), (172, 130)][:max(2, n)]
                line(img, pts, (20, 16, 16), 2)
                if t < cr + 0.7: c.shake = 1
            c.L("UM PROBLEMA QUE OBRA PEQUENA NÃO TEM", 960, 150, 44, WHITE, t, S(k, 6), S(k, 7), w=800)
            c.L("CONCRETO ESQUENTA QUANDO ENDURECE", 960, 150, 46, YEL, t, S(k, 7), S(k, 8), w=800)
            c.L("CIMENTO + ÁGUA = CALOR", 960, 150, 64, WHITE, t, S(k, 8), S(k, 9))
            c.L("O MIOLO NÃO TEM PRA ONDE MANDAR O CALOR", 960, 150, 42, WHITE, t, S(k, 10), S(k, 11), w=800)
            c.L("CENTRO QUENTE", 960, 490, 46, WHITE, t, S(k, 11), S(k, 12)); c.L("SUPERFÍCIE FRIA", 960, 150, 46, LBLUE, t, S(k, 11) + 2.0, cr)
            c.L("PODE RACHAR POR DENTRO", 960, 150, 60, RED, t, cr, S(k, 12))
            c.L("TRINCADA ANTES DE RECEBER O PRÉDIO", 960, 150, 46, RED, t, S(k, 12), S(k, 13), w=800)
    elif t < S(k, 17):
        img[:] = (30, 36, 48)
        ellipse(img, (130, 96, 254, 206), (150, 152, 158), (60, 60, 66)); ellipse(img, (146, 108, 238, 150), (96, 98, 104), (60, 60, 66))
        if t >= S(k, 14): icecubes(img, t, S(k, 14), 150, 230, 0, 126, 22)
        bloquinho(img, 70, 206, pose="point", scale=2)
        c.L("PARECE COISA DE COZINHA", 960, 110, 54, WHITE, t, S(k, 13), S(k, 14))
        c.L("TROCAR PARTE DA ÁGUA POR GELO", 960, 110, 52, YEL, t, S(k, 14), S(k, 15))
        c.L("+1.600 t DE GELO", 960, 110, 90, LBLUE, t, S(k, 15) + 0.8, S(k, 16))
        if t >= S(k, 16):
            panel(img, 300, 40, 344, 200); box(img, 318, 52, 326, 190, (60, 64, 76))
            lv = lerp(0, 96, seg(t, S(k, 16), S(k, 16) + 1.4)); box(img, 318, 190 - lv, 326, 190, LBLUE); box(img, 312, 190 - 108, 332, 190 - 107, RED)
            c.L("LIMITE: 27 °C", 1360, 400, 44, RED, t, S(k, 16) + 1.4, S(k, 17), anchor="rm"); c.L("MÉDIA: 24 °C", 1360, 520, 54, LBLUE, t, S(k, 16) + 3.4, S(k, 17), anchor="rm")
    elif t < S(k, 18):
        blockbg(img, 1.0); heat(img, 0.38); bloquinho(img, 40, 60, pose="thumb"); scale_note(c, t)
        c.L("COMEÇA MAIS FRIO, PICO MAIS BAIXO", 960, 150, 50, WHITE, t, S(k, 17), S(k, 17) + 4.4, w=800)
        c.L("O BLOCO CURA INTEIRO", 960, 150, 64, GRN, t, S(k, 17) + 4.4, 1e9)
    elif t < S(k, 20):
        cutview(img); scale_note(c, t)
        if t >= S(k, 19):
            g = seg(t, S(k, 19) + 1.0, S(k, 19) + 2.4)
            for x in (40, 84): hh = int(96 * g); bld(img, x, 172, hh, 22, (188, 192, 200))
        c.L("A FUNDAÇÃO INTEIRA", 960, 940, 44, WHITE, t, S(k, 18), S(k, 18) + 2.4, box=DARK)
        c.L("+12 mil m³ DE CONCRETO", 1420, 480, 50, YEL, t, S(k, 18) + 2.4, S(k, 20))
        c.L("~1.800 t DE AÇO", 1420, 580, 50, YEL, t, S(k, 18) + 4.8, S(k, 20))
        c.L("= 2 PRÉDIOS DE 50 ANDARES, ENTERRADOS", 960, 940, 44, WHITE, t, S(k, 19) + 0.6, S(k, 20), w=800, box=DARK)
    else:
        if t < S(k, 21):
            skyline(img, t, h=172); c.L("NÃO É A ÚNICA PRAIA COM PRÉDIO ALTO", 960, 160, 50, WHITE, t, S(k, 20), S(k, 21), w=800)
        else:
            orla(img, [4 * seg(t, S(k, 21), S(k, 21) + 2) * s for s in (1, -1.2, 0.8, 1.4, -0.9, 1.1, -1.3, 0.7)])
            c.L("EM OUTRA PRAIA, O FINAL FOI DIFERENTE", 960, 150, 52, YEL, t, S(k, 21), 1e9, w=800)

# ---------------- c7 ----------------
def sc_c7(img, c, t):
    k = "c7"
    if t < S(k, 2):
        orla(img, [s * 4 for s in (1, -1.2, 0.8, 1.4, -0.9, 1.1, -1.3, 0.7)])
        c.L("SANTOS · SP", 960, 170, 90, YEL, t, 0.3, S(k, 1))
        c.L("QUASE 100 PRÉDIOS INCLINADOS", 960, 170, 60, WHITE, t, S(k, 1), 1e9); c.L("A MAIORIA DOS ANOS 60 E 70", 960, 270, 40, WHITE, t, S(k, 1) + 2.8, 1e9, w=800)
    elif t < S(k, 7):
        p = seg(t, S(k, 5) + 1.0, S(k, 6)) if t >= S(k, 5) else 0
        santos_cut(img, lean=7 * p, sink=7 * p, bulb=seg(t, S(k, 5), S(k, 5) + 2.5) if t >= S(k, 5) else 0); scale_note(c, t)
        if t < S(k, 3): img[92:, :] = (img[92:, :] * 0.35).astype(np.uint8)
        elif t < S(k, 3) + 4.0: img[190:, :] = (img[190:, :] * 0.35).astype(np.uint8)
        c.L("POR CIMA, PARECE IGUAL: AREIA", 960, 150, 50, WHITE, t, S(k, 2), S(k, 3), w=800)
        c.L("ARGILA MOLE", 440, 640, 60, LBLUE, t, S(k, 3) + 1.4, S(k, 7))
        c.L("TERRENO FIRME: ~55 m", 520, 1000 - 20, 40, WHITE, t, S(k, 3) + 4.2, S(k, 5), w=800, anchor="lm")
        c.L("FUNDAÇÃO RASA: SAPATAS A 1 OU 2 m", 960, 150, 46, YEL, t, S(k, 4), S(k, 5), w=800)
        c.L("A ARGILA FOI CEDENDO", 960, 150, 52, WHITE, t, S(k, 5) + 1.8, S(k, 6))
        c.L("+2°", 1500, 300, 150, RED, t, S(k, 6) + 1.2, S(k, 7))
    elif t < S(k, 11):
        if t < S(k, 9):
            cutview(img); scale_note(c, t)
            for x in (160, 193, 226): arrow(img, x, 90, x, 176, GRN, 2)
            c.L("BALNEÁRIO CAMBORIÚ: A REGRA VIROU OUTRA", 960, 150, 46, WHITE, t, S(k, 7), S(k, 8), w=800)
            c.L("PRÉDIO ALTO VAI ATÉ A ROCHA", 960, 150, 58, YEL, t, S(k, 8), 1e9)
        elif t < S(k, 10):
            cut(img, 96, 172); scale_note(c, t)
            for x in PXS(15, 120, 266): box(img, x, 104, x + 2, 180, PILE)
            tex(img, CONC, 112, 97, 276, 106); skytower(img, 160, 97, 90, 26); skytower(img, 228, 97, 90, 26)
            c.L("YACHTHOUSE · 2 TORRES · +280 m", 960, 940, 46, WHITE, t, S(k, 9), 1e9, w=800, box=DARK)
            c.L("925 ESTACAS", 400, 640, 60, YEL, t, S(k, 9) + 4.2, 1e9); c.L("DE 28 m", 1540, 640, 60, YEL, t, S(k, 9) + 5.4, 1e9)
            c.L("SEGUNDO OS DADOS DIVULGADOS DA OBRA", 960, 780, 26, (225, 225, 225), t, S(k, 9) + 5.8, 1e9, w=700, sw=3)
        else:
            cutview(img); scale_note(c, t)
            c.L("SENNA TOWER: A MESMA RECEITA", 960, 150, 52, WHITE, t, S(k, 10), S(k, 10) + 2.4, w=800)
            c.L("MAIS FUNDO · MUITO MAIS CARGA", 960, 150, 54, YEL, t, S(k, 10) + 2.4, 1e9)
    elif t < S(k, 14):
        santos_cut(img, lean=7, sink=7, x=96); b = np.array(img[:, :192]).copy()
        gy = 64; sky(img, y1=gy); mid = gy + 46; tex(img, SANDB, 194, gy, LW, mid); tex(img, SEDI, 194, mid, LW, 176); tex(img, ROCK, 194, 176, LW, LH)
        for x in PXS(11, 252, 322): box(img, x, gy + 8, x + 2, 188, PILE)
        tex(img, CONC, 246, gy + 1, 330, gy + 10); skytower(img, 288, gy + 1, gy + 30, 34, crown=False)
        img[:, :192] = b; box(img, 190, 0, 194, LH, (16, 18, 24))
        # desloca o corte direito pro centro do painel
        c.L("SANTOS", 480, 110, 50, WHITE, t, S(k, 11), 1e9, box=DARK); c.L("BALNEÁRIO CAMBORIÚ", 1440, 110, 44, WHITE, t, S(k, 11), 1e9, box=DARK)
        c.L("NÃO É SORTE, NEM O TIPO DE AREIA", 960, 540, 50, WHITE, t, S(k, 11) + 1.8, S(k, 12), w=800, box=DARK)
        c.L("É DECISÃO DE PROJETO", 960, 540, 76, YEL, t, S(k, 12), S(k, 13), box=DARK)
        c.L("APOIAR NO QUE ESTÁ PERTO", 480, 940, 36, WHITE, t, S(k, 13), 1e9, w=800, box=DARK)
        c.L("BUSCAR O QUE É FIRME", 1440, 940, 40, YEL, t, S(k, 13) + 1.0, 1e9, w=800, box=DARK)
    elif t < S(k, 15):
        sky(img, sunset=0.5); ground_strip(img, 150); foundation(img, 140, 151, 5); draw_tower(img, 140, 151, 8, 5)
        skytower(img, 250, 150, 70, 24, crown=False, lean=5)
        c.L("JÁ TEM VÍDEO NO CANAL", 960, 150, 56, WHITE, t, S(k, 14), 1e9)
        c.L("TORRE DE PISA E OS PRÉDIOS DE SANTOS", 960, 940, 46, YEL, t, S(k, 14) + 1.6, 1e9, w=800, box=DARK)
    else:
        housecut(img); bloquinho(img, 220, 90, pose="point", flip=True)
        c.L("E PRA QUEM CONSTRÓI UMA CASA?", 1300, 200, 54, YEL, t, S(k, 15) + 1.0, 1e9, w=800)

# ---------------- c8 ----------------
def tripod(img, x, gy):
    line(img, [(x - 20, gy), (x, gy - 54)], (90, 90, 96), 2); line(img, [(x + 20, gy), (x, gy - 54)], (90, 90, 96), 2); line(img, [(x, gy), (x, gy - 54)], (60, 60, 66), 1)

def sc_c8(img, c, t):
    k = "c8"
    if t < S(k, 3):
        housecut(img); bloquinho(img, 210, 90, pose="point", flip=True)
        c.L("EU PROJETO ESTRUTURA TODO DIA", 1280, 180, 46, WHITE, t, 0.3, S(k, 1), w=800)
        c.L("CASAS E PRÉDIOS DE ATÉ 3 ANDARES", 1280, 260, 36, WHITE, t, 2.4, S(k, 1), w=800)
        c.L("PARANÁ", 1300, 180, 90, YEL, t, S(k, 1) + 0.3, S(k, 2)); c.L("A GRANDE MAIORIA DAS OBRAS É EM ESTACA", 960, 940, 42, WHITE, t, S(k, 1) + 1.4, S(k, 2), w=800, box=DARK)
        c.L("A MINHA CONTA É O OPOSTO DA SENNA TOWER", 960, 940, 42, YEL, t, S(k, 2), 1e9, w=800, box=DARK)
    elif t < S(k, 7):
        housecut(img)
        if t < S(k, 6):
            arrow(img, 98, 46, 98, 66, RED, 2); arrow(img, 134, 46, 134, 66, RED, 2)
            c.L("CARGA DE CADA PILAR: PEQUENA", 1280, 180, 44, WHITE, t, S(k, 3), S(k, 4), w=800)
            c.L("QUEM DECIDE QUANTAS ESTACAS?", 1280, 180, 44, WHITE, t, S(k, 4), S(k, 5), w=800)
            c.L("O SOLO", 1300, 240, 130, YEL, t, S(k, 5), S(k, 6))
        else:
            g = S(k, 6); tripod(img, 40, 90)
            if t >= g + 0.3: box(img, 39, 90, 41, 90 + 100 * seg(t, g + 0.3, g + 2.4), (60, 60, 66))
            if t >= g + 6.0:
                for x in (96, 132): arrow(img, x - 8, 130, x - 2, 130, BLUE, 1); arrow(img, x + 12, 130, x + 5, 130, BLUE, 1); arrow(img, x + 1, 166, x + 1, 154, GRN, 2)
            for i, (s, d0) in enumerate([("1 · SONDAGEM", 0.3), ("2 · ATÉ ONDE O EQUIPAMENTO CHEGA", 2.2), ("3 · QUANTO O SOLO SEGURA (LATERAL + PONTA)", 6.0), ("4 · CARGA DO PILAR ÷ ESSE VALOR", 10.0)]):
                c.L(s, 900, 200 + i * 110, 32, YEL if i == 3 else WHITE, t, g + d0, 1e9, w=800, box=DARK, anchor="lm")
    elif t < S(k, 10):
        gy = 70; sky(img, y1=gy); tex(img, SILT, 0, gy, 190, 160); tex(img, CLAY, 0, 160, 190, LH); box(img, 0, gy, 190, gy + 2, (86, 170, 60))
        for x in (66, 100): box(img, x, gy, x + 3, gy + 62, PILE)
        house(img, 62, gy)
        mid = gy + 46; tex(img, SANDB, 194, gy, LW, mid); tex(img, SEDI, 194, mid, LW, 176); tex(img, ROCK, 194, 176, LW, LH); box(img, 190, 0, 194, LH, (16, 18, 24))
        for x in PXS(11, 252, 322): box(img, x, gy + 8, x + 2, 188, PILE)
        tex(img, CONC, 246, gy + 1, 330, gy + 10); skytower(img, 288, gy + 1, gy + 30, 34, crown=False)
        c.L("CASA: O LIMITE É O SOLO", 480, 940, 40, WHITE, t, S(k, 7), 1e9, w=800, box=DARK)
        c.L("SENNA: O LIMITE É A ESTACA", 1440, 940, 40, YEL, t, S(k, 8) + 1.6, 1e9, w=800, box=DARK)
        c.L("MESMA LÓGICA, ELO FRACO EM OUTRO LUGAR", 960, 540, 44, WHITE, t, S(k, 9), 1e9, w=800, box=DARK)
    elif t < S(k, 23):
        if t < S(k, 11):
            housecut(img); dim(img, 0.4); c.L("3 LIÇÕES PRA QUALQUER OBRA", 960, 480, 76, YEL, t, S(k, 10), 1e9)
        elif t < S(k, 16):
            housecut(img); tripod(img, 230, 90); box(img, 229, 90, 231, 90 + 110 * seg(t, S(k, 12), S(k, 12) + 3), (60, 60, 66)); bloquinho(img, 268, 90, flip=True)
            c.L("1 · FUNDAÇÃO COMEÇA NA SONDAGEM", 960, 150, 52, YEL, t, S(k, 11), 1e9, w=800, box=DARK)
            c.L("SEM ISSO, QUALQUER CÁLCULO É CHUTE", 960, 940, 44, WHITE, t, S(k, 13), S(k, 14), w=800, box=DARK)
            c.L("SENNA TOWER: 4 ANOS DE ESTUDO", 960, 940, 44, WHITE, t, S(k, 14), S(k, 15), w=800, box=DARK)
            c.L("SUA CASA: PELO MENOS UMA SONDAGEM", 960, 940, 44, YEL, t, S(k, 15), S(k, 16), w=800, box=DARK)
        elif t < S(k, 19):
            housecut(img)
            if t >= S(k, 18):
                box(img, 0, 158, LW, 160, GRN); arrow(img, 300, 120, 300, 156, GRN, 3)
            c.L("2 · A PERGUNTA NÃO É “QUÃO FUNDA?”", 960, 150, 50, YEL, t, S(k, 16), 1e9, w=800, box=DARK)
            c.L("ONDE ESTÁ O SOLO QUE AGUENTA?", 1240, 600, 40, WHITE, t, S(k, 18), 1e9, w=800)
            c.L("QUAL É O ELO FRACO: O CHÃO OU A ESTACA?", 960, 940, 42, WHITE, t, S(k, 18) + 2.0, 1e9, w=800, box=DARK)
        else:
            drillbg(img, gy=70); box(img, 110, 70, 150, 204, PILE); tex(img, GROUT, 240, 70, 250, 204); cage(img, 245, 72, 200, w=6)
            if t >= S(k, 21): bloquinho(img, 290, 70, pose="thumb", flip=True)
            c.L("3 · MAIS CONCRETO NÃO É MAIS SEGURANÇA", 960, 150, 46, YEL, t, S(k, 19), 1e9, w=800, box=DARK)
            c.L("ESTACA FINA PORQUE FEZ CONTA", 960, 940, 46, WHITE, t, S(k, 21), S(k, 22), w=800, box=DARK)
            c.L("FUNDAÇÃO BOA = FUNDAÇÃO DIMENSIONADA", 960, 940, 44, YEL, t, S(k, 22), 1e9, w=800, box=DARK)
    else:
        sky(img, sunset=0.3); tex(img, SANDB, 0, 170, LW, LH); tex(img, SEA, 0, 196, LW, LH)
        bloquinho(img, 150, 170, scale=2, pose="point" if t < S(k, 25) else "thumb")
        if t >= S(k, 24) + 4.0: bloquinho(img, 240, 170, scale=2, flip=True, helmet=(80, 160, 255), vest=(80, 200, 120), pose="thumb")
        c.L("A MINHA OPINIÃO, BEM DIRETA", 960, 150, 52, WHITE, t, S(k, 23), S(k, 24))
        c.L("TERRENO DIFÍCIL: PRAIA, RIO, ATERRO", 960, 150, 48, WHITE, t, S(k, 24), S(k, 24) + 4.0, w=800)
        c.L("GEOTÉCNICO COM EXPERIÊNCIA + CALCULISTA", 960, 150, 46, YEL, t, S(k, 24) + 4.0, S(k, 25), w=800)
        c.L("CALCULISTA: A ESTRUTURA", 520, 300, 44, WHITE, t, S(k, 25), 1e9, w=800, box=DARK)
        c.L("GEOTÉCNICO: O SOLO", 1440, 300, 44, YEL, t, S(k, 26), 1e9, w=800, box=DARK)

# ---------------- c9 ----------------
def sc_c9(img, c, t):
    k = "c9"; end = DUR(k) + 0.3
    if t < S(k, 3):
        cutview(img); scale_note(c, t)
        c.L("+500 m EM CIMA DE 60 cm?", 960, 940, 54, WHITE, t, 0.3, S(k, 1), box=DARK)
        c.L("NÃO É A GROSSURA QUE SEGURA", 960, 940, 50, YEL, t, S(k, 1), S(k, 2), box=DARK)
        c.L("A ROCHA", 440, 520, 64, YEL, t, S(k, 2) + 0.2, S(k, 3)); c.L("A QUANTIDADE", 440, 620, 54, YEL, t, S(k, 2) + 1.6, S(k, 3))
        c.L("O MATERIAL", 1500, 560, 60, YEL, t, S(k, 2) + 3.2, S(k, 3))
    elif t < S(k, 5):
        cutview(img); scale_note(c, t); z = seg(t, S(k, 3), S(k, 3) + 1.2); c.cam = (192, lerp(108, 110, z), lerp(1.0, 1.3, z))
        c.L("A AREIA NUNCA FOI O APOIO", 960, 200, 58, WHITE, t, S(k, 3), S(k, 4))
        c.L("ELA É SÓ O CAMINHO", 960, 200, 80, YEL, t, S(k, 4), 1e9)
    elif t < end:
        skyline(img, t, h=172, sunset=0.55)
        if t < S(k, 6):
            bloquinho(img, 204, 24, eyes="sweat", pose="up"); z = seg(t, S(k, 5), S(k, 5) + 1.0); c.cam = (lerp(192, 204, z), lerp(108, 50, z), lerp(1.0, 2.2, z))
            c.L("VOCÊ MORARIA NO ÚLTIMO ANDAR?", 960, 880, 60, WHITE, t, S(k, 5), S(k, 6), box=DARK)
            c.L("CONTA NOS COMENTÁRIOS", 960, 980, 36, YEL, t, S(k, 5) + 1.5, S(k, 6), w=800)
        else:
            bloquinho(img, 120, 196, pose="thumb")
            c.L("SE INSCREVE NO CANAL", 600, 300, 76, YEL, t, S(k, 6) + 2.4, 1e9)
            c.L("TEM MAIS CASO ASSIM VINDO POR AÍ", 600, 400, 38, WHITE, t, S(k, 6) + 4.0, 1e9, w=800)
    else:
        skyline(img, t, h=172, sunset=0.55); dim(img, 0.32)
        c.L("ASSISTA TAMBÉM", 560, 170, 56, WHITE, t, end, 1e9)
        c.L("INSCREVA-SE", 1440, 170, 56, YEL, t, end, 1e9)
        c.L("ENG. EVANNDRO RESENDE · INOVALAB", 960, 1010, 30, WHITE, t, end, 1e9, w=800)

SCENES = {"c0": sc_c0, "c1": sc_c1, "c2": sc_c2, "c3": sc_c3, "c4": sc_c4, "c5": sc_c5, "c6": sc_c6, "c7": sc_c7, "c8": sc_c8, "c9": sc_c9}
