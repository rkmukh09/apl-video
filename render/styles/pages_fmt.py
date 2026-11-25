# Dimensions video stills, illustrated style, one still per key takeaway, in every channel format.
# Usage: FMT=reel|feed|square|wide python3 pages_fmt.py [page ...]
# Text stays inside each format's safe zone (Reels: Meta margins top 270, bottom 672, sides 65, right rail 120).
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FMTS={
 # safe = (x0,y0,x1,y1) where text may go; text: where the caption block sits
 'reel':  dict(W=1080,H=1920,safe=(65,270,960,1248),hz=800, ct=870, cb=1650,cx=512, fw=215,nw=480,text='top'),
 'feed':  dict(W=1080,H=1350,safe=(60,60,1020,1290),hz=370, ct=400, cb=880, cx=540, fw=170,nw=400,text='bottom'),
 'square':dict(W=1080,H=1080,safe=(60,60,1020,1020),hz=270, ct=345, cb=690, cx=540, fw=130,nw=300,text='bottom'),
 'wide':  dict(W=1920,H=1080,safe=(96,60,1824,1020),hz=420, ct=455, cb=1000,cx=1340,fw=200,nw=470,text='left'),
}
FMT=os.environ.get('FMT','reel'); C=FMTS[FMT]; W,H=C['W'],C['H']
FT=dict(COURT=(32+10/12,65+7/12),PAD=(36.0,69.0),ACC=(48.0,81.0)); SV=22+10/12
COURT,PAD,ACC=FT['COURT'],FT['PAD'],FT['ACC']
TERRA=(184,92,62)
LOGO=Image.open(os.path.join(ROOT,'brand','logo.png')).convert('RGBA')
rng=np.random.default_rng(21)
_f={}
def F(sz,w=800):
    k=(sz,w)
    if k not in _f: _f[k]=ImageFont.truetype(os.path.join(ROOT,'brand','fonts',f'figtree-latin-{w}-normal.woff'),sz)
    return _f[k]
_LF={}
def lf(sig,seed):
    k=(sig,seed)
    if k not in _LF:
        r=np.random.default_rng(seed); n=r.normal(0,1,(H//4+1,W//4+1)).astype(np.float32); n=cv2.GaussianBlur(n,(0,0),sig)
        _LF[k]=cv2.resize((n-n.mean())/(n.std()+1e-6),(W,H))
    return _LF[k]
GRAIN=rng.normal(0,1,(H,W)).astype(np.float32); STIP=rng.random((H,W)).astype(np.float32)
STREAK=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),sigmaX=9,sigmaY=1.2); STREAK/=STREAK.std()
TONE=lf(6,3)
def fillpoly(a,pts,col,tex=0.06,seed=0):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(pts)],255,cv2.LINE_AA); m=m.astype(np.float32)/255
    c=np.array(col,np.float32)*(1+tex*lf(3,seed)[...,None]); a[:]=a*(1-m[...,None])+c*m[...,None]
def hill(y0,amp,freq,ph):
    xs=np.linspace(-50,W+50,160); ys=y0-amp*(0.6*np.sin(xs*freq+ph)+0.4*np.sin(xs*freq*2.3+ph*1.7))
    return list(zip(xs,ys))+[(W+50,H),(-50,H)]
def cypress(a,x,yb,h,w,col,seed):
    pts=[(x,yb-h)]+[(x+w*math.sin(t)*(0.55+0.45*t/math.pi),yb-h+h*t/math.pi) for t in np.linspace(0.15,math.pi,30)]
    pts+=[(x-w*math.sin(t)*(0.55+0.45*t/math.pi),yb-h+h*t/math.pi) for t in np.linspace(math.pi,0.15,30)]
    fillpoly(a,pts,col,0.08,seed)
