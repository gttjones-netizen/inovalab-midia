from lib import *

TL = json.load(open("timeline.json"))
CH = ["c%d" % i for i in range(10)]
def OFF(k): return TL[k]["offset"]
def DUR(k): return TL[k]["dur"]
def S(k, i): return TL[k]["sents"][i]["start"] - OFF(k)
def E(k, i): return TL[k]["sents"][i]["end"] - OFF(k)

TITLES = {"c1": "1 · UMA TORRE EM CIMA DE UM COLCHÃO", "c2": "2 · ELA COMEÇOU CAINDO PRO OUTRO LADO",
          "c3": "3 · OS 100 ANOS QUE SALVARAM A TORRE", "c4": "4 · AGORA SIM, PRO SUL",
          "c5": "5 · OS CONSERTOS QUE QUASE DERRUBARAM A TORRE", "c6": "6 · COMO ENDIREITAR UMA TORRE TIRANDO TERRA",
          "c7": "7 · PISA NO BRASIL: OS PRÉDIOS TORTOS DE SANTOS", "c8": "8 · O QUE ISSO MUDA NO SEU PROJETO", "c9": ""}

class Ctx:
    def __init__(s): s.labels = []; s.cam = (LW / 2, LH / 2, 1.0); s.shake = 0; s.mode = None; s.flash = False
    def L(s, text, x, y, size=70, col=WHITE, t=0, t0=0, t1=1e9, w=900, sw=None, box=None, anchor="mm"):
        if t0 <= t < t1:
            k = 0.7 + 0.3 * ease((t - t0) / 0.14)
            s.labels.append((text, x, y, size * k, col, w, sw if sw is not None else max(3, int(size * 0.09)), box, anchor))

# ---------- shared ----------
GY = 150
def tower_scene(img, c, t, floors=8, theta=0.0, bowl=0.0, bloq=None, cath=True, curve=0.0, night=0.0, sunset=0.0, tint=None, x=192):
    sky(img, night, sunset)
    if cath: piazza(img, GY)
    xs = np.arange(LW)
    ground_strip(img, GY, dip=lambda xx: bowl * math.exp(-((xx - x - 10) / 30) ** 2))
    sink = bowl * 0.6
    foundation(img, x, GY + 1 + sink, theta)
    draw_tower(img, x, GY + 1 + sink, floors, theta, curve=curve, tint=tint)
    if bloq: bloquinho(img, *bloq[0], **bloq[1])

def section_scene(img, c, t, floors=8, theta=0.0, dip=0.0, south=0.0, consol=0.0, water=0.0, wobble=0.0, x=192, gy=70, fh=7, tw=18):
    img[:] = 0
    sky(img, y1=gy)
    soil_section(img, gy, x + 6, (gy + 34, gy + 120), dip, south, consol, water, t, wobble)
    sink = dip * 0.4
    foundation(img, x, gy + 1 + sink, theta, w=13, d=5)
    draw_tower(img, x, gy + 1 + sink, floors, theta, fh=fh, tw=tw)

def clockface(c, t, cx, cy, r, speed=40, t0=0, t1=1e9, label=None):
    if t0 <= t < t1:
        c.labels.append(("__clock__", cx, cy, r, (t - t0) * speed, label))

# ---------- chapter scenes ----------
def sc_c0(img, c, t):
    k = "c0"
    th = 9 + 0.6 * math.sin(t * 4) if t < S(k, 3) else lerp(9, 7, seg(t, S(k, 3), S(k, 3) + 2))
    tower_scene(img, c, t, 8, th, 8, ((150, GY + 2), dict(pose="push", eyes="wide")))
    c.cam = (lerp(176, 192, seg(t, 0, 5)), lerp(90, 108, seg(t, 0, 5)), lerp(1.5, 1.0, seg(t, 0, 5)))
    if t < 3: c.shake = 1
    c.L("“Por mais cálculos que fizéssemos, ela não devia estar de pé.”", 960, 170, 46, WHITE, t, S(k, 2) + 1.5, S(k, 3), w=800)
    c.L("JOHN BURLAND · ENGENHEIRO DA COMISSÃO (TRADUÇÃO LIVRE)", 960, 235, 26, YEL, t, S(k, 2) + 1.5, S(k, 3), w=800)
    c.L("14.500 t", 1500, 300, 120, YEL, t, S(k, 3) + 0.6, S(k, 4))
    c.L("5,5°", 1500, 470, 120, YEL, t, S(k, 3) + 2.6, S(k, 4))
    c.L("FUNDAÇÃO RASA + ARGILA MOLE", 1500, 600, 44, WHITE, t, S(k, 3) + 5.0, S(k, 4), w=800)
    clockface(c, t, 1500, 420, 110, 30, S(k, 4), S(k, 6), "~100 ANOS PARADA")
    if t >= S(k, 6):
        dim(img, 0.45)
        items = [("O SOLO", S(k, 6) + 0.3), ("TIRAR TERRA", S(k, 7) + 0.6), ("SANTOS", S(k, 7) + 5.0), ("A LIÇÃO", S(k, 8) + 0.5)]
        for i, (s, t0) in enumerate(items):
            c.L(s, 270 + i * 460, 540, 50, YEL if i % 2 == 0 else WHITE, t, t0, 1e9, box=(20, 24, 32, 220))

