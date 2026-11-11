"""View from the B01 D4 toilet threshold towards entrance D1.

Reuses the v40 1050/575 furniture geometry. The D4 location is taken from the
B01 drawing (760 + 810 + 520 in room 7); the corridor link and exact camera
tie, D4 clear width and door leaves remain unverified. There is no artificial
partition closing the entry/corridor transition. This is a camera blockout,
not an open-door clearance or engineering safety check.
"""
from __future__ import annotations

import importlib.util
import sys
from math import cos, radians, sin
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("hallway40",ROOT/"tools"/"render_hallway_open_geometry_v40.py")
hall=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(hall)

# Local XY axes: X goes across entry from the left wall; Y goes from D1 toward
# corridor and toilet. D4 B01 segment is 760..1570, with provisional camera
# near its right-hand side. D1 centre is 1115 in the B01 dimension chain.
# The detailed B01 model puts the D4 plane ~1270 behind the 1675 entry fragment;
# this is a provisional model tie, not an on-site corridor measurement.
hall.CAM=np.array((1375.0,2945.0,1600.0))
direction=np.array((1115.0-hall.CAM[0],-2945.0,0.0));direction/=np.linalg.norm(direction)
pitch=radians(-5.0)
hall.FWD=np.array((direction[0]*cos(pitch),direction[1]*cos(pitch),sin(pitch)))
hall.RIGHT=np.array((-direction[1],direction[0],0.0))
hall.UP=np.array((-direction[0]*sin(pitch),-direction[1]*sin(pitch),cos(pitch)))
hall.FOV=120.0

assert 760+810+520==2090
assert 610+1010+470==2090
assert 25+1050+575+25==1675
assert 760 < hall.CAM[0] < 1570
assert abs(np.dot(hall.FWD,hall.RIGHT))<1e-8
assert abs(np.dot(hall.FWD,hall.UP))<1e-8

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "ajar"
    if mode=="ajar":
        hall.OUT=ROOT/"Прихожая"/"78_прихожая_от_туалета_полуоткрыто_v42.png"
        hall.make(door_angle_deg=30,strict_visibility=False)
    elif mode=="closed":
        hall.OUT=ROOT/"Прихожая"/"79_прихожая_от_туалета_закрыто_v42.png"
        hall.make(strict_visibility=False,closed_doors=True)
    else:
        raise ValueError("mode must be ajar or closed")
