import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import numpy as np, cv2, apl
from PIL import Image, ImageDraw, ImageFilter
W,H=1080,1920
rot=Image.open(apl.B('photos','overhead-court-vertical.jpg')); OY=(rot.height-H)//2
K=0.74
bgimg=rot.crop((0,OY,W,OY+H)).filter(ImageFilter.GaussianBlur(40))
small=rot.resize((int(W*K),int(rot.height*K)))
SX=(W-small.width)//2; SY=880-int(978*K)
bgimg.paste(small,(SX,SY))
base=np.array(bgimg).astype(np.float32)
PX=79.6*K; CX=SX+534*K; CY=SY+978*K
def dark(k):
    y=np.linspace(-1,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
    v=1-0.35*(x**2+y**2)
    return np.clip(base*k*v[...,None],0,255).astype(np.uint8)
def wm(img):
    lg=apl.LOGO.resize((int(apl.LOGO.width*110/apl.LOGO.height),110))
    img.alpha_composite(lg,(56,56))
def cap(img,h,sub,y=1660):
    d=ImageDraw.Draw(img,'RGBA')
    for dx,dy in [(0,3)]:
        d.text((W//2+dx,y+dy),h,font=apl.F('i',68,700),fill=(0,0,0,110),anchor='mm')
    d.text((W//2,y),h,font=apl.F('i',68,700),fill=(255,255,255,255),anchor='mm')
    if sub: d.text((W//2,y+70),sub,font=apl.F('i',40,500),fill=(235,235,235,255),anchor='mm')
# frame B1: hook
a=dark(0.55); img=Image.fromarray(a).convert('RGBA'); wm(img)
d=ImageDraw.Draw(img,'RGBA')
for i,s in enumerate(["How much space does a","padel court actually need?"]):
    d.text((W//2,880+i*88),s,font=apl.F('i',72,700),fill=(255,255,255,255),anchor='mm')
d.text((W//2,1080),"More than the court itself.",font=apl.F('i',44,500),fill=(230,230,230,255),anchor='mm')
img.convert('RGB').save('styleB_hook.jpg',quality=90)
# frame B2: footprint on photo
a=dark(0.45)
fl,fr,ft,fb=CX-10.97/2*PX,CX+10.97/2*PX,CY-21.03/2*PX,CY+21.03/2*PX
cl,cr,ct,cb=CX-5*PX,CX+5*PX,CY-10*PX,CY+10*PX
apl.poly(a,[(cl,ct),(cr,ct),(cr,cb),(cl,cb)],(255,255,255),5)
apl.dashed_rect(a,fl,ft,fr,fb,(255,255,255),4)
apl.rectfill(a,fl,ft,fr,fb,(255,255,255),0.08)
img=Image.fromarray(a).convert('RGBA'); wm(img)
d=ImageDraw.Draw(img,'RGBA')
def pill(cx,cy,s):
    f=apl.F('i',40,700); tw=f.getbbox(s)[2]
    d.rounded_rectangle((cx-tw/2-24,cy-34,cx+tw/2+24,cy+34),radius=34,fill=(255,255,255,235))
    d.text((cx,cy+1),s,font=f,fill=(20,20,20,255),anchor='mm')
pill(W//2,ft-48,"36 ft (11 m)")
pill(W//2-0, CY, "69 ft (21 m)")
cap(img,"Plan for 36' x 69'","Room for the ring beam, access, and machinery",y=1700)
img.convert('RGB').save('styleB_footprint.jpg',quality=90)
# v1 equivalents
Image.fromarray(apl.frame(2.5)).save('styleA_hook.jpg',quality=90)
Image.fromarray(apl.frame(33.2)).save('styleA_footprint.jpg',quality=90)
ims=[Image.open(f).resize((360,640)) for f in ['styleA_hook.jpg','styleA_footprint.jpg','styleB_hook.jpg','styleB_footprint.jpg']]
s=Image.new('RGB',(360*4+60,640),'white')
for i,im in enumerate(ims): s.paste(im,(i*360+(60 if i>1 else 0),0))
s.save('style_compare.jpg',quality=88)
