---
name: validate
description: >
  Validate a skill through Critical checks, recommended quality review,
  enterprise readiness, and behavioral evaluation routing. Use when checking a
  draft before merge, reviewing a rollout candidate, or deciding what blocks
  release.
compatibility: `_foundation/QUALITY.md`, `_eval/scripts/validate_skill.py`
---

# Validate a Skill

Use this sub-skill to run the smallest useful validation first, then escalate only when the rollout risk justifies it.

## When to Use This Skill

Use this skill when:
- Checking whether a new skill meets the minimum structural bar
- Reviewing an edited skill before publishing or merging
- Preparing a skill for team or organizational rollout
- Deciding whether behavior should be measured with evals

## Workflow: Validate a Skill

### Step 1 — Run L1 Critical Checks

Confirm the five Critical checks from `_foundation/QUALITY.md` all pass. In this repository, run the validator as `uv run python skills\skill\_eval\scripts\validate_skill.py <path-to-skill> --level L1`. This is the hard gate because a skill that cannot be discovered or executed correctly should not move forward.

### Step 2 — Review Recommended Quality Signals

Inspect the Recommended checks to find readability, reuse, and maintainability gaps. These do not block every draft, but they explain why a skill may still feel weak after passing L1.

### Step 3 — Escalate to L3 for Enterprise Use

If the skill is headed for team-wide use, review governance, security, ownership, and operational readiness. This keeps personal experimentation lightweight while protecting broader deployments.

### Step 4 — Route to L4 Only When Behavior Matters

If the question is not "is it well-formed?" but "does it actually improve outcomes?", hand off to `../evaluate/`. Static checks and behavioral checks answer different questions.

## Pitfalls

- **Treating Recommended checks as noise**: repeated weak signals often explain real adoption problems.
- **Skipping enterprise review for shared skills**: rollout risk changes the required level of scrutiny.
- **Using evals to replace structural validation**: behavior tests do not excuse broken metadata or missing workflow guidance.
