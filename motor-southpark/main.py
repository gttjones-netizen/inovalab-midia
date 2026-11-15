import sys
from ep_shots import *

CFG = {
 1: dict(rev=(6, 'TORTO', 'TORTO', 'UM LADO DESCE, O OUTRO NÃO', YEL), cta='PRA QUEM TÁ CONSTRUINDO', blq=[9],
         keys=['AFUND', 'TORTO', 'FOFA', 'FOFO', 'FIRME', 'SAPATA', 'DIAGONAL', 'SONDAGEM', 'RASG', 'ESTACA', 'CONTA'], water=[],
         gaps={6: .1, 9: .3}, thumb_t=1.9),
 2: dict(rev=(5, 'ATRITO', 'ATRITO', 'A ESTACA SEGURA PELOS LADOS', YEL), cta='PRA QUEM COMPROU TERRENO', blq=[],
         keys=['FUROU', 'ESTACA', 'GOLPES', 'SONDAGEM', 'FRACO', 'SEGURA', 'PONTA', 'ATRITO', 'CARGA', 'PILAR', 'BLOCO', 'CONTA', 'VIGA'], water=[],
         gaps={}, thumb_t=1.0),
 3: dict(rev=(5, 'QUINZE', '15 tf', 'POR CORDOALHA', YEL), cta='PRA QUEM QUER SALA SEM PILAR', blq=[9],
         keys=['SORRINDO', 'PÉSSIMO', 'RETA', 'CABO', 'CURVA', 'MACACO', 'CORDOALHA', '15', 'QUINZE', 'TONELADAS', 'PILAR', 'PERIGO', 'CORTAR'], water=[],
         gaps={}, thumb_t=1.0),
 4: dict(rev=(5, 'INTEIRA', 'INTEIRA', 'A VIGA PERDE A FORÇA TODA', YEL), cta='PRO PARENTE DA MAKITA', blq=[0],
         keys=['PARA', 'CABO', 'ENGRAXADO', 'CAPA', 'PONTAS', 'INTEIRA', 'VIGA', 'MAKITA', 'MURO', 'NELSÃO'], water=[],
         gaps={1: .25}, thumb_t=.9),
 5: dict(rev=(5, 'DOBRO', '2×', 'ÁGUA PRESA × TERRA', LBLUE), cta='PRO VIZINHO DO MURO BARRIGUDO', blq=[],
         keys=['RESPIRANDO', 'FASE', 'TOMBA', 'DRENO', 'BRITA', 'MANTA', 'ARMADO', 'BARRIGUDO', 'FERRO', 'PISCINA', 'TERRA', 'DOBRO'], water=['ÁGUA', 'CHUVA'],
         gaps={7: .2}, thumb_t=1.2),
 6: dict(rev=(5, 'DOIS', '2 LADOS', 'CHEIA E VAZIA', YEL), cta='PRO CUNHADO QUE ENTENDE DE OBRA', blq=[],
         keys=['VAZIA', 'ESMAGADAS', 'CUNHADO', 'BLOCO', 'LADOS', 'CONCRETO', 'PILAR', 'VIGA', 'FERRO', 'CASA'], water=['ÁGUA', 'CHEIA'],
         gaps={}, thumb_t=1.1),
}

def word_time(ep, li, S, prefix):
    k = KEYS[(ep, li)]
    for w in CL[k]['words']:
        if re.sub(r'[^A-ZÀ-Ü]', '', w['w'].upper()).startswith(prefix): return S[li] + w['s']
    return S[li] + .5

