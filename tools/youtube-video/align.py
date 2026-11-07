import json, re, subprocess
from texts import T
NUM = {"catorze mil e quinhentas":"14.500","cinco graus e meio":"5,5°","mil cento e setenta e três":"1173","mil cento e setenta e oito":"1178",
 "mil duzentos e setenta e dois":"1272","mil duzentos e setenta e oito":"1278","mil trezentos e sessenta":"1360","mil trezentos e setenta":"1370",
 "mil oitocentos e dezessete":"1817","mil oitocentos e trinta e oito":"1838","mil novecentos e trinta e quatro":"1934","mil novecentos e noventa e dois":"1992",
 "mil novecentos e noventa e três":"1993","mil novecentos e noventa e cinco":"1995","mil novecentos e noventa e nove":"1999","mil novecentos e noventa":"1990",
 "mil novecentos e oitenta e nove":"1989","mil novecentos e sessenta e sete":"1967","mil oitocentos e dez":"1810","dois mil e um":"2001","dois mil e dezoito":"2018",
 "seiscentas":"600","novecentas":"900","quarenta e um":"41","cento e vinte":"120","cinquenta e cinco":"55","dezenove metros e meio":"19,5 metros",
 "dezessete":"17","dezesseis":"16","catorze macacos":"14 macacos","catorze mil":"14 mil","NBR seis um dois dois":"NBR 6122","dois graus e dois décimos":"2,2°",
 "seis décimos de grau":"0,6°","um grau e seis décimos":"1,6°","quase cem":"quase 100","cem anos":"100 anos","duzentos anos":"200 anos","quarenta centímetros":"40 cm",
 "quatro centímetros":"4 cm","vinte litros":"20 litros","quatro metros e meio":"4,5 metros","três metros":"3 metros","quarenta metros":"40 metros","sessenta metros":"60 metros",
 "dez metros":"10 metros","oitenta anos":"80 anos","sete metros":"7 metros"}
def sil(f):
    out = subprocess.run(["ffmpeg","-hide_banner","-i",f,"-af","silencedetect=n=-35dB:d=0.16","-f","null","-"],capture_output=True,text=True).stderr
    ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",out)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",out)]
    dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
    # speech chunks
    ch=[]; st=0.0
    pairs=sorted(zip(ss,se))
    for a,b in pairs:
        if a-st>0.05: ch.append([st,a])
        st=b
    if dur-st>0.05: ch.append([st,dur])
    return ch, dur
res={}; GAP=1.2; off=0.0; srt=[]
for k in sorted(T):
    txt=re.sub(r"\[[a-z]+\]\s*","",T[k])
    sents=[s.strip() for s in re.split(r"(?<=[\.\?\!:])\s+",txt) if s.strip()]
    ch,dur=sil(f"aud/{k}.mp3")
    total=sum(len(s) for s in sents); speech=sum(b-a for a,b in ch)
    # boundaries: cumulative chars -> speech time -> snap to chunk end
    bounds=[]; acc=0
    ends=[c[1] for c in ch]; starts=[c[0] for c in ch]
    def speech_to_abs(x):
        for a,b in ch:
            if x<=b-a: return a+x
            x-=b-a
        return ch[-1][1]
    times=[]; prev=0
    used=set()
    for i,s in enumerate(sents):
        acc+=len(s); target=speech_to_abs(speech*acc/total)
        if i==len(sents)-1: e=ch[-1][1]
        else:
            cand=[j for j in range(len(ends)) if ends[j]>prev+0.3]
            j=min(cand,key=lambda j:abs(ends[j]-target)) if cand else len(ends)-1
            e=ends[j] if abs(ends[j]-target)<1.2 else target
        times.append([prev, e]); 
        nxt=[x for x in starts if x>=e-0.01]
        prev=nxt[0] if nxt else e
    S=[]
    for s,(a,b) in zip(sents,times):
        disp=s
        for kk in sorted(NUM,key=len,reverse=True): disp=disp.replace(kk,NUM[kk])
        S.append({"text":disp,"start":round(off+a,3),"end":round(off+b,3)})
    res[k]={"offset":round(off,3),"dur":round(dur,3),"sents":S}
    off+=dur+GAP
res["total"]=round(off-GAP+1.5,3)
json.dump(res,open("timeline.json","w"),ensure_ascii=False,indent=1)
print(res["total"]); print(res["c2"]["sents"][:5])
