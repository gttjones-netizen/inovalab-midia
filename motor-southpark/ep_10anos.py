import sys, os
sys.path.insert(0, '/home/claude/serie')
from eps import *

TITLE = '10 ANOS DE ENGENHARIA'; SUB = 'O QUE A FACULDADE NÃO CONTA'
THUMB = ['NOTA?', 'NINGUÉM', 'PERGUNTOU']
CTA_WHO = 'PRO AMIGO QUE TÁ SURTANDO COM NOTA'
KEYS_Y = ['NOTA', 'DIPLOMA', 'CLIENTE', 'CONTA', 'SOLUÇÃO', 'HUMANA', 'AUTÔNOMO', 'ZERO', 'PROVA', 'OUVIR', 'EXPLICAR',
          'CUMPRIR', 'COMBINADO', 'RESOLVE', 'PROBLEMA', 'UNIVERSIDADE', '1', '2', '3', '4', '10', 'FACULDADE', 'PESA', 'PERGUNTA']
REV = (5, 'ZERO', '0', 'PERGUNTAS SOBRE NOTA', YEL)
TAIL = 0.6
EXTRA = {11: 1.1}
WHO = {'N': 'BLQ', 'VAL': 'VAL', 'CID': 'CID'}
NUMMAP = {(0, 'Dez'): '10', (1, 'quatro'): '4', (2, 'Um:'): '1:', (4, 'Dois:'): '2:', (6, 'Três:'): '3:', (8, 'Quatro:'): '4:'}
ITEM_OF = {2: 0, 3: 0, 4: 1, 5: 1, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3}
ITEMS = ['NOTA', 'DIPLOMA', 'A CONTA', 'GENTE']

def timeline():
    lines = EPS[1]['lines']; t = 0.05; S = []; E = []; items = []
    for i in range(len(lines)):
        k = KEYS[(1, i)]; d = CL[k]['dur']
        t += EXTRA.get(i, 0)
        S.append(t); E.append(t + d); items.append((k, t)); t += d + GAP
    total = E[-1] + 0.05 + TAIL
    return S, E, items, total

def word_env(k, nf):
    e = np.zeros(nf)
    for w in CL[k]['words']:
        for f in range(int(w['s'] * FPS), int(w['e'] * FPS) + 1):
            if f < nf: e[f] = .55 + .45 * abs(math.sin(f * 1.7))
    return e

def wt(c, li, prefix):
    k = KEYS[(1, li)]
    for w in CL[k]['words']:
        if re.sub(r'[^A-ZÀ-Ü]', '', w['w'].upper()).startswith(prefix): return c.S[li] + w['s']
    return c.S[li] + .5

