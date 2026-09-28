#!/usr/bin/env python3
"""Local AI history to a still and 12-second AI DNA film. No network or model calls."""
import argparse
import base64
import collections
import datetime as dt
import importlib.util
import json
import math
import shutil
import tempfile
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dna_extract', HERE / 'extract.py')
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
STOP = set("""a an and are as at be by can do for from get how i in is it me my of on or our please the this to us we what with you your about after all also any best build create fix help make new show that these those use using want why will work write note detail project plan conversation session task file code
und für der die das den dem des eine einer ein ist nicht mit von auf wie oder aber bei nach aus wir ihr sie mir mich dass wenn noch
have has had but lets let pls please check continue proceed just run read source give could would should there their them from then than where who which also really need wants wanted now same more much many does doing done one two three first last only each every some such into over under http https com www
request response summary issue review update status latest final draft version access idempotent re-run stable opens fail those name format formatting application calculation idea ideas guide tips overview clarification support text message conversation session local prompt input output markdown html json""".split())
WORDS = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9-]{2,}")

def terms(s):
    return [w.lower() for w in WORDS.findall(s) if w.lower() not in STOP and len(w) < 25 and not any(c.isdigit() for c in w)]

def load_history(args):
    stats = collections.defaultdict(collections.Counter)
    conv = {}
    def add(c):
        if c and (c['id'] not in conv or c['messageCount'] > conv[c['id']]['messageCount']):
            conv[c['id']] = c
    for path in args.chatgpt:
        p = Path(path).expanduser()
        if p.suffix.lower() == '.zip':
            for c in extract.load_zip(str(p), stats, p.stem): add(c)
        else:
            for c in extract.parse_chatgpt(json.loads(p.read_text()), p.stem, stats): add(c)
    for root, parser in ((args.claude_code, extract.parse_claude_code), (args.codex, extract.parse_codex)):
        for directory in root:
            p = Path(directory).expanduser()
            if not p.exists(): continue
            for file in p.rglob('*.jsonl'):
                if 'subagents' in file.parts: continue
                add(parser(str(file), 'local', stats))
    return sorted(conv.values(), key=lambda c: c['createdAt'])

def build_data(convs):
    if not convs: raise SystemExit('No conversations found. Pass --chatgpt PATH, --claude-code DIR, or --codex DIR.')
    providers = sorted({c['provider'] for c in convs}, key=lambda x: ('ChatGPT','Claude Code','Codex','Claude').index(x) if x in ('ChatGPT','Claude Code','Codex','Claude') else 99)
    stamps = [dt.datetime.fromisoformat(c['createdAt']).timestamp() for c in convs]
    y = 0.; rungs = []
    for i,c in enumerate(convs):
        if i:
            gap = max(0, (stamps[i] - stamps[i-1])/86400)
            y += 1 + (6*math.log1p(gap-2) if gap>2 else 0)
        rungs.append({'y':round(y,2),'t':int(stamps[i]),'p':providers.index(c['provider']), 'mc':int(c['messageCount']), 'w':int(c['charCount']/5.7), 'title':c.get('title') or '', 'c':'0'})
    # Six chronological eras from the user's titles, using locally ranked terms.
    docs=[set(terms(c.get('title') or '')) for c in convs]
    df=collections.Counter(w for doc in docs for w in doc)
    eras=[]; windows=min(6,len(convs))
    for j in range(windows):
        lo=len(convs)*j//windows; hi=len(convs)*(j+1)//windows
        part=docs[lo:hi]; freq=collections.Counter(w for doc in part for w in doc)
        def score(w): return freq[w]*math.sqrt(freq[w]/max(1,df[w])) if df[w]>=2 else 0
        order={w:i for i,c in enumerate(convs[lo:hi]) for w in terms(c.get('title') or '') if w in freq}
        ranked=sorted(freq,key=lambda w:(score(w),freq[w],-order.get(w,0)),reverse=True)
        anchor=ranked[0] if ranked else None
        related=collections.Counter(w for doc in part if anchor in doc for w in doc if w!=anchor) if anchor else {}
        partner=max(related,key=lambda w:(related[w]*score(w),related[w])) if related else None
        label=' '.join(w.title() for w in (anchor,partner) if w) or f'Era {j+1}'
        eras.append({'label':label.upper(),'y0':rungs[lo]['y'],'y1':rungs[hi-1]['y'],'t0':rungs[lo]['t'],'t1':rungs[hi-1]['t']})
    counts=collections.Counter(c['provider'] for c in convs)
    stats={'conversations':len(convs),'messages':sum(c['messageCount'] for c in convs),'providers':dict(counts)}
    return {'focus':max(range(len(rungs)), key=lambda i:rungs[i]['mc']), 'providers':providers, 'stats':stats,'rungs':rungs,'eras':eras}

