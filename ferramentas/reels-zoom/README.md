# Motor do /reels-zoom (InovaLab)

Referência que funcionou: "28 dias por dentro" (cura do concreto, nov/2026).

- `cura.py`: base (paleta vibrante, dither quadriculado, fontes, etiquetas, contador, cenas reais da laje).
- `zoom_concreto.py`: motor de zoom contínuo num mundo único em mm (laje → brita → areia → cimento → C-S-H → átomos), com geração procedural por células (hash vetorizado) e renderização sem "pipoco" (specks sub-pixel → pontos → formas).

Preparar fontes na pasta de trabalho:

    npm pack @fontsource/pixelify-sans @fontsource/montserrat@5.0.8
    mkdir -p fontsource-pixelify-sans-5.3.0 && tar xzf fontsource-pixelify-sans-*.tgz -C fontsource-pixelify-sans-5.3.0
    tar xzf fontsource-montserrat-5.0.8.tgz && mv package mont

Rodar: `python3 zoom_concreto.py test 2,5,9,15 folha.png` e `python3 zoom_concreto.py full`.
`cfg.json` opcional: `{"bpm": 117.45, "offset": 0.0}` para alinhar os tempos à música.
