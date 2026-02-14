#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL.md Quality Validator

Validates GitHub Copilot agent skills against quality checklist.
Supports both legacy multi-pattern skills and new single-workflow skills.
Includes checks for file length, bilingual support, router skill detection,
and development philosophy (PHILOSOPHY.md Values) integration.

Usage:
    python validate_skill.py path/to/SKILL.md
    python validate_skill.py path/to/SKILL.md --json
    python validate_skill.py path/to/SKILL.md --output report.txt
    
Version: 4.0.0
Author: RyoMurakami1983
Last Updated: 2026-02-13
"""

import argparse
import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional

# Ensure UTF-8 encoding for stdout
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class CheckResult:
    """Individual check result"""
    id: str
    description: str
    passed: bool
    details: str = ""


@dataclass
class CategoryResult:
    """Category validation result"""
    name: str
    checks: List[CheckResult]
    score: int
    max_score: int
    percentage: float
    passed: bool
    threshold: float = 80.0

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"[{self.name}] {self.score}/{self.max_score} ({self.percentage:.0f}%) {status}"


@dataclass
class ValidationReport:
    """Complete validation report"""
    file_path: str
    categories: List[CategoryResult]
    total_score: int
    total_max_score: int
    overall_percentage: float
    overall_passed: bool
    overall_threshold: float = 85.0


class SkillValidator:
    """Base validator with common utilities"""

    def __init__(self, content: str, file_path: str, is_router: bool = False, is_workflow: bool = False):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.is_router = is_router
        self.is_workflow = is_workflow

    def has_section(self, pattern: str) -> bool:
        """Check if section exists (case-insensitive)"""
        return bool(re.search(pattern, self.content, re.IGNORECASE | re.MULTILINE))

    def count_sections(self, pattern: str) -> int:
        """Count number of matching sections, excluding code blocks"""
        # Remove code blocks first to avoid counting headings inside them
        # Use line-start anchor to avoid matching inline code
        content_without_code = re.sub(r'^```.*?^```', '', self.content, flags=re.DOTALL | re.MULTILINE)
        return len(re.findall(pattern, content_without_code, re.MULTILINE))

    def extract_frontmatter(self) -> Optional[str]:
        """Extract YAML frontmatter"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.DOTALL)
        return match.group(1) if match else None

    def get_section_content(self, heading: str) -> Optional[str]:
        """Extract a section body while ignoring headings inside fenced code blocks."""
        lines = self.content.split('\n')
        heading_prefix = heading.strip().lower()
        section_boundary_pattern = re.compile(
            r'^(when to use|core principles|the philosophy|workflow:|related skills|dependencies|'
            r'best practices|good practices|common pitfalls|anti-patterns|quick reference|decision tree|'
            r'resources|validation scripts|migration notice|changelog|pattern\s+\d+:)',
            re.IGNORECASE,
        )
        start_line: Optional[int] = None
        end_line: Optional[int] = None

        in_fence = False
        fence_char = ''
        fence_len = 0

        for idx, line in enumerate(lines):
            # CommonMark: fenced code blocks are recognized with up to 3 leading spaces.
            fence_match = re.match(r'^ {0,3}([`~]{3,})', line)
            if fence_match:
                marker = fence_match.group(1)
                if not in_fence:
                    in_fence = True
                    fence_char = marker[0]
                    fence_len = len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_len:
                    in_fence = False
                continue

            if in_fence:
                # Guardrail for malformed markdown: if a known top-level section appears while
                # a fence remains unclosed, stop the current section at that boundary.
                h2_in_fence = re.match(r'^##\s+(.+?)\s*$', line)
                if start_line is not None and h2_in_fence:
                    h2_title = h2_in_fence.group(1).strip()
                    if section_boundary_pattern.match(h2_title):
                        end_line = idx
                        break
                continue

            h2_match = re.match(r'^##\s+(.+?)\s*$', line)
            if not h2_match:
                continue

            h2_title = h2_match.group(1).strip().lower()
            if start_line is None:
                if h2_title.startswith(heading_prefix):
                    start_line = idx + 1
            else:
                end_line = idx
                break

        if start_line is None:
            return None

        section_lines = lines[start_line:end_line] if end_line is not None else lines[start_line:]
        return '\n'.join(section_lines).strip()


