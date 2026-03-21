"""`grading_result.json` 群を `benchmark_summary.json` へ集計する。

baseline / legacy / current の 3 役を標準の比較軸として扱い、
必要なら append-only の履歴 ledger にも 1 行追記する。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VARIANT_ALIASES = {"with_skill": "current"}
VARIANT_PRIORITY = ("baseline", "legacy", "current")


def canonical_variant_id(variant_id: str) -> str:
    """旧 mode 名を含めて variant 名を標準化する。"""
    return VARIANT_ALIASES.get(variant_id, variant_id)


def parse_result_filename(path: Path, run_id: str) -> tuple[str | None, str | None]:
    """run file 名から variant_id と case_id を推定する。"""
    stem = path.stem

    if "__" in stem:
        parts = stem.split("__", 2)
        if len(parts) == 3 and parts[0] == run_id:
            return canonical_variant_id(parts[1]), parts[2]

    for suffix, variant_id in (
        ("_with_skill", "current"),
        ("_baseline", "baseline"),
        ("_legacy", "legacy"),
        ("_current", "current"),
    ):
        if not stem.endswith(suffix):
            continue
        prefix = stem[: -len(suffix)]
        if "_" not in prefix:
            return canonical_variant_id(variant_id), None
        prefix_run_id, case_id = prefix.rsplit("_", 1)
        if prefix_run_id == run_id:
            return canonical_variant_id(variant_id), case_id

    return None, None


def load_run_results(evals_dir: Path, skill_id: str, run_id: str) -> dict[str, list[dict[str, Any]]]:
    """1 回の run に属する grading result を variant 別に読み込む。"""
    run_dir = evals_dir / skill_id / "runs"
    if not run_dir.exists():
        raise FileNotFoundError(f"Runs directory not found: {run_dir}")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(run_dir.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"WARNING: Skipping malformed JSON in {path}: {exc}", file=sys.stderr)
            data = {}

        embedded_run_id = str(data.get("run_id") or "")
        inferred_variant_id, inferred_case_id = parse_result_filename(path, run_id)
        if embedded_run_id and embedded_run_id != run_id:
            print(
                f"WARNING: Skipping run result with mismatched run_id in {path}: {embedded_run_id}",
                file=sys.stderr,
            )
            continue
        if not embedded_run_id and inferred_variant_id is None:
            continue

        variant_id = str(data.get("variant_id") or data.get("mode") or "")
        case_id = str(data.get("case_id") or "")

        if not variant_id or not case_id:
            variant_id = variant_id or (inferred_variant_id or "")
            case_id = case_id or (inferred_case_id or "")

        if not variant_id or not case_id:
            print(f"WARNING: Skipping unreadable run result file: {path}", file=sys.stderr)
            continue

        canonical = canonical_variant_id(variant_id)
        data = {
            **data,
            "variant_id": canonical,
            "mode": canonical,
            "case_id": case_id,
        }
        grouped[canonical].append(data)

    if not grouped:
        raise ValueError(f"No run results found for run '{run_id}' in {run_dir}")

    for results in grouped.values():
        results.sort(key=lambda item: item["case_id"])

    return dict(grouped)


def load_evals_json(evals_dir: Path, skill_id: str) -> dict[str, dict[str, Any]]:
    """`evals.json` を case_id キーの辞書として読み込む。なければ空辞書を返す。"""
    path = evals_dir / skill_id / "evals.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {case["id"]: case for case in data.get("cases", [])}


def compute_file_sha256(path: Path) -> str | None:
    """ファイル内容の SHA-256 を返す。存在しなければ None。"""
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scores(results: list[dict[str, Any]]) -> list[float]:
    """null でない score だけを取り出す。"""
    return [r["score"] for r in results if r.get("score") is not None]


def compute_stats(results: list[dict[str, Any]]) -> dict[str, Any]:
    """scores から集計値を計算する。"""
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


def build_comparison(lhs: dict[str, Any] | None, rhs: dict[str, Any] | None, lhs_name: str, rhs_name: str) -> dict[str, Any] | None:
    """2 つの variant 集計を比較する。"""
    if not lhs or not rhs:
        return None
    lhs_mean = lhs.get("mean")
    rhs_mean = rhs.get("mean")
    if lhs_mean is None or rhs_mean is None:
        return None

    delta = round(lhs_mean - rhs_mean, 4)
    improvement_pct = round((delta / rhs_mean) * 100, 2) if rhs_mean != 0 else None
    return {
        "lhs": lhs_name,
        "rhs": rhs_name,
        "delta": delta,
        "improvement_pct": improvement_pct,
        "verdict": compute_verdict(delta),
    }


def _pick_reference_variant(available: set[str]) -> str:
    """ギャップ分析の基準となる variant を選ぶ。"""
    if "legacy" in available and "current" in available:
        return "legacy"
    if "baseline" in available:
        return "baseline"
    if "legacy" in available:
        return "legacy"
    return sorted(available)[0]


def _pick_primary_variant(available: set[str]) -> tuple[str, str] | None:
    """summary の主比較対象を決める。"""
    if "current" in available and "legacy" in available:
        return "current", "legacy"
    if "current" in available and "baseline" in available:
        return "current", "baseline"
    if "legacy" in available and "baseline" in available:
        return "legacy", "baseline"

    ordered = [variant for variant in VARIANT_PRIORITY if variant in available]
    if len(ordered) >= 2:
        return ordered[0], ordered[1]
    return None


def _format_gap_message(assertion_type: str, value: str) -> str:
    templates = {
        "contains": "スキル固有のキーワード・コマンド名の知識が不足（「{value}」が回答に現れない）",
        "not_contains": "アンチパターン防止の知識が不足（「{value}」を使ってしまう）",
        "llm_grade": "推論・判断力が不足（{value}）",
    }
    template = templates.get(assertion_type, "「{value}」の条件を満たせない")
    return template.format(value=value[:80])


def _generate_recommendation(failures: list[dict[str, str]]) -> str:
    """reference variant の assertion failure から推奨文を作る。"""
    if not failures:
        return "基準版も十分な回答を生成できています。汎用知識で対応可能なケースです。"

    parts: list[str] = []
    has_contains = any(f["type"] == "contains" for f in failures)
    has_not_contains = any(f["type"] == "not_contains" for f in failures)
    has_llm = any(f["type"] == "llm_grade" for f in failures)

    if has_contains:
        values = [f["value"] for f in failures if f["type"] == "contains"]
        parts.append(f"variant の説明に専門知識（{', '.join(values[:3])}）を明示すると発火率が上がります。")
    if has_not_contains:
        values = [f["value"] for f in failures if f["type"] == "not_contains"]
        parts.append(f"Anti-Patterns セクションに「{', '.join(values[:3])}」を避ける理由を追記すると効果的です。")
    if has_llm:
        parts.append("Decision Table やステップ説明を充実させると、AI の推論精度が向上します。")

    return "　".join(parts)


def build_case_breakdown(
    results_by_variant: dict[str, list[dict[str, Any]]],
    evals_meta: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """case_id ごとの比較結果に prompt と assertion 詳細を付与して返す。"""
    available = set(results_by_variant)
    primary = _pick_primary_variant(available)
    primary_lhs = primary[0] if primary else None
    primary_rhs = primary[1] if primary else None
    reference_variant = _pick_reference_variant(available)
    compat_variant = "current" if "current" in available else "legacy" if "legacy" in available else "baseline"

    by_variant_case = {
        variant: {result["case_id"]: result for result in results}
        for variant, results in results_by_variant.items()
    }
    case_ids = sorted(set().union(*(case_map.keys() for case_map in by_variant_case.values())) | set(evals_meta.keys()))

    breakdown: list[dict[str, Any]] = []
    for case_id in case_ids:
        meta = evals_meta.get(case_id, {})
        eval_assertions = meta.get("assertions", [])

        variant_results: dict[str, dict[str, Any]] = {}
        for variant in VARIANT_PRIORITY + tuple(sorted(available - set(VARIANT_PRIORITY))):
            result = by_variant_case.get(variant, {}).get(case_id)
            if not result:
                continue
            variant_results[variant] = {
                "score": result.get("score"),
                "response_snippet": result.get("response_snippet", ""),
                "assertions": result.get("assertions", []),
            }

        assertion_detail: list[dict[str, Any]] = []
        for index, assertion in enumerate(eval_assertions):
            detail = {
                "type": assertion.get("type", ""),
                "value": assertion.get("value", ""),
                "weight": assertion.get("weight", 1.0),
                "results": {},
            }
            for variant in sorted(available):
                result = by_variant_case.get(variant, {}).get(case_id)
                if not result:
                    continue
                variant_assertions = result.get("assertions", [])
                if index < len(variant_assertions):
                    a = variant_assertions[index]
                    detail["results"][variant] = {
                        "passed": a.get("passed"),
                        "detail": a.get("detail", ""),
                    }

            detail["baseline_passed"] = detail["results"].get("baseline", {}).get("passed")
            detail["legacy_passed"] = detail["results"].get("legacy", {}).get("passed")
            detail["current_passed"] = detail["results"].get("current", {}).get("passed")
            detail["with_skill_passed"] = detail["results"].get(compat_variant, {}).get("passed")

            detail["detail"] = (
                detail["results"].get(reference_variant, {}).get("detail")
                or detail["results"].get("current", {}).get("detail")
                or detail["results"].get("legacy", {}).get("detail")
                or detail["results"].get("baseline", {}).get("detail")
                or ""
            )
            assertion_detail.append(detail)

        reference_failures = [
            {"type": item["type"], "value": item["value"]}
            for item in assertion_detail
            if item["results"].get(reference_variant, {}).get("passed") is False
        ]
        gap_summary = [_format_gap_message(item["type"], item["value"]) for item in reference_failures]
        recommendation = _generate_recommendation(reference_failures)

        primary_delta = None
        if primary_lhs and primary_rhs:
            lhs_score = variant_results.get(primary_lhs, {}).get("score")
            rhs_score = variant_results.get(primary_rhs, {}).get("score")
            if lhs_score is not None and rhs_score is not None:
                primary_delta = round(lhs_score - rhs_score, 4)

        current_mean = variant_results.get("current", {}).get("score")
        legacy_mean = variant_results.get("legacy", {}).get("score")
        baseline_mean = variant_results.get("baseline", {}).get("score")
        primary_mean = variant_results.get(primary_lhs, {}).get("score") if primary_lhs else None
        reference_mean = variant_results.get(reference_variant, {}).get("score")
        compat_mean = variant_results.get(compat_variant, {}).get("score")

        breakdown.append({
            "case_id": case_id,
            "prompt": meta.get("prompt", ""),
            "tags": meta.get("tags", []),
            "variant_results": variant_results,
            "baseline_mean": baseline_mean,
            "legacy_mean": legacy_mean,
            "current_mean": current_mean,
            "with_skill_mean": compat_mean,
            "primary_mean": primary_mean,
            "reference_mean": reference_mean,
            "delta": primary_delta,
            "current_vs_legacy_delta": (
                round(current_mean - legacy_mean, 4)
                if current_mean is not None and legacy_mean is not None
                else None
            ),
            "current_vs_baseline_delta": (
                round(current_mean - baseline_mean, 4)
                if current_mean is not None and baseline_mean is not None
                else None
            ),
            "legacy_vs_baseline_delta": (
                round(legacy_mean - baseline_mean, 4)
                if legacy_mean is not None and baseline_mean is not None
                else None
            ),
            "assertion_detail": assertion_detail,
            "current_snippet": variant_results.get("current", {}).get("response_snippet", ""),
            "with_skill_snippet": variant_results.get(compat_variant, {}).get("response_snippet", ""),
            "legacy_snippet": variant_results.get("legacy", {}).get("response_snippet", ""),
            "baseline_snippet": variant_results.get("baseline", {}).get("response_snippet", ""),
            "gap_summary": gap_summary,
            "recommendation": recommendation,
            "reference_variant": reference_variant,
            "primary_comparison": f"{primary_lhs}_vs_{primary_rhs}" if primary_lhs and primary_rhs else None,
        })

    return breakdown


def append_history_record(
    ledger_path: Path,
    record: dict[str, Any],
) -> None:
    """履歴 ledger に 1 行追記する。"""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def collect_variant_metadata(results_by_variant: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """run result から variant ごとの再現性 metadata を抽出する。"""
    metadata_by_variant: dict[str, dict[str, Any]] = {}
    for variant, results in results_by_variant.items():
        metadata: dict[str, Any] = {}
        for key in ("source_ref", "skill_snapshot_hash", "commit_sha", "model_id"):
            value = next((item.get(key) for item in results if item.get(key) is not None), None)
            if value is not None:
                metadata[key] = value
        if metadata:
            metadata_by_variant[variant] = metadata
    return metadata_by_variant


def aggregate(
    evals_dir: Path,
    skill_id: str,
    run_id: str,
    eval_version: str = "1.0.0",
    campaign_id: str | None = None,
    commit_sha: str | None = None,
    model_id: str | None = None,
) -> dict[str, Any]:
    """run 結果を集計して benchmark summary を作る。"""
    results_by_variant = load_run_results(evals_dir, skill_id, run_id)
    evals_meta = load_evals_json(evals_dir, skill_id)
    suite_hash = compute_file_sha256(evals_dir / skill_id / "evals.json")
    variant_metadata = collect_variant_metadata(results_by_variant)

    variant_stats = {variant: compute_stats(results) for variant, results in results_by_variant.items()}
    comparisons = {
        "current_vs_legacy": build_comparison(variant_stats.get("current"), variant_stats.get("legacy"), "current", "legacy"),
        "current_vs_baseline": build_comparison(variant_stats.get("current"), variant_stats.get("baseline"), "current", "baseline"),
        "legacy_vs_baseline": build_comparison(variant_stats.get("legacy"), variant_stats.get("baseline"), "legacy", "baseline"),
    }
    comparisons = {key: value for key, value in comparisons.items() if value is not None}

    primary_key = next((key for key in ("current_vs_legacy", "current_vs_baseline", "legacy_vs_baseline") if key in comparisons), None)
    primary_delta = comparisons[primary_key]["delta"] if primary_key else None
    primary_improvement_pct = comparisons[primary_key]["improvement_pct"] if primary_key else None
    primary_verdict = comparisons[primary_key]["verdict"] if primary_key else "neutral"

    runs = dict(variant_stats)
    if "current" in variant_stats:
        runs["with_skill"] = variant_stats["current"]
    elif "legacy" in variant_stats:
        runs["with_skill"] = variant_stats["legacy"]
    elif "baseline" in variant_stats:
        runs["with_skill"] = variant_stats["baseline"]

    summary = {
        "skill_id": skill_id,
        "eval_version": eval_version,
        "campaign_id": campaign_id or run_id,
        "variants": variant_stats,
        "runs": runs,
        "comparisons": comparisons,
        "summary": {
            "delta": primary_delta,
            "improvement_pct": primary_improvement_pct,
            "verdict": primary_verdict,
            "primary_comparison": primary_key,
        },
        "case_breakdown": build_case_breakdown(results_by_variant, evals_meta),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if suite_hash is not None:
        summary["suite_hash"] = suite_hash
    if variant_metadata:
        summary["variant_metadata"] = variant_metadata

    if commit_sha is not None:
        summary["commit_sha"] = commit_sha
    if model_id is not None:
        summary["model_id"] = model_id

    return summary


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
    parser.add_argument(
        "--campaign-id",
        default=None,
        help="履歴 ledger で使う campaign ID（既定: run-id）",
    )
    parser.add_argument(
        "--history-ledger",
        default=None,
        help="append-only 履歴 ledger の出力先（既定: evals/<skill_id>/benchmark_history.jsonl）",
    )
    parser.add_argument("--commit-sha", default=None, help="履歴に記録する commit SHA")
    parser.add_argument("--model-id", default=None, help="履歴に記録する model ID")
    return parser.parse_args()


def main() -> int:
    """CLI から benchmark 集計を実行する。"""
    args = parse_args()
    evals_dir = Path(args.evals_dir)

    try:
        result = aggregate(
            evals_dir=evals_dir,
            skill_id=args.skill_id,
            run_id=args.run_id,
            eval_version=args.eval_version,
            campaign_id=args.campaign_id,
            commit_sha=args.commit_sha,
            model_id=args.model_id,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out_path = evals_dir / args.skill_id / "benchmark_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    ledger_path = Path(args.history_ledger) if args.history_ledger else evals_dir / args.skill_id / "benchmark_history.jsonl"
    append_history_record(
        ledger_path,
        {
            "skill_id": args.skill_id,
            "campaign_id": args.campaign_id or args.run_id,
            "run_id": args.run_id,
            "eval_version": args.eval_version,
            "suite_hash": result.get("suite_hash"),
            "commit_sha": args.commit_sha,
            "model_id": args.model_id,
            "generated_at": result["generated_at"],
            "summary": result["summary"],
            "variants": result["variants"],
            "comparisons": result["comparisons"],
            "variant_metadata": result.get("variant_metadata", {}),
        },
    )

    verdict = result["summary"]["verdict"]
    delta = result["summary"]["delta"]
    print(f"benchmark_summary.json written → {out_path}")
    print(f"benchmark_history.jsonl appended → {ledger_path}")
    print(f"Verdict: {verdict}  |  Delta: {delta:+.4f}" if delta is not None else f"Verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
