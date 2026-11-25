# Style sample: grainy illustrated landscape (gouache / risograph feel), original artwork.
# Warm sunset sky, layered hills, cypress trees; the court plan sits on a backyard lawn in perspective.
from common import *
N=270
import os
COURT_COL=tuple(int(v) for v in os.environ.get("COURT_COL","62,112,168").split(","))
rng=np.random.default_rng(21)
F=lambda sz,w=800: font(f'figtree-latin-{w}-normal',sz)
_LF={}
def lf(h,w,sig,seed):
    k=(h,w,sig,seed)
    if k in _LF: return _LF[k]
    _LF[k]=_lf(h,w,sig,seed); return _LF[k]
def _lf(h,w,sig,seed):
    r=np.random.default_rng(seed); n=r.normal(0,1,(h//4+1,w//4+1)).astype(np.float32); n=cv2.GaussianBlur(n,(0,0),sig)
    n=(n-n.mean())/(n.std()+1e-6); return cv2.resize(n,(w,h))
GRAIN=rng.normal(0,1,(H,W)).astype(np.float32)
STIP=rng.random((H,W)).astype(np.float32)
STREAK=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),sigmaX=9,sigmaY=1.2); STREAK/=STREAK.std()
TONE=lf(H,W,6,3)
def fillpoly(a,pts,col,tex=0.06,seed=0):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(pts)],255,cv2.LINE_AA); m=m.astype(np.float32)/255
    c=np.array(col,np.float32)*(1+tex*lf(H,W,3,seed)[...,None])
    a[:]=a*(1-m[...,None])+c*m[...,None]
def hill(y0,amp,freq,ph,col,seed,x0=-50,x1=W+50):
    xs=np.linspace(x0,x1,120); ys=y0-amp*(0.6*np.sin(xs*freq+ph)+0.4*np.sin(xs*freq*2.3+ph*1.7))
    pts=list(zip(xs,ys))+[(x1,H),(x0,H)]; return pts
def cypress(a,x,yb,h,w,col,seed=50,sway=0.0):
    pts=[(x+sway,yb-h)]+[(x+sway*(1-t/math.pi)+w*math.sin(t)*(0.55+0.45*t/math.pi),yb-h+h*t/math.pi) for t in np.linspace(0.15,math.pi,30)]
    pts+= [(x+sway*(1-t/math.pi)-w*math.sin(t)*(0.55+0.45*t/math.pi),yb-h+h*t/math.pi) for t in np.linspace(math.pi,0.15,30)]
    fillpoly(a,pts,col,0.08,seed)