class StructureValidator(SkillValidator):
    """Validates structure requirements (14 items)"""

    def validate(self) -> List[CheckResult]:
        checks = []

        # 1.1 Single SKILL.md file
        checks.append(CheckResult(
            "1.1",
            "Single SKILL.md file",
            self.file_path.endswith('SKILL.md'),
            f"File: {Path(self.file_path).name}"
        ))

        # 1.2 YAML frontmatter present with required fields
        frontmatter = self.extract_frontmatter()
        has_required_fields = False
        if frontmatter:
            has_required_fields = all(field in frontmatter.lower() for field in ['name:', 'description:', 'invocable:'])
        checks.append(CheckResult(
            "1.2",
            "YAML frontmatter with name/description/invocable",
            has_required_fields,
            "Found" if has_required_fields else "Missing or incomplete"
        ))

        # 1.2b Author field present in YAML frontmatter
        has_author = False
        if frontmatter:
            has_author = 'author:' in frontmatter.lower()
        checks.append(CheckResult(
            "1.2b",
            "YAML frontmatter includes author field",
            has_author,
            "Found" if has_author else "Missing author field"
        ))

        # 1.3 frontmatter name matches folder (kebab-case)
        name_match = re.search(r'name:\s*["\']?([^"\'\n]+)["\']?', frontmatter or '', re.IGNORECASE)
        folder_name = Path(self.file_path).parent.name
        names_match = False
        if name_match:
            skill_name = name_match.group(1).strip().lower().replace(' ', '-')
            folder_lower = folder_name.lower()
            names_match = skill_name == folder_lower or skill_name in folder_lower
        checks.append(CheckResult(
            "1.3",
            "Name matches folder (kebab-case)",
            names_match,
            f"Folder: {folder_name}"
        ))

        # 1.4 description <= 100 chars
        desc_match = re.search(r'description:\s*["\']?([^"\'\n]+)["\']?', frontmatter or '', re.IGNORECASE)
        desc_length_ok = False
        if desc_match:
            desc = desc_match.group(1).strip()
            desc_length_ok = len(desc) <= 100
        checks.append(CheckResult(
            "1.4",
            "Description ≤100 chars, problem-focused",
            desc_length_ok,
            f"{len(desc_match.group(1).strip()) if desc_match else 0} chars"
        ))

        # 1.5 "When to Use This Skill" is first H2
        first_h2 = re.search(r'^##\s+(.+)$', self.content, re.MULTILINE)
        when_to_use_first = False
        if first_h2:
            when_to_use_first = 'when to use' in first_h2.group(1).lower()
        checks.append(CheckResult(
            "1.5",
            '"When to Use This Skill" is first H2',
            when_to_use_first,
            first_h2.group(1) if first_h2 else "No H2 found"
        ))

        # 1.6 "Core Principles" or "The Philosophy" exists
        has_principles = (
            self.has_section(r'^##\s+.*Core Principles') or
            self.has_section(r'^##\s+.*The Philosophy')
        )
        checks.append(CheckResult(
            "1.6",
            '"Core Principles" or "The Philosophy" section exists',
            has_principles
        ))

        # 1.7 Workflow or Pattern structure
        # New standard: single "## Workflow:" section
        # Legacy: 7-10 "## Pattern N:" sections
        # Router skills: single routing workflow (detected separately)
        content_without_code = re.sub(r'^```.*?^```', '', self.content, flags=re.DOTALL | re.MULTILINE)
        pattern_count = len(re.findall(r'^##\s+Pattern\s+\d+:', content_without_code, re.MULTILINE))
        has_workflow = bool(re.search(r'^##\s+Workflow:', content_without_code, re.MULTILINE))
        is_router = 'router' in (frontmatter or '').lower() or 'router skill' in self.content[:500].lower()
        
        if has_workflow or is_router:
            structure_ok = True
            detail = "Workflow section found" if has_workflow else "Router skill detected"
        elif 7 <= pattern_count <= 10:
            structure_ok = True
            detail = f"Legacy: {pattern_count} patterns (migration recommended)"
        else:
            structure_ok = False
            detail = f"Found {pattern_count} patterns, no Workflow section"
        
        checks.append(CheckResult(
            "1.7",
            "Workflow section OR 7-10 pattern sections",
            structure_ok,
            detail
        ))
        
        # 1.11 Router skill consistency (if applicable)
        if is_router:
            has_related_table = bool(re.search(r'Related Skills.*?\|', self.content, re.DOTALL | re.IGNORECASE))
            checks.append(CheckResult(
                "1.11",
                "Router skill has Related Skills routing table",
                has_related_table,
                "Router with routing table" if has_related_table else "Router missing routing table"
            ))
        else:
            checks.append(CheckResult(
                "1.11",
                "Router skill has Related Skills routing table",
                True,
                "N/A (not a router skill)"
            ))
        
        # 1.12 Bilingual support (references/SKILL.ja.md exists)
        skill_dir = Path(self.file_path).parent
        ja_path = skill_dir / "references" / "SKILL.ja.md"
        ja_root_path = skill_dir / "SKILL.ja.md"
        has_japanese = ja_path.exists() or ja_root_path.exists()
        checks.append(CheckResult(
            "1.12",
            "Japanese version exists (references/SKILL.ja.md)",
            has_japanese,
            f"Found: {ja_path.name}" if ja_path.exists() else
            f"Found: {ja_root_path.name}" if ja_root_path.exists() else "Missing"
        ))
        
        # 1.13 Line count policy (≤500 recommended, ≤550 max)
        line_count = len(self.lines)
        line_ok = line_count <= 550
        checks.append(CheckResult(
            "1.13",
            "Line count ≤550 (target ≤500)",
            line_ok,
            f"{line_count} lines" + (" ⚠️ over 500" if 500 < line_count <= 550 else "")
        ))

        # 1.8 "Common Pitfalls" exists (N/A for router skills)
        if self.is_router:
            checks.append(CheckResult("1.8", '"Common Pitfalls" section exists', True, "N/A (router skill)"))
        else:
            has_pitfalls = self.has_section(r'^##\s+.*Common Pitfalls')
            checks.append(CheckResult("1.8", '"Common Pitfalls" section exists', has_pitfalls))

        # 1.9 "Anti-Patterns" exists (N/A for router skills)
        if self.is_router:
            checks.append(CheckResult("1.9", '"Anti-Patterns" section exists', True, "N/A (router skill)"))
        else:
            has_antipatterns = self.has_section(r'^##\s+.*Anti-Patterns')
            checks.append(CheckResult("1.9", '"Anti-Patterns" section exists', has_antipatterns))

        # 1.10 "Quick Reference" or "Decision Tree" exists (N/A for router skills)
        if self.is_router:
            checks.append(CheckResult("1.10", '"Quick Reference" or "Decision Tree" exists', True, "N/A (router skill)"))
        else:
            has_reference = (
                self.has_section(r'^##\s+.*Quick Reference') or
                self.has_section(r'^##\s+.*Decision Tree')
            )
            checks.append(CheckResult(
                "1.10",
                '"Quick Reference" or "Decision Tree" exists',
                has_reference
            ))

        return checks


