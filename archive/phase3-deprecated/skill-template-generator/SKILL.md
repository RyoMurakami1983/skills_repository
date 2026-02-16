---
name: skill-template-generator
description: Router skill. Use when unsure which template generation workflow to use.
metadata:
  author: RyoMurakami1983
  tags: [copilot, agent-skills, router, templates]
  invocable: false
---

# Skill Template Generator (Router)

> **This is a router skill.** It guides you to the correct generation workflow. The original multi-pattern content has been migrated to focused single-workflow skills.

## When to Use This Skill

Use this skill when:
- You are not sure which template generation workflow to use
- You want an overview of all available generation workflows
- You are looking for the legacy "skill-template-generator" content
- You need access to the generator script or template assets

---

## Related Skills (Migration Targets)

| Your Intent | Use This Skill | Description |
|-------------|---------------|-------------|
| Generate a single skill skeleton | **[`skills-generate-skill-template`](../skills-generate-skill-template/SKILL.md)** | Single-workflow template generation |
| Generate a family of related skills | **[`skills-generate-skill-suite`](../skills-generate-skill-suite/SKILL.md)** | Coordinated suite generation |
| Write content for a generated skeleton | **[`skills-author-skill`](../skills-author-skill/SKILL.md)** | End-to-end authoring workflow |
| Validate a generated skill | **[`skills-validate-skill`](../skills-validate-skill/SKILL.md)** | Quality validation |

---

## Core Principles

1. **One Skill = One Workflow** — Single skill generation and suite generation are separate workflows (基礎と型)
2. **Router for Compatibility** — This skill exists to preserve backward compatibility (継続は力)
3. **Assets Remain Here** — Template assets and generator scripts stay in this directory (ニュートラル)

---

## Workflow: Route to the Correct Skill

### Step 1 — Identify Your Intent

```
What do you need?
│
├─ Generate one new skill skeleton?
│  └─ → skills-generate-skill-template
│
├─ Generate a family of related skills?
│  └─ → skills-generate-skill-suite
│
├─ Use the Python generator script?
│  └─ → scripts/generate_template.py in this directory
│
├─ Reference the template files?
│  └─ → assets/ in this directory:
│     ├─ SKILL_TEMPLATE.md
│     └─ SKILL_TEMPLATE.ja.md
│
└─ Fill an already-generated skeleton?
   └─ → skills-author-skill
```

### Step 2 — Navigate

Click the link in the Related Skills table above, or invoke the skill by name.

---

## Scripts and Assets

These remain in this directory for backward compatibility:

### Generator Script

```bash
python scripts/generate_template.py \
  --name "git-protect-main" \
  --description "Set up branch protection after git init." \
  --tags "git,branch-protection,setup"
```

### Template Assets

- [`assets/SKILL_TEMPLATE.md`](assets/SKILL_TEMPLATE.md) — English template
- [`assets/SKILL_TEMPLATE.ja.md`](assets/SKILL_TEMPLATE.ja.md) — Japanese template

> **Note**: These templates are being updated to support the "1 skill = 1 workflow" structure. See `skills-generate-skill-template` for the current recommended template.

---

## Migration Notice

This skill was migrated from a multi-pattern format (7 patterns, ~1028 lines) to a router skill as part of the "1 skill = 1 workflow" migration. The original content is now distributed across:

- **`skills-generate-skill-template`** — Single skill generation workflow
- **`skills-generate-skill-suite`** — Suite generation workflow

For the original reference materials, see `references/`.

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-generate-skill-template](../skills-generate-skill-template/SKILL.md) — Primary generation workflow
- [assets/SKILL_TEMPLATE.md](assets/SKILL_TEMPLATE.md) — English template
- [assets/SKILL_TEMPLATE.ja.md](assets/SKILL_TEMPLATE.ja.md) — Japanese template

---
