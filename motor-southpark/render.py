import sys, json, math, random, subprocess, os, secrets
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '/home/claude/serie')
from engine import *
exec(open('/home/claude/serie/script.py').read())

CL = json.load(open('/home/claude/serie/clips.json'))
TH = 2  # thumbnail frames
GAP = 0.24

def clip_keys():
    cnt = {k: 0 for k in VOICES}; m = {}
    for ep in sorted(EPS):
        for i, (sp, t) in enumerate(EPS[ep]['lines']):
            m[(ep, i)] = f'{sp}_{cnt[sp]}'; cnt[sp] += 1
    return m
KEYS = clip_keys()

class Ctx: pass

def timeline(ep, extra_gap, cta_hold=1.6, cred=1.5, post_tail=1.5):
    lines = EPS[ep]['lines']; n = len(lines)
    t = 0.05; S = []; E = []; items = []
    for i in range(n):
        if i == n - 1:
            t += cta_hold; tc0 = t; t += cred; t += 0.35
        t += extra_gap.get(i, 0)
        k = KEYS[(ep, i)]; d = CL[k]['dur']
        S.append(t); E.append(t + d); items.append((k, t))
        t += d + GAP
    total = E[-1] + post_tail
    return S, E, items, tc0, total

def build_audio(ep, items, total, music, sfx, outwav):
    # voice track
    inputs = []; filt = []
    for j, (k, t) in enumerate(items):
        inputs += ['-i', f'/home/claude/serie/clips/{k}.wav']
        filt.append(f'[{j}:a]adelay={int((t + TH / FPS) * 1000)}|{int((t + TH / FPS) * 1000)}[v{j}]')
    nv = len(items)
    mix = ''.join(f'[v{j}]' for j in range(nv))
    filt.append(f'{mix}amix=inputs={nv}:normalize=0:duration=longest[voice]')
    # music
    inputs += ['-ss', '16', '-i', music]
    filt.append(f'[{nv}:a]atrim=0:{total + TH / FPS},asetpts=PTS-STARTPTS,volume=0.17,afade=t=in:d=0.2,afade=t=out:st={total - 1.2}:d=1.2[mus]')
    # sfx file
    inputs += ['-i', sfx]
    filt.append(f'[{nv + 1}:a]volume=1.0[sfx]')
    filt.append(f'[voice][mus][sfx]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{total + TH / FPS}[out]')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-t', str(total + TH / FPS), '-ar', '44100', '-ac', '2', outwav]
    subprocess.run(cmd, check=True)

# ---------- SFX synth ----------
SR = 44100
def s_noise(d, color='white', seed=0):
    rng = np.random.default_rng(seed); x = rng.standard_normal(int(SR * d))
    if color == 'pink': x = np.cumsum(x); x = x - np.convolve(x, np.ones(200) / 200, 'same')
    if color == 'brown': x = np.cumsum(x); x = x - np.convolve(x, np.ones(2000) / 2000, 'same')
    return x / (np.abs(x).max() + 1e-9)
def env(n, a=0.01, r=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-np.maximum(0, t - a) / r); return e
def sfx(kind, d=None):
    if kind == 'whoosh':
        n = int(SR * .35); x = s_noise(.35, 'pink', 1); t = np.arange(n) / SR
        return 0.22 * x * np.sin(np.pi * t / .35) ** 2
    if kind == 'pop':
        t = np.arange(int(SR * .14)) / SR; return 0.5 * np.sin(2 * np.pi * 880 * t) * np.exp(-35 * t)
    if kind == 'blip':
        t = np.arange(int(SR * .07)) / SR; return 0.25 * np.sign(np.sin(2 * np.pi * 1320 * t)) * np.exp(-30 * t)
    if kind == 'riser':
        t = np.arange(int(SR * .75)) / SR; return 0.25 * np.sin(2 * np.pi * (180 + 520 * t) * t) * (t / .75)
    if kind == 'thud':
        n = int(SR * .6); x = s_noise(.6, 'brown', 2); return 0.9 * x * env(n, .005, .15)
    if kind == 'crack':
        n = int(SR * .4); x = s_noise(.4, 'white', 3); return 0.35 * x * env(n, .002, .06)
    if kind == 'alarm':
        t = np.arange(int(SR * .6)) / SR; f = np.where((t * 6).astype(int) % 2 == 0, 660, 880)
        return 0.18 * np.sign(np.sin(2 * np.pi * f * t)) * (1 - t / .6)
    if kind == 'sting':  # credits
        t = np.arange(int(SR * 1.0)) / SR
        return 0.22 * sum(np.sin(2 * np.pi * f * t) for f in (392, 494, 587)) / 3 * np.exp(-2.5 * t)
    if kind == 'rain':
        n = int(SR * (d or 3)); x = s_noise(d or 3, 'pink', 4); return 0.12 * x
    if kind == 'hammer':
        t = np.arange(int(SR * .25)) / SR; return 0.6 * (s_noise(.25, 'brown', 5)[:len(t)] * np.exp(-25 * t) + 0.4 * np.sin(2 * np.pi * 180 * t) * np.exp(-20 * t))
    if kind == 'saw':
        n = int(SR * (d or 1.2)); t = np.arange(n) / SR
        return 0.14 * (np.sign(np.sin(2 * np.pi * 220 * t)) * 0.5 + s_noise(d or 1.2, 'white', 6) * .5) * np.minimum(1, t / .1)
    if kind == 'gulp':
        t = np.arange(int(SR * .5)) / SR; return 0.3 * np.sin(2 * np.pi * (200 + 80 * np.sin(2 * np.pi * 9 * t)) * t) * np.exp(-4 * t)
    if kind == 'boing':
        t = np.arange(int(SR * .5)) / SR; return 0.3 * np.sin(2 * np.pi * (300 + 200 * np.exp(-6 * t) * np.sin(2 * np.pi * 12 * t)) * t) * np.exp(-5 * t)
    if kind == 'stamp':
        n = int(SR * .3); return 0.7 * s_noise(.3, 'brown', 7) * env(n, .002, .05)
    if kind == 'vhs':
        n = int(SR * .4); return 0.15 * s_noise(.4, 'white', 8) * env(n, .01, .2)
    if kind == 'rewind':
        t = np.arange(int(SR * .6)) / SR; return 0.2 * np.sign(np.sin(2 * np.pi * (1200 - 1500 * t) * t))
    return np.zeros(10)

def write_sfx(events, total, path):
    n = int(SR * (total + 1)); buf = np.zeros(n)
    for t, k, *a in events:
        x = sfx(k, *a); i = int(SR * (t + TH / FPS))
        if i < 0: continue
        m = min(len(x), n - i); buf[i:i + m] += x[:m]
    buf = np.clip(buf, -1, 1)
    import wave
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((buf * 32767).astype(np.int16).tobytes()); w.close()
