---
name: skills-author-skill
description: Write a new SKILL.md from scratch following single-workflow best practices. Use when creating agent skills.
author: RyoMurakami1983
tags: [copilot, agent-skills, authoring, documentation]
invocable: false
---

# Author a New Agent Skill

End-to-end workflow for writing a high-quality SKILL.md that follows the "1 skill = 1 workflow" principle, passes quality validation, and integrates with the development constitution (PHILOSOPHY.md).

## When to Use This Skill

Use this skill when:
- Creating a brand-new SKILL.md for a GitHub Copilot / Claude / Codex agent
- Learning the required structure and sections for a single-workflow skill
- Writing clear "When to Use" scenarios and Core Principles
- Ensuring compliance with the 500-line limit and references/ overflow strategy
- Integrating development Values (基礎と型, 成長の複利, etc.) into a skill
- Setting up bilingual support (English SKILL.md + Japanese references/SKILL.ja.md)

---

## Related Skills

- **`skills-generate-skill-template`** — Generate a skeleton before writing content
- **`skills-validate-skill`** — Validate the finished skill against quality criteria
- **`skills-refactor-skill-to-single-workflow`** — Convert legacy multi-pattern skills
- **`skills-optimize-skill-discoverability`** — Improve name/description/tags after authoring

---

## Core Principles

1. **One Skill = One Workflow** — A skill documents exactly one end-to-end workflow, not a collection of topics (基礎と型)
2. **Reader-First Design** — Enable readers to determine relevance within 5 seconds (ニュートラル)
3. **Progressive Disclosure** — Keep SKILL.md ≤ 500 lines; move advanced details to `references/` (基礎と型)
4. **Explain WHY** — Comments and text explain rationale, transforming tacit knowledge into shared assets (成長の複利)
5. **Values Integration** — Every skill connects to PHILOSOPHY.md Values; Core Principles cite at least 2 Values (温故知新)

---

## Workflow: Author a New Skill

### Step 1 — Define Metadata (YAML Frontmatter)

Choose a name following the `<context>-<workflow>` convention (kebab-case, verb-led workflow, ≤ 64 chars).

```yaml
---
name: <context>-<verb>-<object>
description: <what it does>. Use when <activation scenario>. # ≤ 100 chars
author: RyoMurakami1983
tags: [tag1, tag2, tag3]   # 3-5 technology-focused tags
invocable: false
---
```

**Naming examples**:

| Context | Workflow | Full Name |
|---------|----------|-----------|
| `git` | `protect-main` | `git-protect-main` |
| `github` | `review-pr` | `github-review-pr` |
| `skills` | `author-skill` | `skills-author-skill` |
| `dotnet` | `apply-mvvm` | `dotnet-apply-mvvm` |

**Rules**:
- `name` must equal directory name
- `description` includes "Use when..." for agent activation
- `author: RyoMurakami1983` for skills created under this system

### Step 2 — Write "When to Use This Skill"

This must be the **first H2 section** after the title. Write 5–8 specific, action-oriented scenarios.

```markdown
## When to Use This Skill

Use this skill when:
- <Verb>-led scenario 1 (50-100 chars)
- <Verb>-led scenario 2
- ...
```

**Checklist**:
- ✅ Each item starts with a verb (Building, Implementing, Designing)
- ✅ Each item is 50–100 characters
- ❌ No abstract phrases ("When you want quality code")
- ❌ No more than 8 items

### Step 3 — Define Core Principles (3–5)

Connect each principle to at least one PHILOSOPHY Value.

```markdown
## Core Principles

1. **Principle Name** — Short explanation (Value名)
2. **Principle Name** — Short explanation (Value名)
3. **Principle Name** — Short explanation (Value名)
```

Available Values: 基礎と型 / 成長の複利 / 温故知新 / 継続は力 / ニュートラル

### Step 4 — Write the Single Workflow

Structure the workflow as sequential steps. Use a single `## Workflow:` section (not numbered `## Pattern N:` sections).

```markdown
## Workflow: <Workflow Name>

### Step 1 — <Action>
Explanation + example

### Step 2 — <Action>
Explanation + example

### Step 3 — <Action>
Explanation + example
```

**Code example conventions**:
- ✅ Use `// ✅ CORRECT - Reason` and `// ❌ WRONG - Reason` markers
- ✅ Include import/using statements
- ✅ Inline examples ≤ 15 lines; longer examples go to `references/`
- ✅ Comments explain WHY, not WHAT

### Step 5 — Add Good Practices & Pitfalls

```markdown
## Good Practices

### 1. Practice Title
**What**: Brief description.
**Why**: Rationale tied to a Value.
**Values**: Value名

## Common Pitfalls

### 1. Pitfall Title
**Problem**: What goes wrong.
**Solution**: How to fix it.
```

### Step 6 — Add Quick Reference & Resources

```markdown
## Quick Reference
[Checklist, decision tree, or summary table]

## Resources
- [Link 1](url) - Description
- [Link 2](url) - Description
```

### Step 7 — Manage File Size

If SKILL.md exceeds ~450 lines, proactively move content to `references/`:

