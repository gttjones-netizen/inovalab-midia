import subprocess,re,json,sys
def segs(f,th=-38,d=0.55):
    r=subprocess.run(['ffmpeg','-i',f,'-af',f'silencedetect=n={th}dB:d={d}','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',r)]
    en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',r)]
    dur=float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',r).groups()[2])+60*int(re.search(r'Duration: (\d+):(\d+)',r).group(2))
    # speech = complement
    s=[];cur=0.0
    for a,b in zip(st,en+[dur]*(len(st)-len(en))):
        if a-cur>0.05: s.append((cur,a))
        cur=b
    if dur-cur>0.1: s.append((cur,dur))
    return s
for sp,n in [('N',42),('NEL',10),('VAL',4),('CID',6)]:
    for d in [0.55,0.7,0.9,1.1]:
        s=segs(sp+'.mp3',d=d)
        if len(s)==n: break
    print(sp,n,len(s),d)
    json.dump(s,open(sp+'_segs.json','w'))