def scene():
    hz=C['hz']; a=np.zeros((H,W,3),np.float32)
    y=(np.arange(H,dtype=np.float32)/hz)[:,None,None]
    a[:]=np.array((226,98,118),np.float32)*(1-y*0.95).clip(0,1)+np.array((255,192,112),np.float32)*(y*0.95).clip(0,1)
    yy,xx=np.mgrid[0:H,0:W]; sx=C['cx']; d=np.hypot(xx-sx,yy-(hz-40))
    a+=(np.exp(-(d/(0.34*hz))**2)*60)[...,None]*np.array([1,0.85,0.5]); sun=(d<0.1*hz).astype(np.float32)
    a=a*(1-sun[...,None])+np.array((255,236,190))*sun[...,None]
    for k,(fx,fy,sxr,syr) in enumerate([(0.2,0.43,0.24,0.09),(0.8,0.31,0.21,0.08),(0.6,0.62,0.28,0.07)]):
        cx_,cy_=fx*W,fy*hz; sx_,sy_=sxr*max(W,1080),syr*hz
        g=np.exp(-(((xx-cx_)/sx_)**2+((yy-cy_)/sy_)**2))+0.35*lf(4,40+k)*np.exp(-(((xx-cx_)/(sx_*1.3))**2+((yy-cy_)/(sy_*1.6))**2))
        al=np.clip((g-0.35)*3,0,1); al=np.where(STIP<al*1.15,1.0,al*0.5)*(g>0.15)
        a=a*(1-al[...,None]*0.85)+np.array((255,240,228))*al[...,None]*0.85
    fillpoly(a,hill(hz,0.09*hz,0.006,1.0),(222,112,128),0.06,11)
    fillpoly(a,hill(hz+0.08*hz,0.06*hz,0.009,2.2),(120,152,124),0.07,12)
    hx=(0.14 if FMT!='wide' else 0.52)*W; hy=hz+0.04*hz; s=hz/760
    fillpoly(a,[(hx,hy),(hx+120*s,hy),(hx+120*s,hy+70*s),(hx,hy+70*s)],(246,226,200),0.04,13)
    fillpoly(a,[(hx-12*s,hy+2*s),(hx+60*s,hy-45*s),(hx+132*s,hy+2*s)],(204,108,84),0.06,14)
    fillpoly(a,[(hx+50*s,hy+30*s),(hx+72*s,hy+30*s),(hx+72*s,hy+70*s),(hx+50*s,hy+70*s)],(120,80,70),0.0,15)
    gy=hz+0.16*hz; fillpoly(a,hill(gy,0.025*hz,0.012,0.4),(98,142,94),0.03,16)
    for k in range(-14,15):
        xf=C['cx']+k*70; xn=C['cx']+k*260; fillpoly(a,[(xf,gy),(xf+35,gy),(xn+130,H),(xn,H)],(106,150,98),0.02,30+(k%9))
    for k,(fx,h) in enumerate(((0.055,300),(0.92,340),(0.975,260),(0.03,220))):
        cypress(a,fx*W,gy+20*s,h*s,34*s,(46,88,70),50+k)
    for k in range(4):
        x=W*(0.22+0.19*k); fillpoly(a,[(x+30*s*math.cos(u),gy-8-18*s*abs(math.sin(u))) for u in np.linspace(0,math.pi,20)],(76,118,80),0.05,70+k)
    return a
# True 3D camera (3/4 view so the enclosure reads), fitted into each format's court box.
AZ=math.radians(float(os.environ.get('CAM_AZ','0'))); EL=math.radians(float(os.environ.get('CAM_EL','30'))); DIST=170.0
_cp=np.array([DIST*math.cos(EL)*math.sin(AZ),DIST*math.cos(EL)*math.cos(AZ),DIST*math.sin(EL)])
_cf=-_cp/np.linalg.norm(_cp); _r=np.cross(_cf,[0,0,1.0]); _r/=np.linalg.norm(_r); _u=np.cross(_r,_cf)
def _raw(p):
    v=np.array(p,float)-_cp; z=v@_cf; return np.array([(v@_r)/z,-(v@_u)/z])
_fitpts=[(x,y,0) for x in (-24,24) for y in (-40.5,40.5)]+[(x,y,13+1/12) for x in (-COURT[0]/2,COURT[0]/2) for y in (-COURT[1]/2,COURT[1]/2)]
_rp=np.array([_raw(p) for p in _fitpts]); _mn=_rp.min(0); _mx=_rp.max(0)
_bx0,_bx1=C['cx']-C['nw'],C['cx']+C['nw']; _by0,_by1=C['ct']-0.05*H,C['cb']
_sc=min((_bx1-_bx0)/(_mx[0]-_mn[0]),(_by1-_by0)/(_mx[1]-_mn[1]))
_off=np.array([(_bx0+_bx1)/2,(_by0+_by1)/2])-_sc*(_mn+_mx)/2
def proj(x,y,z=0.0): return _off+_sc*_raw((x,y,z))
def P(pts): return np.float32([proj(p[0],p[1],0) for p in pts])
def R(w,l): return P([(-w/2,-l/2),(w/2,-l/2),(w/2,l/2),(-w/2,l/2)])
def up(x,y,h): q=proj(x,y,h); return (float(q[0]),float(q[1]))
def fillR(a,poly,col,al):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(poly)],255,cv2.LINE_AA); mm=(m/255.0*al)[...,None]; return a*(1-mm)+np.array(col)*mm
def court(a,pad=True,clear=False):
    if clear: a=fillR(a,R(*ACC),(236,226,170),0.35)
    if pad: a=fillR(a,R(*PAD),(214,204,188),1.0)
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.int32(R(*COURT))],255,cv2.LINE_AA); mm=(m/255.0)[...,None]
    a=a*(1-mm)+np.array(TERRA)*(1+0.07*TONE[...,None])*mm
    w,l=COURT
    for k,ln in enumerate([R(w,l)]+[P([(-w/2,y),(w/2,y)]) for y in (-SV,0,SV)]+[P([(0,-SV),(0,SV)])]):
        cv2.polylines(a,[np.int32(ln*4)],k==0,(250,244,232),4,cv2.LINE_AA,shift=2)
    return a