def sc_c1(img, c, t):
    k = "c1"
    if t < S(k, 5):
        fl = lerp(0.5, 8, seg(t, S(k, 1), S(k, 3) + 3))
        tower_scene(img, c, t, fl, 0, 0, ((240, GY), dict()))
        c.cam = (192, 108, lerp(1.0, 1.06, seg(t, 0, S(k, 5))))
        c.L("1173 · PISA", 960, 200, 110, YEL, t, 0.2, S(k, 1) + 1)
        c.L("CATEDRAL", 250, 860, 36, WHITE, t, S(k, 2), S(k, 3)); c.L("BATISTÉRIO", 1650, 860, 36, WHITE, t, S(k, 2) + 1, S(k, 3)); c.L("CAMPANÁRIO", 960, 860, 40, YEL, t, S(k, 2) + 2.5, S(k, 3))
        c.L("~60 m · 8 ANDARES · OCA", 1500, 260, 50, WHITE, t, S(k, 3) + 1, S(k, 4))
        if t >= S(k, 4):
            c.cam = (192, 140, lerp(1.0, 2.2, seg(t, S(k, 4), S(k, 4) + 1.5)))
            c.L("ANEL DE PEDRA Ø 19,5 m · RASO", 960, 880, 52, YEL, t, S(k, 4) + 1.2, S(k, 5))
    else:
        south = seg(t, S(k, 9), S(k, 9) + 1.5)
        dip = lerp(0, 18, seg(t, S(k, 14), S(k, 15) + 1)) if t >= S(k, 14) else 0
        wob = 2.0 * (1 - seg(t, S(k, 14), S(k, 14) + 0.5)) if S(k, 13) <= t < S(k, 14) + 0.5 else 0
        if t < S(k, 18):
            section_scene(img, c, t, 8, 0, dip, south, 0, 1.0 if t >= S(k, 10) else 0, wob)
            # reveal layers progressively by masking
            if t < S(k, 6): img[100:, :] = (img[100:, :] * 0.15).astype(np.uint8)
            elif t < S(k, 10): img[104:, :] = (img[104:, :] * 0.15).astype(np.uint8)
            elif t < S(k, 12): img[190:, :] = (img[190:, :] * 0.15).astype(np.uint8)
            c.L("A · SILTES E ARGILAS (~10 m)", 360, 470, 34, WHITE, t, S(k, 6), S(k, 18), w=800, anchor="lm")
            c.L("SUL: MAIS ARGILOSO", 1500, 470, 40, YEL, t, S(k, 9), S(k, 18))
            c.L("N", 80, 330, 50, WHITE, t, S(k, 9), S(k, 18)); c.L("S", 1840, 330, 50, WHITE, t, S(k, 9), S(k, 18))
            c.L("B · ARGILA MARINHA MOLE (ATÉ ~40 m)", 360, 700, 36, LBLUE, t, S(k, 10), S(k, 18), w=800, anchor="lm")
            c.L("“PANCONE”", 1500, 780, 46, LBLUE, t, S(k, 11), S(k, 18))
            c.L("C · AREIA DENSA", 360, 950, 36, SAND_C, t, S(k, 12), S(k, 18), w=800, anchor="lm")
            c.L("UM COLCHÃO ENCHARCADO", 960, 140, 64, WHITE, t, S(k, 13), S(k, 14))
            c.L("~3 m DE RECALQUE MÉDIO", 960, 140, 70, YEL, t, S(k, 15), S(k, 18))
            c.cam = (192, 108, 1.0)
        else:
            # comparison: uniform vs differential
            img[:] = 0; sky(img)
            ground_strip(img, GY, 0, 192); ground_strip(img, GY, 192, LW)
            u = seg(t, S(k, 18), S(k, 18) + 1.5); d = seg(t, S(k, 19), S(k, 19) + 2)
            foundation(img, 96, GY + 1 + 6 * u, 0); draw_tower(img, 96, GY + 1 + 6 * u, 8, 0)
            foundation(img, 288, GY + 1 + 4 * d, 7 * d); draw_tower(img, 288, GY + 1 + 4 * d, 8, 7 * d)
            arrow(img, 70, 175, 70, 175 + 10 * u, BLUE); arrow(img, 122, 175, 122, 175 + 10 * u, BLUE)
            arrow(img, 262, 175, 262, 178 + 2 * d, BLUE); arrow(img, 314, 175, 314, 178 + 14 * d, RED)
            line(img, [(192, 0), (192, LH)], (30, 30, 30), 2)
            c.L("RECALQUE IGUAL", 480, 130, 56, GRN, t, S(k, 18), 1e9)
            c.L("RECALQUE DIFERENCIAL", 1440, 130, 56, RED, t, S(k, 19), 1e9)
            c.L("GUARDA ESSE NOME", 1440, 220, 40, WHITE, t, S(k, 21), 1e9)
SAND_C = (230, 205, 140)

def masonry(img, t, t0):
    img[:] = (60, 64, 72)
    for row in range(10):
        y0 = 20 + row * 18
        tilt = (row % 3 - 1) * 2
        for x in range(30, 354, 24):
            hl = 14 + (tilt if x < 192 else -tilt)
            rect(img, x, y0, x + 22, y0 + 14, (226, 220, 206), (150, 140, 120))
        poly(img, [(30, y0 + 15), (354, y0 + 15), (354, y0 + 17 - tilt), (30, y0 + 17 + tilt)], (180, 172, 156))
    p = clamp((t - t0) / 4)
    mx = int(lerp(90, 290, p)); my = int(lerp(60, 140, p))
    ellipse(img, (mx - 34, my - 34, mx + 34, my + 34), (255, 255, 255), (30, 30, 30), alpha=0.25)
    line(img, [(mx + 24, my + 24), (mx + 44, my + 44)], (60, 40, 20), 4)

def sc_c2(img, c, t):
    k = "c2"
    if t < S(k, 3):
        tower_scene(img, c, t, 3.3, 4 * seg(t, 0.5, 2.5), 3, None)
        c.L("O QUE VOCÊ JÁ OUVIU: “COMEÇOU PRO SUL”", 960, 160, 52, WHITE, t, S(k, 1), 1e9, w=800)
        c.L("NÃO FOI BEM ASSIM", 960, 470, 120, RED, t, S(k, 2), 1e9)
        c.L("N", 80, 700, 50, WHITE, t, 0, 1e9); c.L("S", 1840, 700, 50, WHITE, t, 0, 1e9)
    elif t < S(k, 5):
        tower_scene(img, c, t, 3.3, 0, 1, ((250, GY), dict(pose="shrug")))
        rect(img, 164, 60, 166, GY, (110, 80, 40)); rect(img, 218, 60, 220, GY, (110, 80, 40))
        for yy in range(70, GY, 18): rect(img, 160, yy, 224, yy + 1, (110, 80, 40))
        c.L("1178", 960, 190, 140, YEL, t, S(k, 3), 1e9); c.L("NO 4º ANDAR", 960, 320, 56, WHITE, t, S(k, 3) + 1, 1e9)
        c.L("PAROU", 1500, 600, 90, RED, t, S(k, 4), 1e9)
        c.cam = (192, 100, 1.1)
    elif t < S(k, 8):
        masonry(img, t, S(k, 5))
        c.L("BLOCOS EM CUNHA: A INCLINAÇÃO FICOU GRAVADA", 960, 950, 48, YEL, t, S(k, 6), 1e9, box=(20, 24, 32, 220))
    elif t < S(k, 10):
        th = lerp(0, -2.5, seg(t, S(k, 8), S(k, 8) + 2))
        tower_scene(img, c, t, 3.3, th, 1, ((260, GY), dict(eyes="wide")))
        arrow(img, 150, 70, 120, 70, YEL, 3)
        c.L("~¼° PRO NORTE", 560, 220, 80, YEL, t, S(k, 8) + 1.5, 1e9)
        c.L("(inclinação exagerada no desenho)", 560, 310, 30, WHITE, t, S(k, 8) + 1.5, 1e9, w=700)
        c.L("N", 80, 700, 50, WHITE, t, 0, 1e9); c.L("S", 1840, 700, 50, WHITE, t, 0, 1e9)
    elif t < S(k, 13):
        # what-if simulation
        a = S(k, 10)
        fl = lerp(3.3, 8, seg(t, a + 0.5, S(k, 12)))
        th = 0 if t < S(k, 12) else min(90, ((t - S(k, 12)) / 1.4) ** 2 * 90)
        tower_scene(img, c, t, fl, -0.5 + th, lerp(1, 12, seg(t, a, S(k, 12))), ((300, GY), dict(eyes="wide", pose="up")), tint=(220, 80, 70))
        c.L("SIMULAÇÃO: E SE CONTINUASSEM?", 960, 140, 56, RED, t, a, 1e9, box=(20, 24, 32, 220))
        c.L("O SOLO ROMPE", 1450, 560, 70, RED, t, S(k, 12), 1e9)
        if S(k, 12) + 1.2 < t: dust(img, t, S(k, 12) + 1.2, 260, GY - 4, n=60, seed=3, spread=70, dur=2)
        c.shake = 1 if S(k, 12) + 1.2 < t < S(k, 12) + 2 else 0
    else:
        tower_scene(img, c, t, 3.3, -0.8, 1, ((260, GY), dict(pose="idle")), night=0.3 * (0.5 + 0.5 * math.sin(t * 5)))
        if t < S(k, 13) + 1.0: c.mode = "rewind"
        yr = int(lerp(1178, 1272, seg(t, S(k, 13) + 1, S(k, 16))))
        c.L(str(yr), 1500, 260, 130, YEL, t, S(k, 13) + 1, 1e9)
        clockface(c, t, 1500, 560, 120, 25, S(k, 13) + 1, 1e9, None)
        c.L("GUERRAS COM CIDADES VIZINHAS", 560, 160, 44, WHITE, t, S(k, 14), S(k, 15), w=800, box=(20, 24, 32, 200))
        c.L("100 ANOS QUE SALVARAM A TORRE", 960, 960, 64, YEL, t, S(k, 16), 1e9, box=(20, 24, 32, 220))

