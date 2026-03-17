#!/usr/bin/env python3
"""Create workflow skills, router skills, and router sub-skills from templates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_ROOT / "_foundation" / "TEMPLATE.md"
ROUTER_TEMPLATE_PATH = SKILL_ROOT / "_foundation" / "ROUTER_TEMPLATE.md"
SUB_SKILL_TEMPLATE_PATH = SKILL_ROOT / "_foundation" / "SUB_SKILL_TEMPLATE.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create workflow skills, router skills, and sub-skills")
    parser.add_argument("--name", help="Skill directory name (kebab-case)")
    parser.add_argument("--description", help="Frontmatter description")
    parser.add_argument("--title", help="Display title for the skill")
    parser.add_argument("--compatibility", default="", help="Optional compatibility text")
    parser.add_argument("--output-root", default="skills", help="Directory where skills are created")
    parser.add_argument(
        "--type",
        choices=("workflow", "router"),
        default="workflow",
        help="Skill type to create",
    )
    parser.add_argument("--sub-skills", help="Comma-separated sub-skill names for router creation")
    parser.add_argument("--add-sub-skill", help="Create one sub-skill inside an existing router")
    parser.add_argument("--router-dir", help="Existing router directory for --add-sub-skill")
    parser.add_argument("--suite", help="Path to suite JSON describing multiple skills")
    return parser.parse_args()


def validate_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"Invalid skill name '{name}'. Use kebab-case.")


def default_title(name: str) -> str:
    return name.replace("-", " ").title()


def build_frontmatter(name: str, description: str, compatibility: str = "") -> str:
    lines = ["---", f"name: {name}", f"description: {description}"]
    if compatibility:
        lines.append(f"compatibility: {compatibility}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def build_ja_stub(name: str, description: str, title: str, compatibility: str) -> str:
    return (
        f"{build_frontmatter(name, description, compatibility)}\n"
        f"# {title}\n\n"
        "日本語版は必要になった段階で追加してください。\n"
    )


def build_decision_rows(sub_skills: list[dict[str, str]]) -> str:
    if not sub_skills:
        return (
            "| <Intent A> | `sub_skills/<a>/` | <Brief action summary for route A.> |\n"
            "| <Intent B> | `sub_skills/<b>/` | <Brief action summary for route B.> |"
        )

    rows: list[str] = []
    for item in sub_skills:
        name = item["name"]
        label = name.replace("-", " ")
        intent = item.get("intent", f"Handle {label}")
        summary = item.get(
            "summary",
            f"Route the user to the {label} workflow and replace this summary before publishing.",
        )
        rows.append(f"| {intent} | `sub_skills/{name}/` | {summary} |")
    return "\n".join(rows)


def render_workflow_template(
    template: str,
    *,
    name: str,
    description: str,
    title: str,
    compatibility: str,
) -> str:
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


def render_router_template(
    template: str,
    *,
    name: str,
    description: str,
    title: str,
    sub_skills: list[dict[str, str]],
) -> str:
    rendered = template
    replacements = {
        "<context>-<object>": name,
        "<What this router does>. Use when <scenario 1>, <scenario 2>, or <scenario 3>, even if the user describes the workflow without saying the exact skill name.": description,
        "<Router Title>": title,
        "<Explain what this router unifies and why a single entry point helps.>": "Explain what this router unifies and trim placeholders before publishing.",
        "<Verb-led scenario 1>": "Replace this placeholder with a real router trigger",
        "<Verb-led scenario 2>": "Add a second route-specific scenario before validation",
        "<Verb-led scenario 3>": "Add a third route-specific scenario before validation",
        "<Decision Rows>": build_decision_rows(sub_skills),
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def render_sub_skill_template(
    template: str,
    *,
    name: str,
    description: str,
    title: str,
    compatibility: str,
) -> str:
    rendered = template
    replacements = {
        "<sub-skill-name>": name,
        "<What this sub-skill does>. Use when <scenario 1>, <scenario 2>, or <scenario 3>.": description,
        "compatibility: <optional shared resources or constraints>\n": f"compatibility: {compatibility}\n" if compatibility else "",
        "<Sub-skill Title>": title,
        "<Explain why this sub-skill exists in 1-2 sentences.>": "Explain why this sub-skill exists and trim placeholders before publishing.",
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


def normalize_sub_skill_item(item: str | dict[str, Any]) -> dict[str, str]:
    if isinstance(item, str):
        name = item
        return {
            "name": name,
            "description": f"Handle {name.replace('-', ' ')} concerns. Use when refining that route within this router.",
            "title": default_title(name),
            "compatibility": "_foundation/",
        }

    if not isinstance(item, dict) or "name" not in item:
        raise ValueError("Each sub-skill must be a string name or an object with at least 'name'.")

    name = str(item["name"])
    normalized = {
        "name": name,
        "description": str(
            item.get(
                "description",
                f"Handle {name.replace('-', ' ')} concerns. Use when refining that route within this router.",
            )
        ),
        "title": str(item.get("title", default_title(name))),
        "compatibility": str(item.get("compatibility", "_foundation/")),
    }
    if "intent" in item:
        normalized["intent"] = str(item["intent"])
    if "summary" in item:
        normalized["summary"] = str(item["summary"])
    return normalized


def parse_sub_skill_names(raw_names: str) -> list[dict[str, str]]:
    names = [name.strip() for name in raw_names.split(",") if name.strip()]
    if not names:
        raise ValueError("--sub-skills must contain at least one non-empty name.")
    return [normalize_sub_skill_item(name) for name in names]


def update_router_decision_table(router_skill_path: Path, sub_skill: dict[str, str]) -> None:
    route = f"`sub_skills/{sub_skill['name']}/`"
    content = router_skill_path.read_text(encoding="utf-8")
    if route in content:
        raise FileExistsError(f"Route already exists in router SKILL.md: {route}")

    marker = "\n## Shared Resources"
    if marker not in content:
        raise ValueError(f"Router SKILL.md is missing the Shared Resources section: {router_skill_path}")

    before, after = content.split(marker, maxsplit=1)
    row = build_decision_rows([sub_skill])
    before = before.rstrip() + "\n" + row + "\n"
    router_skill_path.write_text(before + marker + after, encoding="utf-8")


def create_sub_skill(router_dir: Path, template: str, item: dict[str, str], *, update_router: bool = False) -> Path:
    name = item["name"]
    validate_name(name)
    description = item["description"]
    title = item.get("title") or default_title(name)
    compatibility = item.get("compatibility", "_foundation/")

    sub_skill_dir = router_dir / "sub_skills" / name
    if sub_skill_dir.exists():
        raise FileExistsError(f"Destination already exists: {sub_skill_dir}")

    sub_skill_dir.mkdir(parents=True, exist_ok=False)
    (sub_skill_dir / "references").mkdir()
    (sub_skill_dir / "SKILL.md").write_text(
        render_sub_skill_template(
            template,
            name=name,
            description=description,
            title=title,
            compatibility=compatibility,
        ),
        encoding="utf-8",
    )
    (sub_skill_dir / "references" / "SKILL.ja.md").write_text(
        build_ja_stub(name, description, title, compatibility),
        encoding="utf-8",
    )
    if update_router:
        update_router_decision_table(router_dir / "SKILL.md", item)
    return sub_skill_dir


def create_workflow_skill(output_root: Path, template: str, item: dict[str, Any]) -> Path:
    name = str(item["name"])
    validate_name(name)
    description = str(item["description"])
    title = str(item.get("title") or default_title(name))
    compatibility = str(item.get("compatibility", ""))

    skill_dir = output_root / name
    if skill_dir.exists():
        raise FileExistsError(f"Destination already exists: {skill_dir}")

    (skill_dir / "references").mkdir(parents=True, exist_ok=False)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "assets").mkdir()

    (skill_dir / "SKILL.md").write_text(
        render_workflow_template(
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


def create_router_skill(
    output_root: Path,
    router_template: str,
    sub_skill_template: str,
    item: dict[str, Any],
) -> Path:
    name = str(item["name"])
    validate_name(name)
    description = str(item["description"])
    title = str(item.get("title") or default_title(name))
    compatibility = str(item.get("compatibility", ""))
    sub_skills = [normalize_sub_skill_item(raw) for raw in item.get("sub_skills", [])]

    skill_dir = output_root / name
    if skill_dir.exists():
        raise FileExistsError(f"Destination already exists: {skill_dir}")

    (skill_dir / "references").mkdir(parents=True, exist_ok=False)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "assets").mkdir()
    (skill_dir / "_foundation").mkdir()
    (skill_dir / "sub_skills").mkdir()

    (skill_dir / "SKILL.md").write_text(
        render_router_template(
            router_template,
            name=name,
            description=description,
            title=title,
            sub_skills=sub_skills,
        ),
        encoding="utf-8",
    )
    (skill_dir / "references" / "SKILL.ja.md").write_text(
        build_ja_stub(name, description, title, compatibility),
        encoding="utf-8",
    )
    for sub_skill in sub_skills:
        create_sub_skill(skill_dir, sub_skill_template, sub_skill)
    return skill_dir


def create_skill(
    output_root: Path,
    template: str,
    item: dict[str, Any],
    *,
    router_template: str | None = None,
    sub_skill_template: str | None = None,
) -> Path:
    skill_type = str(item.get("type", "workflow"))
    if skill_type == "workflow":
        return create_workflow_skill(output_root, template, item)
    if skill_type == "router":
        if router_template is None or sub_skill_template is None:
            raise ValueError("Router creation requires router_template and sub_skill_template.")
        return create_router_skill(output_root, router_template, sub_skill_template, item)
    raise ValueError(f"Unsupported skill type: {skill_type}")


def add_sub_skill(router_dir: Path, template: str, item: dict[str, Any]) -> Path:
    if not (router_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"Router SKILL.md not found: {router_dir}")
    (router_dir / "sub_skills").mkdir(exist_ok=True)
    return create_sub_skill(router_dir, template, normalize_sub_skill_item(item), update_router=True)


def load_suite(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("skills")
    else:
        items = data
    if not isinstance(items, list) or not items:
        raise ValueError("Suite JSON must be a non-empty array or an object with a 'skills' array.")
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or "name" not in item or "description" not in item:
            raise ValueError("Each suite item must contain 'name' and 'description'.")
        normalized_item: dict[str, Any] = {
            "name": str(item["name"]),
            "description": str(item["description"]),
            "type": str(item.get("type", "workflow")),
        }
        for key in ("title", "compatibility"):
            if key in item:
                normalized_item[key] = str(item[key])
        if "sub_skills" in item:
            if not isinstance(item["sub_skills"], list):
                raise ValueError("'sub_skills' must be a list when provided.")
            normalized_item["sub_skills"] = [normalize_sub_skill_item(sub_skill) for sub_skill in item["sub_skills"]]
        normalized.append(normalized_item)
    return normalized


def main() -> int:
    args = parse_args()
    workflow_template = TEMPLATE_PATH.read_text(encoding="utf-8")
    router_template = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    sub_skill_template = SUB_SKILL_TEMPLATE_PATH.read_text(encoding="utf-8")
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    if args.add_sub_skill:
        if not args.router_dir:
            print("ERROR: --router-dir is required when --add-sub-skill is used.", file=sys.stderr)
            return 1
        created = add_sub_skill(
            Path(args.router_dir),
            sub_skill_template,
            {
                "name": args.add_sub_skill,
                "description": args.description
                or f"Handle {args.add_sub_skill.replace('-', ' ')} concerns. Use when refining that route within this router.",
                "title": args.title or default_title(args.add_sub_skill),
                "compatibility": args.compatibility or "_foundation/",
            },
        )
        print(f"Created {created}")
        return 0

    if args.suite:
        items = load_suite(Path(args.suite))
    else:
        if not args.name or not args.description:
            print("ERROR: --name and --description are required unless --suite is used.", file=sys.stderr)
            return 1
        item: dict[str, Any] = {
            "name": args.name,
            "description": args.description,
            "title": args.title or default_title(args.name),
            "compatibility": args.compatibility,
            "type": args.type,
        }
        if args.type == "router" and args.sub_skills:
            item["sub_skills"] = parse_sub_skill_names(args.sub_skills)
        items = [item]

    created: list[Path] = []
    for item in items:
        created.append(
            create_skill(
                output_root,
                workflow_template,
                item,
                router_template=router_template,
                sub_skill_template=sub_skill_template,
            )
        )

    for path in created:
        print(f"Created {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
