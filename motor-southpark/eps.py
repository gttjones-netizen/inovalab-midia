from render import *

FY = 1340; GY = 1160

def phase(t, a, b): return clamp((t - a) / max(1e-3, b - a))

def ext(d, ep, night=False, nel=True, rain=0, t=0):
    sky(d, night, 0, GY)
    if not night:
        cloud(d, 200 + 20 * math.sin(t * .3), 330); cloud(d, 820, 450, .8)
    else:
        for i in range(25):
            r = random.Random(i); d.ellipse([r.randint(0, W) - 3, r.randint(250, 900) - 3, r.randint(0, W) + 3, 0], fill=None) if False else None
        ell(d, 860, 380, 60, 60, (240, 240, 210), 5)
    ground(d, GY)
    if nel: nelsao_house(d, 860, GY + 5, ep, .38)

def rain_fx(d, t, k=1.0, col=(170, 200, 255)):
    r = random.Random(int(t * 30))
    for i in range(int(90 * k)):
        x = r.randint(0, W); y = r.randint(0, H)
        d.line([(x, y), (x - 10, y + 40)], fill=col, width=4)

def section_bg(d, boundary=None, y0=760):
    sky(d, False, 0, y0); soil_section(d, y0, H, boundary)

def room(d, wall=(240, 228, 205)):
    d.rectangle([0, 0, W, H], fill=wall)
    d.rectangle([0, 1180, W, H], fill=(190, 150, 110)); d.line([(0, 1180), (W, 1180)], fill=OUT, width=7)

def beam(d, x0, x1, y, h, sag, col=(185, 185, 190), face=False, cracks=0, ow=7, t=0):
    n = 30; top = []; bot = []
    for i in range(n + 1):
        u = i / n; x = lerp(x0, x1, u); dy = sag * math.sin(math.pi * u)
        top.append((x, y + dy)); bot.append((x, y + h + dy))
    poly(d, top + bot[::-1], col, ow)
    if face and sag > 8:
        cx = (x0 + x1) / 2; cy = y + h / 2 + sag
        ell(d, cx - 80, cy - 25, 22, 26, WHITE, 5); ell(d, cx + 80, cy - 25, 22, 26, WHITE, 5)
        ell(d, cx - 80, cy - 22, 8, 8, OUT, 0); ell(d, cx + 80, cy - 22, 8, 8, OUT, 0)
        d.arc([cx - 90, cy - 40, cx + 90, cy + 40], 20, 160, fill=OUT, width=8)
    if cracks > 0:
        for i in range(int(7 * cracks)):
            u = .25 + .5 * i / 6; x = lerp(x0, x1, u); yb = y + h + sag * math.sin(math.pi * u)
            line(d, [(x, yb), (x + 6, yb - h * .3), (x - 4, yb - h * .55)], OUT, 6)
    return top, bot

def cable_in_beam(d, x0, x1, y, h, sag, k=1.0, col=(60, 120, 230), w=12):
    pts = []
    for i in range(31):
        u = i / 30; x = lerp(x0 + 20, x1 - 20, u)
        pts.append((x, y + sag * math.sin(math.pi * u) + h * (0.28 + 0.5 * math.sin(math.pi * u))))
    m = max(2, int(len(pts) * k))
    line(d, pts[:m], OUT, w + 8); line(d, pts[:m], col, w)

def pillar(d, x, y0, y1, w=70, col=(185, 185, 190)):
    rect(d, x - w / 2, y0, x + w / 2, y1, col)

def stake(d, x, ytop, L, w=56, col=(170, 170, 175)):
    rect(d, x - w / 2, ytop, x + w / 2, ytop + L, col, 6)

