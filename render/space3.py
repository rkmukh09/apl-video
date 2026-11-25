# Still frame: three nested rectangles for "The space you need" (court, concrete pad, access zone). Feet, to scale.
import sys; sys.path.insert(0,'.')
from apl import *
a=BG.copy()
s=14.5                      # px per foot
cx,cy=540,905
def R(w,l): return (cx-w*s/2,cy-l*s/2,cx+w*s/2,cy+l*s/2)
court=R(32+10/12,65+7/12); pad=R(36,69); acc=R(48,81)   # 6' clear around the 36' x 69' pad
CONC=(150,158,172); ACC=(120,200,170)
rectfill(a,*acc,ACC,0.16); dashed_rect(a,*acc,ACC,5)
rectfill(a,*pad,CONC,0.85); poly(a,[(pad[0],pad[1]),(pad[2],pad[1]),(pad[2],pad[3]),(pad[0],pad[3])],(225,230,238),4)
rectfill(a,*court,COURT,1.0); court_top_l=court
x0,y0,x1,y1=court
poly(a,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],WHITE,5)
line(a,(x0-10,cy),(x1+10,cy),WHITE,5)
sv=(22+10/12)*s
for y in (cy-sv,cy+sv): line(a,(x0,y),(x1,y),WHITE,3)
line(a,(cx,cy-sv),(cx,cy+sv),WHITE,3)
img=Image.fromarray(a).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
brand_tag(img); text(img,"THE SPACE YOU NEED",(W//2,215),fit('b',104,"THE SPACE YOU NEED"),anchor='mm')
# 6' callouts in the access band (outside the court)
f6=F('b',40)
text(img,"6'",(cx,(acc[1]+pad[1])/2),f6,fill=ACC,anchor='mm')
text(img,"6'",(cx,(acc[3]+pad[3])/2),f6,fill=ACC,anchor='mm')
vtext(img,"6'",((acc[0]+pad[0])/2-4,cy-200),f6,fill=ACC); vtext(img,"6'",((acc[2]+pad[2])/2+4,cy-200),f6,fill=ACC)
# number badges
def badge(n,x,y,col,fg):
    d.ellipse((x-30,y-30,x+30,y+30),fill=col+(255,)); text(img,str(n),(x,y+2),F('b',40),fill=fg,anchor='mm')
badge(1,cx+120,cy-120,WHITE,DEEP); badge(2,pad[2]-14,pad[1]+14,(225,230,238),DEEP); badge(3,acc[2]-6,acc[1]+6,ACC,DEEP)
# legend
rows=[(1,WHITE,"COURT (PLAY AREA)","32'10\" x 65'7\""),(2,(225,230,238),"CONCRETE PAD + RING BEAM","36' x 69'"),(3,ACC,"ACCESS ZONE","48' x 81' total, 6' clear around the pad")]
for i,(n,c,h,sub) in enumerate(rows):
    y=1555+i*112
    badge(n,140,y,c,DEEP)
    text(img,h,(200,y-20),F('b',46),anchor='lm'); text(img,sub,(200,y+26),F('i',36,600),fill=SLATE,anchor='lm')
img.convert('RGB').save(sys.argv[1] if len(sys.argv)>1 else 'space3.jpg',quality=92)
