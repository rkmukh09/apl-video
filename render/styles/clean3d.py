# Style sample: clean 3D render. Minimal court rotates while parts get labeled. Figtree.
# Facts from the live site: back walls 9'10" = 6'7" glass + 3'3" mesh; side walls step down to 6'7";
# turf 2,153 sq ft; silica sand infill holds the fibers upright for a true bounce.
from common import *
N=300; SS=2                                     # supersample
BG0=(246,247,249); BG1=(228,231,236)
NAVY=(44,74,114); TURF=(52,98,160); PAD=(205,207,210); STEEL=(58,62,70); GLASS=(170,205,235); INK=(30,34,42); GREY=(120,128,140)
F=lambda sz,w=700: font(f'figtree-latin-{w}-normal',sz)
def bg():
    y=np.linspace(0,1,H)[:,None,None]; a=np.array(BG0,np.float32)*(1-y)+np.array(BG1,np.float32)*y
    return np.repeat(np.repeat(a,1,0),W,1).astype(np.uint8)
BGI=bg()
# ---- geometry (meters; x across 10, y along 20, z up) ----
def quad(x0,y0,x1,y1,z0,z1,axis):
    if axis=='x': return [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)]   # wall in the y-z plane at x=x0
    return [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)]                  # wall in the x-z plane at y=y0
items=[]   # (kind, data, style, group)
def poly(pts,fill,outline=None,w=0,group='',fixed=None): items.append(('poly',pts,(fill,outline,w),group,fixed))
def seg(p,q,col,w,group=''): items.append(('line',(p,q),(col,w),group,None))
poly([(-5.5,-10.5,0),(5.5,-10.5,0),(5.5,10.5,0),(-5.5,10.5,0)],PAD+(255,),group='pad',fixed=0)
poly([(-5,-10,0.02),(5,-10,0.02),(5,10,0.02),(-5,10,0.02)],TURF+(255,),group='turf',fixed=1)
LW=(255,255,255,235)
for y in (-6.95,6.95): items.append(('line',((-5,y,0.03),(5,y,0.03)),(LW,3),'lines',2))
items.append(('line',((0,-6.95,0.03),(0,6.95,0.03)),(LW,3),'lines',2))
for x in (-5,5): items.append(('line',((x,-10,0.03),(x,10,0.03)),(LW,3),'lines',2))
for y in (-10,10): items.append(('line',((-5,y,0.03),(5,y,0.03)),(LW,3),'lines',2))
GL=GLASS+(70,); GO=(120,160,200,200); MESH=(60,66,76,150)
def mesh_panel(pts,group):
    (a,b,c,d)=pts; poly(pts,(80,86,96,25),None,0,group)
    for k in range(1,12):
        t=k/12; p=tuple(a[i]+(b[i]-a[i])*t for i in range(3)); q=tuple(d[i]+(c[i]-d[i])*t for i in range(3)); seg(p,q,MESH,1,group)
    for k in range(1,6):
        t=k/6; p=tuple(a[i]+(d[i]-a[i])*t for i in range(3)); q=tuple(b[i]+(c[i]-b[i])*t for i in range(3)); seg(p,q,MESH,1,group)
for s in (-1,1):
    yb=10*s
    # back wall: 2 m glass + 1 m mesh
    for k in range(5):
        x0=-5+2*k; poly(quad(x0,yb,x0+2,yb,0,2,'y'),GL,GO,2,'glass')
    mesh_panel(quad(-5,yb,5,yb,2,3,'y'),'mesh')
    for x in (-5,5):
        # side walls: 3 m at the back corner, stepping to 2 m toward the net
        poly(quad(x,8*s,x,10*s,0,2,'x'),GL,GO,2,'glass'); mesh_panel(quad(x,8*s,x,10*s,2,3,'x'),'mesh')
        poly(quad(x,6*s,x,8*s,0,2,'x'),GL,GO,2,'glass')
        mesh_panel(quad(x,1*s,x,6*s,0,2,'x'),'mesh')
# steel posts
for s in (-1,1):
    for x in (-5,-3,-1,1,3,5): seg((x,10*s,0),(x,10*s,3),STEEL+(255,),4,'steel')
    for x in (-5,5):
        for y,h in ((8,3),(6,2),(4,2),(2,2),(1,2)): seg((x,y*s,0),(x,y*s,h),STEEL+(255,),4,'steel')
