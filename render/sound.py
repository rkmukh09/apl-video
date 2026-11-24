import numpy as np, wave
SR=48000; D=46.0; n=int(SR*D); out=np.zeros(n)
rng=np.random.default_rng(7)
def add(sig,t,g):
    i=int(t*SR); e=min(n,i+len(sig)); out[i:e]+=g*sig[:e-i]
def whoosh(dur=0.7):
    m=int(SR*dur); x=rng.standard_normal(m)
    # sweep low-pass via moving average of varying width
    env=np.sin(np.linspace(0,np.pi,m))**2
    y=np.convolve(x,np.ones(40)/40,'same')
    return y*env
def tick():
    m=int(SR*0.06); t=np.arange(m)/SR
    return np.sin(2*np.pi*1800*t)*np.exp(-t*90)+0.4*rng.standard_normal(m)*np.exp(-t*200)
def thump():
    m=int(SR*0.25); t=np.arange(m)/SR
    return np.sin(2*np.pi*(110-60*t)*t)*np.exp(-t*14)
# soft pad: two sine chords with slow swell
t=np.arange(n)/SR
pad=sum(np.sin(2*np.pi*f*t) for f in (110,164.8,220,277.2))/4
pad*=0.5+0.5*np.sin(2*np.pi*t/16)**2
fade=np.minimum(1,np.minimum(t/2,(D-t)/3))
out+=0.05*pad*fade
for tt in (3.6,17.0,24.8,34.0,39.8): add(whoosh(),tt-0.1,0.35)
for tt in (0.3,0.5,0.7,6.6,7.4,8.2,11.4,14.0,18.6,19.2,19.9,22.4,27.7,28.0,31.4,31.85,32.3,32.75,36.6,37.2,37.4,41.0,41.35,41.7): add(tick(),tt,0.18)
for tt in (4.4,11.0,26.0,40.2): add(thump(),tt,0.35)
out/=np.max(np.abs(out))/0.89
pcm=(out*32767).astype(np.int16)
w=wave.open('sfx.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
