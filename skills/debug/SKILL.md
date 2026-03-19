---
name: debug
description: >
  Reproduce failures, capture comparable evidence, isolate the owning
  boundary, verify the smallest safe fix, and hand off a reusable evidence
  package. Use when investigating regressions, comparing good vs bad behavior,
  or building a repeatable debug trail before and after a change.
---

# Debug with Reproducible Evidence

Use this skill to debug from proof instead of hunches.

The core workflow stays stable across domains. Domain modules under `modules/` start thin and should grow only from real debugging sessions, not speculation.

## When to Use This Skill

Use this skill when:
- Reproducing a failure before changing code
- Comparing known-good and failing behavior with the same stimulus
- Isolating which layer owns a regression or mismatch
- Verifying a fix with the same scenario, artifacts, and checks
- Handing off bug evidence to review, PR, or incident workflows

## Related Skills

- **`github-pr-workflow`** - Hand off validated fixes with clear evidence
- **`github-pr-review-response`** - Answer review comments with before/after proof
- **`knowledge-capture`** - Capture reusable lessons once the debug session is complete

## Core Principles

1. **Freeze the failing case first** - Debugging gets faster once the target is stable.
2. **Collect evidence before explanation** - Screenshots, logs, traces, and diffs beat guesses.
3. **Compare with the same stimulus** - A changed input weakens the comparison.
4. **Isolate the owning boundary** - Fix the layer that actually broke, not the nearest symptom.
5. **Prefer the smallest root-cause fix** - Small fixes are easier to verify and safer to keep.
6. **Leave a reusable trail** - A debug session should teach the next one.

## Preflight

- Write the observed behavior, expected behavior, and smallest reproducible stimulus.
- Decide which module to load from `modules/` for domain-specific evidence and boundaries.
- Choose a stable artifact location such as `debug/<session>/`.
- Confirm which environments, modes, inputs, or clocks must stay fixed.
- List the existing gates you must rerun after the fix.

## Module Decision Table

Use this table to choose the first module to load. Start with the best fit, then add `evidence-manifest.md` whenever the capture or comparison shape is still unclear.

| Symptom shape | Start here | Why |
|---|---|---|
| UI, rendering, editor, input, focus, or layout mismatch | `gui.md` | Visual and interaction evidence usually matters first |
| HTTP, auth, service, transaction, or cache mismatch | `api-backend.md` | Request and state boundaries usually own the defect |
| Data drift, schema break, join issue, null handling, or wrong aggregates | `data-etl.md` | Snapshot and distribution comparisons matter most |
| Correct result but bad latency, throughput, or memory behavior | `performance.md` | Measured bottlenecks matter more than functional diffs |
| Ordering, retry, race, state sync, or cross-worker timing issues | `distributed-concurrency.md` | Shared-ordering and coordination bugs need their own cut |
| Flaky AI output, seed variation, timing-dependent behavior, or retry noise when shared ordering/state sync is not the main culprit | `nondeterminism.md` | Time and control variables are usually the fastest way in |
| Pass or fail depends on unit, fixture, power, environment, time, location, nearby equipment, or spec compliance | `embedded-hardware.md` | Physical conditions and measurement quality may own the result |
| Unsure what to capture or how to compare before and after | `evidence-manifest.md` | Standardize the evidence package before going deeper |

## Workflow: Debug with Evidence

### Step 1 — Define the failure

Turn the report into one precise statement: what happened, what should have happened, where it happens, and how to trigger it with the smallest repeatable stimulus.

Use when the report is vague, mixed with guesses, or spread across several symptoms. Why: a stable target prevents wandering fixes and keeps later comparisons honest.

> **Values**: 基礎と型 / ニュートラル

### Step 2 — Capture a baseline evidence package

Before editing code, collect the artifacts that make the current behavior undeniable. The exact package depends on the module, but it should usually include the stimulus, the observed output, and the environment or mode.

Save the artifacts in one predictable place.

```text
debug/<session>/
  manifest.(md|json)
  before/
  after/
```

Use when you can reproduce the failure at least once. Why: debugging without a baseline makes it hard to prove what changed.

