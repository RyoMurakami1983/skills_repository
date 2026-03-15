---
name: improve
description: >
  Improve an existing skill by trimming weak guidance, updating metadata,
  synchronizing related resources, and re-validating the result. Use when a
  published skill feels noisy, under-triggers, or needs coordinated revision.
compatibility: `_foundation/CONVENTIONS.md`, `_eval/scripts/validate_skill.py`
---

# Improve a Skill

Use this sub-skill to revise a skill with evidence, not by piling on new rules.

## When to Use This Skill

Use this skill when:
- Revising a published skill after feedback or failed evaluations
- Trimming wording that wastes context without changing behavior
- Updating metadata so the skill triggers more reliably
- Synchronizing references or Japanese guidance after substantial edits

## Workflow: Improve a Skill

### Step 1 — Classify the Change

Separate substantial behavior changes from trivial wording edits. This helps you decide whether to touch references, rerun validation, or leave the change as a small cleanup.

### Step 2 — Read the Evidence

Look at review comments, transcripts, validation output, and eval summaries. When the same helper or explanation keeps getting recreated, that is a strong signal to bundle it as a reusable resource.

### Step 3 — Revise for Generality

Rewrite the skill to explain why the guidance works, not just what to type. Prefer general patterns over test-case overfitting so the skill remains useful beyond the latest example.

### Step 4 — Synchronize Related Resources

Update `references/`, Japanese documentation, and bundled assets when the meaning changes. Skip heavy synchronization for trivial edits that do not change behavior.

### Step 5 — Re-validate

Run L1-L2 validation again after the revision with `uv run python skills\skill\_eval\scripts\validate_skill.py <path-to-skill> --level L2`. Improvement is not finished until the updated guidance still holds together structurally.

## Pitfalls

- **Adding more rules instead of better explanations**: the skill becomes rigid without becoming smarter.
- **Optimizing for one failing case**: overfitting reduces usefulness across real prompts.
- **Forgetting related resources**: stale references quietly undo the benefit of the edit.
