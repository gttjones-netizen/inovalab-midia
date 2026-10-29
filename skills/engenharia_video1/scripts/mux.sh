#!/usr/bin/env bash
# Junta a trilha ao vídeo mudo: corte no offset, fade-in 0,2 s, fade-out 1 s, loudnorm -14 LUFS.
# Gera também uma cópia <30 MB (limite da ponte para salvar no PC).
# Uso: bash mux.sh <video_mudo.mp4> <musica.mp3> <offset_s> <saida.mp4>
set -euo pipefail
V="$1"; M="$2"; OFF="$3"; OUT="$4"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
FO=$(python3 -c "print(max(0,$DUR-1))")
ffmpeg -v error -y -i "$V" -ss "$OFF" -t "$DUR" -i "$M" -map 0:v -map 1:a -c:v copy \
  -af "afade=t=in:d=0.2,afade=t=out:st=$FO:d=1,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart "$OUT"
PC="${OUT%.mp4}_pc.mp4"
BR=$(python3 -c "print(int(26*8*1000/$DUR - 200))")   # ~26 MB
ffmpeg -v error -y -i "$OUT" -c:v libx264 -preset slow -b:v "${BR}k" -maxrate "$((BR*5/4))k" -bufsize "$((BR*2))k" \
  -pix_fmt yuv420p -c:a copy -movflags +faststart "$PC"
ls -la "$OUT" "$PC"