> **Values**: 継続は力 / 成長の複利

### Step 3 — Compare with the same stimulus

Run the same request, input sequence, dataset, workload, or hardware condition against both the failing and reference paths. Keep the stimulus fixed and change only one comparison axis at a time.

Use when you have a known-good path, environment, mode, or historical sample. Why: same-stimulus comparison is the fastest way to separate real differences from noise.

> **Values**: ニュートラル / 基礎と型

### Step 4 — Isolate the owning boundary

Use the selected module to cut the problem by boundaries such as input handling, validation, transactions, layout, cache, timing, concurrency, or sensor chain. Aim to identify the first boundary where reality diverges from expectation.

Use when the symptom is visible but the owner is unclear. Why: boundary-first debugging avoids broad changes and reveals the real root cause.

> **Values**: 温故知新 / 基礎と型

### Step 5 — Apply the smallest root-cause fix

Change the narrowest place that removes the divergence. Avoid piling on unrelated refactors or speculative guardrails unless the evidence shows they are required.

Use when the owning boundary is clear enough to act. Why: a small fix keeps validation tight and reduces new failure modes.

> **Values**: 基礎と型 / 余白の設計

### Step 6 — Re-run the same scenario and gates

Replay the same stimulus, rebuild the evidence package, and rerun the existing checks for the affected surface. End by handing off the root cause, changed files, commands, and artifact paths.

Use when the fix is in place. Why: the same scenario is what turns a code change into a verified repair.

> **Values**: 継続は力 / 成長の複利

## Modules

Treat the files under `modules/` as appendices, not alternate workflows. Start thin, then append only what a real debug session taught you.

| Module | Use when | Current state |
|---|---|---|
| `gui.md` | UI, rendering, editor, input, focus, or layout bugs | Active starting module |
| `api-backend.md` | HTTP, auth, service, transaction, or cache bugs | Thin starter |
| `data-etl.md` | Pipeline, schema, join, distribution, or null-handling bugs | Thin starter |
| `performance.md` | Latency, memory, throughput, or hot-path bugs | Thin starter |
| `distributed-concurrency.md` | Ordering, retry, race, sync, or eventual-consistency bugs | Thin starter |
| `embedded-hardware.md` | Sensors, waveforms, calibration, fixture, or environment bugs | Thin starter |
| `nondeterminism.md` | Cross-cutting time, seed, retry, or parallelism issues | Thin starter |
| `evidence-manifest.md` | Standardizing what to capture and how to compare it | Thin starter |

If the symptom is intermittent, do not assume hardware or software too early. Start with the module whose evidence shape best matches the first clues, then widen only after the first comparison.

## Pitfalls

- **Changing code before taking a baseline**: You lose the strongest before/after proof.
- **Changing the stimulus between runs**: The comparison becomes weaker than it looks.
- **Fixing the symptom instead of the boundary**: The bug often returns in the next scenario.
- **Stuffing domain detail into the core skill**: The hot path becomes noisy and harder to reuse.

## Anti-Patterns

- **Exploratory fix with no evidence package**: Edit first and hope the result explains itself later.
- **One-mode success equals done**: Stop after one happy path without checking the affected modes or environments.
- **Speculative module growth**: Add long domain sections before a real session proves they help.

## Troubleshooting

- **The bug is not reproducible locally**: Capture environment differences, feature flags, and timing assumptions before changing code.
- **The evidence is noisy**: Narrow the stimulus, fix clocks or seeds if possible, and collect fewer but higher-signal artifacts.
- **Several boundaries look suspicious**: Compare one boundary at a time and record where the first divergence appears.

## Self-Review

- Can I point to one stable failing scenario?
- Did I keep the stimulus the same before and after the fix?
- Did I capture artifacts that another person could inspect later?
- Did I name the owning boundary instead of only the symptom?
- Did I rerun the relevant gates and hand off the evidence paths?

## Quick Reference

1. Define the failure.
2. Capture baseline evidence.
3. Compare with the same stimulus.
4. Isolate the owning boundary.
5. Apply the smallest fix.
6. Re-run the same scenario and gates.
7. Hand off root cause, changes, commands, and artifact paths.
