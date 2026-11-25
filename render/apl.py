import numpy as np, cv2, math, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B=lambda *a: os.path.join(ROOT,'brand',*a)
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
DUR=46.0
NAVY=(44,74,114)       # hsl(217 42% 31%) site header/footer
DEEP=(0,34,102)        # hsl(220 100% 20%) primary
COURT=(52,88,135)
WHITE=(255,255,255)
SLATE=(166,178,201)    # hsl(220 20% 70%)
GLASS=(150,190,230)
BEB=B('fonts','figtree-latin-800-normal.woff')  # Figtree for all video text (Raj, Nov 24 2026)
INT=B('fonts','figtree-latin-%d-normal.woff')
_fc={}
def F(kind,size,w=600):
    k=(kind,size,w)
    if k not in _fc: _fc[k]=ImageFont.truetype(BEB if kind=='b' else INT%w,size)
    return _fc[k]
def cl(x): return max(0.0,min(1.0,x))
def ease(x):
    x=cl(x); return x*x*(3-2*x)
def eout(x):
    x=cl(x); return 1-(1-x)**3
def prog(t,a,b): return cl((t-a)/(b-a))

LOGO=Image.open(B('logo.png')).convert('RGBA')
PHOTO=Image.open(B('photos','overhead-court.jpg')).convert('RGB').rotate(90,expand=True)  # court long axis vertical
pw=W; ph=int(PHOTO.height*W/PHOTO.width)
PHOTO=PHOTO.resize((pw,ph),Image.LANCZOS)

def bg():
    a=np.zeros((H,W,3),np.float32)
    y=np.linspace(0,1,H)[:,None,None]
    a[:]=np.array(NAVY,np.float32)*(1-0.35*y)+np.array(DEEP,np.float32)*0.35*y
    # subtle court-line grid texture
    a[::120,:,:]+=4; a[:,::120,:]+=4
    return np.clip(a,0,255).astype(np.uint8)
BG=bg()

def fit(kind,size,s,maxw=980,w=600):
    while size>20 and F(kind,size,w).getbbox(s)[2]>maxw: size-=2
    return F(kind,size,w)

def text(img,s,xy,font,fill=WHITE,anchor='la',alpha=1.0,dy=0):
    if alpha<=0: return
    d=ImageDraw.Draw(img,'RGBA')
    x,y=xy
    d.text((x,y+dy),s,font=font,fill=fill+(int(255*alpha),),anchor=anchor)

def vtext(img,s,center,font,fill=WHITE,alpha=1.0):
    if alpha<=0: return
    bb=font.getbbox(s); tw,th=bb[2]+10,bb[3]+10
    t=Image.new('RGBA',(tw,th),(0,0,0,0))
    ImageDraw.Draw(t).text((5,0),s,font=font,fill=fill+(int(255*alpha),))
    t=t.rotate(90,expand=True)
    img.alpha_composite(t,(int(center[0]-t.width/2),int(center[1]-t.height/2)))

def line(a,p,q,col,th,frac=1.0,alpha=1.0):
    if frac<=0 or alpha<=0: return
    q2=(p[0]+(q[0]-p[0])*frac,p[1]+(q[1]-p[1])*frac)
    ov=a.copy()
    cv2.line(ov,(int(p[0]*4),int(p[1]*4)),(int(q2[0]*4),int(q2[1]*4)),col,th,cv2.LINE_AA,shift=2)
    if alpha<1: cv2.addWeighted(ov,alpha,a,1-alpha,0,a)
    else: a[:]=ov

def poly(a,pts,col,th,frac=1.0,alpha=1.0,closed=True):
    pts=list(pts)+([pts[0]] if closed else [])
    L=[math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)]; tot=sum(L); rem=tot*frac
    for i,l in enumerate(L):
        if rem<=0: break
        f=min(1,rem/l); line(a,pts[i],pts[i+1],col,th,f,alpha); rem-=l

