#!/usr/bin/env python3
"""Check assets, timing, source provenance and preview/final evidence gates."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
FONT_EXT={'.ttf','.otf','.woff','.woff2','.eot','.ttc'}

def inspect(root:Path,mode:str)->dict:
 errors=[];notes=[];blocked=[]
 def exists(path):
  q=(root/path).resolve()
  return q.is_relative_to(root) and q.is_file()
 if not exists('brief.json'):return {'ok':False,'errors':['Missing brief.json'],'notes':[],'publication_blockers':[]}
 try:cfg=json.loads((root/'brief.json').read_text())
 except Exception as e:return {'ok':False,'errors':['Invalid brief.json: '+str(e)],'notes':[],'publication_blockers':[]}
 for name in ['film.html','brief.js','src/film.js','src/orbit.js','assets/brand/edge-lockup.svg']:
  if not exists(name):errors.append('Missing required file: '+name)
 dur=cfg.get('duration',0)
 if not isinstance(dur,(float,int)) or dur<=0:errors.append('Duration must be positive')
 for attr in ['width','height','fps']:
  if not isinstance(cfg.get(attr),int) or cfg[attr]<=0:errors.append(attr+' must be a positive integer')
 if not str(cfg.get('destination','')).startswith('https://'):errors.append('A confirmed HTTPS destination is required')
 requires_run=cfg.get('claim_mode','recorded_run')=='recorded_run'
 if not requires_run and cfg.get('publication_approval')!='non_evidence_showcase':blocked.append('Explicit approval of the non-evidence showcase is required')
 prev=0
 for shot in cfg.get('shots',[]):
  start,end=shot.get('start'),shot.get('end')
  if not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or start!=prev or end<=start:errors.append('Invalid or discontinuous shot: '+str(shot.get('id')))
  prev=end
  if not shot.get('source') or not exists(shot['source']):errors.append('Missing shot source: '+str(shot.get('id')))
  if shot.get('kind') in {'original_demo','workflow_visualization','creator_showcase'} and not shot.get('label'):errors.append('Unlabeled non-recording shot: '+str(shot.get('id')))
  if requires_run and shot.get('kind')=='workflow_visualization':blocked.append('Replace visualized workflow with matching actual-run evidence: '+str(shot.get('id')))
  if requires_run and shot.get('kind')=='original_demo':blocked.append('Replace original demo with same-run output, or explicitly approve a non-evidence showcase: '+str(shot.get('id')))
 if prev!=dur:errors.append('Shot end must equal film duration')
 for claim in cfg.get('claims',[]):
  if not claim.get('source') or claim.get('status') not in {'source_verified','run_verified','user_supplied'}:errors.append('Unverified claim: '+claim.get('text',''))
 for asset in cfg.get('assets',[]):
  if not exists(asset.get('path','')):errors.append('Missing asset bytes: '+asset.get('path',''))
  if asset.get('rights') not in {'original','user_provided','licensed','permission_recorded'}:blocked.append('Asset rights not documented: '+asset.get('path',''))
 for f in root.rglob('*'):
  if f.is_file() and f.suffix.lower() in FONT_EXT:errors.append('Do not bundle font binaries: '+str(f.relative_to(root)))
 for k in ['actual_run','exact_prompt','tool_trace','real_output']:
  v=cfg.get('evidence',{}).get(k)
  if requires_run and (not v or not exists(v)):blocked.append('Missing local evidence: '+k)
 if mode=='final' and cfg.get('mode')!='final':blocked.append('Project is marked preview')
 if mode=='final':errors+=blocked
 elif blocked:notes.append('Preview is correctly separated from a recording-based final cut.')
 return {'ok':not errors,'mode':mode,'errors':errors,'notes':notes,'publication_blockers':blocked,'shots':len(cfg.get('shots',[]))}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--mode',choices=['preview','final'],default='preview');p.add_argument('--out',type=Path);a=p.parse_args()
 result=inspect(a.project.resolve(),a.mode);text=json.dumps(result,indent=2)
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(text)
 print(text);return 0 if result['ok'] else 1
if __name__=='__main__':sys.exit(main())
