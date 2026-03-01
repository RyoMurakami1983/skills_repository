---
name: skills-maintain-bilingual-skill
description: >
  Maintain EN/JA structural parity for bilingual skills. Use when updating a
  SKILL.md and its references/SKILL.ja.md, synchronizing after adding/removing
  steps or sections, or resolving validate_skill.py W1/W3 warnings.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, bilingual, maintenance, parity]
  invocable: false
---

# Maintain Bilingual Skill Parity

Workflow for keeping `SKILL.md` (English) and `references/SKILL.ja.md` (Japanese) in structural and semantic sync. Applies proven parity checks and validator-driven correction to prevent documentation drift.

## When to Use This Skill

Use this skill when:
- Adding or removing workflow steps in an existing bilingual skill
- Resolving validate_skill.py W1.1 (EN/JA H2 count mismatch) warnings
- Checking safety-critical vocabulary alignment (W3.1/W3.2 warnings)
- Reviewing EN and JA versions after a PR review makes changes
- Synchronizing JA after merging EN-only fixes into a skill
- Confirming that negation patterns (W3.2) in JA match EN intent
- Auditing structural parity before publishing or promoting a skill

---

## Dependencies

- `uv` — Python runner for `validate_skill.py` (`uv run python ...`)
- `skills/skill-quality-validation/scripts/validate_skill.py` — Validator script (already in repo)
- `grep` / `Select-String` — For counting sections and steps

---

## Related Skills

- **`skills-author-skill`** — Writing a new bilingual skill from scratch
- **`skills-revise-skill`** — Full revision workflow including changelog and metadata
- **`skills-validate-skill`** — Run quality validator against all check criteria

---

## Core Principles

1. **Structure Before Content** — Section headings and step counts must match before prose is compared (基礎と型)
2. **Meaning Over Literality** — JA may expand "Why" explanations; EN/JA must agree on intent, not word count (ニュートラル)
3. **Validator as Guardrail** — Run `validate_skill.py` EN first, then JA; fix category failures before warnings (継続は力)
4. **Safety Vocabulary Alignment** — Words like 削除/delete, 認証/auth carry risk; always cross-check W3.1 terms (基礎と型)
5. **Minimal Delta** — Sync the minimum needed to achieve parity; avoid unrelated rewrites (余白の設計)

---

## Workflow: Maintain EN/JA Parity

### Step 1: Run Validator on EN Version

Start with the English file to establish a clean baseline.

```bash
uv run python skills\skill-quality-validation\scripts\validate_skill.py <skill>/SKILL.md
```

Review the output for:
- Category failures (Structure / Content / Code Quality / Language) → fix these first
- Warning W1.1 (H2 count mismatch) → note EN H2 count for Step 2
- Warnings W3.1/W3.2 (safety vocab, negation patterns) → note which lines triggered

> **Values**: 継続は力（基準を毎回確認する習慣が品質を守る）

### Step 2: Build Parity Checklist

Compare EN and JA side by side using this checklist:

| Item | EN count | JA count | Match? |
|------|----------|----------|--------|
| H2 sections | | | |
| Workflow steps (Step N) | | | |
| Code blocks | | | |
| Tables | | | |

```bash
# Count H2 sections
grep -c "^## " SKILL.md
grep -c "^## " references/SKILL.ja.md

# Count steps
grep -c "^### Step" SKILL.md
grep -c "^### Step" references/SKILL.ja.md
```

Acceptable tolerances: code blocks ±2; tables ±1 (JA may add illustrative tables).
Zero tolerance: H2 section count and step count must be identical.

> **Values**: 基礎と型（数値で確認できる型を持つ）

### Step 3: Sync Missing Sections

For each mismatch found in Step 2, add the missing section to the lagging file.

**Adding a section to JA**:
1. Locate the equivalent position in `references/SKILL.ja.md`.
2. Copy the EN section as a starting point.
3. Translate headings and key phrases; expand "Why" explanations.
4. Preserve the `> **Values**: ...` annotation line.

**Removing a section from JA** (when EN section was removed):
1. Remove the corresponding JA section.
2. Re-check that surrounding section numbering is consistent.

> **Values**: ニュートラル（構造を揃えることで読者に依存しない文書を作る）

