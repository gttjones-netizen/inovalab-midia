import json, re, subprocess
from texts import T
NUM = {"Oitocentos e vinte e oito metros":"828 metros","oitocentos e vinte e oito":"828","seiscentas e sessenta toneladas":"660 toneladas","um quilômetro":"1 km",
 "dois mil e dezesseis":"2016","dois mil e dezoito":"2018","dois mil e treze":"2013","dois mil e vinte e cinco":"2025","dois mil e vinte e seis":"2026","dois mil e quinze":"2015",
 "dois mil e sete":"2007","dois mil e três":"2003","dois mil e dez":"2010","cento e quarenta metros":"140 metros","três metros e setenta":"3,70 metros",
 "cento e noventa e duas":"192","um metro e meio":"1,5 metro","quarenta e sete metros":"47 metros","mais de quarenta":"mais de 40","oito de novembro":"8 de novembro",
 "seiscentos e um metros":"601 metros","Taipei cento e um":"Taipei 101","quinhentos e oito metros":"508 metros","oitenta e sete":"87","noventa e dois":"92",
 "cinco metros e meio":"5,5 metros","quarenta por cento":"40%","oito de agosto":"8 de agosto","um metro inteiro":"1 metro inteiro","quinhentos metros":"500 metros",
 "cem andares":"100 andares","quatrocentos metros":"400 metros","duzentas e setenta":"270","um metro e oitenta":"1,8 metro","cento e cinco metros":"105 metros",
 "cinco metros de espessura":"5 metros de espessura","vinte e dois mil e quatrocentos megawatts":"22.400 megawatts","vinte e oito milhões":"28 milhões",
 "quarenta bilhões":"40 bilhões","Seis centésimos de microssegundo":"0,06 microssegundo","cento e vinte e cinco anos":"125 anos","cento e noventa e seis metros":"196 metros",
 "sessenta e cinco andares":"65 andares","sete mil novecentos e dezenove metros":"7.919 metros","doze milhões e setecentos mil metros cúbicos":"12,7 milhões de m³",
 "duzentos e dez":"210","catorze mil megawatts":"14.000 megawatts","cento e três milhões":"103 milhões","três pavimentos":"3 pavimentos","N S P T":"NSPT","S P T":"SPT",
 "imagina mil":"imagina 1.000"}
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
res={}; GAP=2.0; off=0.0; srt=[]
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
    pe=0.0
    for i,(s_,tb) in enumerate(zip(sents,times)):
        need=len(s_)/16.0
        if tb[1]-tb[0] < 0.6*need:
            tb[0]=max(pe+0.25, tb[1]-need) if tb[1]-need>pe else pe+0.2
            if tb[1] < tb[0]+0.5: tb[1]=tb[0]+max(0.7,need)
        pe=tb[1]
    for s,(a,b) in zip(sents,times):
        disp=s
        for kk in sorted(NUM,key=len,reverse=True): disp=disp.replace(kk,NUM[kk])
        S.append({"raw":s,"text":disp,"start":round(off+a,3),"end":round(off+b,3)})
    res[k]={"offset":round(off,3),"dur":round(dur,3),"sents":S}
    off+=dur+GAP
res["total"]=round(off-GAP+26.0,3)
json.dump(res,open("timeline.json","w"),ensure_ascii=False,indent=1)
print(res["total"]); 
