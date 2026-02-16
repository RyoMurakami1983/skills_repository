---
name: skills-generate-skill-suite
description: Generate multiple related skills as a coordinated suite. Use when splitting a domain into workflow skills.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, generator, suite, migration]
  invocable: false
---

# Generate a Skill Suite

End-to-end workflow for generating multiple related single-workflow skills as a coordinated suite, including a router skill, consistent naming, and cross-references. This is the replacement for legacy "multi-pattern skills."

Use Model Context Protocol (MCP) patterns when orchestrating multi-skill execution across tools.

## When to Use This Skill

Use this skill when:
- Breaking a domain into multiple single-workflow skills that form a family
- Generating a router skill plus its constituent workflow skills together
- Ensuring consistent naming, tags, and cross-references across a skill family
- Migrating a legacy multi-pattern skill into a suite of new workflow skills
- Planning a new domain that needs 3+ coordinated skills from the start

---

## Related Skills

- **`skills-author-skill`** — Generate and author a single skill (this skill generates multiple)
- **`skills-refactor-skill-to-single-workflow`** — Migration methodology for existing skills
- **`skills-author-skill`** — Fill each generated skeleton with content
- **`skills-validate-skill`** — Validate each skill in the suite

---

## Core Principles

1. **Suite = Coordinated Family** — A suite is a set of skills with consistent naming, shared context prefix, and explicit cross-references (基礎と型)
2. **Router as Entry Point** — Every suite has a router skill that helps users find the right workflow (ニュートラル)
3. **Independent but Related** — Each skill in the suite must be self-contained; the suite adds discoverability, not dependency (成長の複利)
4. **Generate Together, Fill Separately** — Generate all skeletons at once for consistency; fill each one individually (継続は力)

---

## Workflow: Generate a Skill Suite

### Step 1 — Define the Suite

Plan the family of skills:

```markdown
## Suite Plan: skills-system

Context prefix: skills-
Router: (optional) suite-index router if your domain requires it

Workflow Skills:
1. skills-author-skill — Write a new skill end-to-end
2. skills-validate-skill — Run quality validation
3. skills-validate-skill — Validate and remediate issues
4. skills-author-skill — Generate/author each skeleton
5. skills-revise-skill — Improve naming/discoverability after publication
```

**Suite rules**:
- All skills share the same context prefix (e.g., `skills-`)
- Each skill has a unique, verb-led workflow name
- The router lists all skills in a decision table

### Step 2 — Generate All Skeletons

For each skill in the suite, generate the initial skeleton using `skills-author-skill` Step 2:

```bash
# Generate each skill
for skill in skills-author-skill skills-validate-skill skills-revise-skill; do
  python scripts/generate_template.py --name "$skill" --tags "copilot,agent-skills"
done
```

Or generate manually by copying the section-order template from `skills-author-skill`.

### Step 3 — Generate the Router Skill

Create (or convert) a router skill that links all suite members. Use imperative routing language so intent selection is explicit.

```markdown
## Related Skills (Suite Members)

| Your Intent | Use This Skill | Why |
|-------------|---------------|-----|
| Write a new skill | skills-author-skill | Provides skeleton + authoring workflow |
| Validate a skill | skills-validate-skill | Provides scoring and report generation |
| Fix validation issues | skills-validate-skill | Includes integrated remediation loop |
| Generate a template | skills-author-skill | Includes integrated skeleton step |
| Improve discoverability | skills-revise-skill | Handles metadata and trigger optimization |
```

### Step 4 — Add Cross-References

Ensure each skill's "Related Skills" section references other suite members:

```markdown
## Related Skills

- **`skills-validate-skill`** — Validate after authoring
- **`skills-author-skill`** — Generate skeleton before authoring
```

### Step 5 — Verify Consistency

Check that all suite members:
- [ ] Share the same context prefix
- [ ] Have consistent tag sets (shared base + unique tags)
- [ ] Cross-reference each other in Related Skills
- [ ] Follow the same structure template
- [ ] Include `author: RyoMurakami1983`

### Step 6 — Fill and Validate Each Skill

Use `skills-author-skill` to fill each skeleton, then `skills-validate-skill` to validate.

---

## Good Practices

### 1. Plan the Suite Before Generating

**What**: Write a suite plan (context, skills, router) before generating any files.

**Why**: Planning avoids naming conflicts, missing workflows, and inconsistent cross-references.

**Values**: 基礎と型（設計してから実装）

### 2. Generate All Skeletons at Once

**What**: Create all suite directories and files in one pass.

**Why**: Ensures consistent structure, naming, and cross-references from the start.

**Values**: 基礎と型（型があるから速く動ける）

### 3. Keep Suites Small (3–7 Skills)

**What**: A suite should have 3–7 workflow skills plus a router.

**Why**: Too few (1–2) doesn't justify a suite; too many (8+) becomes hard to navigate.

**Values**: ニュートラル（誰もが使える普遍性）

---

## Common Pitfalls

### 1. Inconsistent Naming Across Suite

**Problem**: `skills-author-skill`, `skill-validate-quality`, `quality-check` — mixed prefixes and styles.

**Solution**: All suite members share the same context prefix and follow `<context>-<verb>-<object>`.

### 2. Missing Cross-References

**Problem**: Suite skills don't reference each other; users can't discover related workflows.

**Solution**: Every skill's "Related Skills" section includes at least 2 suite siblings.

### 3. Creating Suite Without Router

**Problem**: Multiple related skills exist but no entry point to help users choose.

**Solution**: Always create a router skill as the suite's table of contents.

---

## Quick Reference

### Suite Generation Checklist

- [ ] Suite plan documented (context, skills, router)
- [ ] All skeletons generated with consistent naming
- [ ] Router skill created with decision table
- [ ] Cross-references added to all suite members
- [ ] Consistency verified (prefix, tags, author, structure)
- [ ] Each skill filled with content
- [ ] Each skill validated with `skills-validate-skill`

### Suite Size Guide

| Size | Skills | Complexity | Example |
|------|--------|-----------|---------|
| Small | 3–4 | Single concern | `git-*` basic operations |
| Medium | 5–6 | Related domain | `skills-*` system |
| Large | 7+ | Broad domain | `dotnet-*` architecture |

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — Single skill generation and authoring
- [skills-refactor-skill-to-single-workflow](../skills-refactor-skill-to-single-workflow/SKILL.md) — Migration guide
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values

---
