---
name: engenharia_video1
description: Edita vídeo vertical (Story/Reels/TikTok) no estilo "HUD de engenharia" da InovaLab — freeze com mira LOCK, setas animadas, aterro 3D sobre o modelo e cortes na batida. Use quando o Evanndro pedir engenharia_video1 ou esse estilo.
---

# engenharia_video1 — HUD de engenharia (InovaLab)

Transforma uma gravação de tela do modelo (Revit/BIM) e prints com marcações em um vídeo 1080x1920 estilo "demo reel": fundo navy com grid de prancheta, viewport com colchetes ciano, HUD (REC, contador de cena, coordenadas), freeze com mira LOCK, setas curvas amarelas, caixas de vidro, terra preenchendo platôs, transições zoom/glitch/flash na batida e frase final em faixa escura.

Esta skill **só produz o vídeo**. Data, agendamento, Metricool e entrega ficam com a skill que chamou (/storie, /reels, /tiktok).

Referência visual aprovada: `references/exemplo-renan/folha-referencia.jpg` (Storie Renan, Jundiaí, 29/10/26).

## Código da skill

O motor e os scripts ficam no repositório `gttjones-netizen/inovalab-midia`, pasta `skills/engenharia_video1/`:

```bash
cd /home/claude
git -C inovalab-midia rev-parse HEAD 2>/dev/null || git clone --depth 1 --filter=blob:none --sparse https://github.com/gttjones-netizen/inovalab-midia
cd inovalab-midia && git sparse-checkout add skills/engenharia_video1 && git pull -q
SK=/home/claude/inovalab-midia/skills/engenharia_video1
pip install --break-system-packages -q opencv-python-headless librosa
```
Se o clone falhar por acesso, chame `add_repo` (owner `gttjones-netizen`, repo `inovalab-midia`) e repita. Playwright, Chromium e ffmpeg já vêm no container.

**Leia `$SK/references/regras-de-feedback.md` antes de começar.** São correções reais do Evanndro e valem sempre.

| Arquivo | Função |
|---|---|
| `engine/index.html` | motor canvas determinístico (cenas, HUD, efeitos, objetos 3D) |
| `engine/render.js` | `node render.js <work> stills t1,t2` ou `node render.js <work> video <saida.mp4>` |
| `scripts/prep_video.py` | recorta tarjas, extrai quadros 30 fps, `meta.json`, `contato.jpg` |
| `scripts/match_frames.py` | acha o quadro de cada print, salva `clean_N.jpg` e homografia |
| `scripts/grid.py` | grade de coordenadas sobre o print para ler vértices |
| `scripts/map_coords.py` | converte pontos do print para o quadro limpo (`coords.json`) |
| `scripts/beats.py` | batida, BPM, drop da trilha e offset de corte |
| `scripts/mux.sh` | trilha + fades + loudnorm; gera também `_pc.mp4` <30 MB |
| `scripts/contact.py` | folha de contato das stills |
| `config/estilo.json` | DNA do estilo: cores, fontes, viewport, efeitos |
| `config/roteiro.exemplo.json` | roteiro completo do exemplo Renan (ponto de partida) |
| `references/roteiro.md` | todos os campos e tipos de cena |

Trabalhe numa pasta própria no scratchpad (`W=<scratchpad>/<projeto>`).

## Fluxo

### 1. Material
Precisa de: **vídeo** da navegação no modelo, **prints** com as marcações dele e o **contexto** (cliente, cidade, o que é o foco). Leitura das marcações:
- seta/texto **verde** → cena `callout` (o texto dele vira a caixa);
- contorno **laranja** → área de terra: `fill` (um platô, cena principal) ou `contencao` (platôs com arrimos em volta).

Trilha: a skill que chamou escolhe (pasta Músicas, controle de uso, máx. 3 usos); se não houver, pergunte.

### 2. Preparar e conferir o vídeo
```bash
python3 $SK/scripts/prep_video.py <video.mp4> $W
```
Veja `contato.jpg`. **Pare e avise** se aparecer nome de arquivo, caminho, nome de cliente, e-mail, aba de navegador ou valor comercial.