def wall_blocks(d, x, ybase, w, h, ang=0, bulge=0, pivot=None, col=(200, 200, 205), rows=10, cols=3):
    pv = pivot or (x + w, ybase)
    for r in range(rows):
        for c in range(cols):
            off = (r % 2) * w / cols / 2
            bx0 = x + c * w / cols - (off if c > 0 else 0); bx1 = bx0 + w / cols
            by1 = ybase - r * h / rows; by0 = by1 - h / rows
            u = (r + .5) / rows; b = bulge * math.sin(math.pi * u)
            pts = [(bx0 + b, by0), (bx1 + b, by0), (bx1 + b, by1), (bx0 + b, by1)]
            poly(d, rot(pts, ang, *pv), col, 5)

def water_tri(d, x, ytop, ybot, k, col=(70, 150, 235, 255)):
    hgt = ybot - ytop; L = 320 * k
    poly(d, [(x, ytop), (x, ybot), (x + L, ybot)], (90, 165, 240), 5)

def scoreboard(d, a, b, y=330):
    label(d, W / 2, y, f'CUNHADO {a}  ×  {b} BLOQUINHO', 46, YEL)

# ---------------- generic overlays ----------------
def tarja(img, d, t, style, dur, title, sub):
    if t > dur + .6: return
    k_in = eout(t / .35); k_out = ease((t - dur) / .4) if t > dur else 0
    fT = F(900, 62 if len(title) < 22 else 52); fS = F(700, 34)
    def band(cx, cy, bw=980, bh=170, ang=0, alpha=215, stripes=False):
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        g.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], 18, fill=(10, 12, 16, alpha))
        if stripes:
            for i in range(-30, 30):
                x = cx - bw / 2 + i * 40
                g.polygon([(x, cy - bh / 2 - 26), (x + 20, cy - bh / 2 - 26), (x + 34, cy - bh / 2), (x + 14, cy - bh / 2)], fill=YEL)
                g.polygon([(x, cy + bh / 2), (x + 20, cy + bh / 2), (x + 34, cy + bh / 2 + 26), (x + 14, cy + bh / 2 + 26)], fill=YEL)
        g.text((cx, cy - 26), title, font=fT, fill=YEL, anchor='mm')
        g.text((cx, cy + 40), sub, font=fS, fill=WHITE, anchor='mm')
        if ang: L = L.rotate(ang, center=(cx, cy), resample=Image.BICUBIC)
        img.alpha_composite(L)
    if style == 'A':
        band(W / 2, lerp(-120, 340, k_in) - 500 * k_out)
    elif style == 'B':
        n = int(len(title) * clamp(t / .9)); tt = title[:n]
        if k_out < 1:
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
            s = 1 - k_out
            g.rounded_rectangle([W / 2 - 490 * s, 380 - 85 * s, W / 2 + 490 * s, 380 + 85 * s], 18, fill=(10, 12, 16, 215))
            if s > .5:
                g.text((W / 2, 354), tt, font=fT, fill=YEL, anchor='mm'); g.text((W / 2, 420), sub, font=fS, fill=WHITE, anchor='mm')
            img.alpha_composite(L)
    elif style == 'C':
        y = 360 if t > .3 else lerp(-200, 360, (t / .3) ** 2)
        if t > .3 and t < .55: y = 360 - 40 * math.sin((t - .3) / .25 * math.pi)
        if k_out > 0:
            r = random.Random(1)
            for i in range(30):
                px = r.randint(100, 980) + r.uniform(-1, 1) * 300 * k_out; py = 360 + r.uniform(-80, 80) + 900 * k_out ** 2
                d.rectangle([px - 18, py - 18, px + 18, py + 18], fill=(10, 12, 16), outline=YEL, width=3)
        else: band(W / 2, y)
    elif style == 'D':
        x = lerp(-700, W / 2, k_in) + 1400 * k_out
        band(x, 360, 1150, 160, 8, stripes=True)
    elif style == 'E':
        y = lerp(-150, 330, k_in) + 1500 * k_out ** 2
        band(W / 2, y, 860, 170, -3 + 10 * k_out)
    elif style == 'F':
        s = lerp(2.5, 1.0, eout(t / .18))
        if k_out < 1:
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); band_img = L
            g = ImageDraw.Draw(L)
            bw, bh = 940 * s, 170 * s
            g.rounded_rectangle([W / 2 - bw / 2, 360 - bh / 2, W / 2 + bw / 2, 360 + bh / 2], 18, fill=(10, 12, 16, int(215 * (1 - k_out))))
            g.text((W / 2, 360 - 26 * s), title, font=F(900, max(10, int(fT.size * s))), fill=YEL + (int(255 * (1 - k_out)),), anchor='mm')
            g.text((W / 2, 360 + 40 * s), sub, font=F(700, max(10, int(34 * s))), fill=(255, 255, 255, int(255 * (1 - k_out))), anchor='mm')
            L = L.rotate(-4, center=(W / 2, 360), resample=Image.BICUBIC); img.alpha_composite(L)
    elif style == 'G':
        glitch = t < .3 or (t > dur and t < dur + .4)
        if t > dur + .4: return
        off = random.Random(int(t * 30)).randint(-25, 25) if glitch else 0
        band(W / 2 + off, 360)
        if glitch:
            for i in range(6):
                y = random.Random(int(t * 30) + i).randint(250, 480)
                d.rectangle([0, y, W, y + 6], fill=(255, 255, 255))

