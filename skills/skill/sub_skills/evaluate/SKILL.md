---
name: evaluate
description: >
  Evaluate whether a skill changes agent behavior by running with-skill versus
  baseline cases, aggregating results, and deciding the next action. Use when
  trigger quality, output quality, or regression risk must be measured.
compatibility: `_eval/agents/`, `_eval/scripts/`, `_eval/schemas/`
---

# Evaluate a Skill

Use this sub-skill when you need evidence about behavioral impact, not only confidence from static review.

## When to Use This Skill

Use this skill when:
- Designing realistic should-trigger and near-miss eval cases
- Comparing with-skill versus baseline behavior on the same prompts
- Generating benchmark summaries and reviewer-friendly HTML output
- Deciding whether to accept, revise, or expand eval coverage

## Workflow: Evaluate a Skill

### Step 1 — Design Good Cases

Create should-trigger and should-not-trigger cases that look like real user requests. Near-miss cases are critical because they reveal false positives better than obviously unrelated prompts.

### Step 2 — Run Both Modes

Use `_eval/agents/runner.md` to execute each case with the skill injected and without it. Matching conditions is what makes the comparison trustworthy.

### Step 3 — Aggregate the Results

Use `uv run python skills\skill\_eval\scripts\aggregate_benchmark.py --skill-id <skill-id> --run-id <run-id>` to compute pass rates and summary deltas. Aggregation makes patterns visible that single-case wins or losses can hide.

### Step 4 — Generate a Review Artifact

Use `uv run python skills\skill\_eval\scripts\generate_viewer.py --skill-id <skill-id>` with `assets/eval_review.html` so humans can inspect the outcome quickly. Fast review matters when you are iterating.

### Step 5 — Decide the Next Action

Accept when the skill clearly helps, revise when it hurts, add cases when evidence is thin, and escalate only when the regression is severe or high-risk.

## Pitfalls

- **Testing only happy paths**: without near-miss cases you cannot judge trigger precision.
- **Changing prompts between modes**: the comparison loses meaning immediately.
- **Treating one good run as proof**: consistent evidence matters more than anecdotal wins.
