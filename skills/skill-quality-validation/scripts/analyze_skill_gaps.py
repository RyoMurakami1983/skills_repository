#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anthropic Pattern Gap Analyzer

Analyzes skills against patterns extracted from Anthropic's skill-creator
and maps gaps to PHILOSOPHY.md Values.

This tool checks:
  1. Progressive Disclosure score (description, body, references usage)
  2. Orchestration maturity (delegation, sub-agent potential, schema contracts)
  3. Why-driven degree (MUST/ALWAYS/NEVER ratio vs reasoning explanations)
  4. Description trigger quality ([What] + [When] + [Key capabilities])
  5. Environment portability (fallback instructions)
  6. PHILOSOPHY.md Values alignment (Core Principles, Good Practices)

Usage:
    python analyze_skill_gaps.py path/to/SKILL.md
    python analyze_skill_gaps.py path/to/SKILL.md --json
    python analyze_skill_gaps.py --all --skills-dir path/to/skills/

Version: 1.0.0
Author: RyoMurakami1983
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# --- PHILOSOPHY.md Values ---
VALUES = [
    "温故知新",
    "継続は力",
    "基礎と型",
    "成長の複利",
    "ニュートラル",
    "余白の設計",
]

# Anthropic patterns mapped to Values
# Each pattern has primary (◎) and secondary (○) value alignments
PATTERN_VALUES_MAP = {
    "progressive_disclosure": {"primary": ["基礎と型", "余白の設計"], "secondary": ["ニュートラル"]},
    "orchestrator_skillmd": {"primary": ["基礎と型", "成長の複利"], "secondary": ["余白の設計"]},
    "schema_contract": {"primary": ["基礎と型"], "secondary": ["ニュートラル"]},
    "why_driven_design": {"primary": ["温故知新", "基礎と型"], "secondary": ["成長の複利"]},
    "description_trigger": {"primary": ["基礎と型"], "secondary": ["継続は力"]},
    "environment_fallback": {"primary": ["ニュートラル", "余白の設計"], "secondary": []},
    "sub_agent_separation": {"primary": ["基礎と型", "余白の設計"], "secondary": ["成長の複利"]},
    "deterministic_offload": {"primary": ["基礎と型"], "secondary": ["継続は力"]},
    "human_in_the_loop": {"primary": ["成長の複利"], "secondary": ["ニュートラル"]},
}


@dataclass
class DimensionScore:
    """Score for a single analysis dimension"""
    name: str
    score: float  # 0.0 - 1.0
    max_score: float  # typically 1.0
    details: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GapReport:
    """Complete gap analysis report for a single skill"""
    skill_name: str
    skill_path: str
    dimensions: List[DimensionScore] = field(default_factory=list)
    overall_score: float = 0.0
    values_coverage: Dict[str, float] = field(default_factory=dict)
    priority: str = "low"  # low, medium, high, critical

    def compute_overall(self):
        if not self.dimensions:
            return
        total = sum(d.score for d in self.dimensions)
        max_total = sum(d.max_score for d in self.dimensions)
        self.overall_score = total / max_total if max_total > 0 else 0.0
        if self.overall_score < 0.3:
            self.priority = "critical"
        elif self.overall_score < 0.5:
            self.priority = "high"
        elif self.overall_score < 0.7:
            self.priority = "medium"
        else:
            self.priority = "low"


