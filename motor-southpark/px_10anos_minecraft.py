import sys, functools
sys.path.insert(0, '/home/claude/serie')
from dez import *   # setup, current, counter, check, wt, tarja, reveal, captions...
import dez

P = 5; LW, LH = W // P, H // P   # 216 x 384
FLOOR = 240; FEET = 268
BK = (20, 18, 24)

def noise_rect(d, x0, y0, x1, y1, base, var=12, seed=0, blk=4):
    r = random.Random(seed)
    for y in range(int(y0), int(y1), blk):
        for x in range(int(x0), int(x1), blk):
            v = r.randint(-var, var)
            d.rectangle([x, y, min(x1, x + blk) - 1, min(y1, y + blk) - 1], fill=tuple(max(0, min(255, c + v)) for c in base))

@functools.lru_cache(maxsize=32)
def bg(kind):
    im = Image.new('RGB', (LW, LH)); d = ImageDraw.Draw(im)
    if kind in ('room', 'room2', 'roomP', 'night'):
        wall = {'room': (196, 160, 112), 'room2': (150, 170, 190), 'roomP': (170, 130, 190), 'night': (44, 48, 84)}[kind]
        noise_rect(d, 0, 0, LW, FLOOR, wall, 10, 1)
        for y in range(16, FLOOR, 16): d.line([(0, y), (LW, y)], fill=tuple(max(0, c - 30) for c in wall))
        noise_rect(d, 0, FLOOR, LW, LH, (120, 84, 52) if kind != 'night' else (70, 60, 70), 12, 2)
        d.line([(0, FLOOR), (LW, FLOOR)], fill=BK, width=2)
    elif kind in ('sky', 'dark'):
        if kind == 'sky':
            for y in range(FLOOR):
                k = y / FLOOR; d.line([(0, y), (LW, y)], fill=(int(100 + 60 * k), int(165 + 45 * k), int(235 + 10 * k)))
            for cx, cy, w in [(20, 70, 34), (140, 56, 44), (170, 110, 26)]:
                d.rectangle([cx, cy, cx + w, cy + 5], fill=(245, 248, 252)); d.rectangle([cx + 5, cy - 5, cx + w - 8, cy], fill=(245, 248, 252))
            noise_rect(d, 0, FLOOR, LW, FLOOR + 8, (86, 170, 60), 14, 3)
            noise_rect(d, 0, FLOOR + 8, LW, LH, (120, 84, 52), 12, 4)
        else:
            noise_rect(d, 0, 0, LW, LH, (28, 30, 42), 5, 5)
            noise_rect(d, 0, FLOOR, LW, LH, (50, 50, 60), 6, 6)
    return im

def ptext(d, xy, s, size, fill, anchor='mm', w=900):
    d.fontmode = '1'
    d.text(xy, s, font=F(w, size), fill=fill, anchor=anchor)

