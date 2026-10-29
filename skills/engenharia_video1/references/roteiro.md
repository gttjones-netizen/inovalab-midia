# roteiro.json — referência dos campos

Coordenadas sempre em **pixels do quadro recortado** (saída de `map_coords.py`). Câmera = `[centroX, centroY, escala]`; a escala mínima é ajustada sozinha para não mostrar borda.

## Topo
| campo | o que é |
|---|---|
| `beat` | período da batida em s (do `beats.py`) |
| `frameSize`, `frames` | copiar do `meta.json` |
| `trilha` | `{arquivo, offset}`: só informativo, o corte é feito no `mux.sh` |
| `hud` | `{top, brand, coords}`: texto do topo, marca do rodapé, coordenadas da cidade |
| `scenes` | lista de cenas em ordem; `beats` = duração em batidas (corte cai na batida) |

## Tipos de cena
**intro**: `label` (mono amarelo), `title1` (branco), `title2` (amarelo), `sub`, `city`, `obj3d`, `bgSrc` (segundo do vídeo para o fundo desfocado). Padrão: 4 batidas.

**model**: vídeo rodando a partir de `src` com scan e checklist. `label`, `title`, `sub`, `checklist[]` (até 4), `highlight` (índice em amarelo), `stamp` (selo amarelo, opcional), `cam` (opcional). Padrão: 6 batidas.

**callout**: lead-in → freeze → mira LOCK → seta curva → caixa. `lead`, `clean` (do `matches.json`), `label`, `title`, `cam`, `target`, `box{tag,title,sub|title2}`, `arrowFromX` (x de saída da seta na caixa), `arrowEnd` (ajuste fino da ponta), `bend` (curvatura ±0,2–0,3). Padrão: 6 batidas.

**fill**: cena principal. Contorno laranja se desenha e a terra preenche no drop. `lead`, `clean`, `label`, `title`, `cam`, `polys[]`, `depth` (16), `layers` (1), `dropBeat` (batida local do drop, 2), `tagText` (rótulo com linha de chamada), `box` (opcional). Padrão: 12 batidas.

**contencao**: platôs preenchem, perímetro acende em ciano com luz correndo e setas de empuxo apontam para os muros. `lead`, `clean`, `label`, `title`, `cam`, `polys[]`, `depth` (50), `layers` (4), `empuxo` (true), `box`. Padrão: 8 batidas.

**outro**: vídeo escurecido a partir de `src` + faixa escura + frase. `lines[]` (até 3, caixa alta, ~13 caracteres por linha), `accent` (linha amarela, até ~30 caracteres com `accentSize` 50), `city`, `obj3d`. Padrão: 8 batidas.

O contador "01 / 04" do HUD conta automaticamente as cenas callout, fill e contencao.

## Objetos 3D disponíveis (`obj3d`)
- `muro_blocos_estacas`: muro de blocos com vergalhões, baldrame, viga superior, blocos de coroamento, estacas, aterro e empuxo.
Para outro sistema (muro de flexão, cortina atirantada, gabião...), adicionar uma função em `OBJ3D` no `engine/index.html`, desenhada com `proj3`.

## Limites de layout (1080x1920)
- Zona segura do Instagram: y 250–1700. Título da cena em y≈300–440, viewport 470–1370, caixa 1410–1590, rodapé 1648–1690.
- Título de cena (70 px): até ~24 caracteres. Linha da caixa (46 px): até ~36 caracteres.