class ContentValidator(SkillValidator):
    """Validates content requirements (20 items)"""

    def validate(self) -> List[CheckResult]:
        checks = []

        # 2.1 "When to Use" section (4 items)
        when_to_use = self.get_section_content("When to Use")
        
        # 2.1.1 5-8 specific scenarios listed (3+ for router skills)
        scenario_count = 0
        if when_to_use:
            scenarios = re.findall(r'^[-*]\s+(.+)$', when_to_use, re.MULTILINE)
            scenario_count = len(scenarios)
        min_scenarios = 3 if self.is_router else 5
        max_scenarios = 10 if self.is_router else 8
        checks.append(CheckResult(
            "2.1.1",
            f"{'3+' if self.is_router else '5-8'} specific scenarios in When to Use",
            min_scenarios <= scenario_count <= max_scenarios,
            f"Found {scenario_count} scenarios"
        ))

        # 2.1.2 Each scenario starts with verb (relaxed for router skills)
        verb_pattern = r'^[-*]\s+([A-Z][a-z]+ing)\s'
        verb_scenarios = 0
        if when_to_use:
            verb_scenarios = len(re.findall(verb_pattern, when_to_use, re.MULTILINE))
        if self.is_router:
            checks.append(CheckResult(
                "2.1.2", "Scenarios start with verbs", True, "N/A (router skill)"
            ))
        else:
            checks.append(CheckResult(
                "2.1.2",
                "Scenarios start with verbs (Designing, Implementing, etc.)",
                verb_scenarios >= scenario_count * 0.8 if scenario_count > 0 else False,
                f"{verb_scenarios}/{scenario_count} start with verbs"
            ))

        # 2.1.3 Each scenario 50-100 chars (relaxed for router skills)
        scenario_length_ok = True
        if when_to_use and not self.is_router:
            scenarios = re.findall(r'^[-*]\s+(.+)$', when_to_use, re.MULTILINE)
            for scenario in scenarios:
                if not (50 <= len(scenario) <= 100):
                    scenario_length_ok = False
                    break
        checks.append(CheckResult(
            "2.1.3",
            "Scenarios are 50-100 chars",
            scenario_length_ok
        ))

        # 2.1.4 No abstract terms
        abstract_terms = ['good code', 'quality software', 'best practices', 
                         'clean code', 'proper implementation']
        has_abstract = False
        if when_to_use:
            has_abstract = any(term in when_to_use.lower() for term in abstract_terms)
        checks.append(CheckResult(
            "2.1.4",
            'No abstract terms ("good code", "quality software")',
            not has_abstract
        ))

        # 2.2 Core Principles section (3 items)
        principles = self.get_section_content("Core Principles") or \
                    self.get_section_content("The Philosophy") or ""

        # 2.2.1 3-5 principles listed
        # Match numbered list format: "1. **Name** - description"
        principle_count = len(re.findall(r'^\d+\.\s+\*\*[^*]+\*\*', principles, re.MULTILINE))
        checks.append(CheckResult(
            "2.2.1",
            "3-5 principles listed",
            3 <= principle_count <= 5,
            f"Found {principle_count} principles"
        ))

        # 2.2.2 Bold name + description format
        principle_format_ok = principle_count > 0
        checks.append(CheckResult(
            "2.2.2",
            "Bold name + description (30-50 chars) format",
            principle_format_ok
        ))

        # 2.2.3 Principles independently understandable
        # Heuristic: each principle should be on separate lines
        principles_independent = principle_count >= 3
        checks.append(CheckResult(
            "2.2.3",
            "Principles independently understandable",
            principles_independent
        ))

        # 2.3 Pattern/Workflow sections (6 items)
        # Router skills get N/A for detailed content checks
        if self.is_router:
            for check_id, desc in [
                ("2.3.1", "Workflow/Pattern structure"), ("2.3.2", "3-tier examples"),
                ("2.3.3", "When to Use guidance"), ("2.3.4", "No duplicate patterns"),
                ("2.3.5", "Patterns in logical order"), ("2.3.6", "Comparison table"),
            ]:
                checks.append(CheckResult(check_id, desc, True, "N/A (router skill)"))
        else:
            # Support both legacy "Pattern N:" and new "Workflow:" structure
            has_workflow = bool(re.search(r'^##\s+Workflow:', self.content, re.MULTILINE))
            
            # 2.3.1 Patterns have "Overview" OR Workflow has "Step N" subsections
            if has_workflow:
                step_count = len(re.findall(r'^###\s+Step\s+\d+', self.content, re.MULTILINE))
                checks.append(CheckResult(
                    "2.3.1",
                    'Workflow has Step subsections (or Patterns have Overview)',
                    step_count >= 3,
                    f"Found {step_count} steps"
                ))
            else:
                overview_count = self.count_sections(r'^###\s+.*Overview')
                checks.append(CheckResult(
                    "2.3.1",
                    'Patterns have "Overview" subsection',
                    overview_count >= 5,
                    f"Found {overview_count} overviews"
                ))

            # 2.3.2 Minimum 3-tier examples (Basic/Intermediate/Advanced) OR step-based examples
            if self.is_workflow:
                # New-style: Steps use inline examples instead of 3-tier structure
                step_count = len(re.findall(r'^###\s+Step\s+\d+', self.content, re.MULTILINE))
                code_block_count = len(re.findall(r'```', self.content))
                checks.append(CheckResult(
                    "2.3.2",
                    "Steps have code examples",
                    code_block_count >= step_count,
                    f"{code_block_count} code blocks for {step_count} steps"
                ))
            else:
                basic_count = len(re.findall(r'basic|simple|beginner', self.content, re.IGNORECASE))
                intermediate_count = len(re.findall(r'intermediate', self.content, re.IGNORECASE))
                advanced_count = len(re.findall(r'advanced|production', self.content, re.IGNORECASE))
                has_tiers = basic_count >= 1 and intermediate_count >= 1 and advanced_count >= 1
                checks.append(CheckResult(
                    "2.3.2",
                    "3-tier examples (Basic/Intermediate/Advanced)",
                    has_tiers,
                    f"B:{basic_count} I:{intermediate_count} A:{advanced_count}"
                ))

            # 2.3.3 Patterns have "When to Use" guidance OR Steps have inline guidance
            if self.is_workflow:
                # New-style: Steps use "Use when" or "**When**" inline
                use_guidance = len(re.findall(r'(?:use when|when to use|\*\*when\*\*)', self.content, re.IGNORECASE))
                checks.append(CheckResult(
                    "2.3.3",
                    'Steps have usage guidance',
                    use_guidance >= 2,
                    f"Found {use_guidance} guidance instances"
                ))
            else:
                when_to_use_count = len(re.findall(r'when to use', self.content, re.IGNORECASE))
                checks.append(CheckResult(
                    "2.3.3",
                    'Patterns have "When to Use" guidance',
                    when_to_use_count >= 3,
                    f"Found {when_to_use_count} instances"
                ))

            # 2.3.4 No pattern duplication (heuristic check)
            checks.append(CheckResult(
                "2.3.4",
                "No duplicate patterns (manual review recommended)",
                True,
                "Heuristic check"
            ))

            # 2.3.5 Logical pattern order (heuristic)
            checks.append(CheckResult(
                "2.3.5",
                "Patterns in logical order (manual review recommended)",
                True,
                "Heuristic check"
            ))

            # 2.3.6 At least one comparison table
            has_comparison_table = bool(re.search(r'\|[^|]+\|[^|]+\|', self.content))
            checks.append(CheckResult(
                "2.3.6",
                "At least one comparison table",
                has_comparison_table
            ))

        # 2.4 Problem-Solution structure (2 items)
        # Router skills: relax marker requirements
        # 2.4.1 ❌/✅ markers for bad/good examples
        bad_marker_count = self.content.count('❌')
        good_marker_count = self.content.count('✅')
        if self.is_router:
            has_markers = True  # Routers don't need ❌/✅ examples
            detail = "N/A (router skill)"
        elif self.is_workflow:
            has_markers = bad_marker_count >= 1 and good_marker_count >= 1
            detail = f"❌:{bad_marker_count} ✅:{good_marker_count}"
        else:
            has_markers = bad_marker_count >= 3 and good_marker_count >= 3
            detail = f"❌:{bad_marker_count} ✅:{good_marker_count}"
        checks.append(CheckResult(
            "2.4.1",
            "❌/✅ markers for bad/good example pairs",
            has_markers,
            detail
        ))

        # 2.4.2 "Why" explanations present
        why_count = len(re.findall(r'\bwhy\b', self.content, re.IGNORECASE))
        checks.append(CheckResult(
            "2.4.2",
            '"Why" explanations for approaches',
            why_count >= 5,
            f"Found {why_count} 'why' explanations"
        ))

        # 2.5 Anti-Patterns & Pitfalls (3 items) — N/A for router skills
        if self.is_router:
            for check_id, desc in [
                ("2.5.1", "Anti-Patterns address architecture-level issues"),
                ("2.5.2", "Pitfalls address implementation-level issues"),
                ("2.5.3", "Issues have fixes/solutions"),
            ]:
                checks.append(CheckResult(check_id, desc, True, "N/A (router skill)"))
        else:
            # Extract all Anti-Patterns and Pitfalls sections (there may be multiple)
            antipatterns_sections = re.findall(
                r'^##\s+Anti-Patterns.*?\n(.*?)(?=^##\s|\Z)',
                self.content, re.MULTILINE | re.DOTALL | re.IGNORECASE
            )
            pitfalls_sections = re.findall(
                r'^##\s+.*Pitfalls.*?\n(.*?)(?=^##\s|\Z)',
                self.content, re.MULTILINE | re.DOTALL | re.IGNORECASE
            )
            
            # Combine all sections
            all_antipatterns = "\n".join(antipatterns_sections)
            all_pitfalls = "\n".join(pitfalls_sections)

            # 2.5.1 Anti-Patterns address architecture-level issues
            has_architecture_terms = any(term in all_antipatterns.lower() 
                                        for term in ['architecture', 'design', 'structure', 'layer'])
            checks.append(CheckResult(
                "2.5.1",
                "Anti-Patterns address architecture-level issues",
                has_architecture_terms or len(all_antipatterns) > 100
            ))

            # 2.5.2 Pitfalls address implementation-level issues
            has_implementation_terms = any(term in all_pitfalls.lower() 
                                          for term in ['implement', 'code', 'method', 'function'])
            checks.append(CheckResult(
                "2.5.2",
                "Pitfalls address implementation-level issues",
                has_implementation_terms or len(all_pitfalls) > 100
            ))

            # 2.5.3 Each issue has fix/solution
            content_no_code = re.sub(r'^```.*?^```', '', self.content, flags=re.DOTALL | re.MULTILINE)
            fix_count = len(re.findall(r'\b(fix|solution|instead|correct)\b', 
                                       content_no_code, re.IGNORECASE))
            checks.append(CheckResult(
                "2.5.3",
                "Issues have fixes/solutions",
                fix_count >= 3,
                f"Found {fix_count} fix indicators"
            ))

        # 2.6 Quick Reference (2 items)
        quick_ref = self.get_section_content("Quick Reference") or \
                   self.get_section_content("Decision Tree") or ""

        # 2.6.1 Decision support table/flowchart
        has_decision_support = (
            bool(re.search(r'\|[^|]+\|[^|]+\|', quick_ref)) or
            'flowchart' in quick_ref.lower() or
            'decision' in quick_ref.lower()
        )
        checks.append(CheckResult(
            "2.6.1",
            "Decision support table/flowchart",
            has_decision_support
        ))

        # 2.6.2 Scannable (can understand patterns at a glance)
        is_scannable = len(quick_ref) > 50 and has_decision_support
        checks.append(CheckResult(
            "2.6.2",
            "Scannable (main patterns understandable at glance)",
            is_scannable
        ))

        return checks


