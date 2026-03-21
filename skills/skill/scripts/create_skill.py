#!/usr/bin/env python3
"""template から workflow skill / router / sub-skill を生成する。"""

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
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(description="workflow skill / router / sub-skill を生成する")
    parser.add_argument("--name", help="skill ディレクトリ名（kebab-case）")
    parser.add_argument("--description", help="frontmatter の description")
    parser.add_argument("--title", help="skill の表示タイトル")
    parser.add_argument("--compatibility", default="", help="任意の compatibility テキスト")
    parser.add_argument("--output-root", default="skills", help="skill を作成する出力先ディレクトリ")
    parser.add_argument(
        "--type",
        choices=("workflow", "router"),
        default="workflow",
        help="生成する skill の種類",
    )
    parser.add_argument("--sub-skills", help="router 作成時の sub-skill 名をカンマ区切りで指定する")
    parser.add_argument("--add-sub-skill", help="既存 router 配下に sub-skill を 1 つ追加する")
    parser.add_argument("--router-dir", help="--add-sub-skill の対象となる既存 router ディレクトリ")
    parser.add_argument("--suite", help="複数 skill 定義を含む suite JSON のパス")
    return parser.parse_args()


def validate_name(name: str) -> None:
    """skill 名が kebab-case かどうか検証する。"""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"無効な skill 名です: '{name}'。kebab-case で指定してください。")


def default_title(name: str) -> str:
    """kebab-case の skill 名から簡易タイトルを作る。"""
    return name.replace("-", " ").title()


def quote_yaml_scalar(value: str) -> str:
    """YAML scalar を安全に埋め込めるよう JSON 形式で quote する。"""
    return json.dumps(value, ensure_ascii=False)


