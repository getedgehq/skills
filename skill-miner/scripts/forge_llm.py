#!/usr/bin/env python3
"""Shared model-call helper for skill-forge stages.

Tries claude first (headless), falls back to codex exec on rate-limit (429)
or CLI failure. Returns plain text output. Forcing an engine: FORGE_ENGINE=claude|codex.
"""
import json
import os
import subprocess
import sys


def _claude(prompt, model, timeout):
    out = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--output-format", "json"],
        capture_output=True, text=True, timeout=timeout,
    )
    if out.returncode != 0:
        raise RuntimeError(f"claude rc={out.returncode}: {out.stderr[:400]}")
    try:
        payload = json.loads(out.stdout)
    except ValueError:
        raise RuntimeError(f"claude non-JSON: {out.stdout[:300]}")
    if payload.get("api_error_status") == 429 or payload.get("is_error"):
        raise RuntimeError(f"claude api error: {payload.get('result', '')[:300]}")
    return payload.get("result", "")


def _codex(prompt, model, timeout):
    cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
    if model:
        cmd = ["codex", "exec", "--skip-git-repo-check", "-m", model, prompt]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError(f"codex rc={out.returncode}: {out.stderr[:400]}")
    return out.stdout


def call_model(prompt, model=None, timeout=600):
    engine = os.environ.get("FORGE_ENGINE", "auto")
    errors = []
    order = {"claude": (_claude, model or "claude-sonnet-4-5"),
             "codex": (_codex, os.environ.get("FORGE_CODEX_MODEL"))}
    seq = [engine] if engine in order else ["claude", "codex"]
    for name in seq:
        fn, m = order[name]
        try:
            return fn(prompt, m, timeout), name
        except (RuntimeError, subprocess.TimeoutExpired, OSError) as e:
            errors.append(f"{name}: {e}")
    sys.exit("all engines failed:\n" + "\n".join(errors))