def scene(dx,t=0):
    a=np.zeros((H,W,3),np.float32)
    y=np.linspace(0,1,H)[:,None,None]
    sky=np.array((226,98,118),np.float32)*(1-y*1.7).clip(0,1)+np.array((255,192,112),np.float32)*(y*1.7).clip(0,1)
    a[:]=sky
    # sun glow
    yy,xx=np.mgrid[0:H,0:W]; d=np.hypot(xx-540,yy-720)
    a+= (np.exp(-(d/260)**2)*(55+10*math.sin(t/30*2)))[...,None]*np.array([1,0.85,0.5])
    sun=(d<78).astype(np.float32); a=a*(1-sun[...,None])+np.array((255,236,190))*sun[...,None]
    # clouds: soft stippled blobs drifting
    for k,(cx,cy,sx,sy) in enumerate([(220,330,260,70),(860,240,230,60),(640,470,300,55)]):
        cxk=cx+dx*(0.6+0.2*k)
        g=np.exp(-(((xx-cxk)/sx)**2+((yy-cy)/sy)**2))+0.35*lf(H,W,4,40+k)*np.exp(-(((xx-cxk)/(sx*1.3))**2+((yy-cy)/(sy*1.6))**2))
        al=np.clip((g-0.35)*3,0,1); al=np.where(STIP<al*1.15,1.0,al*0.5)*(g>0.15)
        a=a*(1-al[...,None]*0.85)+np.array((255,240,228))*al[...,None]*0.85
    fillpoly(a,hill(760,70,0.006,1.0+dx*0.0004,(0,0,0),1),(222,112,128),0.06,11)     # far mauve ridge
    fillpoly(a,hill(820,45,0.009,2.2+dx*0.0008,(0,0,0),2),(120,152,124),0.07,12)     # sage hills
    # little house on the left hill (original drawing)
    hx=150+dx*0.9; fillpoly(a,[(hx,790),(hx+120,790),(hx+120,860),(hx,860)],(246,226,200),0.04,13)
    fillpoly(a,[(hx-12,792),(hx+60,745),(hx+132,792)],(204,108,84),0.06,14)
    fillpoly(a,[(hx+50,820),(hx+72,820),(hx+72,860),(hx+50,860)],(120,80,70),0.0,15)
    fillpoly(a,hill(880,20,0.012,0.4,(0,0,0),3),(98,142,94),0.03,16)                  # lawn
    # mowing stripes in perspective
    for k in range(-8,9):
        x_far=540+k*70; x_near=540+k*260
        fillpoly(a,[(x_far,880),(x_far+35,880),(x_near+130,H),(x_near,H)],(106,150,98),0.02,30+k)
    for k,(x,h) in enumerate(((60,300),(990,340),(1050,260),(30,220))): cypress(a,x+dx*1.1,900,h,34,(46,88,70),50+k,6*math.sin(t/30*1.6+k))
    for k,x in enumerate((240,420,640,860)):
        yy0=872; fillpoly(a,[(x+dx+30*math.cos(u),yy0-18*abs(math.sin(u))) for u in np.linspace(0,math.pi,20)]+[(x+dx-30,yy0)],(76,118,80),0.05,70+k)
    # birds crossing the sky, flapping
    for k in range(5):
        bx=(-80+(t*2.2+k*57)%1300); by=380+k*22+8*math.sin(t/9+k); f=1 if (t//4+k)%2 else 0
        span=14; dy=-8 if f else 4
        cv2.polylines(a,[np.int32([(bx-span,by+dy),(bx,by),(bx+span,by+dy)])],False,(110,60,70),3,cv2.LINE_AA)
    return a
# ground homography: plan feet (x across, y along; access zone 48 x 81) -> screen trapezoid
SRC=np.float32([[-24,-40.5],[24,-40.5],[24,40.5],[-24,40.5]])
DST=np.float32([[330,960],[750,960],[1010,1640],[70,1640]])
Hm=cv2.getPerspectiveTransform(SRC,DST)
def P(pts): return cv2.perspectiveTransform(np.float32(pts)[None],Hm)[0]
def R(w,l): return P([(-w/2,-l/2),(w/2,-l/2),(w/2,l/2),(-w/2,l/2)])
def frame(i):
    t=i; dx=-30+60*(t/N)
    a=scene(dx,t)
    ca=ss(prog(t,20,50)); pa=ss(prog(t,70,100)); aa=ss(prog(t,120,150))
    if aa>0:
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(R(*ACC))],255,cv2.LINE_AA)
        mm=(m/255.0*aa*0.35)[...,None]; a=a*(1-mm)+np.array((236,226,170))*mm
    if pa>0:
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(R(*PAD))],255,cv2.LINE_AA)
        mm=(m/255.0*pa)[...,None]; a=a*(1-mm)+np.array((214,204,188))*(1+0.05*TONE[...,None])*mm
    if ca>0:
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(R(*COURT))],255,cv2.LINE_AA)
        mm=(m/255.0*ca)[...,None]; a=a*(1-mm)+np.array(COURT_COL)*(1+0.07*TONE[...,None])*mm
        L=(250,244,232); w,l=COURT
        lines=[R(w,l)]+[P([(-w/2,y),(w/2,y)]) for y in (-SV,0,SV)]+[P([(0,-SV),(0,SV)])]
        ov=a.copy()
        for k,ln in enumerate(lines): cv2.polylines(ov,[np.int32(ln*4)],k==0,L,4,cv2.LINE_AA,shift=2)
        a=a*(1-ca)+ov*ca
    # grain + slight softness: gouache / risograph feel
    a=a*(1+0.045*STREAK[...,None])
    sp=(STIP<0.035)[...,None]; a=np.where(sp,a*0.86+255*0.14,a)
    a=cv2.GaussianBlur(a,(0,0),0.7)+GRAIN[...,None]*8
    out=np.clip(a,0,255).astype(np.uint8)
    if aa>0:   # dashed clearance line
        q=R(*ACC); q=np.vstack([q,q[:1]])
        for k in range(4):
            p0,p1=q[k],q[k+1]; L_=np.linalg.norm(p1-p0); n=int(L_/26)
            for j in range(0,n,2):
                if j/n>aa: break
                s0=p0+(p1-p0)*j/n; s1=p0+(p1-p0)*(j+1)/n
                cv2.line(out,(int(s0[0]),int(s0[1])),(int(s1[0]),int(s1[1])),(255,248,230),4,cv2.LINE_AA)
    img=Image.fromarray(out).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    def txt(s,xy,f,al,anchor='mm',col=(255,255,255)):
        if al<=0: return
        x,y=xy; d.text((x+3,y+4),s,font=f,fill=(90,50,40,int(110*al)),anchor=anchor); d.text(xy,s,font=f,fill=col+(int(255*al),),anchor=anchor)
    txt("The space you need",(W//2,170),F(76),ss(prog(t,0,20)))
    txt("court  32'10\" x 65'7\"",(W//2,1290),F(40,800),ss(prog(t,45,60)))
    txt("concrete pad  36' x 69'",(W//2,1595),F(36,800),ss(prog(t,95,110)))
    txt("+ 6' clear all around",(W//2,918),F(36,800),ss(prog(t,145,160)))
    al=ss(prog(t,175,200))
    txt("48' x 81' total",(W//2,1755),F(84),al)
    txt("Room for machinery and getting in and out",(W//2,1835),F(34,600),al)
    return zoom(np.array(img.convert('RGB')),1.0+0.04*ss(t/N),0.5,0.55)
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/il_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_illustrated.mp4')