# net
seg((-5,0,0.92),(5,0,0.88),INK+(255,),3,'net'); poly(quad(-5,0,5,0,0.05,0.88,'y'),(40,44,52,60),None,0,'net')
# light poles (4) with heads
LIGHTS=[]
for sx in (-1,1):
    for sy in (-1,1):
        p=(5.6*sx,5.5*sy,0); top=(5.6*sx,5.5*sy,6.0); seg(p,top,STEEL+(255,),5,'lights')
        head=[(5.6*sx-0.0,5.5*sy-0.5,6.0),(5.6*sx-0.0,5.5*sy+0.5,6.0),(5.6*sx-0.6*sx,5.5*sy+0.5,5.85),(5.6*sx-0.6*sx,5.5*sy-0.5,5.85)]
        poly(head,(250,250,245,255),STEEL+(255,),2,'lights'); LIGHTS.append(top)
# ---- camera ----
def cam(az,el,D=34.0,target=(0,0,1.4)):
    t=np.array(target); c=t+D*np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)])
    f=(t-c)/np.linalg.norm(t-c); r=np.cross(f,[0,0,1]); r/=np.linalg.norm(r); u=np.cross(r,f)
    return c,f,r,u
FOC=1850*SS; CX,CY=W*SS/2,1010*SS
def proj(p,C):
    c,f,r,u=C; v=np.array(p)-c; z=v@f
    return (CX+FOC*(v@r)/z, CY-FOC*(v@u)/z, z)
def render3d(C,show):
    im=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
    # soft ground shadow
    sh=Image.new('L',(W*SS,H*SS),0); sd=ImageDraw.Draw(sh)
    pts=[proj(p,C)[:2] for p in [(-7,-12.5,0),(7,-12.5,0),(7,12.5,0),(-7,12.5,0)]]; sd.polygon(pts,fill=90)
    sh=sh.filter(ImageFilter.GaussianBlur(40*SS)); im.paste((20,30,45,255),(0,0),sh.point(lambda v:int(v*0.5)))
    fixed=[it for it in items if it[4] is not None]; free=[it for it in items if it[4] is None]
    def draw(it):
        kind,data,st,g,_=it
        if show.get(g,1)<=0: return
        a=show.get(g,1)
        if kind=='poly':
            P=[proj(p,C)[:2] for p in data]; fill,ol,w=st
            fill=fill[:3]+(int(fill[3]*a),)
            d.polygon(P,fill=fill)
            if ol: d.line(P+[P[0]],fill=ol[:3]+(int(ol[3]*a),),width=w*SS)
        else:
            p,q=data; col,w=st; P=proj(p,C); Q=proj(q,C)
            d.line([P[:2],Q[:2]],fill=col[:3]+(int(col[3]*a),),width=w*SS)
    for it in sorted(fixed,key=lambda it:it[4]): draw(it)
    def depth(it):
        pts=it[1]; return -np.mean([proj(p,C)[2] for p in pts])
    for it in sorted(free,key=depth): draw(it)
    return im.resize((W,H),Image.LANCZOS)
LABELS=[  # (group, anchor3d, title, sub, t_in, side)
    ('turf',(2.5,-6.0,0.05),"TURF","2,153 sq ft playing surface",45,'r'),
    ('sand',None,"SILICA SAND INFILL","Holds the fibers upright for a true bounce",95,'l'),
    ('glass',(-1,-10,1.0),"TEMPERED GLASS","6'7\" tall on the back walls",150,'l'),
    ('mesh',(1,-10,2.5),"METAL MESH","3'3\" above the glass",200,'r'),
    ('lights',None,"LIGHTS","For evening play",245,'l'),
]
def inset(img,cx,cy,r,al):
    # cutaway: sand fills almost to the top of the fibers; only the tips show
    if al<=0: return
    D=2*r; s_=Image.new('RGBA',(D,D),BG0+(255,)); d=ImageDraw.Draw(s_)
    rr=np.random.default_rng(1); sand_top=int(D*0.34)
    d.rectangle((0,sand_top,D,D),fill=(214,192,152,255))
    for _ in range(2400):
        x=rr.uniform(0,D); y=rr.uniform(sand_top,D); c=tuple(int(v) for v in rr.uniform([188,165,122],[236,216,178]))
        d.ellipse((x-2.2,y-2.2,x+2.2,y+2.2),fill=c+(255,))
    for k in range(34):
        x=14+k*(D-28)/33+rr.uniform(-3,3); top=sand_top-rr.uniform(16,30); lean=rr.uniform(-8,8)
        d.line((x,D,x+lean*0.6,sand_top+10),fill=TURF+(140,),width=3)       # fiber inside the sand
        d.line((x+lean*0.6,sand_top+10,x+lean,top),fill=TURF+(255,),width=4) # tip above the sand
    m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse((0,0,D,D),fill=int(255*al)); s_.putalpha(m)
    img.alpha_composite(s_,(int(cx-r),int(cy-r)))
    ImageDraw.Draw(img,'RGBA').ellipse((cx-r,cy-r,cx+r,cy+r),outline=(255,255,255,int(255*al)),width=6)