class GapAnalyzer:
    """Analyzes a SKILL.md against Anthropic patterns"""

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split("\n")
        self.line_count = len(self.lines)
        self.skill_dir = Path(file_path).parent
        self.frontmatter = self._parse_frontmatter()

    def _parse_frontmatter(self) -> Dict:
        """Parse YAML frontmatter into dict (simplified, no external deps)"""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", self.content, re.DOTALL)
        if not match:
            return {}

        lines = match.group(1).split("\n")
        data: Dict = {}
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.startswith(" ") or line.startswith("\t"):
                i += 1
                continue

            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if not m:
                i += 1
                continue

            key = m.group(1)
            val = m.group(2).strip()

            # Handle folded/literal block scalars
            if key == "description" and val in {">", "|", ">-", "|-"}:
                folded: List[str] = []
                i += 1
                while i < len(lines):
                    sub = lines[i]
                    if sub and not sub.startswith(" ") and not sub.startswith("\t"):
                        break
                    if sub.strip():
                        folded.append(sub.strip())
                    i += 1
                data[key] = " ".join(folded).strip()
                continue

            # Handle metadata block
            if key == "metadata":
                meta: Dict = {}
                i += 1
                while i < len(lines):
                    sub = lines[i]
                    if sub and not sub.startswith(" ") and not sub.startswith("\t"):
                        break
                    sm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", sub)
                    if sm:
                        meta[sm.group(1)] = sm.group(2).strip().strip("\"'")
                    i += 1
                data[key] = meta
                continue

            data[key] = val.strip("\"'")
            i += 1

        return data

    def _strip_code_blocks(self) -> str:
        """Remove fenced code blocks from content for text analysis"""
        return re.sub(r"^```.*?^```", "", self.content, flags=re.DOTALL | re.MULTILINE)

    def _has_section(self, pattern: str) -> bool:
        """Check if section heading exists (case-insensitive)"""
        return bool(re.search(pattern, self.content, re.IGNORECASE | re.MULTILINE))

    def _has_dir(self, name: str) -> bool:
        """Check if a subdirectory exists in the skill directory"""
        return (self.skill_dir / name).is_dir()

    def _has_files_in_dir(self, name: str) -> int:
        """Count files in a subdirectory"""
        d = self.skill_dir / name
        if not d.is_dir():
            return 0
        return len([f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")])

    # --- Dimension 1: Progressive Disclosure ---

    def analyze_progressive_disclosure(self) -> DimensionScore:
        """Check Progressive Disclosure: description quality, body size, references usage"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []

        # Level 1: description quality (~100 tokens)
        desc = self.frontmatter.get("description", "")
        desc_words = len(desc.split())
        if 20 <= desc_words <= 150:
            score += 0.15
            details.append(f"✅ description 長さ適切 ({desc_words} words)")
        elif desc_words < 20:
            details.append(f"⚠️ description が短すぎる ({desc_words} words, 推奨: 20-150)")
            recs.append("descriptionを充実させ、[What]+[When]+[Key capabilities]構成にする")
        else:
            details.append(f"⚠️ description が長すぎる ({desc_words} words, 推奨: 20-150)")
            recs.append("descriptionを100トークン程度に簡潔化する")

        # Level 2: SKILL.md body size (<500 lines)
        if self.line_count <= 300:
            score += 0.20
            details.append(f"✅ SKILL.md body 簡潔 ({self.line_count} lines)")
        elif self.line_count <= 500:
            score += 0.15
            details.append(f"✅ SKILL.md body 許容範囲 ({self.line_count} lines)")
        else:
            score += 0.05
            details.append(f"⚠️ SKILL.md body が長い ({self.line_count} lines, 推奨: <500)")
            recs.append("SKILL.md本文を500行以下に。詳細はreferences/に分離する")

        # Level 3: references/ usage
        ref_count = self._has_files_in_dir("references")
        if ref_count >= 2:
            score += 0.20
            details.append(f"✅ references/ 活用あり ({ref_count} files)")
        elif ref_count == 1:
            score += 0.10
            details.append(f"○ references/ 最低限 ({ref_count} file — SKILL.ja.md のみ?)")
            recs.append("深い知識やドメイン情報をreferences/に分離することを検討")
        else:
            details.append("❌ references/ ディレクトリなし")
            recs.append("references/ディレクトリを作成し、詳細情報やスキーマ定義を分離")

        # scripts/ usage (bonus)
        script_count = self._has_files_in_dir("scripts")
        if script_count > 0:
            score += 0.10
            details.append(f"✅ scripts/ あり ({script_count} files) — 確定的処理のオフロード")

        # agents/ usage (bonus)
        agent_count = self._has_files_in_dir("agents")
        if agent_count > 0:
            score += 0.10
            details.append(f"✅ agents/ あり ({agent_count} files) — サブエージェント分離")

        # Explicit references from SKILL.md to external files
        ref_pattern = re.findall(r"references/\S+|scripts/\S+|agents/\S+", self.content)
        if len(ref_pattern) >= 2:
            score += 0.10
            details.append(f"✅ SKILL.md内に外部ファイル参照あり ({len(ref_pattern)} refs)")
        elif len(ref_pattern) == 0 and (ref_count > 1 or script_count > 0):
            recs.append("SKILL.mdから外部ファイルへの明示的参照ポインタを追加する")

        return DimensionScore(
            name="Progressive Disclosure",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Dimension 2: Orchestration Maturity ---

    def analyze_orchestration(self) -> DimensionScore:
        """Check orchestration patterns: delegation, sub-agents, schema contracts"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []
        clean = self._strip_code_blocks()

        # Skill delegation (references to other skills)
        delegation_patterns = re.findall(
            r"(?:skills/|skill\s+)[\w-]+|invok\w+\s+[\w-]+|delegat\w+|委譲|ルーティング",
            clean,
            re.IGNORECASE,
        )
        if len(delegation_patterns) >= 2:
            score += 0.25
            details.append(f"✅ 他スキルへの委譲パターンあり ({len(delegation_patterns)} refs)")
        elif len(delegation_patterns) >= 1:
            score += 0.10
            details.append(f"○ 委譲パターン最低限 ({len(delegation_patterns)} ref)")
        else:
            details.append("❌ 他スキルへの委譲パターンなし")
            recs.append("関連するワークフローを独立スキルに委譲するパターンを検討")

        # Related Skills section
        if self._has_section(r"^##\s+Related Skills"):
            score += 0.15
            details.append("✅ Related Skills セクションあり")
        else:
            recs.append("Related Skillsセクションを追加し、スキル間の関係を明示")

        # Sub-agent separation (agents/ directory or task tool references)
        has_agents = self._has_dir("agents")
        task_refs = len(re.findall(r"task\s+tool|sub\s*agent|サブエージェント|agent_type", clean, re.IGNORECASE))
        if has_agents:
            score += 0.25
            details.append("✅ agents/ ディレクトリでサブエージェント分離済み")
        elif task_refs >= 1:
            score += 0.15
            details.append(f"○ サブエージェント参照あり ({task_refs} refs) — agents/分離は未実施")
            recs.append("頻繁に使うサブエージェントプロンプトはagents/に分離を検討")
        else:
            details.append("○ サブエージェント分離なし（スキルの性質上不要な場合もある）")

        # Schema contract
        has_schemas = self._has_section(r"schema|スキーマ|JSON\s+format|data\s+contract|契約")
        schema_refs = self._has_files_in_dir("references") and any(
            "schema" in f.name.lower()
            for f in (self.skill_dir / "references").iterdir()
            if f.is_file()
        ) if self._has_dir("references") else False
        if schema_refs:
            score += 0.20
            details.append("✅ references/にスキーマ定義ファイルあり")
        elif has_schemas:
            score += 0.10
            details.append("○ SKILL.md内にスキーマ/フォーマット定義あり（分離推奨）")
        else:
            script_count = self._has_files_in_dir("scripts")
            if script_count > 0:
                recs.append("scripts/がある場合、入出力フォーマットのスキーマ契約をreferences/に定義")

        # Workflow step structure
        step_count = len(re.findall(r"^###?\s+Step\s+\d+", clean, re.MULTILINE | re.IGNORECASE))
        if step_count >= 3:
            score += 0.15
            details.append(f"✅ 明確なワークフローステップ ({step_count} steps)")
        elif step_count >= 1:
            score += 0.08
            details.append(f"○ ワークフローステップ少なめ ({step_count} steps)")

        return DimensionScore(
            name="Orchestration Maturity",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Dimension 3: Why-driven Degree ---

    def analyze_why_driven(self) -> DimensionScore:
        """Check ratio of MUST/ALWAYS/NEVER vs reasoning-based instructions"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []
        clean = self._strip_code_blocks()

        # Count imperative/rigid patterns
        must_patterns = len(re.findall(r"\bMUST\b|\bALWAYS\b|\bNEVER\b|\b必ず\b|\b絶対\b|\b禁止\b", clean))

        # Count why/reasoning patterns
        why_patterns = len(re.findall(
            r"\bなぜ\w*\b|\bWhy\b|\bbecause\b|\breason\b|\bを防ぐ\b|\bを避ける\b"
            r"|\bにより\b|\bするため\b|\bこれにより\b|\breasoning\b|\bprevents?\b|\bensures?\b",
            clean,
            re.IGNORECASE,
        ))

        # Values references (WHY alignment)
        values_refs = 0
        for v in VALUES:
            values_refs += len(re.findall(re.escape(v), clean))

        total_directives = must_patterns + why_patterns
        if total_directives > 0:
            why_ratio = why_patterns / total_directives
        else:
            why_ratio = 0.5  # neutral if no directives

        if must_patterns == 0 and why_patterns == 0:
            score += 0.3
            details.append("○ 指示的パターンが少ない（Why-drivenの判定困難）")
        elif why_ratio >= 0.6:
            score += 0.4
            details.append(f"✅ Why-driven優位 (Why: {why_patterns}, Must: {must_patterns}, ratio: {why_ratio:.0%})")
        elif why_ratio >= 0.3:
            score += 0.25
            details.append(f"○ Why/Must 混在 (Why: {why_patterns}, Must: {must_patterns}, ratio: {why_ratio:.0%})")
            recs.append("MUST/ALWAYSの一部を「なぜそうすべきか」の理由説明に置き換える")
        else:
            score += 0.10
            details.append(f"⚠️ Must-driven 偏重 (Why: {why_patterns}, Must: {must_patterns}, ratio: {why_ratio:.0%})")
            recs.append("「崖の近く」以外のMUST/ALWAYSをWhy-driven形式に書き換える")

        # Values integration (Why at a philosophical level)
        if values_refs >= 6:
            score += 0.35
            details.append(f"✅ PHILOSOPHY.md Values 参照が豊富 ({values_refs} refs)")
        elif values_refs >= 3:
            score += 0.20
            details.append(f"○ Values 参照あり ({values_refs} refs)")
        elif values_refs >= 1:
            score += 0.10
            details.append(f"○ Values 参照少なめ ({values_refs} ref)")
            recs.append("Core PrinciplesやGood PracticesでのValues引用を増やす")
        else:
            details.append("❌ PHILOSOPHY.md Values への参照なし")
            recs.append("Core Principlesセクションで最低2つのValuesを引用する")

        # Core Principles section
        if self._has_section(r"^##\s+Core Principles"):
            score += 0.15
            details.append("✅ Core Principles セクションあり")
        else:
            recs.append("Core Principlesセクションを追加し、Valuesとの対応を明示")

        # Good/Best Practices section
        if self._has_section(r"^##\s+(Good|Best)\s+Practices"):
            score += 0.10
            details.append("✅ Good/Best Practices セクションあり")

        return DimensionScore(
            name="Why-driven Design",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Dimension 4: Description Trigger Quality ---

    def analyze_description_trigger(self) -> DimensionScore:
        """Check description against [What] + [When] + [Key capabilities] pattern"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []

        desc = self.frontmatter.get("description", "")
        if not desc:
            details.append("❌ description がない")
            recs.append("descriptionフィールドを追加する")
            return DimensionScore("Description Trigger", 0.0, 1.0, details, recs)

        desc_lower = desc.lower()

        # [What] — does it explain what the skill does?
        # Heuristic: first sentence should be action-oriented
        has_what = bool(re.search(
            r"\b(create|build|run|deploy|validate|review|manage|generate|write|analyze|check|setup|configure|"
            r"capture|guide|作成|実行|検証|レビュー|管理|生成|分析)\b",
            desc_lower,
        ))
        if has_what:
            score += 0.25
            details.append("✅ [What] — スキルの目的が明確")
        else:
            details.append("⚠️ [What] — スキルの目的が不明確")
            recs.append("descriptionの冒頭で「何をするスキルか」を動詞で明確にする")

        # [When] — does it include trigger context?
        has_when = bool(re.search(
            r"\buse when\b|\bwhenever\b|\bif\b.*\bwant|when.*(?:need|start|want|mention|ask)"
            r"|\bトリガー\b|\b使う\b.*?とき|\b場合\b",
            desc_lower,
        ))
        if has_when:
            score += 0.30
            details.append("✅ [When] — トリガー文脈が記述されている")
        else:
            details.append("⚠️ [When] — トリガー文脈がない")
            recs.append("'Use when...'パターンで具体的なトリガー文脈を列挙する")

        # [Key capabilities] — does it list specific capabilities?
        # Count comma-separated items or 'or' clauses as capability listing
        capabilities = re.findall(r",\s*(?:or\s+)?(?:\w+\s+){1,3}\w+", desc)
        enumeration = len(capabilities)
        if enumeration >= 3:
            score += 0.25
            details.append(f"✅ [Key capabilities] — 具体的な機能列挙あり ({enumeration}+ items)")
        elif enumeration >= 1:
            score += 0.15
            details.append(f"○ [Key capabilities] — 機能列挙少なめ ({enumeration} items)")
            recs.append("具体的なユースケースやキーワードをdescriptionに追加する（「押し強め」）")
        else:
            details.append("⚠️ [Key capabilities] — 具体的な機能列挙なし")
            recs.append("トリガーすべき文脈を具体的に列挙する（dashboards, visualization, metrics等）")

        # Length check
        desc_len = len(desc)
        if 80 <= desc_len <= 500:
            score += 0.10
            details.append(f"✅ description 長さ適切 ({desc_len} chars)")
        elif desc_len < 80:
            score += 0.05
            details.append(f"⚠️ description が短い ({desc_len} chars)")
            recs.append("80-500文字の範囲でdescriptionを充実させる")
        else:
            score += 0.05
            details.append(f"⚠️ description が長すぎる ({desc_len} chars)")

        # Pushy check — does it include explicit trigger nudges?
        has_pushy = bool(re.search(
            r"make sure|ensure|always use|whenever|even if|especially when",
            desc_lower,
        ))
        if has_pushy:
            score += 0.10
            details.append("✅ 「押し強め」パターンあり（アンダートリガー対策）")

        return DimensionScore(
            name="Description Trigger",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Dimension 5: Environment Portability ---

    def analyze_portability(self) -> DimensionScore:
        """Check environment-specific fallback instructions"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []
        clean = self._strip_code_blocks()

        # Environment-specific sections
        env_keywords = re.findall(
            r"Claude\.ai|Claude\s+Code|Cowork|Copilot|GitHub\s+Copilot|Gemini|VS\s+Code|"
            r"PowerShell|Bash|Windows|Linux|macOS|環境|フォールバック|fallback",
            clean,
            re.IGNORECASE,
        )
        unique_envs = set(k.lower() for k in env_keywords)

        if len(unique_envs) >= 3:
            score += 0.40
            details.append(f"✅ 複数環境への言及あり ({len(unique_envs)} unique)")
        elif len(unique_envs) >= 1:
            score += 0.20
            details.append(f"○ 環境言及あり ({len(unique_envs)} unique)")
        else:
            details.append("○ 環境固有の記述なし（スキルの性質上不要な場合もある）")
            score += 0.20  # neutral — not all skills need this

        # Fallback patterns
        has_fallback = bool(re.search(
            r"fallback|代替|alternative|不可.*→|できない場合|if.*(?:not available|unavailable)",
            clean,
            re.IGNORECASE,
        ))
        if has_fallback:
            score += 0.30
            details.append("✅ フォールバック/代替手段の記述あり")
        else:
            score += 0.10
            details.append("○ 明示的なフォールバック記述なし")
            recs.append("ツールやサブエージェントが使えない場合の代替手段を記述する")

        # Cross-platform script support
        scripts_dir = self.skill_dir / "scripts"
        if scripts_dir.is_dir():
            exts = {f.suffix for f in scripts_dir.iterdir() if f.is_file()}
            if len(exts) >= 2:
                score += 0.20
                details.append(f"✅ 複数言語のスクリプトあり ({', '.join(exts)})")
            elif len(exts) == 1:
                score += 0.10
                details.append(f"○ スクリプト言語は1種のみ ({', '.join(exts)})")
        else:
            score += 0.10  # neutral — docs-only skills are fine

        # Compatibility field in frontmatter
        if "compatibility" in self.frontmatter or "allowed-tools" in self.frontmatter:
            score += 0.10
            details.append("✅ frontmatter に compatibility/allowed-tools あり")

        return DimensionScore(
            name="Environment Portability",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Dimension 6: PHILOSOPHY.md Values Alignment ---

    def analyze_values_alignment(self) -> DimensionScore:
        """Check alignment with PHILOSOPHY.md Values"""
        score = 0.0
        details: List[str] = []
        recs: List[str] = []
        clean = self._strip_code_blocks()

        # Count references to each Value
        value_counts: Dict[str, int] = {}
        for v in VALUES:
            count = len(re.findall(re.escape(v), clean))
            value_counts[v] = count

        total_refs = sum(value_counts.values())
        covered = sum(1 for c in value_counts.values() if c > 0)

        # Coverage breadth
        if covered >= 4:
            score += 0.30
            details.append(f"✅ Values カバレッジ高 ({covered}/6 Values referenced)")
        elif covered >= 2:
            score += 0.20
            details.append(f"○ Values カバレッジ中 ({covered}/6 Values referenced)")
        elif covered >= 1:
            score += 0.10
            details.append(f"○ Values カバレッジ低 ({covered}/6)")
            recs.append("Core Principlesで複数のValuesを参照する")
        else:
            details.append("❌ Values 参照なし")
            recs.append("Core Principlesセクションで最低2つのPHILOSOPHY.md Valuesを引用")

        # Reference depth
        if total_refs >= 8:
            score += 0.20
            details.append(f"✅ Values 参照が深い ({total_refs} total refs)")
        elif total_refs >= 3:
            score += 0.10
            details.append(f"○ Values 参照あり ({total_refs} total refs)")

        # Core Principles section with Values citations
        cp_section = self._has_section(r"^##\s+Core Principles")
        if cp_section:
            score += 0.15
            details.append("✅ Core Principles セクションあり")
        else:
            recs.append("Core Principlesセクションを追加")

        # Anti-Patterns section
        if self._has_section(r"^##\s+Anti.?Patterns"):
            score += 0.10
            details.append("✅ Anti-Patterns セクションあり")

        # Common Pitfalls section
        if self._has_section(r"^##\s+Common Pitfalls"):
            score += 0.10
            details.append("✅ Common Pitfalls セクションあり")

        # Quick Reference section
        if self._has_section(r"^##\s+Quick Reference"):
            score += 0.10
            details.append("✅ Quick Reference セクションあり")

        # Value breakdown
        breakdown_parts = [f"{v}: {c}" for v, c in value_counts.items() if c > 0]
        if breakdown_parts:
            details.append(f"📊 Values内訳: {', '.join(breakdown_parts)}")

        # Missing values
        missing = [v for v, c in value_counts.items() if c == 0]
        if missing and covered < 4:
            recs.append(f"未参照Values: {', '.join(missing)}")

        return DimensionScore(
            name="Values Alignment",
            score=min(score, 1.0),
            max_score=1.0,
            details=details,
            recommendations=recs,
        )

    # --- Compute Values Coverage ---

    def compute_values_coverage(self) -> Dict[str, float]:
        """Map gaps to PHILOSOPHY.md Values to show which values need more attention"""
        clean = self._strip_code_blocks()
        coverage: Dict[str, float] = {}

        for v in VALUES:
            count = len(re.findall(re.escape(v), clean))
            # Normalize: 0 refs = 0.0, 3+ refs = 1.0
            coverage[v] = min(count / 3.0, 1.0)

        return coverage

    # --- Run Full Analysis ---

    def analyze(self) -> GapReport:
        """Run all dimensions and produce a complete gap report"""
        skill_name = self.frontmatter.get("name", Path(self.file_path).parent.name)

        report = GapReport(skill_name=skill_name, skill_path=self.file_path)

        report.dimensions = [
            self.analyze_progressive_disclosure(),
            self.analyze_orchestration(),
            self.analyze_why_driven(),
            self.analyze_description_trigger(),
            self.analyze_portability(),
            self.analyze_values_alignment(),
        ]

        report.values_coverage = self.compute_values_coverage()
        report.compute_overall()

        return report


# --- Output Formatters ---

def format_text_report(report: GapReport) -> str:
    """Format report as human-readable text"""
    lines = [
        f"{'=' * 70}",
        f"Gap Analysis: {report.skill_name}",
        f"Path: {report.skill_path}",
        f"Overall Score: {report.overall_score:.0%} | Priority: {report.priority.upper()}",
        f"{'=' * 70}",
        "",
    ]

    for dim in report.dimensions:
        pct = dim.score / dim.max_score * 100 if dim.max_score > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        lines.append(f"[{dim.name}] {bar} {pct:.0f}%")
        for d in dim.details:
            lines.append(f"  {d}")
        if dim.recommendations:
            lines.append("  💡 推奨:")
            for r in dim.recommendations:
                lines.append(f"    → {r}")
        lines.append("")

    # Values Coverage
    lines.append("📊 PHILOSOPHY.md Values Coverage:")
    for v, c in report.values_coverage.items():
        bar = "█" * int(c * 10) + "░" * (10 - int(c * 10))
        lines.append(f"  {v}: {bar} {c:.0%}")

    lines.append("")
    return "\n".join(lines)


def format_json_report(report: GapReport) -> str:
    """Format report as JSON"""
    data = {
        "skill_name": report.skill_name,
        "skill_path": report.skill_path,
        "overall_score": round(report.overall_score, 3),
        "priority": report.priority,
        "dimensions": [
            {
                "name": d.name,
                "score": round(d.score, 3),
                "max_score": d.max_score,
                "percentage": round(d.score / d.max_score * 100, 1) if d.max_score > 0 else 0,
                "details": d.details,
                "recommendations": d.recommendations,
            }
            for d in report.dimensions
        ],
        "values_coverage": {k: round(v, 3) for k, v in report.values_coverage.items()},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_matrix_row(report: GapReport) -> Dict:
    """Generate a row for the aggregated matrix"""
    row = {
        "skill": report.skill_name,
        "overall": round(report.overall_score * 100, 1),
        "priority": report.priority,
    }
    for dim in report.dimensions:
        key = dim.name.lower().replace(" ", "_")
        row[key] = round(dim.score / dim.max_score * 100, 1) if dim.max_score > 0 else 0
    for v, c in report.values_coverage.items():
        row[f"value_{v}"] = round(c * 100, 1)
    return row


# --- Main ---

def analyze_single(skill_path: str, output_json: bool = False) -> GapReport:
    """Analyze a single SKILL.md file"""
    path = Path(skill_path)
    if not path.exists():
        print(f"Error: {skill_path} not found", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    analyzer = GapAnalyzer(content, str(path))
    report = analyzer.analyze()

    if output_json:
        print(format_json_report(report))
    else:
        print(format_text_report(report))

    return report


def analyze_all(skills_dir: str, output_json: bool = False) -> List[GapReport]:
    """Analyze all skills in a directory"""
    base = Path(skills_dir)
    reports: List[GapReport] = []

    skill_dirs = sorted(
        d for d in base.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists() and not d.name.startswith(".")
    )

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        analyzer = GapAnalyzer(content, str(skill_md))
        report = analyzer.analyze()
        reports.append(report)

    if output_json:
        # Output aggregated matrix
        matrix = [format_matrix_row(r) for r in reports]
        print(json.dumps(matrix, ensure_ascii=False, indent=2))
    else:
        # Print summary table
        print(f"{'=' * 90}")
        print(f"{'Skill':<40} {'Score':>6} {'Priority':>10} {'PD':>5} {'Orch':>5} {'Why':>5} {'Desc':>5} {'Port':>5} {'Val':>5}")
        print(f"{'-' * 90}")
        for r in sorted(reports, key=lambda x: x.overall_score):
            dims = {d.name: d.score / d.max_score * 100 for d in r.dimensions}
            print(
                f"{r.skill_name:<40} {r.overall_score * 100:>5.0f}% {r.priority:>10}"
                f" {dims.get('Progressive Disclosure', 0):>4.0f}%"
                f" {dims.get('Orchestration Maturity', 0):>4.0f}%"
                f" {dims.get('Why-driven Design', 0):>4.0f}%"
                f" {dims.get('Description Trigger', 0):>4.0f}%"
                f" {dims.get('Environment Portability', 0):>4.0f}%"
                f" {dims.get('Values Alignment', 0):>4.0f}%"
            )
        print(f"{'=' * 90}")
        print(f"Total skills: {len(reports)}")
        priorities = {}
        for r in reports:
            priorities[r.priority] = priorities.get(r.priority, 0) + 1
        for p in ["critical", "high", "medium", "low"]:
            if p in priorities:
                print(f"  {p.upper()}: {priorities[p]}")

    return reports


def main():
    parser = argparse.ArgumentParser(
        description="Analyze skills against Anthropic patterns and PHILOSOPHY.md Values"
    )
    parser.add_argument("path", nargs="?", help="Path to SKILL.md file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--all", action="store_true", help="Analyze all skills in directory")
    parser.add_argument("--skills-dir", default=None, help="Skills directory (for --all)")

    args = parser.parse_args()

    if args.all:
        skills_dir = args.skills_dir or args.path
        if not skills_dir:
            # Auto-detect from script location (.resolve() ensures this works
            # regardless of whether the script is invoked with a relative or
            # absolute path — scripts/ is 2 levels above the skills/ root)
            script_dir = Path(__file__).resolve().parent
            skills_dir = str(script_dir.parent.parent)
        analyze_all(skills_dir, args.json)
    elif args.path:
        analyze_single(args.path, args.json)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
