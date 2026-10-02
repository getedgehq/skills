#!/usr/bin/env python3
"""Approved completed-result sync and deterministic site export. No model calls."""
import argparse
import hashlib
import json
import math
import random
import re
from site_contract import project
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = {'skillsbench-sample-sonnet55': 'skillsbench-sonnet-5-5', 'personal-skills': 'own-workflow-skills'}
FIELDS = {'model', 'arm', 'task', 'trial', 'domain', 'difficulty', 'reward', 'raw_reward', 'exception', 'infra', 'input_tokens', 'cache_tokens', 'output_tokens', 'tokens_total', 'agent_wall_s', 'skill_read', 'skill', 'skill_invoked', 'skill_md_read', 'touched_service', 'checks', 'check_categories'}
UNSAFE = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{15,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|/(?:home|root|srv)/|[\w.+-]+@[\w.-]+\.[a-z]{2,})', re.I)

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def read(path):
    return json.loads(path.read_text())

def safe_bytes(data):
    if UNSAFE.search(data.decode()):
        raise ValueError('Private path, host, account or credential pattern in export')

def records(path):
    data = path.read_bytes()
    safe_bytes(data)
    rows = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
    seen = set()
    for row in rows:
        if set(row) - FIELDS:
            raise ValueError('Unapproved trial fields')
        if row['trial'] in seen:
            raise ValueError('Duplicate trial ID')
        seen.add(row['trial'])
        if row.get('reward') is not None and not 0 <= row['reward'] <= 1:
            raise ValueError('Invalid reward')
        for key in ('checks', 'check_categories'):
            if key in row and not isinstance(row[key], dict):
                raise ValueError('Invalid check map')
        if 'checks' in row and any(type(v) is not bool for v in row['checks'].values()):
            raise ValueError('Check diagnostics are forbidden')
    return rows

def wilson(passes, n):
    if not n:
        return None
    z = 1.95996398454
    p = passes/n
    centre = (p + z*z/(2*n))/(1+z*z/n)
    width = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [round(centre-width, 6), round(centre+width, 6)]

def effect(rows, arms):
    tasks = sorted({r['task'] for r in rows})
    diffs = []
    for task in tasks:
        groups = [[r['reward'] for r in rows if r['task'] == task and r['arm'] == arm] for arm in arms]
        if all(groups):
            diffs.append(sum(groups[1])/len(groups[1])-sum(groups[0])/len(groups[0]))
    if not diffs:
        return None, None
    mean = sum(diffs)/len(diffs)*100
    ci = None
    if len(diffs) > 1:
        rng = random.Random(20261002)
        boot = sorted(sum(rng.choices(diffs, k=len(diffs)))/len(diffs)*100 for _ in range(10000))
        ci = [round(boot[250], 3), round(boot[9750], 3)]
    return round(mean, 3), ci

def outcome(rows, arms):
    result = {}
    for arm in arms:
        group = [r for r in rows if r['arm'] == arm]
        n = len(group)
        passes = sum(r['reward'] == 1 for r in group)
        result[arm] = {'passes': passes, 'trials': n, 'rate': passes/n if n else None, 'wilson_ci95': wilson(passes, n)}
    delta, ci = effect(rows, arms)
    result.update(paired_lift_pp=delta, task_bootstrap_ci95_pp=ci)
    return result

def validate_finished(id, base):
    rows = records(base/'trials.jsonl')
    safe_bytes((base/'summary.json').read_bytes())
    summary = read(base/'summary.json')
    arms = ['A', 'C'] if id.startswith('skillsbench') else ['A', 'S']
    if any(r['arm'] not in arms or r['model'] != 'claude-sonnet-5-5' for r in rows):
        raise ValueError('Unexpected model or arm')
    scored = [r for r in rows if not r.get('infra')]
    if any(r['reward'] is None for r in scored):
        raise ValueError('Missing scored reward')
    data = summary['claude-sonnet-5-5']['all'] if id.startswith('skillsbench') else summary
    for arm in arms:
        group = [r for r in scored if r['arm'] == arm]
        if len(group) != data[arm]['trials'] or sum(r['reward'] == 1 for r in group) != data[arm]['passes']:
            raise ValueError('Summary / trial count mismatch')
    if id == 'personal-skills':
        for arm in arms:
            checks = [v for r in scored if r['arm'] == arm for v in r['checks'].values()]
            if len(checks) != summary[arm]['checks_total'] or sum(checks) != summary[arm]['checks_passed']:
                raise ValueError('Check counts differ from summary')
    if len({r['task'] for r in scored}) != (data['paired']['n_tasks'] if id.startswith('skillsbench') else summary['tasks']):
        raise ValueError('Task count mismatch')
    return rows, scored, summary, arms

