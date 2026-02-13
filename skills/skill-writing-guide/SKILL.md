---
name: skill-writing-guide
description: Router skill. Use when unsure which skill-authoring workflow to use.
author: RyoMurakami1983
tags: [copilot, agent-skills, router, writing]
invocable: false
---

# Skill Writing Guide (Router)

> **This is a router skill.** It guides you to the correct workflow skill. The original multi-pattern content has been migrated to focused single-workflow skills.

## When to Use This Skill

Use this skill when:
- You are not sure which skill-authoring workflow to use
- You want an overview of all available skill-writing workflows
- You are looking for the legacy "skill-writing-guide" content

---

## Related Skills (Migration Targets)

| Your Intent | Use This Skill | Description |
|-------------|---------------|-------------|
| Write a new SKILL.md from scratch | **[`skills-author-skill`](../skills-author-skill/SKILL.md)** | End-to-end authoring workflow |
| Convert a multi-pattern skill to single-workflow | **[`skills-refactor-skill-to-single-workflow`](../skills-refactor-skill-to-single-workflow/SKILL.md)** | Migration workflow |
| Improve name/description/tags for agent discovery | **[`skills-optimize-skill-discoverability`](../skills-optimize-skill-discoverability/SKILL.md)** | Discoverability optimization |
| Generate a skill template/skeleton | **[`skills-generate-skill-template`](../skills-generate-skill-template/SKILL.md)** | Template generation |
| Validate a skill against quality criteria | **[`skills-validate-skill`](../skills-validate-skill/SKILL.md)** | Quality validation |
| Revise an existing skill | **[`skill-revision-guide`](../skill-revision-guide/SKILL.md)** | Revision and changelog management |

---

## Core Principles

1. **One Skill = One Workflow** — Each skill documents exactly one end-to-end workflow (基礎と型)
2. **Router for Compatibility** — This skill exists to preserve backward compatibility during migration (継続は力)
3. **Values Integration** — All workflow skills connect to PHILOSOPHY.md Values (成長の複利)

---

## Workflow: Route to the Correct Skill

### Step 1 — Identify Your Intent

Ask yourself: "What am I trying to accomplish right now?"

### Step 2 — Match to a Workflow Skill

```
What do you need?
│
├─ Creating a brand new skill?
│  └─ → skills-author-skill
│
├─ Converting a legacy multi-pattern skill?
│  └─ → skills-refactor-skill-to-single-workflow
│
├─ Improving skill naming/tags/description?
│  └─ → skills-optimize-skill-discoverability
│
├─ Generating a skeleton/template?
│  └─ → skills-generate-skill-template
│
├─ Validating quality?
│  └─ → skills-validate-skill
│
└─ Updating an existing skill?
   └─ → skill-revision-guide
```

### Step 3 — Navigate

Click the link in the Related Skills table above, or invoke the skill by name.

---

## Migration Notice

This skill was migrated from a multi-pattern format (9 patterns, ~548 lines) to a router skill as part of the "1 skill = 1 workflow" migration. The original content is now distributed across:

- **`skills-author-skill`** — Patterns 1–8 consolidated into one authoring workflow
- **`skills-optimize-skill-discoverability`** — Naming and activation optimization
- **`skills-refactor-skill-to-single-workflow`** — Migration methodology itself

For the original reference materials, see `references/`.

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-author-skill](../skills-author-skill/SKILL.md) — Primary authoring workflow
- [Agent Skills Specification](https://agentskills.io/specification)

---

## Changelog

### Version 3.0.0 (2026-02-13)
- **Breaking**: Converted to router skill (single workflow)
- **Migrated**: 9 patterns → `skills-author-skill`, `skills-refactor-skill-to-single-workflow`, `skills-optimize-skill-discoverability`
- **Preserved**: Backward compatibility via routing table

### Version 2.1.0 (2026-02-13)
- Added Good Practices section with Values integration
- Enhanced Anti-Patterns section

### Version 2.0.0 (2026-02-12)
- Expanded Core Principles with Values integration

### Version 1.0.0 (2026-02-12)
- Initial release with 8 pattern sections

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
