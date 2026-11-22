import sys, os
sys.path.insert(0, '/home/claude/serie')
from eps import *

TITLE = 'O ENGENHEIRO DE 6 BRAÇOS'; SUB = 'A VIDA DE QUEM É AUTÔNOMO'
THUMB = ['6 CARGOS', '1 CPF SÓ']
CTA_WHO = 'PRO ENGENHEIRO QUE FAZ TUDO SOZINHO'
KEYS_Y = ['6', 'BRAÇOS', 'AUTÔNOMO', 'CARGOS', 'ÚLTIMO', 'PROJETAR', 'FACULDADE', 'OBRA', 'CONCRETAGEM', 'CLIENTE', 'DOMINGO',
          'FINANCEIRO', 'NOTA', 'MARKETING', 'CPF', 'SEXTO', 'PROSPECTAR', 'SOZINHO', 'SERVIÇO', 'HORA', 'MARCADA', '1', '2', '3', '4', '5']
TAIL = 0.6
EXTRA = {}
NUMMAP = {(0, 'seis'): '6', (1, 'seis'): '6', (1, 'cinco.'): '5.', (2, 'Um:'): '1:', (3, 'Dois:'): '2:', (5, 'Três:'): '3:', (6, 'Quatro:'): '4:',
          (7, 'Cinco:'): '5:', (8, 'Seis'): '6', (10, 'Seis:'): '6:', (10, 'cinco'): '5'}
PURPLE = (150, 90, 200); ORANGE = (245, 120, 30)
JOBS = [('PROJETO', BLUE), ('OBRA', ORANGE), ('CLIENTE', GREEN), ('FINANCEIRO', PURPLE), ('MARKETING', RED), ('PROSPECÇÃO', YEL)]
ACTIVE = {2: 0, 3: 1, 4: 2, 5: 2, 6: 3, 7: 4, 10: 5}

def timeline():
    lines = EPS[1]['lines']; t = 0.05; S = []; E = []; items = []
    for i in range(len(lines)):
        k = KEYS[(1, i)]; d = CL[k]['dur']
        t += EXTRA.get(i, 0)
        S.append(t); E.append(t + d); items.append((k, t)); t += d + GAP
    total = E[-1] + 0.05 + TAIL
    return S, E, items, total

def wt(c, li, prefix):
    k = KEYS[(1, li)]
    for w in CL[k]['words']:
        if re.sub(r'[^A-ZÀ-Ü]', '', w['w'].upper()).startswith(prefix): return c.S[li] + w['s']
    return c.S[li] + .5

def setup(style, dur):
    S, E, items, total = timeline()
    nf = int((total + TH / FPS) * FPS) + 1
    envs = {k: np.zeros(nf) for k in ['VAL', 'CID']}
    for li, (k, t0) in enumerate(items):
        sp = k.split('_')[0]
        if sp not in envs: continue
        e = envelope(f'/home/claude/serie/clips/{k}.wav', int(CL[k]['dur'] * FPS) + 2)
        f0 = int((t0 + TH / FPS) * FPS)
        for i, v in enumerate(e):
            if f0 + i < nf: envs[sp][f0 + i] = v
    for k in envs:
        mx = np.percentile(envs[k][envs[k] > 0], 90) if (envs[k] > 0).any() else 1
        envs[k] = np.clip(envs[k] / (mx + 1e-9), 0, 1)
    words = []
    for li, (k, t0) in enumerate(items):
        for w in CL[k]['words']:
            words.append(dict(w=NUMMAP.get((li, w['w']), w['w']), s=t0 + w['s'], e=t0 + w['e']))
    c = Ctx(); c.S, c.E, c.total, c.nf = S, E, total, nf
    c.blocks = build_blocks(words); c.envs = envs; c.tarja = (style, dur)
    c.rt = S[8] + .02
    c.rdur = wt(c, 8, 'SEXTO') - .3 - c.rt
    c.sexto = wt(c, 8, 'SEXTO')
    c.ult = wt(c, 1, 'ÚLTIMO'); c.seg = wt(c, 1, 'SEGURA')
    c.fac = wt(c, 2, 'FACULDADE'); c.dom = wt(c, 5, 'DOMINGO')
    c.mk = [wt(c, 7, 'GRAVAR'), wt(c, 7, 'POSTAR'), wt(c, 7, 'RESPONDER')]
    c.sem = wt(c, 10, 'SEM') - .12; c.serv = wt(c, 10, 'SERVIÇO') + .15
    c.blk = [S[11] + .15 + .3 * i for i in range(6)]
    c.ctat = S[12] - .05
    c.pap = [S[6] + .15 + .36 * i for i in range(6)]
    c.bub = [S[5] + .25 + .5 * i for i in range(4)]
    n = len(S)
    ev = [(0.0, 'boing'), (.98, 'thud'), (0.02, {'A': 'whoosh', 'B': 'blip', 'C': 'thud', 'D': 'whoosh', 'E': 'thud', 'F': 'stamp', 'G': 'vhs'}[style])]
    for i in range(1, n): ev.append((S[i] - .18, 'whoosh'))
    ev += [(S[1] + .2 + .2 * i, 'blip') for i in range(6)] + [(c.ult, 'pop')]
    ev += [(c.fac, 'pop'), (S[3] + .5, 'thud'), (S[4] - .1, 'alarm')]
    ev += [(x, 'blip') for x in c.bub] + [(x + .22, 'blip') for x in c.pap]
    ev += [(c.mk[0], 'blip'), (c.mk[1], 'pop'), (c.mk[2], 'blip')]
    ev += [(c.rt - .75, 'riser'), (c.rt, 'pop'), (c.rt + .02, 'thud'), (c.sexto, 'blip')]
    ev += [(S[10] + .05, 'pop'), (c.serv, 'stamp')]
    ev += [(x, 'pop') for x in c.blk] + [(c.blk[-1] + .25, 'sting')]
    ev += [(S[12], 'alarm'), (S[12] + .3, 'boing'), (c.ctat + .05, 'pop'), (total - TAIL - .02, 'whoosh'), (total - TAIL + .02, 'thud')]
    c.ev = ev
    return c

