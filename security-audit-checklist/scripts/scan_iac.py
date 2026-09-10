#!/usr/bin/env python3
"""Quick regex scanner for common IaC misconfigurations in Terraform, CloudFormation, and Dockerfiles."""

import argparse
import os
import re
import sys
from pathlib import Path

RULES = {
    "terraform": [
        ("S3 bucket public access", re.compile(r"acl\s*=\s*\"public-read\""), "critical"),
        ("S3 bucket public access (variant)", re.compile(r"acl\s*=\s*\"public-read-write\""), "critical"),
        ("Security group open to world", re.compile(r"cidr_blocks\s*=\s*\[\"0\.0\.0\.0/0\"\]"), "critical"),
        ("Security group open to world (IPv6)", re.compile(r"ipv6_cidr_blocks\s*=\s*\[\"::/0\"\]"), "critical"),
        ("Unencrypted storage", re.compile(r"encrypted\s*=\s*false"), "critical"),
        ("Hardcoded password", re.compile(r"password\s*=\s*\"[^$\{]"), "critical"),
        ("Hardcoded secret key", re.compile(r"secret_key\s*=\s*\"[^$\{]"), "critical"),
        ("IMDSv1 enabled", re.compile(r"http_tokens\s*=\s*\"optional\""), "warning"),
        ("Default VPC used", re.compile(r"default\s*=\s*true.*vpc"), "warning"),
    ],
    "cloudformation": [
        ("S3 public read ACL", re.compile(r"AccessControl:\s*PublicRead"), "critical"),
        ("S3 public read-write ACL", re.compile(r"AccessControl:\s*PublicReadWrite"), "critical"),
        ("Open security group ingress", re.compile(r"CidrIp:\s*0\.0\.0\.0/0"), "critical"),
        ("Open security group ingress (IPv6)", re.compile(r"CidrIpv6:\s*::/0"), "critical"),
        ("Unencrypted EBS/RDS", re.compile(r"Encrypted:\s*false"), "critical"),
        ("No deletion protection", re.compile(r"DeletionProtection:\s*false"), "warning"),
    ],
    "dockerfile": [
        ("Running as root", re.compile(r"^USER\s+root", re.MULTILINE), "warning"),
        ("No USER directive", re.compile(r"^(?!.*\bUSER\b).*$", re.MULTILINE), "info"),  # heuristic only
        ("Hardcoded secret in ENV", re.compile(r"ENV\s+\w*(SECRET|KEY|TOKEN|PASSWORD)\w*\s*=\s*[^$]"), "critical"),
        ("Hardcoded secret in ARG", re.compile(r"ARG\s+\w*(SECRET|KEY|TOKEN|PASSWORD)\w*\s*=\s*[^$]"), "critical"),
        ("Using latest tag", re.compile(r"FROM\s+[^:\s]+\s*(#.*)?$", re.MULTILINE), "warning"),
        ("curl | bash pattern", re.compile(r"curl.*\|.*(bash|sh)"), "warning"),
    ],
    "kubernetes": [
        ("Privileged container", re.compile(r"privileged:\s*true"), "critical"),
        ("Host network", re.compile(r"hostNetwork:\s*true"), "critical"),
        ("Host PID", re.compile(r"hostPID:\s*true"), "critical"),
        ("Host IPC", re.compile(r"hostIPC:\s*true"), "critical"),
        ("Default service account token mounted", re.compile(r"automountServiceAccountToken:\s*true"), "warning"),
        ("Run as root", re.compile(r"runAsUser:\s*0"), "critical"),
        ("AllowPrivilegeEscalation true", re.compile(r"allowPrivilegeEscalation:\s*true"), "critical"),
        ("No resource limits", re.compile(r"resources:\s*\{\}"), "warning"),
        ("Hardcoded secret in env", re.compile(r"value:\s*\"[A-Za-z0-9_\-]{16,}\""), "critical"),
    ],
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", ".next", ".turbo", ".cache", ".mypy_cache", ".egg-info",
}


def should_scan(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    return True


def classify_file(path: Path) -> str | None:
    name = path.name.lower()
    if name.endswith(".tf") or name.endswith(".tfvars"):
        return "terraform"
    if name.endswith((".yml", ".yaml", ".json")):
        text = path.read_text(errors="ignore").lower()
        if "awstemplateformatversion" in text or "resources:" in text:
            if "aws::" in text or "awstemplateformatversion" in text:
                return "cloudformation"
            if "kind:" in text and ("deployment" in text or "pod" in text or "service" in text):
                return "kubernetes"
    if name.startswith("dockerfile") or name.endswith(".dockerfile"):
        return "dockerfile"
    if "kind:" in path.read_text(errors="ignore") and any(k in path.read_text(errors="ignore") for k in ("Deployment", "Pod", "Service", "Ingress")):
        return "kubernetes"
    return None


def scan_file(path: Path) -> list[dict]:
    findings = []
    ftype = classify_file(path)
    if not ftype:
        return findings
    rules = RULES.get(ftype, [])
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings
    for name, pattern, severity in rules:
        for match in pattern.finditer(text):
            line_num = text[: match.start()].count("\n") + 1
            # Dockerfile USER heuristic: only flag if no USER at all
            if name == "No USER directive":
                if "USER " in text:
                    continue
                line_num = text.count("\n")  # flag at EOF
            # Skip lines that look like comments or examples
            line_text = text.splitlines()[line_num - 1] if line_num <= len(text.splitlines()) else ""
            lower_line = line_text.lower()
            if any(p in lower_line for p in ("# example", "# placeholder", "# your_", "changeme", "example.com")):
                continue
            findings.append({
                "file": str(path),
                "line": line_num,
                "type": name,
                "severity": severity,
                "ftype": ftype,
                "match": line_text.strip()[:80],
            })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan IaC files for common misconfigurations.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--severity", choices=["info", "warning", "critical"], default="info",
                        help="Minimum severity to report")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1

    severity_order = {"info": 0, "warning": 1, "critical": 2}
    min_level = severity_order[args.severity]

    all_findings: list[dict] = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if not should_scan(item):
            continue
        all_findings.extend(scan_file(item))

    # Filter and deduplicate
    seen = set()
    filtered = []
    for f in all_findings:
        if severity_order[f["severity"]] < min_level:
            continue
        key = (f["file"], f["line"], f["type"])
        if key in seen:
            continue
        seen.add(key)
        filtered.append(f)

    if not filtered:
        print("No obvious IaC misconfigurations found. ✅")
        return 0

    for f in filtered:
        icon = "🔴" if f["severity"] == "critical" else "🟡" if f["severity"] == "warning" else "⚪"
        print(f"{icon} [{f['ftype']}] {f['file']}:{f['line']}  {f['type']}")
        if f["match"]:
            print(f"    → {f['match']}")

    print(f"\nTotal findings: {len(filtered)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
