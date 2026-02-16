---
name: skills-generate-skill-template
description: Generate a single-workflow skill skeleton with bilingual support. Use when starting a new skill.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, generator, scaffolding]
  invocable: false
---

# Generate a Skill Template

End-to-end workflow for generating a complete single-workflow skill skeleton (SKILL.md + references/SKILL.ja.md + directory structure) that passes basic structure validation out of the box.

## When to Use This Skill

Use this skill when:
- Starting a new skill and wanting a ready-to-fill skeleton
- Generating correct directory structure with all required files
- Creating bilingual skill boilerplate (English + Japanese)
- Ensuring the generated skeleton follows the "1 skill = 1 workflow" standard
- Setting up a skill that already includes proper YAML frontmatter and section ordering

---

## Related Skills

- **`skills-author-skill`** — Fill the template with actual content (use after generation)
- **`skills-validate-skill`** — Validate the filled skill
- **`skills-generate-skill-suite`** — Generate multiple related skills as a coordinated suite
- **`skills-optimize-skill-discoverability`** — Optimize name/description/tags

---

## Core Principles

1. **基礎と型（Foundation & Form）** — Generated templates embed the standard structure so authors start with a correct foundation
2. **成長の複利（Compound Growth）** — Scaffolding makes it easy to add content incrementally; the skeleton grows into a complete skill
3. **継続は力（Consistency is Strength）** — Bilingual generation (EN + JA) is the default, building the habit from day one
4. **ニュートラル（Neutrality）** — Templates use clear placeholders and guidance suitable for any domain

---

## Workflow: Generate a Skill Template

### Step 1 — Define Skill Metadata

Gather the required information:

```
Skill Name:    <context>-<verb>-<object>    (e.g., git-protect-main)
Description:   <what it does>. Use when <trigger>.  (≤ 100 chars)
Tags:          tag1, tag2, tag3             (3-5 technology tags)
Author:        RyoMurakami1983              (default)
```

### Step 2 — Choose Generation Method

**Option A: Manual (copy and fill)**
Copy the template structure from Step 3 below.

**Option B: Script (automated)**
```bash
# Using the generator script
python scripts/generate_template.py \
  --name "git-protect-main" \
  --description "Set up branch protection after git init. Use when starting new repos." \
  --tags "git,branch-protection,setup"
```

**Option C: AI-assisted**
Ask your AI agent: "Generate a new skill skeleton for `git-protect-main`"

### Step 3 — Template Structure

The generated skeleton creates this directory layout:

```
<skill-name>/
├── SKILL.md                    # English (primary)
└── references/
    └── SKILL.ja.md             # Japanese version
```

**Generated SKILL.md content**:

```markdown
---
name: <skill-name>
description: <description>. Use when <trigger>.
author: RyoMurakami1983
tags: [<tag1>, <tag2>, <tag3>]
invocable: false
---

# <Title Case Skill Name>

<Brief introduction: 1-2 sentences describing what this skill does.>

## When to Use This Skill

Use this skill when:
- <Scenario 1 — verb-led, 50-100 chars>
- <Scenario 2>
- <Scenario 3>
- <Scenario 4>
- <Scenario 5>

---

## Related Skills

- **`<related-skill-1>`** — <How it relates>
- **`<related-skill-2>`** — <How it relates>

---

## Core Principles

1. **<Principle 1>** — <Short explanation> (<Value名>)
2. **<Principle 2>** — <Short explanation> (<Value名>)
3. **<Principle 3>** — <Short explanation> (<Value名>)

---

## Workflow: <Workflow Name>

### Step 1 — <Action>

<Explanation>

### Step 2 — <Action>

<Explanation>

### Step 3 — <Action>

<Explanation>

---

## Good Practices

### 1. <Practice Title>

**What**: <Brief description>.
**Why**: <Rationale>.
**Values**: <Value名>

---

## Common Pitfalls

### 1. <Pitfall Title>

**Problem**: <What goes wrong>.
**Solution**: <How to fix>.

---

## Anti-Patterns

### <Anti-Pattern Name>

**What**: <Description>.
**Why It's Wrong**: <Reason>.
**Better Approach**: <Alternative>.

---

## Quick Reference

<Checklist, decision tree, or summary table>

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution
- [<Related resource>](<url>) — <Description>

---

## Changelog

### Version 1.0.0 (<today>)
- Initial release

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
```

### Step 4 — Generate Japanese Version

Create `references/SKILL.ja.md` with the same structure. The Japanese version adds deeper "Why" explanations.

Key differences in the Japanese template:
- "When to Use" items translated with context
- Core Principles include Japanese Value names naturally (not just appended)
- Workflow steps include "**Why**:" sections with philosophical rationale

### Step 5 — Fill Placeholders

Replace all `<placeholder>` text with actual content. Priority order:
1. YAML frontmatter (name, description, tags)
2. "When to Use" scenarios
3. Core Principles with Values
4. Workflow steps
5. Good Practices, Pitfalls, Anti-Patterns
6. Quick Reference

### Step 6 — Validate the Result

Run `skills-validate-skill` on the filled skill to confirm it passes.

---

## Good Practices

### 1. Generate Bilingual from the Start

**What**: Always create both SKILL.md and references/SKILL.ja.md together.

**Why**: Adding Japanese later is much harder than filling both templates simultaneously.

**Values**: 継続は力（最初から習慣にする）

### 2. Fill Immediately After Generation

**What**: Don't let a generated skeleton sit unfilled for more than one working session.

**Why**: Context about the skill's purpose fades; placeholders become permanent.

**Values**: 継続は力（「いつかやる」ではなく「今日やる」）

### 3. Validate Before Filling Content

**What**: Run validation on the empty skeleton to confirm structure is correct.

**Why**: Fixing structure after writing content is wasteful; validate the foundation first.

**Values**: 基礎と型（基礎が揺らいでいる上に応用を積んでも崩れる）

---

## Common Pitfalls

### 1. Leaving Placeholders

**Problem**: Generated skill is committed with `<placeholder>` text still present.

**Solution**: Search for `<` in the generated file; replace all before committing.

### 2. Generating with Wrong Naming Convention

**Problem**: Using `skill-my-thing` instead of `<context>-<workflow>`.

**Solution**: Check `skills-optimize-skill-discoverability` for naming rules before generating.

### 3. Forgetting Author Field

**Problem**: Generated skills omit `author: RyoMurakami1983`.

**Solution**: The template includes it by default; verify it's present in YAML frontmatter.

---

## Quick Reference

### Generation Workflow

```
1. Define metadata (name, description, tags)
2. Generate skeleton (manual/script/AI)
3. Validate empty skeleton (structure check)
4. Fill placeholders (priority order)
5. Create Japanese version
6. Validate filled skill
7. Commit
```

### Template Options

| Option | When to Use | Speed |
|--------|------------|-------|
| Manual copy | Learning the structure | Slow but educational |
| Script | Batch generation | Fast and consistent |
| AI-assisted | Quick prototype | Fastest |

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — How to fill the generated template
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Validate the result
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- Generator script: `../skill-template-generator/scripts/generate_template.py`
- Template assets: `../skill-template-generator/assets/`

---