class CodeQualityValidator(SkillValidator):
    """Validates code quality requirements (15 items)"""

    def validate(self) -> List[CheckResult]:
        checks = []

        # Router skills: skip most code quality checks (they have minimal code)
        if self.is_router:
            check_ids = [
                ("3.1.1", "Code compilable or marked as pseudocode"),
                ("3.1.2", "Using/import statements included"),
                ("3.1.3", "Dependencies documented"),
                ("3.2.1", "Simple → Intermediate → Advanced progression"),
                ("3.2.2", "Evolution rationale explained"),
                ("3.2.3", "Advanced examples production-ready"),
                ("3.3.1", "✅/❌ markers used consistently"),
                ("3.3.2", 'Comments explain "WHY" not "HOW"'),
                ("3.3.3", "Comments concise (≤50 chars)"),
                ("3.3.4", "No redundant comments"),
                ("3.4.1", "DI configuration examples"),
                ("3.4.2", "Configuration file examples"),
                ("3.4.3", "Error handling examples"),
                ("3.4.4", "Async/await properly implemented"),
                ("3.4.5", "Resource management"),
            ]
            for check_id, desc in check_ids:
                checks.append(CheckResult(check_id, desc, True, "N/A (router skill)"))
            return checks

        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', self.content, re.DOTALL)

        # 3.1 Compilability (3 items)
        # 3.1.1 Code is compilable or marked as pseudocode
        has_pseudocode_marker = 'pseudocode' in self.content.lower()
        has_code = len(code_blocks) > 0
        checks.append(CheckResult(
            "3.1.1",
            "Code compilable or marked as pseudocode",
            has_code or has_pseudocode_marker,
            f"{len(code_blocks)} code blocks found"
        ))

        # 3.1.2 Using statements included (relax for workflow skills with CLI examples)
        has_using = any('using ' in block or 'import ' in block for block in code_blocks)
        has_imports = has_using
        if self.is_workflow:
            # Workflow skills may only use CLI commands — import not required
            checks.append(CheckResult(
                "3.1.2",
                "Using/import statements included",
                has_imports or True,
                "Found" if has_imports else "N/A (workflow skill)"
            ))
        else:
            checks.append(CheckResult(
                "3.1.2",
                "Using/import statements included",
                has_using or not has_code,
                "Found" if has_using else "Check if needed"
            ))

        # 3.1.3 Dependencies documented
        has_dependencies = any(term in self.content.lower() 
                             for term in ['nuget', 'package', 'dependency', 'dependencies', 'npm', 'pip'])
        checks.append(CheckResult(
            "3.1.3",
            "Dependencies documented",
            has_dependencies or len(code_blocks) == 0
        ))

        # 3.2 Progressive evolution (3 items)
        # For workflow skills: Steps provide progression, not Basic/Intermediate/Advanced
        if self.is_workflow:
            step_count = len(re.findall(r'^###\s+Step\s+\d+', self.content, re.MULTILINE))
            checks.append(CheckResult(
                "3.2.1",
                "Steps provide sequential progression",
                step_count >= 3,
                f"{step_count} steps found"
            ))
            # Evolution rationale — check for "why" / "reason" explanations
            evolution_terms = ['why', 'because', 'reason', 'values']
            has_rationale = sum(1 for term in evolution_terms if term in self.content.lower()) >= 2
            checks.append(CheckResult("3.2.2", "Rationale explained", has_rationale))
            # Production-ready — N/A for process-oriented workflows
            checks.append(CheckResult(
                "3.2.3",
                "Examples are practical and usable",
                len(code_blocks) >= 3,
                f"{len(code_blocks)} code blocks"
            ))
        else:
            simple_idx = self.content.lower().find('simple')
            inter_idx = self.content.lower().find('intermediate')
            adv_idx = self.content.lower().find('advanced')
            
            has_progression = False
            if simple_idx != -1 and inter_idx != -1 and adv_idx != -1:
                has_progression = simple_idx < inter_idx < adv_idx
            
            checks.append(CheckResult(
                "3.2.1",
                "Simple → Intermediate → Advanced progression",
                has_progression or len(code_blocks) < 3,
                "Found progression" if has_progression else "Check code examples"
            ))

            # 3.2.2 Evolution rationale explained
            evolution_terms = ['evolve', 'improve', 'enhance', 'why', 'because', 'reason']
            has_rationale = sum(1 for term in evolution_terms if term in self.content.lower()) >= 3
            checks.append(CheckResult(
                "3.2.2",
                "Evolution rationale explained",
                has_rationale
            ))

            # 3.2.3 Advanced examples are production-ready
            has_error_handling = any(term in self.content.lower() 
                                    for term in ['try', 'catch', 'exception', 'error handling'])
            checks.append(CheckResult(
                "3.2.3",
                "Advanced examples production-ready (error handling)",
                has_error_handling
            ))

        # 3.3 Markers and comments (4 items)
        # 3.3.1 ✅/❌ markers used consistently
        marker_count = self.content.count('✅') + self.content.count('❌')
        min_markers = 2 if self.is_workflow else 6
        checks.append(CheckResult(
            "3.3.1",
            "✅/❌ markers used consistently",
            marker_count >= min_markers,
            f"{marker_count} markers found"
        ))

        # 3.3.2 Comments explain WHY not HOW
        comment_count = sum(block.count('//') + block.count('#') for block in code_blocks)
        checks.append(CheckResult(
            "3.3.2",
            'Comments explain "WHY" not "HOW"',
            comment_count >= 3 or len(code_blocks) == 0,
            f"{comment_count} inline comments"
        ))

        # 3.3.3 Concise comments (≤50 chars per line)
        # Heuristic check
        checks.append(CheckResult(
            "3.3.3",
            "Comments concise (≤50 chars)",
            True,
            "Manual review recommended"
        ))

        # 3.3.4 No redundant comments
        checks.append(CheckResult(
            "3.3.4",
            "No redundant comments",
            True,
            "Manual review recommended"
        ))

        # 3.4 Completeness (5 items)
        # Workflow skills focused on process/CLI don't require DI/config/error patterns
        if self.is_workflow:
            # 3.4.1-3.4.5: relaxed for workflow skills
            checks.append(CheckResult("3.4.1", "DI configuration examples (if applicable)", True, "N/A (workflow skill)"))
            has_config = any(term in self.content.lower()
                            for term in ['config', 'configuration', '.yml', '.yaml', '.json'])
            checks.append(CheckResult("3.4.2", "Configuration file examples (if applicable)", has_config or True, "N/A (workflow skill)"))
            checks.append(CheckResult("3.4.3", "Error handling examples", True, "N/A (workflow skill)"))
            checks.append(CheckResult("3.4.4", "Async/await properly implemented", True, "N/A (workflow skill)"))
            checks.append(CheckResult("3.4.5", "Resource management", True, "N/A (workflow skill)"))
        else:
            has_di = any(term in self.content.lower() 
                        for term in ['dependency injection', 'addscoped', 'addsingleton', 
                                    'addtransient', 'configure services'])
            checks.append(CheckResult(
                "3.4.1",
                "DI configuration examples (if applicable)",
                has_di or 'N/A' in self.content,
                "Found" if has_di else "Check if applicable"
            ))

            # 3.4.2 Configuration file examples
            has_config = any(term in self.content.lower() 
                            for term in ['appsettings.json', 'config', 'configuration', 
                                        'app.config', 'web.config'])
            checks.append(CheckResult(
                "3.4.2",
                "Configuration file examples (if applicable)",
                has_config or len(code_blocks) < 3,
                "Found" if has_config else "Check if applicable"
            ))

            # 3.4.3 Error handling examples
            has_error_handling_34 = any(term in self.content.lower() 
                                       for term in ['try', 'catch', 'exception', 'error handling'])
            checks.append(CheckResult(
                "3.4.3",
                "Error handling examples",
                has_error_handling_34,
                "Found" if has_error_handling_34 else "Missing"
            ))

            # 3.4.4 Async properly implemented
            has_async = any(term in self.content.lower() 
                           for term in ['async', 'await', 'task<', 'cancellationtoken'])
            checks.append(CheckResult(
                "3.4.4",
                "Async/await properly implemented",
                has_async or not any('async' in block.lower() for block in code_blocks),
                "Found" if has_async else "N/A or missing"
            ))

            # 3.4.5 Resource management (using, Dispose)
            has_resource_mgmt = any(term in self.content.lower() 
                                   for term in ['using', 'dispose', 'idisposable'])
            checks.append(CheckResult(
                "3.4.5",
                "Resource management (using, Dispose)",
                has_resource_mgmt or len(code_blocks) < 3,
                "Found" if has_resource_mgmt else "Check if applicable"
            ))

        return checks


