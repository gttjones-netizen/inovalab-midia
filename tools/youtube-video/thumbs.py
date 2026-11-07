from lib import *
TW_, TH_ = 256, 144
def base():
    a = np.zeros((LH, LW, 3), np.uint8); sky(a); return a
def finish(a, texts, name):
    im = Image.fromarray(a[:TH_, :TW_]).resize((1280, 720), Image.NEAREST).convert("RGBA")
    d = ImageDraw.Draw(im)
    for s, x, y, size, col, anchor in texts:
        f = font(900, size)
        d.text((x, y), s, font=f, fill=col, anchor=anchor, stroke_width=max(6, size // 9), stroke_fill=BLK)
    im.convert("RGB").save(name, quality=92)
# 1
a = base(); ground_strip(a, 118)
foundation(a, 175, 120, 12, w=22, d=6)
draw_tower(a, 175, 120, 8, 12, fh=12, tw=30)
bloquinho(a, 222, 120, pose="push", eyes="wide", scale=2)
finish(a, [("ERA PRA", 40, 150, 120, YEL, "lm"), ("TER CAÍDO", 40, 290, 120, YEL, "lm"), ("5,5°", 40, 450, 110, WHITE, "lm")], "thumb1.jpg")
# 2
a = np.zeros((LH, LW, 3), np.uint8); sky(a, y1=46)
soil_section(a, 46, 215, (70, 132), 12, 1, 0, 1.0)
foundation(a, 215, 47 + 5, 7, w=16, d=4); draw_tower(a, 215, 47 + 5, 8, 7, fh=5, tw=16)
arrow(a, 236, 64, 236, 108, RED, 3)
finish(a, [("O PROBLEMA", 40, 140, 104, YEL, "lm"), ("TÁ EMBAIXO", 40, 270, 104, YEL, "lm")], "thumb2.jpg")
# 3
a = base(); a[110:, :] = SANDB[110:, :]
foundation(a, 165, 111, 8, w=18, d=5); draw_tower(a, 165, 111, 8, 8, fh=11, tw=26)
from scenes import building
building(a, 225, 112, 16, 7, w=30)
finish(a, [("PISA NO", 40, 150, 120, YEL, "lm"), ("BRASIL?", 40, 290, 120, YEL, "lm")], "thumb3.jpg")
print("ok")