def dashed_rect(a,x0,y0,x1,y1,col,th,alpha=1.0,on=22,off=14):
    for p,q in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:
        L=math.dist(p,q); n=0.0
        while n<L:
            e=min(L,n+on)
            line(a,(p[0]+(q[0]-p[0])*n/L,p[1]+(q[1]-p[1])*n/L),(p[0]+(q[0]-p[0])*e/L,p[1]+(q[1]-p[1])*e/L),col,th,1,alpha)
            n+=on+off

def rectfill(a,x0,y0,x1,y1,col,alpha):
    if alpha<=0: return
    ov=a.copy(); cv2.rectangle(ov,(int(x0),int(y0)),(int(x1),int(y1)),col,-1)
    cv2.addWeighted(ov,alpha,a,1-alpha,0,a)

def dimline_v(a,x,y0,y1,frac,alpha=1.0):
    ym=(y0+y1)/2; h=(y1-y0)/2*frac
    line(a,(x,ym),(x,ym-h),WHITE,3,1,alpha); line(a,(x,ym),(x,ym+h),WHITE,3,1,alpha)
    if frac>0.98:
        for y in (y0,y1): line(a,(x-16,y),(x+16,y),WHITE,3,1,alpha)
def dimline_h(a,y,x0,x1,frac,alpha=1.0):
    xm=(x0+x1)/2; w=(x1-x0)/2*frac
    line(a,(xm,y),(xm-w,y),WHITE,3,1,alpha); line(a,(xm,y),(xm+w,y),WHITE,3,1,alpha)
    if frac>0.98:
        for x in (x0,x1): line(a,(x,y-16),(x,y+16),WHITE,3,1,alpha)

# ---------- top view geometry ----------
PX=50.0; CX,CY=540,1080
CL,CR,CT,CB=CX-5*PX,CX+5*PX,CY-10*PX,CY+10*PX
SV=6.95*PX
FL,FR,FT,FB=CX-10.97/2*PX,CX+10.97/2*PX,CY-21.03/2*PX,CY+21.03/2*PX

