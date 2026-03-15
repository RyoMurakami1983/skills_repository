#!/usr/bin/env python3
"""Validate unified skill structure using Critical and Recommended checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class CheckResult:
    id: str
    label: str
    passed: bool
    details: str = ""


@dataclass
class ValidationReport:
    file_path: str
    level: str
    critical: list[CheckResult]
    recommended: list[CheckResult]
    critical_passed: bool
    recommended_pass_count: int
    recommended_total: int


def extract_frontmatter(content: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    lines = match.group(1).splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        plain = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not plain:
            i += 1
            continue
        key = plain.group(1)
        value = plain.group(2).strip()
        if value in {">", "|", ">-", "|-"}:
            folded: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                folded.append(lines[i].strip())
                i += 1
            data[key] = " ".join(part for part in folded if part).strip()
            continue
        data[key] = value.strip('"\'')
        i += 1
    return data


def get_section(content: str, heading: str) -> str | None:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"^##\s+.+$", content[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(content)
    return content[start:end].strip()


def bullet_lines(section: str | None) -> list[str]:
    if not section:
        return []
    bullets: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "+ ")):
            bullets.append(re.sub(r"^[-*+]\s+", "", stripped))
    return bullets


def has_workflow_or_router(content: str) -> bool:
    return any(
        re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        for pattern in (
            r"^##\s+Workflow:",
            r"^##\s+Decision Table$",
            r"^###\s+Step\s+\d+",
        )
    )


def starts_with_verb(text: str) -> bool:
    first_word = re.match(r"^([A-Za-z][A-Za-z-]*)", text)
    return bool(first_word and first_word.group(1).lower() not in {"the", "a", "an", "this"})


def has_code_blocks(content: str) -> bool:
    return "```" in content


def fenced_blocks(content: str) -> Iterable[str]:
    return re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", content, re.DOTALL)


def validate(path: Path, level: str) -> ValidationReport:
    content = path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    folder_name = path.parent.name
    description = frontmatter.get("description", "")
    when_section = get_section(content, "When to Use This Skill")
    bullets = bullet_lines(when_section)
    quick_reference = get_section(content, "Quick Reference")
    pitfalls = get_section(content, "Pitfalls")
    references_dir = path.parent / "references"

    critical = [
        CheckResult("C1", "Frontmatter has name and description", {"name", "description"} <= frontmatter.keys()),
        CheckResult("C2", "name matches directory", frontmatter.get("name") == folder_name, f"directory={folder_name}"),
        CheckResult("C3", "description contains Use when", "Use when" in description, description),
        CheckResult("C4", "When to Use section exists", when_section is not None),
        CheckResult("C5", "Workflow or router section exists", has_workflow_or_router(content)),
    ]

    recommended = [
        CheckResult("R1", "When to Use has 3-8 bullets", 3 <= len(bullets) <= 8, f"count={len(bullets)}"),
        CheckResult("R2", "When to Use bullets are verb-led", bool(bullets) and all(starts_with_verb(b) for b in bullets)),
        CheckResult("R3", "Explains why", "why" in content.lower() or "because" in content.lower()),
        CheckResult("R4", "Pitfalls section exists", pitfalls is not None),
        CheckResult("R5", "SKILL.md stays compact", len(content.splitlines()) <= 220, f"lines={len(content.splitlines())}"),
        CheckResult("R6", "references/ exists for overflow", references_dir.exists()),
        CheckResult("R7", "Links to related resources", "Related Skills" in content or "Shared Resources" in content),
        CheckResult("R8", "Quick reference or decision table exists", quick_reference is not None or "Decision Table" in content),
        CheckResult("R9", "Code blocks look non-empty", (not has_code_blocks(content)) or all(block.strip() for block in fenced_blocks(content))),
        CheckResult("R10", "Japanese reference exists", (references_dir / "SKILL.ja.md").exists()),
    ]

    critical_passed = all(check.passed for check in critical)
    if level.upper() == "L1":
        recommended = []

    return ValidationReport(
        file_path=str(path),
        level=level.upper(),
        critical=critical,
        recommended=recommended,
        critical_passed=critical_passed,
        recommended_pass_count=sum(1 for check in recommended if check.passed),
        recommended_total=len(recommended),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate unified skill files")
    parser.add_argument("path", help="Path to SKILL.md")
    parser.add_argument("--level", choices=["L1", "L2"], default="L2")
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser.parse_args()


def print_text(report: ValidationReport) -> None:
    print(f"Validation: {report.file_path}")
    print(f"Level: {report.level}")
    print(f"Critical: {'PASS' if report.critical_passed else 'FAIL'}")
    for check in report.critical:
        mark = "PASS" if check.passed else "FAIL"
        print(f"  [{mark}] {check.id} {check.label}")
    if report.recommended:
        print(f"Recommended: {report.recommended_pass_count}/{report.recommended_total}")
        for check in report.recommended:
            mark = "PASS" if check.passed else "WARN"
            print(f"  [{mark}] {check.id} {check.label}")


def main() -> int:
    args = parse_args()
    report = validate(Path(args.path), args.level)
    if args.json_output:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if report.critical_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
