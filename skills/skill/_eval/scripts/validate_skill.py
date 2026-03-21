#!/usr/bin/env python3
"""統一 skill 構造を Critical / Recommended check で検証する。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TRIGGER_PATTERNS = (
    r"Use\s+when:",
    r"こんな\s*ときに\s*使う",
    r"次のような\s*ときに\s*使います",
    r"次のような\s*ときに\s*使用します",
)
WHEN_TO_USE_HEADINGS = ("When to Use This Skill", "こんなときに使う")
QUICK_REFERENCE_HEADINGS = ("Quick Reference", "クイックリファレンス", "早見表")
PITFALL_HEADINGS = ("Pitfalls", "注意点")


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
    """Markdown 文字列から frontmatter を抽出する。"""
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


def get_section(content: str, headings: str | Iterable[str]) -> str | None:
    """候補見出しのいずれかに一致する H2 セクション本文を返す。"""
    heading_list = (headings,) if isinstance(headings, str) else tuple(headings)
    matches = [
        match
        for heading in heading_list
        if (match := re.search(rf"^##\s+{re.escape(heading)}\s*$", content, re.MULTILINE))
    ]
    if not matches:
        return None
    match = min(matches, key=lambda item: item.start())
    start = match.end()
    next_heading = re.search(r"^##\s+.+$", content[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(content)
    return content[start:end].strip()


def bullet_lines(section: str | None) -> list[str]:
    """セクション本文から bullet 行だけを取り出す。"""
    if not section:
        return []
    bullets: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "+ ")):
            bullets.append(re.sub(r"^[-*+]\s+", "", stripped))
    return bullets


def has_workflow_or_router(content: str) -> bool:
    """workflow / router を示す見出しや step 構造があるか判定する。"""
    return any(
        re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        for pattern in (
            r"^##\s+Workflow:",
            r"^##\s+ワークフロー[:：]",
            r"^##\s+Decision Table$",
            r"^##\s+判断表$",
            r"^###\s+Step\s+\d+",
            r"^###\s*ステップ\s*\d+",
        )
    )


def is_action_led(text: str) -> bool:
    """bullet が行動ベースの表現かどうかを緩やかに判定する。"""
    first_word = re.match(r"^([A-Za-z][A-Za-z-]*)", text)
    if first_word:
        return first_word.group(1).lower() not in {"the", "a", "an", "this"}
    if re.search(r"[ぁ-んァ-ン一-龥]", text):
        return (
            text.endswith(("とき", "場合"))
            or "したい" in text
            or bool(
                re.search(
                    r"(する|始める|進める|作る|直す|改善する|確認する|測る|評価する|選ぶ|比べる|整理する|判断する|設計する|移行する|追加する|更新する)$",
                    text,
                )
            )
        )
    return False


def has_trigger_phrase(text: str) -> bool:
    """description に trigger phrase が含まれるか判定する。"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in TRIGGER_PATTERNS)


def has_code_blocks(content: str) -> bool:
    """コードブロックを含むかどうかを返す。"""
    return "```" in content


def fenced_blocks(content: str) -> Iterable[str]:
    """fenced code block の本文を列挙する。"""
    return re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", content, re.DOTALL)


def has_title_heading(content: str) -> bool:
    """H1 タイトルが存在するか判定する。"""
    return re.search(r"^#\s+\S.+$", content, re.MULTILINE) is not None


def validate(path: Path, level: str) -> ValidationReport:
    """1 本の SKILL.md を検証して report を返す。"""
    content = path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    folder_name = path.parent.name
    description = frontmatter.get("description", "")
    when_section = get_section(content, WHEN_TO_USE_HEADINGS)
    bullets = bullet_lines(when_section)
    quick_reference = get_section(content, QUICK_REFERENCE_HEADINGS)
    pitfalls = get_section(content, PITFALL_HEADINGS)
    references_dir = path.parent / "references"

    critical = [
        CheckResult("C1", "Frontmatter に name と description がある", {"name", "description"} <= frontmatter.keys()),
        CheckResult("C2", "name がディレクトリ名と一致する", frontmatter.get("name") == folder_name, f"directory={folder_name}"),
        CheckResult("C3", "description に trigger phrase が入っている", has_trigger_phrase(description), description),
        CheckResult("C4", "『こんなときに使う』互換セクションがある", when_section is not None),
        CheckResult("C5", "ワークフローまたは router セクションがある", has_workflow_or_router(content)),
    ]

    recommended = [
        CheckResult("R1", "『こんなときに使う』が 3-8 個の bullet で書かれている", 3 <= len(bullets) <= 8, f"count={len(bullets)}"),
        CheckResult("R2", "bullet が行動ベースで書かれている", bool(bullets) and all(is_action_led(b) for b in bullets)),
        CheckResult("R3", "なぜ効くかの説明がある", any(term in content.lower() for term in ("why", "because")) or any(term in content for term in ("なぜ", "理由"))),
        CheckResult("R4", "注意点セクションがある", pitfalls is not None),
        CheckResult("R5", "SKILL.md がコンパクトに保たれている", len(content.splitlines()) <= 220, f"lines={len(content.splitlines())}"),
        CheckResult(
            "R6",
            "overflow 用の references/ がある、または本文がそれを要しない",
            references_dir.exists() or len(content.splitlines()) <= 220,
        ),
        CheckResult("R7", "関連リソースへの導線がある", any(marker in content for marker in ("Related Skills", "Shared Resources", "関連スキル", "共通リソース"))),
        CheckResult("R8", "早見表または判断表がある", quick_reference is not None or "Decision Table" in content or "判断表" in content),
        CheckResult("R9", "コードブロックが空でない", (not has_code_blocks(content)) or all(block.strip() for block in fenced_blocks(content))),
        CheckResult("R10", "H1 タイトルがある", has_title_heading(content)),
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
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(description="統一 skill ファイルを検証する")
    parser.add_argument("path", help="SKILL.md のパス")
    parser.add_argument("--level", choices=["L1", "L2"], default="L2")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON 形式で出力する")
    return parser.parse_args()


def print_text(report: ValidationReport) -> None:
    """検証結果を人間向けのテキスト形式で表示する。"""
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
    """CLI から validator を実行する。"""
    args = parse_args()
    report = validate(Path(args.path), args.level)
    if args.json_output:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if report.critical_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
