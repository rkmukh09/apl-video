import numpy as np, cv2, math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W,H,FPS=1080,1920,30
_f={}
def font(name,size):
    k=(name,size)
    if k not in _f: _f[k]=ImageFont.truetype(os.path.join(ROOT,'brand','fonts','styles',name+'.woff') if not name.startswith('figtree') else os.path.join(ROOT,'brand','fonts',name+'.woff'),size)
    return _f[k]
def cl(x): return max(0.0,min(1.0,x))
def ss(x): x=cl(x); return x*x*(3-2*x)
def eout(x): x=cl(x); return 1-(1-x)**3
def prog(t,a,b): return cl((t-a)/(b-a))
# geometry in feet (width x length), long axis vertical
COURT=(32+10/12,65+7/12); PAD=(36.0,69.0); ACC=(48.0,81.0); SV=22+10/12
def rect(cx,cy,s,wl): w,l=wl; return (cx-w*s/2,cy-l*s/2,cx+w*s/2,cy+l*s/2)
def encode(frames_fn,n,out):
    tmp=out[:-4]+'.part.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(np.ascontiguousarray(frames_fn(i)).tobytes())
    p.stdin.close(); assert p.wait()==0; os.replace(tmp,out)
def zoom(a,z,fx=0.5,fy=0.5):
    if abs(z-1)<1e-4: return a
    h,w=a.shape[:2]; cw,ch=w/z,h/z; x0=(w-cw)*fx; y0=(h-ch)*fy
    M=np.float32([[z,0,-x0*z],[0,z,-y0*z]])
    return cv2.warpAffine(a,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