```
my-skill/
├── SKILL.md                    # ≤ 500 lines (English, primary)
└── references/
    ├── SKILL.ja.md             # Japanese version
    ├── advanced-examples.md    # Detailed examples
    └── anti-patterns.md        # Extended anti-patterns
```

### Step 8 — Create Japanese Version

Create `references/SKILL.ja.md` with identical structure. The Japanese version may include deeper "Why" explanations.

### Step 9 — Validate

Run `skills-validate-skill` to check against quality criteria. Target ≥ 80% overall, ≥ 80% per category.

---

## Good Practices

### 1. Start with "When to Use" for Quick Discovery

**What**: Place "When to Use This Skill" as first H2 with 5–8 specific scenarios.

**Why**: Enables 5-second relevance check; improves AI agent discoverability.

**Values**: ニュートラル（形式知化で誰もが理解可能）

### 2. Use ✅/❌ Markers Consistently

**What**: Prefix code with `// ✅ CORRECT - Reason` or `// ❌ WRONG - Reason`.

**Why**: Eliminates ambiguity; enables contrast learning.

**Values**: 基礎と型（明確なパターン）/ 成長の複利（対比学習）

### 3. Explain WHY in Comments

**What**: Comments describe rationale, not syntax.

**Why**: Transforms 暗黙知 into 形式知; supports compound learning growth.

**Values**: 成長の複利（学習資産化）/ ニュートラル（形式知化）

### 4. Keep SKILL.md Under 500 Lines

**What**: Move advanced content to `references/` when approaching the limit.

**Why**: Maintains AI context efficiency; reduces cognitive load.

**Values**: 基礎と型（最小形式で最大可能性）

---

## Common Pitfalls

### 1. Stuffing Multiple Workflows into One Skill

**Problem**: Including 7–10 numbered `## Pattern N:` sections that are really separate workflows.

**Solution**: Each skill = one workflow. Split independent workflows into separate skills.

```markdown
❌ WRONG: One skill with Pattern 1: Setup, Pattern 2: Validate, Pattern 3: Deploy
✅ CORRECT: Three skills — setup-X, validate-X, deploy-X
```

### 2. Vague "When to Use" Scenarios

**Problem**: Abstract scenarios like "When you want better code quality".

**Solution**: Specific, verb-led: "Validating SKILL.md structure against 64-item checklist".

### 3. Missing Values Integration

**Problem**: Core Principles have no connection to PHILOSOPHY.md.

**Solution**: Each principle cites at least one Value in parentheses.

### 4. Exceeding 500-Line Limit

**Problem**: SKILL.md grows beyond 550 lines without using `references/`.

**Solution**: Move detailed examples, anti-patterns, and Japanese content to `references/`.

---

## Anti-Patterns

### Kitchen-Sink Skill

**What**: A single skill that tries to cover an entire domain (e.g., "everything about WPF").

**Why It's Wrong**: Exceeds line limits, impossible for agents to activate precisely, hard to maintain.

**Better Approach**: Split by workflow — one skill per independently executable task.

### Copy-Paste Without Adaptation

**What**: Generating a template and publishing without filling placeholders or adapting to context.

**Why It's Wrong**: Placeholders confuse agents; generic content provides no value.

**Better Approach**: Use `skills-generate-skill-template` for scaffolding, then fill every section with domain-specific content.

---

## Quick Reference

### Skill Authoring Checklist

- [ ] YAML frontmatter: name, description (with "Use when..."), author, tags
- [ ] `name` matches directory name, follows `<context>-<workflow>` convention
- [ ] "When to Use This Skill" is first H2 (5–8 verb-led scenarios)
- [ ] Core Principles (3–5) with ≥ 2 Values references
- [ ] Single workflow section with sequential steps
- [ ] Code examples use ✅/❌ markers, explain WHY
- [ ] Good Practices section with Values links
- [ ] Common Pitfalls (3–5 items)
- [ ] Anti-Patterns (2–3 items)
- [ ] Quick Reference (checklist or decision tree)
- [ ] Resources section
- [ ] SKILL.md ≤ 500 lines
- [ ] `references/SKILL.ja.md` exists (Japanese version)
- [ ] Validated with `skills-validate-skill`

### Section Order

```
1. YAML Frontmatter
2. # Title
3. Introduction (1-2 sentences)
4. ## When to Use This Skill
5. ## Related Skills
6. ## Core Principles
7. ## Workflow: <Name>
8. ## Good Practices
9. ## Common Pitfalls
10. ## Anti-Patterns
11. ## Quick Reference
12. ## Resources
13. ## Changelog
```

---

## Resources

- [GitHub Copilot Agent Skills Documentation](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Agent Skills Specification](https://agentskills.io/specification)
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Quality validation
- [skills-generate-skill-template](../skills-generate-skill-template/SKILL.md) — Template generation

---

## Changelog

### Version 1.0.0 (2026-02-13)
- Initial release: single-workflow authoring guide
- Migrated from legacy `skill-writing-guide` (multi-pattern style)
- Integrated "1 skill = 1 workflow" principle
- Added `<context>-<workflow>` naming convention
- Constitution Values integration throughout

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
