from scenes_base import *

TITLES = {"c1": "1 · O SEGREDO DO BURJ KHALIFA", "c2": "2 · COMO CONFUNDIR O VENTO", "c3": "3 · A BOLA DE 660 t",
          "c4": "4 · O PRÉDIO DE 1 km", "c5": "5 · A OBRA QUE MEXEU NA TERRA", "c6": "6 · DOIS MITOS",
          "c7": "7 · ITAIPU, O RECORDE DO PARANÁ", "c8": "8 · O QUE ISSO MUDA NO SEU PROJETO", "c9": ""}

SANDD = texmap((214, 186, 128), 10, 41)
SANDST = texmap((168, 146, 112), 10, 43)
CALC = texmap((140, 128, 108), 9, 42)
WATERT = texmap((46, 112, 176), 8, 44)
DIRT = texmap((150, 92, 60), 12, 45)      # terra roxa (PR)
GOLD = (222, 178, 60)
RUST = (186, 92, 40)


def L2(c, t, items):
    for it in items: c.L(*it[:3], **dict(it[3], t=t))


# ---------------- prédios ----------------
def burj(img, x, yb, h, w=44, sway=0.0):
    yb = int(yb); h = int(h); body = h * 0.78; n = 9
    for i in range(h):
        y = yb - 1 - i
        if y < 0 or y >= LH: continue
        off = sway * (i / max(h, 1)) ** 2
        if i < body:
            tier = int(i / body * n); ww = max(3, int(w * (1 - tier / n * 0.86)))
        else:
            ww = 2 if i < body + (h - body) * 0.6 else 1
        x0 = int(round(x - ww / 2 + off)); a = max(0, x0); b = min(LW, x0 + ww)
        if b <= a: continue
        row = GLASS[y % 400, np.arange(a, b) % 120].astype(np.int16) + 18
        if i % 5 == 4: row = row + 45
        img[y, a:b] = np.clip(row, 0, 255)
        mid = int(round(x + off)); img[y, max(0, mid - 1):min(LW, mid + 1)] = (200, 214, 230)
        img[y, a] = (30, 50, 80); img[y, b - 1] = (30, 50, 80)


def taipei(img, x, yb, h, w=30, sway=0.0, tint=(70, 150, 120)):
    yb = int(yb); h = int(h); pod = h * 0.18; segs = 8; seg_h = (h * 0.68) / segs
    for i in range(h):
        y = yb - 1 - i
        if y < 0 or y >= LH: continue
        off = sway * (i / max(h, 1)) ** 2
        if i < pod: ww = int(w * (0.9 - 0.25 * i / pod))
        elif i < pod + segs * seg_h:
            k = ((i - pod) % seg_h) / seg_h; ww = int(w * (0.62 + 0.3 * k))
        elif i < h * 0.92: ww = int(w * 0.32)
        else: ww = 2
        x0 = int(round(x - ww / 2 + off)); a = max(0, x0); b = min(LW, x0 + ww)
        if b <= a: continue
        row = GLASS[y % 400, np.arange(a, b) % 120].astype(np.float32) * 0.55 + np.array(tint) * 0.45
        if i % 4 == 3: row = row + 35
        img[y, a:b] = np.clip(row, 0, 255)
        img[y, a] = (20, 50, 40); img[y, b - 1] = (20, 50, 40)


def jeddah(img, x, yb, h, w=40, built=1.0, sway=0.0):
    yb = int(yb); h = int(h); top = int(h * built)
    for i in range(top):
        y = yb - 1 - i
        if y < 0 or y >= LH: continue
        k = i / max(h, 1); off = sway * k * k
        ww = max(1, int(w * (1 - k) ** 1.15))
        if 0.55 < k < 0.6: ww = max(1, ww - 4)
        x0 = int(round(x - ww / 2 + off)); a = max(0, x0); b = min(LW, x0 + ww)
        if b <= a: continue
        row = GLASS[y % 400, np.arange(a, b) % 120].astype(np.int16) + 40
        if i % 6 == 5: row = row + 40
        img[y, a:b] = np.clip(row, 0, 255)
        img[y, a] = (40, 60, 90); img[y, b - 1] = (40, 60, 90)
    if built < 1:
        yt = yb - top
        box(img, x - 1, yt - 26, x + 1, yt, (240, 190, 40)); box(img, x - 1, yt - 26, x + 22, yt - 24, (240, 190, 40))


def desert(img, gy=196, sunset=0.0, city=True):
    sky(img, sunset=sunset)
    if city:
        for x, hh, w in [(40, 30, 12), (56, 44, 10), (70, 26, 14), (270, 40, 12), (286, 54, 11), (300, 30, 14), (318, 46, 10), (340, 34, 13)]:
            bld(img, x, gy, hh, w)
    tex(img, SANDD, 0, gy, LW, LH)


def dubai_cut(img, gy=70, water=0.0, salt=0.0, t=0.0):
    sky(img, y1=gy)
    tex(img, SANDD, 0, gy, LW, gy + 34); tex(img, SANDST, 0, gy + 34, LW, gy + 86); tex(img, CALC, 0, gy + 86, LW, LH)
    if water > 0:
        wy = gy + 10
        for x in range(0, LW, 3):
            if (x // 3 + int(t * 6)) % 2 == 0: box(img, x, wy, x + 2, wy + 1, (90, 160, 240))
        r = random.Random(7)
        for i in range(int(140 * water)):
            xx = r.randint(0, LW - 3); yy = r.randint(wy + 3, LH - 3)
            box(img, xx, yy, xx + 2, yy + 1, (90, 160, 240))
        for i in range(int(90 * salt)):
            xx = r.randint(0, LW - 3); yy = r.randint(wy + 3, LH - 3)
            box(img, xx, yy, xx + 1, yy + 1, (250, 250, 250))


def raft_piles(img, gy, x0, x1, n, L, prog=1.0, thick=8, w=3, rust=0.0):
    tex(img, CONC, x0, gy, x1, gy + thick); box(img, x0, gy, x1, gy + 1, (90, 90, 92)); box(img, x0, gy + thick - 1, x1, gy + thick, (90, 90, 92))
    for i, x in enumerate(PXS(n, x0 + 4, x1 - 4 - w)):
        Lk = clamp(prog * n - i) if prog < 1 else 1.0
        if Lk > 0:
            box(img, x, gy + thick, x + w, gy + thick + L * Lk, PILE)
            if rust > 0:
                r = random.Random(i)
                for j in range(int(10 * rust)):
                    yy = gy + thick + r.randint(0, max(1, int(L * Lk) - 2)); box(img, x + r.randint(0, w - 1), yy, x + r.randint(1, w), yy + 1, RUST)


def friction(img, x, y0, y1, t, k=1.0, w=3):
    n = int(6 * k)
    for i in range(n):
        y = y0 + (y1 - y0) * (i + 0.5) / max(n, 1); ph = (t * 2 + i * 0.3) % 1
        for sx in (x - 6, x + w + 4):
            arrow(img, sx, y + 6 - 3 * ph, sx, y - 2 - 3 * ph, YEL, 1)


def ball(img, cx, cy, r, cables=None):
    if cables:
        for ax, ay in cables: line(img, [(ax, ay), (cx, cy)], (60, 60, 66), 1)
    ellipse(img, (cx - r, cy - r, cx + r, cy + r), GOLD, outline=(110, 80, 20))
    ellipse(img, (cx - r * 0.6, cy - r * 0.7, cx - r * 0.05, cy - r * 0.2), (250, 220, 120))
    for k in (-0.5, 0, 0.5): line(img, [(cx - r * 0.9, cy + r * k), (cx + r * 0.9, cy + r * k)], (180, 140, 40), 1)


def windlines(img, t, y0, y1, x0=0, x1=LW, n=26, speed=140, seed=5, col=(235, 240, 250), strong=1.0):
    r = random.Random(seed)
    for i in range(n):
        y = r.randint(y0, y1); ln = r.randint(8, 22); ph = r.uniform(0, 1)
        x = x0 + ((t * speed * strong * r.uniform(0.7, 1.3) + ph * (x1 - x0)) % (x1 - x0 + ln)) - ln
        box(img, x, y, x + ln, y + 1, col)


def vortices(img, t, x, ys, phase=0.0, alt=True, col=(220, 236, 255)):
    for j, y in enumerate(ys):
        for i in range(4):
            ph = ((t * 0.9 + i * 0.25 + (phase if not alt else 0) * j) % 1)
            side = (1 if (i + (j * phase if alt else 0)) % 2 else -1)
            cx = x + 8 + ph * 120; cy = y + side * 6 * (0.5 + ph)
            rr = 2 + 4 * ph
            pil = Image.fromarray(img); ImageDraw.Draw(pil).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col); img[:] = np.array(pil)


