# Regras aprendidas com o Evanndro (engenharia_video1)

Cada regra veio de uma correção real. Valem para todo vídeo deste estilo.

## Escala e realismo
- **Aterro = camada fina de superfície** (`depth` ~16 px, `layers: 1`). Volume alto, em várias camadas, dá a ideia de obra grande e foi rejeitado (Renan, 28/10/26).
- **Objeto 3D tecnicamente fiel.** O muro da abertura é de blocos de concreto com vergalhão em todos os furos, viga baldrame, viga superior, **blocos de coroamento** ligando cada estaca à baldrame, e estacas. Faltando peça, ele percebe e pede correção. Se o projeto tiver outro sistema de contenção, crie um objeto novo em `OBJ3D`, sem reaproveitar um que não corresponda.
- Empuxo representado triangular (seta maior embaixo).

## Texto
- **Nada de painel com número inventado** (ex.: "Aterro em camadas · 67%"). Foi removido. Só aparece número que esteja no material.
- Vocabulário: **"topografia"**, não "terreno" (nos subtítulos e no checklist).
- Títulos de detalhe descrevem o que se vê ("Regiões de aterro", "Platôs de terra"), não perguntas genéricas.
- O texto das caixas usa as palavras que ele escreveu no print (ex.: "arrimo com fechamento em bloco de concreto").
- Frase final: sempre oferecer **5 ou 6 opções**, no formato bloco branco em caixa alta + linha amarela. A escolhida no Renan: "TOPOGRAFIA, ARRIMOS E ARQUITETURA / conversando no mesmo modelo."
- Tom: sem culpar arquiteto, sem falar de custo, sem absolutos, nada com cara de IA.

## Marcações do print
- Seta/texto verde no print = alvo de uma cena `callout` (o texto dele vira a caixa).
- Contorno laranja = área de terra: cena `fill` (um platô) ou `contencao` (vários platôs com arrimo em volta).
- Um "X" laranja dentro do contorno só indica "preencher"; não é vértice.

## Técnica
- Sempre animar sobre o **quadro limpo do vídeo** achado pelo `match_frames.py`, nunca sobre o print (resolução baixa e marcações à mão).
- O momento principal (preenchimento do aterro) cai no **drop** da trilha.
- Rodapé: wordmark "INOVALAB" (não há arquivo de logo; se ele mandar o PNG, trocar).
- Cópia para o PC precisa ter <30 MB (limite da ponte): use o `_pc.mp4` do `mux.sh`.
