"""手動収集した eval 応答を `grading_result.json` 形式の run file へ変換する。

manual 実行や外部 agent で集めた response を、集計・viewer 生成が扱える
標準の `evals/<skill_id>/runs/` レイアウトへ橋渡しするためのスクリプト。
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    """UTF-8 JSON ファイルを読み込む。"""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_assertions(case: dict, response: str, llm_overrides: list[dict]) -> list[dict]:
    """1 ケース分の assertion を response に対して評価する。"""
    details: list[dict] = []
    llm_index = 0
    for assertion in case.get("assertions", []):
        assertion_type = assertion["type"]
        value = assertion["value"]
        weight = assertion.get("weight", 1.0)

        if assertion_type == "contains":
            details.append({
                "type": assertion_type,
                "passed": value in response,
                "weight": weight,
                "detail": "",
            })
            continue

        if assertion_type == "not_contains":
            details.append({
                "type": assertion_type,
                "passed": value not in response,
                "weight": weight,
                "detail": "",
            })
            continue

        if assertion_type != "llm_grade":
            raise ValueError(f"Unsupported assertion type for manual materialization: {assertion_type}")

        if llm_index >= len(llm_overrides):
            raise ValueError(f"Missing llm override for case {case['id']}")
        override = llm_overrides[llm_index]
        llm_index += 1
        details.append({
            "type": assertion_type,
            "passed": bool(override["passed"]),
            "weight": weight,
            "detail": override.get("detail", ""),
        })

    return details


def score_assertions(assertions: list[dict]) -> float:
    """assertion 群から重み付き score を計算する。"""
    total = sum(item["weight"] for item in assertions)
    passed = sum(item["weight"] for item in assertions if item["passed"])
    if total == 0:
        return 0.0
    return round(passed / total, 4)


def materialize_run(evals_path: Path, manual_path: Path, skill_id: str, evals_dir: Path) -> list[Path]:
    """手動 run データを標準 run file 群へ変換して書き出す。"""
    evals = load_json(evals_path)
    manual = load_json(manual_path)
    run_id = manual["run_id"]
    created: list[Path] = []
    runs_dir = evals_dir / skill_id / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    responses = manual["responses"]
    llm = manual["llm_grade"]

    for mode in ("with_skill", "baseline"):
        mode_responses = responses[mode]
        mode_llm = llm[mode]
        for case in evals.get("cases", []):
            case_id = case["id"]
            response = mode_responses[case_id]
            assertions = evaluate_assertions(case, response, mode_llm.get(case_id, []))
            result = {
                "case_id": case_id,
                "run_id": run_id,
                "mode": mode,
                "score": score_assertions(assertions),
                "assertions": assertions,
                "response_snippet": response[:500],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            out_path = runs_dir / f"{run_id}_{case_id}_{mode}.json"
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            created.append(out_path)

    return created


def parse_args() -> argparse.Namespace:
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(description="手動 eval 応答を run result file へ変換する")
    parser.add_argument("--skill-id", required=True, help="evals/ 配下の skill ディレクトリ名")
    parser.add_argument("--evals", required=True, help="evals.json のパス")
    parser.add_argument("--manual", required=True, help="手動 response JSON のパス")
    parser.add_argument("--evals-dir", default="evals", help="evals 基底ディレクトリ")
    return parser.parse_args()


def main() -> int:
    """CLI から materialize 処理を実行する。"""
    args = parse_args()
    created = materialize_run(
        evals_path=Path(args.evals),
        manual_path=Path(args.manual),
        skill_id=args.skill_id,
        evals_dir=Path(args.evals_dir),
    )
    print(f"Created {len(created)} run file(s)")
    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