def setup(ep, tarja_style, tarja_dur, music):
    cfg = CFG[ep]
    S, E, items, tc, total = timeline(ep, cfg['gaps'])
    n = len(S); nf = int((total + TH / FPS) * FPS) + 1
    # envelopes
    envs = {k: np.zeros(nf) for k in ['N', 'NEL', 'VAL', 'CID', 'BLQ']}
    for li, (k, t0) in enumerate(items):
        sp = k.split('_')[0]
        if sp == 'N' and li in cfg['blq']: sp = 'BLQ'
        e = envelope(f'/home/claude/serie/clips/{k}.wav', int(CL[k]['dur'] * FPS) + 2)
        f0 = int((t0 + TH / FPS) * FPS)
        for i, v in enumerate(e):
            if f0 + i < nf: envs[sp][f0 + i] = v
    for k in envs:
        mx = np.percentile(envs[k][envs[k] > 0], 90) if (envs[k] > 0).any() else 1
        envs[k] = np.clip(envs[k] / (mx + 1e-9), 0, 1)
    # caption words
    words = []
    for li, (k, t0) in enumerate(items):
        for w in CL[k]['words']:
            words.append(dict(w=w['w'], s=t0 + w['s'], e=t0 + w['e']))
    blocks = build_blocks(words)
    rli, rpref, rbig, rsub, rcol = cfg['rev']
    rt = word_time(ep, rli, S, rpref)
    c = Ctx(); c.S, c.E, c.tc, c.total, c.nf = S, E, tc, total, nf
    c.blocks, c.rt, c.envs = blocks, rt, envs
    c.tarja = (tarja_style, tarja_dur); c.music = music
    # sfx
    ev = [(0.0, 'pop')]
    for i in range(1, n): ev.append((S[i] - .18, 'whoosh'))
    ev += [(rt - .75, 'riser'), (rt, 'pop'), (E[n - 2] + .2, 'pop'), (tc, 'sting')]
    st = {'A': 'whoosh', 'B': 'blip', 'C': 'thud', 'D': 'whoosh', 'E': 'thud', 'F': 'stamp', 'G': 'vhs'}[tarja_style]
    ev.append((0.02, st))
    if tarja_style == 'B': ev += [(i * .07, 'blip') for i in range(12)]
    if ep == 1: ev += [(0, 'alarm'), (1.4, 'thud'), (rt + .1, 'crack'), (S[8] + .3, 'crack'), (S[8] + 1.2, 'crack')]
    if ep == 2:
        ev += [(i / 2.2, 'hammer') for i in range(int(E[0] * 2.2) + 1)]
        ev += [(S[3] + i / 3, 'hammer') for i in range(int((E[4] - S[3]) * 3))]
    if ep == 3: ev += [(0, 'boing'), (S[5] + 1.0, 'thud')]
    if ep == 4: ev += [(0, 'saw', 1.0), (S[5] + .3, 'crack'), (S[5] + .5, 'boing'), (S[7] + .5, 'thud'), (S[8] + .5, 'rain', total - S[8])]
    if ep == 5: ev += [(0, 'rain', E[0] + .5), (S[4], 'rain', E[4] - S[4]), (S[4] + .5, 'gulp'), (S[7] + 1.0, 'thud'), (S[7] + 1.1, 'crack')]
    if ep == 6: ev += [(0, 'boing'), (S[8] + 1.2, 'gulp'), (E[-1] + .3, 'crack'), (E[-1] + .4, 'thud')]
    ev.append((S[-1] - .3, 'whoosh'))
    c.ev = ev
    return c

def current(c, t):
    n = len(c.S)
    if t >= c.S[-1] - .3: return 'pos'
    if t >= c.tc: return 'cred'
    if t >= c.E[n - 2] + .1: return 'cta'
    li = 0
    for i in range(n - 1):
        if t >= c.S[i] - .12: li = i
    return li

def frame(ep, c, t, overlays=True):
    img = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(img)
    li = current(c, t)
    fi = int((t + TH / FPS) * FPS)
    c.m = lambda who: float(c.envs[who][fi]) if fi < c.nf else 0
    if li == 'cred':
        credits(d, t, c.tc, ep, EPS[ep]['title'])
        return img.convert('RGB')
    z, cx, cy, sh = SHOTS[ep](li, t, c, d, img)
    if sh:
        r = random.Random(int(t * 60)); cx += r.uniform(-sh, sh) / z * 2; cy += r.uniform(-sh, sh) / z * 2
    if abs(z - 1) > .005 or abs(cx - W / 2) > 1 or abs(cy - H / 2) > 1:
        z = max(z, 1.0); cw, chh = W / z, H / z
        x0 = clamp(cx - cw / 2, 0, W - cw); y0 = clamp(cy - chh / 2, 0, H - chh)
        img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((W, H), Image.BILINEAR)
    d = ImageDraw.Draw(img)
    # cut flash
    n = len(c.S)
    for i in list(range(1, n)):
        if 0 <= t - c.S[i] + .12 < .06: d.rectangle([0, 0, W, H], fill=(255, 255, 255))
    if not overlays: return img.convert('RGB')
    cfg = CFG[ep]
    rshow = c.rt <= t <= c.rt + 2.6
    hide_cap = rshow or (c.E[n - 2] + .1 < t < c.S[-1]) or t > c.E[-1] + .4
    if not hide_cap: draw_caption(d, c.blocks, t, cfg['keys'], cfg['water'])
    rli, rpref, rbig, rsub, rcol = cfg['rev']
    reveal(d, t, c.rt, rbig, rsub, rcol)
    if li == 'cta': cta_fit(d, t, c.E[n - 2] + .2, cfg['cta'])
    if li == 'pos':
        postlabel(d, t, c.S[-1] - .3, ep); nextlabel(d, t, c.E[-1] + .45, ep)
    tarja(img, d, t, c.tarja[0], c.tarja[1], EPS[ep]['title'], f'A OBRA DO SEU VALDIR · EP {ep}/6')
    return img.convert('RGB')

