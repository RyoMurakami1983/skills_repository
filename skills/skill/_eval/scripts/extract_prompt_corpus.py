r"""Extract and summarize user prompts from Copilot session events.jsonl files.

Usage:
    uv run python skills/skill/_eval/scripts/extract_prompt_corpus.py ^
        --root "%USERPROFILE%\.copilot\session-state" ^
        --pattern "(PR|プルリク|レビュー|Issue|issue|コミット|commit|main|pull|git初期化|GitHub)" ^
        --limit 50 ^
        --out evals/github/corpus_summary.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*")
URL_RE = re.compile(r"https?://\S+")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class PromptHit:
    prompt: str
    count: int
    sessions: list[str]
    first_seen: str
    last_seen: str


def anonymize_prompt(text: str) -> str:
    text = URL_RE.sub("<URL>", text)
    text = WINDOWS_PATH_RE.sub("<WINDOWS_PATH>", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def iter_user_messages(events_path: Path):
    with events_path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "user.message":
                continue
            data = event.get("data") or {}
            content = (data.get("content") or "").strip()
            if not content:
                continue
            yield {
                "content": content,
                "timestamp": event.get("timestamp", ""),
                "session_id": events_path.parent.name,
            }


def build_summary(root: Path, pattern: re.Pattern[str] | None, limit: int) -> dict:
    counts: Counter[str] = Counter()
    sessions_by_prompt: dict[str, set[str]] = {}
    first_seen: dict[str, str] = {}
    last_seen: dict[str, str] = {}
    session_aliases: dict[str, str] = {}
    total_user_messages = 0
    matched_messages = 0
    sessions_scanned = 0

    def alias_session(session_id: str) -> str:
        if session_id not in session_aliases:
            session_aliases[session_id] = f"session-{len(session_aliases) + 1:03d}"
        return session_aliases[session_id]

    for events_path in sorted(root.rglob("events.jsonl")):
        sessions_scanned += 1
        for item in iter_user_messages(events_path):
            total_user_messages += 1
            normalized = anonymize_prompt(item["content"])
            if pattern and not pattern.search(normalized):
                continue
            matched_messages += 1
            counts[normalized] += 1
            sessions_by_prompt.setdefault(normalized, set()).add(alias_session(item["session_id"]))
            timestamp = item["timestamp"]
            if timestamp:
                previous_first = first_seen.get(normalized)
                if previous_first is None or timestamp < previous_first:
                    first_seen[normalized] = timestamp
                previous_last = last_seen.get(normalized)
                if previous_last is None or timestamp > previous_last:
                    last_seen[normalized] = timestamp

    top_hits = [
        PromptHit(
            prompt=prompt,
            count=count,
            sessions=sorted(sessions_by_prompt.get(prompt, set())),
            first_seen=first_seen.get(prompt, ""),
            last_seen=last_seen.get(prompt, ""),
        )
        for prompt, count in counts.most_common(limit)
    ]

    return {
        "source_root": "<COPILOT_SESSION_ROOT>",
        "filter_pattern": pattern.pattern if pattern else None,
        "sessions_scanned": sessions_scanned,
        "total_user_messages": total_user_messages,
        "matched_user_messages": matched_messages,
        "unique_matched_prompts": len(counts),
        "top_prompts": [asdict(hit) for hit in top_hits],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract user prompt corpus from Copilot session logs")
    parser.add_argument("--root", required=True, help="Root directory containing session-state/**/events.jsonl")
    parser.add_argument("--pattern", default=None, help="Regex filter for prompts (applied after anonymization)")
    parser.add_argument("--limit", type=int, default=50, help="Number of top prompts to keep")
    parser.add_argument("--out", required=True, help="Output JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    out_path = Path(args.out)
    compiled = re.compile(args.pattern, re.IGNORECASE) if args.pattern else None

    summary = build_summary(root, compiled, args.limit)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Corpus summary written -> {out_path}")
    print(f"Matched prompts: {summary['matched_user_messages']} / {summary['total_user_messages']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