class LanguageValidator(SkillValidator):
    """Validates language and expression requirements (10 items)"""

    def validate(self) -> List[CheckResult]:
        checks = []

        # 4.1 Writing style (4 items)
        # 4.1.1 Active voice (minimal passive)
        passive_indicators = ['is recommended', 'is used', 'is implemented', 
                             'are required', 'was created', 'were designed']
        passive_count = sum(self.content.lower().count(p) for p in passive_indicators)
        sentence_count = self.content.count('.')
        passive_ratio = passive_count / max(sentence_count, 1)
        
        checks.append(CheckResult(
            "4.1.1",
            "Active voice (passive < 20%)",
            passive_ratio < 0.2,
            f"{passive_count} passive indicators in {sentence_count} sentences"
        ))

        # 4.1.2 Short sentences
        # Heuristic: check for overly long lines in prose sections
        prose_lines = [line for line in self.lines 
                      if line.strip() and not line.startswith('#') 
                      and not line.startswith('```')
                      and not line.startswith('|')]
        long_sentences = sum(1 for line in prose_lines if len(line) > 200)
        checks.append(CheckResult(
            "4.1.2",
            "Short sentences (≤20 words in English, ≤50 chars in Japanese)",
            long_sentences < len(prose_lines) * 0.2,
            f"{long_sentences} potentially long sentences"
        ))

        # 4.1.3 Imperative mood
        imperative_count = sum(1 for line in self.lines 
                              if re.match(r'^[-*]\s+(Use|Implement|Create|Define|Apply|Avoid|Consider)', line))
        checks.append(CheckResult(
            "4.1.3",
            'Imperative mood ("Use", "Implement" vs "You should")',
            imperative_count >= 5,
            f"{imperative_count} imperative statements"
        ))

        # 4.1.4 No vague terms
        vague_terms = ['may', 'might', 'possibly', 'perhaps', 'sometimes', 'often']
        vague_count = sum(self.content.lower().count(term) for term in vague_terms)
        checks.append(CheckResult(
            "4.1.4",
            'Minimal vague terms ("may", "might", "possibly")',
            vague_count < 10,
            f"{vague_count} vague terms found"
        ))

        # 4.2 Term consistency (3 items)
        # 4.2.1 Same concept, same term
        # Heuristic: look for synonym pairs
        checks.append(CheckResult(
            "4.2.1",
            "Consistent terminology (manual review recommended)",
            True,
            "Heuristic check"
        ))

        # 4.2.2 Terms defined on first use
        # Check for bold definitions
        definition_count = len(re.findall(r'\*\*[A-Z][^*]+\*\*:', self.content))
        min_definitions = 1 if self.is_workflow else 3
        checks.append(CheckResult(
            "4.2.2",
            "Technical terms defined on first use",
            definition_count >= min_definitions,
            f"{definition_count} definitions found"
        ))

        # 4.2.3 Acronyms expanded
        # Look for pattern: ACRONYM (Full Form) or Full Form (ACRONYM)
        acronym_pattern = r'\b[A-Z]{2,}\b\s*\([^)]+\)|\([A-Z]{2,}\)'
        acronym_count = len(re.findall(acronym_pattern, self.content))
        checks.append(CheckResult(
            "4.2.3",
            "Acronyms expanded on first use",
            acronym_count >= 1,
            f"{acronym_count} expanded acronyms"
        ))

        # 4.3 Scannability (3 items)
        # 4.3.1 Headings reveal structure
        heading_count = self.count_sections(r'^#{2,3}\s+')
        checks.append(CheckResult(
            "4.3.1",
            "Headings reveal document structure",
            heading_count >= 10,
            f"{heading_count} headings (H2/H3)"
        ))

        # 4.3.2 Tables readable (3-6 columns, 5-10 rows)
        tables = re.findall(r'(\|[^\n]+\|\n)+', self.content)
        readable_tables = True
        for table in tables:
            cols = table.split('\n')[0].count('|') - 1
            rows = len(table.split('\n'))
            if not (3 <= cols <= 6) or rows > 15:
                readable_tables = False
                break
        checks.append(CheckResult(
            "4.3.2",
            "Tables readable (3-6 cols, reasonable rows)",
            readable_tables or len(tables) == 0,
            f"{len(tables)} tables found"
        ))

        # 4.3.3 Important info highlighted
        bold_count = self.content.count('**')
        has_tables = len(tables) > 0
        checks.append(CheckResult(
            "4.3.3",
            "Important info highlighted (bold, tables)",
            bold_count >= 20 and has_tables,
            f"{bold_count//2} bold items, {len(tables)} tables"
        ))

        return checks


