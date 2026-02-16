---
name: skills-validate-skill
description: Run quality validation on a SKILL.md with scoring and actionable report. Use when reviewing skills.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, validation, quality]
  invocable: false
---

# Validate a Skill

End-to-end workflow for running quality validation on a SKILL.md file, producing a scored report across structure, content, code quality, and language categories, with actionable improvement recommendations.

## When to Use This Skill

Use this skill when:
- Reviewing a completed SKILL.md before publishing or merging
- Assessing skill quality against the structured checklist criteria
- Generating a quality report with scores and specific improvement items
- Performing peer review of skill documentation and code examples
- Verifying compliance with the "1 skill = 1 workflow" standard
- Re-validating a skill after applying fixes from a previous report

---

## Related Skills

- **`skills-author-skill`** — Write a new skill following best practices
- **`skills-refactor-skill-to-single-workflow`** — Convert legacy multi-pattern skills
- **`skills-revise-skill`** — Revise and version existing skills

---

## Core Principles

1. **Quantitative Assessment** — Use a structured checklist with objective pass/fail criteria; never rely on subjective impressions alone (基礎と型)
2. **Category-Based Scoring** — Evaluate across Structure, Content, Code Quality, and Language independently (ニュートラル)
3. **Actionable Feedback** — Every failed item must include a specific, implementable fix recommendation (成長の複利)
4. **Continuous Improvement** — First pass targets ≥ 80%; iterate to reach 90%+ (継続は力)

---

## Workflow: Validate a Skill

### Step 1 — Structure Validation

Check the physical file structure and section ordering. These are prerequisites for all other checks.

**Structure Checklist**:

| # | Check | Rule | Severity |
|---|-------|------|----------|
| S1 | Single file | SKILL.md is primary file (references/ allowed) | Critical |
| S2 | YAML frontmatter | Contains name, description, metadata(author/tags/invocable) | Critical |
| S3 | Name consistency | `name:` matches directory name (kebab-case) | Critical |
| S4 | Naming convention | Follows `<context>-<workflow>` format | Warning |
| S5 | Description length | ≤ 1024 characters, includes "Use when..." | Error |
| S6 | When to Use position | First H2 section after title | Error |
| S7 | Core Principles | Section exists with 3–5 principles | Error |
| S8 | Single workflow | One `## Workflow:` section (not multiple `## Pattern N:`) | Error |
| S9 | Good Practices | Section exists | Warning |
| S10 | Common Pitfalls | Section exists | Warning |
| S11 | Quick Reference | Section or decision tree exists | Warning |
| S12 | File length | ≤ 500 lines (≤ 550 with tolerance) | Warning |
| S13 | References dir | If > 500 lines, `references/` exists | Error |
| S14 | Japanese version | `references/SKILL.ja.md` exists | Bonus |

**Pass criteria**: All Critical items pass + ≥ 80% overall

### Step 2 — Content Validation

Assess completeness, clarity, and practical utility of skill content.

**Content Checklist**:

| # | Check | Rule |
|---|-------|------|
| C1 | Scenario count | "When to Use" has 5–8 items |
| C2 | Verb-led scenarios | Each scenario starts with a verb |
| C3 | Scenario specificity | No abstract phrases ("good code", "quality") |
| C4 | Principles count | 3–5 Core Principles |
| C5 | Values integration | Core Principles reference ≥ 2 PHILOSOPHY Values |
| C6 | Workflow completeness | Workflow has sequential steps with examples |
| C7 | Why explanations | Steps include rationale (why, not just what) |
| C8 | Good Practices Values | Each practice links to a Value |
| C9 | Pitfalls structure | Each has Problem + Solution format |
| C10 | Anti-patterns structure | Each has What + Why + Better Approach |
| C11 | Related Skills | Section exists with relevant links |
| C12 | Resources | Section exists with valid links |

**Pass criteria**: ≥ 80% (10/12)

### Step 3 — Code Quality Validation

Validate code examples for quality and educational value.

**Code Checklist**:

| # | Check | Rule |
|---|-------|------|
| Q1 | Markers | ✅/❌ used consistently in code blocks |
| Q2 | Comments | Comments explain WHY, not WHAT |
| Q3 | Import statements | Code includes necessary imports |
| Q4 | Example length | Inline examples ≤ 15 lines |
| Q5 | Compilable | Code is syntactically valid |
| Q6 | Progressive | Examples progress from simple to advanced |

**Pass criteria**: ≥ 80% (5/6)

### Step 4 — Language Validation

Validate writing style and readability.

**Language Checklist**:

| # | Check | Rule |
|---|-------|------|
| L1 | Active voice | ≥ 80% of sentences use active voice |
| L2 | Sentence length | ≤ 20 words per sentence average |
| L3 | Consistent terms | Same concept uses same term throughout |
| L4 | Scannable headers | H2/H3 headers reveal content structure |
| L5 | Table clarity | Tables use Scenario/Recommendation/Why format |

**Pass criteria**: ≥ 80% (4/5)

### Step 5 — Generate Report

Compile results into a structured report:

