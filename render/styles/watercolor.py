# Style sample: watercolor field journal. Washes bleed in on paper, hand-inked labels.
from common import *
N=216
rng=np.random.default_rng(7)
SEPIA=(59,47,42)
def lowfreq(sig,scale=1.0):
    n=rng.normal(0,1,(H//4,W//4)).astype(np.float32); n=cv2.GaussianBlur(n,(0,0),sig)
    n=(n-n.mean())/(n.std()+1e-6); return cv2.resize(n,(W,H))*scale
def paper():
    a=np.zeros((H,W,3),np.float32); a[:]=(244,238,225)
    a+=lowfreq(30,6)[...,None]+rng.normal(0,3,(H,W,1))
    fib=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),1.2); a+=fib[...,None]*6
    y,x=np.mgrid[0:H,0:W]; v=((x-W/2)/W)**2+((y-H/2)/H)**2; a*= (1-0.25*v)[...,None]
    return np.clip(a,0,255)
PAPER=paper()
CX,CY,S=540,1000,12.0
C=rect(CX,CY,S,COURT); P=rect(CX,CY,S,PAD); A=rect(CX,CY,S,ACC)
def boxmask(r,hole=None):
    m=np.zeros((H,W),np.float32); cv2.rectangle(m,(int(r[0]),int(r[1])),(int(r[2]),int(r[3])),1,-1)
    if hole: cv2.rectangle(m,(int(hole[0]),int(hole[1])),(int(hole[2]),int(hole[3])),0,-1)
    return m
class Wash:
    def __init__(s,r,hole,col,dens,origin):
        m=cv2.GaussianBlur(boxmask(r,hole),(0,0),5)
        s.m=np.clip((m-0.5+lowfreq(2.5,0.22))*5+0.5,0,1)*(m>0.15); s.col=np.array(col,np.float32)/255; s.dens=dens
        y,x=np.mgrid[0:H,0:W]; d=np.hypot(x-origin[0],y-origin[1]).astype(np.float32); s.d=d/d[s.m>0.5].max()
        s.n=lowfreq(10,0.18); s.v=lowfreq(5,1.0); s.g=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),0.8)
    def alpha(s,p):
        if p<=0: return None
        a=np.clip((p*1.7-s.d+s.n)*5,0,1)*s.m
        a=cv2.GaussianBlur(a,(0,0),2.5)
        edge=np.clip(a-cv2.GaussianBlur(a,(0,0),7),0,1)*2.2      # pigment pools at the edge
        return np.clip((a*(0.5+0.14*s.v+0.08*s.g)+edge*1.3)*s.dens,0,1)
    def apply(s,img,p):
        a=s.alpha(p)
        if a is None: return
        img*= 1-a[...,None]*(1-s.col)
W_COURT=Wash(C,None,(70,125,185),0.75,(CX,CY))
W_PAD=Wash(P,C,(200,180,140),0.85,(CX,P[3]))
W_ACC=Wash(A,P,(150,185,150),0.6,(A[0],A[1]))
def wobble_line(a,p,q,frac,th=3,amp=1.4,seed=0):
    if frac<=0: return
    n=max(2,int(math.dist(p,q)/6)); r=np.random.default_rng(seed)
    ph=r.uniform(0,6); pts=[]
    for k in range(int(n*frac)+1):
        t=k/n; x=p[0]+(q[0]-p[0])*t; y=p[1]+(q[1]-p[1])*t
        nx,ny=-(q[1]-p[1]),(q[0]-p[0]); L=math.hypot(nx,ny) or 1
        o=amp*math.sin(t*9+ph)+r.normal(0,0.3); pts.append((x+nx/L*o,y+ny/L*o))
    pts=np.int32(np.array(pts)*4)
    cv2.polylines(a,[pts],False,SEPIA,th,cv2.LINE_AA,shift=2)
