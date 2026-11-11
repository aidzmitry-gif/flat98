"""Geometric camera guide for APT-001 hallway v39 with open furniture doors.

Pinhole blockout at the D2 threshold. Hall B01 and furniture proposal are in
millimetres. Open angles are illustrative and not a collision or safety check.
The actual electrical-panel size, position and ability to relocate are unknown.
"""
from __future__ import annotations

from math import cos, radians, sin, tan
from pathlib import Path
import importlib.util

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Прихожая"/"74_прихожая_геометрия_открытый_шкаф_v40.png"
spec=importlib.util.spec_from_file_location("camera35",ROOT/"tools"/"render_hallway_kitchen_view_v35.py")
camera=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(camera)
W,H=camera.W,camera.H
CAM,FWD,RIGHT,UP,FOV=camera.CAM,camera.FWD,camera.RIGHT,camera.UP,camera.FOV

assert 25+575+1050+25==1675
assert 550+446+3*18==1050
assert 575-250==325


def make(door_angle_deg=70.0, strict_visibility=True, closed_doors=False):
    half=tan(radians(FOV/2))
    xx=np.linspace(-half,half,W,dtype=np.float32)
    yy=np.linspace(half*H/W,-half*H/W,H,dtype=np.float32)
    sx,sy=np.meshgrid(xx,yy)
    rays=np.stack(tuple(FWD[i]+sx*RIGHT[i]+sy*UP[i] for i in range(3)),axis=-1)
    inv=1.0/np.where(abs(rays)<1e-7,np.float32(1e-7),rays)
    depth=np.full((H,W),np.inf,np.float32)
    ids=np.zeros((H,W),np.int16)
    rgb=np.empty((H,W,3),np.uint8); rgb[:]=(214,232,228)

    tfloor=-CAM[2]*inv[:,:,2]
    fx=CAM[0]+tfloor*rays[:,:,0]; fy=CAM[1]+tfloor*rays[:,:,1]
    floor=(tfloor>1)&(fy>-100)&(fy<3500)&(fx>-1800)&(fx<4000)
    depth[floor]=tfloor[floor];ids[floor]=1
    tint=np.where((np.floor(fx/180)%2)==0,0,7).astype(np.uint8)
    for c,base in enumerate((205,190,169)):rgb[:,:,c][floor]=np.clip(base+tint[floor],0,255)

    tceil=(2750-CAM[2])*inv[:,:,2]
    cx=CAM[0]+tceil*rays[:,:,0];cy=CAM[1]+tceil*rays[:,:,1]
    ceiling=(tceil>1)&(cy>0)&(cy<2300)&(cx>-1000)&(cx<4000)&(tceil<depth)
    depth[ceiling]=tceil[ceiling];ids[ceiling]=2;rgb[ceiling]=(230,225,216)

    def box(lo,hi,color,obj):
        lo=np.asarray(lo,np.float32);hi=np.asarray(hi,np.float32)
        a=(lo-CAM)*inv;b=(hi-CAM)*inv
        near=np.minimum(a,b);far=np.maximum(a,b)
        tn=near.max(axis=2);tf=far.min(axis=2)
        hit=(tf>=np.maximum(tn,.1))&(tn>.1)&(tn<depth)
        if not hit.any():return
        axis=near.argmax(axis=2);shade=np.choose(axis,(1.0,.90,1.06))
        for c in range(3):
            ch=np.clip(color[c]*shade,0,255).astype(np.uint8);rgb[:,:,c][hit]=ch[hit]
        depth[hit]=tn[hit];ids[hit]=obj

    def upright(a,b,z0,z1,color,obj,offset_toward_camera=0):
        a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
        u=b-a; n=np.array((-u[1],u[0]),dtype=np.float64); n/=np.linalg.norm(n)
        if np.dot(CAM[:2]-(a+b)/2,n)<0:n=-n
        a=a+offset_toward_camera*n;b=b+offset_toward_camera*n;u=b-a
        den=rays[:,:,0]*n[0]+rays[:,:,1]*n[1]
        den=np.where(abs(den)<1e-8,np.float32(1e-8),den)
        t=((a[0]-CAM[0])*n[0]+(a[1]-CAM[1])*n[1])/den
        hx=CAM[0]+t*rays[:,:,0];hy=CAM[1]+t*rays[:,:,1];hz=CAM[2]+t*rays[:,:,2]
        f=((hx-a[0])*u[0]+(hy-a[1])*u[1])/(u@u)
        hit=(t>.1)&(t<depth)&(f>=0)&(f<=1)&(hz>=z0)&(hz<=z1)
        if not hit.any():return
        rgb[hit]=color;depth[hit]=t[hit];ids[hit]=obj

    # Hall shell and D2. Corridor beyond Y=1675 is deliberately left unmodelled.
    box((-80,0,0),(0,1675,2750),(213,205,193),3)
    box((0,-80,0),(610,0,2750),(218,211,201),4)
    box((1620,-80,0),(2090,0,2750),(218,211,201),4)
    box((610,-80,2150),(1620,0,2750),(218,211,201),4)
    box((610,-20,0),(1620,5,2150),(43,43,42),5)
    for ya,yb in ((0,565),(1475,1675)):
        box((2090,ya,0),(2250,yb,2750),(220,214,205),6)
    box((2090,565,2150),(2250,1475,2750),(220,214,205),6)

    # Tall cabinet: x depth 580; y=600..1650 gives width 1050 along wall.
    # From entry to corridor: 18 + 446 + 18 + 550 + 18 mm.
    wood=(177,142,104);inside=(198,167,128)
    box((0,600,0),(580,1650,80),wood,10)
    box((0,600,2682),(580,1650,2700),wood,10)
    box((0,600,80),(580,618,2682),wood,10)
    box((0,1064,80),(580,1082,2682),wood,10)
    box((0,1632,80),(580,1650,2682),wood,10)
    box((0,618,80),(18,1632,2682),inside,11)
    # Unknown panel is only a neutral approximate placeholder and is NOT to scale.
    box((20,1180,930),(45,1530,1530),(226,226,216),12)
    box((0,618,2132),(580,1064,2150),wood,13)
    box((0,618,362),(580,1064,380),wood,13)
    box((270,630,1738),(285,1052,1750),(64,71,61),14)
    for y,color in ((675,(173,169,145)),(800,(132,147,127)),(925,(194,155,109))):
        box((260,y,730),(310,y+75,1725),color,15)

    # Bench and top unit adjacent to D1. Upper fronts are shown open.
    box((0,25,460),(32,600,2150),(127,143,114),20)
    box((0,25,2150),(420,600,2168),wood,21)
    box((0,25,2682),(420,600,2700),wood,21)
    box((0,25,2168),(420,43,2682),wood,21)
    box((0,582,2168),(420,600,2682),wood,21)
    box((0,43,2168),(18,582,2682),inside,21)
    box((35,25,400),(420,600,425),(167,133,98),22)
    box((35,25,425),(420,600,460),(222,211,193),23)
    box((40,350,310),(418,600,400),(186,154,119),24)
    for y in (125,300,475):box((33,y,1480),(65,y+20,1540),(63,61,53),25)
    for x,y,h,color in ((110,90,290,(88,76,65)),(110,180,290,(88,76,65)),(125,370,115,(128,119,104)),(125,455,115,(128,119,104))):
        box((x,y,0),(x+230,y+65,h),color,26)

    # Four independently hinged furniture leaves, rendered at 70 degrees as a
    # visual example only. Hinges, actual opening, and safety are not checked.
    angle=radians(door_angle_deg)
    def end(a,length,direction):
        return np.asarray(a)+np.array((sin(angle)*length,direction*cos(angle)*length))
    service_a=np.array((580.,1650.));service_b=end(service_a,574,-1)
    coat_a=np.array((580.,600.));coat_b=end(coat_a,470,1)
    upper_a=np.array((420.,600.));upper_b=end(upper_a,284.5,-1)
    upper2_a=np.array((420.,25.));upper2_b=end(upper2_a,284.5,1)
    if closed_doors:
        box((580,1076,80),(586,1650,2695),(180,145,108),30)
        box((580,600,80),(586,1074,2695),(180,145,108),31)
        box((587,640,140),(590,1025,2500),(147,177,173),32)
        box((420,25,2168),(426,600,2695),(180,145,108),33)
    else:
        upright(service_a,service_b,80,2695,(180,145,108),30)
        upright(coat_a,coat_b,80,2695,(180,145,108),31)
        # Approximate mirror belongs to the exterior of the open coat door.
        m0=coat_a+(coat_b-coat_a)*.10;m1=coat_a+(coat_b-coat_a)*.90
        upright(m0,m1,140,2500,(147,177,173),32,4)
        upright(upper_a,upper_b,2168,2695,(180,145,108),33)
        upright(upper2_a,upper2_b,2168,2695,(180,145,108),34)

    counts={name:int(np.count_nonzero(np.isin(ids,obj))) for name,obj in {
        "entrance":(5,),"panel_placeholder":(12,),"hanging_clothes":(15,),"bench":(20,21,22,23,24,25,26),
        "open_service_door":(30,),"open_mirror_door":(31,32),"upper_open_doors":(33,34)
    }.items()}
    if strict_visibility:
        assert min(counts.values())>50,counts
    else:
        assert counts["entrance"]>50,counts
    print("Visible-pixel check:",counts)
    Image.fromarray(rgb).save(OUT)
    print("Saved:",OUT)


if __name__=="__main__":make()
