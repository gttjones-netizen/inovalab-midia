#!/usr/bin/env python3
"""Monta folha de contato das stills renderizadas para revisão rápida.
Uso: python3 contact.py <workdir> <saida.jpg>   (usa todos os still_*.jpg do workdir, em ordem de tempo)
"""
import glob, os, sys
from PIL import Image
work, out = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(os.path.join(work, 'still_*.jpg')), key=lambda f: float(os.path.basename(f)[6:-4]))
ims = [Image.open(f).resize((360, 640)) for f in fs]
cols = min(5, len(ims)); rows = (len(ims) + cols - 1) // cols
c = Image.new('RGB', (360 * cols, 640 * rows))
for i, im in enumerate(ims): c.paste(im, ((i % cols) * 360, (i // cols) * 640))
c.save(out); print(out, len(ims), 'quadros')