### 3. Casar prints com o vídeo
```bash
python3 $SK/scripts/match_frames.py $W print1.png print2.png ...
```
Confira `conferencia_match.jpg` (print sobreposto ao quadro). Inliers <100 = match duvidoso: avise e use o print.

### 4. Ler as marcações
Para cada print: `python3 $SK/scripts/grid.py print.png grid_N.png`, abra a imagem e anote alvos e vértices **em coordenadas do print**. Monte `$W/marcas.json` (modelo em `config/marcas.exemplo.json`) e rode:
```bash
python3 $SK/scripts/map_coords.py $W $W/marcas.json
```
Confira `conferencia_coords.jpg`: os polígonos têm que assentar sobre as áreas certas.

### 5. Roteiro (aprovação obrigatória)
Copie `config/roteiro.exemplo.json` para `$W/roteiro.json` e adapte (campos em `references/roteiro.md`). Ordem padrão, total de 50 batidas:

| cena | tipo | batidas |
|---|---|---|
| abertura: título + objeto 3D | intro | 4 |
| modelo rodando + checklist | model | 6 |
| detalhes dos prints (1 por print verde) | callout | 6 cada |
| ponto alto: terra preenchendo | fill | 12 |
| platôs + arrimos em volta | contencao | 8 |
| frase final | outro | 8 |

`lead` e `clean` vêm do `matches.json`; `target` e `polys`, do `coords.json`. Escolha `obj3d` compatível com o sistema real do projeto; se não existir, crie em `OBJ3D` (ver `references/roteiro.md`).

Mostre ao Evanndro, em lista curta: título de cada cena, texto de cada caixa e **5 ou 6 opções de frase final** (bloco branco em caixa alta + linha amarela). **Aguarde a escolha.**

### 6. Sincronizar com a trilha
O drop deve cair no início do preenchimento: `drop_video = início da cena fill + dropBeat × beat`.
```bash
python3 $SK/scripts/beats.py <musica.mp3> --drop-video <drop_video> --buscar <ini> <fim>
```
Ponha o `beat` no roteiro; como as durações dependem do beat, recalcule `drop_video` e rode de novo até o offset estabilizar. Guarde o `offset_trilha`.

### 7. Stills de revisão
```bash
node $SK/engine/render.js $W stills <um tempo no meio de cada cena, separados por vírgula>
python3 $SK/scripts/contact.py $W $W/folha.jpg
```
Veja a folha. Confira: texto não estoura a largura, alvo da seta no lugar certo, nada fora de y 250–1700, terra em cima da área marcada.

### 8. Render e trilha
```bash
node $SK/engine/render.js $W video $W/mudo.mp4          # ~3,5 min para 30 s
bash $SK/scripts/mux.sh $W/mudo.mp4 <musica.mp3> <offset> $W/<nome-final>.mp4
```
Envie o `<nome-final>.mp4` com `SendUserFile` (display render) e peça aprovação. Ajustes: edite o `roteiro.json` e renderize de novo; peça nova ao 3D vai no `engine/index.html`.

### 9. Devolver para a skill que chamou
- `<nome-final>.mp4`: arquivo para publicar (GitHub raw → Metricool).
- `<nome-final>_pc.mp4`: cópia <30 MB para salvar no PC (`device_commit_files` via `fileUuid` do `SendUserFile`).
- Registrar o uso da trilha no controle de músicas.

## Evolução da skill
Quando o Evanndro corrigir algo que deve valer sempre, acrescente a regra em `references/regras-de-feedback.md`. Melhoria no motor vai em `engine/`. Faça commit e push no `inovalab-midia` (mensagem clara, sem apagar o exemplo Renan) e avise em uma linha o que mudou.

Novos estilos do banco de animações: duplique a pasta como `skills/<novo_nome>/`, troque `config/estilo.json` e as cenas do `engine/index.html`, e crie a skill com o novo nome.
