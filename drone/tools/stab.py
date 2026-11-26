import sys
BATT_Y=float(sys.argv[1]) if len(sys.argv)>1 else -14.25
GOPRO=float(sys.argv[2]) if len(sys.argv)>2 else 0
NOMOUNT=len(sys.argv)>3 and sys.argv[3]=='nomount'
OUTF=sys.argv[4] if len(sys.argv)>4 else 'stability.json'
import numpy as np, re, json, math
def load(fn):
    d=open(fn,'rb').read()
    return np.array(re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)',d),dtype=float).reshape(-1,3,3)
CAN=np.array([[2,1,1],[1,2,1],[1,1,2]])/120.0
def mesh_props(fn):
    t=load(fn); a,b,c=t[:,0],t[:,1],t[:,2]
    det=np.einsum('ij,ij->i',a,np.cross(b,c))
    V=det.sum()/6; cg=((a+b+c)/4*det[:,None]).sum(0)/det.sum()
    A=np.stack([a,b,c],axis=2)                           # columns a,b,c
    C=np.einsum('n,nij,jk,nlk->il',det,A,CAN,A)          # second moment about origin (mm^5)
    return V, cg, C
# effective density (g/mm^3) = material density x print fill
RHO0={'arm':1.27e-3*0.92,'bottom_plate':1.27e-3*0.92,'top_plate':1.27e-3*0.92,'canopy':1.27e-3,'gps_xt60_mount':1.27e-3*0.75,
     'vtx_plate':1.27e-3,'cam_mount':1.21e-3*0.6,'antenna_mount':1.21e-3*0.6,'gopro_mount':1.21e-3*0.6}
RHO={k:v for k,v in RHO0.items() if not (NOMOUNT and k=='gopro_mount')}
items=[]   # (name, mass g, cg, inertia about own cg 3x3 g*mm^2)
for n,r in RHO.items():
    V,cg,C=mesh_props(n+'.stl'); m=V*r
    Cc=C*r - m*np.outer(cg,cg)                 # covariance about cg
    I=np.trace(Cc)*np.eye(3)-Cc
    items.append((n,m,cg,I,'printed'))
def box(name,m,c,dims,kind='bought'):
    a,b,h=dims; I=np.diag([m*(b*b+h*h)/12, m*(a*a+h*h)/12, m*(a*a+b*b)/12]); items.append((name,m,np.array(c,float),I,kind))
def cyl(name,m,c,d,h,kind='bought'):
    r=d/2; I=np.diag([m*(3*r*r+h*h)/12]*2+[m*r*r/2]); items.append((name,m,np.array(c,float),I,kind))
def pt(name,m,c,kind='hardware'): items.append((name,m,np.array(c,float),np.zeros((3,3)),kind))
mxy=116/math.sqrt(2); P=[(sx*mxy,sy*mxy) for sx in (-1,1) for sy in (-1,1)]
pt_=8  # plate top (arm 5 + plate 3)
box('ESC SpeedyBee BLS 55A',23.5,(0,0,pt_+5),(45.6,44,8))
box('FC SpeedyBee F405 V4',10.5,(0,0,pt_+14.4),(41.6,39.4,7.8))
box('VTX SpeedyBee TX800',5.6,(0,0,pt_+26.55),(28,28,5.5))
box('Camera Caddx Ratel 2',5.9,(0,37,pt_+14),(19,20,19))
for i,(x,y) in enumerate(P): cyl(f'Motor XING2 2207 #{i+1}',31.6,(x,y,5+9.55),29.08,19.1)
for i,(x,y) in enumerate(P): cyl(f'Prop Gemfan 51433 #{i+1}',3.8,(x,y,27.6),129.3,1.0)
box('Battery 6S 1200 (Tattu R-Line V5)',197,(0,BATT_Y,43+2+17),(40,78,34))
box('GPS Matek M10Q-5883',8,(0,-69.25,43+25.05+6.2),(20,20,12.4))
box('XT60 + 12AWG pigtail',8,(0,-76,43+2+4.2),(15.8,16,8.2))
pt('Receiver RP1',2.2,(0,-30,31),'bought'); pt('VTX antenna (SMA)',6,(0,-50,26),'bought')
for sx in (-1,1):
    for sy in (-1,1): pt('Standoff M3x30',1.25,(sx*16,sy*40,25))
for (x,y) in P: pt('Motor screws 4x M3x8',4*0.55,(x,y,2.5)); pt('Prop nut M5',1.5,(x,y,29))
for a in (45,135,225,315):
    r=math.radians(a); pt('Arm bolts 2x M3x12+nut',2*1.05,(31*math.cos(r),31*math.sin(r),6))
for sx in (-1,1):
    for sy in (-1,1): pt('Stack bolt M3x35+nut',2.3,(sx*15.25,sy*15.25,19)); pt('Standoff screws',1.1,(sx*16,sy*40,25))
pt('Tower bolts',1.9,(0,-58,45)); pt('Wiring, capacitor, solder',12,(0,0,16)); pt('Battery straps x2',15,(0,BATT_Y,62)); pt('Battery pad + grommets',4,(0,BATT_Y,44))
if GOPRO: box('GoPro HERO (with frame)',GOPRO,(0,40,43+3+12+9+20),(71,34,50),'bought')
M=sum(i[1] for i in items); cg=sum(i[1]*i[2] for i in items)/M
I=np.zeros((3,3))
for n,m,c,Ii,k in items:
    d=c-cg; I+=Ii+m*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
