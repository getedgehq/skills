#!/usr/bin/env python3
"""Shared model-call helper for skill-forge stages.

Tries claude first (headless), falls back to codex exec on rate-limit (429)
or CLI failure. Returns plain text output. Forcing an engine: FORGE_ENGINE=claude|codex.
"""
import json
import os
import subprocess
import sys


def _with_commas(text, limit=8):
    """text with the commas a model left out between two members put back.

    A reply whose members each sit on their own line loses a comma now and then, and
    the decoder reports it as "Expecting ',' delimiter" pointing at the first
    character of the next member. Repairing only that exact shape is what keeps this
    from inventing anything: the one character inserted is a separator, never a value,
    and the members on either side are the ones the model wrote.

    The pointed-at character has to open a member, which inside an object means a
    quote. That test keeps the repair on the one shape that was observed rather than
    on every reply that happens to raise this message: a missing separator anywhere
    else, inside a list of numbers say, comes back unchanged and fails in the caller.
    Narrow on purpose, since every shape this learns to rewrite is a shape it can get
    wrong quietly.

    What it does not do is tell this apart from an unescaped quote inside a string,
    which raises the same message. It does not have to. A comma inserted mid-string
    leaves something no decoder will accept either, so that reply still fails - just
    not because of anything here.
    """
    dec = json.JSONDecoder(strict=False)
    for _ in range(limit):
        try:
            dec.raw_decode(text)
            return text
        except json.JSONDecodeError as e:
            if e.msg != "Expecting ',' delimiter" or not text[e.pos:e.pos + 1] == '"':
                return text
            text = text[:e.pos] + "," + text[e.pos:]
    return text


def first_object(text):
    """The first complete JSON object in a model reply.

    Slicing from the first "{" to the last "}" is the usual shortcut and it fails on
    exactly the reply this has to survive: a model that answers with the object and
    then keeps going, a second object or a sentence with a brace in it, produces a
    slice that is valid JSON followed by more, and json.loads rejects the whole thing
    with "Extra data". Two real candidates scored 0.00 that way, which reads in the
    output as a judgement the model never made (PR #22). raw_decode stops at the end
    of the first object instead, and each later "{" is tried in case the reply opens
    with prose containing one.

    Each candidate is read twice: once strictly, and once tolerating the two
    malformations that have actually cost a score here - a literal newline inside a
    string, which the strict decoder refuses as a control character, and a missing
    comma between members. The strict read always goes first, so a reply that is
    simply valid is never touched, and the error reported on failure is the strict
    one at the first brace, which is the one worth reading.
    """
    err = None
    at = text.find("{")
    while at != -1:
        chunk = text[at:]
        for source, strict in ((chunk, True), (_with_commas(chunk), False)):
            try:
                obj, _ = json.JSONDecoder(strict=strict).raw_decode(source)
                if isinstance(obj, dict):
                    return obj
            except ValueError as e:
                err = err or e
        at = text.find("{", at + 1)
    raise ValueError(err or "no JSON object in the reply")


def _claude(prompt, model, timeout):
    out = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--output-format", "json"],
        capture_output=True, text=True, timeout=timeout,
    )
    if out.returncode != 0:
        # the JSON result carries the real cause (e.g. expired auth); stderr is often wrapper noise
        raise RuntimeError(f"claude rc={out.returncode}: {out.stdout[-400:]} {out.stderr[-300:]}")
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
    order = {"claude": (_claude, model or "claude-opus-5"),
             "codex": (_codex, os.environ.get("FORGE_CODEX_MODEL"))}
    seq = [engine] if engine in order else ["claude", "codex"]
    for name in seq:
        fn, m = order[name]
        try:
            return fn(prompt, m, timeout), name
        except (RuntimeError, subprocess.TimeoutExpired, OSError) as e:
            errors.append(f"{name}: {e}")
    sys.exit("all engines failed:\n" + "\n".join(errors))
