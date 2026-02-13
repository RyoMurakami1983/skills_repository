---
name: skills-remediate-validation-findings
description: Fix validation failures systematically from a quality report. Use when a skill fails validation.
author: RyoMurakami1983
tags: [copilot, agent-skills, remediation, quality]
invocable: false
---

# Remediate Validation Findings

End-to-end workflow for taking a failed quality report and systematically applying fixes to bring a skill up to passing quality (≥ 80% overall, all categories ≥ 80%).

## When to Use This Skill

Use this skill when:
- A skill has failed quality validation and you have a report with specific findings
- Prioritizing which validation failures to fix first for maximum impact
- Applying structured fixes without introducing regressions
- Iterating from an 80% first-pass score toward 90%+ target quality
- Fixing warnings and bonus items after all critical/error items are resolved

---

## Related Skills

- **`skills-validate-skill`** — Generate the quality report this skill consumes
- **`skills-author-skill`** — Reference for correct skill structure
- **`skills-revise-skill`** — Version management after remediation

---

## Core Principles

1. **Fix by Severity** — Address Critical failures first, then Errors, then Warnings (基礎と型)
2. **One Fix at a Time** — Make atomic changes to avoid introducing new issues (継続は力)
3. **Re-validate After Each Fix** — Confirm the fix works and no regression occurred (成長の複利)
4. **Root Cause over Symptom** — Fix the underlying issue, not just the surface manifestation (ニュートラル)

---

## Workflow: Remediate Findings

### Step 1 — Read the Quality Report

Parse the report and categorize findings by severity:

```markdown
## Triage from Report

### Critical (must fix)
- None

### Error (fix before publish)
- [C5] Values integration: Only 1 Value, need ≥ 2
- [S8] Single workflow: Found 3 `## Pattern N:` sections

### Warning (fix for 90%+)
- [S12] File length: 520 lines (target ≤ 500)
- [L2] Sentence length: Average 22 words (target ≤ 20)

### Bonus (nice to have)
- [S14] Japanese version: references/SKILL.ja.md missing
```

### Step 2 — Fix Critical Items

Critical items block everything. Common critical fixes:

| Finding | Fix |
|---------|-----|
| Missing YAML frontmatter | Add complete frontmatter with name, description, author, tags |
| Name mismatch | Rename directory or update `name:` field to match |
| No SKILL.md | Create the file following `skills-author-skill` workflow |

### Step 3 — Fix Error Items

Error items significantly impact quality. Common error fixes:

**[S8] Multiple Patterns → Single Workflow**:
```markdown
# Before (❌)
## Pattern 1: Setup
## Pattern 2: Configure
## Pattern 3: Deploy

# After (✅)
## Workflow: Setup, Configure, and Deploy
### Step 1 — Setup
### Step 2 — Configure
### Step 3 — Deploy
```

**[C5] Values Integration**:
```markdown
# Before (❌) — No Values
1. **Testability** — Design for testing

# After (✅) — With Values
1. **Testability** — Design for testing from day one (基礎と型)
2. **Incremental Improvement** — Small, verified changes compound over time (成長の複利)
```

**[S5] Description without "Use when..."**:
```yaml
# Before (❌)
description: A comprehensive guide for WPF development

# After (✅)
description: Implement MVVM in WPF with DI and testability. Use when building enterprise WPF apps.
```

### Step 4 — Fix Warning Items

After all errors are resolved:

**[S12] File length > 500 lines**:
1. Identify sections that can move to `references/`
2. Move extended examples, detailed anti-patterns, or verbose explanations
3. Add reference links: `> 📚 See references/advanced-examples.md`

**[L2] Sentence length**:
1. Split long sentences at conjunctions (and, but, because)
2. Use bullet points for lists instead of run-on sentences

### Step 5 — Add Bonus Items

After passing all categories at 80%+:

**[S14] Japanese version**:
1. Create `references/SKILL.ja.md` with identical structure
2. Translate all content; add deeper "Why" explanations in Japanese

### Step 6 — Final Re-validation

Run `skills-validate-skill` one final time to confirm:
- All Critical: PASS
- All categories ≥ 80%
- Overall ≥ 80%

---

## Good Practices

### 1. Fix Structure Before Content

**What**: Always resolve structure failures first — they block meaningful content evaluation.

**Why**: Structure is the foundation; fixing content on a broken structure wastes effort.

**Values**: 基礎と型（基礎の正確さを担保する）

### 2. Make Atomic Fixes

**What**: One fix per edit — don't combine multiple fixes in one change.

**Why**: If a combined fix introduces a regression, you can't tell which change caused it.

**Values**: 継続は力（小さなコミットを積み重ねる）

### 3. Track Fix Progress

**What**: Check off resolved items in the report as you go.

**Why**: Prevents re-working already-fixed items and gives clear progress visibility.

**Values**: 成長の複利（改善を記録し共有する）

---

## Common Pitfalls

### 1. Fixing Symptoms Instead of Root Causes

**Problem**: Adding a Value reference to satisfy [C5] without actually understanding why the principle relates to that Value.

**Solution**: Ensure the Value connection is genuine and meaningful, not just checkbox compliance.

### 2. Fixing One Issue, Breaking Another

**Problem**: Moving content to references/ to fix [S12] but forgetting to update internal links.

**Solution**: After each move, check all internal references still resolve.

### 3. Ignoring Warnings Permanently

**Problem**: Hitting 80% and stopping — never reaching 90%+ quality.

**Solution**: Plan a second pass specifically for warnings after the initial publish.

---

## Quick Reference

### Remediation Priority Order

```
1. Critical items     → Must fix (blocks publication)
2. Error items        → Fix before publish
3. Warning items      → Fix for 90%+ quality
4. Bonus items        → Nice to have
5. Re-validate        → Confirm all fixes, no regressions
```

### Common Fixes Quick Reference

| Finding | Quick Fix |
|---------|-----------|
| No "Use when..." | Add to description: `. Use when <scenario>.` |
| Multiple Patterns | Merge into `## Workflow:` with Steps |
| Missing Values | Add Value names in parentheses to Core Principles |
| File too long | Move details to `references/` |
| No Japanese | Create `references/SKILL.ja.md` |
| Passive voice | Rewrite with active verbs |
| Missing markers | Add `// ✅ CORRECT` / `// ❌ WRONG` to code |

---

## Resources

- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Generate quality reports
- [skills-author-skill](../skills-author-skill/SKILL.md) — Correct skill structure reference
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Values reference for integration fixes

---

## Changelog

### Version 1.0.0 (2026-02-13)
- Initial release: remediation workflow for validation findings
- Severity-based triage and fix ordering
- Common fix patterns for structure, content, and language issues

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
