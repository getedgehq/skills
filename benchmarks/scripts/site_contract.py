"""Adapter to the benchmarks UI's schema_version 1 (all display rates in percent)."""
import hashlib
import json
from pathlib import Path

PUBLIC = {'skillsbench-sample-sonnet55': 'skillsbench-sonnet-5-5', 'personal-skills': 'own-workflow-skills'}

def project(data, root):
    studies, skills, domains, tokens = [], [], [], []
    for s in data['studies']:
        r = s['result']; a, b = (s['arms'][:2] if r else [None, None])
        url = s['public_url'] or '/benchmarks/methodology/'
        studies.append(dict(id=s['id'], name=s['title'], model=', '.join(s['models']) or 'Pending', source='Edge', method=s['method_label'], without=r[a]['rate']*100 if r else None, with_skills=r[b]['rate']*100 if r else None, lift=r['paired_lift_pp'] if r else None, ci=r['task_bootstrap_ci95_pp'] if r else None, tasks=s['tasks'], runs=sum(r[x]['trials'] for x in (a,b)) if r else None, url=url, status='Done' if r else 'Running' if s['status']!='planned' else 'Planned', detail_status=s['status']))
    for r in data['third_party']:
        studies.append(dict(id=r['id'], name=r['id'].replace('-', ' ').title(), model=', '.join(r['models']) or 'Not reported', source=r['publisher'], method=r['method_label'], without=r['baseline_pct'], with_skills=r['treatment_pct'], lift=r['lift_pp'], ci=r['ci95'], tasks=r['tasks'], runs=9396 if r['id']=='skillsbench-1.1-aggregate' else None, url=r['url'], status='Published', metric=r['metric']))
    packages = json.loads((root/'data/skill-packages.json').read_text())
    for s in data['by_skill']:
        r = s['result']; arms = ['A','C'] if s['study_id'].startswith('skillsbench') else ['A','S']
        a,b=arms; study=PUBLIC[s['study_id']]
        identities=[p for t in s['tasks'] for p in packages.get(t,[]) if p['name']==s['skill']]
        identity=identities[0] if identities else {}
        page=identity.get('page')
        evidence=f'/benchmarks/{study}/#per-task'
        skills.append(dict(name=s['skill'], creator=identity.get('creator') or ('Federico De Ponte' if study=='own-workflow-skills' else 'SkillsBench contributors'), source='Edge', method=s['method_label']+'; bundled association', task_names=s['tasks'], tasks=len(s['tasks']), runs=s['runs'], without=r[a]['rate']*100, with_skills=r[b]['rate']*100, lift=r['paired_lift_pp'], ci=r['task_bootstrap_ci95_pp'], url=page or identity.get('url') or evidence, skill_page=page, evidence=evidence, study=study, attribution=s['attribution']))
    for d in data['by_domain']:
        domains.append(dict(name=d['domain'].replace('-',' ').title(), source='Edge', method=d['method_label'], without=d['baseline_rate']*100, with_skills=d['treatment_rate']*100, lift=d['lift_pp'], tasks=d['tasks'], runs=None, ci=None, url='/benchmarks/skillsbench-sonnet-5-5/#per-task'))
    for r in data['success_vs_tokens']:
        study=PUBLIC[r['study_id']]
        tokens.append(dict(study=study, name=study.replace('-',' ').title(), arm='Without skills' if r['arm']=='A' else 'With skills', mean_tokens=r['mean_tokens'], success=r['rate']*100, runs=r['trials'], url=f'/benchmarks/{study}/trials.jsonl', token_definition=r['token_definition']))
    models=[dict(s,name=s['model']+' / '+s['name']) for s in studies if s['source']=='Edge' and s['status']=='Done']
    # Public leaderboard is a distinct snapshot, not pooled with Edge experiments.
    models += json.loads((root/'third-party/data/leaderboard-snapshot.json').read_text())['models']
    provenance=[]
    for id, page in PUBLIC.items():
        for name in ('summary.json','trials.jsonl'):
            path=root/f'studies/{id}/results'/name
            provenance.append(dict(path=f'benchmarks/{page}/{name}',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return dict(schema_version=1,updated=data['as_of'],studies=studies,skills=skills,models=models,domains=domains,tokens=tokens,provenance=provenance)
