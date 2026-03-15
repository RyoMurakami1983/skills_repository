#!/usr/bin/env python3
"""Generate a compact skills index snippet from top-level skills."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip('"\'')
    return data


def build_index(skills_root: Path) -> str:
    rows: list[str] = [
        "<!-- BEGIN SKILL-INDEX -->",
        "# Agent Guidance: skills_repository",
        "",
        "Routing (invoke by name)",
    ]
    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        frontmatter = extract_frontmatter(skill_dir / "SKILL.md")
        name = frontmatter.get("name", skill_dir.name)
        description = frontmatter.get("description", "").split(".")[0]
        rows.append(f"- `{name}`: {description}")
    rows.append("<!-- END SKILL-INDEX -->")
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a markdown skills index snippet")
    parser.add_argument("--skills-root", default="skills", help="Directory containing top-level skills")
    parser.add_argument("--output", help="Write the snippet to this file instead of stdout")
    args = parser.parse_args()

    rendered = build_index(Path(args.skills_root))
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
