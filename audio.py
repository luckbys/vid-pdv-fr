"""Original soundtrack, narrated mix, beat detection and subtitle timing."""
from pathlib import Path
import json, subprocess, re, math
import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'work'
STORY=json.loads((ROOT/'roteiro.json').read_text())
SR=44100; DURATION=STORY['duration']; N=round(SR*DURATION)
rng=np.random.default_rng(93)
music=np.zeros((N,2),np.float64); guide=np.zeros(N,np.float64)
voice=np.zeros(N,np.float64); active=np.zeros(N,np.float64)

def put(x,at,gain=1,pan=0,target=music):
    start=round(at*SR); end=min(N,start+len(x))
    if start<0 or end<=start:return
    x=x[:end-start]*gain
    target[start:end,0]+=x*np.sqrt((1-pan)/2)
    target[start:end,1]+=x*np.sqrt((1+pan)/2)

def tone(f,d,kind='pluck'):
    t=np.arange(round(d*SR))/SR
    x=np.sin(2*np.pi*f*t)+.15*np.sin(4*np.pi*f*t)
    if kind=='pad':env=np.minimum(t/.22,1)*np.minimum((d-t)/.4,1)
    else:env=(1-np.exp(-t*160))*np.exp(-t*5.5)
    return x*env

# A bright original D-Bm-G-A progression; no licensed or stock music.
chords=[[146.83,185,220],[123.47,146.83,185],[98,123.47,146.83],[110,138.59,164.81]]
for bar in range(math.ceil(DURATION/2)):
    base=bar*2; chord=chords[(bar//2)%4]
    for j,f in enumerate(chord):put(tone(f,2.35,'pad'),base,.065,pan=(j-1)*.45)
    for k in range(4):
        put(tone(chord[[0,2,1,2][k]]*2,.9),base+k*.5,.065,pan=(-1 if k%2 else 1)*.25)
        at=base+k*.5
        t=np.arange(round(.3*SR))/SR
        kick=np.sin(2*np.pi*np.cumsum(50+90*np.exp(-t*30))/SR)*np.exp(-t*17)
        kick+=rng.normal(0,.035,len(t))*np.exp(-t*230)
        put(kick,at,.29)
        a=round(at*SR);b=min(N,a+len(kick))
        if b>a:guide[a:b]+=kick[:b-a]
        put(tone(chord[0]/2,.35),at,.09)
        if k%2:
            ts=np.arange(round(.13*SR))/SR
            snap=signal.sosfilt(signal.butter(2,2400,fs=SR,btype='high',output='sos'),rng.normal(0,1,len(ts)))
            put(snap*np.exp(-ts*30),at,.042)
    for k in range(8):
        ts=np.arange(round(.065*SR))/SR
        hat=signal.sosfilt(signal.butter(2,7500,fs=SR,btype='high',output='sos'),rng.normal(0,1,len(ts)))
        put(hat*np.exp(-ts*75),base+k*.25,.014,pan=.4 if k%2 else -.4)

for i,s in enumerate(STORY['segments']):
    path=WORK/f'voice-{i:02d}.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/s['audio']),
         '-af','highpass=f=75,lowpass=f=10000','-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(path)],check=True)
    _,raw=wavfile.read(path);raw=raw.astype(np.float64)/32768
    a=round(s['voice_start']*SR);b=min(N,a+len(raw))
    voice[a:b]+=raw[:b-a]
    words=s['words']
    v0=a+round(words[0]['offset']/1e7*SR)
    v1=a+round((words[-1]['offset']+words[-1]['duration'])/1e7*SR)
    active[max(0,v0-2205):min(N,v1+6615)]=1

wavfile.write(WORK/'narracao-original.wav',SR,np.int16(np.clip(voice,-1,1)*32767))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/'narracao-original.wav'),
    '-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',str(SR),'-ac','1',str(WORK/'narracao.wav')],check=True)
_,voice=wavfile.read(WORK/'narracao.wav');voice=voice.astype(np.float64)/32768
voice=voice[:N]
if len(voice)<N:voice=np.pad(voice,(0,N-len(voice)))
# A 250 Hz control envelope keeps the 100 ms ducking ramp without a costly
# convolution at audio sample rate; interpolation restores sample precision.
hop=round(SR/250)
control=gaussian_filter1d(active[::hop],sigma=.10*SR/hop)
duck=np.interp(np.arange(N),np.arange(len(control))*hop,control)
music*=((.42-.21*duck)[:,None])

switches=[s['start'] for s in STORY['segments']]
callouts=[]
for i,s in enumerate(STORY['segments']):
    offsets={0:[.5,1,1.5],1:[1,2,3],2:[.5,1.5,2.5],3:[.5,2,3.5],4:[.5,1.5,3],5:[.5,1.5,3],6:[.5,1.5,2.5,3.5],7:[.5,1.5,2.5],8:[.5,1.5,2.5]}.get(i,[])
    callouts.extend(s['start']+x for x in offsets if s['start']+x<s['end'])
