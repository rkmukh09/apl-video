# Style sample: real footage + watercolor explainer. Footage pasted on paper; freeze frames get
# hand-drawn ink circles, arrows and yellow highlights; a number cuts to a quick watercolor chart.
# Footage: public/videos/home-court.mp4 from the website repo (stock-style clip, not an APL build).
from common import *
import watercolor as WC
N=390; FOOT='/home/claude/video/foot/home-court.mp4'
INK=(40,34,30); YEL=(237,189,46)
FX,FY,FW,FH=0,640,1080,608
cap=cv2.VideoCapture(FOOT); SRC=[]
while True:
    ok,fr=cap.read()
    if not ok or len(SRC)>250: break
    SRC.append(cv2.resize(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB),(FW,FH),interpolation=cv2.INTER_AREA))
PAPER=WC.PAPER.astype(np.uint8)
TEX=(WC.PAPER/WC.PAPER.mean()).astype(np.float32)
def frozen(img):
    g=img.astype(np.float32); gray=g.mean(2,keepdims=True); g=g*0.8+gray*0.2
    g*=TEX[FY:FY+FH,FX:FX+FW]**1.5
    return np.clip(g,0,255).astype(np.uint8)
F=lambda sz,w=800: font(f'figtree-latin-{w}-normal',sz)
def ink_ellipse(a,c,rx,ry,p,seed,th=7):
    if p<=0: return
    r=np.random.default_rng(seed); n=160; turns=1.12; a0=r.uniform(0,6.28)
    pts=[]
    for k in range(int(n*p)+1):
        t=k/n*turns*2*math.pi+a0; w=1+0.04*math.sin(t*3+seed)+0.02*math.sin(t*7)
        grow=1+0.06*(k/n)
        pts.append((c[0]+rx*w*grow*math.cos(t), c[1]+ry*w*grow*math.sin(t)))
    cv2.polylines(a,[np.int32(np.array(pts)*4)],False,INK,th,cv2.LINE_AA,shift=2)
def ink_arrow(a,p,q,f,seed):
    if f<=0: return
    WC.wobble_line(a,p,q,f,6,2.5,seed)
    if f>0.97:
        ang=math.atan2(q[1]-p[1],q[0]-p[0])
        for s in (-0.5,0.5): WC.wobble_line(a,q,(q[0]-34*math.cos(ang+s),q[1]-34*math.sin(ang+s)),1,6,0.4,seed+3)
_hl={}
def highlight(a,box,p,seed):
    # yellow watercolor marker swash, wiped on left to right, multiplied
    if p<=0: return
    x0,y0,x1,y1=box
    if seed not in _hl:
        m=np.zeros((H,W),np.float32); cv2.rectangle(m,(x0,y0),(x1,y1),1,-1); m=cv2.GaussianBlur(m,(0,0),4)
        m=np.clip((m-0.5+WC.lowfreq(2,0.25))*4+0.5,0,1)*(m>0.1)
        _hl[seed]=m
    m=_hl[seed].copy(); xc=int(x0+(x1-x0)*p); m[:,xc:]=0
    m=m[...,None]*0.75
    a[:]=(a*(1-m)+a*(np.array(YEL)/255)*m).astype(np.uint8)
def text(img,s,xy,f,col=INK,al=1,anchor='la'):
    if al>0: ImageDraw.Draw(img,'RGBA').text(xy,s,font=f,fill=col+(int(255*al),),anchor=anchor)
def paste_footage(a,fr):
    sh=np.zeros((H,W),np.float32); sh[FY+10:FY+FH+22,FX:FX+FW]=1; sh=cv2.GaussianBlur(sh,(0,0),14)[...,None]*0.35
    a[:]=(a*(1-sh)).astype(np.uint8); a[FY:FY+FH,FX:FX+FW]=fr
def frame(i):
    t=i
    if 150<=t<245:                                   # quick chart cut
        k=int(215*eout(prog(t,150,236))); return WC.frame(k)
    a=PAPER.copy()
    if t<60: paste_footage(a,SRC[30+t])
    elif t<150: paste_footage(a,frozen(SRC[90]))
    elif t<305: paste_footage(a,SRC[180+(t-245)])
    else: paste_footage(a,frozen(SRC[240]))
    capt=None
    if 60<=t<150:
        if t<64: a[FY:FY+FH]=np.clip(a[FY:FY+FH].astype(np.int16)+60*(1-(t-60)/4),0,255).astype(np.uint8)   # freeze flash
        ink_ellipse(a,(560,FY+470),470,95,ss(prog(t,66,90)),1)
        ink_arrow(a,(560,1345),(560,FY+FH-25),ss(prog(t,88,100)),5)
        highlight(a,(70,1360,1010,1450),ss(prog(t,104,122)),11)
    if t>=305:
        if t<309: a[FY:FY+FH]=np.clip(a[FY:FY+FH].astype(np.int16)+60*(1-(t-305)/4),0,255).astype(np.uint8)
        ink_ellipse(a,(510,FY+95),60,42,ss(prog(t,310,325)),2,6)
        ink_arrow(a,(730,FY-110),(565,FY+70),ss(prog(t,322,334)),7)
        ink_ellipse(a,(990,FY+330),62,250,ss(prog(t,330,350)),3,6)
        highlight(a,(70,1525,800,1597),ss(prog(t,350,366)),12)
    img=Image.fromarray(a).convert('RGBA')
    # top title, always on paper
    text(img,"How much space does",(70,170),F(64)); text(img,"a padel court need?",(70,250),F(64))
    if t<60: text(img,"Real courts, real numbers",(70,1350),F(40,600),(110,100,92),ss(prog(t,10,30)))
    if 60<=t<150:
        al=ss(prog(t,96,110))
        text(img,"32'10\" x 65'7\" of turf",(90,1405),F(60,800),INK,ss(prog(t,100,116)),'lm')
    if 245<=t<305:
        al=ss(prog(t,250,265))
        text(img,"Plan for 48' x 81' in total",(90,1405),F(56,800),INK,al,'lm')
        text(img,"Court, concrete pad, and 6' clear all around",(90,1475),F(36,600),(110,100,92),al,'lm')
    if t>=305:
        text(img,"lights",(740,FY-150),F(46,800),INK,ss(prog(t,326,338)))
        text(img,"glass walls",(700,FY+FH+40),F(46,800),INK,ss(prog(t,346,356)))
        text(img,"Want lights? Plan access",(90,1485),F(54,800),INK,ss(prog(t,342,356)),'lm')
        text(img,"to your utility box early",(90,1560),F(54,800),INK,ss(prog(t,346,360)),'lm')
    return np.array(img.convert('RGB'))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/hy_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_hybrid.mp4')
