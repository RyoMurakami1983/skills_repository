---
name: skills-refactor-skill-to-single-workflow
description: Convert a legacy multi-pattern skill into a single-workflow skill. Use when migrating existing skills.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, refactoring, migration]
  invocable: false
---

# Refactor a Skill to Single Workflow

End-to-end workflow for converting a legacy multi-pattern SKILL.md (7–10 `## Pattern N:` sections) into a single-workflow skill following the "1 skill = 1 workflow" principle.

## When to Use This Skill

Use this skill when:
- Converting an existing multi-pattern skill to the single-workflow standard
- Migrating legacy skills during the repository-wide modernization effort
- Deciding which patterns to consolidate vs. split into separate skills
- Creating router skills that point to newly split workflow skills
- Reducing SKILL.md from 500+ lines by extracting content to references/

---

## Related Skills

- **`skills-author-skill`** — Write a new skill from scratch (use after splitting)
- **`skills-validate-skill`** — Validate the refactored skill against quality criteria
- **`skills-revise-skill`** — Improve naming/discoverability after refactoring

---

## Core Principles

1. **Split by Workflow, Not by Section** — Only create a new skill when a pattern is an independently executable workflow (基礎と型)
2. **Consolidate First** — Prefer merging related patterns into one workflow over splitting into many small skills (ニュートラル)
3. **Preserve Context** — Each resulting skill must be self-contained; avoid splitting so much that context is lost (成長の複利)
4. **Router for Compatibility** — Keep the original directory as a router skill to prevent broken references (継続は力)

---

## Workflow: Refactor to Single Workflow

### Step 1 — Audit the Existing Skill

Count patterns and classify each one:

```markdown
## Audit: skill-writing-guide (9 patterns)

| # | Pattern Name | Type | Decision |
|---|-------------|------|----------|
| 1 | YAML Frontmatter | Topic/section | Consolidate into authoring workflow |
| 2 | "When to Use" Section | Topic/section | Consolidate into authoring workflow |
| 3 | Core Principles | Topic/section | Consolidate into authoring workflow |
| 4 | Pattern Sections | Topic/section | Consolidate into authoring workflow |
| 5 | Code Example Best Practices | Topic/section | Consolidate into authoring workflow |
| 6 | Comparison Tables | Topic/section | Consolidate into authoring workflow |
| 7 | Anti-Patterns vs Pitfalls | Topic/section | Consolidate into authoring workflow |
| 8 | 500-Line Optimization | Topic/section | Consolidate into authoring workflow |
```

**Classification rules**:
- **Topic/section**: Teaching about a concept → **Consolidate** into one skill
- **Independent workflow**: Can be executed start-to-finish alone → **Split** into a new skill
- **Variant**: Same workflow with different inputs → Keep as options within one skill

### Step 2 — Group into Workflows

Map patterns to end-to-end workflows:

```markdown
## Workflow Mapping

Workflow 1: "Author a new skill" (Patterns 1-8 → consolidated)
  → skills-author-skill

Workflow 2: "Validate a skill" (if separate validation existed)
  → skills-validate-skill

Workflow 3: "Optimize discoverability" (if separate)
  → skills-revise-skill
```

**Decision criteria for splitting**:
- ✅ Split when: The workflow has a distinct trigger ("Use when...") AND can run independently
- ❌ Don't split when: The pattern only makes sense in context of the larger workflow

### Step 3 — Write New Skills

For each identified workflow, create a new skill directory:

```
skills/
├── skills-author-skill/           # New: consolidated workflow
│   ├── SKILL.md
│   └── references/SKILL.ja.md
├── skills-validate-skill/         # New: split workflow
│   ├── SKILL.md
│   └── references/SKILL.ja.md
└── skill-writing-guide/           # Legacy: becomes router
    ├── SKILL.md                   # Rewritten as router
    └── references/SKILL.ja.md
```

Follow `skills-author-skill` for each new skill's structure.

### Step 4 — Convert Original to Router

Rewrite the original SKILL.md as a single-workflow router skill:

```yaml
---
name: skill-writing-guide
description: Router skill. Use when unsure which skill-authoring workflow to use.
author: RyoMurakami1983
tags: [copilot, agent-skills, router]
invocable: false
---
```

The router workflow: guide the user to the correct new skill based on their intent.

### Step 5 — Move Overflow Content

Move reference materials from the original skill to appropriate new skills:

```
# Before
skill-writing-guide/references/anti-patterns.md

# After (move to most relevant new skill)
skills-author-skill/references/anti-patterns.md
```

### Step 6 — Update Cross-References

Search for references to the old skill name and update or add notes:

```bash
# Find all references to the old skill
grep -r "skill-writing-guide" --include="*.md" .
```

### Step 7 — Validate All Results

Run `skills-validate-skill` on each new skill AND the router to ensure compliance.

---

## Good Practices

### 1. Consolidate Before Splitting

**What**: Start by merging all patterns into one workflow; only split if the result exceeds 500 lines or contains truly independent workflows.

**Why**: Over-splitting creates context loss and increases maintenance burden.

**Values**: 基礎と型（最小形式で最大可能性）/ ニュートラル（誰もが使える普遍性）

### 2. Keep Router Skills Minimal

**What**: Router SKILL.md should be < 100 lines — just frontmatter, "When to Use", and a decision table.

**Why**: Routers exist for backward compatibility, not as content repositories.

**Values**: 継続は力（既存参照を壊さない）

### 3. Preserve Author and Values

**What**: All new skills retain `author: RyoMurakami1983` and Constitution Values integration.

**Why**: Authorship and philosophy connection are non-negotiable for this repository.

**Values**: 成長の複利（教える喜び、学ぶ喜び）

---

## Common Pitfalls

### 1. Splitting Every Pattern into Its Own Skill

**Problem**: Creating 8 micro-skills from 8 patterns, each too small to be useful alone.

**Solution**: Only split when the pattern is an independently executable workflow with its own "When to Use".

### 2. Losing Context in the Split

**Problem**: After splitting, each new skill refers to concepts explained in other skills.

**Solution**: Each skill must be self-contained. Duplicate essential context rather than cross-referencing extensively.

### 3. Forgetting the Router

**Problem**: Deleting the original directory, breaking all existing references.

**Solution**: Always convert the original into a router skill; never delete it during migration.

### 4. Not Updating Cross-References

**Problem**: Other skills still reference old pattern numbers that no longer exist.

**Solution**: Search the entire repo for old skill name references and update them.

---

## Anti-Patterns

### Section-Level Splitting

**What**: Making "When to Use" a skill, "Core Principles" another skill, etc.

**Why It's Wrong**: These are sections of a skill, not independent workflows. Splitting destroys the context needed to understand each part.

**Better Approach**: Keep all standard sections within each workflow skill.

### Big-Bang Migration

**What**: Trying to migrate all skills at once in one PR.

**Why It's Wrong**: Too risky, hard to review, high chance of breaking references.

**Better Approach**: Migrate one skill family at a time, validate, then proceed.

---

## Quick Reference

### Refactoring Decision Tree

```
For each Pattern in the legacy skill:
│
├─ Is it an independently executable workflow?
│  ├─ YES → Does it have its own distinct "When to Use"?
│  │  ├─ YES → Split into new skill
│  │  └─ NO  → Consolidate into parent workflow
│  └─ NO  → Consolidate into parent workflow
│
After consolidation:
├─ Result ≤ 500 lines? → Done
└─ Result > 500 lines? → Move details to references/
```

### Migration Checklist

- [ ] Audit: count patterns, classify each
- [ ] Group: map patterns to end-to-end workflows
- [ ] Write: create new skill(s) following `skills-author-skill`
- [ ] Router: convert original into router skill
- [ ] Move: relocate references/assets to new skill directories
- [ ] Update: fix cross-references across repo
- [ ] Validate: run `skills-validate-skill` on all results

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — How to write new skills
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Quality validation
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution

---
