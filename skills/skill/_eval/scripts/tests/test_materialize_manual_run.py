from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "materialize_manual_run.py"
    spec = importlib.util.spec_from_file_location("materialize_manual_run", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_materialize_run_creates_expected_files(tmp_path: Path):
    mod = load_module()
    evals_path = tmp_path / "evals.json"
    manual_path = tmp_path / "manual.json"
    evals_dir = tmp_path / "evals"

    evals_path.write_text(
        json.dumps(
            {
                "skill_id": "sample",
                "cases": [
                    {
                        "id": "tc-001",
                        "prompt": "プルリクして",
                        "assertions": [
                            {"type": "contains", "value": "github-pr-workflow", "weight": 1.0},
                            {"type": "llm_grade", "value": "route is correct", "weight": 1.0},
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manual_path.write_text(
        json.dumps(
            {
                "run_id": "run-001",
                "responses": {
                    "with_skill": {"tc-001": "github-pr-workflow で進めます"},
                    "baseline": {"tc-001": "github-pr-workflow で進めます"},
                },
                "llm_grade": {
                    "with_skill": {"tc-001": [{"passed": True, "detail": "ok"}]},
                    "baseline": {"tc-001": [{"passed": False, "detail": "ng"}]},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    created = mod.materialize_run(evals_path, manual_path, "sample", evals_dir)

    assert len(created) == 2
    result = json.loads((evals_dir / "sample" / "runs" / "run-001_tc-001_with_skill.json").read_text(encoding="utf-8"))
    assert result["score"] == 1.0
    assert result["assertions"][1]["detail"] == "ok"


def test_materialize_run_supports_baseline_legacy_current_layout(tmp_path: Path):
    mod = load_module()
    evals_path = tmp_path / "evals.json"
    manual_path = tmp_path / "manual.json"
    evals_dir = tmp_path / "evals"

    evals_path.write_text(
        json.dumps(
            {
                "skill_id": "sample",
                "cases": [
                    {
                        "id": "tc-001",
                        "prompt": "プルリクして",
                        "assertions": [
                            {"type": "contains", "value": "github-pr-workflow", "weight": 1.0},
                            {"type": "regex", "value": "workflow", "weight": 1.0},
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manual_path.write_text(
        json.dumps(
            {
                "run_id": "run-002",
                "responses": {
                    "baseline": {"tc-001": "github-pr-workflow baseline"},
                    "legacy": {"tc-001": "github-pr-workflow legacy"},
                    "current": {"tc-001": "github-pr-workflow current"},
                },
                "llm_grade": {
                    "baseline": {"tc-001": []},
                    "legacy": {"tc-001": []},
                    "current": {"tc-001": []},
                },
                "variant_meta": {
                    "legacy": {
                        "source_ref": "git:abc123",
                        "skill_snapshot_hash": "legacy-hash",
                    },
                    "current": {
                        "source_ref": "worktree:feature/test",
                        "skill_snapshot_hash": "current-hash",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    created = mod.materialize_run(evals_path, manual_path, "sample", evals_dir)

    assert len(created) == 3
    result = json.loads((evals_dir / "sample" / "runs" / "run-002__current__tc-001.json").read_text(encoding="utf-8"))
    assert result["variant_id"] == "current"
    assert result["score"] == 1.0
    assert result["source_ref"] == "worktree:feature/test"
    assert result["skill_snapshot_hash"] == "current-hash"


def test_materialize_run_supports_starts_with_and_ends_with(tmp_path: Path):
    mod = load_module()
    evals_path = tmp_path / "evals.json"
    manual_path = tmp_path / "manual.json"
    evals_dir = tmp_path / "evals"

    evals_path.write_text(
        json.dumps(
            {
                "skill_id": "sample",
                "cases": [
                    {
                        "id": "tc-010",
                        "prompt": "check edges",
                        "assertions": [
                            {"type": "starts_with", "value": "Route:", "weight": 1.0},
                            {"type": "ends_with", "value": "done", "weight": 1.0},
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manual_path.write_text(
        json.dumps(
            {
                "run_id": "run-010",
                "responses": {
                    "current": {"tc-010": "   Route: check done   "},
                },
                "llm_grade": {
                    "current": {"tc-010": []},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    mod.materialize_run(evals_path, manual_path, "sample", evals_dir)
    result = json.loads((evals_dir / "sample" / "runs" / "run-010__current__tc-010.json").read_text(encoding="utf-8"))

    assert result["score"] == 1.0
    assert [item["passed"] for item in result["assertions"]] == [True, True]


def test_materialize_run_raises_for_invalid_regex(tmp_path: Path):
    mod = load_module()
    evals_path = tmp_path / "evals.json"
    manual_path = tmp_path / "manual.json"
    evals_dir = tmp_path / "evals"

    evals_path.write_text(
        json.dumps(
            {
                "skill_id": "sample",
                "cases": [
                    {
                        "id": "tc-011",
                        "prompt": "bad regex",
                        "assertions": [
                            {"type": "regex", "value": "(", "weight": 1.0},
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    manual_path.write_text(
        json.dumps(
            {
                "run_id": "run-011",
                "responses": {
                    "current": {"tc-011": "anything"},
                },
                "llm_grade": {
                    "current": {"tc-011": []},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    try:
        mod.materialize_run(evals_path, manual_path, "sample", evals_dir)
    except ValueError as exc:
        assert "Invalid regex pattern for case tc-011" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid regex")
