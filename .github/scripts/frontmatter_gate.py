#!/usr/bin/env python3
"""Fail if any SKILL.md front matter is not valid YAML with a name and a description.

Usage (from the repository root):
  python .github/scripts/frontmatter_gate.py

Why this exists. `agent-infra-fixer` shipped with "The rule: infra failures ..." in an unquoted
description. YAML reads ": " as a nested mapping, and `npx skills add` skipped the bundle with a
warning while installing the rest, so the install looked successful. A strict parse in CI catches it.
Duplicate keys fail too: PyYAML keeps the last one silently, while js-yaml (what `npx skills` reads
front matter with) rejects the block.
"""
import glob
import os
import sys

import yaml



class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        seen = set()
        for k, _ in node.value:
            key = self.construct_object(k, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", k.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    failed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "*", "SKILL.md"))):
        slug = os.path.basename(os.path.dirname(path))
        text = open(path, encoding="utf-8").read()
        parts = text.split("---\n", 2)
        if not text.startswith("---\n") or len(parts) < 3:
            print(f"FAIL {slug}: no front matter block")
            failed += 1
            continue
        try:
            meta = yaml.load(parts[1], Loader=UniqueKeyLoader)
        except yaml.YAMLError as e:
            print(f"FAIL {slug}: {str(e).splitlines()[0]}")
            failed += 1
            continue
        missing = [k for k in ("name", "description") if not isinstance(meta, dict) or not meta.get(k)]
        if missing:
            print(f"FAIL {slug}: missing {', '.join(missing)}")
            failed += 1
    print(f"{failed} SKILL.md front matter block(s) failed", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