def cta_fit(d, t, t0, who, y=1470):
    if t < t0: return
    k = eout((t - t0) / .2); s = .7 + .3 * k
    text_c(d, W / 2, y - 55, 'MANDA', F(900, int(92 * s)), YEL, 9)
    sz = 66
    while d.textlength(who, font=F(900, sz)) > 990 and sz > 30: sz -= 2
    text_c(d, W / 2, y + 40, who, F(900, int(sz * s)), WHITE, 8)

def capa(ep, c):
    cfg = CFG[ep]
    base = frame(ep, c, cfg['thumb_t'], overlays=False).convert('RGBA')
    base = base.crop((90, 160, 990, 1760)).resize((W, H), Image.BILINEAR)
    base = ImageEnhance.Brightness(base).enhance(.8)
    vig = Image.new('L', (W, H), 0); g = ImageDraw.Draw(vig)
    g.ellipse([-300, -200, W + 300, H + 200], fill=255); vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 255)); base = Image.composite(base, dark, vig)
    d = ImageDraw.Draw(base)
    char(d, 'BLQ', 830, 1640, 1.3, eyes='wide', arm='point', arm2='face', flip=True, mouth=.8)
    arrow(d, 640, 1180, 470, 1020, RED, 34, 70)
    title = EPS[ep]['thumb']
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    sz = 160
    while g.textlength(title, font=F(900, sz)) > 960 and sz > 90: sz -= 4
    g.rectangle([0, 760 - sz * .75, W, 760 + sz * .75], fill=(10, 12, 16, 235))
    words = title.split(); x = W / 2 - g.textlength(title, font=F(900, sz)) / 2
    for i, w in enumerate(words):
        col = WHITE if (i == len(words) - 1 and len(words) > 1) else YEL
        g.text((x, 760), w, font=F(900, sz), fill=col, stroke_width=11, stroke_fill=(0, 0, 0), anchor='lm')
        x += g.textlength(w + ' ', font=F(900, sz))
    L = L.rotate(4, center=(W / 2, 760), resample=Image.BICUBIC); base.alpha_composite(L)
    d = ImageDraw.Draw(base)
    ell(d, 150, 430, 95, 95, YEL, 8); text_c(d, 150, 430, f'EP{ep}', F(900, 56), OUT, 0)
    return base.convert('RGB')

def render(ep, style, dur, music, out):
    c = setup(ep, style, dur, music)
    sfxp = f'/home/claude/serie/out/sfx{ep}.wav'; aud = f'/home/claude/serie/out/aud{ep}.wav'
    write_sfx(c.ev, c.total, sfxp); build_audio(ep, [(KEYS[(ep, i)], c.S[i]) for i in range(len(c.S))], c.total, music, sfxp, aud)
    cp = capa(ep, c); cp.save(f'/home/claude/serie/out/capa-ep{ep}.png')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', aud, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                          '-t', str(c.nf / FPS), '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(c.nf):
        im = cp if f < TH else frame(ep, c, (f - TH) / FPS)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return c

def sheet(ep, style, dur, music, ts, out):
    c = setup(ep, style, dur, music)
    ims = [capa(ep, c)] + [frame(ep, c, t) for t in ts]
    cols = 6; rows = math.ceil(len(ims) / cols); tw, th = 270, 480
    S = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
    for i, im in enumerate(ims):
        S.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    S.save(out); return c
