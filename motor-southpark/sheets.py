import sys
from main import *
ep=int(sys.argv[1])
c=setup(ep,'D',2.5,'x')
ts=[0.3,1.5]+[c.S[i]+min(1.2,(c.E[i]-c.S[i])*.6) for i in range(1,len(c.S)-1)]+[c.rt+.3,c.E[-2]+.8,c.S[-1]+.6,c.E[-1]+.9]
sheet(ep,'D',2.5,'x',ts,f'out/sheet{ep}.png')
