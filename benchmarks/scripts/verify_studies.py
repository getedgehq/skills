#!/usr/bin/env python3
"""Reconcile counts, deterministic generated artifacts and exported privacy boundary."""
import hashlib
import json
from sync_studies import ROOT, build, safe_bytes, PUBLISHED, validate_finished
from site_contract import project

def verify():
    export, markdown = build()
    assert export == json.loads((ROOT/'data/benchmarks.json').read_text()), 'Generated JSON is stale'
    site=project(export, ROOT)
    assert site == json.loads((ROOT/'data/site-benchmarks.json').read_text()), 'Site contract is stale'
    assert sum(r['source']=='Edge' for r in site['models']) == len(PUBLISHED), 'Completed model row missing'
    assert markdown == (ROOT/'STUDIES.md').read_text(), 'Register is stale'
    manifest = json.loads((ROOT/'data/export-manifest.json').read_text())
    for extra in ('data/skill-packages.json', 'data/benchmarks.json', 'data/site-benchmarks.json'):
        safe_bytes((ROOT/extra).read_bytes())
    files = sorted(p for folder in ('studies', 'third-party') for p in (ROOT/folder).rglob('*') if p.is_file())
    assert set(manifest) == {p.relative_to(ROOT).as_posix() for p in files}, 'Manifest file set differs'
    for p in files:
        safe_bytes(p.read_bytes())
        assert hashlib.sha256(p.read_bytes()).hexdigest() == manifest[p.relative_to(ROOT).as_posix()]
    for id in PUBLISHED:
        approved=json.loads((ROOT/'data/approved-inputs.json').read_text())[id]
        for name,digest in approved.items():
            assert hashlib.sha256((ROOT/f'studies/{id}/results'/name).read_bytes()).hexdigest()==digest, 'Unapproved source bytes'
        _, rows, _, arms = validate_finished(id, ROOT/f'studies/{id}/results')
        print(id, {a: {'passes': sum(r['reward'] == 1 for r in rows if r['arm']==a), 'trials': sum(r['arm']==a for r in rows)} for a in arms})
    for s in export['studies']:
        base = ROOT/'studies'/s['id']
        for p in ('PROTOCOL.md', 'runner.md', 'REPORT.md', 'tasks/manifest.json', 'results/summary.json', 'results/trials.jsonl'):
            assert (base/p).is_file(), p
        if s['id'] not in PUBLISHED:
            assert s['result'] is None
            assert not (base/'results/trials.jsonl').read_text()
    for r in export['third_party']:
        assert r['url'].startswith('https://') and r['publisher']
        if r['baseline_pct'] is not None:
            assert abs(r['treatment_pct']-r['baseline_pct']-r['lift_pp']) < 0.11
    print(f'PASS: {len(files)} approved study/source files; hashes, privacy patterns, counts, pending nulls and site export reconciled')

if __name__ == '__main__':
    verify()