# thrust distribution to cancel the CG offset (X quad, yaw-neutral)
A=np.array([[1,1,1,1],[y for x,y in P],[x for x,y in P],[1,-1,-1,1]])  # sum, Mx~y, My~x, yaw (diag pairs)
b=np.array([1,cg[1],cg[0],0]); T=np.linalg.solve(A,b)              # thrust fractions
dev=(T/0.25-1)*100
prop_plane=27.6
# tip-over on landing: contacts = arm undersides out to the pad edge (r=131 on the diagonals)
e=132/math.sqrt(2)
edges=[e-cg[1], e+cg[1], e-cg[0], e+cg[0]]
tip=math.degrees(math.atan(min(edges)/cg[2]))
# ---- arm beam: cantilever fixed at the plate edge (r=41), tip load at the motor (r=115)
E=1800.0  # MPa = N/mm^2 (printed PETG, XY; Prusa 1.7-1.8 GPa)
def section(r):
    w=22+(15-22)*(r-30)/(116-30)
    if abs(r-58)<1.6 or abs(r-82)<1.6: w-=3.6          # zip-tie slots
    parts=[(w,5.0,0.0)]                                # (width, height, base z) rectangles stacked
    if 41<=r<=98:
        h=8+(14-8)*(r-41)/9 if r<50 else 14+(5-14)*(r-50)/48
        wb=10 if r<=50 else 10+(8-10)*(r-50)/48
        n=20
        for k in range(n):                             # trapezoid as thin strips
            z0=k*h/n; wk=wb+(6-wb)*(k+0.5)/n; parts.append((wk,h/n,5+z0))
    A=sum(w_*h_ for w_,h_,z_ in parts); zc=sum(w_*h_*(z_+h_/2) for w_,h_,z_ in parts)/A
    Iy=sum(w_*h_**3/12+w_*h_*(z_+h_/2-zc)**2 for w_,h_,z_ in parts)
    ztop=max(z_+h_ for w_,h_,z_ in parts)
    return A,Iy,max(zc,ztop-zc)
rs=np.linspace(41,116,751); dr=rs[1]-rs[0]
sec=[section(r) for r in rs]
def tip_deflection(F):   # unit-load method: delta = int M(r) m(r)/(EI) dr
    return sum(F*(116-r)*(116-r)/(E*Iy) for r,(A,Iy,c) in zip(rs,sec))*dr
def max_stress(F):
    return max(F*(116-r)*c/Iy for r,(A,Iy,c) in zip(rs,sec))
k=1/tip_deflection(1.0)          # N/mm
m_arm=1.27e-3*0.92*sum(A for A,Iy,c in sec)*dr     # g, beyond clamp
m_tip=31.6+3.8+2.2+1.5
f_n=1/(2*math.pi)*math.sqrt(k*1000/((m_tip+0.24*m_arm)/1000)) # Hz (k in N/m)
F_hover=M/4*9.81/1000; F60=1.021*9.81; F_max=1.6*9.81
res=dict(mass=M, cg=cg.tolist(), I_diag=np.diag(I).tolist(), thrust_frac=T.tolist(), dev_pct=dev.tolist(),
         prop_plane=prop_plane, cg_above_prop=cg[2]-prop_plane, tip_angle=tip, edge_min=min(edges),
         k=k, f_n=f_n, m_arm=m_arm,
         defl_hover=tip_deflection(F_hover), defl_60=tip_deflection(F60), defl_max=tip_deflection(F_max),
         stress_hover=max_stress(F_hover), stress_60=max_stress(F60), stress_max=max_stress(F_max),
         F_hover_g=M/4, T60_total=4*1021, tw60=4*1021/M,
         beam=[(float(r),float(A),float(Iy)) for r,(A,Iy,c) in list(zip(rs,sec))[::37]])
groups={}
for n,m,c,Ii,kk in items:
    key=re.sub(r' #\d+','',n); groups.setdefault(key,[0,kk]); groups[key][0]+=m
res['groups']=groups
json.dump(res,open(OUTF,'w'),indent=1)
print(f"AUW {M:.0f} g   CG x={cg[0]:.2f} y={cg[1]:.2f} z={cg[2]:.1f} mm")
print(f"Ixx {I[0,0]/1e6:.3f}  Iyy {I[1,1]/1e6:.3f}  Izz {I[2,2]/1e6:.3f} kg*m^2 x1e-3 (g*mm^2/1e6)")
print("thrust share per motor (% of hover) dev:", [f"{d:+.1f}" for d in dev], [P[i] for i in range(4)])
print(f"CG above prop plane {cg[2]-prop_plane:.1f} mm; tip-over angle {tip:.0f} deg (edge {min(edges):.1f} mm)")
print(f"arm k={k:.2f} N/mm  m_arm={m_arm:.1f} g  f_n={f_n:.0f} Hz")
for lab,F in (('hover',F_hover),('60%',F60),('max est',F_max)):
    print(f"  {lab:8s} F={F:5.2f} N  tip defl={tip_deflection(F):.2f} mm  max stress={max_stress(F):.1f} MPa")
for g,(m,kk) in sorted(groups.items(), key=lambda t:-t[1][0]): print(f"   {g:38s}{m:6.1f}")