def build_frontmatter(name: str, description: str, compatibility: str = "") -> str:
    """最小 frontmatter を組み立てる。"""
    description_lines = [line.rstrip() for line in description.strip().splitlines() if line.strip()]
    if not description_lines:
        description_lines = ["公開前に description を書き換えてください。"]

    lines = ["---", f"name: {name}", "description: >"]
    lines.extend(f"  {line}" for line in description_lines)
    if compatibility:
        lines.append(f"compatibility: {quote_yaml_scalar(compatibility)}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def build_decision_rows(sub_skills: list[dict[str, str]]) -> str:
    """router の判断表に差し込む行を生成する。"""
    if not sub_skills:
        return (
            "| <やりたいこと A> | `sub_skills/<a>/` | <ルート A で何をするかを短く書く> |\n"
            "| <やりたいこと B> | `sub_skills/<b>/` | <ルート B で何をするかを短く書く> |"
        )

    rows: list[str] = []
    for item in sub_skills:
        name = item["name"]
        label = name.replace("-", " ")
        intent = item.get("intent", f"{label} に関する流れを扱う")
        summary = item.get(
            "summary",
            f"ユーザーを {label} のワークフローへ案内し、公開前に要約を実文へ置き換える。",
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
    """workflow template のプレースホルダーを実値へ置換する。"""
    rendered = template
    compatibility_line = (
        f"compatibility: {quote_yaml_scalar(compatibility)}\n"
        if compatibility
        else ""
    )
    replacements = {
        "<context>-<verb>-<object>": name,
        "<What this skill does>": description,
        "compatibility: <optional tools, runtime, or platform constraints>\n": compatibility_line,
        "<Skill Title>": title,
        "<Explain why this skill exists in 1-2 sentences.>": "このスキルが必要な理由を書き、公開前にプレースホルダーを削除してください。",
        "<Verb-led scenario 1>": "実際の trigger に置き換える",
        "<Verb-led scenario 2>": "検証前に 2 つ目の具体例を追加する",
        "<Verb-led scenario 3>": "検証前に 3 つ目の具体例を追加する",
        "<Workflow Name>": "置き換えてください",
        "<Action>": "置き換えてください",
        "<Pitfall>": "要置換",
        "<How to avoid it and why the safer choice works better.>": "実際の失敗パターンと回避策へ置き換える。",
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
    """router template のプレースホルダーを実値へ置換する。"""
    rendered = template
    replacements = {
        "<context>-<object>": name,
        "<What this router does>": description,
        "<Router Title>": title,
        "<Explain what this router unifies and why a single entry point helps.>": "この router が何を束ねるのかを書き、公開前にプレースホルダーを削除してください。",
        "<Verb-led scenario 1>": "実際の router trigger に置き換える",
        "<Verb-led scenario 2>": "検証前に 2 つ目のルート別シナリオを追加する",
        "<Verb-led scenario 3>": "検証前に 3 つ目のルート別シナリオを追加する",
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
    """sub-skill template のプレースホルダーを実値へ置換する。"""
    rendered = template
    compatibility_line = (
        f"compatibility: {quote_yaml_scalar(compatibility)}\n"
        if compatibility
        else ""
    )
    replacements = {
        "<sub-skill-name>": name,
        "<What this sub-skill does>": description,
        "compatibility: <optional shared resources or constraints>\n": compatibility_line,
        "<Sub-skill Title>": title,
        "<Explain why this sub-skill exists in 1-2 sentences.>": "この sub-skill が必要な理由を書き、公開前にプレースホルダーを削除してください。",
        "<Verb-led scenario 1>": "実際の trigger に置き換える",
        "<Verb-led scenario 2>": "検証前に 2 つ目の具体例を追加する",
        "<Verb-led scenario 3>": "検証前に 3 つ目の具体例を追加する",
        "<Workflow Name>": "置き換えてください",
        "<Action>": "置き換えてください",
        "<Pitfall>": "要置換",
        "<How to avoid it and why the safer choice works better.>": "実際の失敗パターンと回避策へ置き換える。",
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def normalize_sub_skill_item(item: str | dict[str, Any]) -> dict[str, str]:
    """sub-skill 定義を内部処理しやすい共通形式へ正規化する。"""
    if isinstance(item, str):
        name = item
        return {
            "name": name,
            "description": f"{name.replace('-', ' ')} に関する流れを扱う。こんなときに使う: この router 内でそのルートを磨きたいとき。",
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
                f"{name.replace('-', ' ')} に関する流れを扱う。こんなときに使う: この router 内でそのルートを磨きたいとき。",
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
    """カンマ区切りの sub-skill 名から正規化済み定義一覧を作る。"""
    names = [name.strip() for name in raw_names.split(",") if name.strip()]
    if not names:
        raise ValueError("--sub-skills には少なくとも 1 つ以上の名前を指定してください。")
    return [normalize_sub_skill_item(name) for name in names]


def update_router_decision_table(router_skill_path: Path, sub_skill: dict[str, str]) -> None:
    """既存 router の判断表へ新しい sub-skill の行を追記する。"""
    route = f"`sub_skills/{sub_skill['name']}/`"
    content = router_skill_path.read_text(encoding="utf-8")
    if route in content:
        raise FileExistsError(f"router SKILL.md に同じ route が既に存在します: {route}")

    marker = re.search(r"^##\s+(共通リソース|Shared Resources)\s*$", content, re.MULTILINE)
    if marker is None:
        raise ValueError(f"Router SKILL.md に共通リソース見出しが見つかりません: {router_skill_path}")

    before = content[:marker.start()]
    after = content[marker.start():]
    row = build_decision_rows([sub_skill])
    before = before.rstrip() + "\n" + row + "\n"
    router_skill_path.write_text(before + after, encoding="utf-8")


def create_sub_skill(router_dir: Path, template: str, item: dict[str, str], *, update_router: bool = False) -> Path:
    """router 配下に sub-skill ディレクトリを生成する。"""
    name = item["name"]
    validate_name(name)
    description = item["description"]
    title = item.get("title") or default_title(name)
    compatibility = item.get("compatibility", "_foundation/")

    sub_skill_dir = router_dir / "sub_skills" / name
    if sub_skill_dir.exists():
        raise FileExistsError(f"出力先が既に存在します: {sub_skill_dir}")

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
    if update_router:
        update_router_decision_table(router_dir / "SKILL.md", item)
    return sub_skill_dir


def create_workflow_skill(output_root: Path, template: str, item: dict[str, Any]) -> Path:
    """top-level workflow skill を生成する。"""
    name = str(item["name"])
    validate_name(name)
    description = str(item["description"])
    title = str(item.get("title") or default_title(name))
    compatibility = str(item.get("compatibility", ""))

    skill_dir = output_root / name
    if skill_dir.exists():
        raise FileExistsError(f"出力先が既に存在します: {skill_dir}")

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
    return skill_dir


def create_router_skill(
    output_root: Path,
    router_template: str,
    sub_skill_template: str,
    item: dict[str, Any],
) -> Path:
    """router 親 skill と必要な sub-skill 群をまとめて生成する。"""
    name = str(item["name"])
    validate_name(name)
    description = str(item["description"])
    title = str(item.get("title") or default_title(name))
    compatibility = str(item.get("compatibility", ""))
    sub_skills = [normalize_sub_skill_item(raw) for raw in item.get("sub_skills", [])]

    skill_dir = output_root / name
    if skill_dir.exists():
        raise FileExistsError(f"出力先が既に存在します: {skill_dir}")

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
    """skill 種別に応じて workflow または router の生成へ振り分ける。"""
    skill_type = str(item.get("type", "workflow"))
    if skill_type == "workflow":
        return create_workflow_skill(output_root, template, item)
    if skill_type == "router":
        if router_template is None or sub_skill_template is None:
            raise ValueError("router を作成するには router_template と sub_skill_template が必要です。")
        return create_router_skill(output_root, router_template, sub_skill_template, item)
    raise ValueError(f"未対応の skill 種別です: {skill_type}")


def add_sub_skill(router_dir: Path, template: str, item: dict[str, Any]) -> Path:
    """既存 router に sub-skill を追加する。"""
    if not (router_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"Router の SKILL.md が見つかりません: {router_dir}")
    (router_dir / "sub_skills").mkdir(exist_ok=True)
    return create_sub_skill(router_dir, template, normalize_sub_skill_item(item), update_router=True)


def load_suite(path: Path) -> list[dict[str, Any]]:
    """suite JSON を読み込み、skill 生成用の一覧へ正規化する。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("skills")
    else:
        items = data
    if not isinstance(items, list) or not items:
        raise ValueError("suite JSON は空でない配列、または 'skills' 配列を持つ object である必要があります。")
    normalized: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict) or "name" not in item or "description" not in item:
            raise ValueError("suite の各 item には 'name' と 'description' が必要です。")
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
                raise ValueError("'sub_skills' を指定する場合は list で渡してください。")
            normalized_item["sub_skills"] = [normalize_sub_skill_item(sub_skill) for sub_skill in item["sub_skills"]]
        normalized.append(normalized_item)
    return normalized


def main() -> int:
    """CLI から skill 生成処理を実行する。"""
    args = parse_args()
    workflow_template = TEMPLATE_PATH.read_text(encoding="utf-8")
    router_template = ROUTER_TEMPLATE_PATH.read_text(encoding="utf-8")
    sub_skill_template = SUB_SKILL_TEMPLATE_PATH.read_text(encoding="utf-8")
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    if args.add_sub_skill:
        if not args.router_dir:
            print("ERROR: --add-sub-skill を使うときは --router-dir が必要です。", file=sys.stderr)
            return 1
        created = add_sub_skill(
            Path(args.router_dir),
            sub_skill_template,
            {
                "name": args.add_sub_skill,
                "description": args.description
                or f"{args.add_sub_skill.replace('-', ' ')} に関する流れを扱う。こんなときに使う: この router 内でそのルートを磨きたいとき。",
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
            print("ERROR: --suite を使わない場合は --name と --description が必要です。", file=sys.stderr)
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
