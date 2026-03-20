#!/usr/bin/env python3
"""skill metadata の description を軽量ループで改善する。"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR_PATH = SCRIPT_DIR / "validate_skill.py"


def load_validator():
    """validator モジュールを動的に読み込む。"""
    spec = importlib.util.spec_from_file_location("skill_validate_skill", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load validator module spec: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class CandidateScore:
    description: str
    score: int


def count_trigger_hits(description: str, prompts: list[str]) -> int:
    """description と prompt 群の語彙重なり数を簡易スコアとして数える。"""
    tokens = {token for token in re.findall(r"[A-Za-z][A-Za-z-]+", description.lower()) if len(token) > 3}
    score = 0
    for prompt in prompts:
        prompt_tokens = set(re.findall(r"[A-Za-z][A-Za-z-]+", prompt.lower()))
        if tokens & prompt_tokens:
            score += 1
    return score


def generate_candidates(description: str) -> list[str]:
    """現在の description から比較用の候補文を作る。"""
    if "even if" in description:
        return [description]
    return [
        description,
        description.rstrip(".") + ", even if the workflow is described indirectly.",
        description.rstrip(".") + ", even if the user describes the workflow without saying \"skill\".",
    ]


def rewrite_description(skill_path: Path, description: str) -> None:
    """frontmatter 内の description を新しい文に書き換える。"""
    lines = skill_path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        end = index + 1
        value = line.partition(":")[2].strip()
        if value in {">", "|", ">-", "|-"}:
            while end < len(lines) and (lines[end].startswith(" ") or lines[end].startswith("\t")):
                end += 1
        replacement = ["description: >\n", *(f"  {part}\n" if part else "  \n" for part in description.splitlines())]
        skill_path.write_text("".join([*lines[:index], *replacement, *lines[end:]]), encoding="utf-8")
        return
    raise ValueError(f"description frontmatter not found: {skill_path}")


def parse_args() -> argparse.Namespace:
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(description="簡易ループで skill description を最適化する")
    parser.add_argument("--skill", required=True, help="SKILL.md のパス")
    parser.add_argument("--prompts", required=True, help="trigger prompt を含む JSON ファイル")
    parser.add_argument("--apply", action="store_true", help="最良候補をファイルへ反映する")
    return parser.parse_args()


def main() -> int:
    """候補文を比較し、必要なら最良の description を反映する。"""
    args = parse_args()
    skill_path = Path(args.skill)
    prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8"))
    if isinstance(prompts, dict):
        prompts_list = [str(item) for item in prompts.get("prompts", [])]
    else:
        prompts_list = [str(item) for item in prompts]

    validator = load_validator()
    report = validator.validate(skill_path, "L1")
    frontmatter = validator.extract_frontmatter(skill_path.read_text(encoding="utf-8"))
    current = frontmatter.get("description", "")

    ranked = sorted(
        (CandidateScore(candidate, count_trigger_hits(candidate, prompts_list)) for candidate in generate_candidates(current)),
        key=lambda item: item.score,
        reverse=True,
    )
    best = ranked[0]
    output = {
        "file": str(skill_path),
        "critical_passed": report.critical_passed,
        "current_description": current,
        "best_description": best.description,
        "score": best.score,
        "candidates": [candidate.__dict__ for candidate in ranked],
    }

    if args.apply and best.description != current:
        rewrite_description(skill_path, best.description)
        output["applied"] = True
    else:
        output["applied"] = False

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if report.critical_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
