# Bilingual Parity Workflow (EN/JA)

Detailed parity workflow for `skills-revise-skill` Step 4. Covers structural verification, safety vocabulary alignment, and validator-driven correction.

## Parity Verification Steps

### 1. Run Validator on EN Baseline

```bash
uv run python skills\skill-quality-validation\scripts\validate_skill.py <skill>/SKILL.md
```

Review output for:
- Category failures (Structure / Content / Code Quality / Language) → fix first
- W1.1 (H2 count mismatch) → note EN H2 count
- W3.1/W3.2 (safety vocab, negation patterns) → note flagged lines

### 2. Build Parity Checklist

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

**Tolerances**: code blocks ±2; tables ±1 (JA may add illustrative tables).
**Zero tolerance**: H2 count and step count must be identical.

### 3. Sync Missing Sections

For each mismatch:

**Adding to JA**:
1. Locate equivalent position in `references/SKILL.ja.md`
2. Copy EN section as starting point
3. Translate headings and key phrases; expand "Why" explanations
4. Preserve `> **Values**: ...` annotation

**Removing from JA** (when EN section was removed):
1. Remove corresponding JA section
2. Re-check surrounding section numbering

### 4. Align Safety-Critical Vocabulary (W3.1/W3.2)

**W3.1 — Safety vocab in JA**:

| JA term | Expected EN equivalent | Check |
|---------|----------------------|-------|
| 削除 | delete / remove | Same action described? |
| 上書き | overwrite | Same conditions? |
| 認証 | authentication / credentials | Same security constraints? |
| 移行 | migration | Same scope? |

**W3.2 — Negation patterns** (しない, 不可, 禁止):

```markdown
✅ EN: "Never edit migration files manually."
✅ JA: "マイグレーションファイルを手動編集しない。"

❌ JA: "本番環境では実行しない。" (no EN equivalent)
Fix: Add EN: "Do not run against production environments."
```

### 5. Re-run Validator

```bash
uv run python skills\skill-quality-validation\scripts\validate_skill.py <skill>/SKILL.md
```

**Acceptance criteria**:
- Overall score ≥ 88%
- No W1.1 (H2 count mismatch)
- All W3.x warnings reviewed and either fixed or explicitly accepted

---

## Quick Reference Checklist

```markdown
## EN/JA Parity Checklist — <skill-name>

- [ ] Run validator on EN baseline
- [ ] H2 count matches
- [ ] Step count matches
- [ ] Code block count within ±2
- [ ] Table count within ±1
- [ ] W3.1 terms verified: 削除 / 認証 / 上書き / 移行
- [ ] W3.2 negations verified: しない / 不可 / 禁止
- [ ] Re-run validator post-fix: score >= 88%
- [ ] Commit message records what was synced
```

## Validator Warning Reference

| Warning | Meaning | Fix |
|---------|---------|-----|
| W1.1 | EN/JA H2 section count differs | Add missing section to lagging file |
| W1.3 | EN/JA step count differs | Add/remove steps to match |
| W3.1 | Safety vocab in JA (削除 etc.) | Verify EN has same constraint |
| W3.2 | Negation pattern in JA (しない etc.) | Verify EN has equivalent prohibition |
| W5 | Japanese text in EN SKILL.md | Intentional trigger phrases OK; other → move to JA |