def current(c, t):
    if t >= c.total - TAIL: return 'tail'
    li = 0
    for i in range(len(c.S)):
        if t >= c.S[i] - .12: li = i
    return li

# ---------------- props ----------------
def check(d, x, y, s, col=GREEN):
    pts = [(x - s, y), (x - s * .35, y + s * .65), (x + s, y - s * .8), (x + s * .75, y - s * 1.05), (x - s * .35, y + s * .15), (x - s * .75, y - s * .3)]
    poly(d, pts, col, 5)

def heart(d, x, y, s, col=RED):
    pts = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        pts.append((x + s * 16 * math.sin(a) ** 3, y - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))))
    poly(d, pts, col, 6)

def icon(d, k, x, y, s=1.0):
    ow = max(3, int(6 * s))
    if k == 0:  # prancha de projeto
        rect(d, x - 48 * s, y - 58 * s, x + 48 * s, y + 58 * s, (250, 250, 255), ow, r=int(6 * s))
        bl = (40, 90, 200); w = max(2, int(6 * s))
        d.line([(x - 28 * s, y + 34 * s), (x - 28 * s, y - 22 * s), (x + 28 * s, y - 22 * s), (x + 28 * s, y + 34 * s)], fill=bl, width=w)
        d.line([(x - 40 * s, y + 36 * s), (x + 40 * s, y + 36 * s)], fill=bl, width=w)
    elif k == 1:  # cone de obra
        poly(d, [(x, y - 62 * s), (x + 40 * s, y + 40 * s), (x - 40 * s, y + 40 * s)], ORANGE, ow)
        d.polygon([(x - 17 * s, y - 15 * s), (x + 17 * s, y - 15 * s), (x + 25 * s, y + 6 * s), (x - 25 * s, y + 6 * s)], fill=WHITE)
        rect(d, x - 56 * s, y + 38 * s, x + 56 * s, y + 58 * s, ORANGE, ow)
    elif k == 2:  # celular
        rect(d, x - 38 * s, y - 62 * s, x + 38 * s, y + 62 * s, (40, 44, 56), ow, r=int(12 * s))
        d.rounded_rectangle([x - 26 * s, y - 40 * s, x + 26 * s, y + 4 * s], int(10 * s), fill=GREEN)
        d.rounded_rectangle([x - 26 * s, y + 14 * s, x + 10 * s, y + 38 * s], int(8 * s), fill=(230, 230, 235))
    elif k == 3:  # calculadora
        rect(d, x - 44 * s, y - 60 * s, x + 44 * s, y + 60 * s, (215, 218, 225), ow, r=int(8 * s))
        d.rectangle([x - 32 * s, y - 48 * s, x + 32 * s, y - 22 * s], fill=(60, 90, 70))
        for r_ in range(3):
            for c_ in range(3):
                bx = x - 30 * s + c_ * 22 * s; by = y - 12 * s + r_ * 22 * s
                d.rectangle([bx, by, bx + 16 * s, by + 16 * s], fill=PURPLE if (r_ == 2 and c_ == 2) else (90, 94, 106))
    elif k == 4:  # megafone
        poly(d, [(x - 52 * s, y - 16 * s), (x + 18 * s, y - 50 * s), (x + 18 * s, y + 50 * s), (x - 52 * s, y + 16 * s)], RED, ow)
        rect(d, x + 18 * s, y - 58 * s, x + 36 * s, y + 58 * s, (245, 245, 245), ow)
        rect(d, x - 30 * s, y + 14 * s, x - 10 * s, y + 56 * s, (60, 60, 70), ow)
    elif k == 5:  # lupa
        line(d, [(x + 22 * s, y + 22 * s), (x + 58 * s, y + 60 * s)], OUT, int(26 * s)); line(d, [(x + 24 * s, y + 24 * s), (x + 56 * s, y + 58 * s)], (150, 100, 60), int(14 * s))
        ell(d, x - 8 * s, y - 8 * s, 44 * s, 44 * s, (190, 230, 250), ow + 3)
    elif k == 6:  # caixa ?
        rect(d, x - 52 * s, y - 52 * s, x + 52 * s, y + 52 * s, (20, 20, 28), ow, r=int(12 * s))
        d.text((x, y), '?', font=F(900, max(10, int(84 * s))), fill=YEL, anchor='mm')

