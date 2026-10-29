#!/usr/bin/env python3
"""Desenha uma grade de coordenadas sobre o print (ampliado 2x) para ler os vértices das marcações.
Linhas finas a cada 20 px e vermelhas a cada 100 px, com rótulos nas coordenadas ORIGINAIS do print.
Uso: python3 grid.py <print.png> <saida.png>
"""
import sys
from PIL import Image, ImageDraw

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB'); im = im.resize((im.width * 2, im.height * 2)); d = ImageDraw.Draw(im)
for x in range(0, im.width, 40):
    d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if x % 200 == 0 else (0, 120, 255), width=1)
for y in range(0, im.height, 40):
    d.line([(0, y), (im.width, y)], fill=(255, 0, 0) if y % 200 == 0 else (0, 120, 255), width=1)
for x in range(0, im.width, 200): d.text((x + 2, 2), str(x // 2), fill=(255, 0, 0))
for y in range(0, im.height, 200): d.text((2, y + 2), str(y // 2), fill=(255, 0, 0))
im.save(dst)