def prepare_intro(path, out):
    from PIL import Image, ImageDraw
    p=Path(path).expanduser(); target=out/'intro'; target.mkdir(exist_ok=True)
    vf='scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350'
    if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):
        im=Image.open(p).convert('RGB')
        ratio=max(1080/im.width,1350/im.height)
        im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
        left=(im.width-1080)//2; top=(im.height-1350)//2
        frame=im.crop((left,top,left+1080,top+1350)).tobytes()
        (target/'frames.raw').write_bytes(frame)
    else:
        vf='scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p),'-t','2.8','-vf',vf,'-r','24','-f','rawvideo','-pix_fmt','rgb24',str(target/'frames.raw')]
        subprocess.run(cmd,check=True)
    mask=Image.new('L',(1080,1350)); draw=ImageDraw.Draw(mask)
    draw.ellipse((140,60,940,1160),fill=255)
    mask.save(target/'mask_crop.png')
    return target

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--chatgpt',action='append',default=[],metavar='ZIP_OR_JSON')
    ap.add_argument('--conversations-jsonl',metavar='PATH',help='previously extracted local conversations')
    ap.add_argument('--claude-code',action='append',default=[],metavar='DIR')
    ap.add_argument('--codex',action='append',default=[],metavar='DIR')
    ap.add_argument('--output',default='ai-dna-output')
    ap.add_argument('--preview',action='store_true',help='540x675, 12 fps film')
    ap.add_argument('--hide-titles',action='store_true',help='replace personal titles and era labels in visuals')
    ap.add_argument('--stops',help='JSON array of up to three {title, label} objects')
    ap.add_argument('--face',help='local portrait or short face video; also render an 18s dot intro')
    ap.add_argument('--music',help='local audio to mix into films')
    ap.add_argument('--skip-film',action='store_true',help='generate data and still only')
    args=ap.parse_args()
    if not (args.chatgpt or args.claude_code or args.codex or args.conversations_jsonl):
        args.claude_code=[str(Path.home()/'.claude/projects')]
        args.codex=[str(Path.home()/'.codex/sessions')]
    out=Path(args.output).expanduser().resolve(); out.mkdir(parents=True,exist_ok=True)
    t0=time.monotonic(); convs=load_history(args)
    if args.conversations_jsonl:
        old=[json.loads(line) for line in open(Path(args.conversations_jsonl).expanduser())]
        by_id={c['id']:c for c in old}
        for c in convs:
            if c['id'] not in by_id or c['messageCount']>by_id[c['id']]['messageCount']: by_id[c['id']]=c
        convs=sorted(by_id.values(),key=lambda c:c['createdAt'])
    data=build_data(convs)
    (out/'dna.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
    print(f"{data['stats']['conversations']:,} conversations · {data['stats']['messages']:,} messages",flush=True)
    env=os.environ.copy();env['DNA_FILE']=str(out/'dna.json');env['HIDE_TITLES']='1' if args.hide_titles else '0'
    if args.stops:
        stops_path=Path(args.stops).expanduser().resolve()
        stops=json.loads(stops_path.read_text())
        if not isinstance(stops,list) or not 1<=len(stops)<=3: ap.error('--stops must contain one to three entries')
        matched=[]
        for item in stops:
            if not isinstance(item,dict) or not isinstance(item.get('title'),str) or not item['title']: ap.error('each stop needs a nonempty title prefix')
            found=[i for i,r in enumerate(data['rungs']) if r['title'].startswith(item['title'])]
            if len(found)!=1: ap.error(f"stop title prefix {item['title']!r} matches {len(found)} conversations; use a unique prefix")
            if found[0] in matched: ap.error('stop entries must select distinct conversations')
            matched.append(found[0])
        env['STOPS_FILE']=str(stops_path)
    scratch=Path(tempfile.mkdtemp(prefix='ai-dna-face-')) if args.face and not args.skip_film else None
    if scratch: env['INTRO_DIR']=str(prepare_intro(args.face,scratch))
    render=HERE/'film.py'; scale='0.5' if args.preview else '1'
    subprocess.run([sys.executable,str(render),'hero',str(out/'hero.png'),'--scale',scale],env=env,check=True)
    fps=12 if args.preview else 30
    try:
        if not args.skip_film:
            for mode in (['pure','intro'] if args.face else ['pure']):
                frames=out/(mode+'-frames')
                if frames.exists(): shutil.rmtree(frames)
                subprocess.run([sys.executable,str(render),mode,str(frames),'--scale',scale,'--fps',str(fps),'--jobs','1'],env=env,check=True)
                cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(frames/'%04d.png')]
                if args.music: cmd+=['-stream_loop','-1','-i',str(Path(args.music).expanduser())]
                cmd+=['-map','0:v:0']
                if args.music: cmd+=['-map','1:a:0','-shortest']
                cmd+=['-c:v','libx264','-pix_fmt','yuv420p','-crf','18']
                if args.music:cmd+=['-c:a','aac','-b:a','192k']
                cmd+=['-movflags','+faststart',str(out/(mode+'.mp4'))]
                subprocess.run(cmd,check=True)
    finally:
        if scratch: shutil.rmtree(scratch)
    (out/'run.json').write_text(json.dumps({'stats':data['stats'],'preview':args.preview,'hide_titles':args.hide_titles,'seconds':round(time.monotonic()-t0,1)},indent=2))
    print('Output:',out,'elapsed:',round(time.monotonic()-t0,1),'s')
if __name__=='__main__':main()
