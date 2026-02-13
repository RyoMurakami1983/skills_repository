---
name: skill-quality-validation
description: Router skill. Use when unsure which skill-validation workflow to use.
author: RyoMurakami1983
tags: [copilot, agent-skills, router, validation]
invocable: false
---

# Skill Quality Validation (Router)

> **This is a router skill.** It guides you to the correct validation workflow. The original multi-pattern content has been migrated to focused single-workflow skills.

## When to Use This Skill

Use this skill when:
- You are not sure which validation workflow to use
- You want an overview of all available quality validation workflows
- You are looking for the legacy "skill-quality-validation" content

---

## Related Skills (Migration Targets)

| Your Intent | Use This Skill | Description |
|-------------|---------------|-------------|
| Run a quality check on a SKILL.md | **[`skills-validate-skill`](../skills-validate-skill/SKILL.md)** | Full validation with scoring and report |
| Fix issues found in a quality report | **[`skills-remediate-validation-findings`](../skills-remediate-validation-findings/SKILL.md)** | Systematic remediation workflow |
| Write a new skill correctly | **[`skills-author-skill`](../skills-author-skill/SKILL.md)** | End-to-end authoring workflow |
| Revise an existing skill | **[`skill-revision-guide`](../skill-revision-guide/SKILL.md)** | Revision and changelog management |

---

## Core Principles

1. **One Skill = One Workflow** — Validation and remediation are separate workflows (基礎と型)
2. **Router for Compatibility** — This skill exists to preserve backward compatibility (継続は力)
3. **Scripts Remain Here** — Validation scripts (`.py`, `.ps1`, `.sh`) stay in this directory's `scripts/` folder (ニュートラル)

---

## Workflow: Route to the Correct Skill

### Step 1 — Identify Your Intent

```
What do you need?
│
├─ Run quality checks on a skill?
│  └─ → skills-validate-skill
│
├─ Fix validation failures?
│  └─ → skills-remediate-validation-findings
│
├─ Use automation scripts?
│  └─ → scripts/ in this directory:
│     ├─ validate_skill.py
│     ├─ validate_skill.ps1
│     └─ validate_skill.sh
│
└─ Learn how to write quality skills?
   └─ → skills-author-skill
```

### Step 2 — Navigate

Click the link in the Related Skills table above, or invoke the skill by name.

---

## Validation Scripts

The automation scripts remain in this directory for backward compatibility:

```bash
# Python
python scripts/validate_skill.py path/to/SKILL.md

# PowerShell
./scripts/validate_skill.ps1 -SkillPath path/to/SKILL.md

# Bash
./scripts/validate_skill.sh path/to/SKILL.md
```

> **Note**: These scripts are being updated to support the new "1 skill = 1 workflow" standard. See `skills-validate-skill` for the current checklist criteria.

---

## Migration Notice

This skill was migrated from a multi-pattern format (6 patterns, 64-item checklist, ~593 lines) to a router skill as part of the "1 skill = 1 workflow" migration. The original content is now distributed across:

- **`skills-validate-skill`** — Validation workflow with updated checklist
- **`skills-remediate-validation-findings`** — Remediation workflow

For the original reference materials, see `references/`.

---

## Resources

- [PHILOSOPHY.md](../../PHILOSOPHY.md) — Development constitution and Values
- [skills-validate-skill](../skills-validate-skill/SKILL.md) — Primary validation workflow
- [references/anti-patterns.md](references/anti-patterns.md) — Validation anti-patterns
- [references/validation-examples.md](references/validation-examples.md) — Validator implementations

---

## Changelog

### Version 4.0.0 (2026-02-13)
- **Breaking**: Converted to router skill (single workflow)
- **Migrated**: 6 patterns → `skills-validate-skill`, `skills-remediate-validation-findings`
- **Preserved**: Validation scripts in `scripts/` for backward compatibility

### Version 3.0.0 (2026-02-12)
- Expanded checklist: 56 → 64 items
- Added file length optimization and references/ validation

### Version 2.0.0 (2026-02-12)
- Optimized file length: 780 → 335 lines

### Version 1.0.0 (2026-02-12)
- Initial release with 56-item checklist

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