def callout(img,anchor,ly,title,sub,side,al):
    d=ImageDraw.Draw(img,'RGBA'); A=int(255*al)
    ax,ay=anchor
    tw=max(F(40,800).getbbox(title)[2],F(30,500).getbbox(sub)[2])
    x0=70 if side=='l' else W-70-tw; x1=x0+tw
    inner=x1 if side=='l' else x0
    d.line([(x0,ly),(x1,ly)],fill=INK+(A,),width=3)
    d.line([(inner,ly),(ax,ay)],fill=INK+(A,),width=3)
    d.ellipse((ax-9,ay-9,ax+9,ay+9),fill=(255,255,255,A),outline=INK+(A,),width=3)
    if ay>ly:   # leader goes down: text sits above the rule
        d.text((x0,ly-58),title,font=F(40,800),fill=INK+(A,),anchor='ls'); d.text((x0,ly-14),sub,font=F(30,500),fill=GREY+(A,),anchor='ls')
    else:       # leader goes up: text sits below the rule
        d.text((x0,ly+48),title,font=F(40,800),fill=INK+(A,),anchor='ls'); d.text((x0,ly+92),sub,font=F(30,500),fill=GREY+(A,),anchor='ls')
def frame(i):
    t=i
    az=math.radians(-120+70*ss(t/N)); el=math.radians(26+6*math.sin(t/N*math.pi))
    C=cam(az,el)
    show={'glass':0.25+0.75*ss(prog(t,140,170)),'mesh':0.25+0.75*ss(prog(t,190,215)),'lights':0.15+0.85*ss(prog(t,235,260))}
    img=Image.fromarray(BGI).convert('RGBA')
    img.alpha_composite(render3d(C,show))
    d=ImageDraw.Draw(img,'RGBA')
    p=eout(prog(t,0,25)); d.text((W//2,150+(1-p)*20),"What a padel court",font=F(72,800),fill=INK+(int(255*p),),anchor='mm')
    d.text((W//2,235+(1-p)*20),"is made of",font=F(72,800),fill=INK+(int(255*p),),anchor='mm')
    ys={'turf':1560,'sand':1640,'glass':520,'mesh':420,'lights':360}
    for g,anc,title,sub,t0,side in LABELS:
        al=eout(prog(t,t0,t0+18))*(1-ss(prog(t,t0+48 if g!='sand' else t0+60,t0+62 if g!='sand' else t0+75)))
        if al<=0: continue
        if g=='sand':
            inset(img,830,1560,150,al); callout(img,(690,1560),ys[g],title,sub,'l',al); continue
        if g=='lights':
            pts=[proj(p,C) for p in LIGHTS]; P=min(pts,key=lambda q:q[1]); ax,ay=P[0]/SS,P[1]/SS
        else:
            P=proj(anc,C); ax,ay=P[0]/SS,P[1]/SS
        callout(img,(ax,ay),ys[g],title,sub,side,al)
    # end card: all labels listed small at the bottom
    e=eout(prog(t,262,285))
    if e>0:
        items_=["Turf","Sand infill","Glass","Mesh","Lights"]
        d.text((W//2,1700),"  ·  ".join(items_),font=F(38,700),fill=INK+(int(255*e),),anchor='mm')
    return np.array(img.convert('RGB'))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='still':
        for f in map(int,sys.argv[2:]): Image.fromarray(frame(f)).save(f'/home/claude/video/c3d_{f}.jpg',quality=90)
    else: encode(frame,N,'/home/claude/video/style_clean3d.mp4')
