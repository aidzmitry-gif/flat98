
from pathlib import Path
import math, os, sys
import glfw
import numpy as np
from PIL import Image
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

OUT = Path(__file__).parent
W,H = 1800,1400
S=2048
def unit(a):
    a=np.asarray(a,float)
    return a/np.linalg.norm(a)
def look(a,b,up=(0,0,1)):
    a=np.asarray(a,float); f=unit(np.asarray(b)-a); s=unit(np.cross(f,up)); u=np.cross(s,f)
    return np.array([(*s,-s@a),(*u,-u@a),(*(-f),f@a),(0,0,0,1)])
def persp(deg, aspect, near, far):
    f=1/math.tan(math.radians(deg)/2)
    return np.array([[f/aspect,0,0,0],[0,f,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]])
def orth(l,r,b,t,n,f):
    return np.array([[2/(r-l),0,0,-(r+l)/(r-l)],[0,2/(t-b),0,-(t+b)/(t-b)],[0,0,-2/(f-n),-(f+n)/(f-n)],[0,0,0,1]])

def rgb(s):
    return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))
wall=rgb('e3d8c4'); windowWhite=rgb('f3eadd'); oak=rgb('bf9667')
paleOak=rgb('d1af83'); green=rgb('87926b'); cream=rgb('e6dbca')
olive=rgb('747d59'); linen=rgb('e6d8c1'); dark=rgb('46443b')
yellow=rgb('fbc97a'); shadow=rgb('c1ac93'); white=rgb('eee4d3')
V=[]
group_transform=None
def vertex(p,n,c,mat,uv):
    p=np.array(p); n=np.array(n)
    if group_transform:
        rotation,origin=group_transform
        p=rotation@p+origin
        n=rotation@n
    V.append((*p,*n,*c,mat,*uv))
def face(points,c,mat=0,n=None,uv=None):
    uv=uv if uv is not None else [(0,0)]*len(points)
    if n is None:
        n=unit(np.cross(np.asarray(points[1])-points[0],np.asarray(points[2])-points[0]))
    norms=[n]*len(points) if np.asarray(n).ndim==1 else n
    for i in range(1,len(points)-1):
        for j in (0,i,i+1):
            vertex(points[j],norms[j],c,mat,uv[j])
def box(x,y,z,a,b,h,c,mat=0,r=0):
    lo=np.array((x,y,z),float)
    size=np.array((a,b,h),float)
    if min(size)<=0:return
    center=lo+size/2
    half=size/2
    radius=min(r, min(size)/2-.01)
    if radius <= 0:
        for fix in range(3):
            i,j=(fix+1)%3,(fix+2)%3
            for side in (-1,1):
                pts=[]
                for u,v in ((-1,-1),(1,-1),(1,1),(-1,1)):
                    p=center.copy()
                    p[fix]+=side*half[fix];p[i]+=u*half[i];p[j]+=v*half[j]
                    pts.append(p)
                n=np.zeros(3);n[fix]=side
                face(pts,c,mat,n)
        return
    core=half-radius
    def axis_samples(dim):
        border=[-half[dim],-half[dim]+radius*.29,-core[dim],core[dim],half[dim]-radius*.29,half[dim]]
        return np.unique(border)
    for fix in range(3):
        i,j=(fix+1)%3,(fix+2)%3
        for side in (-1,1):
            grid=[]
            for u in axis_samples(i):
                row=[]
                for v in axis_samples(j):
                    p=np.zeros(3)
                    p[fix]=side*half[fix]; p[i]=u; p[j]=v
                    base=np.clip(p,-core,core); n=unit(p-base)
                    row.append((center+base+radius*n,n))
                grid.append(row)
            for k in range(len(grid)-1):
                for l in range(len(grid[k])-1):
                    vs=(grid[k][l],grid[k+1][l],grid[k+1][l+1],grid[k][l+1])
                    face([v[0] for v in vs],c,mat,[v[1] for v in vs])
