"""Rectilinear camera guides sampled from our corrected v44 panorama.

The source is synthetic geometry, not a user photograph.  This is a visual
guide for separate realistic interpretations; corridor geometry is provisional.
"""
from pathlib import Path
from math import radians, tan
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
directory=ROOT/'Прихожая'
source=np.asarray(Image.open(directory/'92_панорама_уточненная_геометрия_v44.png').convert('RGB'))
sh,sw=source.shape[:2]
W,H=1200,900
half=tan(radians(90/2))
sx,sy=np.meshgrid(np.linspace(-half,half,W), np.linspace(half*H/W,-half*H/W,H))
for yaw,name in ((-100,'слева'),(100,'справа'),(180,'назад')):
    theta=np.deg2rad(yaw)+np.arctan(sx)
    phi=np.arctan2(sy,np.sqrt(1+sx*sx))
    u=(((np.rad2deg(theta)+135)%360)/360*sw).astype(int)%sw
    v=np.clip(((60-np.rad2deg(phi))/120*(sh-1)).astype(int),0,sh-1)
    path=directory/f'94_панорама_уточненная_геометрия_{name}_v44.png'
    Image.fromarray(source[v,u]).save(path)
    print('Saved',path)