def reveal(d, t, t0, big, sub, col=YEL, y=820):
    if t < t0 or t > t0 + 2.6: return
    k = t - t0; s = .4 + .6 * eout(k / .18) + .12 * math.sin(min(1, k / .3) * math.pi) * (k < .3)
    a = 1 if k < 2.3 else 1 - (k - 2.3) / .3
    if a <= 0: return
    f = F(900, int(210 * s)); text_c(d, W / 2, y, big, f, col, 12)
    if k > .2: text_c(d, W / 2, y + 150, sub, F(800, 54), WHITE, 7)

def cta(d, t, t0, who, y=1470):
    if t < t0: return
    k = eout((t - t0) / .2); s = .7 + .3 * k
    f1 = F(900, int(88 * s)); f2 = F(900, int(64 * s))
    text_c(d, W / 2, y - 50, 'MANDA', f1, YEL, 9)
    text_c(d, W / 2, y + 40, who, f2, WHITE, 8)

def credits(d, t, tc, ep, title):
    k = t - tc
    d.rectangle([0, 0, W, H], fill=(8, 8, 12))
    items = [('A OBRA DO SEU VALDIR', 900, 70, YEL), (f'EPISÓDIO {ep}/6', 800, 50, WHITE), (title, 800, 44, WHITE), ('', 700, 30, WHITE),
             ('ELENCO', 800, 40, YEL), ('SEU VALDIR', 700, 38, WHITE), ('NELSÃO, O CUNHADO', 700, 38, WHITE), ('DONA CIDA', 700, 38, WHITE), ('BLOQUINHO', 700, 38, WHITE),
             ('', 700, 30, WHITE), ('NENHUMA ESTRUTURA FOI FERIDA', 700, 32, (170, 170, 180)), ('(QUASE)', 700, 32, (170, 170, 180))]
    y = 1500 - 520 * k
    for s, w, sz, c in items:
        if s: d.text((W / 2, y), s, font=F(w, sz), fill=c, anchor='mm')
        y += sz + 34

def postlabel(d, t, t0, ep):
    if t < t0: return
    label(d, W / 2, 330, 'CENA PÓS-CRÉDITOS', 40, YEL)

def nextlabel(d, t, t0, ep):
    if t < t0: return
    k = eout((t - t0) / .25)
    if ep < 6:
        text_c(d, W / 2, 1520, f'EP {ep + 1} AMANHÃ · 19H', F(900, int(80 * (.6 + .4 * k))), YEL, 9)
    else:
        text_c(d, W / 2, 1520, 'FIM?', F(900, int(150 * (.6 + .4 * k))), YEL, 12)
