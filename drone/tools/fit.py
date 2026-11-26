import subprocess, os, sys, json, concurrent.futures as cf
SCAD='/home/user/RickyBlackKat.github.io/drone/kat5.scad'; OUT=os.path.dirname(os.path.abspath(__file__))
def collide(kind, a, b, c):
    fn=f"{OUT}/t_{kind}_{a}_{b}_{c}.stl"
    r=subprocess.run(['openscad','-q','-D',f'part="{kind}"','-D',f'fa="{a}"','-D',f'fb="{b}"','-D',f'fc_={c}','-o',fn,SCAD],capture_output=True,text=True,timeout=900)
    empty = ('empty' in (r.stderr+r.stdout).lower()) or not os.path.exists(fn) or os.path.getsize(fn)<200
    if os.path.exists(fn): os.remove(fn)
    return not empty
STEPS=[0,0.5,1,2,3,5]
def clearance(kind,a,b):
    best=None
    for c in STEPS:
        if collide(kind,a,b,c): return best   # largest clearance that was still free
        best=c
    return best
# (frame part, component) and (component, component) pairs that can plausibly touch
FP=[('canopy','esc'),('standoffs','esc'),('cam_mount','esc'),('antenna_mount','esc'),
    ('canopy','fc'),('standoffs','fc'),
    ('top_plate','vtx'),('canopy','vtx'),('standoffs','vtx'),('vtx_plate','fc'),
    ('canopy','camera'),('cam_mount','camera'),('top_plate','camera'),('standoffs','camera'),
    ('arm','motors'),
    ('canopy','props'),('top_plate','props'),('bottom_plate','props'),('arm','props'),('gps_xt60_mount','props'),
    ('antenna_mount','props'),('gopro_mount','props'),
    ('gopro_mount','battery'),('gps_xt60_mount','battery'),
    ('gps_xt60_mount','gps'),('gps_xt60_mount','xt60')]
CC=[('camera','esc'),('camera','fc'),('vtx','fc'),('props','battery'),('props','gps'),('battery','gps')]
jobs={}
with cf.ThreadPoolExecutor(8) as ex:
    for a,b in FP: jobs[(a,b)]=ex.submit(clearance,'fit_pair',a,b)
    for a,b in CC: jobs[(b,a)]=ex.submit(clearance,'fit_cc',a,b)   # inflate first item
    res={f"{k[0]}|{k[1]}":v.result() for k,v in jobs.items()}
json.dump(res,open(f'{OUT}/fit_results.json','w'),indent=1)
for k,v in res.items(): print(f"{k:32s} {'COLLIDES' if v is None else ('>= '+str(v)+' mm' if v==5 else str(v)+' mm')}")
