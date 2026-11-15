# Motor /reels-southpark (papel recortado)
Referência: série "A Obra do Seu Valdir" (15–20/11/2026).
Copie esta pasta para /home/claude/serie e as fontes Montserrat para /home/claude/package/files (npm pack @fontsource/montserrat@5.0.8).
- engine.py: primitivas, personagens (char), casa, solo, legendas, envelopes de boca
- render.py: timeline, mix de áudio, SFX sintetizados
- eps.py: cenários (ext, room, section_bg, beam, cable, wall_blocks, pool...) e overlays (tarja A–G, revelação, CTA, créditos, pós-créditos)
- ep_shots.py: exemplo de cenas por fala (um if por linha do roteiro)
- main.py: CFG por vídeo, frame(), capa(), render(), sheet()
- script.py: falas por personagem (N, NEL, VAL, CID) e vozes
