# Padel court dimensions video, illustrated style, terracotta turf. Key frames for approval.
from common import *
import illustrated as IL
F=IL.F
def shadow_txt(d,s,xy,f,anchor='mm',col=(255,255,255),al=1.0):
    x,y=xy; d.text((x+3,y+4),s,font=f,fill=(90,50,40,int(110*al)),anchor=anchor); d.text(xy,s,font=f,fill=col+(int(255*al),),anchor=anchor)
def finish(a):
    a=a*(1+0.045*IL.STREAK[...,None]); sp=(IL.STIP<0.035)[...,None]; a=np.where(sp,a*0.86+255*0.14,a)
    return np.clip(cv2.GaussianBlur(a,(0,0),0.7)+IL.GRAIN[...,None]*8,0,255).astype(np.uint8)
def court_persp(a,col=IL.COURT_COL,pad=True,clear=False):
    if clear:
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(IL.R(*ACC))],255,cv2.LINE_AA); mm=(m/255.0*0.35)[...,None]; a=a*(1-mm)+np.array((236,226,170))*mm
    if pad:
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(IL.R(*PAD))],255,cv2.LINE_AA); mm=(m/255.0)[...,None]; a=a*(1-mm)+np.array((214,204,188))*mm
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(IL.R(*COURT))],255,cv2.LINE_AA); mm=(m/255.0)[...,None]
    a=a*(1-mm)+np.array(col)*(1+0.07*IL.TONE[...,None])*mm
    w,l=COURT; L=(250,244,232)
    for k,ln in enumerate([IL.R(w,l)]+[IL.P([(-w/2,y),(w/2,y)]) for y in (-SV,0,SV)]+[IL.P([(0,-SV),(0,SV)])]):
        cv2.polylines(a,[np.int32(ln*4)],k==0,L,4,cv2.LINE_AA,shift=2)
    return a
def px_per_ft(x,y):
    p=IL.P([(x-0.5,y),(x+0.5,y)]); return float(np.linalg.norm(p[1]-p[0]))
def up(x,y,h):
    b=IL.P([(x,y)])[0]; return (b[0],b[1]-h*px_per_ft(x,y))
def walls(a):
    # glass + mesh enclosure in the same perspective; back walls 9'10" (6'7" glass + 3'3" mesh)
    w,l=COURT; hw,hl=w/2,l/2; G=6+7/12; T=9+10/12
    ov=a.copy()
    def quad(p0,p1,h0,h1,col,al):
        pts=np.float32([IL.P([p0])[0],IL.P([p1])[0],up(*p1,h1),up(*p0,h0)])
        o=a.copy(); cv2.fillPoly(o,[np.int32(pts)],col,cv2.LINE_AA); a[:]=a*(1-al)+o*al
        cv2.polylines(a,[np.int32(pts)],True,(235,240,245),2,cv2.LINE_AA)
    for y in (-hl,):   # far back wall first
        quad((-hw,y),(hw,y),G,G,(200,225,240),0.28); quad
    for x in (-hw,hw):
        quad((x,-hl),(x,-hl+6.56),T,T,(200,225,240),0.22); quad((x,-hl+6.56),(x,-hl+13.1),G,G,(200,225,240),0.22)
        quad((x,hl-13.1),(x,hl-6.56),G,G,(200,225,240),0.22); quad((x,hl-6.56),(x,hl),T,T,(200,225,240),0.22)
    quad((-hw,hl),(hw,hl),G,G,(200,225,240),0.22)
    for x,y in [(-hw,-hl),(hw,-hl),(-hw,hl),(hw,hl)]:
        b=IL.P([(x,y)])[0]; t=up(x,y,13+1/12); cv2.line(a,(int(b[0]),int(b[1])),(int(t[0]),int(t[1])),(52,56,64),5,cv2.LINE_AA)
    return a
