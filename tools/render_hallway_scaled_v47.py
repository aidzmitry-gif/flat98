"""Render an undistorted, geometry-controlled APT-001 view/panorama.

The 3D shell uses the B01 fragment and v47 proposal in millimetres. Unclosed
corridor contours, leaf swings and the furniture inside adjoining rooms are
illustrative, not surveyed. Six 90-degree ray-traced views are reprojected to
a cylindrical 360 x 120 degree panorama; unlike an AI panorama the directions
and sizes come from the model. Room contents are intentionally simplified.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from PIL import Image
from hallway_dimensions_v47 import D

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tmp/b01-mitsuba-runtime'))
import mitsuba as mi
mi.set_variant('scalar_rgb')
T=mi.ScalarTransform4f

def linear(v):
    a=np.asarray(v,dtype=np.float32)
    return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)

def matte(hexrgb):
    h=hexrgb.lstrip('#'); rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return mi.load_dict({'type':'diffuse','reflectance':{'type':'rgb','value':linear(rgb).tolist()}})

def oak_bitmap():
    # Procedural herringbone used only as an approximate decor reference.
    width,depth=14.0,7.0
    x,y=np.meshgrid(np.linspace(0,width,1400),np.linspace(0,depth,700))
    pitch=.125*math.sqrt(2)
    u,v=(x+y)/pitch,(y-x)/pitch
    i,j=np.floor(u),np.floor(v)
    band=(i-j)%8
    horizontal=band<4
    row=np.where(horizontal,i-band,i);col=np.where(horizontal,j,j-(7-band))
    index=(np.sin(12.9898*row+78.233*col)*43758.5453)%1
    along=np.where(horizontal,u-row,v-col);cross=np.where(horizontal,v-col,u-row)
    drift=cross+.014*np.sin(along*1.8+index*9)
    seam=np.minimum.reduce((cross,1-cross,along,4-along))
    light=1+.11*(index-.5)+.014*np.sin(drift*91)+.01*np.sin(drift*193)-.09*np.exp(-(seam/.009)**2)
    srgb=np.clip(light[...,None]*np.array([.73,.67,.59]),0,1)
    return mi.load_dict({'type':'diffuse','reflectance':{'type':'bitmap','bitmap':mi.Bitmap(linear(srgb).astype(np.float32)),'raw':True,'filter_type':'bilinear'}})

WALL=matte('#e6ded1');CEIL=matte('#f2eadf');OAK=matte('#bc9873')
OAK_FRONT=matte('#c49c70');OLIVE=matte('#8c997b');CUSHION=matte('#e5d9c8')
BLACK=matte('#252628');MIRROR=matte('#9ca9a5');WHITE=matte('#eeeae3')
STONE=matte('#c8b8a8');GRAY=matte('#b5afa5');FLOOR=oak_bitmap()
parts={}

def xyz(p):
    # Plan x grows to the observer's right when facing the entrance.  The
    # reflection below converts this drawing convention to Mitsuba's axes.
    x,y,z=p
    return np.array((-x,y,z),dtype=float)/1000

def box(name,lo,hi,bsdf):
    assert all(b>a for a,b in zip(lo,hi)),(name,lo,hi)
    a,b=xyz(lo),xyz(hi); p,q=np.minimum(a,b),np.maximum(a,b)
    parts[name]={'type':'cube','to_world':T().translate((p+q)/2).scale((q-p)/2),'bsdf':bsdf}

def cylinder(name,p0,p1,radius,bsdf):
    parts[name]={'type':'cylinder','p0':xyz(p0).tolist(),'p1':xyz(p1).tolist(),'radius':radius/1000,'bsdf':bsdf}

def point(name,x,y,z,intensity=4.5):
    parts[name]={'type':'point','position':xyz((x,y,z)).tolist(),
                 'intensity':{'type':'rgb','value':[intensity,intensity*.94,intensity*.86]}}

# Floor extends beyond the known entry so openings have a visible threshold;
# exact external/corridor contours and resulting materials are conceptual.
box('floor_all',(-6000,-1900,-40),(8000,4800,0),FLOOR)
box('floor_room7',(0,2945,0),(2090,4685,5),STONE)
box('floor_room6',(2250,2945,0),(3980,4685,5),GRAY)
box('ceiling',(-6000,-1900,2750),(8000,4800,2790),CEIL)

# B01 hall: entry wall D1, left support wall and kitchen opening D2.
box('hall_left',(-80,0,0),(0,1875,2750),WALL)
box('entry_left',(0,-80,0),(610,0,2750),WALL)
box('entry_right',(1620,-80,0),(2090,0,2750),WALL)
box('entry_header',(610,-80,2150),(1620,0,2750),WALL)
box('entry_panel',(610,-25,0),(1620,-15,2150),BLACK)
box('entry_frame_left',(610,-15,0),(630,-5,2150),BLACK)
box('entry_frame_right',(1600,-15,0),(1620,-5,2150),BLACK)
box('kitchen_wall_1',(2090,0,0),(2250,565,2750),WALL)
box('kitchen_wall_2',(2090,1475,0),(2250,1675,2750),WALL)
box('kitchen_header',(2090,565,2150),(2250,1475,2750),WALL)
# D2 leads into the B01 kitchen: a far wall provides depth behind the opening.
box('kitchen_far',(2250,-1905,0),(7960,-1825,2750),WALL)
box('kitchen_outer',(7960,-1825,0),(8040,1675,2750),WALL)

# Known upper walls around the two wings; the complete corridor is unmeasured.
box('upper_left',(-2030,1805,0),(0,1875,2750),WALL)
box('upper_right',(2090,1675,0),(4110,1875,2750),WALL)
for side,x0,x1,ya,yb in (('p6',-2030,-1900,1875,2815),('p2',3980,4110,1875,2785)):
    box(side+'_wall_a',(x0,1675,0),(x1,ya,2750),WALL)
    box(side+'_wall_b',(x0,yb,0),(x1,2945,2750),WALL)
    box(side+'_header',(x0,ya,2130),(x1,yb,2750),WALL)
for i,(x0,x1) in enumerate(((-2030,-1500),(-790,760),(1570,2390),(3200,4110))):
    box('lower_'+str(i),(x0,2915,0),(x1,2945,2750),WALL)
for name,x0,x1,h in (('d5',-1500,-790,2050),('d4',760,1570,2027),('d3',2390,3200,2050)):
    box(name+'_head',(x0,2915,h),(x1,2945,2750),WALL)

# Subordinate rooms use known B01 extents but deliberately simplified interiors.
box('room7_back',(0,4685,0),(2090,4765,2617),WALL)
box('room6_back',(2250,4685,0),(3980,4765,2750),WALL)
box('room8_back',(-1900,4685,0),(-160,4765,2750),WALL)
for name,x0,x1 in (('side_8_7',-160,0),('side_7_6',2090,2250),('side_6_2',3980,4110)):
    box(name,(x0,2945,0),(x1,4685,2750),WALL)
box('side_5_8',(-2030,2815,0),(-1900,4685,2750),WALL)
# A gentle indication of washer/dryer and bath; not furniture dimension proof.
box('laundry_tower',(2800,4080,0),(3440,4685,1850),WHITE)
for i,z in enumerate((430,1280)):
    cylinder('washer_round_'+str(i),(3120,4064,z),(3120,4080,z),190,BLACK)
box('bath_base',(0,3085,0),(700,4685,520),WHITE)
box('vanity',(700,4335,0),(1380,4685,820),OAK)
box('vanity_top',(700,4335,820),(1380,4685,880),WHITE)
box('wc',(1490,4300,0),(1890,4660,420),WHITE)
box('wardrobe_shelf_a',(-1880,3150,1900),(-1450,4650,1950),OAK)
box('wardrobe_shelf_b',(-610,3150,1450),(-180,4650,1500),OAK)

# P6 and P2 far-wall windows follow B01, while room contents remain neutral.
for name,x0,x1 in (('bed',-5900,-5870),('child',7960,7990)):
    for ya,yb in ((1875,2475),(4075,4685)):
        box(name+'_wall_'+str(ya),(x0,ya,0),(x1,yb,2750),WALL)
    box(name+'_sill',(x0,2475,0),(x1,4075,800),WALL)
    box(name+'_head',(x0,2475,2200),(x1,4075,2750),WALL)
    box(name+'_window',(x0,2475,800),(x1,4075,2200),MIRROR)

# Furniture: 562-mm body + 18-mm doors = 580-mm overall closed depth.
body=D.wardrobe_depth-D.facade_thickness
box('wardrobe_body',(0,600,0),(body,1650,2700),OAK)
box('panel_face',(body,1076,40),(580,1650,2695),OAK_FRONT)
box('coat_mirror',(body,600,40),(580,1074,2695),MIRROR)
box('bench_back',(0,25,460),(32,600,2150),OLIVE)
box('bench_base',(35,25,400),(420,600,425),OAK)
box('bench_cushion',(35,25,425),(420,600,460),CUSHION)
box('slipper_drawer',(40,350,310),(418,600,400),OAK_FRONT)
box('bench_upper',(0,25,2150),(420,600,2700),OAK)
for i,(y,h) in enumerate(((30,290),(150,290),(300,120),(420,120))):
    box('shoe_'+str(i),(70,y,0),(370,y+110,h),BLACK)

for i,(x,y) in enumerate(((1000,800),(1000,2300),(-1100,2400),(3300,2400),
                          (1100,3800),(3000,3800),(-900,3800),(3800,800))):
    point('light_'+str(i),x,y,2500,4.0)
parts['environment']={'type':'constant','radiance':{'type':'rgb','value':[.18,.18,.18]}}

CAM=xyz((1120,2200,1600))
FACES=[('front',(0,-1,0),(0,0,1)),('right',(-1,0,0),(0,0,1)),
       ('back',(0,1,0),(0,0,1)),('left',(1,0,0),(0,0,1)),
       ('up',(0,0,1),(0,1,0)),('down',(0,0,-1),(0,-1,0))]

def render_face(fwd,up,size,spp):
    f=np.asarray(fwd,dtype=float);u=np.asarray(up,dtype=float)
    scene=mi.load_dict({'type':'scene','integrator':{'type':'path','max_depth':5},
        'sensor':{'type':'perspective','fov':90,'fov_axis':'x',
            'to_world':T().look_at(origin=CAM,target=CAM+f,up=u),
            'film':{'type':'hdrfilm','width':size,'height':size,'rfilter':{'type':'box'}}},**parts})
    return np.asarray(mi.render(scene,spp=spp,seed=19),dtype=np.float32)

def srgb(a):
    a=np.maximum(a,0)
    # Compress the sun-like highlights from the path tracer instead of
    # clipping walls and wood to pure white in the presentation image.
    a=a/(1+a)
    a=np.where(a<=.0031308,12.92*a,1.055*np.power(a,1/2.4)-.055)
    return (np.clip(a,0,1)*255+.5).astype(np.uint8)

def denoise_ldr(rgb,name):
    """Denoise this project's own noisy ray-traced render, not a source photo."""
    exe=ROOT/'tmp/b01-oidn-runtime/oidn-2.5.1.x64.windows/bin/oidnDenoise.exe'
    if not exe.exists():return rgb
    h,w,_=rgb.shape
    src=ROOT/f'tmp/hallway_v47_{name}.pfm';dst=ROOT/f'tmp/hallway_v47_{name}_clean.pfm'
    with src.open('wb') as f:
        f.write(f'PF\n{w} {h}\n-1.0\n'.encode('ascii'))
        np.asarray((rgb.astype(np.float32)/255)[::-1],dtype='<f4').tofile(f)
    subprocess.run([str(exe),'--ldr',str(src),'--srgb','--device','cpu',
                    '-q','high','-o',str(dst),'-v','0'],check=True)
    with dst.open('rb') as f:
        assert f.readline().strip()==b'PF'
        rw,rh=map(int,f.readline().split());scale=float(f.readline())
        values=np.fromfile(f,dtype='<f4' if scale<0 else '>f4').reshape(rh,rw,3)[::-1]
    assert (rw,rh)==(w,h) and np.isfinite(values).all()
    return (np.clip(values,0,1)*255+.5).astype(np.uint8)

