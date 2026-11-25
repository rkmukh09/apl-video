# Dimensions video stills, illustrated style, one still per key takeaway, in every channel format.
# Usage: FMT=reel|feed|square|wide python3 pages_fmt.py [page ...]
# Text stays inside each format's safe zone (Reels: Meta margins top 270, bottom 672, sides 65, right rail 120).
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FMTS={
 # safe = (x0,y0,x1,y1) where text may go; text: where the caption block sits
 'reel':  dict(W=1080,H=1920,safe=(65,270,960,1248),hz=800, ct=870, cb=1650,cx=512, fw=215,nw=480,text='top'),
 'feed':  dict(W=1080,H=1350,safe=(60,60,1020,1290),hz=370, ct=400, cb=860, cx=540, fw=170,nw=380,text='bottom'),
 'square':dict(W=1080,H=1080,safe=(60,60,1020,1020),hz=250, ct=280, cb=630, cx=540, fw=130,nw=290,text='bottom'),
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
SRC=np.float32([[-24,-40.5],[24,-40.5],[24,40.5],[-24,40.5]])
DST=np.float32([[C['cx']-C['fw'],C['ct']],[C['cx']+C['fw'],C['ct']],[C['cx']+C['nw'],C['cb']],[C['cx']-C['nw'],C['cb']]])
Hm=cv2.getPerspectiveTransform(SRC,DST)
def P(pts): return cv2.perspectiveTransform(np.float32(pts)[None],Hm)[0]
def R(w,l): return P([(-w/2,-l/2),(w/2,-l/2),(w/2,l/2),(-w/2,l/2)])
def ppf(x,y): p=P([(x-0.5,y),(x+0.5,y)]); return float(np.linalg.norm(p[1]-p[0]))
def up(x,y,h): b=P([(x,y)])[0]; return (b[0],b[1]-h*ppf(x,y))
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
    # Regulation enclosure (live article + Raj): back walls 6'7" glass with mesh above; the back corners and the
    # top ball-mesh panels reach 13'1" (4 m); side walls step down to 6'7" toward the net (glass, then mesh).
    w,l=COURT; hw,hl=w/2,l/2; G=6+7/12; TOP=13+1/12; M2=6.5617
    def quad(p0,p1,h0,h1,kind):
        pts=np.float32([P([p0])[0],P([p1])[0],up(*p1,h1),up(*p0,h0)])
        o=a.copy()
        if kind=='glass':
            cv2.fillPoly(o,[np.int32(pts)],(200,225,240),cv2.LINE_AA); a[:]=a*0.75+o*0.25
            cv2.polylines(a,[np.int32(pts)],True,(235,240,245),2,cv2.LINE_AA)
        else:
            cv2.fillPoly(o,[np.int32(pts)],(70,76,86),cv2.LINE_AA); a[:]=a*0.88+o*0.12
            n=max(2,int(abs(np.linalg.norm(np.array(p1)-np.array(p0)))/1.6))
            for k in range(1,n):
                t=k/n; q=(p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t); b0=P([q])[0]; b1=up(*q,h0)
                cv2.line(a,(int(b0[0]),int(b0[1]-(0 if h0==h1 else 0))),(int(b1[0]),int(b1[1])),(60,66,76),1,cv2.LINE_AA)
            for hh in np.arange(1.6,max(h0,h1),1.6):
                b0=up(*p0,hh); b1=up(*p1,hh); cv2.line(a,(int(b0[0]),int(b0[1])),(int(b1[0]),int(b1[1])),(60,66,76),1,cv2.LINE_AA)
    def wall(p0,p1,lo,hi,kind): 
        # lo..hi vertical band: draw as quad from base offset lo up to hi
        pts0=up(*p0,lo); pts1=up(*p1,lo)
        if kind=='glass': quad(p0,p1,hi,hi,'glass') if lo==0 else None
    def band(p0,p1,lo,hi,kind):
        b=[up(*p0,lo),up(*p1,lo),up(*p1,hi),up(*p0,hi)]
        o=a.copy(); col=(200,225,240) if kind=='glass' else (70,76,86); al=0.25 if kind=='glass' else 0.12
        cv2.fillPoly(o,[np.int32(b)],col,cv2.LINE_AA); a[:]=a*(1-al)+o*al
        if kind=='glass': cv2.polylines(a,[np.int32(b)],True,(235,240,245),2,cv2.LINE_AA)
        else:
            L=abs(p1[0]-p0[0])+abs(p1[1]-p0[1]); n=max(2,int(L/1.4))
            for k in range(0,n+1):
                t=k/n; q=(p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t); u0=up(*q,lo); u1=up(*q,hi)
                cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),(64,70,80),1,cv2.LINE_AA)
            for hh in np.arange(lo,hi+0.01,1.4):
                u0=up(*p0,hh); u1=up(*p1,hh); cv2.line(a,(int(u0[0]),int(u0[1])),(int(u1[0]),int(u1[1])),(64,70,80),1,cv2.LINE_AA)
            cv2.polylines(a,[np.int32(b)],True,(60,64,72),2,cv2.LINE_AA)
    def post(x,y,h):
        b=P([(x,y)])[0]; t=up(x,y,h); cv2.line(a,(int(b[0]),int(b[1])),(int(t[0]),int(t[1])),(52,56,64),4,cv2.LINE_AA)
    def back(y):
        band((-hw,y),(hw,y),0,G,'glass'); band((-hw,y),(hw,y),G,TOP,'mesh')
        for x in np.linspace(-hw,hw,6): post(x,y,TOP)
    def side(x,sgn):
        # from the far back (y=-hl) toward the net, then from the net to the near back (y=+hl)
        for end in (-1,1):
            y0=end*hl; d=-end
            band((x,y0),(x,y0+d*M2),0,G,'glass'); band((x,y0),(x,y0+d*M2),G,TOP,'mesh')
            band((x,y0+d*M2),(x,y0+d*2*M2),0,G,'glass')
            band((x,y0+d*2*M2),(x,0),0,G,'mesh')
            post(x,y0,TOP); post(x,y0+d*M2,TOP); post(x,y0+d*2*M2,G)
        post(x,0,G)
    back(-hl)
    for x in (-hw,hw): side(x,1)
    back(hl)
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
        y=stack(bg,y1-hb-int(110*SC)); stack(sl,y+6)
    else:
        tot=sum(f.size*1.25 for _,f in ttl+bg+sl)+60
        y=stack(ttl,max(y0+top,(y0+y1)/2-tot/2)); y=stack(bg,y+40); stack(sl,y+6)
