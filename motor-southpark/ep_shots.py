from eps import *

def cam(z=1.0, cx=W / 2, cy=H / 2, sh=0): return (z, cx, cy, sh)

# ======================= EP1 =======================
def ep1(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    if li == 0:
        ext(d, 1, t=t)
        k = eout(phase(t, 0, 2.6)); ang = 7 * k
        house(d, 230, GY + 30 * k, 520, 560, ang=ang, pivot=(230, GY))
        char(d, 'VAL', 150, FY + 40, .8, eyes='wide', arm='up', arm2='up')
        return cam(1.18 - .14 * k, 520, 900, 6 * (k < .99))
    if li == 1:
        ext(d, 1, t=t)
        rect(d, 560, 1060, 860, 1150, (90, 90, 95)); rect(d, 600, 1150, 620, 1300, (60, 60, 60), 4); rect(d, 800, 1150, 820, 1300, (60, 60, 60), 4)
        for i in range(4): ell(d, 650 + i * 50 + 10 * math.sin(t * 3 + i), 980 - i * 40 - 30 * ((t * .7 + i * .25) % 1), 30, 22, (225, 225, 230), 0)
        char(d, 'NEL', 420, FY, 1.0, eyes='wink' if (t % 1.4) < .5 else 'normal', arm='point', prop='espeto')
        return cam(1.05 + .05 * p, 500, 980)
    if li == 2:
        room(d, (235, 210, 160))
        char(d, 'NEL', 400, FY, 1.05, mouth=m('NEL'), arm='hold', prop='guardanapo', eyes='normal')
        char(d, 'VAL', 800, FY, .9, eyes='normal', arm='down', look=-1)
        return cam(1.0 + .06 * p, 520, 950)
    if li in (3, 4, 5):
        if li == 3: bnd = lambda x: 1080
        elif li == 4: bnd = lambda x: 1080
        else:
            kk = eout(phase(t, S[5], S[5] + 1.5)); bnd = lambda x: 1080 + 260 * kk * (1 - x / W)
        section_bg(d, bnd, 760)
        if li == 3:
            label(d, 260, 900, 'TERRA FOFA', 46, YEL); label(d, 760, 1300, 'SOLO FIRME', 46, WHITE)
            arrow(d, 540, 760 + 300 * eout(p), 540, 1060, RED) if p > .1 else None
        else:
            sink = 0 if li == 4 else 40 * eout(phase(t, S[5] + .8, E[5]))
            for sx, sk in ((250, sink), (830, 0)):
                pillar(d, sx, 560 + sk, 870 + sk)
                poly(d, [(sx - 130, 870 + sk), (sx + 130, 870 + sk), (sx + 90, 820 + sk), (sx - 90, 820 + sk)], (170, 170, 175))
                rect(d, sx - 130, 870 + sk, sx + 130, 920 + sk, (170, 170, 175))
            line(d, [(250, 560 + sink), (830, 560)], OUT, 30); line(d, [(250, 560 + sink), (830, 560)], (200, 200, 205), 18)
            if li == 4: label(d, 540, 1000, 'SAPATA NA PARTE FOFA', 44, YEL)
            if li == 5 and sink > 5: arrow(d, 250, 960, 250, 1040, RED)
        return cam(1.0 + .04 * p, 540, 1000)
    if li == 6:
        ext(d, 1, t=t)
        k = eout(phase(t, S[6], S[6] + 1.2)); wob = 2 * math.sin(t * 9) * (1 - phase(t, S[6], S[6] + 2))
        house(d, 260, GY + 30, 520, 560, ang=7 + 5 * k + wob, pivot=(260, GY), crack=k)
        char(d, 'VAL', 160, FY + 40, .75, eyes='wide', arm='face', arm2='face')
        return cam(1.05, 540, 900, 10 * (phase(t, S[6] + .9, S[6] + 1.6) > 0 and t < S[6] + 1.6))
    if li == 7:
        room(d, (215, 230, 245))
        char(d, 'CID', 560, FY, 1.1, mouth=m('CID'), arm='phone', prop='celular', eyes='normal')
        return cam(1.02 + .08 * p, 560, 950)
    if li == 8:
        ext(d, 1, t=t)
        house(d, 230, GY + 30, 560, 600, ang=10, pivot=(230, GY), crack=eout(p), cr_side=-1)
        arrow(d, 320, 1020, 320, 1150, RED); arrow(d, 760, 1020, 760, 1060, GREEN, 18, 36)
        return cam(1.12 - .08 * p, 520, 860)
    if li == 9 or li == 'cta':
        ext(d, 1, t=t)
        house(d, 160, GY + 30, 440, 470, ang=10, pivot=(160, GY), crack=1, cr_side=-1)
        k = eout(phase(t, S[9] - .2, S[9] + .5))
        char(d, 'BLQ', lerp(1250, 760, k), FY, 1.0, mouth=m('BLQ'), arm='point', eyes='normal', flip=True)
        char(d, 'VAL', 470, FY + 20, .85, eyes='normal' if k > .9 else 'wide', arm='down', look=1)
        return cam(1.0, 540, 980)
    if li == 'pos':
        ext(d, 1, t=t)
        char(d, 'NEL', 540, FY, 1.1, mouth=m('NEL'), eyes='angry', arm='hold', prop='cavadeira')
        char(d, 'BLQ', 930, FY + 30, .65, arm='face', arm2='down', eyes='closed')
        return cam(1.0 + .05 * phase(t, c.S[-1], c.total), 560, 960)

# ======================= EP2 =======================
def spt(d, x, ytop, depth, hammer_y, count):
    line(d, [(x - 150, ytop + 300), (x, ytop), (x + 150, ytop + 300)], (120, 80, 50), 16)
    rect(d, x - 50, ytop + hammer_y, x + 50, ytop + hammer_y + 70, (90, 90, 100))
    line(d, [(x, ytop + 70), (x, ytop + 300 + depth)], OUT, 16); line(d, [(x, ytop + 70), (x, ytop + 300 + depth)], (190, 190, 200), 9)
    label(d, x + 270, ytop + 60, f'GOLPES: {count}', 46, YEL)

def ep2(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    if li == 0:
        ext(d, 2, t=t)
        beat = (t * 2.2) % 1; hy = 20 + 160 * (1 - beat ** .4) if beat < .85 else 180
        cnt = min(30, int(t * 2.2) * 4 + 3)
        spt(d, 480, 760, 120, hy, cnt)
        r = random.Random(int(t * 2.2))
        for i in range(int(t * 2.2) % 4 + 1):
            text_c(d, 480 + r.randint(-300, 300), 880 - r.randint(0, 220), str(r.randint(3, 30)), F(900, 100), YEL, 8)
        char(d, 'VAL', 860, FY, .8, eyes='wide', arm='face', arm2='down', look=-1)
        return cam(1.25 - .08 * p, 520, 1000, 5 * (beat < .1))
    if li == 1:
        ext(d, 2, t=t)
        char(d, 'NEL', 330, FY, 1.0, arm='cross', arm2='cross', eyes='angry')
        char(d, 'VAL', 760, FY, .9, arm='down', eyes='normal', look=-1)
        return cam(1.04 + .05 * p, 540, 960)
    if li == 2:
        section_bg(d, lambda x: 1250, 900)
        char(d, 'NEL', 300, 880, .85, mouth=m('NEL'), arm='point', eyes='normal')
        stake(d, 740, 900 - 40, 230); label(d, 740, 1180, '3 METROS?', 44, YEL)
        return cam(1.02, 540, 960)
    if li in (3, 4):
        def bnd(x): return 1150
        section_bg(d, bnd, 700)
        dep = 150 + 650 * (phase(t, S[3], E[4]))
        beat = (t * 3) % 1
        spt(d, 540, 400, dep, 20 + 160 * (1 - beat ** .4) if beat < .85 else 180, int(phase(t, S[3], E[4]) * 40) + 2)
        if li == 4:
            for i, (n, col) in enumerate([(3, RED), (4, RED), (7, (240, 160, 40)), (12, (240, 200, 40)), (22, GREEN), (30, GREEN)]):
                if p * 6 > i: label(d, 860, 820 + i * 140, f'N = {n}', 44, col)
        return cam(1.0, 540, 1000)
    if li == 5:
        section_bg(d, lambda x: 1150, 700)
        rect(d, 380, 640, 700, 720, (180, 180, 185)); stake(d, 540, 720, 760, 90)
        k = eout(p)
        for yy in range(800, 1440, 110):
            if (yy - 800) / 640 < k * 1.4:
                arrow(d, 440, yy + 60, 440, yy - 10, GREEN, 18, 36); arrow(d, 640, yy + 60, 640, yy - 10, GREEN, 18, 36)
        arrow(d, 540, 1600, 540, 1500, GREEN, 26, 50)
        return cam(1.0 + .04 * p, 540, 1050)
    if li == 6:
        room(d, (230, 220, 245))
        char(d, 'CID', 520, FY, 1.1, mouth=m('CID'), arm='phone', prop='celular')
        return cam(1.03 + .06 * p, 540, 950)
    if li == 7:
        d.rectangle([0, 0, W, H], fill=(245, 240, 225))
        k = eout(p)
        rect(d, 140, 560, 340, 760, (200, 200, 205)); text_c(d, 240, 660, 'CARGA', F(900, 40), RED, 5)
        text_c(d, 420, 660, '÷', F(900, 120), OUT, 0)
        stake(d, 560, 560, 220, 70); text_c(d, 560, 820, 'CADA ESTACA', F(900, 34), GREEN, 5)
        text_c(d, 700, 660, '=', F(900, 120), OUT, 0)
        if k > .4:
            rect(d, 780, 560, 1000, 640, (185, 185, 190)); stake(d, 830, 640, 200, 50); stake(d, 950, 640, 200, 50)
            text_c(d, 890, 900, '2 ESTACAS', F(900, 44), YEL, 6)
        char(d, 'NEL', 300, FY + 60, .85, eyes='wide', arm='face', arm2='face', mouth=.9)
        return cam(1.0, 540, 900)
    if li == 8 or li == 'cta':
        room(d)
        rect(d, 60, 400, 140, 1180, (185, 185, 190)); rect(d, 940, 400, 1020, 1180, (185, 185, 190))
        char(d, 'VAL', 540, FY - 120, 1.0, mouth=m('VAL'), arm='up', arm2='up', eyes='normal')
        return cam(1.0, 540, 900)
    if li == 'pos':
        room(d)
        k = phase(t, c.S[-1], c.S[-1] + 1.5)
        beam(d, 40, 1040, 420, 160 + 80 * k, 30 * k + 6 * math.sin(t * 20) * k)
        char(d, 'NEL', 540, FY, 1.05, mouth=m('NEL'), arm='up', eyes='normal')
        return cam(1.0, 540, 900, 4 * k)

# ======================= EP3 =======================
def ep3(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    def frame_bg():
        room(d); pillar(d, 120, 600, 1180, 90); pillar(d, 960, 600, 1180, 90)
    if li == 0:
        frame_bg(); sag = 90 + 15 * math.sin(t * 6)
        beam(d, 80, 1000, 520, 110, sag, face=True)
        char(d, 'VAL', 540, FY, .75, eyes='wide', arm='up', arm2='up')
        return cam(1.15 - .1 * eout(p), 540, 800)
    if li == 1:
        room(d)
        char(d, 'BLQ', 420, FY, 1.05, arm='hold', prop='cabo', eyes='normal')
        return cam(1.05, 540, 960)
    if li == 2:
        frame_bg(); k = eout(p)
        beam(d, 80, 1000, 520, 110, 90 * k, cracks=k)
        arrow(d, 540, 380, 540, 500, RED)
        return cam(1.05, 540, 820)
    if li == 3:
        frame_bg(); beam(d, 80, 1000, 520, 110, 0)
        cable_in_beam(d, 80, 1000, 520, 110, 0, eout(p))
        char(d, 'BLQ', 540, FY, .8, arm='point', eyes='normal')
        return cam(1.25 - .1 * p, 540, 620)
    if li == 4:
        frame_bg(); k = eout(phase(t, S[4] + .6, E[4]))
        sag = -18 * k
        beam(d, 80, 1000, 520, 110, sag); cable_in_beam(d, 80, 1000, 520, 110, sag)
        rect(d, 1000, 545, 1070, 615, (200, 60, 50))
        for xx in (340, 540, 740): arrow(d, xx, 760, xx, 660, GREEN, 18, 36) if k > .1 else None
        return cam(1.2, 560, 640, 3 * (k > 0 and k < 1))
    if li == 5 or li == 6 or li == 7:
        frame_bg(); beam(d, 80, 1000, 520, 110, -10); cable_in_beam(d, 80, 1000, 520, 110, -10)
        if li == 5:
            k = eout(phase(t, S[5] + .9, S[5] + 1.6))
            char(d, 'VAL', 540, FY, .9, eyes='closed' if k > .5 else 'wide', arm='up', rotdeg=0)
            if k > .5: text_c(d, 640, 920, 'Z Z Z', F(900, 50), WHITE, 6)
        else:
            char(d, 'VAL', 330, FY, .9, mouth=m('VAL'), arm='point', eyes='normal')
            char(d, 'CID', 760, FY, .9, mouth=m('CID'), arm='phone', prop='celular', eyes='normal', flip=True)
        return cam(1.0, 540, 900)
    if li == 8:
        room(d)
        beam(d, 40, 1040, 470, 100, 0)
        for x in range(60, 1040, 50): line(d, [(x, 380), (x + 25, 460), (x + 50, 380)], OUT, 4)
        rect(d, 40, 360, 1040, 380, (190, 190, 195), 5)
        rect(d, 40, 570, 120, 1180, (185, 185, 190)); rect(d, 960, 570, 1040, 1180, (185, 185, 190))
        label(d, 540, 760, 'SEM PILAR NO MEIO', 50, YEL)
        char(d, 'VAL', 380, FY, .85, arm='up', arm2='up'); char(d, 'CID', 700, FY, .85, arm='up', arm2='down')
        return cam(1.05 - .05 * p, 540, 860)
    if li == 9 or li == 'cta':
        room(d); beam(d, 40, 900, 560, 110, -8); cable_in_beam(d, 40, 900, 560, 110, -8)
        line(d, [(900, 615), (1010, 615)], (60, 120, 230), 12)
        poly(d, [(800, 690), (1070, 690), (1070, 830), (800, 830)], (250, 250, 250), 6)
        text_c(d, 935, 760, 'NÃO CORTAR', F(900, 40), RED, 0)
        char(d, 'BLQ', 420, FY, 1.0, mouth=m('BLQ'), arm='point', eyes='normal')
        return cam(1.0, 540, 900)
    if li == 'pos':
        room(d); beam(d, 40, 900, 560, 110, -8); cable_in_beam(d, 40, 900, 560, 110, -8)
        line(d, [(900, 615), (1010, 615)], (60, 120, 230), 12)
        k = eout(phase(t, c.S[-1], c.S[-1] + 1.4))
        char(d, 'NEL', lerp(150, 560, k), FY, 1.0, mouth=m('NEL'), arm='point', prop='makita', eyes='normal', flip=False)
        return cam(1.0 + .12 * k, 640, 850, 3 * (k > .9))

# ======================= EP4 =======================
def ep4(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    def scene_beam(sag=-8, cable=True):
        room(d); beam(d, 40, 900, 560, 110, sag)
        if cable: cable_in_beam(d, 40, 900, 560, 110, sag); line(d, [(900, 615), (1010, 615)], (60, 120, 230), 12)
    if li == 0:
        scene_beam()
        char(d, 'NEL', 820, FY, 1.0, arm='point', prop='makita', flip=True, eyes='wide')
        k = phase(t, S[0], S[0] + 1.6)
        bx = lerp(150, 560, eout(k)); by = FY - 260 * math.sin(math.pi * k)
        char(d, 'BLQ', bx, by, 1.0, mouth=m('BLQ'), arm='up', arm2='up', eyes='wide')
        r = random.Random(int(t * 30))
        for i in range(8): ell(d, 900 + r.randint(-40, 40), 640 + r.randint(-40, 40), 7, 7, YEL, 0)
        return cam(1.1, 640, 860)
    if li == 1:
        scene_beam()
        char(d, 'NEL', 820, FY, 1.0, arm='point', prop='makita', flip=True, eyes='wide')
        char(d, 'BLQ', 560, FY - 220, 1.0, arm='up', arm2='up', eyes='wide')
        for i in range(8): ell(d, 900 + (i * 13) % 40 - 20, 640 + (i * 29) % 60 - 30, 7, 7, YEL, 0)
        rect(d, 60, 300, 130, 420, WHITE, 5); rect(d, 160, 300, 230, 420, WHITE, 5)
        return cam(1.4, 880, 700)
    if li == 2:
        room(d); char(d, 'NEL', 540, FY, 1.15, mouth=m('NEL'), arm='down', prop='makita', eyes='roll')
        return cam(1.05, 540, 950)
    if li == 3:
        d.rectangle([0, 0, W, H], fill=(200, 200, 205))
        rect(d, 0, 700, W, 1100, (180, 180, 185), 0)
        rect(d, 0, 840, W, 960, (40, 40, 45), 7)
        rect(d, 0, 860, W, 940, (220, 180, 60), 0)
        off = (t * 300) % 120
        for x in range(-120, W + 120, 120):
            line(d, [(x + off, 880), (x + off + 60, 920)], (60, 120, 230), 14)
        line(d, [(0, 900), (W, 900)], (60, 120, 230), 10)
        label(d, 300, 760, 'CAPA', 44, WHITE); label(d, 760, 1040, 'GRAXA', 44, YEL)
        return cam(1.0, 540, 900)
    if li == 4:
        scene_beam(); g = .5 + .5 * math.sin(t * 8)
        for x in (40, 900):
            ell(d, x, 615, 50 + 15 * g, 50 + 15 * g, (255, 230, 80), 6)
        label(d, 470, 820, 'SÓ AS PONTAS SEGURAM', 44, YEL)
        return cam(1.0, 520, 760)
    if li == 5:
        k = eout(phase(t, S[5] + .2, S[5] + 1.4))
        room(d); beam(d, 40, 1040, 560, 110, 90 * k, face=k > .5)
        if k < .3: cable_in_beam(d, 40, 1040, 560, 110, 0)
        else:
            r = random.Random(4)
            line(d, [(540, 640), (560 + 300 * k, 460 - 200 * k)], (60, 120, 230), 12)
        return cam(1.05, 540, 800, 12 * (k > 0 and k < .6))
    if li == 6:
        room(d)
        char(d, 'CID', 300, FY, .9, mouth=m('CID'), arm='point', look=1)
        char(d, 'NEL', 640, FY, .9, prop='makita', arm='hold', eyes='normal', look=-1)
        char(d, 'VAL', 900, FY, .8, eyes='normal', look=-1)
        return cam(1.0, 600, 950)
    if li == 7:
        scene_beam(); k = phase(t, S[7], S[7] + 1.0)
        char(d, 'NEL', 820, FY, 1.0, arm='point', eyes='wide', flip=True)
        char(d, 'BLQ', lerp(150, 560, eout(k)), FY - 250 * math.sin(math.pi * k), 1.0, arm='up', arm2='up', eyes='angry')
        mx, my = 900 + 500 * eout(k), 700 - 600 * eout(k)
        ell(d, mx, my, 55, 55, (200, 200, 205), 5); rect(d, mx - 120, my - 25, mx - 30, my + 25, (30, 140, 150), 5)
        return cam(1.0, 600, 900)
    if li == 8 or li == 'cta':
        ext(d, 4, night=False, t=t); d.rectangle([0, 0, W, GY], fill=(120, 140, 170)); ground(d, GY)
        nelsao_house(d, 860, GY + 5, 4, .38)
        char(d, 'VAL', 420, FY, 1.0, mouth=m('VAL'), arm='face', eyes='closed')
        rain_fx(d, t, .6 * phase(t, S[8], S[8] + 1.5) + .1)
        return cam(1.0, 540, 950)
    if li == 'pos':
        sky(d, True, 0, GY); ground(d, GY, (60, 110, 60), (110, 55, 35))
        k = .5 + .5 * math.sin(t * 5)
        wall_blocks(d, 300, GY + 20, 480, 520, bulge=-30 - 40 * k, rows=9, cols=4)
        rain_fx(d, t, 1.2)
        return cam(1.05 + .1 * phase(t, c.S[-1], c.total), 540, 900)

# ======================= EP5 =======================
def ep5(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    def sect(water=0.0, ang=0, bulge=0, night=True):
        sky(d, night, 0, H)
        # soil behind wall (right side)
        wx = 380; gl = 640
        poly(d, [(wx + 90, gl), (W, gl), (W, 1500), (wx + 90, 1500)], (160, 90, 55), 0)
        if water > 0:
            wl = 1500 - (1500 - gl) * water
            d.rectangle([wx + 90, wl, W, 1500], fill=(80, 140, 210))
        d.rectangle([0, 1500, W, H], fill=(120, 65, 40)); line(d, [(0, 1500), (W, 1500)], OUT, 7)
        wall_blocks(d, wx, 1500, 90, 860, ang=ang, bulge=bulge, pivot=(wx, 1500), rows=12, cols=1)
    if li == 0:
        k = .5 + .5 * math.sin(t * 5)
        sky(d, True, 0, GY); ground(d, GY, (60, 110, 60), (110, 55, 35))
        wall_blocks(d, 300, GY + 20, 480, 520, bulge=-30 - 45 * k, rows=9, cols=4)
        rain_fx(d, t, 1.2)
        return cam(1.15 - .08 * p, 540, 900)
    if li == 1:
        sect(.0)
        for i, s in enumerate(['FASE 1', 'FASE 2', 'FASE 3']):
            label(d, 260 + i * 280, 420, s, 44, YEL if p * 3 > i else (120, 120, 130))
        return cam(1.0, 540, 900)
    if li == 2:
        sect(.0)
        char(d, 'NEL', 220, 1500, .7, mouth=m('NEL'), arm='point', eyes='normal', flip=False)
        label(d, 700, 520, 'SEM FERRO', 46, RED)
        return cam(1.0, 540, 1000)
    if li == 3:
        sect(.0)
        for yy in (900, 1100, 1300): arrow(d, 760, yy, 500 + (yy - 900) * .05, yy, RED, 16 + (yy - 900) / 40, 40)
        label(d, 760, 520, 'FASE 1: TERRA', 44, YEL)
        return cam(1.0, 540, 1000)
    if li == 4:
        sect(.6 * eout(p)); rain_fx(d, t, 1.0)
        label(d, 760, 520, 'FASE 2: ÁGUA PRESA', 44, LBLUE)
        return cam(1.0, 540, 1000)
    if li == 5:
        k = eout(phase(t, S[5], S[5] + 1.5)); sect(.6, bulge=-15 * k)
        poly(d, [(470, 640 + 40), (470, 1500), (470 + 380 * k, 1500)], (90, 165, 240), 6)
        for yy in (900, 1100, 1300): arrow(d, 860, yy, 500, yy, RED, 14, 36)
        return cam(1.0, 540, 1050, 4 * (k < 1))
    if li == 6:
        room(d, (60, 70, 110))
        rect(d, 560, 380, 1000, 900, (40, 50, 90), 7);
        sky(d, True, 385, 895) if False else None
        wall_blocks(d, 640, 880, 320, 260, bulge=-35, rows=5, cols=3)
        char(d, 'CID', 320, FY, 1.0, mouth=m('CID'), arm='point', eyes='normal')
        return cam(1.0, 560, 900)
    if li == 7:
        k = eout(phase(t, S[7] + .3, E[7] + .2)) ** 1.6
        sect(.6, ang=-70 * k, bulge=-15)
        char(d, 'NEL', lerp(240, -200, k), 1500, .7, eyes='wide', arm='up', arm2='up')
        return cam(1.0, 540, 1050, 16 * (k > .85 and k < 1))
    if li == 8 or li == 'cta':
        sky(d, False, 0, H); wx = 380
        poly(d, [(wx + 90, 640), (W, 640), (W, 1500), (wx + 90, 1500)], (160, 90, 55), 0)
        k = p if li == 8 else 1
        if k > .1: poly(d, [(wx + 90, 700), (wx + 220, 700), (wx + 220, 1500), (wx + 90, 1500)], (170, 170, 170), 4)
        if k > .3:
            r = random.Random(2)
            for i in range(60): ell(d, wx + 100 + r.randint(0, 110), 720 + r.randint(0, 760), 10, 8, (130, 130, 135), 2)
        if k > .45: line(d, [(wx + 225, 700), (wx + 225, 1500)], (240, 240, 245), 10)
        d.rectangle([0, 1500, W, H], fill=(120, 65, 40)); line(d, [(0, 1500), (W, 1500)], OUT, 7)
        rect(d, wx - 60, 1440, wx + 260, 1500, (185, 185, 190))
        rect(d, wx, 640, wx + 90, 1440, (185, 185, 190))
        if k > .6:
            for yy in range(760, 1440, 160): rect(d, wx - 30, yy, wx + 100, yy + 22, (60, 120, 200), 4)
        if k > .8:
            line(d, [(wx + 30, 660), (wx + 30, 1470), (wx + 230, 1470)], (220, 120, 40), 10)
        return cam(1.0, 540, 1050)
    if li == 'pos':
        sky(d, False, 0, GY); ground(d, GY)
        d.ellipse([200, GY - 40, 880, GY + 200], fill=(110, 60, 40), outline=OUT, width=7)
        char(d, 'NEL', 540, GY + 120, 1.0, mouth=m('NEL'), arm='up', arm2='up', prop='boia', eyes='normal')
        return cam(1.0, 540, 950)

# ======================= EP6 =======================
def pool(d, inward=0.0, water=0.0, concrete=False, y0=640, y1=1380, x0=200, x1=880):
    d.rectangle([0, 0, W, H], fill=(150, 200, 245)); d.rectangle([0, y0 - 40, W, H], fill=(160, 90, 55))
    d.rectangle([0, y0 - 60, W, y0 - 40], fill=(95, 175, 70)); line(d, [(0, y0 - 40), (W, y0 - 40)], OUT, 7)
    inner = [(x0, y0 - 40)] + [(x0 + inward * math.sin(math.pi * (y - y0 + 40) / (y1 - y0 + 40)), y) for y in range(y0 - 40, y1, 30)] + [(x0, y1), (x1, y1)] + \
            [(x1 - inward * math.sin(math.pi * (y - y0 + 40) / (y1 - y0 + 40)), y) for y in range(y1, y0 - 40, -30)] + [(x1, y0 - 40)]
    poly(d, inner, (230, 240, 250), 0)
    if water > 0:
        wl = y1 - (y1 - y0) * water
        d.rectangle([x0 + 10, wl, x1 - 10, y1], fill=(80, 160, 230))
    col = (185, 185, 190) if concrete else (200, 140, 110)
    for side in (-1, 1):
        xs = x0 if side < 0 else x1
        pts = [(xs + side * -inward * math.sin(math.pi * (y - y0 + 40) / (y1 - y0 + 40)) * (-1 if side < 0 else 1), y) for y in range(y0 - 40, y1 + 1, 30)]
        pts = [(xs + (inward * math.sin(math.pi * (y - y0 + 40) / (y1 - y0 + 40)) if side < 0 else -inward * math.sin(math.pi * (y - y0 + 40) / (y1 - y0 + 40))), y) for y in range(y0 - 40, y1 + 1, 30)]
        outer = [(x + side * 60, y) for x, y in pts]
        poly(d, pts + outer[::-1], col, 6)
    rect(d, x0 - 60, y1, x1 + 60, y1 + 60, col, 6)

def ep6(li, t, c, d, img):
    S, E, m = c.S, c.E, c.m
    p = phase(t, S[li], E[li]) if isinstance(li, int) else 1
    if li == 0:
        k = .5 + .5 * math.sin(t * 6); pool(d, inward=40 + 40 * k)
        for yy in (800, 1000, 1200): arrow(d, 60, yy, 170, yy, RED, 16, 36); arrow(d, 1020, yy, 910, yy, RED, 16, 36)
        return cam(1.12 - .06 * p, 540, 1000)
    if li == 1:
        ext(d, 6, t=t, nel=False); scoreboard(d, 0, 5, 560)
        char(d, 'VAL', 380, FY, .9, eyes='normal'); char(d, 'BLQ', 720, FY, .9, eyes='normal', flip=True)
        return cam(1.0, 540, 950)
    if li == 2:
        pool(d, 0)
        char(d, 'NEL', 540, 1300, .8, mouth=m('NEL'), arm='point', eyes='normal')
        return cam(1.0, 540, 1000)
    if li == 3:
        k = eout(p); pool(d, inward=-45 * k, water=.85)
        for yy in (800, 1000, 1200): arrow(d, 300, yy, 180 + 40, yy, BLUE, 16, 36); arrow(d, 780, yy, 860, yy, BLUE, 16, 36)
        return cam(1.0, 540, 1000)
    if li == 4:
        k = eout(p); pool(d, inward=45 * k, water=.85 * (1 - k))
        for yy in (800, 1000, 1200): arrow(d, 40, yy, 150, yy, RED, 16, 36); arrow(d, 1040, yy, 930, yy, RED, 16, 36)
        return cam(1.0, 540, 1000)
    if li == 5:
        k = math.sin(t * 7); pool(d, inward=45 * k, water=.4)
        return cam(1.05, 540, 1000, 3)
    if li == 6:
        ext(d, 6, t=t, nel=False)
        char(d, 'CID', 540, FY, 1.15, mouth=m('CID'), arm='cross', arm2='cross', eyes='normal')
        return cam(1.05 + .05 * p, 540, 950)
    if li == 7:
        k = p; pool(d, 0, concrete=True)
        for x in (200, 880):
            for i in range(int(6 * clamp(k * 1.5))):
                rect(d, x - 22 + (0 if x == 200 else -38) + 10, 640 + i * 120, x + 22 + (0 if x == 200 else -38) + 10, 640 + i * 120 + 90, (210, 210, 215), 3)
        if k > .4:
            for x in (215, 905):
                line(d, [(x, 600), (x, 1420)], (220, 120, 40), 10)
        if k > .7: rect(d, 120, 560, 960, 620, (175, 175, 180), 6)
        return cam(1.0, 540, 1000)
    if li == 8 or li == 'cta':
        pool(d, 0, water=.8, concrete=True)
        char(d, 'VAL', 380, 980, .7, mouth=m('VAL'), arm='up', arm2='up')
        char(d, 'CID', 700, 980, .7, arm='up', eyes='normal')
        char(d, 'BLQ', 960, 640, .6, arm='point', eyes='normal', flip=True)
        k = phase(t, S[8], S[8] + 2)
        rect(d, 80, 540 + 300 * k, 170, 600 + 300 * k, (250, 230, 120), 4)
        return cam(1.0, 540, 900)
    if li == 'pos':
        T0 = c.S[-1]; k = phase(t, T0, c.E[-1] + .3)
        if t < c.E[-1] + .2:
            room(d, (200, 190, 170))
            char(d, 'NEL', 540, FY, 1.1, mouth=m('NEL'), arm='phone', prop='telefone', eyes='normal')
            return cam(1.1, 540, 900)
        ext(d, 6, t=t, nel=False)
        q = eout(phase(t, c.E[-1] + .2, c.E[-1] + 1.4))
        house(d, 250, GY + 20, 520, 560, ang=6 * q, pivot=(250, GY), col=(205, 230, 200), roof=(90, 110, 160), crack=1, cr_side=-1)
        return cam(1.15 - .1 * q, 520, 880, 6 * (q < 1))

SHOTS = {1: ep1, 2: ep2, 3: ep3, 4: ep4, 5: ep5, 6: ep6}
