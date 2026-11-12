import json, re, subprocess
from texts import T
NUM = {"Quinhentos e quarenta e quatro":"544","quinhentos e quarenta e quatro":"544","Sessenta centímetros":"60 centímetros","sessenta centímetros":"60 centímetros",
 "setecentas e noventa e oito":"798","São 798":"São 798","quarenta metros":"40 metros","Quarenta metros":"40 metros","mil e seiscentas toneladas":"1.600 toneladas","mil seiscentos e sessenta":"1.660",
 "quatrocentos e setenta e dois":"472","oitocentos e vinte e oito":"828","cento e trinta mil":"130 mil","vinte e oito mil":"28 mil","trezentas mil":"300 mil",
 "treze andares":"13 andares","cento e noventa e quatro":"194","um metro e meio":"1,5 metro","quarenta e três metros":"43 metros","três metros e setenta":"3,70 metros",
 "trinta quilômetros":"30 quilômetros","doze estacas":"12 estacas","cento e vinte dias":"120 dias","em setenta":"em 70","oitenta e sete toneladas":"87 toneladas","trinta e seis metros":"36 metros",
 "cinco metros":"5 metros","noventa megapascais":"90 megapascais","vinte e cinco ou trinta":"25 ou 30","entre trezentas e quatrocentas":"entre 300 e 400","uns duzentos carros":"uns 200 carros",
 "sete mil setecentos e quarenta":"7.740","quatro metros e meio":"4,5 metros","vinte e sete graus":"27 graus","vinte e quatro":"24","doze mil":"12 mil","mil e oitocentas":"1.800",
 "cinquenta andares":"50 andares","quase cem":"quase 100","sessenta e setenta":"60 e 70","cinquenta e cinco metros":"55 metros","dois graus":"2 graus","duzentos e oitenta":"280",
 "novecentas e vinte e cinco":"925","vinte e oito metros":"28 metros","três andares":"3 andares","quatro anos":"4 anos","quinhentos metros":"500 metros","quatro quadras":"4 quadras","quatro Torres":"4 Torres"}
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
res["total"]=round(off-GAP+14.0,3)
json.dump(res,open("timeline.json","w"),ensure_ascii=False,indent=1)
print(res["total"]); 