def blq_head(d, x, y, r, eyes='normal'):
    ell(d, x, y, r, r * .92, (250, 205, 165), max(3, int(r * .09)))
    d.chord([x - r * 1.05, y - r * 1.1, x + r * 1.05, y + r * .25], 180, 360, fill=ORANGE, outline=OUT, width=max(3, int(r * .08)))
    rect(d, x - r * 1.2, y - r * .5, x + r * 1.2, y - r * .36, ORANGE, max(3, int(r * .07)))
    for k in (-1, 1):
        ex = x + k * r * .3; ey = y - r * .1
        if eyes == 'closed': d.line([(ex - r * .2, ey), (ex + r * .2, ey)], fill=OUT, width=max(2, int(r * .08))); continue
        rr = r * (.3 if eyes == 'wide' else .25)
        ell(d, ex, ey, rr, rr * 1.1, WHITE, max(2, int(r * .06))); ell(d, ex, ey + 1, r * .08, r * .08, OUT, 0)
    d.line([(x - r * .22, y + r * .52), (x + r * .22, y + r * .52)], fill=OUT, width=max(2, int(r * .07)))

HANDS = [(250, -560), (315, -335), (265, -110)]
ICONS_R = [0, 2, 3]; ICONS_L = [1, 4, 5]

def blq6(d, x, y, s, t, eyes='wide', grow=1.0, q6=False, wob=1.0, pulse=0):
    S = s * 1.25
    shy = y - 155 * S
    pos = []
    for j in (2, 1, 0):
        hx, hy = HANDS[j]
        rx = x + (hx + 24 * wob * math.sin(t * 9 + j * 1.7)) * S; ry = y + (hy + 22 * wob * math.cos(t * 11 + j * 2.3)) * S
        lx = x - (hx + 24 * wob * math.sin(t * 8 + j * 2.9 + 1)) * S; ly = y + (hy + 22 * wob * math.cos(t * 10 + j * 1.3 + 2)) * S
        if j > 0 or grow < 1:
            g = grow if j > 0 else max(grow, 0.0)
            if j > 0:
                rx = lerp(x + 110 * S, rx, g); ry = lerp(shy, ry, g); lx = lerp(x - 110 * S, lx, g); ly = lerp(shy, ly, g)
            else:
                # braços normais: de 'pra baixo' até a pose aberta
                rx = lerp(x + 140 * S, rx, g); ry = lerp(shy + 95 * S, ry, g); lx = lerp(x - 140 * S, lx, g); ly = lerp(shy + 95 * S, ly, g)
        if j > 0 and grow < .05:
            pos.append((j, None, None)); continue
        char(d, 'BLQ', x, y, s, eyes=eyes, arm=(rx, ry), arm2=(lx, ly))
        pos.append((j, (rx, ry), (lx, ly)))
    if all(p[1] is None for p in pos[:2]) and grow < .05:
        pass
    for j, r_, l_ in pos:
        if r_ is None: continue
        g = 1 if j == 0 else grow
        if j == 0 and grow < .5: continue
        if g < .5: continue
        icon(d, ICONS_R[j], r_[0] + 14 * S, r_[1] - 20 * S, s * 1.05)
        kl = ICONS_L[j]
        if kl == 5 and q6: icon(d, 6, l_[0] - 14 * S, l_[1] - 20 * S, s * (1.05 + .12 * pulse))
        else: icon(d, kl, l_[0] - 14 * S, l_[1] - 20 * S, s * 1.05)
    return pos

def office_bg(d, wall=(232, 222, 200), win=(110, 430)):
    room(d, wall)
    if win:
        x, y = win
        rect(d, x, y, x + 240, y + 220, (130, 200, 240)); line(d, [(x + 120, y), (x + 120, y + 220)], OUT, 6); line(d, [(x, y + 110), (x + 240, y + 110)], OUT, 6)

def hook_scene(d, img, tp, tw, grow=1.0, eyes='wide'):
    office_bg(d, (232, 222, 200), (760, 430))
    # pilha de pastas que tomba
    k = ease((tp - .85) / .32) if tp > .85 else 0
    ang = 84 * k * k
    cols = [(200, 60, 60), (60, 120, 200), (60, 170, 90), (220, 180, 50), (150, 90, 200)]
    n = 12
    for i in range(n):
        y1 = 1300 - i * 22; y0 = y1 - 22
        jx = (i % 2) * 8
        pts = [(90 + jx, y0), (250 + jx, y0), (250 + jx, y1), (90 + jx, y1)]
        spread = (i / n) * 70 * k
        pts = [(px + spread, py) for px, py in pts]
        poly(d, rot(pts, ang, 258, 1300), cols[i % 5], 5)
    # folhas voando depois do tombo
    if tp > 1.1:
        tt = tp - 1.1
        for i in range(7):
            r = random.Random(i + 5)
            x0 = 330 + i * 28; y0 = 1150 - i * 12
            px = x0 + r.uniform(-60, 160) * min(tt, 1.2); py = min(1290 + r.uniform(-20, 30), y0 - 260 * tt + 420 * tt * tt)
            a = r.uniform(-200, 200) * min(tt, 1.0)
            poly(d, rot([(px - 34, py - 24), (px + 34, py - 24), (px + 34, py + 24), (px - 34, py + 24)], a, px, py), (252, 250, 240), 4)
    blq6(d, 620, FY, .95, tw, eyes, grow)

