import apl, subprocess, os, sys, numpy as np
from multiprocessing import Pool
FPS=apl.FPS; N=int(apl.DUR*FPS)
SEG=[(0,138),(138,522),(522,762),(762,1032),(1032,1212),(1212,N)]
def seg(i):
    a,b=SEG[i]; tmp=f'seg{i}.tmp.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{apl.W}x{apl.H}','-r',str(FPS),'-i','-',
      '-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-r',str(FPS),tmp],stdin=subprocess.PIPE)
    for f in range(a,b): p.stdin.write(apl.frame(f/FPS).tobytes())
    p.stdin.close(); assert p.wait()==0; os.rename(tmp,f'seg{i}.mp4'); return i
if __name__=='__main__':
    with Pool(min(6,os.cpu_count())) as pool: print(pool.map(seg,range(len(SEG))))
    open('list.txt','w').write(''.join(f"file 'seg{i}.mp4'\n" for i in range(len(SEG))))
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','list.txt','-c','copy','video_noaudio.mp4'],check=True)
