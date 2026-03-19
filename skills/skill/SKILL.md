---
name: skill
description: >
  Unify skill authoring, improvement, validation, and evaluation behind one
  router. Use when creating a new skill, improving a published skill,
  validating quality, benchmarking trigger behavior, or generating a related
  skill suite, even if the user describes the workflow without saying
  "skill".
compatibility: GitHub Copilot Agent, Claude Code, Codex
---

# Skill Router

Use this router when the conversation is about making, fixing, checking, or measuring skills themselves.

## When to Use This Skill

Use this skill when:
- Creating a new skill from an idea, workflow, or requirements note
- Improving an existing skill after review feedback or observed friction
- Validating a skill's structure and content before wider rollout
- Evaluating whether a skill actually changes agent behavior
- Generating multiple related skills as a coordinated suite
- Refactoring old meta-skill workflows into the new unified structure

## Decision Table

| Your intent | Route | What to do |
| --- | --- | --- |
| Create a new skill | `sub_skills/new/` | Capture the intent, research constraints, scaffold, and validate the draft. |
| Improve an existing skill | `sub_skills/improve/` | Classify the change, trim weak guidance, update metadata, and re-validate. |
| Check skill quality | `sub_skills/validate/` | Run L1-L4 validation in order and report what blocks release. |
| Measure skill effectiveness | `sub_skills/evaluate/` | Design cases, run with-skill vs baseline, aggregate, and decide the next action. |
| Create a skill family | `sub_skills/new/` | Use batch mode and keep naming and cross-references consistent. |

## Shared Resources

- `_foundation/TEMPLATE.md` for the minimum hot-path template
- `_foundation/ROUTER_TEMPLATE.md` for parent router scaffolding
- `_foundation/SUB_SKILL_TEMPLATE.md` for nested sub-skill scaffolding
- `_foundation/QUALITY.md` for Critical and Recommended checks
- `_foundation/CONVENTIONS.md` for naming, frontmatter, and writing style
- `_eval/` for behavioral evaluation assets and validation scripts
- `scripts/` for reusable generators, packaging, and index maintenance

## Routing Notes

- Jump directly to the sub-skill that matches the user's current state.
- Adapt terminology to the user's literacy level; explain specialized terms when needed.
- In this repository, run Python helper scripts with `uv run python ...` rather than bare `python`.
- Keep execution logic in the sub-skill or script, not in this router.
