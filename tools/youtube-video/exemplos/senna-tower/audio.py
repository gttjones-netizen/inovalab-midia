from mixer import *
from scenes import TL, CH, OFF, S
import numpy as np
TOTAL = TL["total"]; m = Mixer(TOTAL)
A = {n: load(f"aud/s_{n}.mp3") for n in ["broca","concreto","gelo","vento","baque"]}
for k in CH: m.voice(load(f"aud/{k}.mp3"), OFF(k))
for k in CH[1:]: m.sfx(whoosh(0.7), OFF(k) - 1.0, "trans")
def at(k, i, d=0.0): return OFF(k) + S(k, i) + d
KIND = {"broca":"amb","concreto":"amb","gelo":"ui","vento":"amb","baque":"hit"}
ev = [("baque", at("c0",3)), ("gelo", at("c0",5,9.2)),
      ("baque", at("c1",9,2.6)), ("vento", at("c1",11)), ("vento", at("c1",13)),
      ("baque", at("c2",1)), ("baque", at("c2",6)),
      ("broca", at("c3",12,0.8)), ("broca", at("c3",13,0.2)),
      ("broca", at("c4",1,0.3)), ("broca", at("c4",3,0.5)), ("baque", at("c4",4,-0.2)), ("broca", at("c4",5,0.3)), ("concreto", at("c4",9,0.3)), ("concreto", at("c4",9,1.6)),
      ("baque", at("c5",6,0.5)), ("vento", at("c5",15)), ("gelo", at("c5",26,0.3)),
      ("concreto", at("c6",0,0.8)), ("concreto", at("c6",3,0.8)), ("baque", at("c6",11,4.6)), ("gelo", at("c6",14,0.2)), ("gelo", at("c6",15,0.8)), ("gelo", at("c6",15,2.0)),
      ("baque", at("c7",6,1.2)), ("broca", at("c8",12,0.2))]
for n, t in ev: m.sfx(A[n], t, KIND[n])
for k, i, d in [("c0",6,0),("c1",6,0),("c2",8,0.6),("c3",5,0.4),("c3",14,3.0),("c4",15,1.6),("c5",3,3.6),("c5",22,0),("c6",15,0.8),("c7",12,0),("c8",5,0),("c9",4,0)]:
    m.sfx(riser(), at(k,i,d) - 0.8, "trans"); m.sfx(pop(), at(k,i,d), "ui")
M = "/mnt/user-data/uploads/Postagens InovaLab - Cowork/Material para criação de postagens/Músicas/"
m.music(load(M+"ES_City Skylines - Sum Wave.mp3"), 0, OFF("c5") - 0.4)
m.music(load(M+"ES_It's Getting Better - Real Heroes.mp3"), OFF("c5") - 1.2, TOTAL)
m.render("mix.wav")
# conferência: pior trecho de SFX vs voz (janelas de 0,5 s)
