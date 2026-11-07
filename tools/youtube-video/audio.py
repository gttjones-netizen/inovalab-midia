from mixer import *
from scenes import TL, CH, OFF, S
TOTAL = TL["total"]; m = Mixer(TOTAL)
A = {n: load(f"aud/{n}.mp3") for n in ["s_agua","s_broca","s_chumbo","s_macaco","s_desaba","sfx_range","sfx_relogio","sfx_agua"]}
for k in CH: m.voice(load(f"aud/{k}.mp3"), OFF(k))
for k in CH[1:]: m.sfx(whoosh(0.7), OFF(k) - 1.0, "trans")
def at(k, i, d=0.0): return OFF(k) + S(k, i) + d
KIND = {"s_desaba":"hit","s_chumbo":"hit","s_macaco":"hit","s_agua":"amb","s_broca":"amb","sfx_agua":"amb","sfx_range":"ui","sfx_relogio":"ui"}
ev = [("sfx_range", at("c0",0)), ("sfx_relogio", at("c0",4)),
      ("s_desaba", at("c2",12,1.2)), ("sfx_relogio", at("c2",13,1)), ("sfx_agua", at("c3",6)),
      ("sfx_relogio", at("c4",6)), ("sfx_range", at("c4",16)), ("s_desaba", at("c4",20,1.6)),
      ("s_agua", at("c5",4)), ("s_desaba", at("c5",10,3.6)), ("s_chumbo", at("c6",5,0.5)),
      ("s_chumbo", at("c6",10,0.3)), ("s_macaco", at("c7",19,1)), ("s_macaco", at("c7",19,2.5))]
for i in range(4): ev.append(("s_broca", at("c6",17,0.3 + i*1.0)))
for n, t in ev: m.sfx(A[n], t, KIND[n])
m.sfx(alarm(), at("c6",9), "ui"); m.sfx(sweep(), at("c2",13), "ui")
for k, i, d in [("c0",3,0.6),("c1",15,0),("c2",3,0),("c3",13,0),("c4",7,0),("c4",22,0),("c5",12,0),("c6",16,0),("c6",34,0),("c7",14,0),("c8",13,0)]:
    m.sfx(riser(), at(k,i,d) - 0.8, "trans"); m.sfx(pop(), at(k,i,d), "ui")
M = "/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Músicas/"
m.music(load(M+"ES_RISE - Ballpoint.mp3"), 0, OFF("c5") - 0.4)
m.music(load(M+"ES_The Shroud of My Lies (Instrumental Version) - ELFL.mp3"), OFF("c5") - 1.2, TOTAL)
m.render("mix_v2.wav")
