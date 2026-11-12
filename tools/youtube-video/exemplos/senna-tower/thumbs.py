from scenes import *
def finish(a, texts, name, crop=(0, 0)):
    x0, y0 = crop
    im = Image.fromarray(a[y0:y0 + 144, x0:x0 + 256]).resize((1280, 720), Image.NEAREST).convert("RGBA")
    d = ImageDraw.Draw(im)
    for s, x, y, size, col, anchor in texts:
        f = font(900, size); d.text((x, y), s, font=f, fill=col, anchor=anchor, stroke_width=max(6, size // 9), stroke_fill=BLK)
    im.convert("RGB").save(name, quality=93)
def shift(a, n):
    b = blank(); sky(b); b[n:] = a[:-n]; return b
# 1 — 60 CM?!
a = blank(); cut(a, 90, 190, sea=False)
for x in PXS(9, 196, 268): box(a, x, 96, x + 3, 204, PILE)
tex(a, CONC, 188, 91, 280, 102); skytower(a, 234, 91, 91, 54, crown=False)
bloquinho(a, 120, 90, eyes="wide", pose="point", scale=2)
finish(a, [("60 CM?!", 40, 480, 160, YEL, "lm"), ("544 m", 40, 630, 100, WHITE, "lm")], "thumb1.jpg", (40, 20))
# 2 — NÃO AFUNDA?
a = blank(); cut(a, 90, 180, sea=False)
skytower(a, 236, 91, 91, 44, crown=False); tex(a, CONC, 200, 91, 272, 99)
arrow(a, 236, 104, 236, 178, RED, 5)
bloquinho(a, 110, 90, eyes="sweat", pose="shrug", scale=2)
finish(a, [("NÃO", 40, 450, 150, YEL, "lm"), ("AFUNDA?", 40, 610, 130, YEL, "lm")], "thumb2.jpg", (40, 20))
# 3 — 1.600 t DE GELO
a = blank(); blockbg(a, 1.0); heat(a, 0.9)
icecubes(a, 3.1, 0, 110, 300, 6, 60, 40, seed=9); icecubes(a, 1.7, 0, 110, 300, 6, 60, 30, seed=4)
a = shift(a, 26)
bloquinho(a, 56, 86, eyes="wide", pose="up", scale=2)
finish(a, [("1.600 t", 330, 530, 150, YEL, "lm"), ("DE GELO", 330, 660, 100, (190, 228, 250), "lm")], "thumb3.jpg", (30, 0))
print("ok")
