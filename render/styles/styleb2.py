import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
import numpy as np, apl
from PIL import Image, ImageDraw, ImageFilter
W,H=1080,1920
rot=Image.open(apl.B('photos','overhead-court-vertical.jpg')); OY=(rot.height-H)//2
bg=rot.crop((0,OY,W,OY+H)).filter(ImageFilter.GaussianBlur(28))
a=(np.array(bg).astype(np.float32)*0.38).astype(np.uint8)
CX,CY,PX=apl.CX,apl.CY-40,apl.PX
cl,cr,ct,cb=CX-5*PX,CX+5*PX,CY-10*PX,CY+10*PX; SV=apl.SV
fl,fr,ft,fb=CX-10.97/2*PX,CX+10.97/2*PX,CY-21.03/2*PX,CY+21.03/2*PX
apl.rectfill(a,cl,ct,cr,cb,(46,92,58),0.85)
apl.poly(a,[(cl,ct),(cr,ct),(cr,cb),(cl,cb)],(255,255,255),5)
apl.line(a,(cl-12,CY),(cr+12,CY),(255,255,255),4)
for y in (CY-SV,CY+SV): apl.line(a,(cl,y),(cr,y),(255,255,255),3)
apl.line(a,(CX,CY-SV),(CX,CY+SV),(255,255,255),3)
apl.rectfill(a,fl,ft,fr,fb,(255,255,255),0.06)
apl.dashed_rect(a,fl,ft,fr,fb,(255,255,255),4)
img=Image.fromarray(a).convert('RGBA')
lg=apl.LOGO.resize((int(apl.LOGO.width*110/apl.LOGO.height),110)); img.alpha_composite(lg,(56,56))
d=ImageDraw.Draw(img,'RGBA')
def pill(cx,cy,s):
    f=apl.F('i',40,700); tw=f.getbbox(s)[2]
    d.rounded_rectangle((cx-tw/2-24,cy-34,cx+tw/2+24,cy+34),radius=34,fill=(255,255,255,240))
    d.text((cx,cy+1),s,font=f,fill=(20,20,20,255),anchor='mm')
pill(W//2,ft-50,"36 ft (11 m)")
pill(fr+0,CY,"69 ft (21 m)")
d.text((W//2,1700),"Plan for 36' x 69'",font=apl.F('i',68,700),fill=(255,255,255,255),anchor='mm')
d.text((W//2,1770),"Room for the ring beam, access, and machinery",font=apl.F('i',38,500),fill=(230,230,230,255),anchor='mm')
img.convert('RGB').save('styleB_footprint.jpg',quality=90)
ims=[Image.open(f).resize((360,640)) for f in ['styleA_hook.jpg','styleA_footprint.jpg','styleB_hook.jpg','styleB_footprint.jpg']]
s=Image.new('RGB',(360*4+60,690),'white'); dd=ImageDraw.Draw(s)
for i,im in enumerate(ims): s.paste(im,(i*360+(60 if i>1 else 0),50))
dd.text((360,25),"A: Website (v1) - navy, Bebas caps, line diagrams",font=apl.F('i',22,700),fill=(0,0,0),anchor='mm')
dd.text((1140,25),"B: Instagram - real footage, sentence case, logo mark",font=apl.F('i',22,700),fill=(0,0,0),anchor='mm')
s.save('style_compare.jpg',quality=88)