### Step 4: Align Safety-Critical Vocabulary (W3.1/W3.2)

When the validator reports W3.1 or W3.2, cross-check each flagged term.

**W3.1 — Safety vocab in JA** (削除, 認証, 上書き, 移行, etc.)

| JA term | Expected EN equivalent | Check |
|---------|----------------------|-------|
| 削除 | delete / remove | Do EN and JA describe the same action? |
| 上書き | overwrite | Are the conditions identical? |
| 認証 | authentication / credentials | Are security constraints the same? |

**W3.2 — Negation patterns** (しない, 不可, 禁止, etc.)

Verify that each JA negation has a corresponding EN prohibition or caution:

```markdown
✅ EN: "Never edit migration files manually."
✅ JA: "マイグレーションファイルを手動編集しない。"

❌ JA: "本番環境では実行しない。" (no EN equivalent)
Fix: Add EN: "Do not run against production environments."
```

> **Values**: 基礎と型（安全制約は両言語で同等に伝える）

### Step 5: Run Validator Post-Fix

Re-run the validator to verify remaining warnings are expected or intentional.

```bash
uv run python skills\skill-quality-validation\scripts\validate_skill.py <skill>/SKILL.md
```

The validator reads EN SKILL.md and cross-checks `references/SKILL.ja.md` automatically.
Remaining W3.x warnings need manual judgement — intentional phrases (e.g., Japanese trigger phrases in EN descriptions) are acceptable.

**Acceptance criteria**:
- Overall score ≥ 88%
- No W1.1 (H2 count mismatch)
- All W3.x warnings reviewed and either fixed or explicitly accepted

> **Values**: 継続は力（最後の一手まで検証する）

### Step 6: Commit with Parity Proof

Record the sync action explicitly in the commit message:

```text
docs(<skill-name>): sync EN/JA parity

- Add JA equivalent of Step N (mirrors EN addition in commit <sha>)
- Fix W3.1: align 削除 description with EN "remove" semantics
- Validate: 92.3% PASS

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

> **Values**: 成長の複利（変更理由を記録することで知識が蓄積される）

---

## Common Pitfalls

1. **Editing JA first, then EN**
   Fix: Always start with EN, validate EN baseline, then mirror to JA. JA-first edits create parity gaps.

2. **Translating "Why" too literally**
   Fix: JA versions may expand "Why" with Japanese reasoning context. Richer JA is expected and acceptable.

3. **Ignoring W3 warnings after fixing them**
   Fix: After fixing a W3.1/W3.2 issue, re-run the validator to confirm the warning disappears.

4. **Rewriting EN content while fixing JA parity**
   Fix: Parity sync and EN content improvements belong in separate commits.

---

## Anti-Patterns

### Silent Step Drift

**Problem**: H2 counts match but step counts drift when steps are added inside an existing H2. W1.1 warning does not fire.

**Fix**: Always check Step N counts separately from H2 counts. Include step count in the parity checklist.

### Machine-Translate and Ship

**Problem**: Auto-translating EN section and pasting into JA without review misses domain terms, Values kanji, and skill-specific language.

**Fix**: Translate headings and key phrases manually; expand "Why" with Japanese context.

---

## Quick Reference

### Parity Checklist

```markdown
## EN/JA Parity Checklist — <skill-name>

- [ ] uv run python skills\skill-quality-validation\scripts\validate_skill.py <skill>/SKILL.md
- [ ] H2 count matches
- [ ] Step count matches
- [ ] Code block count within ±2
- [ ] Table count within ±1
- [ ] W3.1 terms verified: 削除 / 認証 / 上書き / 移行
- [ ] W3.2 negations verified: しない / 不可 / 禁止
- [ ] Re-run validator post-fix: score >= 88%
- [ ] Commit message records what was synced
```

### Validator Warning Reference

| Warning | Meaning | Fix |
|---------|---------|-----|
| W1.1 | EN/JA H2 section count differs | Add missing section to lagging file |
| W3.1 | Safety vocab in JA (削除 etc.) | Verify EN has same safety constraint |
| W3.2 | Negation pattern in JA (しない etc.) | Verify EN has equivalent prohibition |
| W5 | Japanese text in EN SKILL.md | Intentional trigger phrases OK; other content → move to JA |