def grains(img, t, flow=0.0, comp=0.0):
    img[:] = (30, 34, 44)
    r = random.Random(4)
    for i in range(160):
        x = r.randint(10, 374); y = r.randint(30, 200)
        y2 = int(y + comp * (y - 30) * -0.15)
        ellipse(img, (x - 6, y2 - 4, x + 6, y2 + 4), (150, 120, 90), (90, 70, 50))
    rr = random.Random(9)
    for i in range(220):
        x = rr.randint(5, 379); y = rr.randint(25, 205)
        if flow > 0: y = int(y - ((t * 30 * flow + rr.random() * 200) % 200))
        if 20 < y < 210 and rr.random() > comp * 0.8: img[y:y + 2, x:x + 3] = (80, 160, 255)

def piston(img, t, load, drain, gauge):
    img[:] = (30, 34, 44)
    x0, x1, yb = 120, 264, 200
    rect(img, x0 - 4, 40, x0, yb, (180, 180, 190)); rect(img, x1, 40, x1 + 4, yb, (180, 180, 190)); rect(img, x0 - 4, yb, x1 + 4, yb + 4, (180, 180, 190))
    ptop = int(lerp(80, 120, drain))
    rect(img, x0, ptop + 8, x1, yb - 1, (60, 120, 210))
    # spring
    pts = []
    n = 10; hs = (yb - ptop - 10)
    for i in range(n + 1):
        pts.append((192 + (12 if i % 2 else -12), ptop + 8 + hs * i / n))
    line(img, pts, (230, 230, 230), 3)
    rect(img, x0, ptop, x1, ptop + 8, (120, 120, 130), (40, 40, 40))
    rect(img, 186, ptop, 198, ptop + 8, (30, 34, 44))  # hole
    if load > 0:
        ly = int(lerp(-40, ptop - 30, ease(load)))
        rect(img, 150, ly, 234, ly + 30, (110, 110, 120), (40, 40, 40))
    if drain > 0 and drain < 1:
        rr = random.Random(int(t * 12))
        for i in range(6):
            img[ptop - rr.randint(2, 30):ptop - rr.randint(0, 2) + 1, 191:193] = (80, 160, 255)
    # gauge
    gx, gy = 320, 120
    ellipse(img, (gx - 26, gy - 26, gx + 26, gy + 26), (240, 240, 240), (40, 40, 40))
    ang = math.radians(210 - 240 * gauge)
    line(img, [(gx, gy), (gx + 20 * math.cos(ang), gy - 20 * math.sin(ang))], (230, 50, 40), 3)
    rect(img, x0 - 30, ptop + 4, x0 - 4, ptop + 6, (120, 120, 130))

def sc_c3(img, c, t):
    k = "c3"
    if t < S(k, 1):
        img[:] = (24, 28, 36)
        c.L("ADENSAMENTO", 960, 520, 160, YEL, t, 0.2, 1e9)
    elif t < S(k, 3):
        grains(img, t)
        c.L("ESPONJA CHEIA D'ÁGUA", 960, 120, 60, WHITE, t, S(k, 1), 1e9, box=(20, 24, 32, 220))
        c.L("GRÃOS", 400, 980, 44, (220, 180, 140), t, S(k, 2), 1e9, box=(20, 24, 32, 220)); c.L("ÁGUA NOS VAZIOS", 1450, 980, 44, LBLUE, t, S(k, 2) + 1, 1e9, box=(20, 24, 32, 220))
    elif t < S(k, 8):
        load = seg(t, S(k, 3), S(k, 3) + 0.8)
        drain = seg(t, S(k, 6), S(k, 7) + 4)
        gauge = (seg(t, S(k, 5), S(k, 5) + 0.6)) * (1 - drain)
        piston(img, t, load, drain, gauge)
        c.L("MODELO DE TERZAGHI", 960, 100, 50, WHITE, t, S(k, 3), 1e9, box=(20, 24, 32, 220))
        c.L("QUEM SEGURA PRIMEIRO: A ÁGUA", 960, 950, 54, LBLUE, t, S(k, 4), S(k, 6))
        c.L("POROPRESSÃO", 1600, 780, 36, WHITE, t, S(k, 5), 1e9)
        c.L("A ÁGUA SAI · A MOLA (OS GRÃOS) ASSUME", 960, 950, 50, YEL, t, S(k, 6) + 1, 1e9)
    elif t < S(k, 10):
        img[:] = (24, 28, 36)
        rect(img, 30, 60, 180, 190, (200, 175, 115)); rect(img, 204, 60, 354, 190, (112, 122, 138))
        rr = random.Random(int(t * 20))
        for i in range(14): x = rr.randint(40, 170); y = int(60 - ((t * 120 + i * 20) % 50)); img[max(0, y):max(0, y) + 3, x:x + 2] = (80, 160, 255)
        if int(t * 1.5) % 2 == 0: img[56:59, 278:280] = (80, 160, 255)
        c.L("AREIA: MINUTOS", 525, 160, 56, GRN, t, S(k, 8), 1e9); c.L("ARGILA: ANOS OU DÉCADAS", 1395, 160, 56, RED, t, S(k, 9), 1e9)
    elif t < S(k, 14):
        img[:] = (24, 28, 36)
        if t < S(k, 11):
            c.L("KARL TERZAGHI", 960, 420, 120, YEL, t, S(k, 10), 1e9); c.L("ANOS 1920 · PAI DA MECÂNICA DOS SOLOS", 960, 600, 54, WHITE, t, S(k, 10) + 1, 1e9)
        else:
            rect(img, 40, 120, 170, 150, (112, 122, 138)); rect(img, 214, 90, 344, 150, (112, 122, 138))
            arrow(img, 105, 148, 105, 122, BLUE); arrow(img, 279, 148, 279, 92, BLUE)
            c.L("t ~ H²", 960, 200, 130, YEL, t, S(k, 11), 1e9)
            c.L("H", 300, 680, 60, WHITE, t, S(k, 12), 1e9); c.L("2H", 1180, 600, 60, WHITE, t, S(k, 12), 1e9)
            c.L("1×", 525, 900, 90, GRN, t, S(k, 13), 1e9); c.L("4×", 1395, 900, 90, RED, t, S(k, 13), 1e9)
    else:
        cons = seg(t, S(k, 15), S(k, 17))
        section_scene(img, c, t, 3.3, -0.8, lerp(4, 10, cons), 1, cons, 1.0)
        if S(k, 15) <= t < S(k, 17):
            for x in (60, 192, 324): arrow(img, x, 180, x, 112, BLUE)
        yr = int(lerp(1178, 1272, cons))
        c.L(str(yr), 1600, 200, 110, YEL, t, S(k, 15), 1e9)
        c.L("ARGILA GANHANDO RESISTÊNCIA", 960, 950, 54, LBLUE, t, S(k, 16), S(k, 18), box=(20, 24, 32, 200))
        c.L("FOI SORTE", 960, 520, 150, YEL, t, S(k, 19), S(k, 20))
        c.L("HOJE A GENTE FAZ ISSO DE PROPÓSITO", 960, 950, 54, GRN, t, S(k, 20), 1e9, box=(20, 24, 32, 220))