def frame_hook():
    a=IL.scene(0,0); a=court_persp(a); out=finish(walls(a))
    img=Image.fromarray(out).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    for k,s in enumerate(["How much space does","a padel court need?"]): shadow_txt(d,s,(W//2,180+k*92),F(76))
    shadow_txt(d,"Padel court dimensions, explained",(W//2,1790),F(44,700)); return img
def frame_steel():
    a=IL.scene(0,0); a=court_persp(a); a=walls(a); out=finish(a)
    img=Image.fromarray(out).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    w,l=COURT; x,y=w/2,l/2; b=IL.P([(x,y)])[0]; t=up(x,y,13+1/12)
    dx=50; d.line((b[0]+dx,b[1],t[0]+dx,t[1]),fill=(255,255,255,255),width=5)
    for p in (b,t): d.line((p[0]+dx-16,p[1],p[0]+dx+16,p[1]),fill=(255,255,255,255),width=5)
    shadow_txt(d,"13'1\"",(t[0]+dx+20,(b[1]+t[1])/2),F(64),anchor='lm')
    shadow_txt(d,"The steel structure",(W//2,180),F(76))
    shadow_txt(d,"Tallest steel member: 13'1\"",(W//2,1760),F(64)); shadow_txt(d,"Glass and mesh walls on a steel frame",(W//2,1840),F(38,600)); return img
def frame_tips():
    base=Image.open('/home/claude/video/ov_plain.jpg').convert('RGBA'); d=ImageDraw.Draw(base,'RGBA')
    # dark band behind the tip list for legibility
    band=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(band).rounded_rectangle((40,1250,1040,1880),radius=40,fill=(30,40,30,150)); base.alpha_composite(band)
    shadow_txt(d,"Tips before you build",(W//2,170),F(76))
    # compass on the lawn
    cx,cy=950,560; d.ellipse((cx-60,cy-60,cx+60,cy+60),fill=(250,244,230,230)); d.polygon([(cx,cy-52),(cx-16,cy),(cx+16,cy)],fill=(184,92,62,255)); d.polygon([(cx,cy+52),(cx-16,cy),(cx+16,cy)],fill=(60,60,60,255)); d.text((cx,cy-80),"N",font=F(36),fill=(255,255,255,255),anchor='mm')
    tips=[("Check setback rules","How far the court must sit from your property lines"),("Run it north-south","Keeps the sun out of players' eyes"),("Slope the slab 0.5-0.7%","From one short end to the other, so water drains"),("Want lights?","Plan access to your utility box")]
    for k,(t1,t2) in enumerate(tips):
        y=1300+k*142; d.ellipse((80,y-6,132,y+46),fill=(184,92,62,255)); d.text((106,y+20),str(k+1),font=F(34),fill=(255,255,255,255),anchor='mm')
        d.text((160,y),t1,font=F(46),fill=(255,255,255,255)); d.text((160,y+58),t2,font=F(30,600),fill=(235,230,215,255))
    return base
def frame_cta():
    a=IL.scene(0,0); a=court_persp(a); out=finish(walls(a))
    img=Image.fromarray(out).convert('RGBA')
    band=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(band).rounded_rectangle((40,1300,1040,1880),radius=40,fill=(30,40,30,150)); img.alpha_composite(band)
    d=ImageDraw.Draw(img,'RGBA')
    for k,s in enumerate(["Will a court fit","your property?"]): shadow_txt(d,s,(W//2,180+k*92),F(76))
    lines=[("Permit rules vary by county and city",F(40,800)),("Plan early to avoid costly redesigns",F(40,800)),("We'll help you navigate and plan your home court",F(32,600)),("Free court-fit assessment",F(40,800)),("americanpadellabs.com",F(56))]
    for k,(s,f) in enumerate(lines): d.text((W//2,1360+k*100),s,font=f,fill=(255,255,255,255),anchor='mm')
    return img
if __name__=='__main__':
    for n,fn in [('hook',frame_hook),('steel',frame_steel),('tips',frame_tips),('cta',frame_cta)]:
        fn().convert('RGB').save(f'/home/claude/video/di_{n}.jpg',quality=90)
