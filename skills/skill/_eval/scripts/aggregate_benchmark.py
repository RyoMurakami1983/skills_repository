"""`grading_result.json` 群を `benchmark_summary.json` へ集計する。

使い方:
    uv run python skills/skill/_eval/scripts/aggregate_benchmark.py \\
        --skill-id skill \\
        --run-id run-20260310-001 \\
        [--evals-dir evals]

出力:
    evals/<skill_id>/benchmark_summary.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# ギャップ分析ヘルパー
# ---------------------------------------------------------------------------

_FAILURE_MESSAGES = {
    "contains": "スキル固有のキーワード・コマンド名の知識が不足（「{value}」が回答に現れない）",
    "not_contains": "アンチパターン防止の知識が不足（「{value}」を使ってしまう）",
    "llm_grade": "推論・判断力が不足（{value}）",
}


def _format_gap_message(assertion_type: str, value: str) -> str:
    tpl = _FAILURE_MESSAGES.get(assertion_type, "「{value}」の条件を満たせない")
    return tpl.format(value=value[:80])


def _generate_recommendation(failures: list[dict]) -> str:
    """baseline 側の assertion failure からルールベースで推奨文を作る。"""
    if not failures:
        return "ベースラインも十分な回答を生成できています。スキル固有ではない汎用知識で対応可能なケースです。"

    parts: list[str] = []
    has_contains = any(f["type"] == "contains" for f in failures)
    has_not_contains = any(f["type"] == "not_contains" for f in failures)
    has_llm = any(f["type"] == "llm_grade" for f in failures)

    if has_contains:
        values = [f["value"] for f in failures if f["type"] == "contains"]
        parts.append(
            f"スキル固有の専門知識（{', '.join(values[:3])}）をスキルに明示することで発火率が上がります。"
        )
    if has_not_contains:
        values = [f["value"] for f in failures if f["type"] == "not_contains"]
        parts.append(
            f"Anti-Patterns セクションに「{', '.join(values[:3])}」を避ける理由を追記すると効果的です。"
        )
    if has_llm:
        parts.append(
            "Decision Table やステップ説明を充実させると、AIの推論精度が向上します。"
        )
    return "　".join(parts)


# ---------------------------------------------------------------------------
# データ読み込み
# ---------------------------------------------------------------------------

def load_run_results(evals_dir: Path, skill_id: str, run_id: str) -> tuple[list[dict], list[dict]]:
    """1 回の run に属する grading result を mode 別に読み込む。"""
    run_dir = evals_dir / skill_id / "runs"
    if not run_dir.exists():
        raise FileNotFoundError(f"Runs directory not found: {run_dir}")

    with_skill: list[dict] = []
    baseline: list[dict] = []

    for path in sorted(run_dir.glob(f"{run_id}_*_with_skill.json")):
        try:
            with open(path, encoding="utf-8") as f:
                with_skill.append(json.load(f))
        except json.JSONDecodeError as exc:
            print(f"WARNING: Skipping malformed JSON in {path}: {exc}", file=sys.stderr)
            with_skill.append({"case_id": path.stem.split("_")[1], "score": None})

    for path in sorted(run_dir.glob(f"{run_id}_*_baseline.json")):
        try:
            with open(path, encoding="utf-8") as f:
                baseline.append(json.load(f))
        except json.JSONDecodeError as exc:
            print(f"WARNING: Skipping malformed JSON in {path}: {exc}", file=sys.stderr)
            baseline.append({"case_id": path.stem.split("_")[1], "score": None})

    if not with_skill:
        raise ValueError(f"No with_skill results found for run '{run_id}' in {run_dir}")
    if not baseline:
        raise ValueError(f"No baseline results found for run '{run_id}' in {run_dir}")

    return with_skill, baseline


def load_evals_json(evals_dir: Path, skill_id: str) -> dict[str, dict]:
    """`evals.json` を case_id キーの辞書として読み込む。なければ空辞書を返す。"""
    path = evals_dir / skill_id / "evals.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {case["id"]: case for case in data.get("cases", [])}


# ---------------------------------------------------------------------------
# 統計計算
# ---------------------------------------------------------------------------

def _scores(results: list[dict]) -> list[float]:
    """null でない score だけを取り出す。"""
    return [r["score"] for r in results if r.get("score") is not None]


def compute_stats(results: list[dict]) -> dict:
    scores = _scores(results)
    if not scores:
        return {"count": 0, "mean": None, "stddev": None, "min": None, "max": None}

    n = len(scores)
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n
    stddev = math.sqrt(variance)

    return {
        "count": n,
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(scores), 4),
        "max": round(max(scores), 4),
    }


def compute_verdict(delta: float) -> str:
    if delta > 0.05:
        return "improved"
    if delta < -0.05:
        return "degraded"
    return "neutral"


# ---------------------------------------------------------------------------
# ケース別 breakdown
# ---------------------------------------------------------------------------

def build_case_breakdown(
    with_skill: list[dict],
    baseline: list[dict],
    evals_meta: dict[str, dict],
) -> list[dict]:
    """case_id ごとの比較結果に prompt と assertion 詳細を付与して返す。"""
    ws_map = {r["case_id"]: r for r in with_skill if r.get("score") is not None}
    bl_map = {r["case_id"]: r for r in baseline if r.get("score") is not None}

    case_ids = sorted(set(ws_map) | set(bl_map))
    breakdown = []
    for cid in case_ids:
        ws = ws_map.get(cid, {})
        bl = bl_map.get(cid, {})
        ws_score = ws.get("score")
        bl_score = bl.get("score")
        delta = None
        if ws_score is not None and bl_score is not None:
            delta = round(ws_score - bl_score, 4)

        # run result 側の assertion 詳細と evals.json 側の期待値を突き合わせる。
        meta = evals_meta.get(cid, {})
        eval_assertions = meta.get("assertions", [])
        ws_assertions = ws.get("assertions", [])
        bl_assertions = bl.get("assertions", [])

        assertion_detail: list[dict] = []
        for i, ea in enumerate(eval_assertions):
            ws_a = ws_assertions[i] if i < len(ws_assertions) else {}
            bl_a = bl_assertions[i] if i < len(bl_assertions) else {}
            assertion_detail.append({
                "type": ea.get("type", ""),
                "value": ea.get("value", ""),
                "weight": ea.get("weight", 1.0),
                "with_skill_passed": ws_a.get("passed"),
                "baseline_passed": bl_a.get("passed"),
                "detail": ws_a.get("detail") or bl_a.get("detail") or "",
            })

        # baseline failure をもとに、足りない知識や改善方向を要約する。
        baseline_failures = [
            {"type": a["type"], "value": a["value"]}
            for a in assertion_detail
            if a["baseline_passed"] is False
        ]
        gap_summary = [
            _format_gap_message(f["type"], f["value"])
            for f in baseline_failures
        ]
        recommendation = _generate_recommendation(baseline_failures)

        breakdown.append({
            "case_id": cid,
            "prompt": meta.get("prompt", ""),
            "tags": meta.get("tags", []),
            "with_skill_mean": ws_score,
            "baseline_mean": bl_score,
            "delta": delta,
            "assertion_detail": assertion_detail,
            "with_skill_snippet": ws.get("response_snippet", ""),
            "baseline_snippet": bl.get("response_snippet", ""),
            "gap_summary": gap_summary,
            "recommendation": recommendation,
        })
    return breakdown


# ---------------------------------------------------------------------------
# メイン集計
# ---------------------------------------------------------------------------

def aggregate(
    evals_dir: Path,
    skill_id: str,
    run_id: str,
    eval_version: str = "1.0.0",
) -> dict:
    with_skill, baseline = load_run_results(evals_dir, skill_id, run_id)
    evals_meta = load_evals_json(evals_dir, skill_id)

    ws_stats = compute_stats(with_skill)
    bl_stats = compute_stats(baseline)

    delta: float | None = None
    improvement_pct: float | None = None
    verdict = "neutral"

    if ws_stats["mean"] is not None and bl_stats["mean"] is not None:
        delta = round(ws_stats["mean"] - bl_stats["mean"], 4)
        if bl_stats["mean"] != 0:
            improvement_pct = round(delta / bl_stats["mean"] * 100, 2)
        verdict = compute_verdict(delta)

    summary = {
        "skill_id": skill_id,
        "eval_version": eval_version,
        "runs": {
            "with_skill": ws_stats,
            "baseline": bl_stats,
        },
        "summary": {
            "delta": delta,
            "improvement_pct": improvement_pct,
            "verdict": verdict,
        },
        "case_breakdown": build_case_breakdown(with_skill, baseline, evals_meta),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """CLI 引数を定義して返す。"""
    parser = argparse.ArgumentParser(
        description="grading_result.json を benchmark_summary.json へ集計する"
    )
    parser.add_argument("--skill-id", required=True, help="skill ディレクトリ名")
    parser.add_argument("--run-id", required=True, help="run ID の接頭辞")
    parser.add_argument(
        "--evals-dir",
        default="evals",
        help="eval ファイル群の基底ディレクトリ（既定: evals/）",
    )
    parser.add_argument(
        "--eval-version",
        default="1.0.0",
        help="出力に埋め込む eval suite version（既定: 1.0.0）",
    )
    return parser.parse_args()


def main() -> int:
    """CLI から benchmark 集計を実行する。"""
    args = parse_args()
    evals_dir = Path(args.evals_dir)

    try:
        result = aggregate(evals_dir, args.skill_id, args.run_id, args.eval_version)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out_path = evals_dir / args.skill_id / "benchmark_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    verdict = result["summary"]["verdict"]
    delta = result["summary"]["delta"]
    print(f"benchmark_summary.json written → {out_path}")
    print(f"Verdict: {verdict}  |  Delta: {delta:+.4f}" if delta is not None else f"Verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
