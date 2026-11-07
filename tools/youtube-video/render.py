import sys, subprocess
from scenes import *

TOTAL = TL["total"]
LOGO = Image.open("logo_icon.png").convert("RGBA"); LOGO = LOGO.resize((int(LOGO.width * 64 / LOGO.height), 64), Image.LANCZOS)

def locate(T):
    for i, k in enumerate(CH):
        o = OFF(k)
        nxt = OFF(CH[i + 1]) if i + 1 < len(CH) else TOTAL + 10
        if T < nxt - 1.2 or i + 1 == len(CH):
            return k, T - o, False
        if nxt - 1.2 <= T < nxt:
            return CH[i + 1], T - nxt, True
    return CH[-1], T - OFF(CH[-1]), False

def draw_labels(fr, c, t):
    d = ImageDraw.Draw(fr)
    for item in c.labels:
        if item[0] == "__clock__":
            _, cx, cy, r, a, lab = item
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 250, 250), outline=BLK, width=10)
            d.line([cx, cy, cx + r * 0.8 * math.sin(a), cy - r * 0.8 * math.cos(a)], fill=BLK, width=8)
            d.line([cx, cy, cx + r * 0.5 * math.sin(a / 12), cy - r * 0.5 * math.cos(a / 12)], fill=RED, width=10)
            if lab:
                f = font(900, 56); w = f.getlength(lab)
                d.text((cx - w / 2, cy + r + 20), lab, font=f, fill=YEL, stroke_width=6, stroke_fill=BLK)
            continue
        text, x, y, size, col, w, sw, box, anchor = item
        f = font(w, size)
        tw = f.getlength(text)
        if tw > 1820:
            f = font(w, size * 1820 / tw); tw = f.getlength(text)
        if box:
            bb = d.textbbox((x, y), text, font=f, anchor=anchor)
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([bb[0] - 26, bb[1] - 16, bb[2] + 26, bb[3] + 16], 18, fill=box)
            fr.alpha_composite(ov); d = ImageDraw.Draw(fr)
            d.text((x, y), text, font=f, fill=col, anchor=anchor)
        else:
            d.text((x, y), text, font=f, fill=col, anchor=anchor, stroke_width=sw, stroke_fill=BLK)

def render_frame(T):
    k, t, gap = locate(T)
    c = Ctx()
    img = blank()
    if gap:
        img[:] = (18, 20, 26)
    else:
        SCENES[k](img, c, t)
    cx, cy, z = c.cam
    left = cx - LW / 2 / z; top = cy - LH / 2 / z
    left = min(max(left, 0), LW - LW / z); top = min(max(top, 0), LH - LH / z)
    pil = Image.fromarray(img).resize((W, H), Image.NEAREST, box=(left, top, left + LW / z, top + LH / z))
    if c.shake:
        sx = int(8 * math.sin(T * 61)); sy = int(6 * math.cos(T * 47))
        pil = pil.transform((W, H), Image.AFFINE, (1, 0, -sx, 0, 1, -sy), fillcolor=(0, 0, 0))
    if c.mode == "rewind":
        a = np.array(pil).astype(np.int16); r = random.Random(int(T * 30))
        for _ in range(6):
            y = r.randint(0, H - 30); a[y:y + r.randint(6, 26)] += r.randint(20, 60)
        a[:, :, 0] = np.roll(a[:, :, 0], 6, axis=1); pil = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    fr = pil.convert("RGBA")
    if c.flash == "red":
        fr.alpha_composite(Image.new("RGBA", (W, H), (200, 0, 0, 60)))
    draw_labels(fr, c, t)
    d = ImageDraw.Draw(fr)
    # chapter card
    title = TITLES.get(k, "")
    if title and (gap or t < 2.5):
        a = 1.0 if gap else 1 - clamp((t - 1.8) / 0.7)
        if gap:
            f = font(900, 76); d.text((960, 540), title, font=f, fill=YEL, anchor="mm", stroke_width=6, stroke_fill=BLK)
        else:
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            f = font(800, 34); tw = f.getlength(title)
            od.rounded_rectangle([40, 30, 40 + tw + 50, 96], 14, fill=(10, 12, 16, int(200 * a)))
            od.text((65, 63), title, font=f, fill=YEL + (int(255 * a),), anchor="lm")
            fr.alpha_composite(ov); d = ImageDraw.Draw(fr)
    # watermark (bottom-left)
    wm = LOGO.copy(); al = np.array(wm); al[:, :, 3] = (al[:, :, 3] * 0.85).astype(np.uint8); wm = Image.fromarray(al)
    fr.alpha_composite(wm, (36, H - 100))
    d.text((36 + wm.width + 14, H - 68), "@inovalab_projetos", font=font(800, 30), fill=(230, 235, 245), anchor="lm", stroke_width=3, stroke_fill=BLK)
    return fr.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = [render_frame(x).resize((384, 216)) for x in ts]
        cols = 5; rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (384 * cols, 216 * rows), (40, 40, 40))
        for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 384, (i // cols) * 216))
        sh.save(sys.argv[3] if len(sys.argv) > 3 else "sheet.png"); print("ok")
    else:
        a, b, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
        n0, n1 = int(a * FPS), int(b * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(n0, n1): p.stdin.write(render_frame(i / FPS).tobytes())
        p.stdin.close(); p.wait(); print("done", out)
