#!/usr/bin/env python3
"""Render a deterministic HTML film to H.264/AAC with Chromium and FFmpeg."""
from __future__ import annotations
import argparse, base64, json, mimetypes, re, shutil, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project',type=Path);p.add_argument('--out',type=Path)
    p.add_argument('--width',type=int);p.add_argument('--height',type=int)
    p.add_argument('--fps',type=int);p.add_argument('--duration',type=float)
    p.add_argument('--chromium',type=Path);p.add_argument('--stills',action='store_true')
    a=p.parse_args(); root=a.project.resolve()
    if not (root/'film.html').is_file(): p.error('PROJECT must contain film.html')
    cfg=json.loads((root/'brief.json').read_text())
    w=a.width or cfg.get('width',1920);h=a.height or cfg.get('height',1080)
    fps=a.fps or cfg.get('fps',30);duration=a.duration or cfg.get('duration',30)
    if w<=0 or h<=0 or w%2 or h%2 or fps<=0 or duration<=0: p.error('Dimensions must be positive even numbers; fps and duration must be positive.')
    out=(a.out or root/'renders'/'film.mp4').resolve();out.parent.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        exe=str(a.chromium) if a.chromium else shutil.which('chromium') or shutil.which('google-chrome')
        browser=pw.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        page.on('pageerror',lambda e:(errors.append(str(e)),print('Browser:',str(e),flush=True)))
        html=(root/'film.html').read_text()
        def inline_script(match):
            path=(root/match.group(1)).resolve()
            if not path.is_relative_to(root): raise ValueError('Script path escapes the project root')
            source=path.read_text()
            def embed_asset(m):
                asset=(root/m.group(2)).resolve()
                if not asset.is_relative_to(root) or not asset.is_file(): raise ValueError('Missing local asset: '+m.group(2))
                mime=mimetypes.guess_type(asset.name)[0] or 'application/octet-stream'
                return m.group(1)+'data:'+mime+';base64,'+base64.b64encode(asset.read_bytes()).decode()+m.group(1)
            source=re.sub(r"(['\"])(assets/[^'\"]+)\1",embed_asset,source)
            return '<script>'+source+'</script>'
        html=re.sub(r'<script src="([^"]+)"></script>',inline_script,html)
        html=html.replace('src="audio/original-score.wav"','')
        html=html.replace('<body>','<body class="capture">')
        page.set_content(html,wait_until='load')
        page.wait_for_function('window.__ready === true',timeout=15000)
        page.evaluate('document.fonts.ready')
        if a.stills:
          qa=root/'qa';qa.mkdir(exist_ok=True)
          for i,t in enumerate([0,2,4.5,6.4,8.6,12.9,16.1,19.8,24.2,28.5]):
            page.evaluate('async (t)=>{await window.renderAt(t)}',min(t,duration-1/fps))
            page.screenshot(path=str(qa/f'frame-{i:02d}-{t:04.1f}.png'))
          (qa/'browser-errors.json').write_text(json.dumps(errors,indent=2))
          browser.close(); print('Representative frames saved:',qa,flush=True)
          return 1 if errors else 0
        if not shutil.which('ffmpeg'):p.error('FFmpeg is not installed or not in PATH.')
        audio=root/'audio'/'original-score.wav'
        if not audio.exists():p.error('Generate audio/original-score.wav with synthesize_audio.py first.')
        cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','mjpeg','-framerate',str(fps),'-i','pipe:0','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-threads','2','-crf','17','-pix_fmt','yuv420p','-vf',f'scale={w}:{h}:flags=lanczos','-c:a','aac','-b:a','192k','-ar','48000','-af','loudnorm=I=-16:TP=-2:LRA=8','-t',str(duration),'-movflags','+faststart',str(out)]
        log=out.with_suffix('.render.log')
        with log.open('w') as stderr:
          enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=stderr)
          try:
            previous=None
            for frame in range(round(duration*fps)):
              data=page.evaluate('async (t)=>{const key=window.frameKey?window.frameKey(t):null;if(key&&key===window.__captureKey)return null;await window.renderAt(t);window.__captureKey=key;return document.getElementById("film").toDataURL("image/jpeg",0.96).split(",")[1]}',frame/fps)
              if data is not None:previous=base64.b64decode(data)
              if previous is None:raise RuntimeError('No rendered frame returned')
              enc.stdin.write(previous)
              if frame%(fps*3)==0:print(f'Rendered {frame}/{round(duration*fps)} frames',flush=True)
            enc.stdin.close();status=enc.wait(timeout=180)
          except Exception:
            enc.kill();raise
        browser.close()
        if status:raise RuntimeError(f'FFmpeg failed. See {log}')
        if errors:raise RuntimeError('Browser errors: '+'; '.join(errors))
        probe=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out)],capture_output=True,text=True,check=True)
        out.with_suffix('.ffprobe.json').write_text(probe.stdout)
        print('Created',out,flush=True)
        return 0
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:print('Render failed:',e,file=sys.stderr);sys.exit(1)