def panorama(faces,w,h):
    theta=np.deg2rad(np.linspace(-135,225,w,endpoint=False))
    phi=np.deg2rad(np.linspace(60,-60,h))
    th,ph=np.meshgrid(theta,phi)
    ray=np.stack((-np.sin(th)*np.cos(ph),-np.cos(th)*np.cos(ph),np.sin(ph)),axis=-1)
    directions=np.array([f for _,f,_ in FACES],dtype=float)
    dots=np.einsum('hwc,kc->hwk',ray,directions)
    choice=dots.argmax(axis=2);out=np.zeros((h,w,3),np.float32)
    for i,(_,forward,up) in enumerate(FACES):
        mask=choice==i; f=np.array(forward,dtype=float);u=np.array(up,dtype=float)
        right=np.cross(f,u); denom=dots[:,:,i][mask]
        sx=(ray[mask]@right)/denom;sy=(ray[mask]@u)/denom
        n=faces[i].shape[0]
        ix=np.clip(((sx+1)*.5*(n-1)).astype(np.int32),0,n-1)
        iy=np.clip(((1-sy)*.5*(n-1)).astype(np.int32),0,n-1)
        out[mask]=faces[i][iy,ix]
    return srgb(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');opt=ap.parse_args()
    size,spp,w,h=(400,12,1200,400) if opt.preview else (880,48,2400,800)
    faces=[]
    for name,f,u in FACES:
        t=time.monotonic();faces.append(render_face(f,u,size,spp))
        print(name,'seconds',round(time.monotonic()-t,2),flush=True)
    image=Image.fromarray(denoise_ldr(panorama(faces,w,h),'panorama'))
    out=(ROOT/'tmp/hallway_scaled_v47_preview.png') if opt.preview else (ROOT/'Прихожая/114_панорама_масштабная_модель_v47.png')
    image.save(out);print('Saved',out,flush=True)
    # Forward 90-degree camera from the same physical point; not an AI render.
    forward=Image.fromarray(denoise_ldr(srgb(faces[0]),'forward'))
    out2=(ROOT/'tmp/hallway_forward_v47_preview.png') if opt.preview else (ROOT/'Прихожая/115_к_входу_масштабная_модель_v47.png')
    forward.save(out2);print('Saved',out2,flush=True)

if __name__=='__main__':main()
