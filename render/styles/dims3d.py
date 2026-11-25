# Padel court dimensions video, clean 3D style. Key frames first (CLAUDE.md), full render after approval.
from common import *
import clean3d as C3
from clean3d import items, poly, seg, proj, cam, render3d, F, INK, GREY, BGI, SS
FT=0.3048
# extra geometry: slab sides (pad 36' x 69'), clearance zone (48' x 81') on the ground
pw,pl=36*FT/2,69*FT/2; aw,al=48*FT/2,81*FT/2
items[0]=('poly',[(-pw,-pl,0),(pw,-pl,0),(pw,pl,0),(-pw,pl,0)],((205,207,210,255),None,0),'pad',0)
poly([(-aw,-al,-0.01),(aw,-al,-0.01),(aw,al,-0.01),(-aw,al,-0.01)],(150,190,160,90),None,0,'clear',fixed=-1)
for (p,q) in [((-aw,-al),(aw,-al)),((aw,-al),(aw,al)),((aw,al),(-aw,al)),((-aw,al),(-aw,-al))]:
    n=int(math.dist(p,q)/0.6)
    for k in range(0,n,2):
        a=(p[0]+(q[0]-p[0])*k/n,p[1]+(q[1]-p[1])*k/n,0); b=(p[0]+(q[0]-p[0])*(k+1)/n,p[1]+(q[1]-p[1])*(k+1)/n,0)
        items.append(('line',(a,b),((60,110,80,255),3),'clear',-0.5))
# tallest steel member: back corner posts to 4 m (13'1")
for sx in (-1,1):
    for sy in (-1,1): seg((5*sx,10*sy,0),(5*sx,10*sy,4.0),C3.STEEL+(255,),6,'tall')
def dim3d(img,Cm,p,q,label,al,off=(0,0),size=46):
    if al<=0: return
    d=ImageDraw.Draw(img,'RGBA'); P=proj(p,Cm); Q=proj(q,Cm)
    P=(P[0]/SS,P[1]/SS); Q=(Q[0]/SS,Q[1]/SS); A=int(255*al)
    d.line([P,Q],fill=INK+(A,),width=4)
    for X in (P,Q): d.ellipse((X[0]-7,X[1]-7,X[0]+7,X[1]+7),fill=INK+(A,))
    m=((P[0]+Q[0])/2+off[0],(P[1]+Q[1])/2+off[1]); f=F(size,800); tw=f.getbbox(label)[2]
    d.rounded_rectangle((m[0]-tw/2-18,m[1]-34,m[0]+tw/2+18,m[1]+34),radius=34,fill=(255,255,255,int(235*al)))
    d.text(m,label,font=f,fill=INK+(A,),anchor='mm')
def title(img,lines,al=1,y=150,size=70):
    d=ImageDraw.Draw(img,'RGBA')
    for k,s in enumerate(lines): d.text((W//2,y+k*(size+14)),s,font=F(size,800),fill=INK+(int(255*al),),anchor='mm')
def caption(img,big,small,al=1,y=1640):
    d=ImageDraw.Draw(img,'RGBA')
    f=F(60,800)
    while f.getbbox(big)[2]>980: f=F(f.size-2,800)
    d.text((W//2,y),big,font=f,fill=INK+(int(255*al),),anchor='mm')
    if small: d.text((W//2,y+70),small,font=F(36,500),fill=GREY+(int(255*al),),anchor='mm')
def base(Cm,show):
    img=Image.fromarray(BGI).convert('RGBA'); img.alpha_composite(render3d(Cm,show)); return img
HIDE={'clear':0,'tall':0}
def kf_hook():
    Cm=cam(math.radians(-110),math.radians(24),D=40); img=base(Cm,dict(HIDE))
    title(img,["How much space does an","outdoor padel court need?"],size=62)
    caption(img,"Padel court dimensions, explained",None,y=1700); return img
def kf_space():
    Cm=cam(math.radians(-90),math.radians(62),D=56,target=(0,1.5,0)); img=base(Cm,{'clear':1,'tall':0,'glass':0.15,'mesh':0.15,'lights':0,'steel':0.3,'net':0.5})
    title(img,["The space you need"])
    dim3d(img,Cm,(-5,-10.9,0.05),(5,-10.9,0.05),"32'10\"",1,(0,50))
    dim3d(img,Cm,(-aw-0.3,-al,0),(-aw-0.3,al,0),"81'",1,(-50,0))
    dim3d(img,Cm,(-aw,al+0.6,0),(aw,al+0.6,0),"48'",1,(0,-50))
    caption(img,"48' x 81' in total","Court 32'10\" x 65'7\", pad 36' x 69', 6' clear all around"); return img
def kf_steel():
    Cm=cam(math.radians(-135),math.radians(16),D=38,target=(0,0,2.0)); img=base(Cm,{'clear':0,'tall':1,'lights':0})
    title(img,["The steel structure"])
    dim3d(img,Cm,(5.8,10,0),(5.8,10,4.0),"13'1\"",1,(80,0))
    caption(img,"Tallest steel member: 13'1\"","Glass and mesh walls on a steel frame"); return img
def kf_cta():
    Cm=cam(math.radians(-60),math.radians(28),D=50,target=(0,0,-1.5)); img=base(Cm,dict(HIDE))
    title(img,["Will a court fit","your property?"])
    d=ImageDraw.Draw(img,'RGBA')
    for k,(s,f,c) in enumerate([("Permit rules vary by county and city",F(40,700),INK),("Plan early to avoid costly redesigns",F(40,700),INK),("Free court-fit assessment",F(40,500),GREY),("AMERICANPADELLABS.COM",F(56,800),INK)]):
        d.text((W//2,1560+k*80),s,font=f,fill=c+(255,),anchor='mm')
    return img
if __name__=='__main__':
    for n,fn in [('hook',kf_hook),('space',kf_space),('steel',kf_steel),('cta',kf_cta)]:
        fn().convert('RGB').save(f'/home/claude/video/d3_{n}.jpg',quality=90)
