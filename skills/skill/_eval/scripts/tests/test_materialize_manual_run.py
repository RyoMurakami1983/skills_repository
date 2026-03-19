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