def globe(img, cx, cy, r, rot=0.0, night=0.25):
    yy, xx = np.mgrid[0:LH, 0:LW]
    dx = (xx - cx) / r; dy = (yy - cy) / r; d2 = dx * dx + dy * dy; m = d2 <= 1
    lon = np.arcsin(np.clip(dx / np.sqrt(np.maximum(1e-6, 1 - dy * dy)), -1, 1)) + rot
    lat = np.arcsin(np.clip(dy, -1, 1))
    land = (np.sin(lon * 3) * np.cos(lat * 4) + 0.5 * np.sin(lon * 7 + lat * 3)) > 0.35
    col = np.where(land[..., None], np.array((70, 150, 80)), np.array((40, 100, 190)))
    shade = np.clip(1 - night * (dx + 1) * 0.6, 0.4, 1)[..., None]
    img[m] = (col * shade)[m].astype(np.uint8)
    ell_band = m & (np.abs(dy) > 0.86)
    img[ell_band] = (235, 240, 245)


def damcut(img, x, gy, h, water=1.0, w0=10, w1=48, col=None):
    sky(img, y1=LH)
    tex(img, ROCK, 0, gy, LW, LH)
    wl = gy - int(h * 0.9 * water)
    if water > 0: tex(img, WATERT, 0, wl, x - w1 // 2, gy)
    tex(img, WATERT, x + w1 // 2, gy - 8, LW, gy)
    poly(img, [(x - w0 // 2, gy - h), (x + w0 // 2, gy - h), (x + w1 // 2, gy), (x - w1 // 2, gy)], col or (176, 174, 168), (90, 90, 92))
    for yy in range(gy - h + 6, gy, 6): line(img, [(x - w0 // 2 - (w1 - w0) / 2 * (yy - gy + h) / h, yy), (x + w0 // 2 + (w1 - w0) / 2 * (yy - gy + h) / h, yy)], (150, 148, 142), 1)


def damfront(img, gy=150, t=0.0, spill=True):
    sky(img); tex(img, SEDI, 0, 120, LW, LH)
    poly(img, [(0, 120), (60, 104), (330, 104), (384, 120)], (60, 120, 60))
    tex(img, CONC, 20, 92, 364, gy)
    for x in range(30, 360, 16): box(img, x, 96, x + 8, gy - 4, (160, 160, 156))
    box(img, 20, 90, 364, 93, (110, 110, 108))
    if spill:
        for x in range(270, 350, 3):
            y = 93 + ((t * 80 + x * 7) % (gy - 93)); box(img, x, y, x + 2, y + 4, (220, 236, 250))
    tex(img, WATERT, 0, gy, LW, LH)


def stadium(img, x, y, s=1):
    ellipse(img, (x, y, x + 9 * s, y + 6 * s), (230, 230, 226), outline=(120, 120, 120)); ellipse(img, (x + 2 * s, y + 1.5 * s, x + 7 * s, y + 4.5 * s), (70, 160, 70))


def skater(img, x, y, arms=0.0):
    box(img, x - 2, y - 22, x + 2, y - 8, (200, 60, 90)); ellipse(img, (x - 3, y - 29, x + 3, y - 23), (225, 180, 140))
    line(img, [(x - 1, y - 8), (x - 4, y)], (40, 40, 50), 2); line(img, [(x + 1, y - 8), (x + 4, y)], (40, 40, 50), 2)
    span = 4 + 14 * arms
    line(img, [(x - span, y - 18 + 4 * (1 - arms)), (x, y - 19)], (225, 180, 140), 2); line(img, [(x + span, y - 18 + 4 * (1 - arms)), (x, y - 19)], (225, 180, 140), 2)


def heights(img, t, t0, show=(1, 1, 1), gy=200):
    sky(img, sunset=0.3); tex(img, SANDD, 0, gy, LW, LH)
    k = seg(t, t0, t0 + 1.4)
    if show[1]: taipei(img, 80, gy, 86 * k, 26)
    if show[0]: burj(img, 190, gy, 141 * k, 34)
    if show[2]: jeddah(img, 300, gy, 170 * k, 40)


def mixer(img, x, y):
    box(img, x - 16, y - 10, x + 18, y, (60, 60, 66)); poly(img, [(x - 12, y - 10), (x - 6, y - 30), (x + 10, y - 30), (x + 14, y - 10)], (230, 120, 40), (90, 50, 20))
    box(img, x - 12, y - 2, x - 6, y + 4, (20, 20, 22)); box(img, x + 8, y - 2, x + 14, y + 4, (20, 20, 22))


def cracks(img, x0, y0, x1, y1, k, seed=2):
    r = random.Random(seed)
    for i in range(int(6 * k)):
        x = r.randint(x0, x1); y = y0; pts = [(x, y)]
        for j in range(5): x += r.randint(-4, 4); y += r.randint(3, 7); pts.append((x, y))
        line(img, pts, (40, 30, 26), 1)


# ======================= CENAS =======================
def sc_c0(img, c, t):
    k = "c0"
    if t < S(k, 2):
        h = lerp(40, 180, seg(t, 0, 2.2)); desert(img, sunset=0.15); burj(img, 192, 196, h, 46)
        bloquinho(img, 140, 196, eyes="wide", pose="point")
        c.cam = (192, lerp(70, 108, seg(t, 1.6, 4)), lerp(1.8, 1.0, seg(t, 1.6, 4)))
        c.L("828 m", 1500, 300, 160, YEL, t, 0.2, S(k, 2))
        c.L("O PRÉDIO MAIS ALTO DO MUNDO", 960, 120, 50, WHITE, t, S(k, 1), S(k, 2), w=800, box=DARK)
    elif t < S(k, 5):
        dubai_cut(img, 70, water=seg(t, S(k, 4) + 2.5, S(k, 4) + 3.5), salt=seg(t, S(k, 4) + 3, S(k, 4) + 4), t=t)
        burj(img, 192, 70, 70, 26); scale_note(c, t)
        if S(k, 3) <= t < S(k, 3) + 0.45: c.shake = 1
        c.L("E EMBAIXO?", 960, 130, 64, WHITE, t, S(k, 2), S(k, 3))
        c.L("NÃO ESTÁ NA ROCHA", 960, 130, 84, YEL, t, S(k, 3), S(k, 5))
        c.L("AREIA", 300, 470, 56, WHITE, t, S(k, 4), S(k, 5))
        c.L("ROCHA FRACA", 360, 780, 56, WHITE, t, S(k, 4) + 1.3, S(k, 5))
        c.L("ÁGUA MAIS SALGADA QUE O MAR", 1350, 640, 46, LBLUE, t, S(k, 4) + 2.6, S(k, 5), w=800, box=DARK)
    elif t < S(k, 6):
        dubai_cut(img, 70, 1, 1, t); scale_note(c, t)
        raft_piles(img, 70, 150, 234, 9, 70, prog=seg(t, S(k, 5), S(k, 5) + 1.2))
        burj(img, 192, 70, 70, 26)
        if t > S(k, 5) + 0.9:
            for x in (168, 216): friction(img, x, 80, 146, t)
        c.L("ATRITO", 960, 150, 120, YEL, t, S(k, 5) + 0.6, 1e9)
    elif t < S(k, 7):
        desert(img, sunset=0.4); burj(img, 192, 196, 180, 46); dim(img, 0.4)
        bloquinho(img, 120, 196, eyes="normal", pose="shrug", scale=2)
        c.L("A PEÇA ESCONDIDA", 1180, 420, 84, YEL, t, S(k, 6), 1e9)
        c.L("QUE SEGURA OS GIGANTES", 1180, 530, 50, WHITE, t, S(k, 6) + 1.2, 1e9)
    elif t < S(k, 8):
        q = (t - S(k, 7)) / max(0.1, E(k, 7) - S(k, 7)); p = min(3, int(q * 4))
        if p == 0:
            sky(img); panel(img, 120, 20, 264, 196); ball(img, 192, 110, 34, [(150, 22), (234, 22), (192, 22)])
            bloquinho(img, 250, 196, eyes="wide"); c.L("660 t", 1500, 420, 130, YEL, t, 0, 1e9)
            c.L("PENDURADA NO CÉU", 1500, 560, 44, WHITE, t, 0, 1e9)
        elif p == 1:
            desert(img); jeddah(img, 230, 196, 186, 44); burj(img, 130, 196, 150, 32); bloquinho(img, 290, 196, eyes="wide", pose="up")
            c.L("1 km", 420, 300, 140, YEL, t, 0, 1e9); c.L("SUBINDO AGORA", 420, 440, 44, WHITE, t, 0, 1e9)
        elif p == 2:
            blank_ = blank((6, 8, 20)); img[:] = blank_; globe(img, 192, 108, 80, rot=t * 0.8)
            c.L("A TERRA GIROU", 960, 120, 58, WHITE, t, 0, 1e9); c.L("MAIS DEVAGAR?", 960, 950, 70, YEL, t, 0, 1e9)
        else:
            damfront(img, t=t); bloquinho(img, 60, 150, pose="thumb")
            c.L("RECORDE MUNDIAL", 960, 120, 70, YEL, t, 0, 1e9); c.L("NO PARANÁ", 960, 220, 56, WHITE, t, 0, 1e9)
    else:
        housecut(img, 120); burj(img, 300, 120, 110, 30); scale_note(c, t)
        for x in (96, 132): friction(img, x, 130, 180, t, 0.7)
        bloquinho(img, 210, 120, pose="thumb")
        c.L("O MESMO PRINCÍPIO", 960, 140, 76, YEL, t, S(k, 8) + 1.2, 1e9)


def sc_c1(img, c, t):
    k = "c1"
    if t < S(k, 2):
        desert(img, sunset=0.25); burj(img, 192, 196, 180, 46)
        c.cam = (lerp(150, 200, seg(t, 0, 8)), 108, 1.0 + 0.1 * seg(t, 0, 8))
        c.L("DUBAI · EMIRADOS ÁRABES", 960, 110, 52, WHITE, t, 0.2, S(k, 2), box=DARK)
        c.L("INAUGURADO EM 2010", 1450, 470, 54, YEL, t, S(k, 1), S(k, 2))
    elif t < S(k, 5):
        dubai_cut(img, 46); rig(img, 160, 46, 130)
        d = seg(t, S(k, 2) + 0.5, S(k, 4)); auger(img, 166 + 8, 46, 46 + 160 * d, ph=t * 20)
        bloquinho(img, 250, 46, eyes="sweat" if t > S(k, 4) else "normal", pose="shrug" if t > S(k, 4) else "point")
        c.L("SONDAGEM", 960, 110, 56, WHITE, t, S(k, 2), S(k, 3), box=DARK)
        c.L("ATÉ 140 m", 1500, 620, 96, YEL, t, S(k, 3), S(k, 5))
        c.L("ROCHA FIRME? NADA", 1500, 760, 52, RED, t, S(k, 4), S(k, 5), w=900)
    elif t < S(k, 6):
        dubai_cut(img, 46); scale_note(c, t)
        c.L("AREIA", 960, 300, 56, WHITE, t, S(k, 5), 1e9)
        c.L("ARENITO FRACO", 960, 600, 56, WHITE, t, S(k, 5) + 2.0, 1e9)
        c.L("CALCISSILTITO: ROCHA MOLE", 960, 880, 56, YEL, t, S(k, 5) + 4.0, 1e9, box=DARK)
    elif t < S(k, 9):
        dubai_cut(img, 60); scale_note(c, t)
        raft_piles(img, 60, 120, 264, 11, 120, prog=seg(t, S(k, 8), S(k, 8) + 2.4) if t >= S(k, 8) else 0.0, thick=int(4 + 6 * seg(t, S(k, 7), S(k, 7) + 1)))
        burj(img, 192, 60, 58, 30)
        c.L("RADIER · 3,70 m", 1500, 260, 58, YEL, t, S(k, 7), 1e9, box=DARK)
        c.L("192 ESTACAS", 420, 260, 60, YEL, t, S(k, 7) + 3.5, 1e9, box=DARK)
        c.L("Ø 1,5 m", 1600, 650, 64, WHITE, t, S(k, 8) + 1.0, 1e9)
        c.L("47 m", 1600, 760, 90, YEL, t, S(k, 8) + 2.4, 1e9)
    elif t < S(k, 13):
        dubai_cut(img, 30); scale_note(c, t)
        box(img, 184, 30, 200, 210, PILE); tex(img, CONC, 150, 22, 234, 32)
        c.cam = (192, 112, 1.0)
        if S(k, 10) <= t < S(k, 11):
            arrow(img, 192, 200, 192, 186, RED, 2); c.L("PONTA?", 1250, 960, 64, RED, t, S(k, 10), S(k, 11))
            line(img, [(176, 192), (208, 208)], RED, 2); line(img, [(176, 208), (208, 192)], RED, 2)
        if t >= S(k, 11):
            friction(img, 184, 40, 200, t, 1.6, w=16)
            c.L("ATRITO LATERAL", 960, 160, 84, YEL, t, S(k, 11), 1e9)
        c.L("O PULO DO GATO", 960, 160, 72, WHITE, t, S(k, 9), S(k, 10))
        c.L("O SOLO APERTANDO A ESTACA", 960, 960, 46, WHITE, t, S(k, 12), 1e9, w=800, box=DARK)
        bloquinho(img, 250, 30, eyes="wide", pose="point")
    elif t < S(k, 14):
        img[:] = (20, 24, 32); n = int(192 * seg(t, S(k, 13), S(k, 13) + 2.5))
        for i in range(n):
            r_, cc = divmod(i, 24); x = 96 + cc * 8; y = 50 + r_ * 12; ellipse(img, (x, y, x + 5, y + 5), PILE)
        c.L("× 192", 960, 120, 100, YEL, t, S(k, 13), 1e9)
    elif t < S(k, 18):
        dubai_cut(img, 60, water=1.0, salt=seg(t, S(k, 15), S(k, 15) + 1.5), t=t); scale_note(c, t)
        raft_piles(img, 60, 120, 264, 11, 110, rust=seg(t, S(k, 16), S(k, 16) + 1.5) * (1 - seg(t, S(k, 17) + 3, S(k, 17) + 5)))
        burj(img, 192, 60, 58, 30)
        if t >= S(k, 17) + 3:
            box(img, 116, 70, 268, 71, (200, 210, 225))
            for x in range(116, 268, 6):
                if (x // 6 + int(t * 8)) % 3 == 0: box(img, x, 72, x + 3, 73, YEL)
        c.L("O 2º INIMIGO", 960, 140, 70, WHITE, t, S(k, 14), S(k, 15))
        c.L("MAIS CLORETO E SULFATO QUE O MAR", 960, 140, 50, LBLUE, t, S(k, 15), S(k, 17), w=800, box=DARK)
        c.L("CORRÓI O AÇO", 1500, 900, 56, RED, t, S(k, 16), S(k, 17) + 2)
        c.L("CONCRETO ESPECIAL", 960, 140, 56, YEL, t, S(k, 17), S(k, 17) + 3, box=DARK)
        c.L("PROTEÇÃO CATÓDICA · MALHA DE TITÂNIO", 960, 140, 44, YEL, t, S(k, 17) + 3, 1e9, w=800, box=DARK)
    else:
        desert(img, sunset=0.25); burj(img, 192, 196, 180, 46)
        z = seg(t, S(k, 18), S(k, 19) + 1); c.cam = (192, lerp(160, 40, z), lerp(1.4, 2.0, z))
        c.L("CHÃO RESOLVIDO", 960, 940, 60, GRN, t, S(k, 18), S(k, 19), box=DARK)
        c.L("E LÁ EM CIMA?", 960, 940, 66, YEL, t, S(k, 19), 1e9, box=DARK)


def sc_c2(img, c, t):
    k = "c2"
    if t < S(k, 4):
        desert(img, sunset=0.2)
        sw = 0 if t < S(k, 3) else 7 * math.sin(t * 5) * seg(t, S(k, 3), S(k, 3) + 3)
        burj(img, 192, 196, 180, 46, sway=sw)
        windlines(img, t, 20, 190, 0, 170, strong=1.2)
        if t >= S(k, 2): vortices(img, t, 214, [60, 110, 150])
        c.L("O VENTO", 960, 120, 90, WHITE, t, 0, S(k, 2))
        c.L("REDEMOINHOS ALTERNADOS", 960, 120, 56, WHITE, t, S(k, 2), S(k, 3), box=DARK)
        c.L("RESSONÂNCIA", 960, 120, 80, RED, t, S(k, 3), 1e9)
    elif t < S(k, 5):
        img[:] = (24, 28, 36); panel(img, 60, 40, 324, 176); windlines(img, t, 60, 160, 64, 320, 30, 200)
        burj(img, 200, 168, 110, 26); bloquinho(img, 96, 196, pose="point", eyes="normal")
        c.L("+ DE 40 ENSAIOS", 960, 110, 70, YEL, t, S(k, 4), 1e9)
        c.L("TÚNEL DE VENTO · CANADÁ", 960, 960, 46, WHITE, t, S(k, 4) + 1, 1e9, box=DARK)
    elif t < S(k, 7):
        img[:] = (24, 28, 36); cx, cy = 192, 112; a = t * 0.6
        for lvl in range(5):
            sc = 1 - lvl * 0.17; rot = a + lvl * 0.18
            pts = []
            for j in range(3):
                ang = rot + j * 2 * math.pi / 3
                for dw in (-0.22, 0.22):
                    pts.append((cx + 70 * sc * math.cos(ang + dw * 0.4) + 12 * sc * math.cos(ang + math.pi / 2) * dw * 4,
                                cy + 70 * sc * math.sin(ang + dw * 0.4) + 12 * sc * math.sin(ang + math.pi / 2) * dw * 4))
                    pts.append((cx + 14 * sc * math.cos(ang + dw * 3), cy + 14 * sc * math.sin(ang + dw * 3)))
            col = tuple(int(v) for v in (80 + lvl * 30, 130 + lvl * 20, 190))
            for j in range(3):
                ang = rot + j * 2 * math.pi / 3
                line(img, [(cx, cy), (cx + 70 * sc * math.cos(ang), cy + 70 * sc * math.sin(ang))], col, max(2, int(16 * sc)))
        c.L("PLANTA EM Y", 960, 110, 70, YEL, t, S(k, 5), 1e9)
        c.L("DEGRAUS EM ESPIRAL", 960, 970, 50, WHITE, t, S(k, 6), 1e9, box=DARK)
    elif t < S(k, 10):
        desert(img, sunset=0.2); burj(img, 192, 196, 180, 46)
        windlines(img, t, 20, 190, 0, 170, strong=1.0)
        for j, (y, ph) in enumerate([(60, 0.0), (100, 0.33), (140, 0.66), (175, 0.15)]):
            vortices(img, t + ph * 3, 200 - (j * 3), [y], alt=False, col=[(255, 200, 80), (120, 220, 255), (255, 120, 160), (160, 255, 140)][j])
        c.L("CADA ALTURA, UM DESENHO", 960, 120, 56, WHITE, t, S(k, 7), S(k, 9), box=DARK)
        c.L("CONFUNDIR O VENTO", 960, 120, 90, YEL, t, S(k, 9), 1e9)
    elif t < S(k, 14):
        desert(img, sunset=0.2); burj(img, 192, 196, 180, 46, sway=2.2 * math.sin(t * 2.2)); windlines(img, t, 20, 190, 0, 170)
        bloquinho(img, 120, 196, eyes="wide" if t < S(k, 11) else "normal", pose="shrug" if t < S(k, 11) else "thumb")
        c.L("E BALANÇA?", 1450, 400, 76, WHITE, t, S(k, 10), S(k, 11))
        c.L("SIM", 1450, 400, 110, YEL, t, S(k, 11), 1e9)
        c.L("TODO ARRANHA-CÉU BALANÇA", 1450, 540, 44, WHITE, t, S(k, 12), 1e9, w=800)
        c.L("O PROJETO CONTROLA QUANTO", 960, 960, 50, GRN, t, S(k, 13), 1e9, box=DARK)
    elif t < S(k, 17):
        sky(img, night=0.35); tex(img, SANDD, 0, 196, LW, LH); burj(img, 192, 196, 150, 40)
        box(img, 214, 196 - 150 * 0.78, 216, 196, (240, 120, 40)); mixer(img, 236, 196)
        q = seg(t, S(k, 15) + 1, S(k, 15) + 9); yb = 196 - 117 * q
        box(img, 212, yb - 4, 218, yb, (190, 190, 186))
        c.cam = (200, lerp(150, 90, q), lerp(1.3, 1.0, q))
        c.L("08/11/2007", 520, 170, 60, WHITE, t, S(k, 15), 1e9, box=DARK)
        c.L("%d m" % int(601 * q), 1500, 420, 120, YEL, t, S(k, 15) + 1, 1e9)
        c.L("RECORDE MUNDIAL DE BOMBEAMENTO", 960, 970, 50, YEL, t, S(k, 16), 1e9, box=DARK)
        c.L("MAIS UM RECORDE ESCONDIDO", 960, 970, 50, WHITE, t, S(k, 14), S(k, 15), box=DARK)
    else:
        sky(img, night=0.5); tex(img, SANDD, 0, 196, LW, LH); taipei(img, 192, 196, 170, 44); dim(img, 0.55)
        ball(img, 192, 60, 10 + 2 * math.sin(t * 3))
        c.L("UMA BOLA GIGANTE?", 960, 940, 70, YEL, t, S(k, 17) + 1.5, 1e9, box=DARK)


def sc_c3(img, c, t):
    k = "c3"
    if t < S(k, 2):
        sky(img, night=0.1 + 0.4 * seg(t, S(k, 1) + 2, S(k, 1) + 4)); tex(img, GRASS, 0, 196, LW, LH)
        for x, hh, w in [(40, 50, 14), (60, 40, 12), (270, 46, 12), (300, 60, 14), (330, 36, 12)]: bld(img, x, 196, hh, w)
        taipei(img, 192, 196, 176, 44)
        if t > S(k, 1) + 2: windlines(img, t, 10, 190, strong=1.6)
        c.L("TAIPEI, TAIWAN", 960, 110, 56, WHITE, t, 0.2, S(k, 1), box=DARK)
        c.L("TAIPEI 101 · 508 m", 960, 110, 60, YEL, t, S(k, 1), 1e9, box=DARK)
        c.L("TUFÃO + TERREMOTO", 1450, 600, 52, RED, t, S(k, 1) + 2.5, 1e9)
    elif t < S(k, 5):
        img[:] = (26, 30, 38)
        for y in range(10, 210, 22): box(img, 110, y, 274, y + 2, (90, 96, 108))
        box(img, 108, 0, 112, LH, (70, 150, 120)); box(img, 272, 0, 276, LH, (70, 150, 120))
        ball(img, 192, 120, 36, [(140, 12), (244, 12), (170, 12), (214, 12)])
        bloquinho(img, 250, 186, eyes="wide")
        c.L("ANDAR 92", 360, 90, 40, WHITE, t, S(k, 2), 1e9); c.L("ANDAR 87", 360, 900, 40, WHITE, t, S(k, 2), 1e9)
        c.L("660 t", 1600, 420, 120, YEL, t, S(k, 3), 1e9); c.L("Ø 5,5 m", 1600, 560, 60, WHITE, t, S(k, 3) + 1.5, 1e9)
        c.L("AMORTECEDOR DE MASSA SINTONIZADA", 960, 970, 46, YEL, t, S(k, 4), 1e9, w=800, box=DARK)
    elif t < S(k, 8):
        img[:] = (26, 30, 38); s_ = 14 * math.sin(t * 2.4)
        for y in range(10, 210, 22): box(img, 110 + s_, y, 274 + s_, y + 2, (90, 96, 108))
        box(img, 108 + s_, 0, 112 + s_, LH, (70, 150, 120)); box(img, 272 + s_, 0, 276 + s_, LH, (70, 150, 120))
        bx = 192 - 10 * math.sin(t * 2.4)
        ball(img, bx, 120, 36, [(140 + s_, 12), (244 + s_, 12), (192 + s_, 12)])
        if t >= S(k, 6):
            for sx in (-1, 1):
                x0 = bx + sx * 36; x1 = 192 + s_ + sx * 76
                line(img, [(x0, 130), (x1, 130)], (200, 200, 210), 3); box(img, min(x0, x1) + abs(x1 - x0) * 0.4, 127, min(x0, x1) + abs(x1 - x0) * 0.6, 133, RED)
        arrow(img, 192 + s_ * 2, 30, 192 + s_ * 4, 30, LBLUE, 2) if abs(s_) > 4 else None
        c.L("O PRÉDIO VAI PRA UM LADO", 960, 110, 48, WHITE, t, S(k, 5), S(k, 5) + 2.5, box=DARK)
        c.L("A BOLA PUXA PRO OUTRO", 960, 110, 48, YEL, t, S(k, 5) + 2.5, S(k, 6), box=DARK)
        c.L("MOVIMENTO VIRA CALOR", 960, 110, 56, ORANGE, t, S(k, 6), S(k, 7), box=DARK)
        c.L("ATÉ 40% MENOS BALANÇO", 960, 110, 60, GRN, t, S(k, 7), 1e9, box=DARK)
    elif t < S(k, 12):
        img[:] = (26, 30, 38); s_ = 6 * math.sin(t * 3)
        for y in range(10, 210, 22): box(img, 110 + s_, y, 274 + s_, y + 2, (90, 96, 108))
        sw = (30 if t >= S(k, 9) else 12) * math.sin(t * 2.6)
        ball(img, 192 + sw, 120, 36, [(150, 12), (234, 12), (192, 12)])
        windlines(img, t, 0, 216, strong=2.4, n=40, col=(150, 170, 200))
        box(img, 132, 200, 252, 202, (200, 200, 200)); box(img, 162, 196, 163, 206, YEL); box(img, 222, 196, 223, 206, YEL)
        box(img, 132, 196, 133, 206, RED); box(img, 252, 196, 253, 206, RED)
        c.L("08/08/2015 · TUFÃO SOUDELOR", 960, 110, 48, WHITE, t, S(k, 8), 1e9, box=DARK)
        c.L("1 m", 960, 920, 60, YEL, t, S(k, 9), 1e9)
        c.L("LIMITE 1,5 m", 1560, 920, 44, RED, t, S(k, 10), 1e9)
        c.L("FUNCIONOU", 960, 520, 110, GRN, t, S(k, 11), 1e9)
    else:
        heights(img, t, S(k, 12), show=(0, 1, 1))
        c.L("500 m", 400, 560, 70, WHITE, t, S(k, 12), 1e9); c.L("1.000 m?", 1500, 150, 80, YEL, t, S(k, 12) + 1.2, 1e9)


def sc_c4(img, c, t):
    k = "c4"
    if t < S(k, 2):
        sky(img, sunset=0.2); tex(img, SANDD, 0, 196, LW, LH); tex(img, SEA, 0, 200, 90, LH)
        jeddah(img, 210, 196, lerp(60, 192, seg(t, 0, 3)), 46); bloquinho(img, 290, 196, eyes="wide", pose="up")
        c.cam = (200, lerp(70, 108, seg(t, 2, 6)), lerp(1.8, 1.0, seg(t, 2, 6)))
        c.L("JIDÁ, ARÁBIA SAUDITA", 960, 110, 52, WHITE, t, 0.2, S(k, 1), box=DARK)
        c.L("+ DE 1 km", 1500, 420, 110, YEL, t, S(k, 1) + 1, 1e9)
        c.L("O PRIMEIRO DA HISTÓRIA", 1500, 540, 44, WHITE, t, S(k, 1) + 2, 1e9)
    elif t < S(k, 4):
        sky(img, sunset=0.1); tex(img, SANDD, 0, 196, LW, LH)
        a0 = S(k, 2); y_ = [(a0, "2013 · COMEÇOU", WHITE), (a0 + 2.3, "2018 · PAROU", RED), (a0 + 4.6, "2025 · VOLTOU", GRN), (S(k, 3), "2026 · +100 ANDARES · +400 m", YEL)]
        b = 0.25 if t < a0 + 2.3 else (0.3 if t < a0 + 4.6 else (0.33 if t < S(k, 3) else lerp(0.33, 0.43, seg(t, S(k, 3), S(k, 3) + 2))))
        jeddah(img, 192, 196, 190, 46, built=b)
        for i, (t0, s, col) in enumerate(y_):
            t1 = y_[i + 1][0] if i + 1 < len(y_) else 1e9
            c.L(s, 960, 120, 56, col, t, t0, t1, w=900, box=DARK)
    elif t < S(k, 7):
        dubai_cut(img, 30); scale_note(c, t); jeddah(img, 192, 30, 30, 30)
        raft_piles(img, 30, 110, 274, 13, 170, prog=seg(t, S(k, 5), S(k, 5) + 3), thick=int(4 + 8 * seg(t, S(k, 6), S(k, 6) + 1)), w=4)
        c.L("270 ESTACAS", 420, 300, 64, YEL, t, S(k, 5), 1e9, box=DARK)
        c.L("ATÉ Ø 1,8 m", 1520, 300, 56, WHITE, t, S(k, 5) + 2, 1e9, box=DARK)
        c.L("ATÉ 105 m", 1520, 820, 90, YEL, t, S(k, 5) + 3.6, 1e9)
        c.L("RADIER DE 5 m", 960, 110, 56, WHITE, t, S(k, 6), 1e9, box=DARK)
    elif t < S(k, 10):
        dubai_cut(img, 20); scale_note(c, t)
        tex(img, CONC, 100, 20, 160, 26); box(img, 128, 26, 133, 26 + 80, PILE)
        tex(img, CONC, 224, 20, 284, 28); box(img, 251, 28, 257, 28 + 178, PILE)
        bloquinho(img, 192, 20, pose="point", eyes="wide")
        c.L("BURJ · 47 m", 650, 680, 54, WHITE, t, S(k, 8), 1e9, box=DARK)
        c.L("JEDDAH · 105 m", 1560, 1000, 54, YEL, t, S(k, 9), 1e9, box=DARK)
        c.L("REPARA NA DIFERENÇA", 960, 160, 60, WHITE, t, S(k, 7), S(k, 9))
        c.L("MAIS QUE O DOBRO", 960, 160, 76, YEL, t, S(k, 9), 1e9)
    elif t < S(k, 12):
        sky(img); tex(img, SANDD, 0, 150, LW, LH); jeddah(img, 192, 150, 140, 36)
        tex(img, CONC, 150, 150, 234, 156)
        arrow(img, 150, 20, 150, 90, RED, 3); windlines(img, t, 20, 120, 0, 170, strong=1.6)
        arrow(img, 60, 60, 120, 60, LBLUE, 3)
        if t >= S(k, 11):
            for x in (160, 192, 224): arrow(img, x, 158, x, 200, YEL, 2)
        c.L("PESO", 520, 260, 60, RED, t, S(k, 10), 1e9); c.L("VENTO", 300, 420, 60, LBLUE, t, S(k, 10) + 1.4, 1e9)
        c.L("TUDO DESCE PRA FUNDAÇÃO", 960, 960, 54, YEL, t, S(k, 11), 1e9, box=DARK)
    else:
        sky(img); tex(img, ROCK, 0, 150, LW, LH); lvl = seg(t, S(k, 12), S(k, 13) + 0.4)
        tex(img, WATERT, 0, int(150 - 100 * lvl), LW, 150)
        c.L("O PESO QUE IMPORTA?", 960, 160, 64, WHITE, t, S(k, 12), S(k, 13))
        c.L("É A ÁGUA", 960, 520, 120, LBLUE, t, S(k, 13), 1e9)


def sc_c5(img, c, t):
    k = "c5"
    if t < S(k, 4):
        damcut(img, 200, 196, 110, water=seg(t, S(k, 3), S(k, 3) + 2.5) if t >= S(k, 3) else 0.0, w0=16, w1=96)
        bloquinho(img, 300, 188, eyes="wide", pose="point")
        c.L("RIO YANGTZÉ, CHINA", 960, 110, 52, WHITE, t, 0.2, S(k, 1), box=DARK)
        c.L("TRÊS GARGANTAS", 960, 110, 64, YEL, t, S(k, 1), S(k, 2), box=DARK)
        c.L("22.400 MW", 1500, 420, 90, YEL, t, S(k, 1) + 2.5, S(k, 2))
        c.L("28 MILHÕES DE m³ DE CONCRETO", 960, 110, 50, WHITE, t, S(k, 2), S(k, 3), w=800, box=DARK)
        c.L("40 BILHÕES DE m³ DE ÁGUA", 700, 500, 54, LBLUE, t, S(k, 3), 1e9, w=800)
    elif t < S(k, 7):
        img[:] = (6, 8, 20); globe(img, 150, 108, 84, rot=t * (0.6 if t < S(k, 6) else 0.6))
        if t >= S(k, 5): ellipse(img, (170, 70, 182, 82), (250, 80, 60), alpha=0.6 + 0.4 * math.sin(t * 6))
        c.L("BENJAMIN FONG CHAO · NASA", 960, 100, 46, WHITE, t, S(k, 4), S(k, 5), w=800, box=DARK)
        c.L("MASSA REDISTRIBUÍDA", 1450, 520, 52, YEL, t, S(k, 5), S(k, 6))
        if t >= S(k, 6):
            skater(img, 300, 170, arms=seg(t, S(k, 6) + 0.5, S(k, 6) + 1.5))
            c.L("BRAÇOS ABERTOS = GIRO MAIS LENTO", 960, 980, 44, YEL, t, S(k, 6), 1e9, w=800, box=DARK)
    elif t < S(k, 11):
        img[:] = (6, 8, 20); globe(img, 192, 108, 70, rot=t * 0.3)
        c.L("O DIA FICOU MAIS LONGO", 960, 120, 60, WHITE, t, S(k, 7), 1e9)
        c.L("QUANTO?", 960, 950, 60, WHITE, t, S(k, 9), S(k, 10))
        c.L("+0,06 MICROSSEGUNDO", 960, 950, 84, YEL, t, S(k, 10), 1e9)
    else:
        img[:] = (6, 8, 20); globe(img, 192, 300, 200, rot=t * 0.1)
        bloquinho(img, 192, 104, eyes="normal", pose="shrug")
        c.L("A CHINA NÃO PAROU A TERRA", 960, 160, 60, WHITE, t, S(k, 11), S(k, 12))
        c.L("MAS MEXEU NELA", 960, 160, 70, YEL, t, S(k, 12), S(k, 13))
        c.L("VISTO LÁ DE CIMA...", 960, 160, 60, WHITE, t, S(k, 13), 1e9)


def sc_c6(img, c, t):
    k = "c6"
    if t < S(k, 3):
        z = seg(t, 0, S(k, 2) + 3)
        img[:] = (100, 120, 80); r = random.Random(3)
        tex(img, SEDI, 0, 0, LW, LH); tex(img, GRASS, 0, 120, LW, LH)
        pts = [(0, 140)]; x = 0; y = 140
        while x < LW: x += 12; y += r.randint(-8, 8); y = max(60, min(200, y)); pts.append((x, y))
        line(img, pts, (150, 140, 120), 1)
        c.cam = (192, 108, lerp(1.0, 4.0, 1 - z) if False else lerp(1.0, 1.0, z))
        dim(img, 0.9)
        c.L("MITO", 960, 160, 110, RED, t, 0.2, 1e9)
        c.L("A MURALHA SE VÊ DO ESPAÇO?", 960, 960, 50, WHITE, t, 0.4, S(k, 2), w=800, box=DARK)
        c.L("ESTREITA + COR DO TERRENO", 960, 960, 50, YEL, t, S(k, 2), 1e9, w=800, box=DARK)
    elif t < S(k, 7):
        img[:] = (6, 8, 20); globe(img, 140, 140, 110, rot=t * 0.2)
        box(img, 280, 50, 300, 62, (220, 220, 226)); box(img, 300, 54, 318, 58, (80, 140, 220)); box(img, 262, 54, 280, 58, (80, 140, 220))
        if t >= S(k, 6): ellipse(img, (330, 10, 370, 50), (200, 200, 190))
        c.L("YANG LIWEI · 2003", 1450, 200, 52, WHITE, t, S(k, 3), 1e9, box=DARK)
        c.L("\"NÃO VI\"", 1450, 380, 76, YEL, t, S(k, 3) + 3, 1e9)
        c.L("NASA: EM GERAL, NÃO DÁ", 960, 980, 50, WHITE, t, S(k, 4), 1e9, w=800, box=DARK)
        c.L("DA LUA? NEM PENSAR", 1500, 300 + 400, 54, RED, t, S(k, 6), 1e9)
    elif t < S(k, 10):
        img[:] = (28, 30, 38); panel(img, 100, 40, 284, 190); tex(img, CONC, 120, 70, 264, 180)
        if t >= S(k, 9): heat(img, seg(t, S(k, 9), S(k, 9) + 2), 0, 120, 264, 70, 180)
        if t < S(k, 9):
            line(img, [(150, 90), (234, 160)], RED, 3); line(img, [(150, 160), (234, 90)], RED, 3)
        c.L("OUTRO MITO", 960, 120, 70, RED, t, S(k, 7), S(k, 8))
        c.L("\"O CONCRETO SECA\"", 960, 120, 64, WHITE, t, S(k, 8), S(k, 9))
        c.L("ELE REAGE COM A ÁGUA", 960, 120, 60, YEL, t, S(k, 9), 1e9, box=DARK)
        c.L("E ESQUENTA", 960, 980, 70, ORANGE, t, S(k, 9) + 2.5, 1e9)
    elif t < S(k, 11):
        sky(img); tex(img, ROCK, 0, 0, 110, LH); tex(img, ROCK, 274, 0, LW, LH)
        q = seg(t, S(k, 10) + 2, S(k, 10) + 6)
        for i, x in enumerate(range(110, 274, 14)):
            hh = 40 + (i * 37) % 60
            tex(img, CONC, x, 196 - hh, x + 13, 196)
        heat(img, 1 - q * 0.5, 0, 110, 274, 60, 196)
        tex(img, WATERT, 0, 196, LW, LH)
        c.L("REPRESA HOOVER · EUA", 960, 110, 52, WHITE, t, S(k, 10), 1e9, box=DARK)
        c.L("UM BLOCO SÓ?", 960, 520, 64, WHITE, t, S(k, 10) + 2, S(k, 10) + 5)
        c.L("125 ANOS PRA ESFRIAR", 960, 950, 70, YEL, t, S(k, 10) + 5, 1e9, box=DARK)
    else:
        damfront(img, t=t); dim(img, 0.6)
        bloquinho(img, 192, 196, pose="up", eyes="wide", scale=2)
        c.L("E AQUI NO BRASIL...", 960, 140, 76, YEL, t, S(k, 11) + 1, 1e9)


def sc_c7(img, c, t):
    k = "c7"
    if t < S(k, 2):
        damfront(img, t=t); c.cam = (lerp(140, 230, seg(t, 0, 6)), 110, 1.15)
        c.L("RIO PARANÁ · FOZ DO IGUAÇU (PR)", 960, 980, 50, WHITE, t, 0.2, 1e9, w=800, box=DARK)
        c.L("ITAIPU", 960, 140, 120, YEL, t, S(k, 1) - 0.2, 1e9)
    elif t < S(k, 4):
        if t < S(k, 3):
            damcut(img, 150, 200, 170, 1.0, 12, 60)
            for i in range(65):
                y = 200 - (i + 1) * 170 / 65; box(img, 250, y, 290, y + 2, (170 + (i % 2) * 20, 176, 186))
            c.L("196 m", 960, 120, 90, YEL, t, S(k, 2), 1e9)
            c.L("= PRÉDIO DE 65 ANDARES", 1500, 980, 44, WHITE, t, S(k, 2) + 2, 1e9, w=800, box=DARK)
        else:
            img[:] = (24, 28, 36); q = seg(t, S(k, 3), S(k, 3) + 3)
            tex(img, CONC, 20, 100, 20 + 344 * q, 116)
            c.L("7.919 m DE BARRAGEM", 960, 300, 76, YEL, t, S(k, 3), 1e9)
    elif t < S(k, 5):
        img[:] = (24, 28, 36); n = int(210 * seg(t, S(k, 4), S(k, 4) + 5))
        for i in range(n):
            r_, cc = divmod(i, 21); stadium(img, 22 + cc * 16.5, 30 + r_ * 16)
        c.L("12,7 MILHÕES DE m³", 960, 70, 54, WHITE, t, S(k, 4), 1e9, box=DARK)
        c.L("= 210 MARACANÃS", 960, 1000, 66, YEL, t, S(k, 4) + 2.5, 1e9, box=DARK)
    elif t < S(k, 9):
        img[:] = (28, 30, 38); blockbg(img, 1.0, piles=False)
        hot = seg(t, S(k, 6), S(k, 6) + 1.5); cold = seg(t, S(k, 8) + 0.5, S(k, 8) + 3)
        heat(img, hot * (1 - 0.8 * cold), cold * 0.3)
        if t >= S(k, 7) + 2: cracks(img, 90, 66, 300, 120, seg(t, S(k, 7) + 2, S(k, 7) + 4) * (1 - cold))
        if t >= S(k, 8): icecubes(img, t, S(k, 8), 90, 300, 0, 60, 30)
        c.L("UM DETALHE QUE POUCA GENTE CONHECE", 960, 110, 44, WHITE, t, S(k, 5), S(k, 6), w=800, box=DARK)
        c.L("CIMENTO + ÁGUA = CALOR", 960, 110, 60, ORANGE, t, S(k, 6), S(k, 7), box=DARK)
        c.L("MIOLO QUENTE x SUPERFÍCIE FRIA", 960, 110, 50, ORANGE, t, S(k, 7), S(k, 7) + 3.5, w=800, box=DARK)
        c.L("TRINCA", 1500, 520, 80, RED, t, S(k, 7) + 3.5, S(k, 8))
        c.L("CONCRETO COM GELO", 960, 110, 64, LBLUE, t, S(k, 8), 1e9, box=DARK)
    elif t < S(k, 11):
        img[:] = (24, 28, 36)
        q = seg(t, S(k, 9), S(k, 9) + 1.5)
        box(img, 70, 70, 70 + 260 * q, 92, (200, 70, 60)); box(img, 70, 120, 70 + 162 * q, 142, (70, 170, 90))
        c.L("TRÊS GARGANTAS · 22.400 MW", 960, 260, 40, WHITE, t, S(k, 9), 1e9, w=800)
        c.L("ITAIPU · 14.000 MW", 960, 510, 40, WHITE, t, S(k, 9), 1e9, w=800)
        c.L("2016: 103 MILHÕES DE MWh", 960, 800, 60, YEL, t, S(k, 10) + 1, 1e9, box=DARK)
        c.L("RECORDE MUNDIAL", 960, 940, 76, YEL, t, S(k, 10) + 3.5, 1e9)
    else:
        damfront(img, t=t); bloquinho(img, 192, 150, pose="up" if t < S(k, 12) else "point", eyes="normal", scale=1)
        c.L("O PARANÁ NO TOPO DO MUNDO", 960, 960, 56, YEL, t, S(k, 11), S(k, 12), w=800, box=DARK)
        c.L("E O SEU PROJETO?", 960, 960, 66, WHITE, t, S(k, 12), 1e9, box=DARK)


def sc_c8(img, c, t):
    k = "c8"
    if t < S(k, 2):
        sky(img, y1=110); tex(img, DIRT, 0, 110, LW, LH); box(img, 0, 110, LW, 112, (86, 170, 60))
        house(img, 150, 110, 70, 34)
        for x in (160, 210): box(img, x, 112, x + 4, 190, PILE)
        bloquinho(img, 260, 110, pose="thumb")
        c.L("ENG. EVANNDRO RESENDE", 960, 110, 56, YEL, t, 0.2, 1e9, box=DARK)
        c.L("ESTRUTURAS E FUNDAÇÕES · PR", 960, 210, 40, WHITE, t, 1.0, S(k, 1), w=800)
        c.L("ALTO PADRÃO · SOBRADO · ATÉ 3 PAVIMENTOS", 960, 210, 40, WHITE, t, S(k, 1), 1e9, w=800)
        c.L("QUASE TUDO EM ESTACA", 960, 980, 50, WHITE, t, 4.0, 1e9, box=DARK)
    elif t < S(k, 4):
        sky(img, y1=60); tex(img, DIRT, 0, 60, 192, LH); tex(img, CALC, 192, 60, LW, LH); box(img, 191, 0, 193, LH, (20, 20, 24))
        house(img, 60, 60, 60, 30); box(img, 88, 62, 94, 180, PILE)
        burj(img, 288, 60, 58, 26); tex(img, CONC, 250, 60, 326, 66); box(img, 285, 66, 293, 200, PILE)
        if t >= S(k, 3):
            friction(img, 88, 70, 175, t, 1.0, w=6); friction(img, 285, 72, 196, t, 1.0, w=8)
            arrow(img, 91, 196, 91, 184, YEL, 2); arrow(img, 289, 212, 289, 202, YEL, 2)
        c.L("O MESMO RACIOCÍNIO", 960, 960, 56, YEL, t, S(k, 2), S(k, 3), box=DARK)
        c.L("PONTA + ATRITO LATERAL", 960, 960, 60, YEL, t, S(k, 3), 1e9, box=DARK)
    elif t < S(k, 8):
        sky(img, y1=40); tex(img, TOPS, 0, 40, LW, 90); tex(img, SILT, 0, 90, LW, 150); tex(img, CLAY, 0, 150, LW, LH)
        tripod(img, 120, 40); box(img, 119, 40, 121, 40 + 160 * seg(t, S(k, 4), S(k, 4) + 4), (70, 70, 76))
        ns = [3, 5, 7, 10, 14, 19, 26]
        for i, n_ in enumerate(ns):
            if t >= S(k, 4) + 0.6 * i: c.L("N = %d" % n_, 860, 290 + i * 110, 40, WHITE, t, 0, 1e9, w=800)
        if t >= S(k, 5):
            line(img, [(150, 168), (380, 168)], RED, 1)
            c.L("PROFUNDIDADE POSSÍVEL", 1500, 800, 44, RED, t, S(k, 5), S(k, 7), w=800)
        c.L("MÉTODO DE TEIXEIRA · NSPT", 960, 100, 54, YEL, t, S(k, 4), S(k, 6), box=DARK)
        c.L("Nº DE ESTACAS = CARGA ÷ CAPACIDADE", 960, 100, 46, YEL, t, S(k, 6), S(k, 7), w=800, box=DARK)
        c.L("QUEM LIMITA É O SOLO", 960, 100, 64, YEL, t, S(k, 7), 1e9, box=DARK)
    else:
        sky(img, y1=110); tex(img, DIRT, 0, 110, LW, LH); box(img, 0, 110, LW, 112, (86, 170, 60)); house(img, 150, 110, 70, 34)
        if t >= S(k, 10): tripod(img, 80, 110)
        bloquinho(img, 280, 110, pose="point" if t < S(k, 12) else "thumb", eyes="normal")
        c.L("A LIÇÃO SERVE PRA UMA CASA", 960, 960, 54, WHITE, t, S(k, 8), S(k, 9), w=800, box=DARK)
        c.L("SEM SONDAGEM = CHUTE", 960, 960, 64, RED, t, S(k, 9), S(k, 10), box=DARK)
        c.L("SONDAGEM SPT SEMPRE", 960, 960, 64, GRN, t, S(k, 10), S(k, 11), box=DARK)
        c.L("SOLO DIFÍCIL? GEOTÉCNICO COM EXPERIÊNCIA", 960, 960, 46, YEL, t, S(k, 11), S(k, 12), w=800, box=DARK)
        c.L("A PARTE QUE NINGUÉM VÊ", 960, 960, 64, YEL, t, S(k, 12), 1e9, box=DARK)


def sc_c9(img, c, t):
    k = "c9"; end = DUR(k) + 0.4
    if t < S(k, 5):
        heights(img, t, -5)
        if t >= S(k, 2): ball(img, 80, 140, 6)
        c.L("O QUE SEGURA UM GIGANTE?", 960, 110, 60, WHITE, t, 0, S(k, 1), box=DARK)
        c.L("ATRITO + FORMATO", 950, 300, 40, YEL, t, S(k, 1), 1e9, box=DARK)
        c.L("BOLA DE 660 t", 400, 560, 40, YEL, t, S(k, 2), 1e9, box=DARK)
        c.L("ESTACAS DE 105 m", 1500, 150, 40, YEL, t, S(k, 3), 1e9, box=DARK)
        c.L("ITAIPU: CONCRETO GELADO", 960, 1000, 44, LBLUE, t, S(k, 4), 1e9, box=DARK)
    elif t < S(k, 7):
        img[:] = (20, 24, 32)
        c.L("NÃO É FORÇA BRUTA", 960, 420, 90, WHITE, t, S(k, 5), 1e9)
        c.L("CHÃO · VENTO · MATERIAL", 960, 600, 70, YEL, t, S(k, 6), 1e9)
    elif t < end:
        heights(img, t, -5); dim(img, 0.6); bloquinho(img, 120, 200, pose="thumb", scale=2)
        c.L("SE INSCREVE NO CANAL", 1150, 380, 76, YEL, t, S(k, 7), 1e9)
        c.L("QUAL OBRA VOCÊ QUER VER?", 1150, 500, 46, WHITE, t, S(k, 7) + 2, 1e9, w=800)
        c.L("VÍDEO DO SENNA TOWER", 1150, 640, 46, LBLUE, t, S(k, 8), 1e9, w=800)
    else:
        heights(img, t, -5); dim(img, 0.32)
        c.L("ASSISTA TAMBÉM", 560, 170, 56, WHITE, t, end, 1e9)
        c.L("INSCREVA-SE", 1440, 170, 56, YEL, t, end, 1e9)
        c.L("ENG. EVANNDRO RESENDE · INOVALAB", 960, 1010, 30, WHITE, t, end, 1e9, w=800)


SCENES = {"c0": sc_c0, "c1": sc_c1, "c2": sc_c2, "c3": sc_c3, "c4": sc_c4, "c5": sc_c5, "c6": sc_c6, "c7": sc_c7, "c8": sc_c8, "c9": sc_c9}
