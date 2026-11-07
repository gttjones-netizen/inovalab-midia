# Motor de vídeo longo do YouTube (InovaLab, pixel art 1920×1080)

Usado pela skill `/youtube-video`. Referência aprovada: **"A Torre de Pisa deveria ter caído. Uma guerra salvou ela"** (13:10, 07/11/2026). Os arquivos aqui são o projeto real desse vídeo.

| Arquivo | O que é | Num vídeo novo |
|---|---|---|
| `lib.py` | texturas, céu, solo em corte, torre/prédio, **Bloquinho**, setas, poeira, fontes | reaproveitar; acrescentar desenhos novos |
| `texts.py` | `T = {"c0": ..., "c9": ...}` narração por capítulo | reescrever |
| `align.py` | alinha frases ao áudio (silencedetect) → `timeline.json`; `NUM` troca números por extenso por dígitos | trocar o dicionário `NUM` |
| `scenes.py` | uma função `sc_cN(img, c, t)` por capítulo + `TITLES` | reescrever (exemplo de Pisa) |
| `render.py` | cartões de capítulo, rótulos, câmera, marca d'água | reaproveitar |
| `mixer.py` | **mixagem v2**: SFX normalizados abaixo da voz + ducking | reaproveitar |
| `audio.py` | exemplo de uso do mixer (eventos de Pisa) | reescrever os eventos |
| `thumbs.py` | 3 thumbs 1280×720 | reescrever |

Render: `python3 align.py` → `python3 render.py sheet 5,60,200 sheet.png` (conferir) → `python3 render.py run 0 400 part1.mp4` e `400 FIM part2.mp4` em paralelo → `python3 audio.py` → juntar + `loudnorm=I=-14:TP=-1`.
