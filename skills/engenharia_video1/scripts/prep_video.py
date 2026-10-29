#!/usr/bin/env python3
"""Prepara o vídeo-base: detecta tarjas pretas, recorta, extrai quadros a 30 fps e gera folha de contato.
Uso: python3 prep_video.py <video.mp4> <workdir>
Saídas: <workdir>/v/f0001.jpg..., <workdir>/meta.json, <workdir>/contato.jpg
"""
import json, os, re, subprocess, sys
from collections import Counter

video, work = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(work, 'v'), exist_ok=True)

probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate',
                                   '-show_entries', 'format=duration', '-of', 'json', video], capture_output=True, text=True).stdout)
vs = [s for s in probe['streams'] if s['codec_type'] == 'video'][0]
dur = float(probe['format']['duration'])
has_audio = any(s['codec_type'] == 'audio' for s in probe['streams'])

log = subprocess.run(['ffmpeg', '-i', video, '-vf', 'cropdetect=24:2:0', '-t', str(min(dur, 30)), '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
crops = Counter(re.findall(r'crop=(\d+:\d+:\d+:\d+)', log))
crop = crops.most_common(1)[0][0] if crops else f"{vs['width']}:{vs['height']}:0:0"
cw, ch, cx, cy = map(int, crop.split(':'))

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'crop={crop},fps=30', '-q:v', '2',
                os.path.join(work, 'v', 'f%04d.jpg')], check=True)
n = len([f for f in os.listdir(os.path.join(work, 'v')) if f.endswith('.jpg')])
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'crop={crop},fps=1/{max(dur/12,0.5):.3f},scale=480:-1,tile=4x3',
                '-frames:v', '1', os.path.join(work, 'contato.jpg')], check=True)

meta = {'video': os.path.abspath(video), 'duracao': round(dur, 3), 'original': [vs['width'], vs['height']], 'fps_original': vs['r_frame_rate'],
        'crop': crop, 'frameSize': [cw, ch], 'frames': {'dir': 'v', 'count': n}, 'tem_audio': has_audio}
json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))
