#!/usr/bin/env python3
"""Acha, para cada print, o quadro exato do vídeo (SIFT + homografia) e salva a versão limpa em alta.
Uso: python3 match_frames.py <workdir> print1.png print2.png ...
Requer prep_video.py rodado antes (usa meta.json e v/).
Saídas: <workdir>/clean_<i>.jpg, <workdir>/H_<i>.npy, <workdir>/matches.json, <workdir>/conferencia_match.jpg
  matches.json -> por print: tempo do quadro, 'lead' (tempo -0.6 s para o lead-in) e inliers (>=100 é confiável).
"""
import cv2, glob, json, os, subprocess, sys, tempfile
import numpy as np

work, prints = sys.argv[1], sys.argv[2:]
meta = json.load(open(os.path.join(work, 'meta.json')))
frames = sorted(glob.glob(os.path.join(work, 'v', 'f*.jpg')))
sift = cv2.SIFT_create(5000); bf = cv2.BFMatcher()

def homog(d1, k1, img):
    k2, d2 = sift.detectAndCompute(img, None)
    if d2 is None or len(k2) < 10: return 0, None
    m = bf.knnMatch(d1, d2, k=2); good = [a for a, b in (x for x in m if len(x) == 2) if a.distance < 0.7 * b.distance]
    if len(good) < 10: return 0, None
    p1 = np.float32([k1[a.queryIdx].pt for a in good]); p2 = np.float32([k2[a.trainIdx].pt for a in good])
    H, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 3)
    return (int(mask.sum()) if mask is not None else 0), H

# busca grossa: 1 a cada 5 quadros (6 fps), em meia resolução
coarse = []
for i in range(0, len(frames), 5):
    g = cv2.imread(frames[i], 0); g = cv2.resize(g, None, fx=0.5, fy=0.5)
    coarse.append((i, g))

out = {}; checks = []
for pi, pr in enumerate(prints, 1):
    g = cv2.imread(pr, 0); k1, d1 = sift.detectAndCompute(g, None)
    best = (0, None)
    for i, img in coarse:
        n, _ = homog(d1, k1, img)
        if n > best[0]: best = (n, i)
    t0 = best[1] / 30
    # refino: 60 fps em torno do melhor tempo, direto do vídeo original recortado
    tmp = tempfile.mkdtemp()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(0, t0 - 0.3)), '-i', meta['video'], '-t', '0.6',
                    '-vf', f"crop={meta['crop']}", '-vsync', '0', '-q:v', '1', os.path.join(tmp, 'g%03d.jpg')], check=True)
    fps60 = sorted(glob.glob(os.path.join(tmp, 'g*.jpg')))
    rb = (0, None, None)
    for j, f in enumerate(fps60):
        n, H = homog(d1, k1, cv2.imread(f, 0))
        if n > rb[0]: rb = (n, f, H)
    # o refino usa o fps original; estima o tempo pelo índice
    num, den = map(int, meta['fps_original'].split('/')); fo = num / den
    t = max(0, t0 - 0.3) + fps60.index(rb[1]) / fo
    name = f'clean_{pi}.jpg'
    cv2.imwrite(os.path.join(work, name), cv2.imread(rb[1]), [cv2.IMWRITE_JPEG_QUALITY, 97])
    np.save(os.path.join(work, f'H_{pi}.npy'), rb[2])
    out[os.path.basename(pr)] = {'indice': pi, 'clean': name, 'tempo': round(t, 3), 'lead': round(max(0, t - 0.6), 3), 'inliers': rb[0]}
    col = cv2.imread(pr); hh = cv2.imread(rb[1])
    w = cv2.warpPerspective(col, rb[2], (hh.shape[1], hh.shape[0]))
    checks.append(cv2.resize(cv2.addWeighted(hh, 0.5, w, 0.5, 0), (734, 540)))
    print(f"{pr}: t={t:.2f}s inliers={rb[0]}{'  <-- BAIXO, conferir' if rb[0] < 100 else ''}")

json.dump(out, open(os.path.join(work, 'matches.json'), 'w'), indent=1, ensure_ascii=False)
while len(checks) % 2: checks.append(np.zeros_like(checks[0]))
rows = [np.hstack(checks[i:i + 2]) for i in range(0, len(checks), 2)]
cv2.imwrite(os.path.join(work, 'conferencia_match.jpg'), np.vstack(rows))
