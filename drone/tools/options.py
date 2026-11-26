import math, numpy as np, json
E=1800.0
def run(at=4, hs=5, hp=8, ht=3, wb=8, wt=4, r1=98, rho=1.27e-3*0.92):
    def section(r):
        w=22+(15-22)*(r-30)/85
        if abs(r-58)<1.6 or abs(r-82)<1.6: w-=3.6
        parts=[(w,at,0.0)]
        if 41<=r<=r1:
            h=hs+(hp-hs)*(r-41)/9 if r<50 else hp+(ht-hp)*(r-50)/(r1-50)
            wbr=wb if r<=50 else wb+((wb-2)-wb)*(r-50)/(r1-50)
            n=20
            for k in range(n): parts.append((wbr+(wt-wbr)*(k+0.5)/n,h/n,at+k*h/n))
        A=sum(a*b for a,b,c in parts); zc=sum(a*b*(c+b/2) for a,b,c in parts)/A
        I=sum(a*b**3/12+a*b*(c+b/2-zc)**2 for a,b,c in parts); zt=max(c+b for a,b,c in parts)
        return A,I,max(zc,zt-zc)
    rs=np.linspace(41,115,741); dr=rs[1]-rs[0]; sec=[section(r) for r in rs]
    d1=sum((115-r)**2/(E*I) for r,(A,I,c) in zip(rs,sec))*dr; k=1/d1
    m_arm=rho*sum(A for A,I,c in sec)*dr
    f=1/(2*math.pi)*math.sqrt(k*1000/((39.1+0.24*m_arm)/1000))
    smax=max(15.7*(115-r)*c/I for r,(A,I,c) in zip(rs,sec))
    whole=rho*(sum(A for A,I,c in sec)*dr)   # beyond clamp only
    return k,f,m_arm,smax
opts=[('current: t4, spine 5/8/3, w 8→4',dict()),
      ('t5',dict(at=5)),
      ('spine 7/12/4',dict(hs=7,hp=12,ht=4)),
      ('spine 7/12/4, w 10→5',dict(hs=7,hp=12,ht=4,wb=10,wt=5)),
      ('t5 + spine 7/12/4, w 10→5',dict(at=5,hs=7,hp=12,ht=4,wb=10,wt=5)),
      ('t5 + spine 8/14/5, w 10→6',dict(at=5,hs=8,hp=14,ht=5,wb=10,wt=6))]
for n,o in opts:
    k,f,m,s=run(**o); print(f"{n:34s} k={k:6.1f} N/mm  f={f:5.0f} Hz  arm(out of clamp)={m:5.1f} g  σmax={s:5.1f} MPa")
