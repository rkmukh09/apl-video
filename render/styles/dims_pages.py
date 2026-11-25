# Dimensions video, illustrated style: one still per key takeaway (Raj, Nov 24).
# Perspective view only, glass walls in every scene, white text on the scene, no panels.
from common import *
import os
import illustrated as IL
from dims_illustrated import finish, court_persp, walls, up, shadow_txt
F=IL.F; WHITE=(255,255,255)
LOGO=Image.open(os.path.join(ROOT,'brand','logo.png')).convert('RGBA')
def base(pad=True,clear=False,court_col=None):
    a=IL.scene(0,0); a=court_persp(a,pad=pad,clear=clear) if court_col is None else court_persp(a,court_col,pad,clear)
    return a
def dashed(a,pts,closed=True,col=(255,248,230),seg=26,th=4):
    q=list(pts)+([pts[0]] if closed else [])
    for k in range(len(q)-1):
        p0=np.array(q[k],np.float32); p1=np.array(q[k+1],np.float32); n=max(2,int(np.linalg.norm(p1-p0)/seg))
        for j in range(0,n,2):
            s0=p0+(p1-p0)*j/n; s1=p0+(p1-p0)*(j+1)/n; cv2.line(a,(int(s0[0]),int(s0[1])),(int(s1[0]),int(s1[1])),col,th,cv2.LINE_AA)
