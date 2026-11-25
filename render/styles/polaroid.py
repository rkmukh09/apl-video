# Style sample: instant-film scrapbook. Polaroids drop onto a corkboard with a small bounce; slow pan.
from common import *
N=320
rng=np.random.default_rng(11)
BW,BH=1080,4100
F=lambda sz,w=800: font(f'figtree-latin-{w}-normal',sz)
def cork():
    a=np.zeros((BH,BW,3),np.float32); a[:]=(176,128,82)
    n1=cv2.GaussianBlur(rng.normal(0,1,(BH,BW)).astype(np.float32),(0,0),1.2)*14
    n2=cv2.resize(cv2.GaussianBlur(rng.normal(0,1,(BH//8,BW//8)).astype(np.float32),(0,0),3),(BW,BH))*10
    a+=(n1+n2)[...,None]
    spots=rng.random((BH,BW))>0.985; a[spots]*=0.72
    y,x=np.mgrid[0:H,0:W]; return np.clip(a,0,255).astype(np.uint8)
CORK=cork()
IW=660
def illus(step):
    # faded, warm, grainy top-view illustration; step 0..3 shows court, pad, clearance, total
    S=IW; a=np.zeros((S,S,3),np.float32); a[:]=(236,222,196)
    s=7.0; cx,cy=S/2,S/2
    def R(wl): w,l=wl; return (int(cx-w*s/2),int(cy-l*s/2),int(cx+w*s/2),int(cy+l*s/2))
    A=R(ACC);P=R(PAD);C=R(COURT)
    if step>=2: cv2.rectangle(a,A[:2],A[2:],(196,206,170),-1)
    if step>=1: cv2.rectangle(a,P[:2],P[2:],(170,146,116),-1)
    cv2.rectangle(a,C[:2],C[2:],(92,128,150),-1)
    L=(245,238,225)
    cv2.rectangle(a,C[:2],C[2:],L,3,cv2.LINE_AA); cv2.line(a,(C[0]-6,int(cy)),(C[2]+6,int(cy)),L,4,cv2.LINE_AA)
    for y in (cy-SV*s,cy+SV*s): cv2.line(a,(C[0],int(y)),(C[2],int(y)),L,2,cv2.LINE_AA)
    cv2.line(a,(int(cx),int(cy-SV*s)),(int(cx),int(cy+SV*s)),L,2,cv2.LINE_AA)
    if step>=2:
        for k in range(0,A[2]-A[0],18): cv2.line(a,(A[0]+k,A[1]),(A[0]+k+9,A[1]),(90,80,60),2); cv2.line(a,(A[0]+k,A[3]),(A[0]+k+9,A[3]),(90,80,60),2)
        for k in range(0,A[3]-A[1],18): cv2.line(a,(A[0],A[1]+k),(A[0],A[1]+k+9),(90,80,60),2); cv2.line(a,(A[2],A[1]+k),(A[2],A[1]+k+9),(90,80,60),2)
    # instant-film look: fade, warm cast, grain, vignette, soft bloom
    a=a*0.82+np.array([240,215,180])*0.18
    a=a*0.85+cv2.GaussianBlur(a,(0,0),6)*0.15
    a+=rng.normal(0,7,(S,S,1))
    y,x=np.mgrid[0:S,0:S]; v=((x-S/2)**2+(y-S/2)**2)/(S/2)**2; a*=(1-0.22*v)[...,None]
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
CAPS=["the court  32'10\" x 65'7\"","concrete pad  36' x 69'","+ 6' clear all around","total  48' x 81'"]
def polaroid(k):
    pw,ph=IW+60,IW+60+170
    im=Image.new('RGBA',(pw,ph),(250,248,242,255)); im.paste(illus(k),(30,30))
    d=ImageDraw.Draw(im); f=F(44,800)
    s=CAPS[k]
    while f.getbbox(s)[2]>pw-60: f=F(f.size-2,800)
    d.text((pw//2,IW+60+82),s,font=f,fill=(38,34,40,255),anchor='mm')
    return im
POL=[polaroid(k) for k in range(4)]
SLOTS=[(500,760,-4.0,'tape'),(580,1640,3.0,'pin'),(490,2520,-2.5,'tape'),(570,3400,5.0,'pin')]
LAND=[18,96,178,256]
def tape(w=210,h=64):
    t=Image.new('RGBA',(w,h),(232,222,190,170)); d=ImageDraw.Draw(t)
    for x in (0,w-1):
        for y in range(0,h,6): d.point((x,y),fill=(0,0,0,0))
    return t
def pin(img,xy):
    d=ImageDraw.Draw(img); x,y=xy
    d.ellipse((x-24+6,y-24+8,x+24+6,y+24+8),fill=(0,0,0,70))
    d.ellipse((x-24,y-24,x+24,y+24),fill=(196,48,40,255)); d.ellipse((x-12,y-15,x-2,y-5),fill=(240,150,140,255))
def board(t):
    b=Image.fromarray(CORK).convert('RGBA')
    for k,(x,y,rot,acc) in enumerate(SLOTS):
        if t<LAND[k]: continue
        u=(t-LAND[k])/30*FPS/30
        # drop: falls in from above and larger, small bounce on landing
        if u<0.33: s=1.18-0.21*ss(u/0.33); dy=-60*(1-ss(u/0.33))
        elif u<0.55: s=0.97+0.03*ss((u-0.33)/0.22); dy=0
        else: s=1.0; dy=0
        p=POL[k].resize((int(POL[k].width*s),int(POL[k].height*s)),Image.BICUBIC).rotate(rot,expand=True,resample=Image.BICUBIC)
        sh=Image.new('RGBA',p.size,(0,0,0,0)); sh.putalpha(p.getchannel('A').point(lambda v:int(v*0.45)))
        sh=sh.filter(ImageFilter.GaussianBlur(12+20*(s-1)*5)); off=int(10+60*(s-1))
        b.alpha_composite(sh,(int(x-p.width/2+off),int(y-p.height/2+dy+off+6)))
        b.alpha_composite(p,(int(x-p.width/2),int(y-p.height/2+dy)))
        if u>=0.4:
            if acc=='tape':
                tp=tape().rotate(rot+(-8 if k%2 else 8),expand=True); b.alpha_composite(tp,(int(x-tp.width/2),int(y-p.height/2-18)))
            else: pin(b,(int(x),int(y-p.height/2+36)))
    return b
CAMY=[(0,0),(68,0),(98,680),(150,680),(180,1560),(228,1560),(258,2440),(320,2470)]
def camy(t):
    for (t0,y0),(t1,y1) in zip(CAMY,CAMY[1:]):
        if t<=t1: return y0+(y1-y0)*ss((t-t0)/(t1-t0))
    return CAMY[-1][1]
TOP=F(58,800)
def frame(i):
    t=i; y=int(min(BH-H,camy(t)))
    b=board(t).crop((0,y,W,y+H))
    d=ImageDraw.Draw(b)
    if y<300:
        al=int(255*ss(prog(t,0,15)))
        d.text((W//2,170-y),"The space you need",font=TOP,fill=(255,250,240,al),anchor='mm')
    return np.array(b.convert('RGB'))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/pol_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_polaroid.mp4')