def page(a,title,big,small=None,extra=None,top=0):
    img=Image.fromarray(finish(a)).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
    if extra: extra(img,d)
    textblock(d,title,big,small,top)
    x0,y0,x1,y1=C['safe']; h=int(100*SC) if FMT!='wide' else 90
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
    return page(a,"Total space you need","48' x 81'","Plus around 6' around the pad, for machinery and easy access in and out",ex)
def pg_steel():
    def ex(img,d):
        x,y=w/2,l/2; b=P([(x,y)])[0]; t=up(x,y,13+1/12); dx=50*SC
        d.line((b[0]+dx,b[1],t[0]+dx,t[1]),fill=(255,255,255,255),width=5)
        for p in (b,t): d.line((p[0]+dx-16,p[1],p[0]+dx+16,p[1]),fill=(255,255,255,255),width=5)
        stxt(d,"13'1\"",(t[0]+dx+18,(b[1]+t[1])/2),F(int(58*SC)),anchor='lm')
    return page(walls(court(scene())),"Tallest steel member: 13'1\"","Glass and mesh walls on a steel frame",None,ex)
def pg_setback():
    a=walls(court(scene(),clear=True)); dashed(a,R(*ACC)); xl=ACC[0]/2+17
    dashed(a,P([(xl,-ACC[1]/2-4),(xl,ACC[1]/2+2)]),closed=False,col=(255,236,150),seg=18,th=5)
    def ex(img,d):
        p0=P([(ACC[0]/2,-8)])[0]; p1=P([(xl,-8)])[0]; d.line((p0[0],p0[1],p1[0],p1[1]),fill=(255,255,255,255),width=4)
        pp=P([(xl,-ACC[1]/2+2)])[0]; lbl(d,"property line",(min(pp[0],W-120*SC),pp[1]-30*SC),28)
    return page(a,"Tips before you build","1. Check your town’s setback rules","This decides where on your property a court can go",ex)
def pg_orient():
    def ex(img,d):
        r=60*SC
        if FMT=='wide': cx,cy=C['safe'][0]+640+110,H*0.5
        elif FMT=='reel': cx,cy=C['safe'][0]+r+20,1080   # beside the court, inside the Reels safe zone
        else: cb=P([(0,COURT[1]/2+4.5)])[0][1]; cx=C['cx']; cy=cb+r+40*SC
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,255),width=4)
        d.polygon([(cx,cy-r+8),(cx-16,cy),(cx+16,cy)],fill=TERRA+(255,)); d.polygon([(cx,cy+r-8),(cx-16,cy),(cx+16,cy)],fill=(255,255,255,255))
        stxt(d,"N",(cx,cy-r-26*SC),F(int(36*SC))); stxt(d,"S",(cx,cy+r+26*SC),F(int(36*SC)))
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
    ub=P([(PAD[0]/2+12,l/2-14)])[0]; s=SC
    cv2.rectangle(a,(int(ub[0]-26*s),int(ub[1]-44*s)),(int(ub[0]+26*s),int(ub[1])),(170,170,165),-1); cv2.rectangle(a,(int(ub[0]-26*s),int(ub[1]-44*s)),(int(ub[0]+26*s),int(ub[1])),(90,90,90),3)
    pl=P([poles[3]])[0]; dashed(a,[(ub[0]-26*s,ub[1]-10),(pl[0],pl[1])],closed=False,col=(255,236,150),seg=14,th=4)
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
