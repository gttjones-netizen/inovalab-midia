import subprocess, os
from PIL import ImageFont

S = "/tmp/claude-0/-home-claude/b1d88ea1-414d-5945-967c-51579a6665d9/scratchpad/reel"
os.makedirs(S, exist_ok=True)
V1 = "/root/.claude/uploads/b1d88ea1-414d-5945-967c-51579a6665d9/5be60b93-escada.mp4"
V2 = "/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Reels/5/modelagem escada plissada.mp4"
NARR = "/root/.claude/uploads/b1d88ea1-414d-5945-967c-51579a6665d9/81c6b9a8-New_tts_node.mp3"
MUS = "/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Músicas/ES_Red Red Sea - Ava Low.mp3"
F9 = "/tmp/cal/Montserrat-900.ttf"; F8 = "/tmp/cal/Montserrat-800.ttf"; F7 = "/tmp/cal/Montserrat-700.ttf"
DUR = 15.4
YEL = "0xF2C14E"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); raise SystemExit(1)

# ---------- 1. segmentos de vídeo (1080x1920) ----------
# (fonte, inicio_fonte, duracao_saida, velocidade, crop, zoom: 'punch'|'in'|None)
C1 = "crop=1252:939:334:70"
C2 = "crop=1021:766:30:222"
segs = [
    (V1, 0.0, 3.0, 1.5, C1, "punch"),
    (V2, 18.6, 3.6, 1.0, C2, "in"),
    (V2, 28.0, 3.3, 1.0, C2, "in"),
    (V1, 13.0, 3.1, 2.0, C1, None),
    (V1, 0.0, 2.4, 1.0, C1, None),
]
parts = []
for i, (src, ss, d, sp, crop, zoom) in enumerate(segs):
    src_len = d * sp + 0.1
    if zoom == "punch":
        z = "if(lt(t,0.4),1.2-0.2*t/0.4,1)"
    elif zoom == "in":
        z = f"1+0.22*t/{d}"
    else:
        z = "1"
    fg = (f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30,{crop},scale=1080:810,"
          f"scale=w='trunc(1080*({z})/2)*2':h='trunc(810*({z})/2)*2':eval=frame,"
          f"crop=1080:810,eq=contrast=1.05,unsharp=5:5:0.6[fg];")
    bg = (f"[0:v]setpts=(PTS-STARTPTS)/{sp},fps=30,{crop},scale=-2:1920,crop=1080:1920,"
          f"boxblur=28:3,eq=brightness=-0.48:saturation=0.75[bg];")
    fc = fg + bg + "[bg][fg]overlay=0:555,format=yuv420p[v]"
    out = f"{S}/seg{i}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(src_len), "-i", src,
         "-filter_complex", fc, "-map", "[v]", "-t", str(d), "-an",
         "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
    parts.append(out)

with open(f"{S}/list.txt", "w") as f:
    for p in parts: f.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{S}/list.txt",
     "-c", "copy", f"{S}/base.mp4"])

# ---------- 2. legendas (Hormozi, palavra-chave amarela) ----------
OFF = 0.15
speech = [  # (inicio, fim, [(chunk, sílabas, palavras_amarelas)])
    (0.00, 2.06, [("QUANTO AÇO", 4, {"AÇO"}), ("VAI NUMA ESCADA", 6, set()), ("PLISSADA?", 3, {"PLISSADA?"})]),
    (3.08, 6.00, [("ARMAÇÃO COM", 4, set()), ("ESTRIBOS PARA", 5, {"ESTRIBOS"}),
                  ("COMBATER O", 4, set()), ("EMPUXO NO VAZIO", 6, {"EMPUXO", "VAZIO"})]),
    (6.94, 9.20, [("TUDO RESOLVIDO", 6, set()), ("NO MODELO,", 4, {"MODELO,"}), ("ANTES DA OBRA.", 5, {"OBRA."})]),
    (10.25, 12.18, [("APENAS", 3, set()), (None, 7, set()), ("DE AÇO.", 3, {"AÇO."})]),
    (13.17, 14.44, [("VOCÊ TINHA", 4, set()), ("CHUTADO", 3, set()), ("QUANTO?", 2, {"QUANTO?"})]),
]
SIZE = 74
font = ImageFont.truetype(F9, SIZE)
space = font.getlength(" ")
CAP_Y = 1250
draw = []
counter_start = None
for si, (a, b, chunks) in enumerate(speech):
    a += OFF; b += OFF
    total = sum(c[1] for c in chunks)
    t = a
    times = []
    for c in chunks:
        dt = (b - a) * c[1] / total
        times.append((t, t + dt)); t += dt
    nxt = speech[si + 1][0] + OFF if si + 1 < len(speech) else DUR
    for ci, (c, (ta, tb)) in enumerate(zip(chunks, times)):
        text = c[0]
        if text is None:
            counter_start = ta; continue
        end = times[ci + 1][0] if ci + 1 < len(chunks) else min(b + 0.45, nxt)
        if chunks[ci + 1:ci + 2] and chunks[ci + 1][0] is None:
            end = ta + 0.5
        words = text.split(" ")
        widths = [font.getlength(w) for w in words]
        lw = sum(widths) + space * (len(words) - 1)
        assert lw <= 780, (text, lw)
        x = (1080 - lw) / 2
        for w, wd in zip(words, widths):
            col = YEL if w in c[2] else "white"
            safe = w.replace("'", "’").replace(":", "\\:").replace(",", "\\,")
            draw.append(
                f"drawtext=fontfile={F9}:text='{safe}':fontsize={SIZE}:fontcolor={col}:"
                f"borderw=7:bordercolor=black@0.85:shadowx=0:shadowy=6:shadowcolor=black@0.55:"
                f"x={x:.0f}:y='{CAP_Y}+14*max(0\\,1-(t-{ta:.3f})/0.10)':"
                f"alpha='min(1\\,(t-{ta:.3f})/0.06)':enable='between(t\\,{ta:.3f}\\,{end:.3f})'")
            x += wd + space

