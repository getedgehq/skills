#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, sys, tempfile, json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def run_cli(text:str):
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'prompt.md'; out=Path(td)/'out.json'; p.write_text(text)
        subprocess.check_call([sys.executable,str(HERE/'audit_prompt.py'),str(p),'--out',str(out)])
        return json.loads(out.read_text())

def main():
    r=run_cli('You are an agent. Always act. Never act before asking. Be concise but extremely detailed. Think step by step.')
    types={x['type'] for x in r['findings']}
    assert 'possible-contradiction' in types
    assert 'cot-request' in types
    assert r['diagnostic_only'] is True
    print('system prompt audit tests passed')
if __name__=='__main__': main()

