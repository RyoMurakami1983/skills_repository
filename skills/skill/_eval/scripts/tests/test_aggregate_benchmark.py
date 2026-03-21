from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "aggregate_benchmark.py"
    spec = importlib.util.spec_from_file_location("aggregate_benchmark", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_aggregate_supports_baseline_legacy_current_and_history(tmp_path: Path):
    mod = load_module()
    evals_dir = tmp_path / "evals"
    skill_id = "sample"
    run_id = "run-003"
    runs_dir = evals_dir / skill_id / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    (evals_dir / skill_id / "evals.json").write_text(
        json.dumps(
            {
                "skill_id": skill_id,
                "cases": [
                    {
                        "id": "tc-001",
                        "prompt": "variant compare",
                        "tags": ["should-trigger"],
                        "assertions": [
                            {"type": "contains", "value": "ok", "weight": 1.0},
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    payloads = {
        "baseline": {"score": 0.7, "passed": False},
        "legacy": {"score": 0.8, "passed": True},
        "current": {"score": 0.9, "passed": True},
    }

    for variant_id, payload in payloads.items():
        (runs_dir / f"{run_id}__{variant_id}__tc-001.json").write_text(
            json.dumps(
                {
                    "case_id": "tc-001",
                    "run_id": run_id,
                    "variant_id": variant_id,
                    "mode": variant_id,
                    "score": payload["score"],
                    "assertions": [
                        {
                            "type": "contains",
                            "passed": payload["passed"],
                            "weight": 1.0,
                            "detail": f"{variant_id} detail",
                        }
                    ],
                    "response_snippet": f"{variant_id} response",
                    "timestamp": "2026-03-20T00:00:00Z",
                    "source_ref": f"ref:{variant_id}",
                    "skill_snapshot_hash": f"hash-{variant_id}",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    result = mod.aggregate(
        evals_dir=evals_dir,
        skill_id=skill_id,
        run_id=run_id,
        eval_version="2.0.0",
        campaign_id="campaign-001",
        commit_sha="abc123",
        model_id="gpt-test",
    )

    assert result["variants"]["baseline"]["mean"] == 0.7
    assert result["variants"]["legacy"]["mean"] == 0.8
    assert result["variants"]["current"]["mean"] == 0.9
    assert result["comparisons"]["current_vs_legacy"]["delta"] == 0.1
    assert result["summary"]["primary_comparison"] == "current_vs_legacy"
    assert result["case_breakdown"][0]["reference_variant"] == "legacy"
    assert result["case_breakdown"][0]["current_vs_legacy_delta"] == 0.1
    assert result["case_breakdown"][0]["gap_summary"] == []
    assert result["suite_hash"] is not None
    assert result["variant_metadata"]["current"]["source_ref"] == "ref:current"
    assert result["variant_metadata"]["legacy"]["skill_snapshot_hash"] == "hash-legacy"

    ledger_path = tmp_path / "benchmark_history.jsonl"
    mod.append_history_record(
        ledger_path,
        {
            "skill_id": skill_id,
            "summary": result["summary"],
            "suite_hash": result["suite_hash"],
            "variant_metadata": result["variant_metadata"],
        },
    )
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["skill_id"] == skill_id


def test_load_run_results_skips_prefix_collisions(tmp_path: Path):
    mod = load_module()
    evals_dir = tmp_path / "evals"
    skill_id = "sample"
    runs_dir = evals_dir / skill_id / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    (runs_dir / "run-003__current__tc-001.json").write_text(
        json.dumps(
            {
                "run_id": "run-003",
                "case_id": "tc-001",
                "variant_id": "current",
                "mode": "current",
                "score": 1.0,
                "assertions": [],
                "response_snippet": "ok",
                "timestamp": "2026-03-21T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (runs_dir / "run-0039__current__tc-999.json").write_text(
        json.dumps(
            {
                "run_id": "run-0039",
                "case_id": "tc-999",
                "variant_id": "current",
                "mode": "current",
                "score": 0.0,
                "assertions": [],
                "response_snippet": "wrong",
                "timestamp": "2026-03-21T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    results = mod.load_run_results(evals_dir, skill_id, "run-003")

    assert list(results) == ["current"]
    assert [item["case_id"] for item in results["current"]] == ["tc-001"]
