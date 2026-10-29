#!/usr/bin/env python3
"""Analisa a trilha e calcula onde cortar para o drop cair num momento do vídeo.
Uso: python3 beats.py <musica.mp3> [--drop-video <seg>] [--buscar <ini> <fim>]
  --drop-video : segundo do vídeo onde o drop deve cair (ex.: início do preenchimento do aterro)
  --buscar     : janela da música (s) onde procurar o drop (padrão 20 90)
Imprime: período da batida (beat), BPM, tempo do drop na música e offset de início da trilha.
O 'beat' impresso vai no roteiro.json; o offset vai no mux.sh.
"""
import argparse, json
import librosa, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('musica'); ap.add_argument('--drop-video', type=float)
ap.add_argument('--buscar', nargs=2, type=float, default=[20, 90]); a = ap.parse_args()
y, sr = librosa.load(a.musica, sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
beat = float(np.median(np.diff(beats)))
hop = 2205  # 0,1 s
rms = librosa.feature.rms(y=y, hop_length=hop)[0]
t_rms = np.arange(len(rms)) * 0.1
# drop = maior salto de energia (média 2 s depois / 2 s antes) dentro da janela
best = (0, None)
for i in range(20, len(rms) - 20):
    t = t_rms[i]
    if not (a.buscar[0] <= t <= a.buscar[1]): continue
    jump = rms[i:i + 20].mean() / (rms[i - 20:i].mean() + 1e-6)
    if jump > best[0]: best = (jump, t)
drop = float(beats[np.argmin(np.abs(beats - best[1]))]) if best[1] is not None else None
res = {'beat': round(beat, 4), 'bpm': round(60 / beat, 1), 'duracao': round(len(y) / sr, 1), 'drop_musica': drop,
       'salto_energia': round(float(best[0]), 2)}
if a.drop_video is not None and drop is not None:
    res['offset_trilha'] = round(drop - a.drop_video, 3)
print(json.dumps(res, indent=1))
print('energia por segundo:', ' '.join(f'{int(v * 100)}' for v in rms[::10]))