def heading(img,s,sub,t0,t,y=215):
    p=eout(prog(t,t0,t0+0.5))
    text(img,s,(W//2,y),fit('b',104,s),anchor='mm',alpha=p,dy=(1-p)*30)
    if sub: 
        p2=eout(prog(t,t0+0.25,t0+0.75))
        text(img,sub,(W//2,y+80),F('i',38,500),fill=SLATE,anchor='mm',alpha=p2,dy=(1-p2)*20)

def caption(img,lines,t0,t,y=1700,alpha=1.0):
    for i,(s,big) in enumerate(lines):
        p=eout(prog(t,t0+i*0.25,t0+i*0.25+0.5))*alpha
        if big:
            sz=84
            while F('b',sz).getbbox(s)[2]>980: sz-=4
            text(img,s,(W//2,y+i*90),F('b',sz),anchor='mm',alpha=p,dy=(1-p)*25)
        else:
            sz=40
            while F('i',sz,600).getbbox(s)[2]>1000: sz-=2
            text(img,s,(W//2,y+i*90),F('i',sz,600),fill=SLATE,anchor='mm',alpha=p,dy=(1-p)*25)

def brand_tag(img,alpha=1.0):
    text(img,"A M E R I C A N   P A D E L   L A B S",(W//2,92),F('b',38),fill=SLATE,anchor='mm',alpha=alpha)

def court_top(a,t,draw=1.0,lines=1.0,alpha=1.0):
    rectfill(a,CL,CT,CR,CB,COURT,0.9*alpha*ease(draw))
    poly(a,[(CL,CT),(CR,CT),(CR,CB),(CL,CB)],WHITE,6,ease(draw),alpha)
    # net
    line(a,(CL-14,CY),(CR+14,CY),WHITE,5,ease(lines),alpha)
    # service lines + center line
    for y in (CY-SV,CY+SV): line(a,(CL,y),(CR,y),WHITE,3,ease(prog(lines,0.2,0.8)),alpha)
    line(a,(CX,CY-SV),(CX,CY+SV),WHITE,3,ease(prog(lines,0.5,1)),alpha)

# ---------- scenes ----------
def s_hook(img,a,t):
    # photo with slow zoom, crossfades out 3.6-4.4
    z=1.12-0.06*t/4
    pw2,ph2=int(W*z),int(PHOTO.height*z)
    im=PHOTO.resize((pw2,ph2),Image.BILINEAR)
    ox=(pw2-W)//2; oy=(ph2-H)//2
    crop=np.array(im)[max(0,oy):max(0,oy)+H, ox:ox+W]
    canvas=a.copy(); hh=min(H,crop.shape[0]); y0=(H-hh)//2
    canvas[y0:y0+hh]=crop[:hh]
    # navy gradient for legibility
    g=np.linspace(0,1,H)[:,None,None]
    shade=np.clip(0.75-1.3*g,0,0.75)+np.clip((g-0.7)*2.0,0,0.6)
    canvas=(canvas*(1-shade)+np.array(DEEP)*shade).astype(np.uint8)
    f=ease(prog(t,3.6,4.4))
    a[:]=(canvas*(1-f)+a*f).astype(np.uint8)
    return f

def frame(t):
    a=BG.copy()
    img=None
    post=[]   # text ops after raster
    # ----- S1 hook 0-4.4
    if t<4.4:
        f=s_hook(None,a,t)
        def p1(img,t=t,f=f):
            al=1-f
            brand_tag(img,al)
            p=eout(prog(t,0.3,0.9)); 
            for i,s in enumerate(["HOW MUCH SPACE","DOES A PADEL COURT","ACTUALLY NEED?"]):
                pp=eout(prog(t,0.3+i*0.2,0.9+i*0.2))
                text(img,s,(W//2,330+i*125),fit('b',112,"DOES A PADEL COURT"),anchor='mm',alpha=pp*al,dy=(1-pp)*40)
            pp=eout(prog(t,1.4,2.0))
            text(img,"Padel court dimensions, explained",(W//2,1780),F('i',44,600),anchor='mm',alpha=pp*al)
        post.append(p1)
    # ----- top view scenes 3.6-17.4 and 25-34.4
    topA = ease(prog(t,3.6,4.4))*(1-ease(prog(t,16.8,17.4))) + ease(prog(t,24.8,25.4))*(1-ease(prog(t,33.8,34.4)))
    if topA>0:
        if t<20: draw=prog(t,4.4,6.0); ln=prog(t,11.0,13.0)
        else: draw=1; ln=1
        court_top(a,t,draw,ln,topA)
        if t<20:
            # dims of court
            fa=topA*(1-ease(prog(t,10.6,11.0)))
            dimline_h(a,CT-60,CL,CR,ease(prog(t,6.0,6.8)),fa)
            dimline_v(a,CR+70,CT,CB,ease(prog(t,6.8,7.6)),fa)
            # net-to-service dim on left
            sa=topA*ease(prog(t,13.4,13.9))
            dimline_v(a,CL-60,CY-SV,CY,ease(prog(t,13.4,14.2)),sa)
            # net pulse
            pulse=ease(prog(t,11.0,11.4))*(1-ease(prog(t,12.6,13.2)))
            if pulse>0: line(a,(CL-14,CY),(CR+14,CY),(255,255,255),14,1,0.35*pulse*topA)
        else:
            # footprint
            g=ease(prog(t,25.8,27.2))
            x0=CL+(FL-CL)*g; x1=CR+(FR-CR)*g; y0=CT+(FT-CT)*g; y1=CB+(FB-CB)*g
            if g>0:
                rectfill(a,x0,y0,x1,y1,(255,255,255),0.07*topA)
                dashed_rect(a,x0,y0,x1,y1,WHITE,4,topA)
            da=topA*ease(prog(t,27.2,27.8))
            dimline_h(a,FT-50,FL,FR,ease(prog(t,27.2,27.9)),da)
            dimline_v(a,FR+60,FT,FB,ease(prog(t,27.5,28.2)),da)
            # ring beam highlight
            rb=ease(prog(t,29.0,29.5))*(1-ease(prog(t,30.3,30.8)))
            if rb>0: poly(a,[(CL,CT),(CR,CT),(CR,CB),(CL,CB)],(255,255,255),18,1,0.45*rb*topA)
        def p2(img,t=t,topA=topA):
            brand_tag(img,topA)
            if t<20:
                h1=topA*(1-ease(prog(t,10.6,11.0)))
                if h1>0:
                    heading(img,"THE COURT",None,4.6,t)
                    al=h1*ease(prog(t,6.6,7.0))
                    text(img,"32'10\"",(CX-10,CT-110),F('b',72),anchor='rm',alpha=al)
                    text(img,"(10M)",(CX+10,CT-106),F('b',48),fill=SLATE,anchor='lm',alpha=al)
                    al=h1*ease(prog(t,7.4,7.8))
                    vtext(img,"65'7\"  (20M)",(CR+125,CY),F('b',72),alpha=al)
                    caption(img,[("65'7\" X 32'10\"",True),("20m x 10m  ·  2,153 sq ft (200 m²) of turf",False)],8.2,t,alpha=h1)
                h2=topA*ease(prog(t,11.0,11.4))
                if h2>0:
                    heading(img,"NET + SERVICE LINES",None,11.0,t)
                    al=h2*ease(prog(t,11.4,11.9))
                    text(img,"NET",(CR+30,CY-4),F('b',56),anchor='lm',alpha=al)
                    al=h2*ease(prog(t,14.0,14.5))
                    vtext(img,"22'10\" (6.95M)",(CL-115,CY-SV/2),F('b',54),alpha=al)
                    caption(img,[("NET: 2'11\" CENTER, 3'0\" POSTS",True),("0.88m center, 0.92m posts",False)],11.6,t,alpha=h2*(1-ease(prog(t,13.8,14.1))))
                    caption(img,[("SERVICE LINE: 22'10\" FROM NET",True),("6.95m from the net",False)],14.2,t,alpha=h2)
            else:
                heading(img,"THE SPACE YOU NEED",None,25.4,t)
                al=topA*ease(prog(t,27.7,28.2))
                text(img,"36'",(CX-10,FT-100),F('b',72),anchor='rm',alpha=al)
                text(img,"(11M)",(CX+10,FT-96),F('b',48),fill=SLATE,anchor='lm',alpha=al)
                vtext(img,"69'  (21M)",(FR+115,CY),F('b',72),alpha=al)
                caption(img,[("PLAN FOR 36' X 69'",True),("11m x 21m footprint",False)],28.0,t,y=1690,alpha=topA*(1-ease(prog(t,30.8,31.1))))
                # reasons
                rs=["RING BEAM","ACCESS","MACHINERY","GAMEPLAY"]
                if t>31.1:
                    text(img,"Room for:",(W//2,1675),F('i',38,500),fill=SLATE,anchor='mm',alpha=topA*ease(prog(t,31.15,31.5)))
                for i,s in enumerate(rs):
                    p=eout(prog(t,31.4+i*0.45,31.9+i*0.45))*topA
                    if p<=0: continue
                    d=ImageDraw.Draw(img,'RGBA'); fx=F('b',52)
                    tw=fx.getbbox(s)[2]; cx=[W//2-255,W//2+255][i%2]; cy=1755+(i//2)*95
                    d.rounded_rectangle((cx-tw/2-26,cy-38+(1-p)*20,cx+tw/2+26,cy+38+(1-p)*20),radius=38,fill=(255,255,255,int(235*p)))
                    text(img,s,(cx,cy+3+(1-p)*20),fx,fill=DEEP,anchor='mm',alpha=p)
        post.append(p2)
    # ----- S4 walls 17.0-25.4
    wA=ease(prog(t,17.0,17.6))*(1-ease(prog(t,24.6,25.2)))
    if wA>0:
        S=88; x0=W//2-5*S; x1=W//2+5*S; yb=820; yg=yb-2*S; yt=yb-3*S
        p=ease(prog(t,17.6,18.6))
        rectfill(a,x0,yg,x1,yb,GLASS,0.35*wA*p)
        # mesh grid
        mp=ease(prog(t,18.3,19.2))
        if mp>0:
            for x in np.arange(x0,x1+1,22): line(a,(x,yg),(x,yg-(yg-yt)*mp),SLATE,2,1,wA*0.8)
            for y in np.arange(yg,yt-1,-22):
                if yg-y<= (yg-yt)*mp: line(a,(x0,y),(x1,y),SLATE,2,1,wA*0.8)
        poly(a,[(x0,yb),(x0,yt),(x1,yt),(x1,yb)],WHITE,6,p,wA,closed=False)
        line(a,(x0,yg),(x1,yg),WHITE,4,p,wA)
        line(a,(x0-60,yb),(x1+60,yb),WHITE,4,1,wA)
        # posts
        for xx in np.linspace(x0,x1,6): line(a,(xx,yb),(xx,yt),WHITE,3,p,wA*0.7)
        dimline_v(a,x1+40,yt,yb,ease(prog(t,19.2,19.9)),wA)
        # side profile (half court, back wall to net)
        sp=ease(prog(t,21.2,22.6)); sA=wA*ease(prog(t,21.0,21.4))
        if sA>0:
            Sx=88; sx0=W//2-5*Sx; sb=1440
            pts=[(sx0,sb),(sx0,sb-3*Sx),(sx0+4*Sx,sb-3*Sx),(sx0+4*Sx,sb-2*Sx),(sx0+10*Sx,sb-2*Sx),(sx0+10*Sx,sb)]
            rectfill(a,sx0,sb-2*Sx,sx0+10*Sx,sb,GLASS,0.25*sA*sp)
            poly(a,pts,WHITE,6,sp,sA,closed=False)
            line(a,(sx0-40,sb),(sx0+10*Sx+60,sb),WHITE,4,1,sA)
        def p3(img,t=t,wA=wA,x1=x1,yt=yt,yb=yb,yg=yg,x0=x0):
            brand_tag(img,wA)
            heading(img,"THE WALLS",None,17.4,t)
            al=wA*ease(prog(t,18.6,19.1))
            text(img,"GLASS 6'7\" (2M)",(W//2,(yg+yb)//2),F('b',60),fill=DEEP if False else WHITE,anchor='mm',alpha=al)
            al=wA*ease(prog(t,19.2,19.7))
            text(img,"MESH 3'3\" (1M)",(W//2,(yt+yg)//2),F('b',50),anchor='mm',alpha=al)
            al=wA*ease(prog(t,19.9,20.3))
            text(img,"TOTAL HEIGHT 9'10\" (3M)",(W//2,yt-50),F('b',58),anchor='mm',alpha=al)
            text(img,"BACK WALL",(W//2,yb+50),F('i',34,600),fill=SLATE,anchor='mm',alpha=wA*ease(prog(t,18.2,18.7)))
            sA=wA*ease(prog(t,21.0,21.4))
            if sA>0:
                text(img,"SIDE WALL (BACK WALL TO NET)",(W//2,1440+50),F('i',34,600),fill=SLATE,anchor='mm',alpha=sA)
                al=wA*ease(prog(t,22.4,22.9))
                text(img,"9'10\"",(W//2-5*88+2*88,1440-3*88-40),F('b',56),anchor='mm',alpha=al)
                text(img,"6'7\"",(W//2-5*88+7*88,1440-2*88-40),F('b',56),anchor='mm',alpha=al)
            caption(img,[("SIDES STEP DOWN TO 6'7\" (2M)",True),("3m at the back, stepping down to 2m toward the net",False)],22.8,t,y=1660,alpha=wA)
        post.append(p3)
    # ----- S6 indoor 34.0-40.4
    iA=ease(prog(t,34.0,34.6))*(1-ease(prog(t,39.8,40.4)))
    if iA>0:
        S=45; x0=W//2-10*S; x1=W//2+10*S; yb=1250
        p=ease(prog(t,34.6,35.6))
        # court side elevation: 3m at ends, 2m middle
        pts=[(x0,yb),(x0,yb-3*S),(x0+4*S,yb-3*S),(x0+4*S,yb-2*S),(x1-4*S,yb-2*S),(x1-4*S,yb-3*S),(x1,yb-3*S),(x1,yb)]
        rectfill(a,x0,yb-2*S,x1,yb,GLASS,0.25*iA*p)
        poly(a,pts,WHITE,5,p,iA,closed=False)
        line(a,(x0-40,yb),(x1+40,yb),WHITE,4,1,iA)
        line(a,(W//2,yb),(W//2,yb-0.9*S),WHITE,3,p,iA)  # net
        # ceilings
        c1=ease(prog(t,35.8,36.6))
        rectfill(a,x0-40,yb-8*S,x0-40+(x1-x0+80)*c1,yb-7*S,(255,255,255),0.18*iA)
        dashed_rect(a,x0-40,yb-6*S,x0-40+(x1-x0+80)*c1,yb-6*S,WHITE,4,iA*c1)
        dimline_v(a,x0-80,yb-6*S,yb,ease(prog(t,36.4,37.0)),iA)
        def p4(img,t=t,iA=iA,yb=yb,S=S):
            brand_tag(img,iA)
            heading(img,"INDOORS",None,34.4,t)
            al=iA*ease(prog(t,36.6,37.1))
            text(img,"MIN. CEILING 19'8\" (6M)",(W//2,yb-6*S+38),F('b',54),anchor='mm',alpha=al)
            al=iA*ease(prog(t,37.2,37.7))
            text(img,"COMPETITION: 23'-26'3\" (7-8M)",(W//2,yb-8*S-38),F('b',54),fill=SLATE,anchor='mm',alpha=al)
            text(img,"SIDE VIEW, FULL COURT",(W//2,yb+50),F('i',34,600),fill=SLATE,anchor='mm',alpha=iA)
            caption(img,[("19'8\" OF CLEAR HEIGHT",True),("6m minimum above the whole playing surface",False)],37.4,t,y=1640,alpha=iA)
        post.append(p4)
    # ----- S7 CTA 39.8-46
    eA=ease(prog(t,39.8,40.6))
    if eA>0:
        def p5(img,t=t,eA=eA):
            lg=LOGO.resize((int(LOGO.width*420/LOGO.height),420),Image.LANCZOS)
            p=eout(prog(t,40.2,40.9))
            lg.putalpha(lg.getchannel('A').point(lambda v:int(v*p)))
            img.alpha_composite(lg,(W//2-lg.width//2,330+int((1-p)*30)))
            for i,(s,f,c) in enumerate([("WILL A COURT FIT YOUR PROPERTY?",fit('b',76,"WILL A COURT FIT YOUR PROPERTY?"),WHITE),("Free court-fit assessment",F('i',46,600),SLATE),("AMERICANPADELLABS.COM",fit('b',70,"AMERICANPADELLABS.COM"),WHITE)]):
                pp=eout(prog(t,41.0+i*0.35,41.6+i*0.35))
                text(img,s,(W//2,960+i*130),f,fill=c,anchor='mm',alpha=pp,dy=(1-pp)*25)
        post.append(p5)
    img=Image.fromarray(a).convert('RGBA')
    for fn in post: fn(img)
    if eA>0:
        # CTA background fade over everything except its own text: redo
        base=Image.fromarray(BG).convert('RGBA')
        img=Image.blend(img,base,eA*0.0)
    return np.array(img.convert('RGB'))