def rod(a,b,r,c,mat=0,segments=14):
    a=np.array(a,float); b=np.array(b,float); axis=unit(b-a)
    seed=(0,0,1) if abs(axis[2])<.8 else (1,0,0)
    i=unit(np.cross(axis,seed)); j=np.cross(axis,i)
    normals=[i*math.cos(k*2*math.pi/segments)+j*math.sin(k*2*math.pi/segments) for k in range(segments+1)]
    for u,v in zip(normals,normals[1:]):
        face([a+r*u,a+r*v,b+r*v,b+r*u],c,mat,[u,v,v,u])
        face([a,a+r*u,a+r*v],c,mat,-axis)
        face([b,b+r*u,b+r*v],c,mat,axis)
def ellipsoid(center,scale,c,mat=0,steps=22):
    center=np.array(center); scale=np.array(scale)
    for i in range(steps):
        for j in range(steps//2):
            p=[]; n=[]
            for u,v in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
                a=u*2*math.pi/steps;b=v*math.pi/(steps//2)
                vec=np.array((math.cos(a)*math.sin(b),math.sin(a)*math.sin(b),math.cos(b)))
                p.append(center+scale*vec);n.append(unit(vec/scale))
            face(p,c,mat,n)
def torus(center,r,tube,c):
    center=np.array(center,float)
    for i in range(32):
        for j in range(10):
            p=[];n=[]
            for u,v in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
                a=u*2*math.pi/32;b=v*2*math.pi/10
                rad=np.array((math.cos(a),0,math.sin(a)))
                N=math.cos(b)*rad+np.array((0,math.sin(b),0))
                p.append(center+r*rad+tube*N);n.append(N)
            face(p,c,1,n)
def star(x,y,z,r,on):
    points=[(x,y+math.sin(i*math.pi/5)*(r if i%2==0 else r*.49),z+math.cos(i*math.pi/5)*(r if i%2==0 else r*.49)) for i in range(10)]
    center=(x,y,z); color=rgb('ffe9b6') if on else cream
    for i in range(10):
        a,b=points[i-1],points[i]
        face([center,a,b],color,6 if on else 0,(-1,0,0))
        face([a,b,(b[0]+14,*b[1:]),(a[0]+14,*a[1:])],oak,1)
def shelf(side):
    is_left=side==0
    x=0 if is_left else 2210
    # Openings are on the opposing X faces. Lower tambour is aligned with the outer carcass.
    back=x if is_left else x+581
    inner=x+583 if is_left else x
    box(back,10,761,19,489,1920,oak,1)
    for y in (10,482):
        box(x,y,755,600,18,1926,paleOak,1)
    levels=[753,1018,1292,1566,1840,2114,2390,2660]
    for z in levels:
        box(x+1,28,z,596,455,20,paleOak,1)
    box(x+3,21,71,594,472,655,cream,0,4)
    box(x+5,26,0,590,463,65,olive)
    box(inner,38,81,16,445,623,green,0,2)
    for z in range(98,703,18):
        box(inner+(-1 if is_left else -1),42,z,18,438,2,olive)
    bx=inner+16 if is_left else inner-9
    box(bx,214,675,7,83,8,oak,1,2)
    for k,z in enumerate(levels[1:6]):
        lampx=x+533 if is_left else x+58
        box(lampx,45,levels[k+2]-8,9,425,4,yellow,6)
        if k in (0,2,3):
            for i in range(6):
                height=100+(i*31+k*18)%95
                clr=[rgb('ddd0b3'),rgb('909c75'),rgb('b97f65'),rgb('e8ddcb'),rgb('b5aa8d'),rgb('d2bc93')][i]
                bookx=x+290 if is_left else x+83
                box(bookx,64+i*52,z+22,215,31+(i%2)*8,height,clr,7,2)
        elif k==1:
            px=x+425 if is_left else x+163
            rod((px,263,z+23),(px,263,z+105),62,rgb('e8dac3'),0)
            for i in range(9):
                a=i*2.4; tx=px+75*math.cos(a);ty=263+75*math.sin(a);tz=z+160+i%3*30
                rod((px,263,z+94),(tx,ty,tz),2,olive)
                ellipsoid((tx,ty,tz),(54,31,13),[green,olive,rgb('657653')][i%3],0,12)
        elif k==4:
            xx=x+281 if is_left else x+86
            box(xx,85,z+21,225,316,150,rgb('c3a584'),7,9)
            box(xx+4,91,z+159,222,310,14,linen,7,4)
            box(xx+(216 if is_left else -2),210,z+104,7,52,13,dark,0,3)
def wardrobe(left=False):
    x=0 if left else 2210
    carcass=x if left else x+19
    box(carcass,500,55,581,800,2629,cream)
    box(x+2,508,0,597,784,56,olive)
    for i in range(2):
        yy=507+i*396
        face_x=(x+581 if left else x)+( -7 if left and i else 7 if i else 0)
        box(face_x,yy,57,19,389,2619,white if i==0 else cream,0,3)
        handle=face_x+(18.8 if left else -.2)
        box(handle,yy+(350 if i==0 else 30),795,.4,18,470,olive,0,0)
def chair(x,y):
    matclr=rgb('dcc9b0')
    ellipsoid((x,y-2,436),(181,164,46),matclr,7,32)
    ellipsoid((x,y+125,619),(200,70,172),matclr,7,32)
    for xx in (-150,150):
        ellipsoid((x+xx,y+70,506),(48,123,69),matclr,7,22)
    rod((x,y,135),(x,y,410),25,dark)
    for i in range(5):
        angle=i*2*math.pi/5+.2
        dx,dy=178*math.cos(angle),178*math.sin(angle)
        rod((x,y,151),(x+dx,y+dy,49),12,dark)
        ellipsoid((x+dx,y+dy,32),(21,19,20),dark,0,10)
def blanket(x,y,z,width,length,c):
    # A soft cloth surface with folds and a drooping visible edge.
    nx,ny=26,34
    def vertex_at(i,j):
        u,v=i/nx,j/ny
        wav=math.sin(v*20+.46*math.sin(u*13))
        if u < .075:
            q=u/.075
            xx=x-34+19*q
            drop=56*pow(1-q,1.28)
        else:
            xx=x-15+(u-.075)*(width+15)/.925
            drop=0
        yy=y+v*length-7*math.exp(-v*17)*(1+.2*math.sin(u*16))
        zz=z-drop+3.6*math.sin(u*26+v*10)+3.9*wav
        return np.array((xx,yy,zz))
    for i in range(nx):
        for j in range(ny):
            a,b,cc,dd=[vertex_at(u,v) for u,v in ((i,j),(i+1,j),(i+1,j+1),(i,j+1))]
            face([a,b,cc,dd],c,7,unit(np.cross(b-a,dd-a)))

def bed(future):
    # 2100 along the right wall and 1050 across it. The stair slot is at the window end.
    for x in (1760,2751):
        for y in (1737,3774):
            box(x,y,0,58,58,2685,cream,0,4)
    box(1760,1737,190,1050,2100,126,white,0,7)
    for i in range(3):
        y=1790+677*i
        box(1763,y,25,22,666,161,green,0,5)
        box(1758,y+270,146,8,120,11,olive,0,5)
    box(1817,1795,311,935,1970,143,linen,7,28)
    blanket(1825,1820,468,910,1300,green)
    box(1848,3404,446,772,335,103,white,7,39)
    box(1910,3370,486,370,275,112,olive,7,42)
    box(2505,3465,485,217,238,102,rgb('bfa47a'),7,40)
    box(1761,1738,1267,1049,2098,127,white,0,5)
    box(1775,1757,1243,14,1880,9,yellow,6)
    box(1768,1741,1394,1033,2078,29,paleOak,1)
    box(1766,1750,2642,44,2083,55,paleOak,1)
    for y in range(1818,3789,77):
        box(1769,y,1391,33,27,1259,paleOak,1,3)
    box(1766,3780,1381,1028,54,1302,cream)
    box(1803,1745,2642,962,52,55,paleOak,1,4)
    for x in range(1836,2370,73):
        box(x,1753,1386,26,33,1267,paleOak,1,3)
    if future:
        box(1817,1800,1422,932,1965,126,linen,7,25)
        blanket(1828,1820,1557,902,1328,green)
        box(1874,3420,1544,781,311,110,white,7,40)
        box(2574,3460,1590,181,212,102,green,7,37)
    else:
        # The upper frame is visible for comparison. The mattress is a future fit-out.
        box(1818,1806,1408,928,1952,18,paleOak,1)
    star(2781,2820,974,100,True)
    star(2781,3275,2110,109,future)
    for i in range(6):
        start=1760+i*175
        top=1390*(i+1)/6
        box(start,1300,0,174,437,top-28,cream,0,4)
        box(start,1300,top-28,176,437,28,white,0,5)
        box(start-2,1320,top-220,12,397,177,green,0,6)
        box(start-7,1470,top-86,7,88,13,olive,0,6)
def yend(x):
    return 3825+12*x/2810
def build_scene(future,wide):
    global group_transform,V
    V=[]; group_transform=None
    face([(0,0,0),(2810,0,0),(2810,3837,0),(0,3825,0)],rgb('c6ad8a'),2,(0,0,1))
    face([(0,3825,-133),(2810,3837,-133),(2810,3837,0),(0,3825,0)],shadow,0,(0,1,0))
    box(-95,0,-132,95,3825,132,shadow)
    if wide:
        box(-95,0,0,95,3825,110,cream)
        box(-95,-105,-132,3000,105,132,shadow)
    else:
        box(-98,0,0,98,3825,2716,wall)
    box(2810,0,-132,96,3837,2844,wall)
    box(2790,0,0,20,3837,82,cream)
    # Window bay follows the source wall chain 600-1600-610.
    sill=803; top=2320
    box(-96,-92,0,696,92,2716,wall)
    box(2200,-92,0,706,92,2712,wall)
    box(600,-92,0,1600,92,sill,wall)
    box(600,-92,top,1600,92,2714-top,wall)
    box(599,-63,774,1602,81,28,windowWhite,0,3)
    for x in (600,1377,2170):
        box(x,-57,sill,30,43,top-sill,windowWhite,0,3)
    for z in (sill,top-32):
        box(600,-58,z,1600,43,32,windowWhite,0,3)
    for x,w in ((628,749),(1407,763)):
        face([(x,-62,sill+28),(x+w,-62,sill+28),(x+w,-62,top-25),(x,-62,top-25)],
             white,4,(0,1,0),[(0,0),(1,0),(1,1),(0,1)])
        box(x,-10,1630,w,16,665,linen,5,1)
        box(x,4,2284,w,25,22,white,0,3)
        box(x,6,1627,w,14,15,cream,0,2)
    box(1344,-9,1380,13,18,65,white,0,3)
    box(1410,-9,1380,13,18,65,white,0,3)
    # A radiator is shown with illustrative size and valve location.
    for i in range(25):
        box(1006+33*i,44,189,29,87,400,white,0,7)
    box(1006,75,552,830,29,20,white,0,3)
    rod((1833,90,545),(1886,90,545),17,cream)
    box(1884,73,532,38,34,26,cream,0,5)
    for x in (1060,1812):
        rod((x,88,0),(x,88,204),12,white)
    # Desktop fills the wall-to-wall bay, continuing under both shelf stacks.
    box(0,3,725,2810,497,29,paleOak,1,4)
    for x in (608,1410):
        box(x,425,653,783,72,71,cream,0,4)
        box(x+313,497,681,118,6,9,oak,1,3)
    shelf(0); shelf(1); wardrobe()
    if future:
        wardrobe(True)
    chair(1000,923); chair(1800,923)
    rod((951,270,754),(951,270,778),74,cream)
    rod((951,270,778),(951,270,886),22,cream)
    ellipsoid((951,270,886),(89,89,56),cream,0,24)
    box(1570,221,756,217,165,10,linen,7,4)
    box(1590,230,766,196,145,4,white,0,2)
    box(1687,233,769,2,137,2,oak)
    # Wallpaper behind the right-hand bunk. One plane follows the wall.
    face([(2808,1729,255),(2808,3836,255),(2808,3836,2709),(2808,1729,2709)],
         linen,3,(-1,0,0),[(0,0),(1,0),(1,1),(0,1)])
    bed(future)
    if True:
        # Entry wall, with visible 910 mm opening at the bypass corner.
        box(-95,3825,0,95,93,(115 if os.environ.get("NUR_CAM")=="top" else 2716),wall)
        box(910,3829,0,1900,89,(115 if os.environ.get("NUR_CAM")=="top" else 2712),wall)
        if os.environ.get("NUR_CAM")!="top": box(0,3829,2140,910,89,576,wall)
        box(0,3815,0,31,31,2164,windowWhite,0,2)
        box(883,3817,0,31,31,2164,windowWhite,0,2)
        if os.environ.get("NUR_CAM")!="top": box(0,3817,2136,909,31,28,windowWhite,0,2)
        angle=math.radians(-90 if os.environ.get("NUR_CAM")=="top" else -90)
        R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
        group_transform=(R,np.array((32,3832,0)))
        box(0,-37,15,832,39,2103,cream,0,4)
        box(47,-39,130,735,5,1834,white,0,4)
        box(47,3,130,735,5,1834,white,0,4)
        rod((755,-40,1070),(755,-85,1070),9,dark)
        rod((755,-85,1070),(686,-85,1070),10,dark)
        rod((755,3,1070),(755,46,1070),9,dark)
        rod((755,46,1070),(686,46,1070),10,dark)
        group_transform=None
    box(0,3828,-85,910,865,85,rgb("c6ad8a"),2)
    box(-98,3917,0,98,778,2716,wall)
    box(910,3917,0,93,778,2716,wall)
    box(0,4695,0,1003,92,2716,rgb("dfd6c5"))
    # Sports setup occupies the 850 mm segment between the 910 mm opening and the bed.
    for x in (1015,1611):
        box(x,3716,0,42,105,2240,paleOak,1,7)
        box(x,3460,2204,42,339,42,paleOak,1,6)
        rod((x+21,3765,1975),(x+21,3495,2220),19,paleOak,1)
    for z in range(240,2160,197):
        rod((1036,3748,z),(1632,3748,z),16,paleOak,1)
    rod((1040,3480,2223),(1632,3480,2223),19,oak,1)
    ringz=1440 if future else 1930
    for x in (1186,1486):
        rod((x,3483,2226),(x,3483,ringz+83),5,rgb('a58057'),1)
        torus((x,3483,ringz),72,12,paleOak)
    if future:
        for i in range(3):
            box(1035,2035+600*i,2,600,596,56,green,7,12)
    else:
        for i in range(3):
            box(1035,3228,2+47*i,600,596,46,green,7,9)
    # Small play pieces stay away from the ring footprint and the door sweep.
    if not future:
        for i in range(3):
            box(175+77*i,1710+21*i,0,49,49,49,[paleOak,green,rgb('b98064')][i],1,5)
        rod((341,1814,5),(341,1814,59),25,paleOak,1)
    shadow_vertex_count=len(V)
    if not wide:
        box(-98,-92,2712,3004,3929,50,white)
        for y in (770,1670,2580):
            for x in (992,1610):
                rod((x,y,2703),(x,y,2713),42,cream)
                rod((x,y,2701),(x,y,2704),34,yellow,6)
    return np.asarray(V,np.float32),shadow_vertex_count


MURAL = OUT.parent / "Отделка" / "Лесные_обои_текстура.png"
vert=r"""
#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;
layout(location=2) in vec3 color;
layout(location=3) in float material;
layout(location=4) in vec2 tex;
uniform mat4 camera;
out vec3 pos; out vec3 nor; out vec3 col;
flat out int mat;
out vec2 uv;
void main(){
    pos=position; nor=normal; col=color; mat=int(material); uv=tex;
    gl_Position=camera*vec4(pos,1.0);
}
"""
frag=r"""
#version 330 core
in vec3 pos; in vec3 nor; in vec3 col;
flat in int mat; in vec2 uv;
uniform mat4 lightMatrix;
uniform sampler2D shadowMap;
uniform sampler2D muralMap;
uniform sampler2D outdoors;
uniform sampler2D oakFloor;
out vec4 pixel;
float hash(vec2 a){return fract(sin(dot(a,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){
    vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
float grain(vec2 p){
    return .96 + .025*sin(p.y*.22 + 2.2*noise(p*vec2(.012,.026))) +
            .028*noise(p*vec2(.033,.32)) + .014*sin(p.y*.75+6.*noise(p*vec2(.009,.034)));
}
float lit(vec3 n){
    vec4 clip=lightMatrix*vec4(pos,1);
    vec3 s=clip.xyz/clip.w*.5+.5;
    if(s.z>1. || s.z<0. || min(s.x,s.y)<.001 || max(s.x,s.y)>.999) return 1.;
    float answer=0.,nDot=max(dot(n,normalize(vec3(-.29,-.82,.61))),0.);
    float bias=mix(.0013,.00035,nDot);
    for(int i=-2;i<=2;i++) for(int j=-2;j<=2;j++)
        answer += step(s.z-bias,texture(shadowMap,s.xy+vec2(i,j)*.00105).r);
    return answer*.04;
}
vec3 trees(vec2 uv){
    vec3 sky=mix(vec3(.92,.88,.72),vec3(.70,.83,.87),smoothstep(.07,.96,uv.y));
    float high=0.43+noise(vec2(uv.x*5.,2.1))*.17+noise(vec2(uv.x*19.,1.2))*.10;
    float med=0.51+noise(vec2(uv.x*6.,6.1))*.19+noise(vec2(uv.x*31.,2.3))*.08;
    float fuzz=noise(uv*49.);
    sky=mix(sky,vec3(.59,.68,.50)+.12*noise(uv*31.),1.-smoothstep(med-.09,med+.06,uv.y));
    vec3 forest=mix(vec3(.32,.43,.25),vec3(.63,.68,.36),fuzz);
    sky=mix(sky,forest,1.-smoothstep(high-.09,high+.05,uv.y));
    sky=mix(sky,vec3(.92,.85,.71),.12);
    return sky;
}
void main(){
    vec3 n=normalize(nor);
    vec3 base=col;
    if(mat==1){
        vec2 p=abs(n.z)>.7?pos.xy:(abs(n.x)>.7?pos.zy:pos.zx);
        base*=grain(p);
    } else if(mat==2){
        if(pos.z<1. && n.z>.8){
            vec2 uvp=mat2(.70710678,-.70710678,.70710678,.70710678)*(pos.xy+vec2(40.,72.))/125.;
            vec2 cell=floor(uvp);
            float idx=mod(cell.x-cell.y,10.);
            bool horizontal=idx<5.;
            vec2 start=horizontal?vec2(cell.x-idx,cell.y):vec2(cell.x,cell.y-(9.-idx));
            vec2 tile=uvp-start;
            vec2 l=horizontal?tile:tile.yx;
            float edge=min(min(l.x,5.-l.x),min(l.y,1.-l.y));
            float id=hash(start);
            base*= .96+.135*id;
            vec2 tileUV=vec2(l.x*.20,l.y);
            if(id>.53) tileUV.x=1.-tileUV.x;
            if(id>.71 || id<.30) tileUV.y=1.-tileUV.y;
            vec3 oakPhoto=texture(oakFloor,tileUV).rgb;
            base=mix(base*1.025,oakPhoto,.54);
            base*=mix(.76,1.,smoothstep(.002,.014,edge));
            float border=min(min(pos.x,2810.-pos.x),min(pos.y,3830.-pos.y));
            base*=.88+.12*smoothstep(0.,205.,border);
        } else {
            base*=.97 + .025*sin(pos.z*2.) + .015*noise(pos.zy*.2);
        }
    } else if(mat==3){
        base=texture(muralMap,vec2(uv.x,uv.y)).rgb * .97;
    } else if(mat==4){
        vec2 q=vec2(uv.x,(uv.y-.04)*1.55);
        if(pos.x>1380.) q.x=1.-q.x;
        vec3 leaves=texture(outdoors,clamp(q,0.,1.)).rgb;
        pixel=vec4(mix(leaves,vec3(.93,.94,.89),.20),1);
        return;
    } else if(mat==5){
        base*=1. + .065*sin(pos.z*6.283185/19.) + .04*sin(pos.z*6.283185/9.5);
    } else if(mat==6){
        pixel=vec4(base,1); return;
    } else if(mat==7){
        base*=.97+.055*noise(pos.xy*.24+pos.zz*.14);
    }
    vec3 sun=normalize(vec3(-.29,-.82,.61));
    float shade=lit(n);
    float dn=max(dot(n,sun),0.);
    float up=max(n.z,0.);
    vec3 toWindow=vec3(1405.,25.,1480.)-pos;
    float distanceToWindow=length(toWindow);
    float windowFacing=.43+.57*max(0.,dot(n,normalize(toWindow)));
    float daylight=windowFacing*(.29/(1.+pow(distanceToWindow/1710.,1.66)));
    float ceilingSoft=.048 + .049*max(-n.z,0.);
    float sideBounce=.052*max(0.,dot(n,normalize(vec3(-1,0,.1))));
    vec3 baseLighting=vec3(.66+.094*up+ceilingSoft+sideBounce)+daylight*vec3(1.03,1.04,1.09);
    vec3 sunColor=.42*shade*dn*vec3(1.00,.9,.73);
    vec3 color=base*(baseLighting+sunColor);
    if(mat==7){
        vec3 sheen=vec3(.055,.052,.046)*up*exp(-abs(pos.y-2000.)/2900.);
        color+=sheen;
    }
    // Warm bounce under the bunk and at the integrated shelves.
    float bunk=(1.-smoothstep(320.,575.,abs(pos.x-2150.)))*(1.-smoothstep(932.,1120.,abs(pos.y-2750.)));
    float lowLight=exp(-abs(pos.z-1200.)/414.);
    color+=vec3(.107,.062,.021)*lowLight*bunk;
    float shelves=exp(-abs(pos.y-200.)/520.);
    float insideShelves=max(exp(-abs(pos.x-425.)/197.),exp(-abs(pos.x-2380.)/193.));
    color+=vec3(.126,.081,.030)*shelves*insideShelves*smoothstep(720.,1100.,pos.z);
    if(mat==3){
        float low=exp(-length((pos.yz-vec2(2820,974))/121.));
        float high=exp(-length((pos.yz-vec2(3275,2110))/121.));
        color += vec3(.18,.11,.034)*low;
        color += vec3(.08,.06,.026)*high;
        color += vec3(.09,.052,.014)*exp(-abs(pos.z-1210.)/115.);
    }
    color=pow(max(color,vec3(0)),vec3(.96));
    pixel=vec4(clamp(color,0.,1.),1);
}
"""
shadowV=r"""
#version 330 core
layout(location=0) in vec3 position;
layout(location=3) in float material;
flat out int surface;
uniform mat4 camera;
void main(){gl_Position=camera*vec4(position,1); surface=int(material);}
"""
shadowF=r"""
#version 330 core
flat in int surface;
void main(){if (surface == 4) discard;}
"""
def uniform(program,name,val):
    glUniformMatrix4fv(glGetUniformLocation(program,name),1,GL_TRUE,np.asarray(val,dtype=np.float32))
def bind_mesh(data):
    import ctypes
    vao=glGenVertexArrays(1);glBindVertexArray(vao)
    buf=glGenBuffers(1);glBindBuffer(GL_ARRAY_BUFFER,buf)
    glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,GL_STATIC_DRAW)
    offset=0
    for i,n in enumerate((3,3,3,1,2)):
        glVertexAttribPointer(i,n,GL_FLOAT,False,48,ctypes.c_void_p(offset*4))
        glEnableVertexAttribArray(i)
        offset+=n
    return vao,buf
def run():
    assert glfw.init()
    glfw.window_hint(glfw.VISIBLE,glfw.FALSE)
    glfw.window_hint(glfw.SAMPLES,4)
    window=glfw.create_window(W,H,"Nursery E02",None,None)
    assert window
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    painter=compileProgram(compileShader(vert,GL_VERTEX_SHADER),compileShader(frag,GL_FRAGMENT_SHADER))
    caster=compileProgram(compileShader(shadowV,GL_VERTEX_SHADER),compileShader(shadowF,GL_FRAGMENT_SHADER))
    depth=glGenTextures(1); glBindTexture(GL_TEXTURE_2D,depth)
    glTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,S,S,0,GL_DEPTH_COMPONENT,GL_FLOAT,None)
    for par in (GL_TEXTURE_MIN_FILTER,GL_TEXTURE_MAG_FILTER):
        glTexParameteri(GL_TEXTURE_2D,par,GL_NEAREST)
    fbo=glGenFramebuffers(1);glBindFramebuffer(GL_FRAMEBUFFER,fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,depth,0)
    glDrawBuffer(GL_NONE);glReadBuffer(GL_NONE)
    assert glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE
    glBindFramebuffer(GL_FRAMEBUFFER,0)
    texture=glGenTextures(1); glBindTexture(GL_TEXTURE_2D,texture)
    pic=Image.open(MURAL).convert("RGB").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,pic.width,pic.height,0,GL_RGB,GL_UNSIGNED_BYTE,pic.tobytes())
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
    glGenerateMipmap(GL_TEXTURE_2D)
    tex_extras=[]
    for name in ("outside.png","floorgrain.png"):
        tid=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,tid)
        art=Image.open(OUT/name).convert("RGB")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,art.width,art.height,0,GL_RGB,GL_UNSIGNED_BYTE,art.tobytes())
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        glGenerateMipmap(GL_TEXTURE_2D)
        tex_extras.append(tid)
    light=orth(-3400,3400,-2970,2970,10,14000)@look((-1130,-5700,6250),(1350,1710,900))
    preview="preview" in sys.argv
    for wide in (False,):
        if preview and not wide: continue
        for future in (True,):
            if preview and not future: continue
            data,shadow_vertex_count=build_scene(future,wide)
            print(f"{wide=} {future=} vertices {len(data)}",flush=True)
            vao,buf=bind_mesh(data)
            glBindFramebuffer(GL_FRAMEBUFFER,fbo);glViewport(0,0,S,S)
            glClear(GL_DEPTH_BUFFER_BIT)
            glUseProgram(caster);uniform(caster,"camera",light)
            glDrawArrays(GL_TRIANGLES,0,len(data))
            glBindFramebuffer(GL_FRAMEBUFFER,0);glViewport(0,0,W,H)
            glClearColor(.951,.944,.920,1);glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            glUseProgram(painter)
            if wide:
                if os.environ.get("NUR_CAM")=="top":
                    camera=persp(42,W/H,20,28000)@look((-1130,6640,7200),(1340,1860,1100))
                elif os.environ.get("NUR_CAM")=="alt":
                    camera=persp(34,W/H,20,28000)@look((-5950,2090,4700),(1320,1960,1310))
                else:
                    camera=persp(36,W/H,20,28000)@look((-5890,2170,5050),(1200,1900,1270))
            else:
                camera=persp(97,W/H,12,24000)@look((920,550,1570),(1670,3260,1240))
            camera[0,:] *= -1
            uniform(painter,"camera",camera);uniform(painter,"lightMatrix",light)
            glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,depth)
            glUniform1i(glGetUniformLocation(painter,"shadowMap"),0)
            glActiveTexture(GL_TEXTURE1);glBindTexture(GL_TEXTURE_2D,texture)
            glUniform1i(glGetUniformLocation(painter,"muralMap"),1)
            for unit_index,(name,tid) in enumerate(zip(("outdoors","oakFloor"),tex_extras),2):
                glActiveTexture(GL_TEXTURE0+unit_index)
                glBindTexture(GL_TEXTURE_2D,tid)
                glUniform1i(glGetUniformLocation(painter,name),unit_index)
            glDrawArrays(GL_TRIANGLES,0,len(data));glFinish()
            glPixelStorei(GL_PACK_ALIGNMENT,1)
            output=Image.frombytes("RGB",(W,H),glReadPixels(0,0,W,H,GL_RGB,GL_UNSIGNED_BYTE))
            output=output.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            output.save(OUT / (("wide" if wide else "selected")+("-future" if future else "-now")+".png"))
            glDeleteBuffers(1,[buf]);glDeleteVertexArrays(1,[vao])
    glfw.terminate()
if __name__=="__main__":
    run()