def carpet(img, t, t0, ttop):
    sky(img)
    for x in range(LW):
        y = 170 + int(2 * math.sin(x * 0.2))
        img[y:, x] = (150, 60, 70)
    n = int(clamp((t - t0) / 0.5) * 1)
    blocks = int(clamp((t - t0) / (ttop - t0)) * 9) + 1
    th = 0
    if t > ttop: th = min(80, ((t - ttop) / 1.2) ** 2 * 80)
    cx, base = 192, 170
    pil = Image.fromarray(img).convert("RGBA")
    lay = Image.new("RGBA", (60, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(blocks):
        y = 200 - (i + 1) * 14
        d.rectangle([10 + (i % 2) * 2, y, 50 + (i % 2) * 2, y + 13], fill=[(230, 80, 60), (60, 140, 230), (245, 200, 30), (60, 190, 90)][i % 4] + (255,), outline=(30, 30, 30, 255))
    lay = lay.rotate(-th - 2 * min(1, blocks / 9) * math.sin(t * 3), resample=Image.NEAREST, center=(30, 200), expand=False)
    pil.alpha_composite(lay, (cx - 30, base - 200 + 2))
    img[:] = np.array(pil.convert("RGB"))
    bloquinho(img, 260, 172, pose="up" if t > ttop else "idle", eyes="wide" if t > ttop else "normal")

def sc_c4(img, c, t):
    k = "c4"
    if t < S(k, 8):
        fl = lerp(3.3, 7, seg(t, S(k, 0), S(k, 2) + 1)) if t < S(k, 7) else 7
        th = lerp(-0.8, 2, seg(t, S(k, 1), S(k, 2) + 2))
        if t >= S(k, 7): th = lerp(2, 4, seg(t, S(k, 7), S(k, 7) + 2))
        tower_scene(img, c, t, fl, th, lerp(1, 6, seg(t, S(k, 1), S(k, 7) + 2)), ((290, GY), dict()))
        c.L("1272", 960, 190, 130, YEL, t, 0.1, S(k, 1))
        c.L("AGORA PRO SUL", 1450, 300, 64, YEL, t, S(k, 1), S(k, 2))
        c.L("1278 · 0,6° SUL", 960, 190, 100, YEL, t, S(k, 2), S(k, 3))
        c.L("PAROU DE NOVO (GUERRA)", 960, 190, 72, RED, t, S(k, 3), S(k, 6))
        clockface(c, t, 1500, 480, 110, 30, S(k, 6), S(k, 7), "~80 ANOS")
        c.L("1360 · 1,6°", 960, 190, 110, YEL, t, S(k, 7), 1e9)
        c.L("(inclinação exagerada no desenho)", 960, 290, 30, WHITE, t, S(k, 1), 1e9, w=700)
        c.L("N", 80, 700, 50, WHITE, t, 0, 1e9); c.L("S", 1840, 700, 50, WHITE, t, 0, 1e9)
    elif t < S(k, 13):
        cv = lerp(0, -1.6, seg(t, S(k, 9), S(k, 9) + 3))
        tower_scene(img, c, t, 8 if t >= S(k, 9) + 2 else 7, 4, 6, None, curve=cv)
        if t >= S(k, 11):
            pts = [(192 + 4 * 0 + i * 0.0, 0) for i in range(1)]
            # dashed curve axis
            for i in range(0, 9):
                a = math.radians(4); h = 10 + i * 15
                xx = 192 + h * math.sin(a) + cv * i * math.cos(a); yy = GY + 3 - h * math.cos(a)
                rect(img, int(xx) - 1, int(yy) - 3, int(xx) + 1, int(yy) + 3, YEL)
        c.L("CADA ANDAR CORRIGIDO PRO OUTRO LADO", 960, 140, 50, WHITE, t, S(k, 9), S(k, 11), box=(20, 24, 32, 200))
        c.L("EIXO CURVO: UMA BANANA", 1450, 500, 64, YEL, t, S(k, 12), 1e9)
    elif t < S(k, 15):
        img[:] = (40, 44, 54)
        rect(img, 60, 30, 324, 200, (226, 220, 206), (150, 140, 120))
        for i in range(4): rect(img, 70 + i * 14, 170 - i * 14, 84 + i * 14, 200 - i * 14, (180, 172, 156), (120, 110, 100))
        for i in range(6): rect(img, 300 - i * 14, 170 - i * 9, 314 - i * 14, 200 - i * 9, (180, 172, 156), (120, 110, 100))
        c.L("NORTE: 4 DEGRAUS", 450, 120, 60, WHITE, t, S(k, 14), 1e9); c.L("SUL: 6 DEGRAUS", 1470, 120, 60, YEL, t, S(k, 14) + 1, 1e9)
    elif t < S(k, 18):
        th = lerp(4, 9, seg(t, S(k, 16), S(k, 16) + 3))
        tower_scene(img, c, t, 8, th, lerp(6, 9, seg(t, S(k, 16), S(k, 17))), ((300, GY), dict(eyes="wide")), curve=-1.6)
        c.L("1370 · ~200 ANOS DEPOIS", 960, 180, 80, YEL, t, S(k, 15), S(k, 16))
        c.L("O PESO FINAL EMPURROU", 960, 180, 70, RED, t, S(k, 16), S(k, 17))
        if t >= S(k, 17):
            a = math.radians(th); topx = 192 + 125 * math.sin(a); topy = GY - 125 * math.cos(a)
            line(img, [(topx, topy), (topx, GY - 2)], (240, 240, 240), 1); rect(img, int(topx) - 2, GY - 6, int(topx) + 2, GY - 2, (90, 90, 90))
            c.L("1817 · ~5° (FIO DE PRUMO)", 960, 180, 76, YEL, t, S(k, 17), 1e9)
    else:
        if t < S(k, 22):
            carpet(img, t, S(k, 18), S(k, 20) + 1.5)
            c.L("BLOCOS EM CARPETE FOFO", 960, 140, 60, WHITE, t, S(k, 19), 1e9, box=(20, 24, 32, 200))
            c.L("INSTABILIDADE POR INCLINAÇÃO", 960, 950, 64, YEL, t, S(k, 21), 1e9, box=(20, 24, 32, 220))
        else:
            tower_scene(img, c, t, 8, 9, 9, None, curve=-1.6)
            line(img, [(150, 18), (300, 18)], RED, 2)
            c.L("ALTURA CRÍTICA", 1450, 60, 70, RED, t, S(k, 22), 1e9)

def sc_c5(img, c, t):
    k = "c5"
    base_th = 9
    if t < S(k, 2):
        tower_scene(img, c, t, 8, base_th, 9, ((300, GY), dict(pose="shrug")), curve=-1.6)
        c.L("TODA VEZ QUE TENTARAM AJUDAR...", 960, 180, 64, WHITE, t, S(k, 0), 1e9)
        c.L("PIOROU", 960, 330, 130, RED, t, S(k, 1) + 1, 1e9)
    elif t < S(k, 5):
        th = base_th + (1.2 if t > S(k, 4) + 0.5 else 0) * seg(t, S(k, 4) + 0.5, S(k, 4) + 1)
        tower_scene(img, c, t, 8, th, 9, None, curve=-1.6)
        w = seg(t, S(k, 2) + 1, S(k, 2) + 3)
        rect(img, 150, GY + 2, 150 + int(84 * w), GY + 10, (90, 70, 50))
        if t >= S(k, 3):
            f = seg(t, S(k, 4), S(k, 4) + 1.5)
            rect(img, 200, GY + 10 - int(8 * f), 234, GY + 10, (70, 140, 230))
        c.L("1838 · CALÇADA ESCAVADA", 960, 180, 80, YEL, t, S(k, 2), 1e9)
        c.L("ABAIXO DO LENÇOL (SUL)", 1450, 760, 50, LBLUE, t, S(k, 3), 1e9)
        c.L("+ MAIS DE ¼°", 1450, 380, 90, RED, t, S(k, 4) + 1, 1e9)
        c.shake = 1 if S(k, 4) + 0.5 < t < S(k, 4) + 1.1 else 0
    elif t < S(k, 7):
        tower_scene(img, c, t, 8, base_th + 1.2, 9, None, curve=-1.6)
        for i, x in enumerate((170, 190, 214)):
            yy = GY + 6 + int(4 * math.sin(t * 6 + i))
            rect(img, x, yy - 18, x + 4, yy, (200, 200, 210), (60, 60, 60))
        c.L("1934 · INJEÇÃO DE CALDA", 960, 180, 80, YEL, t, S(k, 5), 1e9)
        c.L("+1 cm PRO SUL", 1450, 380, 90, RED, t, S(k, 6), 1e9)
    elif t < S(k, 9):
        tower_scene(img, c, t, 8, base_th + 1.3, 9, None, curve=-1.6)
        for x in (40, 340):
            rect(img, x - 6, GY - 14, x + 6, GY, (90, 120, 160), (30, 30, 30)); line(img, [(x, GY), (x, LH)], (120, 120, 130), 2)
        c.L("ANOS 70 · BOMBEAMENTO", 960, 180, 80, YEL, t, S(k, 7), 1e9)
        c.L("+1,2 cm", 1450, 380, 90, RED, t, S(k, 7) + 2, 1e9)
        c.L("NO LIMITE: QUALQUER COISA MEXIA COM ELA", 960, 950, 50, WHITE, t, S(k, 8), 1e9, box=(20, 24, 32, 220))
    elif t < S(k, 10):
        img[:] = (24, 28, 36)
        pts = [(40 + i * 30, 180 - (i * 1.0) ** 1.6 * 2.2) for i in range(11)]
        line(img, [(40, 190), (360, 190)], (120, 120, 130), 1); line(img, [(40, 30), (40, 190)], (120, 120, 130), 1)
        n = int(seg(t, S(k, 9), S(k, 9) + 3) * 10) + 1
        line(img, pts[:n + 1], RED, 3)
        c.L("VELOCIDADE DA INCLINAÇÃO", 960, 120, 56, WHITE, t, S(k, 9), 1e9)
        c.L("1930: 1×", 420, 850, 60, WHITE, t, S(k, 9), 1e9); c.L("1990: 2×", 1600, 300, 80, RED, t, S(k, 9) + 2.5, 1e9)
    elif t < S(k, 11):
        sky(img); ground_strip(img, GY)
        th = 0 if t < S(k, 10) + 3 else min(90, ((t - S(k, 10) - 3) / 1.2) ** 2 * 90)
        if th < 90:
            pil = Image.fromarray(img).convert("RGBA"); lay = Image.new("RGBA", (40, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.rectangle([4, 10, 36, 140], fill=(170, 90, 70, 255), outline=(80, 40, 30, 255))
            for yy in range(14, 140, 8): d.line([4, yy, 36, yy], fill=(140, 70, 55, 255))
            d.polygon([(4, 10), (20, 0), (36, 10)], fill=(120, 60, 50, 255))
            lay = lay.rotate(-th, resample=Image.NEAREST, center=(20, 140))
            pil.alpha_composite(lay, (172, GY - 139)); img[:] = np.array(pil.convert("RGB"))
        dust(img, t, S(k, 10) + 3.6, 220, GY - 4, n=80, seed=5, spread=80, dur=2.5)
        c.L("PAVIA, 1989", 960, 180, 100, WHITE, t, S(k, 10) + 1, 1e9)
        c.L("(ilustração)", 960, 290, 30, WHITE, t, S(k, 10) + 1, 1e9, w=700)
        c.shake = 1 if S(k, 10) + 3.6 < t < S(k, 10) + 4.4 else 0
    else:
        tower_scene(img, c, t, 8, 11, 9, ((300, GY), dict(eyes="sweat")), curve=-1.6)
        for x in range(120, 270, 12):
            rect(img, x, GY - 12, x + 6, GY - 10, RED); rect(img, x + 6, GY - 12, x + 12, GY - 10, WHITE)
        c.L("1990 · FECHADA AO PÚBLICO", 960, 180, 80, RED, t, S(k, 11), 1e9)
        c.L("5,5°", 560, 520, 120, YEL, t, S(k, 12), 1e9); c.L("~4,5 m FORA DO PRUMO", 1450, 520, 56, YEL, t, S(k, 12) + 2, 1e9)

def sc_c6(img, c, t):
    k = "c6"
    TH = 11
    if t < S(k, 3):
        img[:] = (40, 44, 54)
        rect(img, 90, 140, 294, 150, (150, 110, 70))
        for i, (x, hc) in enumerate([(120, (245, 130, 30)), (170, (240, 240, 240)), (220, (60, 140, 230)), (270, (60, 190, 90))]):
            bloquinho(img, x, 140, helmet=hc)
        c.L("COMISSÃO INTERNACIONAL", 960, 140, 70, YEL, t, S(k, 0), 1e9)
        for i, s in enumerate(["SEM ESCORAS VISÍVEIS", "SEM MUDAR O MONUMENTO", "TUDO REVERSÍVEL"]):
            c.L("✕ " if False else s, 960, 300 + i * 90, 50, WHITE, t, S(k, 2) + i * 1.8, 1e9, box=(20, 24, 32, 220))
    elif t < S(k, 12):
        th = TH
        lead = 0
        if t >= S(k, 5): lead = seg(t, S(k, 5), S(k, 5) + 3) * 6
        if t >= S(k, 6): th = TH - 0.6 * seg(t, S(k, 6), S(k, 7) + 1)
        if t >= S(k, 9): th = TH - 0.6 + 1.0 * seg(t, S(k, 9), S(k, 10))
        if t >= S(k, 10): lead = 6 + 3 * seg(t, S(k, 10), S(k, 10) + 2); th = lerp(TH + 0.4, TH - 0.3, seg(t, S(k, 10), S(k, 11)))
        tower_scene(img, c, t, 8, th, 9, None, curve=-1.6)
        if t >= S(k, 4):
            for yy in (GY - 16, GY - 26, GY - 36):
                line(img, [(170, yy + 3), (216, yy - 1)], ORANGE, 2)
        if lead > 0:
            rect(img, 140, GY - 2, 176, GY + 2, (150, 150, 148), (60, 60, 60))
            for i in range(int(lead)):
                rect(img, 144, GY - 6 - i * 4, 172, GY - 3 - i * 4, (90, 90, 100), (40, 40, 50))
        c.L("1992 · CABOS DE AÇO", 960, 180, 80, YEL, t, S(k, 4), S(k, 5))
        c.L("1993 · 600 t DE CHUMBO (NORTE)", 960, 180, 76, YEL, t, S(k, 5), S(k, 8))
        c.L("1995 · TENTATIVA COM TIRANTES", 960, 180, 76, WHITE, t, S(k, 8), S(k, 10))
        c.L("900 t ÀS PRESSAS", 960, 180, 90, RED, t, S(k, 10), 1e9)
        c.L("“SETEMBRO NEGRO”", 960, 330, 80, RED, t, S(k, 11), 1e9)
        if S(k, 9) <= t < S(k, 11) and int(t * 4) % 2 == 0: c.flash = "red"
    elif t < S(k, 17):
        img[:] = (24, 28, 36)
        c.L("SUL AFUNDOU DEMAIS?", 960, 300, 90, WHITE, t, S(k, 13), 1e9)
        c.L("FAZ O NORTE DESCER", 960, 440, 110, YEL, t, S(k, 13) + 2, 1e9)
        c.L("TIRANDO TERRA DE BAIXO DELE", 960, 620, 64, WHITE, t, S(k, 15), 1e9)
        c.L("SUBESCAVAÇÃO", 960, 840, 140, GRN, t, S(k, 16), 1e9)
    elif t < S(k, 24):
        rot = 0
        section_scene(img, c, t, 8, 8.5 - rot, 10, 1, 0.6, 0.4, x=200)
        # tubes from north
        for i in range(3):
            y = 92 + i * 6
            L = int(70 * ease((t - S(k, 17) - i * 0.4) / 1.2))
            line(img, [(100, y - 20), (100 + L, y)], (30, 30, 30), 5); line(img, [(100, y - 20), (100 + L, y)], (230, 190, 60), 3)
            if L > 60:
                for j in range(0, L, 6):
                    xx = 100 + j; yy = y - 20 + 20 * j / L
                    if (j + int(t * 20)) % 12 < 6: img[int(yy) - 1:int(yy) + 1, xx:xx + 2] = (90, 60, 40)
        if t >= S(k, 20):
            for yy in range(78, 130, 4): rect(img, 182, yy, 183, yy + 2, YEL)
            poly(img, [(100, 76), (182, 76), (182, 130), (100, 130)], None, GRN)
            poly(img, [(183, 76), (300, 76), (300, 130), (183, 130)], None, RED)
        c.L("TUBOS INCLINADOS + BROCA EM ESPIRAL", 960, 140, 56, WHITE, t, S(k, 17), S(k, 18), box=(20, 24, 32, 220))
        c.L("MILÍMETRO POR MILÍMETRO", 960, 140, 64, YEL, t, S(k, 18), S(k, 20))
        c.L("LINHA CRÍTICA", 960, 140, 80, YEL, t, S(k, 20), 1e9)
        c.L("SEGURO", 620, 760, 56, GRN, t, S(k, 21), 1e9); c.L("INSTÁVEL", 1250, 760, 56, RED, t, S(k, 22), 1e9)
        if t >= S(k, 23):
            dim(img, 0.35)
            c.L("TESTE EM FUNDAÇÃO DE 7 m NA PRAÇA", 960, 420, 62, WHITE, t, S(k, 23), 1e9, box=(20, 24, 32, 230))
            c.L("CABOS DE SEGURANÇA NO 3º ANDAR", 960, 560, 62, WHITE, t, S(k, 23) + 4, 1e9, box=(20, 24, 32, 230))
    elif t < S(k, 28):
        prog = seg(t, S(k, 26), S(k, 28))
        th = TH - 0.3 - 2.5 * prog
        tower_scene(img, c, t, 8, th, 9, ((300, GY), dict(eyes="wide" if prog < 0.5 else "normal")), curve=-1.6)
        for yy in (GY - 46,):
            line(img, [(210, yy), (40, 40)], (60, 60, 60), 1)
        rect(img, 30, 30, 50, GY, None, (90, 90, 90))
        lit = 20 if t < S(k, 27) else int(lerp(20, 120, seg(t, S(k, 27), S(k, 27) + 3)))
        c.L("1999" if t < S(k, 27) else "2000", 960, 170, 100, YEL, t, S(k, 24), 1e9)
        c.L(f"{lit} LITROS/DIA", 1450, 360, 70, WHITE, t, S(k, 24), 1e9)
        c.L("41 FUROS", 1450, 470, 60, YEL, t, S(k, 27), 1e9)
        c.L("GIRANDO PRO NORTE", 420, 640, 56, GRN, t, S(k, 26), 1e9)
    else:
        th = TH - 2.8
        tower_scene(img, c, t, 8, th, 9, ((300, GY), dict(pose="thumb")), curve=-1.6)
        if S(k, 30) <= t < S(k, 31):
            x = int(lerp(-60, 420, seg(t, S(k, 30), S(k, 31))))
            for dx in (0, 70):
                rect(img, x + dx, GY - 16, x + dx + 40, GY - 4, (230, 200, 40), (60, 60, 60)); rect(img, x + dx + 40, GY - 14, x + dx + 54, GY - 4, (200, 60, 50), (60, 60, 60))
                poly(img, [(x + dx + 4, GY - 16), (x + dx + 36, GY - 16), (x + dx + 30, GY - 22), (x + dx + 10, GY - 22)], (120, 84, 52))
        c.L("2001", 960, 170, 100, YEL, t, S(k, 28), S(k, 31))
        c.L("-0,5°", 560, 420, 150, GRN, t, S(k, 29), S(k, 31)); c.L("~40 cm NO TOPO", 560, 580, 60, WHITE, t, S(k, 29) + 1.5, S(k, 31))
        c.L("~2 CAMINHÕES DE TERRA", 1400, 300, 56, WHITE, t, S(k, 30), S(k, 31))
        c.L("DE VOLTA À INCLINAÇÃO DE ~1810", 960, 170, 64, YEL, t, S(k, 32), 1e9)
        c.L("+4 cm SOZINHA ATÉ 2018", 560, 460, 70, GRN, t, S(k, 34), 1e9, box=(20, 24, 32, 220))
        c.L("200+ ANOS ESTÁVEL", 560, 600, 70, YEL, t, S(k, 35), 1e9, box=(20, 24, 32, 220))

def building(img, x, yb, floors, theta, w=26, col=(220, 214, 200), win=(70, 100, 130), fh=6):
    h = floors * fh + 4
    pil = Image.fromarray(img).convert("RGBA")
    lay = Image.new("RGBA", (w + 4, h + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([2, 0, w + 1, h], fill=col + (255,), outline=(90, 90, 90, 255))
    for f in range(floors):
        for wx in range(5, w - 2, 6): d.rectangle([wx, 3 + f * fh, wx + 2, 3 + f * fh + 2], fill=win + (255,))
    big = Image.new("RGBA", (w + 4 + 2 * h, 2 * h + 2), (0, 0, 0, 0)); big.paste(lay, (h, 0))
    big = big.rotate(-theta, resample=Image.NEAREST, center=(h + w / 2 + 2, h))
    pil.alpha_composite(big, (int(x - h - w / 2 - 2), int(yb - h)))
    img[:] = np.array(pil.convert("RGB"))

def sc_c7(img, c, t):
    k = "c7"
    if t < S(k, 2) or S(k, 20) <= t:
        sky(img)
        img[150:, :] = SANDB[150:, :]
        img[176:, :] = SEA[176:, :]
        for x in range(0, LW, 3):
            if (x + int(t * 10)) % 9 < 3: img[176, x:x + 3] = (240, 240, 250)
        tilts = [-2, 1.5, -1, 2.5, 0.5, -2.5, 1.8]
        for i, th in enumerate(tilts):
            extra = 0.4 * math.sin(t * 0.5 + i) if t >= S(k, 20) else 0
            building(img, 30 + i * 54, 150, 14 + (i % 3) * 2, th + extra)
        c.L("SANTOS · SP", 960, 140, 100, YEL, t, S(k, 0), 1e9)
        c.L("QUASE 100 PRÉDIOS INCLINADOS", 960, 260, 60, WHITE, t, S(k, 1) + 1, 1e9, box=(20, 24, 32, 200))
        c.L("AINDA RECALCANDO", 960, 380, 60, RED, t, S(k, 21), 1e9) if t >= S(k, 20) else None
    elif t < S(k, 9):
        img[:] = 0; sky(img, y1=60)
        img[60:63, :] = SANDB[60:63, :]
        img[63:100, :] = SANDB[63:100, :]
        clay_t = 100
        img[clay_t:190, :] = CLAY[clay_t:190, :]
        img[190:, :] = SAND[190:, :]
        building(img, 192, 60, 14, 0)
        rect(img, 176, 60, 208, 66, (130, 126, 120), (50, 50, 50))
        if t >= S(k, 7):
            a = seg(t, S(k, 7), S(k, 7) + 2)
            ellipse(img, (192 - 30 - 30 * a, 66, 192 + 30 + 30 * a, 66 + 40 + 80 * a), (230, 80, 60), None, alpha=0.25)
        c.L("AREIA ~10–12 m", 360, 400, 44, (90, 60, 20), t, S(k, 2), 1e9, w=800, anchor="lm")
        c.L("ARGILA MARINHA MOLE", 360, 700, 50, LBLUE, t, S(k, 3), 1e9, w=800, anchor="lm")
        c.L("FIRME SÓ AOS ~55 m", 360, 950, 44, WHITE, t, S(k, 4), 1e9, w=800, anchor="lm")
        c.L("SAPATA A 1,5–2 m", 1500, 300, 56, YEL, t, S(k, 5), 1e9)
        c.L("IGUALZINHO A PISA", 1500, 560, 64, RED, t, S(k, 8), 1e9)
    elif t < S(k, 12):
        img[:] = 0; sky(img, y1=60)
        img[60:100, :] = SANDB[60:100, :]; img[100:190, :] = CLAY[100:190, :]; img[190:, :] = SAND[190:, :]
        lean = 3 * seg(t, S(k, 11), S(k, 11) + 3)
        building(img, 160, 60 + lean * 0.5, 14, lean); building(img, 224, 60 + lean * 0.5, 14, -lean)
        a = seg(t, S(k, 10), S(k, 10) + 2)
        ellipse(img, (100, 66, 220, 66 + 110 * a), (230, 80, 60), None, alpha=0.22)
        ellipse(img, (164, 66, 284, 66 + 110 * a), (230, 80, 60), None, alpha=0.22)
        c.L("CARGAS SE SOMAM NA ARGILA", 960, 140, 64, YEL, t, S(k, 11), 1e9, box=(20, 24, 32, 200))
    elif t < S(k, 15):
        sky(img); img[150:, :] = SANDB[150:, :]
        th = lerp(0, 2.2 * 2, seg(t, S(k, 12), S(k, 14) + 1))
        building(img, 192, 150, 17, th, w=34)
        c.L("NÚNCIO MALZONI", 960, 140, 90, YEL, t, S(k, 12), 1e9)
        c.L("1967 · 17 ANDARES · SAPATAS RASAS", 960, 250, 50, WHITE, t, S(k, 13), 1e9)
        c.L("2,2°", 1500, 520, 140, RED, t, S(k, 14), 1e9)
        c.L("(inclinação exagerada no desenho)", 1500, 650, 30, WHITE, t, S(k, 14), 1e9, w=700)
    elif t < S(k, 17):
        img[:] = (24, 28, 36)
        c.L("PISA: O LADO ALTO DESCEU", 520, 420, 56, WHITE, t, S(k, 15), 1e9)
        c.L("SANTOS: O LADO BAIXO SUBIU", 1400, 420, 56, YEL, t, S(k, 16), 1e9)
        arrow(img, 104, 110, 104, 140, BLUE, 3); arrow(img, 280, 140, 280, 110, YEL, 3)
    else:
        img[:] = 0; sky(img, y1=60)
        img[60:100, :] = SANDB[60:100, :]; img[100:190, :] = CLAY[100:190, :]; img[190:, :] = SAND[190:, :]
        th = 4.4 * (1 - seg(t, S(k, 19) + 1, S(k, 19) + 7))
        building(img, 192, 60, 17, th, w=34)
        p = seg(t, S(k, 17), S(k, 17) + 3)
        for x in (162, 222):
            rect(img, x - 2, 64, x + 2, 64 + int(150 * p), (150, 150, 148), (60, 60, 60))
        c.L("16 ESTACAS ATÉ 55 m", 1450, 260, 60, YEL, t, S(k, 17), 1e9)
        if t >= S(k, 18):
            rect(img, 152, 56, 232, 62, (170, 170, 168), (60, 60, 60))
            c.L("VIGAS DE TRANSIÇÃO", 1450, 360, 56, WHITE, t, S(k, 18), 1e9)
        if t >= S(k, 19):
            for x in (158, 166, 218, 226):
                rect(img, x - 2, 62, x + 2, 66, RED)
            c.L("14 MACACOS HIDRÁULICOS", 1450, 460, 56, RED, t, S(k, 19), 1e9)
            c.L("DE VOLTA AO PRUMO", 960, 140, 80, GRN, t, S(k, 19) + 6, 1e9)

def card_bg(img, t): img[:] = (24, 28, 36)

def sc_c8(img, c, t):
    k = "c8"
    if t < S(k, 1):
        card_bg(img, t); c.L("O QUE ISSO MUDA NO SEU PROJETO", 960, 520, 90, YEL, t, 0.2, 1e9)
    elif t < S(k, 6):
        sky(img); ground_strip(img, GY)
        bloquinho(img, 150, GY, pose="point", scale=2)
        bloquinho(img, 240, GY, pose="thumb", scale=2, helmet=(240, 240, 240), vest=(60, 140, 230), flip=True)
        rect(img, 270, GY - 30, 274, GY, (160, 120, 80))
        c.L("MINHA OPINIÃO", 960, 120, 70, YEL, t, S(k, 1), 1e9)
        c.L("CHAME UM ENGENHEIRO GEOTÉCNICO COM EXPERIÊNCIA", 960, 220, 50, WHITE, t, S(k, 2), 1e9, box=(20, 24, 32, 220))
        c.L("CALCULISTA: A ESTRUTURA", 560, 950, 46, YEL, t, S(k, 3), 1e9, box=(20, 24, 32, 220))
        c.L("GEOTÉCNICO: O SOLO", 1400, 950, 46, LBLUE, t, S(k, 4), 1e9, box=(20, 24, 32, 220))
    else:
        cards = [("1 · SONDAGEM", S(k, 7)), ("2 · DIFERENCIAL", S(k, 11)), ("3 · TEMPO", S(k, 17)), ("4 · MONITORAR", S(k, 22))]
        cur = 0
        for i, (_, t0) in enumerate(cards):
            if t >= t0: cur = i
        sky(img); ground_strip(img, GY)
        if cur == 0:
            rect(img, 180, 60, 184, GY, (90, 90, 100)); poly(img, [(170, 60), (194, 60), (182, 48)], (200, 80, 60))
            yy = int(GY + 30 * seg(t, S(k, 7), S(k, 9)))
            rect(img, 181, GY, 183, yy, (40, 40, 40))
            hy = 70 + int(10 * abs(math.sin(t * 4)))
            rect(img, 176, hy, 188, hy + 8, (140, 140, 150))
            if t >= S(k, 10):
                rect(img, 270, 110, 330, 146, (200, 200, 210), (60, 60, 60)); rect(img, 285, 92, 315, 110, (120, 120, 130), (60, 60, 60))
                c.L("ENSAIO DE ADENSAMENTO", 1500, 300, 50, WHITE, t, S(k, 10), 1e9)
            c.L("SEM SONDAGEM, TODO CÁLCULO É CHUTE", 960, 950, 50, WHITE, t, S(k, 9), 1e9, box=(20, 24, 32, 220))
        elif cur == 1:
            building(img, 140, GY, 10, 2.5); building(img, 250, GY, 6, 0)
            rect(img, 200, GY, 226, GY + 20, (60, 40, 30))
            c.L("O VILÃO É O DIFERENCIAL", 960, 300, 70, RED, t, S(k, 13), 1e9)
            c.L("NBR 6122: VERIFICAR RECALQUES", 960, 950, 56, YEL, t, S(k, 16), 1e9, box=(20, 24, 32, 220))
        elif cur == 2:
            if t < S(k, 21):
                poly(img, [(100, GY), (140, GY - 26), (244, GY - 26), (284, GY)], (150, 110, 70))
                for x in range(130, 260, 14): line(img, [(x, GY), (x, LH)], (60, 160, 255), 1)
                rr = random.Random(int(t * 10))
                for i in range(8):
                    x = 130 + rr.randint(0, 9) * 14; y = LH - int((t * 40 + i * 20) % 60)
                    img[y:y + 2, x - 1:x + 1] = (120, 200, 255)
                c.L("PRÉ-CARREGAMENTO + DRENOS VERTICAIS", 960, 300, 56, LBLUE, t, S(k, 20), 1e9)
            else:
                building(img, 192, GY, 12, 0, w=40)
                for x in (176, 192, 208): rect(img, x - 1, GY, x + 1, LH - 4, (150, 150, 148))
                img[LH - 8:, :] = SAND[LH - 8:, :]
                c.L("OU FUNDAÇÃO ATÉ O SOLO FIRME", 960, 300, 60, YEL, t, S(k, 21), 1e9)
            c.L("O TEMPO É VARIÁVEL DE PROJETO", 960, 160, 64, WHITE, t, S(k, 18), 1e9, box=(20, 24, 32, 220))
        else:
            building(img, 192, GY, 12, 0, w=40)
            for x in (172, 212): rect(img, x - 1, GY - 6, x + 1, GY - 4, YEL)
            rect(img, 60, GY - 22, 62, GY, (60, 60, 60)); rect(img, 54, GY - 28, 70, GY - 22, (240, 200, 40), (40, 40, 40))
            line(img, [(70, GY - 25), (172, GY - 5)], (255, 80, 80), 1)
            c.L("CONTROLE DE RECALQUES", 960, 300, 64, GRN, t, S(k, 25), 1e9)
            c.L("AVISA ANTES DA TRINCA", 960, 950, 56, WHITE, t, S(k, 25) + 2, 1e9, box=(20, 24, 32, 220))
        for i, (s, t0) in enumerate(cards):
            if t >= t0:
                c.L(s, 250 + i * 470, 70, 40, YEL if i == cur else (160, 160, 160), t, t0, 1e9, box=(20, 24, 32, 230))

def sc_c9(img, c, t):
    k = "c9"
    tower_scene(img, c, t, 8, 8, 9, ((300, GY), dict(pose="thumb" if t > S(k, 1) else "push")), curve=-1.6, sunset=0.7)
    c.L("SEUS PROJETOS NÃO PODEM DEPENDER DE SORTE", 960, 160, 56, YEL, t, S(k, 1), 1e9, box=(20, 24, 32, 200))
    c.L("SUA CIDADE TEM PRÉDIO TORTO? COMENTA AQUI", 960, 950, 48, WHITE, t, S(k, 2), 1e9, box=(20, 24, 32, 220))

SCENES = {k: globals()["sc_" + k] for k in CH}