def walls(a):
    # Panoramic court, matched to Raj's reference renders (Nov 24): full-height glass back walls with a steel
    # top beam and a ball-stop mesh band above; glass side panels for the first 4 m from each back wall, the
    # first 2 m also topped with mesh; full-height mesh side panels in the middle with one opening per side
    # next to the net. Corner posts and the top mesh reach 13'1" (Raj).
    w,l=COURT; hw,hl=w/2,l/2; TOP=13+1/12; G=9+10/12; M=3.2808   # 1 m in feet
    STEEL=(46,50,58); MESH=(62,68,78)
    def band(p0,p1,lo,hi,kind):
        b=[up(*p0,lo),up(*p1,lo),up(*p1,hi),up(*p0,hi)]
        o=a.copy(); col=(205,228,242) if kind=='glass' else MESH; al=0.30 if kind=='glass' else 0.10
        cv2.fillPoly(o,[np.int32(b)],col,cv2.LINE_AA); a[:]=a*(1-al)+o*al
        if kind=='glass':
            hl_=[up(*p0,hi*0.92),up(*p1,hi*0.92)]; cv2.line(a,(int(hl_[0][0]),int(hl_[0][1])),(int(hl_[1][0]),int(hl_[1][1])),(240,246,250),1,cv2.LINE_AA)
        else:
            L=abs(p1[0]-p0[0])+abs(p1[1]-p0[1]); n=max(2,int(L/0.9))
            for k in range(1,n):
                t=k/n; q=(p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t); u0=up(*q,lo); u1=up(*q,hi)
                cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),MESH,1,cv2.LINE_AA)
            for hh in np.arange(lo+0.9,hi,0.9):
                u0=up(*p0,hh); u1=up(*p1,hh); cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),MESH,1,cv2.LINE_AA)
    def beam(p0,p1,h,th=3):
        u0=up(*p0,h); u1=up(*p1,h); cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),STEEL,th,cv2.LINE_AA)
    def post(x,y,h,th=4):
        bb=P([(x,y)])[0]; t=up(x,y,h); cv2.line(a,(int(bb[0]),int(bb[1])),(int(t[0]),int(t[1])),STEEL,th,cv2.LINE_AA)
    def glass_panels(p0,p1,n,h):
        for k in range(n):
            q0=(p0[0]+(p1[0]-p0[0])*k/n,p0[1]+(p1[1]-p0[1])*k/n); q1=(p0[0]+(p1[0]-p0[0])*(k+1)/n,p0[1]+(p1[1]-p0[1])*(k+1)/n)
            band(q0,q1,0,h,'glass')
            u0=P([q1])[0]; u1=up(*q1,h); cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),(225,235,242),1,cv2.LINE_AA)
    def back(y):
        glass_panels((-hw,y),(hw,y),5,G); band((-hw,y),(hw,y),G,TOP,'mesh')
        beam((-hw,y),(hw,y),G); beam((-hw,y),(hw,y),TOP)
        for x in np.linspace(-hw,hw,6): post(x,y,TOP,5 if abs(x)==hw else 3)
    def side(x,opening_sign):
        # spec (Raj, Nov 24): 4 m of glass at each end (3 m tall), 12 m of 3 m mesh in the middle,
        # 4 m columns; ball-stop mesh above the end glass, stepping down over the second panel.
        for end in (-1,1):
            y0=end*hl; d=-end
            glass_panels((x,y0),(x,y0+d*2*M),1,G); band((x,y0),(x,y0+d*2*M),G,TOP,'mesh')
            glass_panels((x,y0+d*2*M),(x,y0+d*4*M),1,G); band((x,y0+d*2*M),(x,y0+d*4*M),G,G+0.5*M,'mesh')
            beam((x,y0),(x,y0+d*4*M),G); beam((x,y0),(x,y0+d*2*M),TOP); beam((x,y0+d*2*M),(x,y0+d*4*M),G+0.5*M,2)
            post(x,y0+d*2*M,TOP,4); post(x,y0+d*4*M,G+0.5*M,4)
            ystart=y0+d*4*M; yo=d*0.75*M          # opening 1.5 m wide, centered on the net
            band((x,ystart),(x,-yo),0,G,'mesh'); band((x,-yo),(x,0),2.2*M,G,'mesh')
            post(x,-yo,G,3); beam((x,-yo),(x,0),2.2*M,2)
            for yy in np.linspace(ystart,-yo,4)[1:-1]: post(x,yy,G,2)
            beam((x,ystart),(x,0),G,2)
    farx=-hw if math.sin(AZ)>=0 else hw
    back(-hl); side(farx,1); side(-farx,-1); back(hl)
    return a
