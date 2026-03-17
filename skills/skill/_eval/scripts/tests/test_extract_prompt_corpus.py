from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "extract_prompt_corpus.py"
    spec = importlib.util.spec_from_file_location("extract_prompt_corpus", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_anonymize_prompt_replaces_paths_and_urls():
    mod = load_module()

    text = r"プルリクして C:\Users\murak\repo を見て https://example.com/abc"
    result = mod.anonymize_prompt(text)

    assert "<WINDOWS_PATH>" in result
    assert "<URL>" in result
    assert r"C:\Users\murak\repo" not in result
    assert "https://example.com/abc" not in result


def test_anonymize_prompt_redacts_github_identity_markers():
    mod = load_module()

    text = "RyoMurakami1983のprivateリポジトリと RyoMurakami1983/skills_repository を確認して"
    result = mod.anonymize_prompt(text)

    assert "<GITHUB_OWNER>のprivateリポジトリ" in result
    assert "<GITHUB_OWNER>/<GITHUB_REPO>" in result
    assert "RyoMurakami1983" not in result


def test_build_summary_counts_matching_user_messages(tmp_path: Path):
    mod = load_module()
    session_dir = tmp_path / "session-a"
    session_dir.mkdir(parents=True)
    events_path = session_dir / "events.jsonl"
    events_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "user.message",
                        "timestamp": "2026-03-17T00:00:00Z",
                        "data": {"content": "プルリクして"},
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "type": "user.message",
                        "timestamp": "2026-03-17T00:01:00Z",
                        "data": {"content": "commitして"},
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "type": "assistant.message",
                        "timestamp": "2026-03-17T00:02:00Z",
                        "data": {"content": "ignored"},
                    },
                    ensure_ascii=False,
                ),
            ]
        ),
        encoding="utf-8",
    )

    summary = mod.build_summary(tmp_path, mod.re.compile(r"(プルリク|commit)", mod.re.IGNORECASE), limit=10)

    assert summary["sessions_scanned"] == 1
    assert summary["total_user_messages"] == 2
    assert summary["matched_user_messages"] == 2
    assert summary["unique_matched_prompts"] == 2
    assert summary["source_root"] == "<COPILOT_SESSION_ROOT>"
    prompts = {item["prompt"]: item for item in summary["top_prompts"]}
    assert prompts["プルリクして"]["count"] == 1
    assert prompts["commitして"]["count"] == 1
    assert prompts["プルリクして"]["sessions"] == ["session-001"]


def test_build_summary_uses_min_max_timestamps_and_redacts_sessions(tmp_path: Path):
    mod = load_module()
    session_a = tmp_path / "session-z"
    session_b = tmp_path / "session-a"
    session_a.mkdir(parents=True)
    session_b.mkdir(parents=True)
    (session_a / "events.jsonl").write_text(
        json.dumps(
            {
                "type": "user.message",
                "timestamp": "2026-03-17T00:10:00Z",
                "data": {"content": "skillを実装して"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (session_b / "events.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "user.message",
                        "timestamp": "2026-03-17T00:00:00Z",
                        "data": {"content": "skillを実装して"},
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "type": "user.message",
                        "timestamp": "2026-03-17T00:20:00Z",
                        "data": {"content": "skillを実装して"},
                    },
                    ensure_ascii=False,
                ),
            ]
        ),
        encoding="utf-8",
    )

    summary = mod.build_summary(tmp_path, mod.re.compile(r"skill", mod.re.IGNORECASE), limit=10)

    hit = summary["top_prompts"][0]
    assert hit["first_seen"] == "2026-03-17T00:00:00Z"
    assert hit["last_seen"] == "2026-03-17T00:20:00Z"
    assert hit["sessions"] == ["session-001", "session-002"]