sfx=np.zeros((N,2),np.float64)
for at in switches[1:]:
    ts=np.arange(round(.24*SR))/SR
    sw=signal.sosfilt(signal.butter(2,[800,4600],fs=SR,btype='band',output='sos'),rng.normal(0,1,len(ts)))
    put(sw*np.sin(np.pi*ts/.24)**2,at-.24,.018,pan=-.2,target=sfx)
    put(tone(659.25,.5),at,.019,pan=.2,target=sfx)
for at in callouts:
    put(tone(987.77,.16),at,.009,pan=.15,target=sfx)

fade=np.minimum(np.arange(N)/SR/.02,1)*np.clip((DURATION-np.arange(N)/SR)/1.25,0,1)
music*=fade[:,None];sfx*=fade[:,None]
mixed=music+sfx+voice[:,None]/np.sqrt(2)
wavfile.write(WORK/'trilha-original.wav',SR,np.int16(np.clip(music+sfx,-1,1)*32767))
wavfile.write(WORK/'mix-raw.wav',SR,np.int16(np.clip(mixed,-1,1)*32767))

# Recover the grid from the synthesized kick stem, allowing its attack latency.
window=441
rms=np.sqrt(np.mean(guide[:N//window*window].reshape(-1,window)**2,axis=1))
peaks,_=signal.find_peaks(rms,height=.035,distance=40)
onsets=peaks*window/SR
period=float(np.median(np.diff(onsets)))
phase=float(np.median(onsets-np.round(onsets/period)*period))
beats=[round(i*period,6) for i in range(round(DURATION/period))]
grid=dict(duration=DURATION,sample_rate=SR,bpm=round(60/period,5),beats=beats,
    scene_switches=switches,callouts=callouts,detected_onsets=onsets.tolist(),
    measured_attack_latency_seconds=round(phase,5),
    analysis='RMS transient detection on the original kick stem; scipy.find_peaks, attack latency compensated.')
(ROOT/'beats.json').write_text(json.dumps(grid,indent=2))

captions_spec=[
    [('Fila no caixa?',0,2)],
    [('Vendas lentas e tarefas manuais',0,4),('fazem o cliente esperar',5,8),('e aumentam o retrabalho.',9,12)],
    [('Com o F-PDV da Frenty,',0,7),('sua loja conecta atendimento,',8,11),('estoque e emissão fiscal.',12,15)],
    [('Venda com uma interface intuitiva',0,4),('e automatize a emissão',5,8),('das notas fiscais.',9,11)],
    [('Atualize o estoque em tempo real',0,5),('e acompanhe os produtos disponíveis.',6,10)],
    [('Menos digitação repetida.',0,2),('Mais organização e precisão',3,6),('nas informações das vendas.',7,10)],
    [('Acompanhe relatórios,',0,1),('identifique tendências',2,3),('e decida com mais clareza.',4,8)],
    [('Quer ver como funciona',0,3),('na sua loja?',4,6),('Agende uma demonstração gratuita',7,10),('do F-PDV.',11,15)],
    [('Acesse frenty.com.br',0,6),('e fale com o nosso time.',7,12)],
]
caps=[]
for s,spec in zip(STORY['segments'],captions_spec):
    for text,a,b in spec:
        words=s['words'];start=s['voice_start']+words[a]['offset']/1e7
        end=s['voice_start']+(words[b]['offset']+words[b]['duration'])/1e7
        caps.append(dict(start=round(start,3),end=round(end+.10,3),text=text))
for i,c in enumerate(caps[:-1]):c['end']=min(c['end'],caps[i+1]['start']-.02)
(ROOT/'legendas.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2))
def stamp(t):
    n=round(t*1000);h=n//3600000;m=n//60000%60;s=n//1000%60;ms=n%1000
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
(ROOT/'legendas.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(caps))+'\n')

measure=subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(WORK/'mix-raw.wav'),
    '-af','loudnorm=I=-14:TP=-2.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
data=json.loads(re.findall(r'\{[\s\S]*?\}',measure.stderr)[-1])
flt='loudnorm=I=-14:TP=-2.5:LRA=7:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true'.format(**data)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/'mix-raw.wav'),
    '-af',flt,'-ar',str(SR),str(WORK/'audio-final.wav')],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/'audio-final.wav'),
    '-c:a','aac','-b:a','192k','-movflags','+faststart',str(WORK/'audio-final.m4a')],check=True)
(WORK/'loudness-first-pass.json').write_text(json.dumps(data,indent=2))
encoded=subprocess.run(['ffmpeg','-hide_banner','-i',str(WORK/'audio-final.m4a'),'-af','loudnorm=I=-14:TP=-2.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
metrics=json.loads(re.findall(r'\{[\s\S]*?\}',encoded.stderr)[-1])
gain=-14-float(metrics['input_i'])
if abs(gain)>.05 and float(metrics['input_tp'])+gain<-.8:
    temp=WORK/'audio-adjusted.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/'audio-final.wav'),'-af',f'volume={gain:.4f}dB',str(temp)],check=True)
    temp.replace(WORK/'audio-final.wav')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(WORK/'audio-final.wav'),'-c:a','aac','-b:a','192k','-movflags','+faststart',str(WORK/'audio-final.m4a')],check=True)
(WORK/'aac-first-check.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps(dict(duration=DURATION,beats=len(beats),bpm=grid['bpm'],captions=len(caps),raw_lufs=data['input_i'])))
