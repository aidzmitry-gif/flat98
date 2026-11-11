"""Preliminary 360-degree visibility guide for APT-001, looking out from D4.

It uses the B01 spatial relationships and the v39 furniture proposal.  D1/D2
corner ties, complete corridor perimeter, exact camera position, D3-D5 clear
sizes and door swings are not verified.  Surfaces in the unmeasured corridor
are illustrative closures only and must never be used as a construction plan.
"""
from pathlib import Path
from math import radians
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Прихожая"
W, H = 3240, 1080
CAM = np.array((1120., 2200., 1600.), dtype=np.float32)
# Unwrap clockwise from the gap between the wardrobe and toilet openings.
# Entry is near the middle; the D4 toilet aperture appears at the far right.
yaw = np.deg2rad(np.linspace(-135., 225., W, endpoint=False, dtype=np.float32))
pitch = np.deg2rad(np.linspace(60., -60., H, dtype=np.float32))
th, ph = np.meshgrid(yaw, pitch)
rays = np.stack((np.sin(th)*np.cos(ph), -np.cos(th)*np.cos(ph), np.sin(ph)), axis=-1)
inv = 1 / np.where(abs(rays) < 1e-7, np.float32(1e-7), rays)
depth = np.full((H,W), np.inf, np.float32)
ids = np.zeros((H,W), np.int16)
rgb = np.full((H,W,3), (186,207,204), dtype=np.uint8)

def box(lo, hi, color, obj):
    lo, hi = np.asarray(lo,np.float32), np.asarray(hi,np.float32)
    aa, bb = (lo-CAM)*inv, (hi-CAM)*inv
    near, far = np.minimum(aa,bb), np.maximum(aa,bb)
    tn, tf = near.max(axis=2), far.min(axis=2)
    hit = (tf >= np.maximum(tn,.1)) & (tn > .1) & (tn < depth)
    if not np.any(hit): return
    axis = near.argmax(axis=2)
    shade = np.choose(axis,(1., .92, 1.04))
    for c in range(3):
        channel = np.clip(color[c]*shade,0,255).astype(np.uint8)
        rgb[:,:,c][hit] = channel[hit]
    depth[hit], ids[hit] = tn[hit], obj

# Floor/ceiling are purely illustrative beyond the surveyed B01 fragment.
box((-3000,-500,-40),(5000,4100,0),(195,176,151),1)
box((-2400,-100,2750),(4300,3150,2780),(227,223,213),2)

# Entry 3: full front-wall B01 chain and right D2 partition.
box((-80,0,0),(0,1675,2750),(220,213,203),3)
box((0,-80,0),(610,0,2750),(221,215,207),3)
box((1620,-80,0),(2090,0,2750),(221,215,207),3)
box((610,-80,2150),(1620,0,2750),(221,215,207),3)
box((610,-25,0),(1620,-15,2150),(39,39,39),10) # D1
for a,b in ((0,565),(1475,1675)):
    box((2090,a,0),(2250,b,2750),(220,214,205),3)
box((2090,565,2150),(2250,1475,2750),(220,214,205),3)
box((2400,565,0),(2410,1475,2150),(160,187,179),11) # D2 beyond

# Confirmed bedroom-to-entry wall, and ST-01 on kitchen side.  Their
# relationship to the unclosed corridor perimeter remains provisional.
box((-2030,1595,0),(0,1675,2750),(222,216,206),4)
box((2250,1595,0),(4110,1675,2750),(222,216,206),4)

# Bedroom P6 and child's room P2: openings, not assumed door leaves.
for x0,x1,ya,yb,code,col in ((-2160,-2030,1875,2815,12,(135,169,178)),
                              (4110,4240,1875,2785,13,(161,188,159))):
    box((x0,1675,0),(x1,ya,2750),(219,214,205),4)
    box((x0,yb,0),(x1,2945,2750),(219,214,205),4)
    box((x0,ya,2130),(x1,yb,2750),(219,214,205),4)
    xa = x0-180 if code==12 else x1+170
    box((xa,ya,0),(xa+10,yb,2130),col,code)

# Service-room frontage: three apertures D5/D4/D3.  Their clear sizes and
# leaves are unknown; colored planes are room placeholders for AI guidance.
for x0,x1 in ((-2030,-1500),(-790,760),(1570,2390),(3200,4110)):
    box((x0,2945,0),(x1,2975,2750),(222,215,205),5)
for x0,x1,h in ((-1500,-790,2050),(760,1570,2027),(2390,3200,2050)):
    box((x0,2945,h),(x1,2975,2750),(222,215,205),5)
# Backdrops span the room behind each aperture; otherwise oblique rays would
# incorrectly miss the doorway even after passing between its actual jambs.
for x0,x1,h,code,col in ((-1900,-160,2050,14,(181,155,177)),
                          (0,2090,2027,15,(185,177,165)),
                          (2250,3980,2050,16,(151,169,188))):
    box((x0,3200,0),(x1,3210,h),col,code)

# Confirmed v39 furniture arrangement; doors closed for panoramic overview.
wood=(174,137,98)
box((0,600,0),(580,1650,2700),wood,20)
box((581,1077,70),(588,1650,2695),(182,146,105),21)
box((581,600,70),(588,1075,2695),(171,180,170),22) # mirror-front hint
box((0,25,0),(420,600,400),(175,142,107),23)
box((0,25,400),(420,600,460),(222,211,195),23)
box((0,25,460),(35,600,2150),(128,144,115),23)
box((0,25,2150),(420,600,2700),wood,23)

out = OUT / "84_панорама_от_туалета_геометрия_v43.png"
Image.fromarray(rgb).save(out)
print("Saved", out)
for code,name in ((10,"D1 entry"),(11,"D2 kitchen"),(12,"P6 bedroom"),
                  (13,"P2 child"),(14,"D5 wardrobe"),(15,"D4 toilet"),
                  (16,"D3 bathroom"),(20,"hall cabinet")):
    ys,xs = np.where(ids==code)
    if len(xs):
        print(f"{name}: pixels={len(xs)}, x={xs.min()}..{xs.max()}, y={ys.min()}..{ys.max()}")
    else:
        print(f"{name}: OCCLUDED")

# Add guide-only numbers at the median of each visible colored placeholder.
im = Image.fromarray(rgb)
draw = ImageDraw.Draw(im)
font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",42)
for code,label in ((10,"D1"),(11,"D2"),(12,"P6"),(13,"P2"),(14,"D5"),(15,"D4"),(16,"D3")):
    ys,xs = np.where(ids==code)
    if not len(xs): continue
    x,y = int(np.median(xs)), int(np.median(ys))
    draw.rounded_rectangle((x-42,y-30,x+42,y+30),radius=12,fill=(19,71,68))
    bb=draw.textbbox((0,0),label,font=font)
    draw.text((x-(bb[2]-bb[0])/2,y-(bb[3]-bb[1])/2-bb[1]),label,font=font,fill="white")
out_annotated = OUT / "85_панорама_от_туалета_геометрия_метки_v43.png"
im.save(out_annotated)
print("Saved", out_annotated)
