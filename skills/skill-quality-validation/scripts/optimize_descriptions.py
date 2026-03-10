#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""optimize_descriptions.py

Scan SKILL.md files for W7-failing descriptions and generate improved ones.

Usage:
    # Report all W7 failures (dry-run)
    python skills/skill-quality-validation/scripts/optimize_descriptions.py

    # Report as JSON
    python skills/skill-quality-validation/scripts/optimize_descriptions.py --output json

    # Apply rule-based improvements to all failing skills
    python skills/skill-quality-validation/scripts/optimize_descriptions.py --apply

    # Single skill, LLM-powered improvement (requires gh auth + GitHub Models access)
    python skills/skill-quality-validation/scripts/optimize_descriptions.py \\
        --skill-id skills-author-skill --provider github-models

    # Limit to a specific directory
    python skills/skill-quality-validation/scripts/optimize_descriptions.py \\
        --skills-dir skills/
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# W7 check constants (mirrored from validate_skill.py for standalone use)
# ---------------------------------------------------------------------------

_W7_MIN_LENGTH = 80

_ACTION_VERBS = re.compile(
    r'\b('
    r'add|analyze|apply|audit|automate|bootstrap|build|capture|check|commit|'
    r'configure|create|define|deploy|detect|enforce|establish|execute|explain|'
    r'format|generate|guide|handle|implement|initialize|install|integrate|'
    r'maintain|manage|migrate|monitor|onboard|protect|report|respond|restore|'
    r'review|revise|run|scan|scaffold|set\s+up|setup|standardize|sync|track|'
    r'update|use|validate|write'
    r')\b',
    re.IGNORECASE,
)

_COMMA_CLAUSE = re.compile(r',\s*(?:or\s+)?(?:\w+\s+){0,3}\w+')


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class W7Result:
    passes_w7_1: bool  # length ≥ 80
    passes_w7_2: bool  # has action verb
    passes_w7_3: bool  # ≥ 2 comma-separated items
    length: int
    current_desc: str

    @property
    def passes_all(self) -> bool:
        return self.passes_w7_1 and self.passes_w7_2 and self.passes_w7_3

    @property
    def failing_ids(self) -> list[str]:
        ids = []
        if not self.passes_w7_1:
            ids.append("W7.1")
        if not self.passes_w7_2:
            ids.append("W7.2")
        if not self.passes_w7_3:
            ids.append("W7.3")
        return ids


@dataclass
class SkillScanResult:
    skill_id: str
    file_path: str
    w7: W7Result
    suggested_desc: str = ""
    applied: bool = False


