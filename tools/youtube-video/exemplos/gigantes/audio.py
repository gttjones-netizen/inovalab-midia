from mixer import *
from scenes import TL, CH, OFF, S
TOTAL = TL["total"]; m = Mixer(TOTAL)
rng = np.random.default_rng(11)

def thump(d=0.8):
    t = np.arange(int(d * SR)) / SR
    x = np.sin(2 * np.pi * (70 * np.exp(-3 * t)) * t) * np.exp(-5 * t) + 0.3 * rng.standard_normal(len(t)) * np.exp(-14 * t)
    return x
def noise_band(d, win=60):
    n = int(d * SR); x = rng.standard_normal(n); x = ma(x.astype(np.float32), win); x /= np.abs(x).max() + 1e-9
    f = int(0.3 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f); return x
def wind(d=3.0):
    x = noise_band(d, 120); t = np.arange(len(x)) / SR; return x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t))
def drill(d=2.0):
    t = np.arange(int(d * SR)) / SR; x = np.sign(np.sin(2 * np.pi * 38 * t)) * 0.3 + noise_band(d, 20) * 0.7
    x = ma(x.astype(np.float32), 8); f = int(0.15 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f); return x
def water(d=2.5): return noise_band(d, 30)
def tink():
    t = np.arange(int(0.25 * SR)) / SR; return np.sin(2 * np.pi * 1320 * t) * np.exp(-18 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t) * np.exp(-24 * t)

def at(k, i, d=0.0): return OFF(k) + S(k, i) + d
for k in CH: m.voice(load(f"aud/{k}.mp3"), OFF(k))
for k in CH[1:]: m.sfx(whoosh(0.7), OFF(k) - 1.2, "trans")

hits = [("c0", 3, 0), ("c1", 4, 0), ("c4", 13, 0), ("c6", 10, 5.0)]
for k, i, d in hits: m.sfx(thump(), at(k, i, d), "hit", trim=-1.5)
m.sfx(drill(2.5), at("c1", 2, 0.5), "amb"); m.sfx(drill(2.0), at("c1", 3, 0.2), "amb")
m.sfx(water(3.0), at("c1", 15), "amb"); m.sfx(water(2.5), at("c4", 12), "amb")
m.sfx(wind(4.0), at("c2", 0), "amb"); m.sfx(wind(4.0), at("c2", 7), "amb")
m.sfx(wind(4.0), at("c3", 8), "amb"); m.sfx(wind(3.0), at("c3", 9, 1.0), "amb")
m.sfx(sweep(), at("c2", 15, 1.0), "ui")
for d in (0.0, 0.7, 1.6): m.sfx(tink(), at("c7", 8, d), "ui")
m.sfx(alarm(0.5), at("c1", 16), "ui", trim=-3)
for k, i, d in [("c0", 5, 0.6), ("c1", 11, 0), ("c2", 9, 0), ("c3", 3, 0), ("c3", 9, 0), ("c4", 5, 3.6),
                ("c5", 10, 0), ("c6", 10, 5.0), ("c7", 10, 3.5), ("c8", 10, 0), ("c9", 5, 0)]:
    m.sfx(riser(), at(k, i, d) - 0.8, "trans"); m.sfx(pop(), at(k, i, d), "ui")
M = "/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Músicas/"
m.music(load(M + "ES_The Connection - Lennon Hutton.mp3"), 0, OFF("c5") - 0.4)
m.music(load(M + "ES_Sports Rocker - Taelimb.mp3"), OFF("c5") - 1.4, TOTAL)
m.render("mix.wav")

# conferência: pior janela de SFX vs voz (0,5 s)
fx = np.zeros(m.N, np.float32)
vref = active_db(m.vo[np.abs(m.vo) > 0])
for x, t, kind, trim in m.ev:
    g = 10 ** ((vref + REL[kind] + trim - active_db(x)) / 20); i = int(t * SR); xx = x[:m.N - i]; fx[i:i + len(xx)] += xx * g
w = SR // 2; n = m.N // w
r = 20 * np.log10(np.sqrt((fx[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)
act = r[r > -80]
print("pior janela SFX (sem ducking) vs voz: %+.1f dB" % (act.max() - vref))
