#!/usr/bin/env python3
"""Build the self-contained package the person keeps: the evaluated base model + chosen adapter,
style card, memory, chat program, launchers and a private venv. No fusing or re-quantizing:
what ships is exactly what was evaluated.

  python package.py --base <snapshot dir> --adapter runs/v1/adapter --system-file system.md --card style-card.md --memory memory.md \
      --out ~/my-model/package --backend hf --license-file <model LICENSE> [--venv]
"""
import argparse
import json
import os
import shutil
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HF_REQ = ["torch==2.14.1", "transformers==5.18.0", "peft==0.21.2", "accelerate", "safetensors"]
MLX_REQ = ["mlx-lm==0.32.0"]

MAC = """#!/bin/bash
cd "$(dirname "$0")"
export HF_HUB_OFFLINE=1 UV_OFFLINE=1
{run} chat.py
"""
SH = """#!/bin/bash
cd "$(dirname "$0")"
export HF_HUB_OFFLINE=1
{run} chat.py
"""
BAT = """@echo off
cd /d "%~dp0"
set HF_HUB_OFFLINE=1
.venv\\Scripts\\python.exe chat.py
pause
"""
README = """# Your model

This folder is your own small writing helper. It runs on this computer and does not need the internet.

**To use it:** double-click "Talk to my model" ({launcher}). Paste a message you received, press Enter,
and it writes a draft in your style. Always read a draft before you send it.

- If a draft is not how you would say it, type `/better` and then your version. Next time you ask Claude
  to "update my model", it learns from these.
- `/forget some words` marks old examples with those words to be removed at the next update.
- What it knows about you is in `memory.md`, how you write in `style-card.md`. To change either, ask Claude to
  "update my model" so the change is checked before it is used (the helper reads `system.md`).

**Private:** this folder contains what was learned from your writing. Do not share or upload it.
To delete everything, delete the whole `my-model` folder (see DELETE.md).

The base model is {model_name}; its licence is in MODEL-LICENSE.txt.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="local snapshot dir of the pinned base model")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--system-file", required=True, help="the exact system.md used in training and the check")
    ap.add_argument("--card", required=True)
    ap.add_argument("--memory")
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", choices=["hf", "mlx"], default="hf")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--license-file", required=True)
    ap.add_argument("--model-name", default="")
    ap.add_argument("--work-dir", help="where /better feedback is saved (default: next to the package)")
    ap.add_argument("--venv", action="store_true", help="create package/.venv with pinned packages (hf backend)")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    shutil.copytree(a.base, os.path.join(a.out, "base"), dirs_exist_ok=True, symlinks=False)
    shutil.copytree(a.adapter, os.path.join(a.out, "adapter"), dirs_exist_ok=True)
    shutil.copy(a.system_file, os.path.join(a.out, "system.md"))
    shutil.copy(a.card, os.path.join(a.out, "style-card.md"))
    if a.memory:
        shutil.copy(a.memory, os.path.join(a.out, "memory.md"))
    shutil.copy(a.license_file, os.path.join(a.out, "MODEL-LICENSE.txt"))
    for f in ("chat.py", "generate.py", "common.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(a.out, f))
    json.dump({"base": "base", "adapter": "adapter", "backend": a.backend, "device": a.device,
               "work_dir": os.path.abspath(a.work_dir or a.out)}, open(os.path.join(a.out, "package.json"), "w"), indent=1)
    req = HF_REQ if a.backend == "hf" else MLX_REQ
    open(os.path.join(a.out, "requirements.lock"), "w").write("\n".join(req) + "\n")
    open(os.path.join(a.out, ".gitignore"), "w").write("*\n")

    if a.backend == "mlx":
        run = 'uv run --offline --python 3.12 --with "mlx-lm==0.32.0" python'
        launchers = {"Talk to my model.command": MAC.format(run=run)}
        name = "Talk to my model.command"
    else:
        launchers = {"Talk to my model.sh": SH.format(run=".venv/bin/python"), "Talk to my model.bat": BAT}
        name = "Talk to my model.sh / .bat"
    for fn, body in launchers.items():
        p = os.path.join(a.out, fn)
        open(p, "w", newline="\r\n" if fn.endswith(".bat") else "\n").write(body)
        os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP)
    open(os.path.join(a.out, "README.md"), "w").write(README.format(launcher=name, model_name=a.model_name or a.base))
    open(os.path.join(a.out, "DELETE.md"), "w").write(
        "To delete your model: delete the whole `my-model` folder. Also delete the chats or Project files in Claude "
        "where you pasted or uploaded examples (claude.ai: open the chat or Project, menu, Delete).\n")

    if a.venv and a.backend == "hf":
        vd = os.path.join(a.out, ".venv")
        subprocess.check_call([sys.executable, "-m", "venv", vd])
        pip = [os.path.join(vd, "bin", "pip"), "install", "-q"]
        subprocess.check_call(pip + ["--index-url", "https://download.pytorch.org/whl/cpu", HF_REQ[0]])
        subprocess.check_call(pip + HF_REQ[1:])
    print(json.dumps({"package": a.out, "launchers": list(launchers)}))


if __name__ == "__main__":
    main()