def finish(a):
    a=a*(1+0.045*STREAK[...,None]); sp=(STIP<0.035)[...,None]; a=np.where(sp,a*0.86+255*0.14,a)
    return np.clip(cv2.GaussianBlur(a,(0,0),0.7)+GRAIN[...,None]*8,0,255).astype(np.uint8)
def dashed(a,pts,closed=True,col=(255,248,230),seg=26,th=4):
    q=list(pts)+([pts[0]] if closed else [])
    for k in range(len(q)-1):
        p0=np.array(q[k],np.float32); p1=np.array(q[k+1],np.float32); n=max(2,int(np.linalg.norm(p1-p0)/seg))
        for j in range(0,n,2):
            s0=p0+(p1-p0)*j/n; s1=p0+(p1-p0)*(j+1)/n; cv2.line(a,(int(s0[0]),int(s0[1])),(int(s1[0]),int(s1[1])),col,th,cv2.LINE_AA)
def stxt(d,s,xy,f,anchor='mm'):
    x,y=xy; d.text((x+3,y+4),s,font=f,fill=(90,50,40,110),anchor=anchor); d.text(xy,s,font=f,fill=(255,255,255,255),anchor=anchor)
def fitf(s,size,w,maxw):
    f=F(size,w)
    while f.getbbox(s)[2]>maxw and size>18: size-=2; f=F(size,w)
    return f
def wrap(s,size,w,maxw):
    words=s.replace(' x ','\u00a0x\u00a0').split(' '); lines=[]; cur=''
    for wd in words:
        t=(cur+' '+wd).strip()
        if F(size,w).getbbox(t)[2]>maxw and cur: lines.append(cur); cur=wd
        else: cur=t
    return lines+[cur] if cur else lines
SC=H/1920 if FMT=='reel' else min(W,H)/1080   # type scale
def textblock(d,title,big,small,top=0):
    x0,y0,x1,y1=C['safe']; mw=x1-x0; cx=(x0+x1)/2
    T=[]   # (string, font) lines in order
    tl=title if isinstance(title,list) else ([title] if title else [])
    sm=small if isinstance(small,list) else ([small] if small else [])
    tsz,bsz,ssz=int(74*SC),int(60*SC),int(36*SC)
    if FMT=='wide': tsz,bsz,ssz=62,54,32; mw=640; cx=x0+mw/2
    ttl=[(s,F(tsz)) for t in tl for s in wrap(t,tsz,800,mw)]
    bg=[(s,F(bsz)) for s in (wrap(big,bsz,800,mw) if big else [])]
    sl=[(s,F(ssz,700)) for t in sm for s in wrap(t,ssz,700,mw)]
    def stack(lines,ytop,gap=1.25):
        y=ytop
        for s,f in lines: h=f.size*gap; stxt(d,s,(cx,y+h/2),f); y+=h
        return y
    if C['text']=='top':
        y=stack(ttl,y0+10+top); y=stack(bg,y+20); stack(sl,y+6)
    elif C['text']=='bottom':
        stack(ttl,y0+10+top)
        hb=sum(f.size*1.25 for _,f in bg)+sum(f.size*1.25 for _,f in sl)+6
        y=stack(bg,y1-hb); stack(sl,y+6)
    else:
        tot=sum(f.size*1.25 for _,f in ttl+bg+sl)+60
        y=stack(ttl,max(y0+top,(y0+y1)/2-tot/2)); y=stack(bg,y+40); stack(sl,y+6)