def chips(d, t, c, li):
    if not isinstance(li, int) or li < 2 or li > 11: return
    t0 = c.S[2] - .1
    act = ACTIVE.get(li, -1)
    alldone = li == 11
    for i in range(6):
        k = eout((t - t0 - .07 * i) / .25)
        if k <= 0: continue
        x = 200 + (i % 3) * 340; y = lerp(140, 296 + (i // 3) * 92, k)
        done = alldone or (li >= 8 and i < 5) or (act > i)
        on = (i == act) and not alldone
        if i == 5 and li == 10 and t < c.S[10] + .05: on = False
        sc = 1.08 if on else 1.0
        if i == 5 and li in (8, 9) and not done: sc = 1.04 + .05 * math.sin(t * 9)
        w2, h2 = 158 * sc, 38 * sc
        fill = GREEN if done else (JOBS[i][1] if on else (40, 40, 48))
        d.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 14, fill=fill, outline=OUT, width=6)
        lab = f'{i + 1} ' + (JOBS[i][0] if (on or done) else '?')
        d.text((x, y), lab, font=F(900, 30), fill=OUT if (done or (on and i in (5,))) else WHITE, anchor='mm')

def org_scene(d, t, c):
    d.rectangle([0, 0, W, H], fill=(28, 34, 58))
    t0 = c.S[1]
    rect(d, 320, 470, 760, 574, YEL, 7, r=18); d.text((540, 522), 'ESCRITÓRIO', font=F(900, 50), fill=OUT, anchor='mm')
    line(d, [(540, 574), (540, 630)], WHITE, 6); line(d, [(200, 630), (880, 630)], WHITE, 6)
    cx = [200, 540, 880]; cy = [800, 1100]
    for i in range(6):
        x = cx[i % 3]; y = cy[i // 3]
        k = eout((t - t0 - .2 - .2 * i) / .2)
        if i < 3: line(d, [(x, 630), (x, 680)], WHITE, 6)
        else: line(d, [(x, 925), (x, 975)], WHITE, 6)
        if k <= 0: continue
        last = (i == 5) and t > c.ult
        s = (.6 + .4 * k) * (1 + .05 * math.sin(t * 12) if last else 1)
        w2, h2 = 135 * s, 125 * s
        d.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 20, fill=(245, 240, 225) if not last else YEL, outline=OUT, width=7)
        blq_head(d, x, y - 26 * s, 62 * s)
        d.text((x, y + 86 * s), f'CARGO {i + 1}', font=F(900, max(10, int(30 * s))), fill=OUT, anchor='mm')
    if t > c.seg:
        g = eout((t - c.seg) / .45)
        for i in range(5):
            x = cx[i % 3]; y = cy[i // 3]
            sx, sy = 880, 1100
            if i < 3: sy -= 125; ty = y + 125; tx = x
            else: sx -= 135; tx = x + 135; ty = y
            arrow(d, sx, sy, lerp(sx, tx, g), lerp(sy, ty, g), GREEN, 18, 40)

def truck(d, x, y, t):
    # caminhão betoneira virado pra esquerda; x = centro, y = chão
    rect(d, x - 170, y - 80, x + 190, y - 40, (60, 60, 70), 6)
    rect(d, x + 80, y - 220, x + 190, y - 78, (235, 235, 240), 7, r=14)
    rect(d, x + 120, y - 195, x + 175, y - 140, (130, 200, 240), 5)
    ell(d, x - 40, y - 175, 135, 100, (205, 208, 215), 7)
    for i in range(4):
        ph = ((t * 1.6 + i / 4) % 1)
        xx = x - 40 - 135 + 270 * ph
        hh = 100 * math.sqrt(max(0, 1 - ((xx - (x - 40)) / 135) ** 2))
        d.line([(xx, y - 175 - hh + 6), (xx + 20, y - 175 + hh - 6)], fill=ORANGE, width=10)
    d.ellipse([x - 175, y - 275, x + 95, y - 75], outline=OUT, width=7)
    for wx in (x - 110, x + 10, x + 140):
        ell(d, wx, y - 30, 38, 38, OUT, 0); ell(d, wx, y - 30, 15, 15, (170, 170, 175), 0)

def sc_projetar(d, img, t, c, p):
    office_bg(d, (225, 232, 240), None)
    rect(d, 690, 440, 960, 630, (170, 120, 60), 8); rect(d, 712, 462, 938, 608, (252, 248, 230), 5)
    d.text((825, 502), 'DIPLOMA', font=F(900, 36), fill=OUT, anchor='mm')
    for i in range(2): d.line([(742, 540 + i * 24), (908, 540 + i * 24)], fill=(160, 160, 170), width=5)
    ell(d, 900, 588, 16, 16, YEL, 4)
    rect(d, 80, 1040, 640, 1078, (150, 95, 55))
    for lx in (110, 590): rect(d, lx, 1078, lx + 26, 1215, (125, 75, 40), 6)
    rect(d, 330, 990, 390, 1042, (90, 90, 100), 5)
    rect(d, 150, 690, 570, 992, (40, 44, 56), 8, r=16); d.rectangle([174, 714, 546, 968], fill=(235, 245, 255))
    bl = (40, 90, 200)
    segs = [[(200, 930), (520, 930)], [(250, 930), (250, 790)], [(470, 930), (470, 790)], [(225, 790), (495, 790)], [(250, 930), (250, 955)], [(470, 930), (470, 955)]]
    kk = clamp(p * 1.6)
    m = int(len(segs) * kk + .999)
    for sg_ in segs[:max(1, m)]: line(d, sg_, bl, 9)
    if kk >= 1:
        for xx in (250, 470): rect(d, xx - 26, 925, xx + 26, 950, bl, 0)
    char(d, 'BLQ', 830, FY, .9, eyes='normal', arm='point', flip=True)
    if t > c.fac: check(d, 968, 448, 50 * eout((t - c.fac) / .2))

def sc_obra(d, img, t, c, p):
    sky(d, False, 0, GY); cloud(d, 220 + 15 * math.sin(t * .3), 520, .9); ground(d, GY)
    pillar(d, 350, 800, GY, 60); pillar(d, 640, 800, GY, 60)
    rect(d, 300, 700, 690, 802, (200, 150, 90), 7)
    f = eout(p)
    d.rectangle([312, 712, 678, 790], fill=(120, 80, 45))
    d.line([(322, 774), (668, 774)], fill=ORANGE, width=7); d.line([(322, 728), (668, 728)], fill=ORANGE, width=5)
    d.rectangle([678 - 366 * f, 712, 678, 790], fill=(175, 175, 180))
    truck(d, 880, GY, t)
    poly(d, [(745, 905), (770, 925), (700, 735), (680, 730)], (150, 150, 158), 6)
    label(d, 495, 640, 'CONCRETAGEM', 40, WHITE, (60, 60, 70))
    bx = lerp(-160, 165, eout(clamp(p * 1.5))); by = FY - abs(math.sin(t * 13)) * 34
    char(d, 'BLQ', bx, by, .85, eyes='wide', arm='up', arm2='up')
    for i in range(3):
        ell(d, bx - 20 + i * 60, by - 520 - 20 * abs(math.sin(t * 9 + i)), 11, 15, LBLUE, 4)

def sc_val(d, img, t, c, p, m):
    room(d, (215, 235, 215)); rect(d, 90, 480, 330, 700, (130, 200, 240)); line(d, [(210, 480), (210, 700)], OUT, 6)
    char(d, 'VAL', 560, FY + 30, 1.15, mouth=m('VAL'), eyes='angry', arm='phone', prop='celular')
    for i in range(3):
        a = -.5 + i * .5; r0 = 70 + 25 * ((t * 4) % 1); x0 = 860; y0 = 900
        d.arc([x0 - r0 - i * 28, y0 - r0 - i * 28, x0 + r0 + i * 28, y0 + r0 + i * 28], -40, 40, fill=OUT, width=8)
    label(d, 720, 540, 'CLIENTE', 54, YEL)

def sc_cliente(d, img, t, c, p):
    room(d, (250, 236, 210))
    pulse = 1 + .1 * math.sin((t - c.dom) * 18) * (0 < t - c.dom < .5)
    cw, ch = 135 * pulse, 150 * pulse
    rect(d, 815 - cw, 580 - ch, 815 + cw, 580 + ch, WHITE, 8, r=14)
    d.rounded_rectangle([815 - cw + 4, 580 - ch + 4, 815 + cw - 4, 580 - ch + 84 * pulse], 12, fill=RED)
    d.text((815, 580 - ch + 44 * pulse), 'DOMINGO', font=F(900, int(40 * pulse)), fill=WHITE, anchor='mm')
    d.text((815, 580 + 30 * pulse), 'DOM', font=F(900, int(92 * pulse)), fill=RED, anchor='mm')
    char(d, 'BLQ', 260, FY, .92, eyes='roll' if (t - c.S[5]) > .5 else 'normal', arm='phone', prop='celular', arm2='down')
    msgs = ['E O PROJETO?', 'OI??', 'TÁ PRONTO?', 'URGENTE!']
    for i, tb in enumerate(c.bub):
        if t < tb: continue
        k = eout((t - tb) / .18); f = F(800, int(42 * (.7 + .3 * k)))
        y = 1190 - sum(1 for x in c.bub if x <= t) * 100 + (i + 1) * 100 - 100
        w = d.textlength(msgs[i], font=f) + 56
        d.rounded_rectangle([450, y - 42, 450 + w, y + 42], 26, fill=(70, 190, 110), outline=OUT, width=6)
        d.text((478, y), msgs[i], font=f, fill=WHITE, anchor='lm')

def sc_fin(d, img, t, c, p):
    office_bg(d, (236, 228, 214), (760, 430))
    char(d, 'BLQ', 800, FY - 30, .9, eyes='roll' if p > .35 else 'normal', arm='face', arm2='down', flip=True)
    rect(d, 90, 1040, 990, 1080, (150, 95, 55))
    for lx in (130, 930): rect(d, lx, 1080, lx + 26, 1215, (125, 75, 40), 6)
    icon(d, 3, 600, 962, 1.25)
    labs = ['NOTA', 'BOLETO', 'IMPOSTO', 'RECIBO', 'NOTA', 'BOLETO']
    for i, tp in enumerate(c.pap):
        if t < tp: continue
        k = clamp((t - tp) / .22); k = k * k
        yl = 1012 - i * 56; y = lerp(250, yl, k); x = 300 + (18 if i % 2 else -14)
        rect(d, x - 150, y - 27, x + 150, y + 27, (252, 250, 240), 5, r=6)
        d.text((x, y), labs[i], font=F(900, 34), fill=OUT if labs[i] != 'IMPOSTO' else RED, anchor='mm')

def sc_mkt(d, img, t, c, p):
    room(d, (245, 228, 236))
    line(d, [(300, 900), (300, 1110)], OUT, 14)
    for ex in (215, 300, 385): line(d, [(300, 1110), (ex, 1250)], OUT, 12)
    d.ellipse([140, 590, 460, 910], outline=OUT, width=52); d.ellipse([146, 596, 454, 904], outline=(255, 240, 170), width=40)
    rect(d, 250, 670, 350, 830, (40, 44, 56), 6, r=14); d.rectangle([260, 684, 340, 816], fill=(110, 190, 245))
    blq_head(d, 300, 760, 30)
    char(d, 'BLQ', 740, FY, .95, eyes='wink' if t > c.mk[1] else 'normal', arm='up', arm2='down', flip=True)
    if t > c.mk[0]:
        on = int((t - c.mk[0]) * 3) % 2 == 0
        d.rounded_rectangle([210, 480, 390, 548], 16, fill=(20, 20, 26), outline=OUT, width=5)
        if on: ell(d, 246, 514, 14, 14, RED, 0)
        d.text((316, 514), 'REC', font=F(900, 38), fill=WHITE, anchor='mm')
    if t > c.mk[1]:
        k = eout((t - c.mk[1]) / .18); heart(d, 560, 640 - 30 * min(1, t - c.mk[1]), 4.2 * (.5 + .5 * k) + .5 * math.sin(min(1, (t - c.mk[1]) / .3) * math.pi))
    if t > c.mk[2]:
        k = eout((t - c.mk[2]) / .18); s = .5 + .5 * k
        d.rounded_rectangle([880 - 110 * s, 600 - 55 * s, 880 + 110 * s, 600 + 55 * s], int(30 * s), fill=WHITE, outline=OUT, width=6)
        for i in range(3): ell(d, 880 + (i - 1) * 50 * s, 600, 13 * s, 13 * s, OUT, 0)

def reveal2(d, t, c):
    t0 = c.rt
    if t < t0 or t > t0 + c.rdur: return
    k = t - t0; s = .4 + .6 * eout(k / .18) + .12 * math.sin(min(1, k / .3) * math.pi) * (k < .3)
    text_c(d, W / 2, 570, '6 CARGOS', F(900, int(168 * s)), YEL, 12)
    if k > .22: text_c(d, W / 2, 712, '1 CPF SÓ', F(900, int(96 * min(1, .7 + .3 * eout((k - .22) / .15)))), WHITE, 9)

def sc_reveal(d, img, t, c, p):
    d.rectangle([0, 0, W, H], fill=(28, 34, 58))
    cx0, cy0 = 540, 1080
    for i in range(12):
        a0 = math.radians(i * 30 + t * 14); a1 = math.radians(i * 30 + 15 + t * 14)
        if i % 2 == 0: d.polygon([(cx0, cy0), (cx0 + 2200 * math.cos(a0), cy0 + 2200 * math.sin(a0)), (cx0 + 2200 * math.cos(a1), cy0 + 2200 * math.sin(a1))], fill=(38, 46, 80))
    q = t > c.sexto - .1
    blq6(d, 540, FY + 70, .8, t, 'wide', 1.0, q6=q, pulse=math.sin(t * 14) if q else 0)

def sc_cid(d, img, t, c, p, m):
    room(d, (225, 215, 240)); rect(d, 110, 500, 350, 720, (130, 200, 240)); line(d, [(230, 500), (230, 720)], OUT, 6)
    char(d, 'VAL', 930, FY + 40, .7, eyes='normal', arm='down', flip=True, look=-1)
    char(d, 'CID', 500, FY, 1.1, mouth=m('CID'), arm='hold', prop='celular', eyes='normal')

def sc_prosp(d, img, t, c, p):
    if t < c.sem:
        sky(d, False, 0, GY); cloud(d, 800, 480, .8); ground(d, GY)
        for i, hx in enumerate((470, 700, 930)):
            house(d, hx, GY + 5, 190, 210, small=True, col=[(250, 225, 170), (205, 230, 200), (240, 205, 205)][i], roof=[(200, 70, 55), (90, 110, 160), (150, 90, 60)][i])
        bx = lerp(170, 300, eout(phase(t, c.S[10], c.sem)))
        hy = FY - 330
        char(d, 'BLQ', bx, FY - abs(math.sin(t * 9)) * 14, .95, eyes='normal', arm=(bx + 200, hy + 60), arm2='down', look=1)
        icon(d, 5, bx + 230, hy + 20, 1.5)
        return
    room(d, (214, 220, 232))
    # teia no canto
    for a in range(0, 100, 18):
        ar = math.radians(a); d.line([(0, 0), (330 * math.cos(ar), 250 + 330 * math.sin(ar) - 250)], fill=WHITE, width=4)
    d.line([(0, 250), (W, 250)], fill=(214, 220, 232), width=1)
    for a in range(0, 91, 18):
        ar = math.radians(a)
    for r_ in (110, 200, 290):
        d.line([(r_ * math.cos(math.radians(a)), r_ * math.sin(math.radians(a))) for a in range(0, 91, 18)], fill=WHITE, width=3)
    rect(d, 40, 1150, 1040, 1190, (150, 95, 55))
    for i in range(5):
        x = 140 + i * 200
        char(d, 'BLQ', x, FY - 105, .5, eyes='closed', arm='cross', arm2='cross')
        icon(d, i, x, 878, .85)
        zz = (t * .9 + i * .3) % 1
        text_c(d, x + 58, 800 - 46 * zz, 'z', F(900, 40 + int(14 * zz)), WHITE, 5)
    if t > c.serv:
        k = eout((t - c.serv) / .15); s = lerp(2.0, 1.0, k)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        g.rounded_rectangle([540 - 330 * s, 620 - 70 * s, 540 + 330 * s, 620 + 70 * s], 16, outline=RED, width=int(12 * s), fill=(255, 255, 255, 215))
        g.text((540, 620), 'SEM SERVIÇO', font=F(900, int(84 * s)), fill=RED, anchor='mm')
        L = L.rotate(6, center=(540, 620), resample=Image.BICUBIC); img.alpha_composite(L)

def sc_agenda(d, img, t, c, p):
    room(d, (236, 240, 246))
    x0, y0, x1 = 80, 478, 1000
    rh = 86; y1 = y0 + 104 + 6 * rh + 14
    rect(d, x0, y0, x1, y1, WHITE, 9, r=22)
    d.rounded_rectangle([x0 + 5, y0 + 5, x1 - 5, y0 + 100], 18, fill=(40, 44, 56))
    d.text(((x0 + x1) / 2, y0 + 54), 'AGENDA DA SEMANA', font=F(900, 48), fill=WHITE, anchor='mm')
    for i, tb in enumerate(c.blk):
        cy_ = y0 + 108 + (i + .5) * rh
        ell(d, x0 + 62, cy_, 30, 30, (245, 245, 250), 5)
        a = math.radians(-90 + i * 55); d.line([(x0 + 62, cy_), (x0 + 62 + 20 * math.cos(a), cy_ + 20 * math.sin(a))], fill=OUT, width=5)
        d.line([(x0 + 62, cy_), (x0 + 62, cy_ - 13)], fill=OUT, width=5)
        if t < tb:
            d.rounded_rectangle([x0 + 112, cy_ - 32, x1 - 22, cy_ + 32], 14, outline=(205, 210, 220), width=4)
            continue
        k = eout((t - tb) / .16); s = lerp(1.25, 1.0, k)
        xa = x0 + 112; xb = x1 - 22; xm = (xa + xb) / 2; w2 = (xb - xa) / 2 * min(1.02, s); h2 = 34 * s
        d.rounded_rectangle([xm - w2, cy_ - h2, xm + w2, cy_ + h2], 14, fill=JOBS[i][1], outline=OUT, width=6)
        d.text((xm, cy_), JOBS[i][0], font=F(900, int(44 * s)), fill=WHITE if i != 5 else OUT, stroke_width=0 if i == 5 else 4, stroke_fill=OUT, anchor='mm')
        if k >= 1: check(d, xb - 50, cy_ + 2, 20, WHITE if i != 5 else OUT)
    char(d, 'BLQ', 905, FY + 95, .52, eyes='normal', arm='up', arm2='down', flip=True)

# ---------------- shots ----------------
def shot(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    if li == 'tail':
        th = t - (c.total - TAIL)
        hook_scene(d, img, th, th)
        return (1.22, 620, 1000, 10 * (th < .2))
    p = phase(t, S[li], E[li])
    if li == 0:
        hook_scene(d, img, t, t)
        z = 1.22 if t < 1.0 else lerp(1.22, 1.06, eout(phase(t, 1.0, 2.0)))
        return (z, 620, 1000, 10 * (.95 < t < 1.25))
    if li == 1:
        org_scene(d, t, c)
        z = 1.0 if t < c.ult else lerp(1.0, 1.07, eout(phase(t, c.ult, c.ult + .5)))
        return (z, 540, 930, 0)
    if li == 2:
        sc_projetar(d, img, t, c, p); return (1.0 + .05 * p, 540, 930, 0)
    if li == 3:
        sc_obra(d, img, t, c, p); return (1.0 + .05 * p, 540, 960, 5 * (p > .15 and p < .3))
    if li == 4:
        sc_val(d, img, t, c, p, m); return (1.05 + .1 * eout(p), 560, 900, 0)
    if li == 5:
        sc_cliente(d, img, t, c, p); return (1.0 + .05 * p, 540, 960, 6 * (0 < t - c.dom < .2))
    if li == 6:
        sc_fin(d, img, t, c, p); return (1.03 + .05 * p, 520, 930, 0)
    if li == 7:
        sc_mkt(d, img, t, c, p); return (1.0 + .06 * p, 540, 950, 0)
    if li == 8:
        sc_reveal(d, img, t, c, p)
        if t > c.sexto - .1:
            g = eout(phase(t, c.sexto - .1, c.sexto + .35))
            return (lerp(1.03, 1.3, g), lerp(540, 380, g), lerp(960, 1180, g), 0)
        return (1.0 + .03 * p, 540, 960, 12 * (0 < t - c.rt < .25))
    if li == 9:
        sc_cid(d, img, t, c, p, m); return (1.03 + .1 * eout(p), 520, 930, 0)
    if li == 10:
        sc_prosp(d, img, t, c, p)
        if t < c.sem: return (1.05, 480, 960, 0)
        return (1.0 + .05 * phase(t, c.sem, E[10]), 540, 960, 9 * (0 < t - c.serv < .2))
    if li == 11:
        sc_agenda(d, img, t, c, p); return (1.0, 540, 960, 0)
    if li == 12:
        tl = t - S[12]
        g = eout(phase(tl, .3, .62))
        hook_scene(d, img, 0, tl, grow=g, eyes='normal' if tl < .3 else 'wide')
        if tl < .3:
            for i in range(3):
                r0 = 40 + 30 * ((tl * 6) % 1) + i * 24
                d.arc([790 - r0, 1100 - r0, 790 + r0, 1100 + r0], -50, 50, fill=OUT, width=8)
        return (lerp(1.06, 1.22, eout(phase(tl, .25, .8))), 620, 1000, 9 * (.3 < tl < .55))

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
    if not overlays: return img.convert('RGB')
    rshow = c.rt <= t <= c.rt + c.rdur
    if not rshow and t < c.ctat: draw_caption(d, c.blocks, t, KEYS_Y, [])
    reveal2(d, t, c)
    chips(d, t, c, li)
    if t >= c.ctat:
        k = eout((t - c.ctat) / .2); s = .7 + .3 * k
        text_c(d, W / 2, 1452, 'MANDA', F(900, int(104 * s)), YEL, 10)
        text_c(d, W / 2, 1548, 'PRO ENGENHEIRO', F(900, int(70 * s)), WHITE, 9)
        text_c(d, W / 2, 1628, 'QUE FAZ TUDO SOZINHO', F(900, int(70 * s)), WHITE, 9)
    tarja(img, d, t, c.tarja[0], c.tarja[1], TITLE, SUB)
    return img.convert('RGB')

def capa(c):
    base = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(base)
    office_bg(d, (232, 222, 200), (760, 430))
    base = ImageEnhance.Brightness(base).enhance(.8)
    vig = Image.new('L', (W, H), 0); g = ImageDraw.Draw(vig)
    g.ellipse([-300, -200, W + 300, H + 200], fill=255); vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 255)); base = Image.composite(base, dark, vig)
    d = ImageDraw.Draw(base)
    blq6(d, 540, 1800, 1.08, .35, 'wide')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    sz = 158; l1, l2 = THUMB
    while max(g.textlength(l1, font=F(900, sz)), g.textlength(l2, font=F(900, sz))) > 960: sz -= 4
    g.rectangle([-100, 740 - sz * 1.28, W + 100, 740 + sz * 1.28], fill=(10, 12, 16, 238))
    g.text((W / 2, 740 - sz * .6), l1, font=F(900, sz), fill=YEL, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    g.text((W / 2, 740 + sz * .62), l2, font=F(900, sz), fill=WHITE, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    L = L.rotate(4, center=(W / 2, 740), resample=Image.BICUBIC); base.alpha_composite(L)
    d = ImageDraw.Draw(base)
    arrow(d, 760, 985, 905, 1075, RED, 34, 66)
    return base.convert('RGB')

def sheet(c, ts, out):
    ims = [capa(c)] + [frame(c, t) for t in ts]
    cols = 6; rows = math.ceil(len(ims) / cols); tw, th = 270, 480
    Sh = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
    for i, im in enumerate(ims):
        Sh.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
        ImageDraw.Draw(Sh).text(((i % cols) * tw + 5, (i // cols) * th + 5), f'{ts[i-1]:.1f}' if i else 'capa', fill=(255, 0, 0), font=F(800, 20))
    Sh.save(out)

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

if __name__ == '__main__':
    c = setup('A', 1.5)
    print('total', round(c.total, 2), 'rt', round(c.rt, 2), round(c.rt / c.total * 100), '%', 'S', [round(x, 2) for x in c.S])
    S, E = c.S, c.E
    ts = [0.05, 0.6, 1.3, 2.0, S[1] + 1.4, c.seg + .6, S[2] + 1.8, S[3] + 1.4, S[4] + 1.0, c.dom + .3, S[6] + 2.3, c.mk[2] + .4,
          c.rt + .6, c.sexto + .6, S[9] + 2.0, S[10] + .5, c.serv + .3, c.blk[2] + .1, E[11] - .1, S[12] + .2, S[12] + .8, c.total - .3, c.total - .02]
    sheet(c, ts, '/home/claude/serie/out/sheet.png')
