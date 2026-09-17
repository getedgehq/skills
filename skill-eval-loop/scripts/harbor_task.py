#!/usr/bin/env python3
"""Render a brief into a Harbor task directory.

Usage: harbor_task.py <brief.json> <out-dir>

Harbor (github.com/harbor-framework/harbor) runs an agent inside a container it
builds per trial, and injects a skill directory at trial time with --skill. That
buys the loop two things the local runner cannot give it:

  1. A second runner. run_eval.sh has to know where each CLI looks for skills
     (.claude/skills, .agents/skills, .opencode/skill) and got that wrong once
     already; Harbor's own agent classes know, and 24 of them declare
     capabilities.skills = True.
  2. Blindness by construction. In the without arm no skill is injected, so
     Trial._resolve_effective_skills_dir() returns None, _upload_injected_skills()
     returns early, and the container never receives the files at all. The local
     runner instead put both arms under one host tree and relied on the judge's
     manifest to hide the skill, which is exactly the thing that leaked.

Two properties of the generated task carry that second point, and tests pin both:

  environment.skills_dir is never set. Setting it makes the skills directory
  exist in both arms (_resolve_effective_skills_dir returns a task-level path
  whether or not anything was injected), which hands the without arm an empty
  directory the with arm has content in: a tell, and a needless one.

  The instruction is the brief's prompt verbatim. Harbor's own hello-skills
  example opens with "You have a skill installed called generate-greeting",
  which is fine for a smoke test and fatal for a blind pair. The prompt an arm
  sees may not mention skills at all, and it is byte-identical across arms.

The verifier is left to the host. judge.py already runs the brief's verify in the
arm's workdir, and a skill proven under Harbor has to be comparable to the ten
already adopted under the local runner: two implementations of the objective gate
would make the two corpora measure different things. Harbor is the substrate the
agent runs on, not a second opinion about whether it passed.
"""
import json
import os
import sys

# ubuntu:24.04 matches Harbor's own examples and carries no agent CLI: Harbor
# installs the one under test into the container itself.
DEFAULT_IMAGE = "ubuntu:24.04"

DOCKERFILE = """FROM {image}

RUN apt-get update && apt-get install -y \\
    curl ca-certificates git \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
{setup}"""

# No [environment].skills_dir: see the module docstring. artifacts pulls the
# agent's workdir back to the host, where judge.py reads it as the arm's workdir.
TASK_TOML = """schema_version = "1.1"

artifacts = [
    {{ source = "/app", destination = "app" }},
]

[task]
name = "skill-forge/{name}"
description = "skill-forge eval brief {name}"
authors = []
keywords = [ "skill-forge",]

[metadata]
difficulty = "unknown"
category = "skill-forge"
tags = [ "skill-forge",]

[verifier]
timeout_sec = 60.0

[agent]
timeout_sec = {agent_timeout}.0

[environment]
build_timeout_sec = 900.0
cpus = {cpus}
memory_mb = {memory_mb}
storage_mb = 10240
gpus = 0
mcp_servers = []
"""


def slug(brief_id):
    """A task name Harbor accepts, derived from the brief id."""
    keep = [c if (c.isalnum() or c in "-_") else "-" for c in str(brief_id).lower()]
    return "".join(keep).strip("-") or "brief"


def dockerfile(brief):
    """The task image: the brief's own setup, run at build time.

    The local runner runs brief['setup'] per arm at run time against a shared
    $FORGE_ROOT/fixtures tree. In a container there is no shared tree and no
    reason to redo the work per arm, so setup is baked into the image both arms
    are built from: identical bytes, and one less thing that can differ.
    """
    setup = (brief.get("setup") or "").strip()
    lines = "\n".join("RUN " + line for line in setup.splitlines() if line.strip())
    return DOCKERFILE.format(image=brief.get("image") or DEFAULT_IMAGE,
                             setup=lines + "\n" if lines else "")


def render(brief, out):
    os.makedirs(os.path.join(out, "environment"), exist_ok=True)
    os.makedirs(os.path.join(out, "tests"), exist_ok=True)
    name = slug(brief["id"])

    with open(os.path.join(out, "task.toml"), "w") as fh:
        fh.write(TASK_TOML.format(
            name=name,
            agent_timeout=int(brief.get("timeout_sec") or 1200),
            cpus=int(brief.get("cpus") or 2),
            memory_mb=int(brief.get("memory_mb") or 4096)))

    # Byte-identical across arms. Nothing is appended for the with arm: the only
    # difference between the two runs is Harbor's --skill flag.
    with open(os.path.join(out, "instruction.md"), "w") as fh:
        fh.write(brief["prompt"])

    with open(os.path.join(out, "environment", "Dockerfile"), "w") as fh:
        fh.write(dockerfile(brief))

    # Harbor wants a verifier; the real gate runs on the host in judge.py. This
    # one reports nothing rather than a passing score it did not check, so a
    # reward read off a Harbor job is never mistaken for our objective gate.
    with open(os.path.join(out, "tests", "test.sh"), "w") as fh:
        fh.write("#!/bin/bash\n"
                 "# The objective gate is the brief's verify, run on the host by\n"
                 "# judge.py. Reward 0 here means 'not scored', not 'failed'.\n"
                 "mkdir -p /logs/verifier\n"
                 "echo 0 > /logs/verifier/reward.txt\n")
    os.chmod(os.path.join(out, "tests", "test.sh"), 0o755)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip().splitlines()[2])
    brief = json.load(open(sys.argv[1]))
    for key in ("id", "prompt"):
        if not brief.get(key):
            sys.exit(f"brief has no {key}")
    print(render(brief, sys.argv[2]))


if __name__ == "__main__":
    main()