def build():
    registry = read(ROOT/'data/study-registry.json')
    model_rows, domains, skills, tokens = [], [], [], []
    for study in registry['studies']:
        id = study['id']
        if id not in PUBLISHED:
            assert study['result'] is None
            continue
        all_rows, rows, summary, arms = validate_finished(id, ROOT/f'studies/{id}/results')
        result = outcome(rows, arms)
        if id.startswith('skillsbench'):
            original = summary['claude-sonnet-5-5']['all']
            result['paired_lift_pp'] = original['paired']['mean_delta']*100
            result['task_bootstrap_ci95_pp'] = [x*100 for x in original['paired']['delta_ci95_task_bootstrap']]
            result['exposure_rate'] = original['C']['skill_read_rate']
            mapping = read(ROOT/f'studies/{id}/results/sample.json')['tasks']
            for domain, d in original['per_domain'].items():
                domains.append(dict(study_id=id, domain=domain, tasks=d['tasks'], baseline_rate=d['A'], treatment_rate=d['C'], lift_pp=d['delta_pp'], ci95=None, metric='descriptive pooled fully-correct rates', method_label=study['method_label']))
        else:
            result['paired_lift_pp'] = summary['paired_delta']*100
            result['task_bootstrap_ci95_pp'] = [x*100 for x in summary['task_bootstrap_ci95']]
            result['exposure_rate'] = summary['exposure']['loaded']/summary['exposure']['total']
            mapping = {r['task']: {'skills': [r['skill']]} for r in rows}
        result['infrastructure_excluded'] = len(all_rows)-len(rows)
        tasks = {r['task'] for r in rows}
        result['never_solved_tasks'] = sum(not any(r['reward'] == 1 for r in rows if r['task'] == t) for t in tasks)
        result['always_solved_tasks'] = sum(all(r['reward'] == 1 for r in rows if r['task'] == t) for t in tasks)
        study['result'] = result
        model_rows.append(dict(study_id=id, model='Claude Code / Sonnet 5.5', method_label=study['method_label'], source='Edge', result=result))
        names = sorted({s for t in tasks for s in mapping.get(t, {}).get('skills', [])})
        for name in names:
            ids = sorted(t for t in tasks if name in mapping.get(t, {}).get('skills', []))
            group = [r for r in rows if r['task'] in ids]
            skills.append(dict(study_id=id, skill=name, creator=None, skill_url=None, source_task_url='https://github.com/benchflow-ai/skillsbench/tree/v1.1' if id.startswith('skillsbench') else None, tasks=ids, runs=len(group), result=outcome(group, arms), attribution='bundled treatment association, not isolated skill effect', ci_method='task bootstrap; null for single-task groups', method_label=study['method_label']))
        for arm in arms:
            group = [r for r in rows if r['arm'] == arm and r.get('input_tokens') is not None and r.get('output_tokens') is not None]
            if group:
                tokens.append(dict(study_id=id, model='Claude Code / Sonnet 5.5', arm=arm, trials=len(group), rate=sum(r['reward'] == 1 for r in group)/len(group), mean_tokens=sum(r['input_tokens']+r['output_tokens'] for r in group)/len(group), token_definition='input plus output as recorded by harness; cache accounting may differ across studies', method_label=study['method_label']))
    third = read(ROOT/'third-party/data/published.json')
    for r in third:
        if r['baseline_pct'] is not None and len(r['models']) == 1:
            model_rows.append(dict(study_id=r['id'], model=r['models'][0], source='third-party', method_label=r['method_label'], metric=r['metric'], baseline_pct=r['baseline_pct'], treatment_pct=r['treatment_pct'], lift_pp=r['lift_pp'], ci95=None, source_url=r['url']))
    export = dict(schema_version=1, as_of=registry['as_of'], studies=registry['studies'], third_party=third, by_model=model_rows, by_domain=domains, by_skill=skills, success_vs_tokens=tokens)
    lines = ['# Edge study register', '', 'Edge brings specialist expertise into agent work. Completed and planned studies remain separate; every row keeps its method label.', '', '| Study | Question | Tasks | Arms | Models | k | Method | Status | Result | Report |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for s in export['studies']:
        result = s['result']
        headline = 'Pending'
        if result:
            arms = [a for a in s['arms'] if a in result]
            headline = ' vs '.join(f"{result[a]['passes']}/{result[a]['trials']}" for a in arms) + f"; paired +{result['paired_lift_pp']:.1f} pp"
        lines.append('| '+ ' | '.join([s['title'], s['question'], str(s['tasks'] or 'Pending') + ' ('+s['tasks_kind']+')', ', '.join(s['arms']) or 'Pending', ', '.join(s['models']) or 'Pending', str(s['k'] or 'Pending'), s['method_label'], s['status'], headline, f"[Report]({s['report']})"])+' |')
    lines += ['', 'Third-party numerical facts and source links: [SOURCES.md](third-party/SOURCES.md) and [published.json](third-party/data/published.json). Different metrics, samples and interventions cannot support a pooled ranking.', '', 'Snapshot date: '+registry['as_of']+'. Running/prepared refers to study work, not a claim that subject jobs are currently active.', '']
    return export, '\n'.join(lines)

def refresh_reports(export):
    for study in export["studies"]:
        id=study["id"]
        if id not in PUBLISHED: continue
        all_rows, rows, summary, arms = validate_finished(id, ROOT/f"studies/{id}/results")
        result=study["result"]
        report = ROOT/f'studies/{id}/REPORT.md'
        tasks = {r['task'] for r in rows}
        base = report.read_text().split('## Reanalysis')[0]
        lines = ['## Reanalysis', '', f"Completed scored trials: {len(rows)}; infrastructure exclusions: {result['infrastructure_excluded']}. Never-solved tasks: {result['never_solved_tasks']}; always-solved tasks: {result['always_solved_tasks']}. Exposure: {result['exposure_rate']*100:.1f}%.", '', 'Rates, Wilson intervals and the original published task-bootstrap effect are in the generated evidence JSON. Exclusion and sensitivity details stay in the approved public report.', '', '| Task | Baseline passes / runs | Skill passes / runs |', '| --- | --- | --- |']
        for task in sorted(tasks):
            cells=[]
            for arm in arms:
                group=[r for r in rows if r['task']==task and r['arm']==arm]
                cells.append(f"{sum(r['reward']==1 for r in group)}/{len(group)}")
            lines.append('| '+task+' | '+' | '.join(cells)+' |')
        lines += ['', '### Recorded failure taxonomy', '']
        exceptions = {}
        for r in all_rows:
            if r.get('exception'):
                key=r['exception']; exceptions[key]=exceptions.get(key,0)+1
        lines += [f'- {key}: {value} records.' for key,value in sorted(exceptions.items())]
        if id=='personal-skills':
            failed={}
            for r in rows:
                for check,value in r['checks'].items():
                    if not value: failed[check]=failed.get(check,0)+1
            lines += ['', 'Failed check counts (task diagnostics and private values omitted):', '']
            lines += [f'- {key}: {value}.' for key,value in sorted(failed.items())]
        else:
            lines += ['', 'Task-specific failure explanations and verifier-coupling sensitivity are in the linked approved public report; exceptions alone do not describe task failures.']
        report.write_text(base+'\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lanes-root', type=Path)
    parser.add_argument('--site-output', type=Path)
    args = parser.parse_args()
    if args.lanes_root:
        # Stage and validate every source before changing any tracked evidence.
        sources = []
        for id, page in PUBLISHED.items():
            source = args.lanes_root/'bench-publish/site/benchmarks'/page
            validate_finished(id, source)
            approved = read(ROOT/'data/approved-inputs.json')[id]
            for name in ('summary.json', 'trials.jsonl'):
                if hashlib.sha256((source/name).read_bytes()).hexdigest() != approved[name]:
                    raise ValueError('Finished source changed; review and update approved-inputs.json before import')
            sources.append((id, source))
        for id, source in sources:
            for name in ('summary.json', 'trials.jsonl'):
                (ROOT/f'studies/{id}/results'/name).write_bytes((source/name).read_bytes())
    export, markdown = build()
    refresh_reports(export)
    dump(ROOT/'data/benchmarks.json', export)
    site = project(export, ROOT)
    dump(ROOT/'data/site-benchmarks.json', site)
    (ROOT/'STUDIES.md').write_text(markdown)
    paths = sorted(p for folder in ('studies', 'third-party') for p in (ROOT/folder).rglob('*') if p.is_file())
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    dump(ROOT/'data/export-manifest.json', manifest)
    if args.site_output:
        dump(args.site_output, site)
    print(f"Exported {len(export['studies'])} Edge studies, {len(export['third_party'])} credited source rows, {len(export['by_skill'])} skill associations")

if __name__ == '__main__':
    main()
