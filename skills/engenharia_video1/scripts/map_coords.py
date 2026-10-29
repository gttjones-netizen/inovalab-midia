#!/usr/bin/env python3
"""Converte pontos lidos no print (alvos de seta, vértices de polígono) para coordenadas do quadro limpo.
Uso: python3 map_coords.py <workdir> <marcas.json>
marcas.json (coordenadas no PRINT original, lidas com grid.py):
{
  "aterro_alvo":  {"print": 1, "ponto": [262, 240]},
  "plato":        {"print": 3, "poligono": [[160,41],[383,97],[318,148]]}
}
"print" = índice do print em matches.json (1, 2, 3...).
Saídas: <workdir>/coords.json (mesmas chaves, em pixels do quadro) e <workdir>/conferencia_coords.jpg
"""
import cv2, json, os, sys
import numpy as np

work, marks = sys.argv[1], json.load(open(sys.argv[2]))
out = {}; byprint = {}
for k, m in marks.items():
    H = np.load(os.path.join(work, f"H_{m['print']}.npy"))
    pts = [m['ponto']] if 'ponto' in m else m['poligono']
    q = cv2.perspectiveTransform(np.float32(pts).reshape(-1, 1, 2), H).reshape(-1, 2)
    q = [[round(float(a), 1), round(float(b), 1)] for a, b in q]
    out[k] = q[0] if 'ponto' in m else q
    byprint.setdefault(m['print'], []).append((k, out[k], 'ponto' in m))
json.dump(out, open(os.path.join(work, 'coords.json'), 'w'), indent=1)
tiles = []
for p, items in sorted(byprint.items()):
    img = cv2.imread(os.path.join(work, f'clean_{p}.jpg'))
    for k, v, is_pt in items:
        if is_pt: cv2.circle(img, tuple(np.int32(v)), 14, (0, 0, 255), 4)
        else: cv2.polylines(img, [np.int32(v)], True, (0, 140, 255), 4)
        x, y = np.int32(v if is_pt else v[0]); cv2.putText(img, k, (int(x) + 16, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    tiles.append(cv2.resize(img, (734, 540)))
while len(tiles) % 2: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(os.path.join(work, 'conferencia_coords.jpg'), np.vstack([np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles), 2)]))
print(json.dumps(out))
