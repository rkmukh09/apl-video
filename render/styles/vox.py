# Style sample: Vox-style paper collage. Board, ink, one yellow. Animated on twos.
from common import *
import random
BOARD=(0xEF,0xEB,0xE3); INK=(0x1D,0x1C,0x20); YEL=(0xED,0xBD,0x2E); BEI=(0xF1,0xED,0xE4)
N=216
rng=np.random.default_rng(3)
def board():
    a=np.zeros((H,W,3),np.float32); a[:]=BOARD
    hatch=np.zeros((H,W),np.uint8)
    for k in range(-H,W,22): cv2.line(hatch,(k,0),(k+H,H),255,2,cv2.LINE_AA)
    a-= (hatch[...,None]/255.0)*0.10*(np.array(BOARD)-np.array(INK))
    g=rng.normal(0,5,(H,W,1)); a+=g
    return np.clip(a,0,255).astype(np.uint8)
BOARD_IMG=board()
CX,CY,S=540,1010,12.5
C=rect(CX,CY,S,COURT); P=rect(CX,CY,S,PAD); A=rect(CX,CY,S,ACC)
def jit(seed,amt=1.5):
    r=random.Random(str(seed)); return r.uniform(-amt,amt),r.uniform(-amt,amt)
def ink_poly(a,pts,frac,th,seed,closed=False):
    if frac<=0: return
    pts=list(pts)+([pts[0]] if closed else [])
    pts=[(x+jit((seed,k))[0],y+jit((seed,k))[1]) for k,(x,y) in enumerate(pts)]
    L=[math.dist(pts[k],pts[k+1]) for k in range(len(pts)-1)]; rem=sum(L)*frac
    for k,l in enumerate(L):
        if rem<=0: break
        f=min(1,rem/l); p=pts[k]; q=(p[0]+(pts[k+1][0]-p[0])*f,p[1]+(pts[k+1][1]-p[1])*f)
        cv2.line(a,(int(p[0]*4),int(p[1]*4)),(int(q[0]*4),int(q[1]*4)),INK,th,cv2.LINE_AA,shift=2); rem-=l
def marker_dash(a,r,frac,seed):
    x0,y0,x1,y1=r; pts=[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)]
    L=[math.dist(pts[k],pts[k+1]) for k in range(4)]; tot=sum(L)*frac; d=0
    rr=random.Random(str(seed))
    for k in range(4):
        p,q=pts[k],pts[k+1]; n=0
        while n<L[k] and d<tot:
            e=min(L[k],n+22); 
            a0=(p[0]+(q[0]-p[0])*n/L[k],p[1]+(q[1]-p[1])*n/L[k]); a1=(p[0]+(q[0]-p[0])*e/L[k],p[1]+(q[1]-p[1])*e/L[k])
            w=int(6*(1+rr.uniform(-.15,.15)))
            cv2.line(a,(int(a0[0]+rr.uniform(-1,1)),int(a0[1]+rr.uniform(-1,1))),(int(a1[0]),int(a1[1])),INK,w,cv2.LINE_AA)
            n+=40; d+=40
def shadowed(img,spr,xy,rot,scale,seed):
    # boil
    dx,dy=jit(seed,1.5); r=random.Random(str(seed)+"r").uniform(-.4,.4)
    spr=spr.resize((max(1,int(spr.width*scale)),max(1,int(spr.height*scale))),Image.BICUBIC).rotate(rot+r,expand=True,resample=Image.BICUBIC)
    x=int(xy[0]-spr.width/2+dx); y=int(xy[1]-spr.height/2+dy)
    sh=Image.new('RGBA',spr.size,(0,0,0,0)); sh.putalpha(spr.getchannel('A').point(lambda v:int(v*.32)))
    sh=sh.filter(ImageFilter.GaussianBlur(6)); img.alpha_composite(sh,(x+5,y+7)); img.alpha_composite(spr,(x,y))
def slap(i,i0):
    if i<i0: return 0
    k=(i-i0)//2; return [1.1,0.98,1.0][min(k,2)]
def tag(text,size=26):
    f=font('special-elite-latin-400-normal',size); s=' '.join(text)  # letter-spaced
    tw=f.getbbox(s)[2]; im=Image.new('RGBA',(tw+40,size+30),YEL+(255,)); d=ImageDraw.Draw(im)
    d.text((20,12),s,font=f,fill=INK); return paper_edge(im)
def paper_edge(im,edge=7):
    w,h=im.size; out=Image.new('RGBA',(w+2*edge,h+2*edge),(255,255,255,255)); out.paste(im,(edge,edge))
    return out
TITLE="The space\nyou need"
def title_card(n):
    im=Image.new('RGBA',(560,250),BEI+(255,)); d=ImageDraw.Draw(im)
    d.multiline_text((36,40),TITLE[:n],font=font('libre-caslon-text-latin-400-normal',68),fill=INK,spacing=6)
    return paper_edge(im)
