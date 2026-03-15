#!/usr/bin/env python3
"""Create one or more skill skeletons from the unified template."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_ROOT / "_foundation" / "TEMPLATE.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create skill skeletons from the unified template")
    parser.add_argument("--name", help="Skill directory name (kebab-case)")
    parser.add_argument("--description", help="Frontmatter description")
    parser.add_argument("--title", help="Display title for the skill")
    parser.add_argument("--compatibility", default="", help="Optional compatibility text")
    parser.add_argument("--output-root", default="skills", help="Directory where skills are created")
    parser.add_argument("--suite", help="Path to suite JSON describing multiple skills")
    return parser.parse_args()


def validate_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"Invalid skill name '{name}'. Use kebab-case.")


def render_template(template: str, *, name: str, description: str, title: str, compatibility: str) -> str:
    rendered = template
    replacements = {
        "<context>-<verb>-<object>": name,
        "<What this skill does>. Use when <scenario 1>, <scenario 2>, or <scenario 3>, even if the user describes the workflow without saying \"skill\".": description,
        "<optional tools, runtime, or platform constraints>": compatibility or "",
        "<Skill Title>": title,
        "<Explain why this skill exists in 1-2 sentences.>": "Explain why this skill exists and trim placeholders before publishing.",
        "<Verb-led scenario 1>": "Replace this placeholder with a real trigger",
        "<Verb-led scenario 2>": "Add a second real scenario before validation",
        "<Verb-led scenario 3>": "Add a third real scenario before validation",
        "<Workflow Name>": "Replace Me",
        "<Action>": "Replace Me",
        "<Pitfall>": "Placeholder",
        "<How to avoid it and why the safer choice works better.>": "Replace with a real failure mode.",
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def build_ja_stub(name: str, description: str, title: str, compatibility: str) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"compatibility: {compatibility}\n"
        "---\n\n"
        f"# {title}\n\n"
        "日本語版は必要になった段階で追加してください。\n"
    )


def create_skill(output_root: Path, template: str, item: dict[str, str]) -> Path:
    name = item["name"]
    validate_name(name)
    description = item["description"]
    title = item.get("title") or name.replace("-", " ").title()
    compatibility = item.get("compatibility", "")

    skill_dir = output_root / name
    if skill_dir.exists():
        raise FileExistsError(f"Destination already exists: {skill_dir}")

    (skill_dir / "references").mkdir(parents=True, exist_ok=False)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "assets").mkdir()

    (skill_dir / "SKILL.md").write_text(
        render_template(
            template,
            name=name,
            description=description,
            title=title,
            compatibility=compatibility,
        ),
        encoding="utf-8",
    )
    (skill_dir / "references" / "SKILL.ja.md").write_text(
        build_ja_stub(name, description, title, compatibility),
        encoding="utf-8",
    )
    return skill_dir


def load_suite(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("skills")
    else:
        items = data
    if not isinstance(items, list) or not items:
        raise ValueError("Suite JSON must be a non-empty array or an object with a 'skills' array.")
    normalized: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict) or "name" not in item or "description" not in item:
            raise ValueError("Each suite item must contain 'name' and 'description'.")
        normalized.append({k: str(v) for k, v in item.items()})
    return normalized


def main() -> int:
    args = parse_args()
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    if args.suite:
        items = load_suite(Path(args.suite))
    else:
        if not args.name or not args.description:
            print("ERROR: --name and --description are required unless --suite is used.", file=sys.stderr)
            return 1
        items = [
            {
                "name": args.name,
                "description": args.description,
                "title": args.title or args.name.replace("-", " ").title(),
                "compatibility": args.compatibility,
            }
        ]

    created: list[Path] = []
    for item in items:
        created.append(create_skill(output_root, template, item))

    for path in created:
        print(f"Created {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