```markdown
# Quality Report: <skill-name>

**Date**: YYYY-MM-DD
**Validator**: skills-validate-skill v1.0

## Summary

| Category | Score | Status |
|----------|-------|--------|
| Structure | 12/14 (86%) | ✅ PASS |
| Content | 10/12 (83%) | ✅ PASS |
| Code Quality | 5/6 (83%) | ✅ PASS |
| Language | 4/5 (80%) | ✅ PASS |
| **Overall** | **31/37 (84%)** | **✅ PASS** |
| Bonus | +1 (Japanese) | ➕ |

## Failed Items

### [S12] File length — WARNING
- Current: 520 lines
- Target: ≤ 500 lines
- Fix: Move detailed examples to references/advanced-examples.md

### [C5] Values integration — ERROR
- Found: 1 Value reference (基礎と型)
- Required: ≥ 2 Values
- Fix: Add a second Value to Core Principles (e.g., 成長の複利)

## Recommendations
1. Priority: Fix [C5] Values integration (ERROR)
2. Consider: Reduce file length [S12] (WARNING)
```

### Step 6 — Re-validate After Fixes

After applying fixes, re-run the full validation to confirm no regressions.

### Step 7 — Remediate by Severity (Integrated)

Use this integrated loop to fix findings systematically:

1. Fix **Critical** items first (hard gates)
2. Fix **Error** items next (publish blockers)
3. Fix **Warning** items to push quality from 80% to 90%+
4. Re-run full validation after each fix batch

Common remediation actions:
- Multiple patterns → consolidate to one `## Workflow:` with `### Step N`
- Missing Values integration → add explicit Value linkage in Core Principles
- Oversized file → move details to `references/` and keep SKILL.md lean
- Missing JA parity → mirror section/step/table structure in `references/SKILL.ja.md`

---

## Good Practices

### 1. Validate Early and Often

**What**: Run validation during writing, not just at the end.

**Why**: Catching issues early prevents compound errors.

**Values**: 継続は力（コツコツ積み上げ）

### 2. Fix Structure First

**What**: Structure failures block everything else — fix them before content.

**Why**: A skill with broken structure can't be properly evaluated for content or code quality.

**Values**: 基礎と型（基礎が揺らいでいる上に応用を積んでも崩れる）

### 3. Use Reports as Learning Assets

**What**: Save quality reports and analyze common failure patterns.

**Why**: Reports become compound learning material for future skill authors.

**Values**: 成長の複利（ドキュメントを学習資産として設計）

### 4. Review EN First, Check JA Structure Parity

**What**: Use `SKILL.md` as the primary review target, then check `references/SKILL.ja.md` for structural equivalence (same major sections/steps/tables).

**Why**: This keeps review focus high while preserving bilingual consistency.

**Values**: ニュートラル（判断基準を明示） / 基礎と型（構造の型を守る）

---

## Common Pitfalls

### 1. Passing Skills with Critical Failures

**Problem**: A skill scores 85% overall but has a Critical structure failure.

**Solution**: Critical items are hard gates — must all pass regardless of overall score.

### 2. Ignoring Warnings

**Problem**: Treating warnings as "nice to have" and never addressing them.

**Solution**: Warnings should be fixed before reaching 90%+ target quality.

### 3. Not Re-validating After Fixes

**Problem**: Fixing one issue introduces another (regression).

**Solution**: Always re-run full validation after any changes.

### 4. Over-Reviewing Japanese Wording While Missing Risk Mismatch

**Problem**: Spending time on JP phrasing details but missing safety-risk reversals, meaning inversion, or broken procedures between EN/JA.

**Solution**: Prioritize structural parity and risk-critical meaning alignment; treat style wording differences as secondary.

---

## Anti-Patterns

### Rubber-Stamp Validation

**What**: Running validation as a formality without acting on results.

**Why It's Wrong**: Defeats the purpose; quality degrades over time.

**Better Approach**: Treat every failed item as a required action item.

### Validating Only New Skills

**What**: Never re-validating existing skills as standards evolve.

**Why It's Wrong**: Standards improve; existing skills should be brought up to current standards.

**Better Approach**: Periodically re-validate all skills, especially after standard changes.

---

## Quick Reference

### Validation Workflow

```
1. Structure Check
   ├─ All Critical pass? → Continue
   └─ Any Critical fail? → STOP, fix first

2. Content Check (≥ 80%)
   ├─ PASS → Continue
   └─ FAIL → Fix content issues

3. Code Quality Check (≥ 80%)
   ├─ PASS → Continue
   └─ FAIL → Fix code examples

4. Language Check (≥ 80%)
   ├─ PASS → Generate report
   └─ FAIL → Improve writing

5. Overall ≥ 80% + all categories ≥ 80%?
    ├─ YES → ✅ PUBLISH
   └─ NO  → Iterate with integrated remediation loop (Step 7)
```

### Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| Critical | Blocks publication | Must fix immediately |
| Error | Significantly impacts quality | Fix before publish |
| Warning | Minor quality issue | Fix to reach 90%+ |
| Bonus | Extra quality points | Nice to have |

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — Authoring best practices
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- Validation scripts: `../skill-quality-validation/scripts/` (validate_skill.py/.ps1/.sh)

---
