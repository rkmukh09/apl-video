# Still: bird's-eye view of the court plan in a backyard, grainy illustrated style (matches illustrated.py).
from common import *
import illustrated as IL
F=IL.F; rng=np.random.default_rng(8)
S=13.0; CX,CY=540,990
def R(wl): w,l=wl; return (CX-w*S/2,CY-l*S/2,CX+w*S/2,CY+l*S/2)
A=R(ACC); P=R(PAD); C=R(COURT)
a=np.zeros((H,W,3),np.float32); a[:]=(98,146,92)
# mowing stripes (diagonal)
for k in range(-30,30):
    x=k*110; IL.fillpoly(a,[(x,0),(x+55,0),(x+55+H*0.35,H),(x+H*0.35,H)],(108,158,100),0.02,200+k%7)
a*=1+0.06*IL.lf(H,W,5,9)[...,None]
# stone path to the court
for k,y in enumerate(range(1900,1760,-70)):
    x=540+18*math.sin(k); cv2.ellipse(a,(int(x),y),(46,26),k*7,0,360,(214,204,186),-1,cv2.LINE_AA)
# flower beds and shrubs (dots like the reference cards)
for k in range(260):
    side=rng.choice([0,1]); x=rng.uniform(20,200) if side==0 else rng.uniform(880,1060); y=rng.uniform(560,1460)
    col=[(236,120,150),(250,200,120),(240,240,230)][k%3]; cv2.circle(a,(int(x),int(y)),int(rng.uniform(3,6)),col,-1,cv2.LINE_AA)
# concrete pad, clearance, court
def rectfill(r,col,al=1.0):
    ov=a.copy(); cv2.rectangle(ov,(int(r[0]),int(r[1])),(int(r[2]),int(r[3])),col,-1); a[:]=a*(1-al)+ov*al
rectfill(A,(236,226,170),0.32)
rectfill(P,(214,206,190))
# glass + steel frame shadow cast to the lower right (late afternoon sun)
sh=np.zeros((H,W),np.float32); cv2.rectangle(sh,(int(C[0])+10,int(C[1])+14),(int(C[2])+26,int(C[3])+30),1,10); sh=cv2.GaussianBlur(sh,(0,0),6)
a*=1-0.28*sh[...,None]
rectfill(C,(62,112,168)); a[int(C[1]):int(C[3]),int(C[0]):int(C[2])]*=1+0.06*IL.TONE[int(C[1]):int(C[3]),int(C[0]):int(C[2]),None]
L=(250,244,232)
cv2.rectangle(a,(int(C[0]),int(C[1])),(int(C[2]),int(C[3])),L,4,cv2.LINE_AA)
for y in (CY-SV*S,CY+SV*S): cv2.line(a,(int(C[0]),int(y)),(int(C[2]),int(y)),L,3,cv2.LINE_AA)
cv2.line(a,(CX,int(CY-SV*S)),(CX,int(CY+SV*S)),L,3,cv2.LINE_AA)
cv2.line(a,(int(C[0])-8,CY),(int(C[2])+8,CY),(40,44,52),6,cv2.LINE_AA)          # net
cv2.line(a,(int(C[0])-8,CY+10),(int(C[2])+8,CY+10),(40,60,80),5,cv2.LINE_AA)     # net shadow
cv2.rectangle(a,(int(C[0])-3,int(C[1])-3),(int(C[2])+3,int(C[3])+3),(200,225,240),3,cv2.LINE_AA)  # glass edge
# trees from above: round grainy canopies with offset shadows
for k,(x,y,r) in enumerate([(110,420,105),(980,360,120),(70,1560,110),(1010,1420,95),(150,1840,90),(960,1830,115),(1040,860,70),(40,980,75)]):
    s2=np.zeros((H,W),np.float32); cv2.circle(s2,(x+28,y+34),r,1,-1); s2=cv2.GaussianBlur(s2,(0,0),10); a*=1-0.35*s2[...,None]
    m=np.zeros((H,W),np.float32); cv2.circle(m,(x,y),r,1,-1); m=cv2.GaussianBlur(m,(0,0),4)
    m=np.clip((m-0.5+IL.lf(H,W,2,300+k)*0.25)*4+0.5,0,1)*(m>0.05)
    yy,xx=np.mgrid[0:H,0:W]; light=np.clip(1.15-0.4*np.hypot(xx-(x-r*0.35),yy-(y-r*0.35))/r,0.7,1.15)
    col=np.array([(46,96,70),(64,112,72),(40,84,66)][k%3],np.float32)
    a=a*(1-m[...,None])+(col*light[...,None])*m[...,None]
# dashed clearance line
q=[(A[0],A[1]),(A[2],A[1]),(A[2],A[3]),(A[0],A[3]),(A[0],A[1])]
for k in range(4):
    p0=np.array(q[k]); p1=np.array(q[k+1]); n=int(np.linalg.norm(p1-p0)/26)
    for j in range(0,n,2):
        s0=p0+(p1-p0)*j/n; s1=p0+(p1-p0)*(j+1)/n; cv2.line(a,(int(s0[0]),int(s0[1])),(int(s1[0]),int(s1[1])),(255,248,230),4,cv2.LINE_AA)
# shared finish: brush streaks, speckle, grain
a=a*(1+0.045*IL.STREAK[...,None]); sp=(IL.STIP<0.035)[...,None]; a=np.where(sp,a*0.86+255*0.14,a)
a=cv2.GaussianBlur(a,(0,0),0.7)+IL.GRAIN[...,None]*8
img=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
def txt(s,xy,f,anchor='mm',col=(255,255,255)):
    x,y=xy; d.text((x+3,y+4),s,font=f,fill=(40,50,30,120),anchor=anchor); d.text(xy,s,font=f,fill=col+(255,),anchor=anchor)
txt("The space you need",(W//2,170),F(76))
txt("court  32'10\" x 65'7\"",(CX,CY-200),F(38,800))
txt("concrete pad  36' x 69'",(CX,int((P[3]+A[3])/2)+6),F(30,800))
for xx in (CX-150,CX+150): d.line((xx,int(P[3])-2,xx,int((P[3]+A[3])/2)-12),fill=(255,255,255,230),width=3)
txt("+ 6' clear all around",(CX,int(A[1])-32),F(36,800))
txt("48' x 81' total",(W//2,1660),F(84))
img.convert('RGB').save('/home/claude/video/illustrated_overhead.jpg',quality=92)