# ---------- 3. etiqueta fixa no topo ----------
draw.insert(0, f"drawtext=fontfile={F9}:text='ESCADA PLISSADA':fontsize=50:fontcolor={YEL}:"
               f"x=(w-text_w)/2:y=392:shadowx=0:shadowy=4:shadowcolor=black@0.55")
draw.insert(1, f"drawtext=fontfile={F7}:text='UMUARAMA-PR  ·  DETALHADA EM BIM':fontsize=32:fontcolor=white:"
               f"x=(w-text_w)/2:y=458:shadowx=0:shadowy=3:shadowcolor=black@0.55")

# ---------- 4. contador 0 → 85 kg ----------
c0 = counter_start
c1 = c0 + 1.0
cend = 13.0
with open(f"{S}/counter.txt", "w") as f:
    f.write(f"%{{eif:floor(85*pow(clip((t-{c0:.3f})/1.0\\,0\\,1)\\,0.6)):d}}")
draw.append(f"drawbox=x=0:y=555:w=1080:h=810:color=black@0.55:t=fill:enable='between(t\\,{c0-0.15:.3f}\\,{cend})'")
draw.append(f"drawtext=fontfile={F9}:textfile={S}/counter.txt:expansion=normal:fontsize=230:fontcolor={YEL}:"
            f"x=(w-text_w)/2-60:y=800:shadowx=0:shadowy=8:shadowcolor=black@0.6:enable='between(t\\,{c0:.3f}\\,{cend})'")
draw.append(f"drawtext=fontfile={F9}:text='KG':fontsize=110:fontcolor={YEL}:"
            f"x=(w)/2+120:y=905:shadowx=0:shadowy=6:shadowcolor=black@0.6:enable='between(t\\,{c0:.3f}\\,{cend})'")
draw.append(f"drawtext=fontfile={F8}:text='18 barras Ø8 · 12 m cada':fontsize=46:fontcolor=white:"
            f"x=(w-text_w)/2:y=1070:alpha='min(1\\,max(0\\,(t-{c1:.3f})/0.15))':"
            f"shadowx=0:shadowy=4:shadowcolor=black@0.6:enable='between(t\\,{c1:.3f}\\,{cend})'")

with open(f"{S}/vf.txt", "w") as f:
    f.write(",".join(draw))

# ---------- 5. efeitos sonoros ----------
cuts = [3.0, 6.6, 9.9, 13.0]
run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anoisesrc=c=pink:d=0.35:a=0.6:r=44100",
     "-af", "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.15,volume=0.30",
     "-ac", "2", f"{S}/woosh.wav"])
run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=1100:d=0.07:r=44100",
     "-af", "afade=t=out:st=0.02:d=0.05,volume=0.45", "-ac", "2", f"{S}/pop.wav"])
sfx = [("woosh", c - 0.2) for c in cuts] + [("pop", 0.0), ("pop", c1)]

# ---------- 6. render final ----------
inputs = ["-i", f"{S}/base.mp4", "-i", NARR, "-ss", "18.8", "-i", MUS]
fa = []
for k, (name, at) in enumerate(sfx):
    inputs += ["-i", f"{S}/{name}.wav"]
    fa.append(f"[{3+k}:a]adelay={int(at*1000)}|{int(at*1000)}[s{k}]")
fc = (f"[0:v]{open(f'{S}/vf.txt').read()},format=yuv420p[v];"
      f"[1:a]aresample=44100,aformat=channel_layouts=stereo,adelay={int(OFF*1000)}|{int(OFF*1000)},volume=1.35,asplit=2[nar][key];"
      f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.55[mus0];"
      f"[mus0][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[mus];"
      + ";".join(fa) + ";"
      f"[nar][mus]" + "".join(f"[s{k}]" for k in range(len(sfx))) +
      f"amix=inputs={2+len(sfx)}:normalize=0:duration=longest,"
      f"atrim=0:{DUR},afade=t=out:st={DUR-0.6}:d=0.6,alimiter=limit=0.95[a]")
run(["ffmpeg", "-v", "error", "-y"] + inputs +
    ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(DUR),
     "-r", "30", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{S}/reels-22-10-26.mp4"])
print("ok", counter_start)
