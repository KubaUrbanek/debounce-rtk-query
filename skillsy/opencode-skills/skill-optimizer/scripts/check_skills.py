#!/usr/bin/env python3
"""Perform deterministic structural checks on OpenCode Agent Skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SUPPORTED_KEYS = {"name", "description", "license", "compatibility", "metadata"}


def discover(inputs: list[str]) -> list[Path]:
    if inputs:
        candidates: list[Path] = []
        for raw in inputs:
            path = Path(raw).expanduser()
            if path.is_file():
                candidates.append(path)
            elif path.is_dir() and (path / "SKILL.md").is_file():
                candidates.append(path / "SKILL.md")
            elif path.is_dir():
                candidates.extend(path.rglob("SKILL.md"))
            else:
                print(f"warning: target does not exist: {path}", file=sys.stderr)
        return sorted(set(item.resolve() for item in candidates))

    roots = [
        Path.cwd() / ".opencode/skills",
        Path.cwd() / ".agents/skills",
        Path.cwd() / ".claude/skills",
        Path.home() / ".config/opencode/skills",
        Path.home() / ".agents/skills",
        Path.home() / ".claude/skills",
    ]
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            found.extend(root.glob("*/SKILL.md"))
    return sorted(set(item.resolve() for item in found))


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    issues: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["missing opening YAML frontmatter delimiter"]
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, text, ["missing closing YAML frontmatter delimiter"]

    data: dict[str, Any] = {}
    active_map: str | None = None
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if active_map == "metadata" and ":" in line:
                key, value = line.strip().split(":", 1)
                metadata = data.setdefault("metadata", {})
                metadata[key.strip()] = scalar(value)
            else:
                issues.append(f"line {number}: unsupported multiline or nested frontmatter")
            continue
        if ":" not in line:
            issues.append(f"line {number}: invalid frontmatter entry")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        active_map = key if key == "metadata" else None
        if key == "metadata" and not value.strip():
            data[key] = {}
        else:
            data[key] = scalar(value)
    return data, "\n".join(lines[end + 1 :]), issues


def finding(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def check(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, parser_issues = parse_frontmatter(text)
    findings = [finding("error", "frontmatter", issue) for issue in parser_issues]
    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name:
        findings.append(finding("error", "name-required", "frontmatter name is required"))
    else:
        if not NAME_PATTERN.fullmatch(name):
            findings.append(finding("error", "name-format", "name must use lowercase alphanumerics with single hyphens"))
        if name != path.parent.name:
            findings.append(finding("error", "name-directory", f"name `{name}` does not match directory `{path.parent.name}`"))

    if not isinstance(description, str) or not description.strip():
        findings.append(finding("error", "description-required", "frontmatter description is required"))
    elif len(description) > 1024:
        findings.append(finding("error", "description-length", "description exceeds OpenCode's 1024-character limit"))
    elif len(description) < 25:
        findings.append(finding("warning", "description-specificity", "description may be too short to discriminate activation"))

    for key in frontmatter:
        if key not in SUPPORTED_KEYS:
            findings.append(finding("warning", "frontmatter-unknown", f"OpenCode ignores unknown frontmatter key `{key}`"))

    if re.search(r"\b(TODO|FIXME|TBD)\b|\[TODO", text, flags=re.IGNORECASE):
        findings.append(finding("error", "placeholder", "unfinished placeholder found"))
    if not body.strip():
        findings.append(finding("error", "body-empty", "skill body is empty"))
    if len(body.splitlines()) > 500:
        findings.append(finding("warning", "body-large", "SKILL.md exceeds 500 body lines; consider progressive disclosure"))

    for target in LINK_PATTERN.findall(body):
        target = target.strip().split("#", 1)[0]
        if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, flags=re.IGNORECASE):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            findings.append(finding("error", "link-broken", f"linked local resource does not exist: {target}"))

    return {
        "path": str(path),
        "name": name,
        "description": description,
        "line_count": len(text.splitlines()),
        "findings": findings,
    }


def render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    for skill in report["skills"]:
        lines.append(f"{skill['path']}: {skill['name'] or '<unknown>'}")
        if not skill["findings"]:
            lines.append("  OK")
        for item in skill["findings"]:
            lines.append(f"  {item['level'].upper():7} {item['code']}: {item['message']}")
    summary = report["summary"]
    lines.append(f"Checked {summary['skills']} skill(s): {summary['errors']} error(s), {summary['warnings']} warning(s)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="*", help="SKILL.md files, skill folders, or roots to scan")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    paths = discover(args.targets)
    if not paths:
        print("No SKILL.md files found", file=sys.stderr)
        return 2

    skills = [check(path) for path in paths]
    counts = Counter(skill.get("name") for skill in skills if skill.get("name"))
    for skill in skills:
        name = skill.get("name")
        if name and counts[name] > 1:
            skill["findings"].append(finding("warning", "name-duplicate", f"skill name `{name}` appears {counts[name]} times in this scan"))

    errors = sum(item["level"] == "error" for skill in skills for item in skill["findings"])
    warnings = sum(item["level"] == "warning" for skill in skills for item in skill["findings"])
    report = {"skills": skills, "summary": {"skills": len(skills), "errors": errors, "warnings": warnings}}
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else render_text(report))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