def page(a,title,big,small=None,extra=None,top=0):
    img=Image.fromarray(finish(a)).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    if extra: extra(img,d)
    textblock(d,title,big,small,top)
    if FMT!='wide': return img   # watermark on YouTube only (Raj, Nov 24)
    x0,y0,x1,y1=C['safe']; h=90
    lg=LOGO.resize((int(LOGO.width*h/LOGO.height),h),Image.LANCZOS); al=lg.getchannel('A').point(lambda v:int(v*0.85)); lg.putalpha(al)
    img.alpha_composite(lg,(int(x1-lg.width),int(y1-lg.height)))
    return img
def lbl(d,s,xy,size=40): stxt(d,s,xy,F(max(22,int(size*SC))))
w,l=COURT
def pg_hook(): return page(walls(court(scene(),pad=False)),"How much space does a padel court need?",None,None)
def pg_court():
    def ex(img,d):
        p=P([(-w/2,l/2+3),(w/2,l/2+3)]); lbl(d,"32'10\"",tuple(p.mean(0)+[0,20*SC]))
        q=P([(w/2+4,-l/2),(w/2+4,l/2)]); lbl(d,"65'7\"",tuple(q.mean(0)+[55*SC,0]))
    return page(walls(court(scene(),pad=False)),"Regulation court: 65'7\" x 32'10\"",None,"Playing area, 2,153 sq ft",ex)
def pg_pad():
    def ex(img,d):
        p=P([(-PAD[0]/2,PAD[1]/2+3),(PAD[0]/2,PAD[1]/2+3)]); lbl(d,"36'",tuple(p.mean(0)+[0,22*SC]))
        q=P([(PAD[0]/2+4,-PAD[1]/2),(PAD[0]/2+4,PAD[1]/2)]); lbl(d,"69'",tuple(q.mean(0)+[50*SC,0]))
    return page(walls(court(scene())),"Concrete pad: 36' x 69'","Includes perimeter ring beam to anchor the court",None,ex)
def pg_total():
    a=walls(court(scene(),clear=True)); dashed(a,R(*ACC))
    def ex(img,d):
        for p in [((ACC[0]+PAD[0])/4,0),(-(ACC[0]+PAD[0])/4,0),(0,-(ACC[1]+PAD[1])/4),(0,(ACC[1]+PAD[1])/4)]: lbl(d,"6'",tuple(P([p])[0]),36)
    return page(a,"Total space you need","About 48' x 81'","Leave about 6' around the pad for machinery and easy access in and out",ex)
def pg_steel():
    def ex(img,d):
        x,y=max([(sx*w/2,sy*l/2) for sx in (-1,1) for sy in (-1,1)],key=lambda c:P([c])[0][1]); b=P([(x,y)])[0]; t=up(x,y,13+1/12); dx=40*SC
        d.line((b[0]+dx,b[1],t[0]+dx,t[1]),fill=(255,255,255,255),width=5)
        for p in (b,t): d.line((p[0]+dx-16,p[1],p[0]+dx+16,p[1]),fill=(255,255,255,255),width=5)
        stxt(d,"13'1\"",(t[0]+dx+18,(b[1]+t[1])/2),F(int(58*SC)),anchor='lm')
    return page(walls(court(scene())),"Tallest steel member: 13'1\"","Glass and mesh walls on a steel frame",None,ex)
def pg_setback():
    a=walls(court(scene(),clear=True)); dashed(a,R(*ACC)); xl=-(ACC[0]/2+17)
    dashed(a,P([(xl,-ACC[1]/2),(xl,ACC[1]/2)]),closed=False,col=(255,236,150),seg=18,th=5)
    def ex(img,d):
        p0=P([(-ACC[0]/2,-8)])[0]; p1=P([(xl,-8)])[0]; d.line((p0[0],p0[1],p1[0],p1[1]),fill=(255,255,255,255),width=4)
        pp=P([(xl,-ACC[1]/2)])[0]; lbl(d,"property line",(min(max(pp[0],C['safe'][0]+110*SC),W-120*SC),pp[1]-30*SC),28)
    return page(a,"Tips before you build","1. Check your town’s setback rules","This decides where on your property a court can go",ex)