@dataclass
class ScanReport:
    total: int = 0
    passing: int = 0
    failing: int = 0
    results: list[SkillScanResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return (self.passing / self.total * 100) if self.total else 0.0


# ---------------------------------------------------------------------------
# Frontmatter + section parsing
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter as a simple key→value dict (single level)."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end < 0:
        return {}
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def _extract_when_to_use(content: str) -> list[str]:
    """Return bullet-point lines from the 'When to Use This Skill' section."""
    lines = content.splitlines()
    in_section = False
    bullets: list[str] = []
    fence_open = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            fence_open = not fence_open
            continue
        if fence_open:
            continue
        if re.match(r'^##\s+When to Use This Skill', stripped):
            in_section = True
            continue
        if in_section:
            if re.match(r'^##\s+', stripped) and not re.match(r'^###', stripped):
                break  # next H2 = end of section
            if stripped.startswith(("- ", "* ", "+ ")):
                text = re.sub(r'^[-*+]\s+', '', stripped)
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # strip bold
                text = text.rstrip('.')
                if text:
                    bullets.append(text)
    return bullets


# ---------------------------------------------------------------------------
# W7 checker
# ---------------------------------------------------------------------------

def check_w7(desc: str) -> W7Result:
    length = len(desc)
    has_verb = bool(_ACTION_VERBS.search(desc))
    clauses = _COMMA_CLAUSE.findall(desc)
    item_count = len(clauses) + 1 if clauses else 0
    return W7Result(
        passes_w7_1=length >= _W7_MIN_LENGTH,
        passes_w7_2=has_verb,
        passes_w7_3=item_count >= 2,
        length=length,
        current_desc=desc,
    )


# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------

@runtime_checkable
class DescriptionProvider(Protocol):
    def improve(self, skill_name: str, current_desc: str, when_to_use: list[str]) -> str:
        ...


class RuleBasedProvider:
    """Deterministic description generator — no API key required.

    Algorithm:
    1. Infer the primary verb from the skill name.
    2. Take up to 4 'When to Use' bullets as capability phrases.
    3. Compose: "Use when {verb}ing — {cap1}, {cap2}, {cap3}."
    4. Guarantee W7.1 ≥80 chars / W7.2 verb / W7.3 ≥2 items.
    """

    # Map skill-name segments to a canonical action verb.
    _VERB_MAP: dict[str, str] = {
        "author": "author",
        "validate": "validate",
        "revise": "revise",
        "review": "review",
        "generate": "generate",
        "deploy": "deploy",
        "capture": "capture",
        "optimize": "optimize",
        "maintain": "maintain",
        "index": "index",
        "intake": "capture",
        "init": "initialize",
        "setup": "set up",
        "commit": "commit",
        "pr": "create",
        "response": "respond",
        "workflow": "run",
        "autopilot": "automate",
        "batch": "run",
        "explain": "explain",
        "label": "standardize",
        "quality": "validate",
        "eval": "evaluate",
        "pipeline": "run",
        "notion": "manage",
        "furikaeri": "run",
        "knowledge": "capture",
        "evidence": "generate",
        "practice": "run",
        "safe": "manage",
        "suite": "generate",
    }

    def _infer_verb(self, skill_name: str) -> str:
        parts = skill_name.lower().replace("_", "-").split("-")
        for part in parts:
            if part in self._VERB_MAP:
                return self._VERB_MAP[part]
        # Fallback: last meaningful segment
        meaningful = [p for p in parts if len(p) > 3 and p not in ("skill", "skills", "with", "from", "into")]
        if meaningful:
            return meaningful[-1]
        return "use"

    def _shorten_bullet(self, text: str, max_len: int = 60) -> str:
        """Trim a bullet to a readable short phrase."""
        # Strip leading 'Use when ...' to avoid nesting
        text = re.sub(r'^[Uu]se when\s+', '', text)
        # Keep only up to the first clause boundary
        for sep in ('.', ';', '—', ' — ', ' - ', '('):
            if sep in text:
                text = text[:text.index(sep)]
        text = text.strip().rstrip(',')
        return text[:max_len]

    def improve(self, skill_name: str, current_desc: str, when_to_use: list[str]) -> str:
        verb = self._infer_verb(skill_name)

        # Pick up to 4 bullets for capabilities
        caps = [self._shorten_bullet(b) for b in when_to_use[:4] if b]
        caps = [c for c in caps if len(c) > 5][:4]

        if len(caps) < 2:
            # Fall back to generic capability phrases derived from skill name
            parts = [p for p in skill_name.split("-") if p not in ("skill", "skills", "git", "github")]
            caps = [p.replace("-", " ") for p in parts[:3]]
            while len(caps) < 2:
                caps.append(f"{verb} tasks")

        # Compose description
        caps_str = ", ".join(caps)
        desc = f"Use when {verb}ing a skill — {caps_str}."

        # Ensure W7.1 (≥80 chars): pad with more detail if needed
        if len(desc) < _W7_MIN_LENGTH:
            extra = f" Covers {verb}ing workflows, quality checks, and best-practice guidance."
            desc = desc.rstrip('.') + extra

        # Final safety: truncate at 512 to avoid overly long descriptions
        return desc[:512]


class GitHubModelsProvider:
    """LLM-powered description generator via GitHub Models API (gh api).

    Requires:
    - gh CLI authenticated with a token that has models:read scope
    - GitHub Models beta access on the account

    Falls back to RuleBasedProvider on any error.
    """

    _MODEL = "openai/gpt-4.1-mini"
    _FALLBACK = RuleBasedProvider()

    def _build_prompt(self, skill_name: str, current_desc: str, when_to_use: list[str]) -> str:
        bullets = "\n".join(f"- {b}" for b in when_to_use[:5])
        return (
            f"You are a GitHub Copilot skill description writer.\n"
            f"Skill name: {skill_name}\n"
            f"Current description: {current_desc!r}\n"
            f"When to use bullets:\n{bullets}\n\n"
            f"Write ONE improved description string (no quotes, no extra text) that:\n"
            f"1. Is ≥80 characters\n"
            f"2. Starts with 'Use when' followed by an action verb\n"
            f"3. Lists ≥2 comma-separated capability phrases\n"
            f"4. Is ≤200 characters\n"
            f"Output only the description string."
        )

    def improve(self, skill_name: str, current_desc: str, when_to_use: list[str]) -> str:
        prompt = self._build_prompt(skill_name, current_desc, when_to_use)
        payload = {
            "model": self._MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.3,
        }
        try:
            result = subprocess.run(
                ["gh", "api", "https://models.inference.ai.azure.com/chat/completions",
                 "--method", "POST",
                 "--input", "-"],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip())
            data = json.loads(result.stdout)
            return data["choices"][0]["message"]["content"].strip().strip('"')
        except Exception as exc:
            print(f"  [github-models] Error: {exc} — falling back to rule-based", file=sys.stderr)
            return self._FALLBACK.improve(skill_name, current_desc, when_to_use)


def make_provider(name: str) -> DescriptionProvider:
    if name == "github-models":
        return GitHubModelsProvider()
    return RuleBasedProvider()


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def find_skill_files(skills_dir: Path) -> list[Path]:
    """Return sorted list of SKILL.md paths (excludes SKILL.ja.md)."""
    return sorted(
        p for p in skills_dir.rglob("SKILL.md")
        if not p.name.endswith(".ja.md")
    )


def scan_skill(path: Path, provider: DescriptionProvider) -> SkillScanResult:
    content = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    desc = fm.get("description", "")
    skill_id = path.parent.name

    w7 = check_w7(desc)
    suggested = ""
    if not w7.passes_all:
        when_to_use = _extract_when_to_use(content)
        suggested = provider.improve(skill_id, desc, when_to_use)

    return SkillScanResult(
        skill_id=skill_id,
        file_path=str(path),
        w7=w7,
        suggested_desc=suggested,
    )


def scan_all(skills_dir: Path, provider: DescriptionProvider, skill_id_filter: str | None) -> ScanReport:
    paths = find_skill_files(skills_dir)
    if skill_id_filter:
        paths = [p for p in paths if p.parent.name == skill_id_filter]

    report = ScanReport(total=len(paths))
    for path in paths:
        result = scan_skill(path, provider)
        report.results.append(result)
        if result.w7.passes_all:
            report.passing += 1
        else:
            report.failing += 1

    return report


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_improvement(result: SkillScanResult) -> bool:
    """Overwrite the description field in the SKILL.md frontmatter."""
    if not result.suggested_desc or result.w7.passes_all:
        return False
    path = Path(result.file_path)
    content = path.read_text(encoding="utf-8")

    # Replace description: "..." or description: '...' or description: bare value
    new_line = f'description: "{result.suggested_desc}"'
    # Match both quoted and unquoted single-line description
    patched, count = re.subn(
        r'^description:[ \t].*$',
        new_line,
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _w7_badge(passes: bool) -> str:
    return "✅" if passes else "❌"


def print_text_report(report: ScanReport, dry_run: bool) -> None:
    mode = "(dry-run)" if dry_run else "(applied)"
    print(f"\n## Description Quality Report {mode}")
    print(f"Total: {report.total}  Passing: {report.passing}  Failing: {report.failing}  "
          f"Pass rate: {report.pass_rate:.1f}%\n")

    if not report.results:
        print("No SKILL.md files found.")
        return

    for r in sorted(report.results, key=lambda x: (x.w7.passes_all, x.skill_id)):
        status = "✅ PASS" if r.w7.passes_all else f"❌ FAIL [{', '.join(r.w7.failing_ids)}]"
        applied = " (applied)" if r.applied else ""
        print(f"### {r.skill_id}  {status}{applied}")
        print(f"  Current : {r.w7.current_desc[:100]!r}  ({r.w7.length} chars)")
        if not r.w7.passes_all and r.suggested_desc:
            w7_check = check_w7(r.suggested_desc)
            badges = (f"W7.1{_w7_badge(w7_check.passes_w7_1)} "
                      f"W7.2{_w7_badge(w7_check.passes_w7_2)} "
                      f"W7.3{_w7_badge(w7_check.passes_w7_3)}")
            print(f"  Suggest : {r.suggested_desc[:100]!r}  ({len(r.suggested_desc)} chars)  {badges}")
        print()


def print_json_report(report: ScanReport) -> None:
    def _to_dict(r: SkillScanResult) -> dict:
        return {
            "skill_id": r.skill_id,
            "file_path": r.file_path,
            "passes_all": r.w7.passes_all,
            "failing_ids": r.w7.failing_ids,
            "current_desc": r.w7.current_desc,
            "length": r.w7.length,
            "suggested_desc": r.suggested_desc,
            "applied": r.applied,
        }

    out = {
        "summary": {
            "total": report.total,
            "passing": report.passing,
            "failing": report.failing,
            "pass_rate_pct": round(report.pass_rate, 1),
        },
        "results": [_to_dict(r) for r in report.results],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan and improve SKILL.md descriptions to pass W7 quality checks"
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="Root directory to scan for SKILL.md files (default: auto-detect repo root / skills/)",
    )
    parser.add_argument(
        "--skill-id",
        default=None,
        help="Process only the skill with this directory name",
    )
    parser.add_argument(
        "--provider",
        choices=["rule", "github-models"],
        default="rule",
        help="Description generation provider (default: rule — no API key required)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write improved descriptions back to SKILL.md files (default: dry-run)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser.parse_args()


def _resolve_skills_dir(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    # Walk up from this script to find repo root (contains PHILOSOPHY.md)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "PHILOSOPHY.md").exists():
            candidate = parent / "skills"
            if candidate.exists():
                return candidate
    # Fallback: cwd/skills or cwd
    fallback = Path.cwd() / "skills"
    return fallback if fallback.exists() else Path.cwd()


def main() -> int:
    # Ensure UTF-8 on Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    args = parse_args()
    skills_dir = _resolve_skills_dir(args.skills_dir)

    if not skills_dir.exists():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    provider = make_provider(args.provider)
    report = scan_all(skills_dir, provider, args.skill_id)

    if args.apply:
        for result in report.results:
            if not result.w7.passes_all and result.suggested_desc:
                result.applied = apply_improvement(result)

    if args.output == "json":
        print_json_report(report)
    else:
        print_text_report(report, dry_run=not args.apply)

    return 0 if report.failing == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