# ---------------- people ----------------
SK = (225, 180, 140)
def person(d, who, x, feet, s=2, pose='idle', eyes='normal', mouth=0.0, flip=False, prop=None):
    def R(x0, y0, x1, y1, c):
        if flip: x0, x1 = -x1, -x0
        d.rectangle([x + x0 * s, feet + y0 * s, x + x1 * s - 1, feet + y1 * s - 1], fill=c)
    if who == 'BLQ': pants, shirt, sk = (90, 90, 95), (245, 200, 30), SK
    elif who == 'VAL': pants, shirt, sk = (55, 75, 140), (200, 50, 50), (240, 195, 155)
    else: pants, shirt, sk = (150, 80, 170), (150, 80, 170), (240, 190, 160)
    R(-4, -9, -1, 0, pants); R(1, -9, 4, 0, pants)
    R(-5, -2, -1, 0, (50, 40, 35)); R(1, -2, 5, 0, (50, 40, 35))
    R(-5, -19, 5, -9, shirt)
    if who == 'CID': R(-6, -12, 6, -6, shirt)
    if who == 'BLQ': R(-5, -14, 5, -12, (210, 215, 220))
    if who == 'VAL':
        for xx in (-3, 0, 3): R(xx, -19, xx + 1, -9, (140, 30, 30))
        R(-5, -15, 5, -14, (140, 30, 30))
    if pose == 'up':
        R(-7, -26, -5, -17, shirt); R(5, -26, 7, -17, shirt); R(-7, -28, -5, -26, sk); R(5, -28, 7, -26, sk)
    elif pose == 'point':
        R(5, -18, 13, -15, shirt); R(13, -18, 15, -15, sk); R(-7, -18, -5, -11, shirt); R(-7, -11, -5, -9, sk)
    elif pose == 'phone':
        R(5, -24, 7, -16, shirt); R(5, -26, 7, -24, sk); R(6, -28, 9, -23, (40, 40, 50)); R(-7, -18, -5, -11, shirt); R(-7, -11, -5, -9, sk)
    elif pose == 'hold':
        R(5, -18, 10, -15, shirt); R(10, -18, 12, -15, sk); R(-10, -18, -5, -15, shirt); R(-12, -18, -10, -15, sk)
    elif pose == 'face':
        R(5, -24, 7, -16, shirt); R(5, -26, 7, -24, sk); R(-7, -18, -5, -11, shirt); R(-7, -11, -5, -9, sk)
    else:
        R(-7, -18, -5, -11, shirt); R(5, -18, 7, -11, shirt); R(-7, -11, -5, -9, sk); R(5, -11, 7, -9, sk)
    R(-5, -29, 5, -19, sk)
    if eyes == 'closed':
        R(-4, -25, -1, -24, BK); R(1, -25, 4, -24, BK)
    elif eyes == 'wide':
        R(-4, -27, -1, -23, WHITE); R(1, -27, 4, -23, WHITE); R(-3, -26, -2, -24, BK); R(2, -26, 3, -24, BK)
    elif eyes == 'roll':
        R(-4, -27, -2, -25, WHITE); R(2, -27, 4, -25, WHITE); R(-3, -27, -2, -26, BK); R(3, -27, 4, -26, BK)
    else:
        R(-4, -26, -2, -24, WHITE); R(2, -26, 4, -24, WHITE); R(-3, -26, -2, -25, BK); R(3, -26, 4, -25, BK)
    if who == 'CID':
        R(-5, -27, -1, -26, BK); R(1, -27, 5, -26, BK); R(-1, -26, 1, -25, BK)
    if who == 'VAL': R(-4, -22, 4, -21, (95, 60, 35))
    if mouth > .3 or eyes == 'wide': R(-2, -21, 2, -19, (120, 30, 40))
    else: R(-2, -21, 2, -20, (120, 60, 50))
    if who == 'BLQ':
        R(-6, -32, 6, -29, (245, 130, 30)); R(-4, -34, 4, -32, (245, 130, 30)); R(-7, -30, 7, -29, (220, 105, 10))
    elif who == 'VAL':
        R(-6, -32, 6, -28, (40, 90, 170)); R(5, -30, 10, -28, (40, 90, 170))
    else:
        R(-6, -31, 6, -28, (90, 55, 40)); R(-3, -35, 3, -31, (90, 55, 40)); R(-7, -30, -5, -20, (90, 55, 40)); R(5, -30, 7, -20, (90, 55, 40))