def setup(style, dur):
    S, E, items, total = timeline()
    nf = int((total + TH / FPS) * FPS) + 1
    envs = {k: np.zeros(nf) for k in ['BLQ', 'VAL', 'CID']}
    for li, (k, t0) in enumerate(items):
        sp = WHO[k.split('_')[0]]
        n = int(CL[k]['dur'] * FPS) + 2
        wav = f'/home/claude/serie/clips/{k}.wav'
        e = envelope(wav, n) if os.path.exists(wav) else word_env(k, n)
        f0 = int((t0 + TH / FPS) * FPS)
        for i, v in enumerate(e):
            if f0 + i < nf: envs[sp][f0 + i] = v
    for k in envs:
        mx = np.percentile(envs[k][envs[k] > 0], 90) if (envs[k] > 0).any() else 1
        envs[k] = np.clip(envs[k] / (mx + 1e-9), 0, 1)
    words = []
    for li, (k, t0) in enumerate(items):
        for w in CL[k]['words']:
            ww = NUMMAP.get((li, w['w']), w['w'])
            words.append(dict(w=ww, s=t0 + w['s'], e=t0 + w['e']))
    c = Ctx(); c.S, c.E, c.total, c.nf = S, E, total, nf
    c.blocks = build_blocks(words); c.envs = envs; c.tarja = (style, dur)
    c.rt = wt(c, REV[0], REV[1])
    c.tick = [wt(c, 10, 'OUVIR'), wt(c, 10, 'EXPLICAR'), wt(c, 10, 'CUMPRIR')]
    c.stamp6 = wt(c, 6, 'OBRIGA'); c.sol6 = wt(c, 6, 'ELE')
    c.ctat = E[10] + .05
    c.res = wt(c, 10, 'COMBINADO') + .3
    n = len(S)
    ev = [(0.0, 'boing'), (1.05, 'thud'), (0.02, {'A': 'whoosh', 'B': 'blip', 'C': 'thud', 'D': 'whoosh', 'E': 'thud', 'F': 'stamp', 'G': 'vhs'}[style])]
    for i in range(1, n): ev.append((S[i] - .18, 'whoosh'))
    ev += [(S[1] + .1 + .15 * i, 'blip') for i in range(4)]
    ev += [(S[2] + .3 + .25 * i, 'blip') for i in range(5)]
    ev += [(c.rt - .75, 'riser'), (c.rt, 'pop')]
    ev += [(c.stamp6, 'stamp'), (c.sol6 + .1, 'pop')]
    ev += [(x, 'blip') for x in c.tick] + [(c.res, 'stamp'), (c.res + .05, 'sting'), (c.ctat, 'pop')]
    ev += [(S[11] - .1, 'boing'), (total - TAIL - .02, 'whoosh')]
    c.ev = ev
    return c

def current(c, t):
    if t >= c.total - TAIL: return 'tail'
    li = 0
    for i in range(len(c.S)):
        if t >= c.S[i] - .12: li = i
    return li