def pg_orient():
    def ex(img,d):
        r=60*SC
        if FMT=='wide': cx,cy=C['safe'][0]+640+110,H*0.5
        elif FMT=='reel': cx,cy=C['safe'][0]+r+20,1080   # beside the court, inside the Reels safe zone
        else: cb=P([(0,COURT[1]/2+4.5)])[0][1]; cx=C['cx']; cy=cb+r+40*SC
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,255),width=4)
        a0=P([(0,l/2)])[0]; a1=P([(0,-l/2)])[0]; v=(a1-a0)/np.linalg.norm(a1-a0); n=np.array([-v[1],v[0]])
        tip=(cx+v[0]*(r-8),cy+v[1]*(r-8)); tail=(cx-v[0]*(r-8),cy-v[1]*(r-8)); s1=(cx+n[0]*16,cy+n[1]*16); s2=(cx-n[0]*16,cy-n[1]*16)
        d.polygon([tip,s1,s2],fill=TERRA+(255,)); d.polygon([tail,s1,s2],fill=(255,255,255,255))
        stxt(d,"N",(cx+v[0]*(r+28*SC),cy+v[1]*(r+28*SC)),F(int(36*SC))); stxt(d,"S",(cx-v[0]*(r+28*SC),cy-v[1]*(r+28*SC)),F(int(36*SC)))
    return page(walls(court(scene())),"Tips before you build","2. Run it north-south","Keeps the sun out of players' eyes",ex)
def pg_slope():
    def ex(img,d):
        p=P([(-w/2-3,-l/2),(-w/2-3,l/2)]); d.line((p[0][0],p[0][1],p[1][0],p[1][1]),fill=(255,255,255,255),width=6)
        ang=math.atan2(p[1][1]-p[0][1],p[1][0]-p[0][0])
        for s in (-0.45,0.45): d.line((p[1][0],p[1][1],p[1][0]-30*math.cos(ang+s),p[1][1]-30*math.sin(ang+s)),fill=(255,255,255,255),width=6)
    return page(walls(court(scene())),"Tips before you build","3. Slope the slab 0.5-0.7%","From one short end to the other, so water drains",ex)
def pg_lights():
    a=walls(court(scene()))
    poles=[(-PAD[0]/2-3,-l/2+4),(PAD[0]/2+3,-l/2+4),(-PAD[0]/2-3,l/2-4),(PAD[0]/2+3,l/2-4)]
    for x,y in poles:
        b=P([(x,y)])[0]; t=up(x,y,20); cv2.line(a,(int(b[0]),int(b[1])),(int(t[0]),int(t[1])),(52,56,64),5,cv2.LINE_AA)
        g=np.zeros((H,W),np.float32); cv2.circle(g,(int(t[0]),int(t[1])),int(36*SC)+4,1,-1); g=cv2.GaussianBlur(g,(0,0),16)[...,None]
        a[:]=a*(1-g*0.7)+np.array((255,245,210))*g*0.7
    ub=P([(-(PAD[0]/2+(6 if FMT=='reel' else 12)),l/2-14)])[0]; s=SC
    cv2.rectangle(a,(int(ub[0]-26*s),int(ub[1]-44*s)),(int(ub[0]+26*s),int(ub[1])),(170,170,165),-1); cv2.rectangle(a,(int(ub[0]-26*s),int(ub[1]-44*s)),(int(ub[0]+26*s),int(ub[1])),(90,90,90),3)
    pl=P([poles[2]])[0]; dashed(a,[(ub[0]-26*s,ub[1]-10),(pl[0],pl[1])],closed=False,col=(255,236,150),seg=14,th=4)
    def ex(img,d): lbl(d,"utility box",(ub[0],ub[1]+28*SC),28)
    return page(a,"Tips before you build","3. Want lights?","Plan access to your utility box",ex)
def pg_cta1(): return page(walls(court(scene())),"Permit rules vary by city or county","We plan this early to avoid costly redesigns")
def pg_cta2(): return page(walls(court(scene())),"Get a free court-fit assessment","americanpadellabs.com")
PAGES={'01_hook':pg_hook,'02_court':pg_court,'03_pad':pg_pad,'04_total':pg_total,'05_steel':pg_steel,'06_setback':pg_setback,
       '07_orientation':pg_orient,'09_lights':pg_lights,'10_cta_permits':pg_cta1,'11_cta_help':pg_cta2}
if __name__=='__main__':
    import sys
    out=f'/home/claude/video/pages/{FMT}'; os.makedirs(out,exist_ok=True)
    for k,fn in PAGES.items():
        if len(sys.argv)>1 and k not in sys.argv[1:]: continue
        fn().convert('RGB').save(f'{out}/{k}.jpg',quality=90)