RANSOM="48' x 81'"
RF=['libre-caslon-text-latin-700-normal','anton-latin-400-normal','special-elite-latin-400-normal']
RB=[(INK,BEI),(BEI,INK),(YEL,INK)]
def ransom(ch,k):
    if ch==' ': return None
    bg,fg=RB[k%3]; f=font(RF[k%3],92); bb=f.getbbox(ch)
    im=Image.new('RGBA',(max(70,bb[2]+30),130),bg+(255,)); ImageDraw.Draw(im).text(((max(70,bb[2]+30)-bb[2])/2,8),ch,font=f,fill=fg)
    return paper_edge(im,5)
NOTE="room for machinery\n+ getting in and out"
def frame(i):
    i2=i-i%2; seed=i//8
    a=BOARD_IMG.copy()
    # access zone cross-hatch (featured region) once access appears
    ap=prog(i2,96,120)
    if ap>0:
        m=np.zeros((H,W),np.uint8)
        for k in range(-H,W,13): cv2.line(m,(k,0),(k+H,H),255,2,cv2.LINE_AA); cv2.line(m,(k,H),(k+H,0),255,2,cv2.LINE_AA)
        box=np.zeros((H,W),np.uint8); cv2.rectangle(box,(int(A[0]),int(A[1])),(int(A[2]),int(A[3])),255,-1)
        cv2.rectangle(box,(int(P[0]),int(P[1])),(int(P[2]),int(P[3])),0,-1)
        mm=(m.astype(np.float32)/255)*(box/255)*0.18*ap
        a=(a*(1-mm[...,None])+np.array(INK)*mm[...,None]).astype(np.uint8)
    # yellow pad, multiplied 90%, sweep south->north over 16 frames
    yp=prog(i2,62,78)
    if yp>0:
        top=P[3]-(P[3]-P[1])*yp
        sub=a[int(top):int(P[3]),int(P[0]):int(P[2])].astype(np.float32)
        mul=sub*np.array(YEL,np.float32)/255
        a[int(top):int(P[3]),int(P[0]):int(P[2])]=(sub*0.1+mul*0.9).astype(np.uint8)
    # court interior back to paper so the pad reads as the band around it
    if yp>0:
        cy0=max(int(C[1]),int(P[3]-(P[3]-P[1])*yp))
        if cy0<int(C[3]): a[cy0:int(C[3]),int(C[0]):int(C[2])]=BOARD_IMG[cy0:int(C[3]),int(C[0]):int(C[2])]
    # court in ink
    cp=prog(i2,20,48)
    ink_poly(a,[(C[0],C[1]),(C[2],C[1]),(C[2],C[3]),(C[0],C[3])],ss(cp),6,(1,seed),closed=True)
    lp=prog(i2,40,56)
    ink_poly(a,[(C[0]-10,CY),(C[2]+10,CY)],ss(lp),5,(2,seed))
    for k,y in enumerate((CY-SV*S,CY+SV*S)): ink_poly(a,[(C[0],y),(C[2],y)],ss(lp),3,(3+k,seed))
    ink_poly(a,[(CX,CY-SV*S),(CX,CY+SV*S)],ss(lp),3,(5,seed))
    marker_dash(a,A,ss(prog(i2,96,122)),(6,seed))
    img=Image.fromarray(a).convert('RGBA')
    # title card + FIG tag
    n=max(0,(i2-6)); 
    if i2>=4: shadowed(img,title_card(min(len(TITLE),n)),(330,250),-1.2,slap(i,4),(10,seed))
    if i2>=8: shadowed(img,tag('FIG. 01',22),(150,128),3,slap(i,8),(11,seed))
    # tags
    if i2>=50: shadowed(img,tag("COURT  32'10\" X 65'7\""),(CX,CY-260),-2,slap(i,50),(12,seed))
    if i2>=80: shadowed(img,tag("CONCRETE PAD  36' X 69'"),(CX,P[3]-40),1.5,slap(i,80),(13,seed))
    if i2>=122: shadowed(img,tag("+6' CLEAR, ALL SIDES"),(CX+100,A[1]-4),-1,slap(i,122),(14,seed))
    # marker note
    k=int(max(0,i2-134)*1.3)
    if k>0:
        d=ImageDraw.Draw(img); d.multiline_text((70,1560),NOTE[:k],font=font('permanent-marker-latin-400-normal',60),fill=INK+(255,),spacing=4)
    # ransom total
    x=170
    for j,ch in enumerate(RANSOM):
        t0=166+j*3
        sp=ransom(ch,j)
        if sp is None: x+=40; continue
        if i2>=t0: shadowed(img,sp,(x+sp.width/2,1800),random.Random(j).uniform(-6,6),slap(i,t0),(20+j,seed))
        x+=sp.width-2
    out=np.array(img.convert('RGB'))
    z=1.14-0.14*ss(prog(i2,24,60))
    return zoom(out,z,0.3,0.15)
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/vox_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_vox.mp4')
