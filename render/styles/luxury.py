# Style sample: quiet luxury. Off-white and stone, thin serif, slow push-in, lots of empty space.
from common import *
N=240
BG=(244,241,235); STONE=(220,213,200); STONE2=(196,186,170); CHAR=(43,41,38); TAUPE=(140,123,103)
rng=np.random.default_rng(5)
base=np.zeros((H,W,3),np.float32); base[:]=BG; base+=rng.normal(0,1.6,(H,W,1)); BASE=np.clip(base,0,255).astype(np.uint8)
CX,CY,S=540,930,9.0
C=rect(CX,CY,S,COURT); P=rect(CX,CY,S,PAD); A=rect(CX,CY,S,ACC)
def hl(a,p,q,frac,col,th=2):
    if frac<=0: return
    q2=(p[0]+(q[0]-p[0])*frac,p[1]+(q[1]-p[1])*frac)
    cv2.line(a,(int(p[0]*8),int(p[1]*8)),(int(q2[0]*8),int(q2[1]*8)),col,th,cv2.LINE_AA,shift=3)
def rlines(a,r,frac,col,th=2):
    x0,y0,x1,y1=r; segs=[((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]
    for k,(p,q) in enumerate(segs): hl(a,p,q,cl(frac*4-k),col,th)
def fill(a,r,col,al,hole=None):
    if al<=0: return
    ov=a.copy(); cv2.rectangle(ov,(int(r[0]),int(r[1])),(int(r[2]),int(r[3])),col,-1)
    if hole is not None: ov[int(hole[1]):int(hole[3]),int(hole[0]):int(hole[2])]=a[int(hole[1]):int(hole[3]),int(hole[0]):int(hole[2])]
    cv2.addWeighted(ov,al,a,1-al,0,a)
def dashed(a,r,frac,col):
    x0,y0,x1,y1=r; segs=[((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]
    for k,(p,q) in enumerate(segs):
        f=cl(frac*4-k); L=math.dist(p,q); n=0
        while n<L*f:
            e=min(L*f,n+8); hl(a,(p[0]+(q[0]-p[0])*n/L,p[1]+(q[1]-p[1])*n/L),(p[0]+(q[0]-p[0])*e/L,p[1]+(q[1]-p[1])*e/L),1,col,2); n+=16
SER=lambda sz,w=300: font(f'cormorant-garamond-latin-{w}-normal',sz)
def spaced(s,n=2): return (' '*0).join(c+(' '*n if c!=' ' else '  ') for c in s)
def txt(img,s,xy,f,col,al,anchor='la'):
    if al<=0: return
    ImageDraw.Draw(img,'RGBA').text(xy,s,font=f,fill=col+(int(255*al),),anchor=anchor)
def fade(t,a,b): return ss(prog(t,a,b))
ROWS=[("COURT","32'10\" × 65'7\"",60),("CONCRETE PAD","36' × 69'",112),("CLEARANCE","6' on all sides",164)]
def frame(i):
    t=i
    a=BASE.copy()
    fill(a,A,STONE,0.35*fade(t,150,190),P)
    fill(a,P,STONE2,0.9*fade(t,100,140))
    fill(a,C,BG,fade(t,100,140))          # court reads as the light plane on the stone pad
    rlines(a,C,ss(prog(t,30,80)),CHAR,2)
    lp=ss(prog(t,70,100))
    hl(a,(C[0]-6,CY),(C[2]+6,CY),lp,CHAR,2)
    for y in (CY-SV*S,CY+SV*S): hl(a,(C[0],y),(C[2],y),lp,CHAR,1)
    hl(a,(CX,CY-SV*S),(CX,CY+SV*S),lp,CHAR,1)
    dashed(a,A,ss(prog(t,150,200)),TAUPE)
    z=1.0+0.10*(t/N)                     # slow, continuous push-in
    a=zoom(a,z,0.5,(CY/H))
    img=Image.fromarray(a).convert('RGBA')
    txt(img,"N° 01      PLANNING",(W//2,190),SER(30,500),TAUPE,fade(t,0,30),'mm')
    txt(img,"The space you need",(W//2,265),SER(86,300),CHAR,fade(t,8,45),'mm')
    d=ImageDraw.Draw(img,'RGBA')
    y0=1440
    for k,(lab,val,t0) in enumerate(ROWS):
        al=fade(t,t0+40,t0+75); y=y0+k*78
        if al>0: d.line((150,y+40,930,y+40),fill=STONE2+(int(255*al),),width=1)
        txt(img,lab,(150,y+12),SER(30,500),TAUPE,al,'lm'); txt(img,val,(930,y+12),SER(40,400),CHAR,al,'rm')
    al=fade(t,200,236)
    txt(img,"48' × 81'",(W//2,1745),SER(118,300),CHAR,al,'mm')
    txt(img,"TOTAL FOOTPRINT",(W//2,1830),SER(28,500),TAUPE,al,'mm')
    return np.array(img.convert('RGB'))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/lux_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_luxury.mp4')
