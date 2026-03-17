---
name: new
description: >
  Create a new skill or skill suite from requirements, conversation context,
  or an existing workflow. Use when drafting a new skill, converting a manual
  process into a skill, or generating multiple related skills at once.
compatibility: "_foundation/TEMPLATE.md, _eval/scripts/validate_skill.py"
---

# Create a New Skill

Use this sub-skill to turn an idea into a structured skill without carrying the full weight of the legacy authoring stack.

## When to Use This Skill

Use this skill when:
- Capturing a new workflow and turning it into a skill draft
- Researching constraints before writing a SKILL.md
- Generating a router plus several sibling skills as one suite
- Replacing ad-hoc prompts with a reusable skill package

## Workflow: Create a Skill

### Step 1 — Capture Intent

Define what the skill should do, when it should trigger, what output shape it should produce, and whether it needs reusable scripts or assets. This keeps the draft anchored to an actual workflow instead of a topic dump.

### Step 2 — Interview and Research

Ask about edge cases, dependencies, failure modes, and success criteria before drafting. If similar skills already exist, compare them so the new skill adds a missing pattern instead of duplicating one.

### Step 3 — Draft from the Template

Start from `_foundation/TEMPLATE.md`. Write a pushy `description`, keep the hot path short, and only add `compatibility` when a real runtime or tool constraint exists.

### Step 4 — Run L1 Validation

Use `uv run python skills/skill/_eval/scripts/validate_skill.py <path-to-skill>/SKILL.md --level L1` in draft mode to confirm the Critical checks pass early. Fix naming, trigger language, and missing workflow structure before polishing details.

### Step 5 — Batch When the Domain Needs a Suite

If the user is splitting one domain into several workflows, plan the suite first, generate all skeletons together, then fill them individually. This preserves naming and routing consistency.

### Step 6 — Choose the Right Pattern

Decide whether the domain is best modeled as a flat workflow, a peer-skill orchestrator, or a router with nested `sub_skills/`. Use a flat workflow when one ordered path is enough, an orchestrator when the skill mainly delegates to other top-level skills, and a router when one entry point must branch into distinct internal modes.

### Step 7 — Scaffold Router Structure When Needed

When the domain needs internal routing, scaffold it with `uv run python skills\skill\scripts\create_skill.py --name <router-name> --description "<description>" --type router --sub-skills <route-a>,<route-b>`. Keep the parent `SKILL.md` focused on the Decision Table and move the real execution logic into each generated sub-skill.

## Pitfalls

- **Writing before researching**: Missing constraints usually force major rewrites later.
- **Making the template verbose**: Keep essentials in `SKILL.md`; push details into `references/`.
- **Generating a suite without a shared naming plan**: Inconsistent names make routing brittle.
- **Using a router for one linear workflow**: Nested structure adds cost without helping discovery.
