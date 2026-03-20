#!/usr/bin/env python3
"""top-level skill からコンパクトな index 断片を生成する。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_frontmatter(path: Path) -> dict[str, str]:
    """SKILL.md の frontmatter を抽出する。"""
    content = path.read_text(encoding="utf-8")
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


def build_index(skills_root: Path) -> str:
    """skills ディレクトリ配下の一覧を Markdown 断片として組み立てる。"""
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
    """CLI 引数を受け取り、skill index を stdout またはファイルへ出力する。"""
    parser = argparse.ArgumentParser(description="Markdown の skill index 断片を生成する")
    parser.add_argument("--skills-root", default="skills", help="top-level skill を含むディレクトリ")
    parser.add_argument("--output", help="stdout の代わりにこのファイルへ書き出す")
    args = parser.parse_args()

    rendered = build_index(Path(args.skills_root))
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