def validate_skill_file(file_path: str) -> ValidationReport:
    """Main validation function"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = path.read_text(encoding='utf-8')
    
    # Detect router skills (description contains "router" or first 500 chars mention "router skill")
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    frontmatter = frontmatter_match.group(1) if frontmatter_match else ''
    is_router = 'router' in frontmatter.lower() or 'router skill' in content[:500].lower()
    is_workflow = bool(re.search(r'^##\s+Workflow:', content, re.MULTILINE)) and not is_router
    
    # Run all validators
    structure = StructureValidator(content, file_path, is_router=is_router, is_workflow=is_workflow)
    content_validator = ContentValidator(content, file_path, is_router=is_router, is_workflow=is_workflow)
    code_quality = CodeQualityValidator(content, file_path, is_router=is_router, is_workflow=is_workflow)
    language = LanguageValidator(content, file_path, is_router=is_router, is_workflow=is_workflow)
    
    # Collect results
    categories = []
    
    # Structure (dynamic item count, 80% threshold)
    structure_checks = structure.validate()
    structure_max = len(structure_checks)
    structure_score = sum(1 for c in structure_checks if c.passed)
    structure_result = CategoryResult(
        name="Structure",
        checks=structure_checks,
        score=structure_score,
        max_score=structure_max,
        percentage=structure_score / structure_max * 100 if structure_max > 0 else 0,
        passed=structure_score >= structure_max * 0.8
    )
    categories.append(structure_result)
    
    # Content (20 items, 80% threshold)
    content_checks = content_validator.validate()
    content_max = len(content_checks)
    content_score = sum(1 for c in content_checks if c.passed)
    content_result = CategoryResult(
        name="Content",
        checks=content_checks,
        score=content_score,
        max_score=content_max,
        percentage=content_score / content_max * 100 if content_max > 0 else 0,
        passed=content_score >= content_max * 0.8
    )
    categories.append(content_result)
    
    # Code Quality (15 items, 80% threshold)
    code_checks = code_quality.validate()
    code_max = len(code_checks)
    code_score = sum(1 for c in code_checks if c.passed)
    code_result = CategoryResult(
        name="Code Quality",
        checks=code_checks,
        score=code_score,
        max_score=code_max,
        percentage=code_score / code_max * 100 if code_max > 0 else 0,
        passed=code_score >= code_max * 0.8
    )
    categories.append(code_result)
    
    # Language (10 items, 80% threshold)
    language_checks = language.validate()
    language_max = len(language_checks)
    language_score = sum(1 for c in language_checks if c.passed)
    language_result = CategoryResult(
        name="Language",
        checks=language_checks,
        score=language_score,
        max_score=language_max,
        percentage=language_score / language_max * 100 if language_max > 0 else 0,
        passed=language_score >= language_max * 0.8
    )
    categories.append(language_result)
    
    # Overall
    total_score = sum(c.score for c in categories)
    total_max = sum(c.max_score for c in categories)
    overall_percentage = total_score / total_max * 100 if total_max > 0 else 0
    overall_passed = overall_percentage >= 85 and all(c.passed for c in categories)
    
    return ValidationReport(
        file_path=file_path,
        categories=categories,
        total_score=total_score,
        total_max_score=total_max,
        overall_percentage=overall_percentage,
        overall_passed=overall_passed
    )


def format_text_report(report: ValidationReport) -> str:
    """Format validation report as text"""
    lines = []
    lines.append("=" * 60)
    lines.append("=== Skill Quality Validation Report ===")
    lines.append("=" * 60)
    lines.append(f"File: {report.file_path}")
    lines.append("")
    
    for category in report.categories:
        lines.append(str(category))
        for check in category.checks:
            status = "✅" if check.passed else "❌"
            detail = f" - {check.details}" if check.details else ""
            lines.append(f"  {status} {check.id} {check.description}{detail}")
        lines.append("")
    
    lines.append("-" * 60)
    overall_status = "✅ PASS" if report.overall_passed else "❌ FAIL"
    lines.append(f"Overall: {report.total_score}/{report.total_max_score} "
                f"({report.overall_percentage:.1f}%) {overall_status}")
    lines.append(f"Threshold: {report.overall_threshold}% (each category ≥80%)")
    lines.append("-" * 60)
    
    if not report.overall_passed:
        lines.append("")
        lines.append("⚠️  FAILED CHECKS:")
        for category in report.categories:
            failed = [c for c in category.checks if not c.passed]
            if failed:
                lines.append(f"\n[{category.name}]:")
                for check in failed:
                    lines.append(f"  ❌ {check.id} {check.description}")
                    if check.details:
                        lines.append(f"     {check.details}")
    
    return "\n".join(lines)


def format_json_report(report: ValidationReport) -> str:
    """Format validation report as JSON"""
    data = {
        "file_path": report.file_path,
        "overall": {
            "score": report.total_score,
            "max_score": report.total_max_score,
            "percentage": round(report.overall_percentage, 2),
            "passed": report.overall_passed,
            "threshold": report.overall_threshold
        },
        "categories": []
    }
    
    for category in report.categories:
        cat_data = {
            "name": category.name,
            "score": category.score,
            "max_score": category.max_score,
            "percentage": round(category.percentage, 2),
            "passed": category.passed,
            "threshold": category.threshold,
            "checks": [
                {
                    "id": check.id,
                    "description": check.description,
                    "passed": check.passed,
                    "details": check.details
                }
                for check in category.checks
            ]
        }
        data["categories"].append(cat_data)
    
    return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md against quality checklist (supports legacy + single-workflow)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_skill.py path/to/SKILL.md
  python validate_skill.py path/to/SKILL.md --json
  python validate_skill.py path/to/SKILL.md --output report.txt
  python validate_skill.py path/to/SKILL.md --json --output report.json
        """
    )
    
    parser.add_argument(
        'skill_file',
        help='Path to SKILL.md file to validate'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output report in JSON format'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Write report to file instead of stdout'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation process'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Validating: {args.skill_file}")
            print("Running checks...")
        
        report = validate_skill_file(args.skill_file)
        
        if args.json:
            output = format_json_report(report)
        else:
            output = format_text_report(report)
        
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"Report written to: {args.output}")
        else:
            print(output)
        
        # Exit with appropriate code
        exit(0 if report.overall_passed else 1)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(3)


if __name__ == "__main__":
    import sys
    main()