def boletim(d, x, y, s=1.0, big10=True):
    w, h = int(22 * s), int(28 * s)
    d.rectangle([x - w // 2 - 1, y - h // 2 - 1, x + w // 2 + 1, y + h // 2 + 1], fill=BK)
    d.rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], fill=(250, 248, 238))
    for i in range(3): d.line([(x - w // 2 + 3, y - h // 2 + 6 + i * 3), (x + w // 2 - 3, y - h // 2 + 6 + i * 3)], fill=(160, 160, 170))
    if big10: ptext(d, (x, y + h // 4), '10', max(8, int(12 * s)), RED)

def desk(d, t, k):
    wob = int(round(2 * math.sin(t * 15) * (1 - k)))
    d.rectangle([60, 200 + wob, 164, 207 - wob // 2], fill=(140, 90, 50)); d.rectangle([60, 200 + wob, 164, 201 + wob], fill=(170, 115, 70))
    d.rectangle([64, 207 + wob, 69, 244], fill=(110, 70, 40)); d.rectangle([155, 207, 160, 244], fill=(110, 70, 40))
    d.rectangle([80, 190 + wob, 88, 200 + wob], fill=(240, 240, 245)); d.rectangle([80, 190 + wob, 88, 191 + wob], fill=(120, 80, 50))
    if (1 - k) > .3:
        for i in range(3): d.rectangle([90 + 4 * i, 184 - 4 * i + int(2 * math.sin(t * 20 + i)), 92 + 4 * i, 186 - 4 * i + int(2 * math.sin(t * 20 + i))], fill=(120, 80, 50))
    d.rectangle([110, 197 + wob, 140, 200 + wob], fill=WHITE)

def hook(d, t, m=0.0, eyes=None, blq=True):
    k = eout(phase(t, .75, 1.05))
    desk(d, t, k)
    if k >= 1:
        d.rectangle([58, 244, 76, 250], fill=BK); d.rectangle([59, 245, 75, 249], fill=(250, 248, 238)); ptext(d, (67, 247), '10', 7, RED)
    else:
        boletim(d, int(lerp(150, 67, k)), int(lerp(206, 246, k)), lerp(1.0, .4, k), k < .6)
    if blq: person(d, 'BLQ', 180, FEET, 2.6, 'hold' if k < .2 else 'point', eyes or ('closed' if t < .4 else 'wide'), m, flip=True)
    return k

def house(d, x, y, crack=0.0, fixed=False):
    noise_rect(d, x, y - 56, x + 76, y, (235, 215, 160), 8, 9)
    for i in range(12):
        d.rectangle([x - 6 + i * 4, y - 56 - (i if i < 6 else 11 - i) * 3 - 4, x - 6 + i * 4 + 7, y - 56 - (i if i < 6 else 11 - i) * 3 + 2], fill=(190, 60, 50))
    for wx, wy in ((x + 10, y - 46), (x + 50, y - 46), (x + 10, y - 26)):
        d.rectangle([wx - 1, wy - 1, wx + 14, wy + 12], fill=BK); d.rectangle([wx, wy, wx + 13, wy + 11], fill=(130, 200, 240))
    d.rectangle([x + 34, y - 22, x + 44, y], fill=(110, 70, 40))
    if crack > 0 and not fixed:
        pts = [(x + 46, y - 4), (x + 50, y - 14), (x + 47, y - 22), (x + 53, y - 32), (x + 50, y - 40), (x + 56, y - 50)]
        n = max(2, int(len(pts) * crack)); d.line(pts[:n], fill=BK, width=2)

def chalk(d):
    d.rectangle([14, 76, 202, 172], fill=(70, 50, 30)); d.rectangle([18, 80, 198, 168], fill=(40, 85, 65))

# ---------------- shots (logical) ----------------
def shot(li, t, c, d, img, post):
    S, E, m = c.S, c.E, c.m
    if li == 'tail':
        th = t - (c.total - TAIL); img.paste(bg('room')); hook(d, th, 0)
        return (1.18, 560, 1080, 0)
    p = phase(t, S[li], E[li])
    if li in (0, 11):
        img.paste(bg('room'))
        d.rectangle([20, 70, 60, 110], fill=BK); d.rectangle([22, 72, 58, 108], fill=(130, 200, 240))
        if li == 0:
            hook(d, t, m('BLQ'))
            z = 1.18 if t < 1.05 else lerp(1.18, 1.02, eout(phase(t, 1.6, 3.4)))
            return (z, 560, 1080, 9 * (1.05 < t < 1.3))
        hook(d, (t - S[11]) * .3, m('BLQ'), eyes='normal')
        return (lerp(1.02, 1.18, eout(p)), 560, 1080, 0)
    if li == 1:
        img.paste(bg('sky'))
        noise_rect(d, 30, 140, 190, FLOOR, (170, 70, 50), 14, 11)
        for i in range(20): d.rectangle([24 + i * 9, 136 - min(i, 19 - i) * 3, 33 + i * 9, 140], fill=(140, 50, 40))
        for wx in (40, 70, 130, 160):
            for wy in (160, 196):
                d.rectangle([wx, wy, wx + 14, wy + 16], fill=BK); d.rectangle([wx + 1, wy + 1, wx + 13, wy + 15], fill=(130, 200, 240))
        d.rectangle([98, 206, 120, FLOOR], fill=(100, 60, 35))
        d.rectangle([66, 144, 150, 156], fill=(50, 25, 20)); ptext(d, (108, 150), 'FACULDADE', 9, WHITE)
        person(d, 'BLQ', 176, FEET, 2.6, 'up', 'normal', m('BLQ'), flip=True)
        return (1.0 + .05 * p, 540, 960, 0)
    if li == 2:
        ts = wt(c, 2, 'NENHUM') - .15
        if t < ts:
            img.paste(bg('night'))
            d.rectangle([150, 60, 190, 100], fill=BK); d.rectangle([152, 62, 188, 98], fill=(20, 24, 60)); d.rectangle([174, 70, 182, 78], fill=(240, 240, 210))
            d.rectangle([20, 210, 200, 216], fill=(120, 80, 50))
            n = 3 + int(phase(t, S[2], ts) * 16)
            for i in range(n):
                col = [(200, 60, 60), (60, 120, 200), (60, 170, 90), (220, 180, 50)][i % 4]
                d.rectangle([30 + (i % 2) * 2, 210 - (i + 1) * 7, 66 + (i % 2) * 2, 209 - i * 7], fill=col)
            d.rectangle([150, 190, 152, 210], fill=BK); d.rectangle([140, 184, 160, 190], fill=(240, 200, 60))
            person(d, 'BLQ', 112, FEET, 2.6, 'face', 'closed' if (t * 2) % 2 < .6 else 'roll')
            for i in range(2): ptext(d, (140 + i * 8, 140 - i * 10 - int(6 * ((t * .8 + i * .5) % 1))), 'z', 10 + 2 * i, WHITE)
            return (1.04 + .05 * phase(t, S[2], ts), 540, 960, 0)
        img.paste(bg('room2'))
        k = eout(phase(t, ts, ts + .3))
        person(d, 'VAL', 156, FEET + 4, 2.6, 'phone', 'normal', 0, flip=True)
        person(d, 'BLQ', 60, FEET, 2.6, 'up', 'normal', m('BLQ'))
        boletim(d, 80, int(lerp(230, 150, k)), 1.1)
        return (1.05, 540, 1000, 0)
    if li == 3:
        img.paste(bg('room2'))
        person(d, 'BLQ', 54, FEET, 2.6, 'hold', 'closed')
        boletim(d, 78, 210 + int(8 * eout(p)), .8)
        person(d, 'VAL', 150, FEET + 2, 2.3, 'point', 'roll', m('VAL'), flip=True)
        return (1.08 + .06 * p, 640, 950, 0)
    if li == 4:
        img.paste(bg('room'))
        d.rectangle([50, 82, 166, 160], fill=(160, 110, 50)); d.rectangle([56, 88, 160, 154], fill=(250, 246, 228))
        ptext(d, (108, 102), 'DIPLOMA', 12, BK); ptext(d, (108, 118), 'ENG. CIVIL', 8, (90, 90, 100))
        d.rectangle([140, 136, 150, 146], fill=YEL)
        k = eout(phase(p, .35, 1.0))
        if k > 0:
            cx, cy = 160, 86; Rr = 46 * k
            for a in range(0, 100, 18):
                ar = math.radians(90 + a); d.line([(cx, cy), (cx + Rr * math.cos(ar), cy + Rr * math.sin(ar))], fill=(250, 250, 250))
            for r in (.35, .65, 1.0):
                d.line([(cx + Rr * r * math.cos(math.radians(90 + a)), cy + Rr * r * math.sin(math.radians(90 + a))) for a in range(0, 100, 18)], fill=(250, 250, 250))
            d.rectangle([cx - 14 * k, cy + 14 + int(6 * math.sin(t * 3)), cx - 11 * k, cy + 17 + int(6 * math.sin(t * 3))], fill=BK)
        sad = p > .55
        person(d, 'BLQ', 108, FEET + 6, 1.8, 'down' if sad else 'up', 'closed' if sad else 'normal', m('BLQ'))
        if .2 < p < .55:
            d.rectangle([40, 164, 176, 178], fill=(40, 120, 60)); ptext(d, (108, 171), 'UNIVERSIDADE BOA', 8, WHITE)
        return (1.0 + .06 * p, 540, 860, 0)
    if li == 5:
        tq = wt(c, 5, 'MAS') - .1
        img.paste(bg('dark'))
        if t < tq:
            yr = 2016 + min(10, int((t - S[5]) / .12))
            d.rectangle([80, 236, 136, 252], fill=(240, 240, 245)); ptext(d, (108, 244), str(yr), 11, BK)
            person(d, 'BLQ', 170, FEET + 10, 1.6, 'point', 'wide', m('BLQ'), flip=True)
            return (1.0, 540, 960, 7 * (0 < t - c.rt < .25))
        d.rectangle([18, 92, 86, 176], fill=BK); d.rectangle([20, 94, 84, 174], fill=(250, 248, 238))
        ptext(d, (52, 104), 'PROVA', 9, BK)
        for i in range(5): d.line([(26, 118 + i * 10), (78, 118 + i * 10)], fill=(160, 160, 170))
        d.line([(20, 94), (84, 174)], fill=RED, width=4); d.line([(84, 94), (20, 174)], fill=RED, width=4)
        d.rectangle([108, 90, 196, 180], fill=(12, 12, 16)); d.rectangle([108, 90, 196, 92], fill=(70, 70, 80))
        ptext(d, (152, 132 + int(2 * math.sin(t * 6))), '?', 56, YEL)
        d.rectangle([142, 168, 162, 184], fill=(230, 180, 40)); d.rectangle([146, 162, 158, 168], fill=(200, 200, 205)); d.rectangle([149, 165, 155, 168], fill=(12, 12, 16))
        person(d, 'BLQ', 40, FEET + 10, 1.6, 'point', 'normal', m('BLQ'))
        return (1.0 + .08 * phase(t, tq, E[5]), 680, 760, 0)
    if li == 6:
        img.paste(bg('room')); chalk(d)
        if t < c.sol6 + .1:
            ls = ['Md = 1,4 x 42', 'As = Md/(0,87 fyd d)', 'x/d < 0,45', 'Asw/s > 0,2 fct']
            for i, s in enumerate(ls): ptext(d, (26, 92 + i * 18), s, 9, (235, 240, 230), 'lm', 800)
            sleep = t < c.stamp6
            person(d, 'VAL', 166, FEET + 4, 2.6, 'idle', 'closed' if sleep else 'normal', 0, flip=True)
            if sleep:
                for i in range(2): ptext(d, (186 + i * 8, 180 - i * 10 - int(6 * ((t + i * .5) % 1))), 'z', 10 + 2 * i, WHITE)
            person(d, 'BLQ', 50, FEET, 2.6, 'point', 'normal', m('BLQ'))
            if t > c.stamp6:
                post.append(('stamp', c.stamp6, (560, 720), 'CALCULADO', GREEN, 6))
        else:
            k = eout((t - c.sol6 - .1) / .3)
            house(d, 70, 166)
            if k > 0: post.append(('check', 760, 560, 80 * k))
            person(d, 'VAL', 166, FEET + 4, 2.6, 'up', 'wide', .8, flip=True)
            person(d, 'BLQ', 50, FEET, 2.6, 'point', 'normal', m('BLQ'))
            post.append(('label', 540, 1000, 'SOLUÇÃO'))
        return (1.03 + .04 * p, 540, 900, 8 * (0 < t - c.stamp6 < .2))
    if li == 7:
        img.paste(bg('roomP'))
        d.rectangle([20, 70, 60, 110], fill=BK); d.rectangle([22, 72, 58, 108], fill=(130, 200, 240))
        person(d, 'CID', 104, FEET, 2.5, 'phone', 'normal', m('CID'))
        person(d, 'VAL', 186, FEET + 8, 1.5, 'idle', 'normal', 0, flip=True)
        if p > .25: post.append(('label', 300, 700, 'SOBRINHO (ENG.)'))
        return (1.03 + .07 * p, 540, 950, 0)
    if li in (8, 9):
        img.paste(bg('sky')); house(d, 70, FLOOR + 2, crack=1)
        if li == 8:
            person(d, 'BLQ', 50, FEET, 2.6, 'face', 'normal', m('BLQ'))
            person(d, 'VAL', 166, FEET + 4, 2.6, 'up', 'normal', 0, flip=True)
            if p > .1: post.append(('label', 540, 470, 'PARTE HUMANA'))
            tc = wt(c, 8, 'TODO') - .1
            if t > tc: return (lerp(1.0, 1.15, eout(phase(t, tc, E[8]))), 760, 1000, 0)
            return (1.0, 540, 960, 0)
        person(d, 'BLQ', 40, FEET + 12, 1.5, 'idle', 'normal', 0)
        person(d, 'VAL', 148, FEET + 8, 2.6, 'hold', 'wide', m('VAL'), flip=True)
        return (lerp(1.12, 1.24, eout(p)), 720, 980, 0)
    if li == 10:
        img.paste(bg('sky'))
        fixed = t > c.res
        house(d, 70, FLOOR + 2, crack=1, fixed=fixed)
        k = phase(t, S[10] + .2, S[10] + 1.2)
        if k < 1: boletim(d, int(lerp(56, -40, k)), int(lerp(190, 60, k)), .9)
        person(d, 'BLQ', 50, FEET, 2.6, 'up' if fixed else 'point', 'normal', m('BLQ'))
        person(d, 'VAL', 168, FEET + 4, 2.6, 'up' if fixed else 'idle', 'wide' if fixed else 'normal', .8 if fixed else 0, flip=True)
        post.append(('list',))
        if fixed: post.append(('stamp', c.res, (705, 900), 'RESOLVIDO', GREEN, -7))
        return (1.0, 540, 960, 12 * (0 < t - c.res < .25))

def stamp(img, t, t0, xy, txt, col, ang):
    k2 = eout((t - t0) / .18); s = lerp(2.2, 1.0, k2)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L); x, y = xy
    g.rectangle([x - 240 * s, y - 62 * s, x + 240 * s, y + 62 * s], outline=col, width=int(12 * s), fill=(255, 255, 255, 210))
    g.text((x, y), txt, font=F(900, int(68 * s)), fill=col, anchor='mm')
    L = L.rotate(ang, center=xy, resample=Image.NEAREST); img.alpha_composite(L)

def pixlabel(d, x, y, s, size=46, fill=WHITE, bgc=(20, 20, 26)):
    f = F(900, size); bb = d.textbbox((x, y), s, font=f, anchor='mm')
    d.rectangle([bb[0] - 20, bb[1] - 14, bb[2] + 20, bb[3] + 14], fill=bgc, outline=BK, width=6)
    d.text((x, y), s, font=f, fill=fill, anchor='mm')

def frame(c, t, overlays=True):
    lo = Image.new('RGB', (LW, LH)); d = ImageDraw.Draw(lo)
    li = current(c, t)
    fi = int((t + TH / FPS) * FPS)
    c.m = lambda who: float(c.envs[who][fi]) if fi < c.nf else 0
    post = []
    z, cx, cy, sh = shot(li, t, c, d, lo, post)
    if sh:
        r = random.Random(int(t * 60)); cx += r.uniform(-sh, sh) * 2; cy += r.uniform(-sh, sh) * 2
    z = max(z, 1.0); cw, chh = LW / z, LH / z
    x0 = clamp(cx / P - cw / 2, 0, LW - cw); y0 = clamp(cy / P - chh / 2, 0, LH - chh)
    img = lo.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.NEAREST).convert('RGBA')
    d = ImageDraw.Draw(img)
    for it in post:
        if it[0] == 'stamp': stamp(img, t, it[1], it[2], it[3], it[4], it[5]); d = ImageDraw.Draw(img)
        elif it[0] == 'check': check(d, it[1], it[2], it[3])
        elif it[0] == 'label': pixlabel(d, it[1], it[2], it[3], 46, YEL if it[3] in ('PARTE HUMANA', 'SOLUÇÃO') else WHITE, (20, 20, 26) if it[3] != 'SOBRINHO (ENG.)' else (40, 120, 60))
        elif it[0] == 'list':
            labs = ['OUVIR', 'EXPLICAR SIMPLES', 'CUMPRIR O COMBINADO']
            for i, tt in enumerate(c.tick):
                if t >= tt - .05:
                    kk = eout((t - tt + .05) / .2); y = 430 + i * 110
                    d.rectangle([80, y - 44, 80 + 800 * kk, y + 44], fill=(20, 20, 26), outline=BK, width=6)
                    if kk > .6: check(d, 130, y + 4, 30); d.text((180, y), labs[i], font=F(900, 48), fill=WHITE, anchor='lm')
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

THUMB2 = ['MEU BOLETIM', 'VIROU CALÇO']
def capa(c):
    lo = Image.new('RGB', (LW, LH)); d = ImageDraw.Draw(lo)
    lo.paste(bg('room')); desk(d, 2.0, 1)
    # calço gigante
    d.rectangle([52, 240, 82, 252], fill=BK); d.rectangle([53, 241, 81, 251], fill=(250, 248, 238)); ptext(d, (67, 246), '10', 10, RED)
    z = 1.5; cw, chh = LW / z, LH / z; x0, y0 = 20, 250 - chh * .78
    img = lo.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.NEAREST)
    img = ImageEnhance.Brightness(img).enhance(.85).convert('RGBA')
    vig = Image.new('L', (W, H), 0); g = ImageDraw.Draw(vig)
    g.ellipse([-300, -200, W + 300, H + 200], fill=255); vig = vig.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(img, Image.new('RGBA', (W, H), (0, 0, 0, 255)), vig)
    # Bloquinho grande, olhos arregalados (desenhado em lógico e ampliado)
    B = Image.new('RGBA', (90, 90), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
    person(bd, 'BLQ', 45, 86, 2.4, 'point', 'wide', 1.0, flip=True)
    B = B.resize((90 * 7, 90 * 7), Image.NEAREST); img.alpha_composite(B, (520, 1100))
    d = ImageDraw.Draw(img)
    arrow(d, 600, 1420, 380, 1330, RED, 34, 70)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    sz = 140
    while max(g.textlength(s, font=F(900, sz)) for s in THUMB2) > 980: sz -= 4
    g.rectangle([0, 760 - sz * 1.3, W, 760 + sz * 1.3], fill=(10, 12, 16, 235))
    g.text((W / 2, 760 - sz * .6), THUMB2[0], font=F(900, sz), fill=YEL, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    g.text((W / 2, 760 + sz * .62), THUMB2[1], font=F(900, sz), fill=WHITE, stroke_width=11, stroke_fill=(0, 0, 0), anchor='mm')
    L = L.rotate(-4, center=(W / 2, 760), resample=Image.BICUBIC); img.alpha_composite(L)
    return img.convert('RGB')

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
    sfxp = '/home/claude/serie/out/sfx2.wav'; aud = '/home/claude/serie/out/aud2.wav'
    write_sfx(c.ev, c.total, sfxp)
    build_audio(1, [(KEYS[(1, i)], c.S[i]) for i in range(len(c.S))], c.total, music, sfxp, aud)
    cp = capa(c); cp.save(capa_out)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', aud, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                          '-af', 'volume=1.55,alimiter=limit=0.95', '-t', str(c.nf / FPS), '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(c.nf):
        im = cp if f < TH else frame(c, (f - TH) / FPS)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return c

if __name__ == '__main__':
    import secrets
    if sys.argv[1] == 'sheet':
        c = setup(sys.argv[2], float(sys.argv[3]))
        ts = [0.1, 0.9, 1.5, 2.6, 5.0] + [c.S[i] + min(1.5, (c.E[i] - c.S[i]) * .6) for i in range(2, 11)] + [c.S[2] + .6, c.rt + .4, c.stamp6 + .1, c.sol6 + .4, c.res + .2, c.ctat + .5, c.S[11] + .5, c.total - .3]
        sheet(c, ts, '/home/claude/serie/out/sheet2.png')