def page(a,title,big,small=None,big_y=1735,extra=None):
    img=Image.fromarray(finish(a)).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    for k,s in enumerate(title if isinstance(title,list) else [title]): shadow_txt(d,s,(W//2,175+k*90),F(74))
    if big:
        f=F(64)
        while f.getbbox(big)[2]>1000: f=F(f.size-2)
        shadow_txt(d,big,(W//2,big_y),f)
    if small:
        for k,s in enumerate(small if isinstance(small,list) else [small]):
            f=F(36,700)
            while f.getbbox(s)[2]>1000: f=F(f.size-2,700)
            shadow_txt(d,s,(W//2,big_y+78+k*54),f)
    if extra: extra(img,d)
    return img
def lbl(d,s,xy,size=40): shadow_txt(d,s,xy,F(size))
w,l=COURT
PAGES={}
PAGES['01_hook']=lambda: page(walls(base(pad=False)),["How much space does","a padel court need?"],None,"Padel court dimensions, explained",big_y=1700)
def space1():
    a=walls(base(pad=False))
    def ex(img,d):
        p=IL.P([(-w/2,l/2+2.5),(w/2,l/2+2.5)]); lbl(d,"32'10\"",tuple(p.mean(0)+[0,26]))
        q=IL.P([(w/2+3,-l/2),(w/2+3,l/2)]); lbl(d,"65'7\"",tuple(q.mean(0)+[60,0]))
    return page(a,"The space you need","Regulation court: 65'7\" x 32'10\"","Playing area, 2,153 sq ft",extra=ex)
PAGES['02_space_court']=space1
def space2():
    a=walls(base(pad=True))
    def ex(img,d):
        p=IL.P([(-PAD[0]/2,PAD[1]/2+2.5),(PAD[0]/2,PAD[1]/2+2.5)]); lbl(d,"36'",tuple(p.mean(0)+[0,30]))
        q=IL.P([(PAD[0]/2+3,-PAD[1]/2),(PAD[0]/2+3,PAD[1]/2)]); lbl(d,"69'",tuple(q.mean(0)+[56,0]))
    return page(a,"The space you need","Recommended concrete pad: 36' x 69'","Includes the perimeter concrete ring beam that anchors the court",extra=ex)
PAGES['03_space_pad']=space2
def space3():
    a=walls(base(pad=True,clear=True)); dashed(a,IL.R(*ACC))
    def ex(img,d):
        for p in [((ACC[0]/2+PAD[0]/2)/2,0),(-(ACC[0]/2+PAD[0]/2)/2,0),(0,-(ACC[1]/2+PAD[1]/2)/2),(0,(ACC[1]/2+PAD[1]/2)/2)]:
            lbl(d,"6'",tuple(IL.P([p])[0]),36)
    return page(a,"The space you need","48' x 81' total","Plus 6' clear around the pad, for install machinery and easy access in and out",extra=ex)
PAGES['04_space_total']=space3
def steel():
    a=walls(base(pad=True))
    def ex(img,d):
        x,y=w/2,l/2; b=IL.P([(x,y)])[0]; t=up(x,y,13+1/12); dx=50
        d.line((b[0]+dx,b[1],t[0]+dx,t[1]),fill=(255,255,255,255),width=5)
        for p in (b,t): d.line((p[0]+dx-16,p[1],p[0]+dx+16,p[1]),fill=(255,255,255,255),width=5)
        shadow_txt(d,"13'1\"",(t[0]+dx+20,(b[1]+t[1])/2),F(60),anchor='lm')
    return page(a,"The steel structure","Tallest steel member: 13'1\"","Glass and mesh walls on a steel frame",extra=ex)
PAGES['05_steel']=steel
def tip1():
    a=walls(base(pad=True,clear=True)); dashed(a,IL.R(*ACC))
    xl=ACC[0]/2+9; dashed(a,IL.P([(xl,-ACC[1]/2-6),(xl,ACC[1]/2+4)]),closed=False,col=(255,236,150),seg=18,th=5)
    def ex(img,d):
        p0=IL.P([(ACC[0]/2,8)])[0]; p1=IL.P([(xl,8)])[0]
        d.line((p0[0],p0[1],p1[0],p1[1]),fill=(255,255,255,255),width=4)
        lbl(d,"property line",tuple(IL.P([(xl,-ACC[1]/2-4)])[0]+[-10,-34]),30)
    return page(a,["Tips before you build"],"1. Check setback rules","How far the court must sit from your property lines",extra=ex)
PAGES['06_tip_setback']=tip1
def tip2():
    a=walls(base(pad=True))
    def ex(img,d):
        cx,cy=150,1480; r=70
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,255),width=4)
        d.polygon([(cx,cy-r+8),(cx-18,cy),(cx+18,cy)],fill=(184,92,62,255)); d.polygon([(cx,cy+r-8),(cx-18,cy),(cx+18,cy)],fill=(255,255,255,255))
        shadow_txt(d,"N",(cx,cy-r-30),F(40)); shadow_txt(d,"S",(cx,cy+r+30),F(40))
        p=IL.P([(0,-l/2-4),(0,l/2+3)])
        d.line((p[1][0],p[1][1],p[0][0],p[0][1]),fill=(255,255,255,200),width=4)
    return page(a,["Tips before you build"],"2. Run it north-south","Keeps the sun out of players' eyes",extra=ex)
PAGES['07_tip_orientation']=tip2
def tip3():
    a=walls(base(pad=True))
    def ex(img,d):
        p=IL.P([(-w/2-2.5,-l/2),(-w/2-2.5,l/2)])
        d.line((p[0][0],p[0][1],p[1][0],p[1][1]),fill=(255,255,255,255),width=6)
        ang=math.atan2(p[1][1]-p[0][1],p[1][0]-p[0][0])
        for s in (-0.45,0.45): d.line((p[1][0],p[1][1],p[1][0]-30*math.cos(ang+s),p[1][1]-30*math.sin(ang+s)),fill=(255,255,255,255),width=6)
        lbl(d,"water drains",tuple(p.mean(0)+[-120,0]),32)
    return page(a,["Tips before you build"],"3. Slope the slab 0.5-0.7%","From one short end to the other, so water drains",extra=ex)
PAGES['08_tip_slope']=tip3
def tip4():
    a=walls(base(pad=True))
    poles=[(-PAD[0]/2-3,-l/2+4),(PAD[0]/2+3,-l/2+4),(-PAD[0]/2-3,l/2-4),(PAD[0]/2+3,l/2-4)]
    for x,y in poles:
        b=IL.P([(x,y)])[0]; t=up(x,y,20); cv2.line(a,(int(b[0]),int(b[1])),(int(t[0]),int(t[1])),(52,56,64),5,cv2.LINE_AA)
        g=np.zeros((H,W),np.float32); cv2.circle(g,(int(t[0]),int(t[1])),40,1,-1); g=cv2.GaussianBlur(g,(0,0),18)[...,None]
        a[:]=a*(1-g*0.7)+np.array((255,245,210))*g*0.7
    ub=IL.P([(PAD[0]/2+14,l/2-2)])[0]; cv2.rectangle(a,(int(ub[0])-30,int(ub[1])-50),(int(ub[0])+30,int(ub[1])),(170,170,165),-1)
    cv2.rectangle(a,(int(ub[0])-30,int(ub[1])-50),(int(ub[0])+30,int(ub[1])),(90,90,90),3)
    pl=IL.P([poles[3]])[0]; dashed(a,[(ub[0]-30,ub[1]-10),(pl[0],pl[1])],closed=False,col=(255,236,150),seg=14,th=4)
    def ex(img,d): lbl(d,"utility box",(ub[0]-20,ub[1]+34),30)
    return page(a,["Tips before you build"],"4. Want lights?","Plan access to your utility box",extra=ex)
PAGES['09_tip_lights']=tip4
def cta_logo(img):
    lg=LOGO.resize((int(LOGO.width*260/LOGO.height),260),Image.LANCZOS); img.alpha_composite(lg,(W//2-lg.width//2,300))
def cta1():
    return page(walls(base(pad=True)),["Will a court fit","your property?"],"Permit rules vary by county and city","Plan early to avoid costly redesigns")
PAGES['10_cta_permits']=cta1
def cta2():
    def ex(img,d): cta_logo(img)
    return page(walls(base(pad=True)),[],"We'll help you navigate and plan your home court",["Free court-fit assessment","Planning a club or indoor facility? We can help with that too.","americanpadellabs.com"],big_y=1640,extra=ex)
PAGES['11_cta_help']=cta2
if __name__=='__main__':
    import sys
    os.makedirs('/home/claude/video/pages',exist_ok=True)
    for k,fn in PAGES.items():
        if len(sys.argv)>1 and k not in sys.argv[1:]: continue
        fn().convert('RGB').save(f'/home/claude/video/pages/{k}.jpg',quality=90)
