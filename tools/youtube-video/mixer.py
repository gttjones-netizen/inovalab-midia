"""Mixer v2 (InovaLab YouTube) — SFX sempre abaixo da voz.
Uso:
    from mixer import Mixer
    m = Mixer(total_seconds)
    m.voice(arr, t)                 # narração (referência de volume)
    m.sfx(arr, t, kind="ui")        # efeitos: kind = ui | hit | amb | trans
    m.music(arr, t0, t1)            # trilha (loop + fade)
    m.render("mix.wav")
Regras (medidas no vídeo da Torre de Pisa, 11/2026): os SFX entravam no mesmo nível
ou ACIMA da voz (range −18 dB, alarme quadrado −16 dB, voz −18,6 dB) e não abaixavam
durante a fala. Aqui cada efeito é normalizado em relação à voz e abaixa sob a fala.
"""
import numpy as np, subprocess, wave

SR = 44100
# alvo (dB RMS ativo, relativo à voz) por tipo de efeito
REL = {"ui": -14.0, "trans": -16.0, "amb": -16.0, "hit": -10.0}
DUCK_SPEECH_DB = -6.0      # SFX a mais de redução enquanto há fala
MUSIC_SPEECH, MUSIC_GAP = 0.09, 0.16


def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def ma(x, win):
    c = np.cumsum(np.concatenate([[0], x])); y = (c[win:] - c[:-win]) / win
    return np.concatenate([np.full(win // 2, y[0]), y, np.full(len(x) - len(y) - win // 2, y[-1])]).astype(np.float32)


def active_db(x, w=0.05):
    w = int(w * SR); n = max(len(x) // w, 1)
    r = np.sqrt((np.pad(x, (0, max(0, n * w - len(x))))[:n * w].reshape(n, w) ** 2).mean(1))
    r = r[r > r.max() * 0.1]
    return 20 * np.log10(np.sqrt((r ** 2).mean()) + 1e-9)


class Mixer:
    def __init__(s, total):
        s.N = int(SR * total); s.vo = np.zeros(s.N, np.float32); s.fx = np.zeros(s.N, np.float32)
        s.mu = np.zeros(s.N, np.float32); s.ev = []

    def _put(s, buf, x, t, v=1.0):
        i = int(t * SR)
        if i < 0 or i >= s.N: return
        x = x[:s.N - i]; buf[i:i + len(x)] += x * v

    def voice(s, x, t): s._put(s.vo, x, t)
    def sfx(s, x, t, kind="ui", trim=0.0): s.ev.append((x, t, kind, trim))   # trim = ajuste fino em dB

    def music(s, track, t0, t1, overlap=2.0, fade=1.5):
        n = int((t1 - t0) * SR); seg = np.zeros(n, np.float32); pos = 0
        while pos < n:
            piece = track[:n - pos]; seg[pos:pos + len(piece)] += piece
            if len(piece) < len(track): break
            pos += len(piece) - int(overlap * SR)
        f = int(fade * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        s._put(s.mu, seg, t0)

    def render(s, path, report=True):
        vref = active_db(s.vo[np.abs(s.vo) > 0] if np.any(s.vo) else s.vo)
        for x, t, kind, trim in s.ev:
            g = 10 ** ((vref + REL[kind] + trim - active_db(x)) / 20)
            s._put(s.fx, x, t, g)
        win = int(0.25 * SR)
        speech = ma((ma(np.abs(s.vo), win) > 0.01).astype(np.float32), int(0.12 * SR))   # 0..1 suave
        fxg = 1 + (10 ** (DUCK_SPEECH_DB / 20) - 1) * speech
        fx = s.fx * fxg
        pk = np.abs(fx).max()
        if pk > 0.5: fx *= 0.5 / pk                                    # SFX nunca passa de −6 dBFS antes do master
        mug = MUSIC_GAP + (MUSIC_SPEECH - MUSIC_GAP) * speech
        mix = s.vo + fx + s.mu * mug
        mix *= 0.9 / np.abs(mix).max()
        w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
        if report:
            m = np.abs(fx) > 1e-4
            print(f"voz {vref:.1f} dB | SFX ativo {active_db(fx[m]):.1f} dB "
                  f"({active_db(fx[m]) - vref:+.1f} dB vs voz) | eventos {len(s.ev)}")
        return path


# ---------- SFX sintéticos suaves (8-bit, sem sons de jogo) ----------
_rng = np.random.default_rng(3)
def whoosh(d=0.6):
    n = int(d * SR); x = np.cumsum(_rng.standard_normal(n)); x -= ma(x, 200); x /= np.abs(x).max(); return x * np.hanning(n)
def pop():          # mais grave e curto que o v1 (880 Hz cansava)
    t = np.arange(int(0.10 * SR)) / SR; return np.sin(2 * np.pi * 520 * t) * np.exp(-40 * t) + 0.4 * np.sin(2 * np.pi * 780 * t) * np.exp(-55 * t)
def riser(d=0.8):
    t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * (160 + 380 * t) * t) * np.linspace(0, 1, len(t)) ** 2
def alarm(d=0.5):   # seno em vez de onda quadrada
    t = np.arange(int(d * SR)) / SR; f = 620 + 180 * (np.sin(2 * np.pi * 4 * t) > 0)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.hanning(len(t)) ** 0.3
def sweep(d=1.0):
    t = np.arange(int(d * SR)) / SR; ph = 2 * np.pi * np.cumsum(700 * np.exp(-1.5 * t)) / SR; return np.sin(ph) * np.linspace(1, 0.2, len(t))
