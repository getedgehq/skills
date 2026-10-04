#!/usr/bin/env python3
"""Make an original 30-second, 128 BPM electronic music bed. No samples required."""
from __future__ import annotations
import argparse,wave
from pathlib import Path
import numpy as np

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 sr=48000;duration=30;beat=60/128;n=round(duration*sr);rng=np.random.default_rng(280926)
 music=np.zeros((n,2),np.float64)
 def add(sig,start,pan=0,gain=1):
  i=round(start*sr)
  if i<0 or i>=n:return
  sig=np.asarray(sig);sig=sig[:n-i]
  if sig.ndim==1:sig=np.column_stack((sig*np.sqrt((1-pan)/2),sig*np.sqrt((1+pan)/2)))
  music[i:i+len(sig)]+=sig*gain
 def tt(d):return np.arange(round(d*sr))/sr
 def noise(d):
  z=rng.standard_normal(round(d*sr));return z-np.concatenate(([0],z[:-1]))*.88
 def tone(freq,d,amp=.1,bright=.5):
  t=tt(d);s=np.sin(2*np.pi*freq*t)+bright*.33*np.sin(2*np.pi*freq*2.006*t)+bright*.12*np.sin(2*np.pi*freq*3*t)
  return amp*s*(1-np.exp(-t*120))*np.exp(-t*2.7)
 # Chords in A minor, warm and deliberately sparse.
 chords=[[57,60,64,71],[53,57,60,64],[48,55,59,64],[55,59,62,69]]
 def hz(note):return 440*2**((note-69)/12)
 for b in range(64):
  start=b*beat;section=b//16;bar=b//4
  # A short thinner bridge leaves space for the request and handoff.
  full=not(24<=b<32);end=b>=61
  if not end and (full or b%4==0):
   t=tt(.40);f=48+108*np.exp(-t*38);phase=2*np.pi*np.cumsum(f)/sr
   kick=np.sin(phase)*np.exp(-t*12)*(1-np.exp(-t*950))+.08*noise(.40)*np.exp(-t*200)
   add(kick,start,gain=.47)
  if b%4 in (1,3) and not end:
   t=tt(.20);cl=noise(.20);cl*=np.exp(-t*23)*(1+.6*np.cos(2*np.pi*t*42));add(cl,start,pan=.1,gain=.07)
  if not end:
   for off in [0,.5]:
    d=.075 if off==0 else .13;t=tt(d);z=noise(d)*np.exp(-t*(80 if off==0 else 35));add(z,start+off*beat,pan=(-.45 if b%2==0 else .45),gain=.016 if off==0 else .027)
  if 32<=b<56:
   t=tt(.08);add(noise(.08)*np.exp(-t*70),start+.76*beat,pan=.65,gain=.011)
  chord=chords[min(section,3)]
  if b%4 in (0,2) and b<61:
   base=hz(chord[0]-12);t=tt(.42);waveform=np.sin(2*np.pi*base*t)+.16*np.sin(2*np.pi*base*2*t)
   add(waveform*np.exp(-t*5)*(1-np.exp(-t*160)),start+.08*beat,gain=.20)
  # Off-beat stabs and their short stereo echoes.
  if b%2==0 and b<59:
   for note in chord:
    sig=tone(hz(note+12),.9,amp=.030,bright=.5 if b<32 else .8)
    add(sig,start+.48*beat,pan=-.3,gain=1)
    add(sig,start+1.23*beat,pan=.6,gain=.22)
  if b>=8 and b<59:
   note=chord[[2,3,1,2,0,2,3,1][b%8]]+12
   sig=tone(hz(note),.55,amp=.032,bright=.8)
   add(sig,start+.75*beat,pan=(-.3 if b%2 else .3));add(sig,start+1.50*beat,pan=.55,gain=.18)
 # Sustained, gently detuned chord pad with a beat-shaped ducking envelope.
 for k,ch in enumerate(chords):
  start=k*7.5;t=tt(7.7);env=np.minimum(t/.55,1)*np.minimum((7.7-t)/.8,1)
  duck=1-.28*np.exp(-(t%beat)*13)
  for idx,note in enumerate(ch):
   f=hz(note);left=(np.sin(2*np.pi*f*.999*t)+.18*np.sin(2*np.pi*f*2*t))*env*duck*.014
   right=(np.sin(2*np.pi*f*1.001*t+.12)+.18*np.sin(2*np.pi*f*2*t))*env*duck*.014
   add(np.column_stack((left,right)),start)
 # Original transition swishes and a final, resolved minor ninth.
 for s in [3.6,7.35,11.10,14.85,26.10]:
  t=tt(.20);z=noise(.20)*np.sin(np.pi*t/.20)**2;add(z,s,pan=.2,gain=.035)
 for note in [57,60,64,71]:add(tone(hz(note+12),1.8,amp=.045,bright=.32),28.12,pan=(note-64)/30)
 # Short beginning ramp and clean final decay.
 fade=np.ones(n);fade[:480]=np.linspace(0,1,480);fade[-24000:]=np.linspace(1,0,24000)
 music*=fade[:,None];music=np.tanh(music*1.2)*.83
 peak=np.max(np.abs(music));music*=.88/max(peak,1e-9)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(a.out),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((np.clip(music,-1,1)*32767).astype('<i2').tobytes())
 print('Original stereo score:',a.out)
if __name__=='__main__':main()