def rect_lines(a,r,frac,th,seed,dash=False):
    x0,y0,x1,y1=r; segs=[((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]
    for k,(p,q) in enumerate(segs):
        f=cl(frac*4-k)
        if not dash: wobble_line(a,p,q,f,th,seed=seed+k)
        else:
            L=math.dist(p,q); n=0
            while n<L*f:
                e=min(L*f,n+16); a0=(p[0]+(q[0]-p[0])*n/L,p[1]+(q[1]-p[1])*n/L); a1=(p[0]+(q[0]-p[0])*e/L,p[1]+(q[1]-p[1])*e/L)
                wobble_line(a,a0,a1,1,th,0.6,seed+int(n)); n+=28
def write_on(img,text,xy,fnt,col,p,spacing=6,anchor='la'):
    if p<=0: return
    lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.multiline_text(xy,text,font=fnt,fill=col+(255,),spacing=spacing,anchor=anchor)
    bb=lay.getbbox()
    if not bb: return
    x=bb[0]+(bb[2]-bb[0]+40)*p
    m=np.zeros((H,W),np.float32); m[:, :int(max(0,x))]=1; m=cv2.GaussianBlur(m,(0,0),10)
    al=np.array(lay.getchannel('A')).astype(np.float32)*m
    lay.putalpha(Image.fromarray(al.astype(np.uint8))); img.alpha_composite(lay)
def arrow(a,p,q,frac,seed):
    wobble_line(a,p,q,frac,2,2.5,seed)
    if frac>0.98:
        ang=math.atan2(q[1]-p[1],q[0]-p[0])
        for s in (-0.5,0.5): wobble_line(a,q,(q[0]-18*math.cos(ang+s),q[1]-18*math.sin(ang+s)),1,2,0.3,seed+9)
HF=lambda sz,w=500: font(f'figtree-latin-{w}-normal',sz)
def frame(i):
    t=i
    img=PAPER.copy()/255
    W_ACC.apply(img,ss(prog(t,118,165)))
    W_PAD.apply(img,ss(prog(t,72,118)))
    W_COURT.apply(img,ss(prog(t,22,72)))
    a=np.clip(img*255,0,255).astype(np.uint8)
    rect_lines(a,C,ss(prog(t,40,82)),3,10)
    lp=ss(prog(t,70,92))
    wobble_line(a,(C[0]-8,CY),(C[2]+8,CY),lp,4,1,20)
    for k,y in enumerate((CY-SV*S,CY+SV*S)): wobble_line(a,(C[0],y),(C[2],y),lp,2,1,30+k)
    wobble_line(a,(CX,CY-SV*S),(CX,CY+SV*S),lp,2,1,40)
    rect_lines(a,P,ss(prog(t,100,122)),2,50)
    rect_lines(a,A,ss(prog(t,150,175)),2,60,dash=True)
    arrow(a,(200,800),(P[0]-4,830),ss(prog(t,118,128)),70)
    arrow(a,(960,500),((A[2]+P[2])/2,570),ss(prog(t,170,180)),80)
    pil=Image.fromarray(a).convert('RGBA')
    write_on(pil,"The space you need",(70,120),HF(80,700),SEPIA,prog(t,0,22))
    write_on(pil,"field notes · no. 01",(74,225),HF(36),(120,108,98),prog(t,10,28))
    write_on(pil,"court  32'10\" x 65'7\"",(CX,C[1]+38),HF(34,700),(255,255,255),prog(t,82,98),anchor='ma')
    write_on(pil,"concrete pad\n+ ring beam\n36' x 69'",(28,620),HF(32,700),SEPIA,prog(t,124,142))
    write_on(pil,"6' clear\nall around",(850,390),HF(34,700),SEPIA,prog(t,176,190))
    write_on(pil,"total: 48' x 81'",(CX,1555),HF(92,700),SEPIA,prog(t,186,204),anchor='ma')
    write_on(pil,"room for machinery + getting in and out",(CX,1700),HF(36),(120,108,98),prog(t,196,212),anchor='ma')
    out=np.array(pil.convert('RGB'))
    return zoom(out,1.0+0.035*ss(t/N),0.5,0.5)
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/wc_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_watercolor.mp4')
