#!/usr/bin/env python3
"""Collect a week of real work into content-digest.md (read-only). Sources: Claude Code + Codex session logs,
git log, company docs. Redacts secrets. Usage: collect.py --days 7 --repo . --out content-digest.md"""
import argparse,calendar,glob,json,os,re,subprocess,time
ap=argparse.ArgumentParser(); ap.add_argument('--days',type=int,default=7); ap.add_argument('--repo',default='.')
ap.add_argument('--out',default='content-digest.md'); ap.add_argument('--max',type=int,default=25,help='max requests kept per session (most recent)')
a=ap.parse_args(); since=time.time()-a.days*86400
RED=[(re.compile(r'(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})'),'[SECRET]'),
     (re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),'[EMAIL]'),(re.compile(r'(?<![\w-])(\+\d[\d ()-]{7,}\d|\(\d{3}\) ?\d{3}[ -]\d{4}|\d{3}[ .-]\d{3}[ .-]\d{4})(?![\w-])'),'[PHONE]'),   # not dates or ids
     (re.compile(r'(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+'),r'\1=[SECRET]')]
def clean(t):
    t=re.sub(r'\s+',' ',t).strip()
    for r,s in RED: t=r.sub(s,t)
    return t
def text_of(c):
    if isinstance(c,str): return c
    if isinstance(c,list): return ' '.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type') in ('text','input_text','output_text'))
    return ''
items=[]
logs=glob.glob(os.path.expanduser('~/.claude/projects/*/*.jsonl'))+glob.glob(os.path.expanduser('~/.codex/sessions/**/*.jsonl'),recursive=True)
for f in sorted(logs,key=os.path.getmtime,reverse=True):
    if os.path.getmtime(f)<since: continue
    proj=os.path.basename(os.path.dirname(f)); last_asst=None; asks=[]
    for i,l in enumerate(open(f,errors='ignore'),1):
        try: d=json.loads(l)
        except Exception: continue
        m=d.get('message') or d.get('payload') or {}
        role=m.get('role') or d.get('type'); t=text_of(m.get('content'))
        ts=d.get('timestamp','')
        if not t or t.startswith('<') or 'tool_result' in l[:300] or t.startswith('This session is being continued'): continue
        try:
            if ts and calendar.timegm(time.strptime(ts[:19],'%Y-%m-%dT%H:%M:%S'))<since: continue
        except Exception: pass
        if role=='user' and len(t)>15: asks.append(('ask',ts,proj,f'{os.path.basename(f)}:{i}',clean(t)[:300]))
        elif role=='assistant' and len(t)>80: last_asst=(ts,proj,f'{os.path.basename(f)}:{i}',clean(t)[:600])
    items.extend(asks[-a.max:])
    if last_asst: items.append(('result',)+last_asst)
git=[]
try:
    out=subprocess.run(['git','-C',a.repo,'log',f'--since={a.days} days ago','--pretty=%h|%ad|%s','--date=short'],capture_output=True,text=True).stdout
    git=[l.split('|',2) for l in out.splitlines() if l.count('|')>=2][:a.max]
except Exception: pass
docs=[]
for name in ['README.md','CLAUDE.md','AGENTS.md','CHANGELOG.md']:
    p=os.path.join(a.repo,name)
    if os.path.exists(p): docs.append((name,clean(open(p,errors='ignore').read())[:1500]))
with open(a.out,'w') as o:
    o.write(f'# Content digest, last {a.days} days\n\nRead-only extract. Secrets, emails and phone numbers redacted. Review before sharing.\n\n')
    o.write('## Company context\n'+''.join(f'\n### {n}\n{t}\n' for n,t in docs)+'\n')
    o.write(f'## Commits ({len(git)})\n'+''.join(f'- {h} {d}: {clean(s)}\n' for h,d,s in git)+'\n')
    o.write('## Agent sessions: what you asked\n'+''.join(f'- [{ts[:10]}] ({p}) {t}  `{src}`\n' for k,ts,p,src,t in items if k=='ask')+'\n')
    o.write('## Agent sessions: where each session ended\n'+''.join(f'- [{ts[:10]}] ({p}) {t}  `{src}`\n' for k,ts,p,src,t in items if k=='result'))
print(f'{a.out}: {len(git)} commits, {sum(1 for x in items if x[0]=="ask")} requests, {sum(1 for x in items if x[0]=="result")} session results, {len(docs)} docs')
