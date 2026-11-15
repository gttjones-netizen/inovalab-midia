import sys, json
from main import *
plan=json.load(open('/home/claude/serie/plan.json'))
MD='/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Músicas/'
for ep in map(int, sys.argv[1:]):
    p=plan[str(ep)]
    render(ep, p['style'], p['dur'], MD+p['music'], f'/home/claude/serie/out/serie-valdir-ep{ep}.mp4')
    print('done',ep,flush=True)
