---
name: skills-optimize-skill-discoverability
description: Improve skill name, description, and tags for better agent activation. Use when skills are not being found.
author: RyoMurakami1983
tags: [copilot, agent-skills, discoverability, naming]
invocable: false
---

# Optimize Skill Discoverability

End-to-end workflow for improving a skill's name, description, tags, and "When to Use" section so that AI agents (Copilot, Claude, Codex) reliably find and activate it.

## When to Use This Skill

Use this skill when:
- An existing skill is not being activated by agents despite being relevant
- Choosing a name for a new skill and wanting maximum discoverability
- Reviewing description length, tag coverage, and activation keywords
- Standardizing naming across a skill family (e.g., all `git-*` skills)
- Auditing the entire repository for naming consistency and gaps

---

## Related Skills

- **`skills-author-skill`** — Write a new skill (includes naming step)
- **`skills-validate-skill`** — Validate skill quality including structure checks
- **`skills-refactor-skill-to-single-workflow`** — Refactor legacy skills (may need renaming)

---

## Core Principles

1. **Name = Intent** — The skill name should immediately convey what workflow it performs (基礎と型)
2. **Description = Activation** — The description is the primary signal agents use for matching; include "Use when..." (ニュートラル)
3. **Tags = Discovery Surface** — Tags expand the search surface beyond the name and description (成長の複利)
4. **Consistency = Trust** — Consistent naming across skill families builds predictability (継続は力)

---

## Workflow: Optimize Discoverability

### Step 1 — Audit Current Metadata

Extract and review the current frontmatter:

```yaml
# Current state
name: skill-writing-guide                    # ❌ Generic, no context prefix
description: Guide for writing high-quality GitHub Copilot agent skills.  # ❌ No "Use when..."
tags: [copilot, agent-skills, documentation, writing-guide]
```

**Check against rules**:

| Field | Rule | Pass? |
|-------|------|-------|
| name | `<context>-<workflow>`, verb-led, kebab-case, ≤ 64 chars | ❌ |
| description | ≤ 100 chars, includes "Use when...", problem-focused | ❌ |
| tags | 3–5 tags, technology-focused, no duplicates of name words | ⚠️ |

### Step 2 — Apply Naming Convention

Transform the name to `<context>-<workflow>` format:

```
❌ skill-writing-guide          → Generic, "skill-" prefix is noise
❌ writing-guide                → No context, no verb
✅ skills-author-skill          → Context: skills, Workflow: author-skill (verb-led)
```

**Naming rules**:
- **Context**: bounded domain (`skills`, `git`, `github`, `dotnet`, `python`, `tdd`)
- **Workflow**: verb-led imperative (`author-skill`, `validate-structure`, `protect-main`)
- **Length**: ≤ 5 tokens, ≤ 64 characters
- **No generic verbs alone**: `do`, `fix`, `handle` → pair with object

### Step 3 — Optimize Description

Rewrite the description to include activation context:

```yaml
# Before
description: Guide for writing high-quality GitHub Copilot agent skills.

# After (≤ 100 chars, includes "Use when...")
description: Write a new SKILL.md following single-workflow best practices. Use when creating agent skills.
```

**Description formula**: `<What it does>. Use when <specific trigger>.`

### Step 4 — Optimize Tags

Tags should complement (not duplicate) the name:

```yaml
# Before - duplicates name words
tags: [copilot, agent-skills, documentation, writing-guide]

# After - adds discovery surface
tags: [copilot, agent-skills, authoring, documentation]
```

**Tag rules**:
- 3–5 tags
- Technology-focused (not generic like "best-practices")
- Don't repeat words already in the name
- Include the ecosystem tag (`copilot`, `claude`, `codex`)

### Step 5 — Optimize "When to Use" Section

Ensure scenarios use activation-friendly language:

```markdown
# Before - vague
- Learning required structure and sections
- Understanding code example best practices

# After - specific, verb-led
- Creating a brand-new SKILL.md for a GitHub Copilot agent
- Writing clear "When to Use" scenarios and Core Principles
```

### Step 6 — Validate Activation

Test that agents can find the skill:
1. Use a query that should trigger the skill
2. Check if the agent activates it
3. If not, refine description and "When to Use" keywords

---

## Good Practices

### 1. Front-Load the Verb in Names

**What**: Start the workflow portion with an action verb.

**Why**: Agents match on intent; verbs signal actionability.

**Values**: 基礎と型（型があるから速く動ける）

### 2. Include "Use when..." in Every Description

**What**: Always end the description with a "Use when..." clause.

**Why**: This is the primary activation signal for AI agents.

**Values**: ニュートラル（誰もが理解可能な形式知）

### 3. Keep Names Short and Specific

**What**: ≤ 5 tokens, ≤ 64 characters. Prefer specificity over completeness.

**Why**: Long names are harder to match and remember.

**Values**: 基礎と型（最小形式で最大可能性）

---

## Common Pitfalls

### 1. Using "skill-" as a Prefix

**Problem**: Every skill starts with "skill-", adding noise without information.

**Solution**: Use the bounded context as prefix (`git-`, `skills-`, `dotnet-`).

### 2. Description Without Activation Context

**Problem**: "A comprehensive guide for..." — no "Use when..." clause.

**Solution**: Always include "Use when <specific scenario>." in the description.

### 3. Too Many or Too Generic Tags

**Problem**: `tags: [best-practices, guide, documentation, help, useful]`.

**Solution**: 3–5 technology-specific tags: `[copilot, agent-skills, authoring]`.

---

## Quick Reference

### Discoverability Checklist

- [ ] Name follows `<context>-<workflow>` (verb-led, kebab-case, ≤ 64 chars)
- [ ] Description ≤ 100 chars with "Use when..." clause
- [ ] 3–5 technology-focused tags (no name duplication)
- [ ] "When to Use" has 5–8 specific, verb-led scenarios
- [ ] Related Skills section links to family members
- [ ] Name matches directory name exactly

### Naming Quick Reference

| Context | Example Workflows |
|---------|------------------|
| `skills` | `author-skill`, `validate-skill`, `generate-skill-template` |
| `git` | `protect-main`, `commit-practices`, `setup-hooks` |
| `github` | `review-pr`, `create-pr`, `manage-issues` |
| `dotnet` | `apply-mvvm`, `configure-di`, `setup-testing` |
| `python` | `create-cli`, `setup-venv`, `write-tests` |
| `tdd` | `standard-practice`, `write-test-list` |

---

## Resources

- [skills-author-skill](../skills-author-skill/SKILL.md) — Naming is part of Step 1
- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution
- [Agent Skills Specification](https://agentskills.io/specification) — Official metadata rules

---

## Changelog

### Version 1.0.0 (2026-02-13)
- Initial release: discoverability optimization workflow
- Naming convention reference (`<context>-<workflow>`)
- Description, tags, and "When to Use" optimization steps

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
