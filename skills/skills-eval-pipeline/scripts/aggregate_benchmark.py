"""aggregate_benchmark.py

Aggregate grading_result.json files into benchmark_summary.json.

Usage:
    python skills/skills-eval-pipeline/scripts/aggregate_benchmark.py \\
        --skill-id skills-author-skill \\
        --run-id run-20260310-001 \\
        [--evals-dir evals]

Output:
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
# Data loading
# ---------------------------------------------------------------------------

def load_run_results(evals_dir: Path, skill_id: str, run_id: str) -> tuple[list[dict], list[dict]]:
    """Load all grading results for one run, split by mode."""
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


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def _scores(results: list[dict]) -> list[float]:
    """Extract valid (non-null) scores."""
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
# Case breakdown
# ---------------------------------------------------------------------------

def build_case_breakdown(with_skill: list[dict], baseline: list[dict]) -> list[dict]:
    """Per-case score comparison keyed by case_id."""
    ws_map = {r["case_id"]: r["score"] for r in with_skill if r.get("score") is not None}
    bl_map = {r["case_id"]: r["score"] for r in baseline if r.get("score") is not None}

    case_ids = sorted(set(ws_map) | set(bl_map))
    breakdown = []
    for cid in case_ids:
        ws_score = ws_map.get(cid)
        bl_score = bl_map.get(cid)
        delta = None
        if ws_score is not None and bl_score is not None:
            delta = round(ws_score - bl_score, 4)
        breakdown.append({
            "case_id": cid,
            "with_skill_mean": ws_score,
            "baseline_mean": bl_score,
            "delta": delta,
        })
    return breakdown


# ---------------------------------------------------------------------------
# Main aggregation
# ---------------------------------------------------------------------------

def aggregate(
    evals_dir: Path,
    skill_id: str,
    run_id: str,
    eval_version: str = "1.0.0",
) -> dict:
    with_skill, baseline = load_run_results(evals_dir, skill_id, run_id)

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
        "case_breakdown": build_case_breakdown(with_skill, baseline),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate grading_result.json files into benchmark_summary.json"
    )
    parser.add_argument("--skill-id", required=True, help="Skill directory name")
    parser.add_argument("--run-id", required=True, help="Run identifier prefix")
    parser.add_argument(
        "--evals-dir",
        default="evals",
        help="Base directory for eval files (default: evals/)",
    )
    parser.add_argument(
        "--eval-version",
        default="1.0.0",
        help="Eval suite version to embed in output (default: 1.0.0)",
    )
    return parser.parse_args()


def main() -> int:
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
