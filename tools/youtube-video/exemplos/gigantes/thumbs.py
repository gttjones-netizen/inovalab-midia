from scenes import *
from PIL import ImageEnhance

def finish(a, texts, name, crop=(0, 0), arrows=()):
    x0, y0 = crop
    im = Image.fromarray(a[y0:y0 + 144, x0:x0 + 256]).resize((1280, 720), Image.NEAREST)
    im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.12).convert("RGBA")
    # vinheta escura à esquerda (área do texto)
    g = np.zeros((720, 1280, 4), np.uint8); xs = np.linspace(1, 0, 1280)
    g[..., 3] = (np.clip(xs * 1.6 - 0.35, 0, 1) * 170).astype(np.uint8)[None, :]
    im.alpha_composite(Image.fromarray(g))
    d = ImageDraw.Draw(im)
    for (ax0, ay0, ax1, ay1) in arrows:
        d.line([ax0, ay0, ax1, ay1], fill=BLK, width=30); d.line([ax0, ay0, ax1, ay1], fill=RED, width=18)
        ang = math.atan2(ay1 - ay0, ax1 - ax0)
        pts = [(ax1 + 30 * math.cos(ang), ay1 + 30 * math.sin(ang)), (ax1 + 34 * math.cos(ang + 2.4), ay1 + 34 * math.sin(ang + 2.4)), (ax1 + 34 * math.cos(ang - 2.4), ay1 + 34 * math.sin(ang - 2.4))]
        d.polygon(pts, fill=RED, outline=BLK, width=6)
    for s, x, y, size, col, anchor in texts:
        f = font(900, size); d.text((x, y), s, font=f, fill=col, anchor=anchor, stroke_width=max(8, size // 8), stroke_fill=BLK)
    im.convert("RGB").save(name, quality=94)

# 1 — SEM ROCHA?! 828 m
a = blank(); dubai_cut(a, 84, water=0.6, salt=0.3); sky(a, sunset=0.35, y1=84)
raft_piles(a, 84, 240, 330, 7, 46, w=4)
for x in (254, 314): friction(a, x, 96, 136, 0.3)
burj(a, 285, 84, 80, 40)
bloquinho(a, 205, 84, eyes="wide", pose="point", scale=2)
finish(a, [("SEM", 40, 360, 150, YEL, "lm"), ("ROCHA?!", 40, 510, 150, YEL, "lm"), ("828 m", 1250, 70, 96, WHITE, "rm")],
       "thumb1.jpg", (64, 0), arrows=[(760, 650, 880, 640)])

# 2 — 1 KM DE PRÉDIO
a = blank(); sky(a, sunset=0.55); tex(a, SANDD, 0, 140, LW, LH)
jeddah(a, 250, 142, 142, 56); burj(a, 190, 142, 117, 32)
bloquinho(a, 296, 142, eyes="wide", pose="up")
finish(a, [("1 km", 40, 300, 210, YEL, "lm"), ("DE PRÉDIO", 40, 470, 96, WHITE, "lm")], "thumb2.jpg", (64, 0))

# 3 — 660 t NO CÉU
a = blank((24, 28, 36))
for y in range(4, 150, 18): box(a, 150, y, 330, y + 2, (90, 96, 108))
box(a, 146, 0, 150, LH, (70, 150, 120)); box(a, 330, 0, 334, LH, (70, 150, 120))
ball(a, 240, 78, 48, [(176, 0), (304, 0), (240, 0)])
bloquinho(a, 300, 140, eyes="wide", pose="up", scale=1)
finish(a, [("660 t", 40, 300, 200, YEL, "lm"), ("NO CÉU", 40, 470, 110, WHITE, "lm")], "thumb3.jpg", (76, 0))
print("ok")