# ---------------- props ----------------
def boletim(d, x, y, s=1.0, ang=0, big=True):
    w, h = 170 * s, 220 * s
    pts = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]
    poly(d, rot(pts, ang, x, y), (252, 250, 240), max(3, int(6 * s)))
    if s > .35:
        L = Image.new('RGBA', (int(w) + 4, int(h) + 4), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        g.text((w / 2, h * .16), 'BOLETIM', font=F(900, max(8, int(26 * s))), fill=OUT, anchor='mm')
        for i in range(3): g.line([(w * .12, h * (.3 + i * .1)), (w * .88, h * (.3 + i * .1))], fill=(150, 150, 160), width=max(1, int(4 * s)))
        g.text((w / 2, h * .72), '10', font=F(900, max(10, int(92 * s))), fill=RED, anchor='mm')
        return L, (x, y), ang
    return None

def paste_rot(img, L, center, ang):
    if L is None: return
    R = L.rotate(-ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(R, (int(center[0] - R.width / 2), int(center[1] - R.height / 2)))

def desk(d, img, t, k_fixed):
    # table x 300..820, top y 1010, legs to 1240; wobble around right leg
    wob = 3.2 * math.sin(t * 15) * (1 - k_fixed)
    pv = (800, 1240)
    poly(d, rot([(300, 1000), (820, 1000), (820, 1040), (300, 1040)], wob, *pv), (150, 95, 55))
    for lx in (330, 780):
        poly(d, rot([(lx, 1040), (lx + 26, 1040), (lx + 26, 1205), (lx, 1205)], wob, *pv), (125, 75, 40), 6)
    # cup + papers
    cx, cy = rot([(420, 960)], wob, *pv)[0]
    poly(d, [(cx - 30, cy - 40), (cx + 30, cy - 40), (cx + 24, cy + 40), (cx - 24, cy + 40)], (240, 240, 245), 6)
    if (1 - k_fixed) > .3:
        for i in range(3): ell(d, cx + 40 + 25 * i + 6 * math.sin(t * 20 + i), cy - 50 - 20 * i, 9, 9, (120, 80, 50), 0)
    px, py = rot([(640, 990)], wob, *pv)[0]
    poly(d, rot([(px - 80, py - 10), (px + 80, py - 10), (px + 80, py + 10), (px - 80, py + 10)], wob, px, py), (255, 255, 255), 5)

def hook_scene(d, img, t, li_mouth=0.0, eyes=None, blq=True):
    room(d, (232, 222, 200))
    rect(d, 120, 420, 360, 640, (130, 200, 240)); line(d, [(240, 420), (240, 640)], OUT, 6); line(d, [(120, 530), (360, 530)], OUT, 6)
    k = eout(phase(t, .75, 1.05))
    desk(d, img, t, k)
    if k < 1:
        bx = lerp(900, 343, k); by = lerp(820, 1222, k); s = lerp(1.0, .55, k); ang = lerp(-10, 0, k)
    else:
        bx, by, s, ang = 343, 1222, .55, 0
    # calço: boletim deitado (achatado) embaixo do pé esquerdo
    if k >= 1:
        rect(d, 285, 1205, 400, 1240, (252, 250, 240), 5)
        text_c(d, 342, 1223, '10', F(900, 34), RED, 0)
    else:
        r = boletim(d, bx, by, s, ang); paste_rot(img, r[0], r[1], r[2])
    arm = 'hold' if k < .2 else 'point'
    e = eyes or ('angry' if t < .8 else 'wide')
    if blq: char(d, 'BLQ', 900, FY, .95, mouth=li_mouth, eyes=e, arm=arm, flip=True)
    return k

def counter(d, t, c):
    t0 = max(c.S[1], 4.15)
    if t < t0 or t >= c.total - TAIL: return
    li = current(c, t)
    act = ITEM_OF.get(li, -1) if isinstance(li, int) else 3
    alldone = t >= c.res
    for i in range(4):
        k = eout((t - t0 - .15 * i) / .25)
        if k <= 0: continue
        x = 540 + (i - 1.5) * 225; y = lerp(150, 305, k)
        done = alldone or (act > i)
        on = (i == act) and not alldone
        sc = 1.12 if on else 1.0
        if i == 3 and isinstance(li, int) and li == 1 and t > wt(c, 1, 'PESA') - .1:
            sc = 1.1 + .08 * math.sin(t * 20)
        w2, h2 = 100 * sc, 46 * sc
        fill = GREEN if done else (YEL if on else (40, 40, 48))
        d.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 14, fill=fill, outline=OUT, width=6)
        lab = f'{i + 1} ' + (ITEMS[i] if (on or done) else '?')
        fs = 34 if len(lab) < 9 else 28
        d.text((x, y), lab, font=F(900, fs), fill=OUT if (done or on) else WHITE, anchor='mm')
        if alldone:
            ks = eout((t - c.res - .1 * i) / .2)
            if ks > 0: check(d, x + 88, y - 40, 34 * ks)

def check(d, x, y, s, col=GREEN):
    pts = [(x - s, y), (x - s * .35, y + s * .65), (x + s, y - s * .8), (x + s * .75, y - s * 1.05), (x - s * .35, y + s * .15), (x - s * .75, y - s * .3)]
    poly(d, pts, col, 5)

def faculdade(d, t):
    sky(d, False, 0, GY); cloud(d, 200 + 15 * math.sin(t * .3), 520, .9); ground(d, GY)
    poly(d, [(170, 700), (910, 700), (540, 520)], (160, 60, 50))
    rect(d, 220, 700, 860, 1165, (175, 75, 55))
    for fx in (270, 430, 640, 760):
        for fy in (760, 900):
            rect(d, fx, fy, fx + 70, fy + 90, (130, 200, 240), 5)
    rect(d, 500, 1010, 580, 1165, (110, 70, 40), 5)
    label(d, 540, 730, 'FACULDADE', 42, WHITE, (60, 30, 25))

def night_study(d, t, p):
    d.rectangle([0, 0, W, H], fill=(40, 45, 80)); d.rectangle([0, 1180, W, H], fill=(70, 60, 70)); line(d, [(0, 1180), (W, 1180)], OUT, 7)
    rect(d, 760, 380, 960, 560, (20, 24, 60), 6); ell(d, 900, 430, 30, 30, (240, 240, 210), 4)
    rect(d, 150, 1040, 900, 1080, (120, 80, 50))
    n = 3 + int(p * 18)
    for i in range(n):
        col = [(200, 60, 60), (60, 120, 200), (60, 170, 90), (220, 180, 50)][i % 4]
        rect(d, 220 + (i % 2) * 8, 1040 - (i + 1) * 34, 400 + (i % 2) * 8, 1040 - i * 34, col, 5)
    line(d, [(760, 1040), (760, 900), (690, 860)], OUT, 10); poly(d, [(640, 830), (740, 830), (720, 880), (660, 880)], (240, 200, 60), 5)
    char(d, 'BLQ', 600, FY, .9, eyes='closed' if (t * 2) % 2 < .6 else 'roll', arm='face', arm2='down')
    for i in range(2):
        text_c(d, 700 + i * 40, 760 - i * 50 - 30 * ((t * .8 + i * .5) % 1), 'z', F(900, 60 + i * 15), WHITE, 6)

def office(d, wall=(225, 232, 240)):
    room(d, wall)
    rect(d, 760, 420, 980, 620, (130, 200, 240)); line(d, [(870, 420), (870, 620)], OUT, 6)

def diploma(d, t, p):
    room(d, (215, 225, 235))
    rect(d, 260, 470, 820, 860, (170, 120, 60), 10)
    rect(d, 300, 510, 780, 820, (252, 248, 230), 6)
    d.text((540, 570), 'DIPLOMA', font=F(900, 64), fill=OUT, anchor='mm')
    d.text((540, 640), 'ENGENHARIA CIVIL', font=F(800, 34), fill=(90, 90, 100), anchor='mm')
    for i in range(2): d.line([(360, 700 + i * 34), (720, 700 + i * 34)], fill=(160, 160, 170), width=5)
    ell(d, 700, 770, 34, 34, YEL, 5)
    # teia
    k = eout(phase(p, .35, 1.0))
    if k > 0:
        cx, cy = 790, 490; R = 230 * k
        for a in range(0, 100, 18):
            ar = math.radians(90 + a)
            d.line([(cx, cy), (cx + R * math.cos(ar), cy + R * math.sin(ar))], fill=(250, 250, 250), width=4)
        for r in (.3, .55, .8, 1.0):
            pts = [(cx + R * r * math.cos(math.radians(90 + a)), cy + R * r * math.sin(math.radians(90 + a))) for a in range(0, 100, 18)]
            d.line(pts, fill=(250, 250, 250), width=3)
        ell(d, cx - 60 * k, cy + 70 + 40 * math.sin(t * 3), 14, 12, OUT, 0)
    rnd = random.Random(int(t * 4))
    for i in range(int(12 * k)):
        ell(d, rnd.randint(260, 820), rnd.randint(470, 860), 4, 4, (200, 190, 170), 0)

def chalk(d, x0, y0, x1, y1):
    rect(d, x0, y0, x1, y1, (40, 85, 65), 10)

def scene_conta(d, img, t, c, p):
    office(d, (236, 228, 214))
    chalk(d, 80, 400, 1000, 900)
    if t < c.sol6 + .1:
        f = F(800, 40)
        lines = ['Md = 1,4 × 42 kN.m', 'As = Md / (0,87 fyd d)', 'x / d < 0,45', 'Nk / Ac + ... = fcd', 'Asw / s > 0,2 fct bw']
        for i, s in enumerate(lines):
            d.text((130, 460 + i * 85), s, font=f, fill=(235, 240, 230))
        if t > c.stamp6:
            k = eout((t - c.stamp6) / .15); s = lerp(1.8, 1.0, k)
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
            g.rounded_rectangle([540 - 260 * s, 760 - 60 * s, 540 + 260 * s, 760 + 60 * s], 14, outline=GREEN, width=int(10 * s))
            g.text((540, 760), 'CALCULADO', font=F(900, int(70 * s)), fill=GREEN, anchor='mm')
            L = L.rotate(6, center=(540, 760), resample=Image.BICUBIC); img.alpha_composite(L)
        sleep = t < c.stamp6
        char(d, 'VAL', 830, FY + 20, .85, eyes='closed' if sleep else 'normal', arm='down', look=-1)
        if sleep:
            for i in range(2): text_c(d, 900 + i * 40, 1000 - i * 50 - 30 * ((t + i * .5) % 1), 'z', F(900, 60 + 14 * i), WHITE, 6)
        char(d, 'BLQ', 300, FY, .9, mouth=c.m('BLQ'), eyes='normal', arm='point', flip=False)
    else:
        k = eout((t - c.sol6 - .1) / .3)
        house(d, 330, 820, 420, 360, small=True)
        if k > 0: check(d, 820, 560, 90 * k)
        label(d, 540, 960, 'SOLUÇÃO', 46, YEL)
        char(d, 'VAL', 830, FY + 20, .85, eyes='wide', mouth=.7, arm='up', arm2='up', look=-1)
        char(d, 'BLQ', 300, FY, .9, mouth=c.m('BLQ'), eyes='normal', arm='point')

def question_box(d, t, p):
    d.rectangle([0, 0, W, H], fill=(30, 32, 44)); d.rectangle([0, 1180, W, H], fill=(55, 55, 66)); line(d, [(0, 1180), (W, 1180)], OUT, 7)
    # prova riscada
    pts = rot([(110, 480), (430, 480), (430, 900), (110, 900)], -6, 270, 690)
    poly(d, pts, (252, 250, 240), 6)
    d.text((270, 540), 'PROVA', font=F(900, 46), fill=OUT, anchor='mm')
    for i in range(5): d.line([(150, 610 + i * 52), (400, 610 + i * 52)], fill=(160, 160, 170), width=5)
    line(d, [(120, 500), (430, 890)], RED, 16); line(d, [(430, 500), (120, 890)], RED, 16)
    s = 1 + .05 * math.sin(t * 6)
    rect(d, 560, 470, 960, 910, (15, 15, 20), 8, r=24)
    text_c(d, 760, 690, '?', F(900, int(300 * s)), YEL, 12)
    # cadeado
    d.arc([720, 840, 800, 920], 180, 360, fill=(200, 200, 205), width=12)
    rect(d, 705, 880, 815, 960, (230, 180, 40), 6)

def human_scene(d, t, c, p, close=False):
    sky(d, False, 0, GY); cloud(d, 820, 420, .8); ground(d, GY)
    house(d, 470, GY + 10, 470, 500, crack=1, cr_side=1)
    if not close:
        char(d, 'BLQ', 250, FY, .9, mouth=c.m('BLQ'), eyes='normal', arm='face', arm2='down')
        char(d, 'VAL', 800, FY + 20, .85, mouth=c.m('VAL'), eyes='normal', arm='up', look=-1, flip=True)
        if p > .1: label(d, 540, 520, 'PARTE HUMANA', 50, YEL)
    else:
        char(d, 'BLQ', 200, FY + 60, .75, eyes='normal', arm='down', flip=False)
        char(d, 'VAL', 700, FY + 40, 1.1, mouth=c.m('VAL'), eyes='wide', arm='hold', arm2='hold', look=-1, flip=True)

def final_scene(d, img, t, c, p):
    sky(d, False, 0, GY); cloud(d, 200, 380, .8); ground(d, GY)
    fixed = t > c.res
    house(d, 470, GY + 10, 470, 500, crack=0 if fixed else 1, cr_side=1)
    # boletim voando pra fora
    k = phase(t, c.S[10] + .2, c.S[10] + 1.2)
    if k < 1:
        r = boletim(d, lerp(260, -200, k), lerp(900, 300, k), .6, k * 400); paste_rot(img, r[0], r[1], r[2])
    # checklist
    labs = ['OUVIR', 'EXPLICAR SIMPLES', 'CUMPRIR O COMBINADO']
    for i, tt in enumerate(c.tick):
        if t >= tt - .05:
            kk = eout((t - tt + .05) / .2); y = 420 + i * 110
            d.rounded_rectangle([90, y - 44, 90 + 760 * kk, y + 44], 16, fill=(20, 20, 26), outline=OUT, width=5)
            if kk > .6:
                check(d, 140, y + 4, 30)
                d.text((190, y), labs[i], font=F(900, 48), fill=WHITE, anchor='lm')
    if fixed:
        k2 = eout((t - c.res) / .18); s = lerp(2.2, 1.0, k2)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        g.rounded_rectangle([705 - 230 * s, 880 - 60 * s, 705 + 230 * s, 880 + 60 * s], 14, outline=GREEN, width=int(11 * s), fill=(255, 255, 255, 200))
        g.text((705, 880), 'RESOLVIDO', font=F(900, int(66 * s)), fill=GREEN, anchor='mm')
        L = L.rotate(-7, center=(705, 880), resample=Image.BICUBIC); img.alpha_composite(L)
    char(d, 'BLQ', 230, FY, .9, mouth=c.m('BLQ'), eyes='normal', arm='up' if fixed else 'point', arm2='down')
    char(d, 'VAL', 860, FY + 20, .82, eyes='wide' if fixed else 'normal', mouth=.8 if fixed else 0, arm='up' if fixed else 'down', arm2='up' if fixed else 'down', flip=True)

# ---------------- shots ----------------
def shot(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    if li == 'tail':
        th = t - (c.total - TAIL)
        hook_scene(d, img, th, 0)
        return (1.22 - .02 * th / .6, 600, 1020, 0)
    p = phase(t, S[li], E[li])
    if li == 0:
        k = hook_scene(d, img, t, m('BLQ'))
        z = 1.22 if t < 1.05 else lerp(1.22, 1.05, eout(phase(t, 1.6, 3.4)))
        return (z, 600, 1020, 9 * (1.05 < t < 1.3))
    if li == 11:
        hook_scene(d, img, (t - S[11]) * .3, m('BLQ'), eyes='normal')
        return (lerp(1.05, 1.22, eout(p)), 600, 1020, 0)
    if li == 1:
        faculdade(d, t)
        char(d, 'BLQ', 830, FY, .9, mouth=m('BLQ'), eyes='normal', arm='up', flip=True)
        return (1.0 + .05 * p, 540, 960, 0)
    if li == 2:
        tsplit = wt(c, 2, 'NENHUM') - .15
        if t < tsplit:
            night_study(d, t, phase(t, S[2], tsplit))
            return (1.04 + .06 * phase(t, S[2], tsplit), 520, 960, 0)
        office(d)
        k = eout(phase(t, tsplit, tsplit + .3))
        char(d, 'VAL', 760, FY + 20, .85, eyes='normal', arm='phone', prop='celular', look=1)
        char(d, 'BLQ', 300, FY, .9, mouth=m('BLQ'), eyes='normal', arm='up')
        r = boletim(d, 410, lerp(1100, 760, k), .8, 8); paste_rot(img, r[0], r[1], r[2])
        return (1.05, 540, 1000, 0)
    if li == 3:
        office(d)
        char(d, 'BLQ', 260, FY, .85, eyes='closed', arm='hold')
        r = boletim(d, 360, 1080 + 40 * eout(p), .65, 30 * eout(p)); paste_rot(img, r[0], r[1], r[2])
        char(d, 'VAL', 740, FY + 10, 1.0, mouth=m('VAL'), eyes='roll', arm='point', flip=True, look=-1)
        return (1.08 + .06 * p, 640, 950, 0)
    if li == 4:
        diploma(d, t, p)
        sad = p > .55
        char(d, 'BLQ', 540, FY + 40, .8, mouth=m('BLQ'), eyes='normal' if not sad else 'closed', arm='up' if not sad else 'down', arm2='down')
        if .2 < p < .55: label(d, 540, 400, 'UNIVERSIDADE BOA', 46, WHITE, (40, 120, 60))
        return (1.0 + .08 * p, 540, 860, 0)
    if li == 5:
        tq = wt(c, 5, 'MAS') - .1
        if t < tq:
            d.rectangle([0, 0, W, H], fill=(30, 32, 44))
            yr = 2016 + min(10, int((t - S[5]) / .12))
            label(d, 540, 1250, f'{yr}', 60, WHITE)
            char(d, 'BLQ', 880, FY + 60, .7, mouth=m('BLQ'), eyes='wide', arm='point', flip=True)
            return (1.0, 540, 960, 7 * (t - c.rt < .25 and t > c.rt))
        question_box(d, t, p)
        char(d, 'BLQ', 200, FY + 60, .7, mouth=m('BLQ'), eyes='normal', arm='point')
        return (1.0 + .1 * phase(t, tq, E[5]), 700, 820, 0)
    if li == 6:
        scene_conta(d, img, t, c, p)
        return (1.03 + .04 * p, 540, 900, 8 * (0 < t - c.stamp6 < .2))
    if li == 7:
        room(d, (225, 215, 240))
        rect(d, 140, 420, 380, 640, (130, 200, 240))
        char(d, 'CID', 520, FY, 1.1, mouth=m('CID'), arm='phone', prop='celular', eyes='normal')
        char(d, 'VAL', 930, FY + 40, .7, eyes='normal', arm='down', flip=True, look=-1)
        if p > .25: label(d, 300, 760, 'SOBRINHO (ENG.)', 40, WHITE, (40, 120, 60))
        return (1.03 + .08 * p, 540, 950, 0)
    if li == 8:
        tc = wt(c, 8, 'TODO') - .1
        human_scene(d, t, c, p, close=False)
        if t > tc: return (lerp(1.0, 1.15, eout(phase(t, tc, E[8]))), 760, 950, 0)
        return (1.0, 540, 960, 0)
    if li == 9:
        human_scene(d, t, c, p, close=True)
        return (lerp(1.15, 1.25, eout(p)), 720, 900, 0)
    if li == 10:
        final_scene(d, img, t, c, p)
        return (1.0, 540, 960, 12 * (0 < t - c.res < .25))

def frame(c, t, overlays=True):
    img = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(img)
    li = current(c, t)
    fi = int((t + TH / FPS) * FPS)
    c.m = lambda who: float(c.envs[who][fi]) if fi < c.nf else 0
    z, cx, cy, sh = shot(li, t, c, d, img)
    if sh:
        r = random.Random(int(t * 60)); cx += r.uniform(-sh, sh) / z * 2; cy += r.uniform(-sh, sh) / z * 2
    if abs(z - 1) > .005 or abs(cx - W / 2) > 1 or abs(cy - H / 2) > 1:
        z = max(z, 1.0); cw, chh = W / z, H / z
        x0 = clamp(cx - cw / 2, 0, W - cw); y0 = clamp(cy - chh / 2, 0, H - chh)
        img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.BILINEAR)
    d = ImageDraw.Draw(img)
    for i in range(1, len(c.S)):
        if 0 <= t - c.S[i] + .12 < .06: d.rectangle([0, 0, W, H], fill=(255, 255, 255))
    if 0 <= t - (c.total - TAIL) < .04: d.rectangle([0, 0, W, H], fill=(255, 255, 255))
    if not overlays or li == 'tail': return img.convert('RGB')
    rshow = c.rt <= t <= c.rt + 2.6
    if not rshow and t < c.ctat: draw_caption(d, c.blocks, t, KEYS_Y, [])
    reveal(d, t, c.rt, REV[2], REV[3], REV[4])
    counter(d, t, c)
    if t >= c.ctat:
        k = eout((t - c.ctat) / .2); s = .7 + .3 * k
        text_c(d, W / 2, 1440, 'MANDA', F(900, int(96 * s)), YEL, 10)
        sz = 62
        while d.textlength(CTA_WHO, font=F(900, sz)) > 1000 and sz > 30: sz -= 2
        text_c(d, W / 2, 1535, CTA_WHO, F(900, int(sz * s)), WHITE, 8)
    tarja(img, d, t, c.tarja[0], c.tarja[1], TITLE, SUB)
    return img.convert('RGB')

def capa(c):
    base = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(base)
    hook_scene(d, base, 2.0, 0, blq=False)
    rect(d, 262, 1196, 424, 1242, (252, 250, 240), 5); text_c(d, 343, 1219, '10', F(900, 44), RED, 0)
    z = 1.35; cx, cy = 520, 1150; cw, chh = W / z, H / z
    base = base.crop((int(cx - cw / 2), int(cy - chh / 2), int(cx + cw / 2), int(cy + chh / 2))).resize((W, H), Image.BILINEAR)
    base = ImageEnhance.Brightness(base).enhance(.88)
    vig = Image.new('L', (W, H), 0); g = ImageDraw.Draw(vig)
    g.ellipse([-300, -200, W + 300, H + 200], fill=255); vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 255)); base = Image.composite(base, dark, vig)
    d = ImageDraw.Draw(base)
    d.ellipse([150, 960, 460, 1160], outline=RED, width=12)
    char(d, 'BLQ', 800, 1690, 1.25, eyes='wide', arm='point', arm2='face', flip=True, mouth=.8)
    arrow(d, 640, 1260, 470, 1120, RED, 30, 64)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    sz = 150; l1 = THUMB[0]; l2 = ' '.join(THUMB[1:])
    while g.textlength(l2, font=F(900, sz)) > 990: sz -= 4
    g.rectangle([0, 760 - sz * 1.3, W, 760 + sz * 1.3], fill=(10, 12, 16, 235))
    g.text((W / 2, 760 - sz * .6), l1, font=F(900, sz), fill=YEL, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    g.text((W / 2, 760 + sz * .62), l2, font=F(900, sz), fill=WHITE, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    L = L.rotate(4, center=(W / 2, 760), resample=Image.BICUBIC); base.alpha_composite(L)
    return base.convert('RGB')

def sheet(c, ts, out):
    ims = [capa(c)] + [frame(c, t) for t in ts]
    cols = 6; rows = math.ceil(len(ims) / cols); tw, th = 270, 480
    Sh = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
    for i, im in enumerate(ims):
        Sh.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
        ImageDraw.Draw(Sh).text(((i % cols) * tw + 5, (i // cols) * th + 5), f'{ts[i-1]:.1f}' if i else 'capa', fill=(255, 0, 0), font=F(800, 20))
    Sh.save(out)

if __name__ == '__main__':
    c = setup('D', 3.5)
    print('total', c.total, 'rt', c.rt, 'S', [round(x, 2) for x in c.S])
    ts = [0.1, 0.9, 1.5, 2.6, 5.0] + [c.S[i] + min(1.5, (c.E[i] - c.S[i]) * .6) for i in range(2, 11)] + [c.S[2] + .6, c.rt + .4, c.stamp6 + .1, c.res + .2, c.ctat + .5, c.tick[1] + .3, c.S[11] + .5, c.total - .3]
    sheet(c, ts, '/home/claude/serie/out/sheet.png')

def render_all(style, dur, music, out, capa_out):
    c = setup(style, dur)
    sfxp = '/home/claude/serie/out/sfx.wav'; aud = '/home/claude/serie/out/aud.wav'
    write_sfx(c.ev, c.total, sfxp)
    build_audio(1, [(KEYS[(1, i)], c.S[i]) for i in range(len(c.S))], c.total, music, sfxp, aud)
    cp = capa(c); cp.save(capa_out)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', aud, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                          '-t', str(c.nf / FPS), '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(c.nf):
        im = cp if f < TH else frame(c, (f - TH) / FPS)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return c
