---
name: skills-eval-pipeline
description: "Use when you need to evaluate a skill's effectiveness by running test cases with and without skill injection, comparing results, and generating a visual benchmark report."
---

# Skills Eval Pipeline

An orchestrated evaluation pipeline that measures whether a SKILL.md improves agent output quality. Runs test cases with and without skill injection, grades responses, aggregates statistics, and generates a visual HTML report.

## When to Use This Skill

Use this skill when:
- Measuring whether a SKILL.md actually improves agent responses on real prompts
- Comparing "with skill" vs "baseline" (no skill) performance quantitatively
- Validating a modified skill with benchmark evidence before merging to main
- Identifying which test cases fail and diagnosing why the skill underperforms
- Building a test suite (`evals.json`) for a skill that has no eval coverage yet
- Generating a visual HTML report to share benchmark results with stakeholders

> **Scope**: Covers test case design → execution → grading → aggregation → visualization → feedback loop. Phase 4.2 (Tauri/WPF native GUI) is out of scope for this version.

## Related Skills

- **`skills-author-skill`** — Create the skill under test
- **`skills-validate-skill`** — Static validation (run before eval pipeline)
- **`skills-revise-skill`** — Apply feedback from `feedback.json` to improve the skill
- **`skill-quality-validation`** — validate_skill.py static checks (complement to eval)

---

## Dependencies

- Python 3.10+
- `uv` (or `pip`) for running scripts
- No external API calls required — agent responses are handled by `task tool` sub-agents

---

## Core Principles

1. **Schema First** (基礎と型) — All data contracts defined in `references/schemas.md` before implementation
2. **Parallel Execution** (継続は力) — with_skill and baseline run simultaneously to reduce latency
3. **Human-in-the-Loop** (余白の設計) — Pipeline produces data; humans decide whether to accept or revise
4. **Composable** (成長の複利) — Each agent (runner/grader/analyzer) is independently reusable
5. **Fail Gracefully** (温故知新) — Case-level errors don't abort the full run; only setup errors stop execution

---

## Decision Table

Use this to jump directly to the right step based on current state.

| Current state | Next step |
|---------------|-----------|
| No `evals.json` yet | Step 1: Design test cases |
| `evals.json` exists, no `runs/` | Step 2: Run evaluations |
| `runs/` exists, no `benchmark_summary.json` | Step 3: Aggregate results |
| `benchmark_summary.json` exists, no viewer | Step 4: Generate HTML (HyperText Markup Language) viewer |
| Viewer generated, no `feedback.json` | Step 5: Analyze and generate feedback |
| `feedback.json` exists | Step 6: Act on feedback |

---

## Directory Structure

```
skills/skills-eval-pipeline/
├── SKILL.md                    # This file — orchestrator
├── agents/
│   ├── runner.md               # Spawns sub-agents for with_skill + baseline
│   ├── grader.md               # Scores one response against assertions
│   └── analyzer.md             # Generates feedback.json from benchmark results
├── scripts/
│   ├── aggregate_benchmark.py  # Aggregates grading results → benchmark_summary.json
│   └── generate_viewer.py      # Renders benchmark_summary.json → HTML viewer
├── viewer/
│   └── index.html              # HTML viewer template (self-contained)
└── references/
    ├── schemas.md              # JSON contracts for all data files
    └── SKILL.ja.md             # Japanese version
```

---

## Workflow: Evaluate a Skill

### Step 1: Design Test Cases

Create `evals/<skill_id>/evals.json` with at least 3 test cases.

**Assertion types** (from `references/schemas.md`):

| Type | When to use |
|------|-------------|
| `contains` | Structural checks — must-have strings in output |
| `not_contains` | Negative checks — output must NOT contain |
| `llm_grade` | Semantic checks — rubric-based quality judgment |
| `regex` | Pattern matching for IDs, formats, etc. |

**Minimum viable test suite**:
1. **Happy path** — standard use case; verify key structural elements appear
2. **Edge case** — ambiguous input; verify graceful handling
3. **Anti-pattern** — input that should NOT trigger the skill; verify non-regression

```json
{
  "skill_id": "skills-author-skill",
  "version": "1.0.0",
  "description": "新規スキル作成フローの基本テスト",
  "cases": [
    {
      "id": "tc-001",
      "prompt": "バックアップスクリプトを自動化するスキルを作って",
      "assertions": [
        { "type": "contains", "value": "name:", "weight": 1.0 },
        { "type": "contains", "value": "description:", "weight": 1.0 },
        { "type": "contains", "value": "When to Use", "weight": 0.8 },
        { "type": "llm_grade", "value": "フロントマターが正しい形式で、When to Use セクションが明確か", "weight": 1.0 }
      ],
      "tags": ["happy-path"]
    }
  ]
}
```

Use when starting a new evaluation. Why: test cases are the ground truth — define them before running.

> **Values**: 基礎と型

### Step 2: Run Evaluations

Invoke `agents/runner.md` via `task tool` sub-agent, passing:
- `skill_id` — directory name of the skill under test
- `evals_path` — path to `evals.json`
- `run_id` — unique identifier (e.g., `run-YYYYMMDD-NNN`)

The runner will spawn **two parallel sub-agents per test case**:

```
For each case:
  ├── task(with_skill): prompt + SKILL.md content → response → grader
  └── task(baseline):   prompt only              → response → grader
```

Each sub-agent passes its response to `agents/grader.md`, which returns a `grading_result.json`.

Results are written to `evals/<skill_id>/runs/`.

Use when test cases are ready. Why: parallel execution gives comparable results with minimum latency.

> **Values**: 継続は力

### Step 3: Aggregate Results

Run the aggregation script to compute statistics across all runs:

```bash
# Bash / macOS / Linux
python skills/skills-eval-pipeline/scripts/aggregate_benchmark.py \
  --skill-id skills-author-skill \
  --run-id run-20260310-001
```

```powershell
# PowerShell (Windows)
python skills\skills-eval-pipeline\scripts\aggregate_benchmark.py `
  --skill-id skills-author-skill `
  --run-id run-20260310-001
```

Output: `evals/<skill_id>/benchmark_summary.json`

| Field | Meaning |
|-------|---------|
| `verdict` | `improved` / `neutral` / `degraded` |
| `delta` | `with_skill.mean - baseline.mean` |
| `improvement_pct` | `delta / baseline.mean × 100` |

Use when all run results are collected. Why: aggregation makes patterns visible that individual case scores hide.

> **Values**: 温故知新

### Step 4: Generate HTML Viewer

```bash
# Bash / macOS / Linux
python skills/skills-eval-pipeline/scripts/generate_viewer.py \
  --skill-id skills-author-skill
```

```powershell
# PowerShell (Windows)
python skills\skills-eval-pipeline\scripts\generate_viewer.py `
  --skill-id skills-author-skill
```

Output: `evals/<skill_id>/viewer.html` — open in any browser, no server required.

The viewer shows:
- Verdict badge (✅ Improved / ⚠️ Neutral / ❌ Degraded)
- with_skill vs baseline means + delta
- Per-case breakdown table

Use when benchmark_summary.json is ready. Why: visual summary enables quick human judgment.

> **Values**: 余白の設計

### Step 5: Analyze and Generate Feedback

Invoke `agents/analyzer.md` via `task tool` sub-agent, passing:
- `benchmark_summary.json` path
- `evals.json` path (for assertion context)
- Optional: raw `grading_result.json` files for deep analysis

Output: `evals/<skill_id>/feedback.json` — KPT-classified improvement items.

| `next_action` | Meaning |
|---------------|---------|
| `accept` | delta > 0.1, no degraded cases — skill is effective |
| `revise_skill` | Regression or problems found — hand off to `skills-revise-skill` |
| `add_cases` | Neutral verdict — need more test cases |
| `escalate` | Severe regression (delta < -0.2) — manual review required |

Use when benchmark results are available. Why: structured feedback guides the next iteration.

> **Values**: 余白の設計 / 成長の複利

### Step 6: Act on Feedback

| `next_action` | Next step |
|---------------|-----------|
| `accept` | Commit `evals/` directory, PR with benchmark evidence |
| `revise_skill` | Invoke `skills-revise-skill` with `feedback.json` items as input |
| `add_cases` | Return to Step 1 and add edge cases |
| `escalate` | Review runner/grader output manually; check for prompt injection |

✅ **Good**: Let `feedback.json` drive revisions — don't edit the skill based on intuition alone.
❌ **Bad**: Run the eval once, get "neutral", and call it done without adding more cases.
Why: one run with 3 cases is signal, not proof. The pipeline is a loop, not a one-shot.

> **Values**: 継続は力

---

## Anti-Patterns

### Architecture-Level

- **Merging runner + grader into one agent** — Runner spawns sub-agents and collects raw responses; Grader scores against assertions. Combining them makes scoring non-reusable and debugging impossible. Keep them separate.

- **Skipping schemas.md and inventing ad-hoc JSON** — All data flows through contracts defined in `references/schemas.md`. Diverging from the schema breaks `aggregate_benchmark.py` and the viewer silently.

- **Using eval pipeline as a substitute for static validation** — Run `skills-validate-skill` (structural + language checks) before `skills-eval-pipeline` (behavioral checks). Eval doesn't catch frontmatter errors.

- **One-shot eval without iteration** — The pipeline is designed as a loop: run → analyze → revise → re-run. Treating a single run as final defeats the purpose of the feedback loop.

---

## Best Practices

- Write at least one `llm_grade` assertion per test case for semantic coverage
- Use `run_id` with a date stamp (e.g., `run-20260310-001`) for traceability
- Commit `evals/<skill_id>/evals.json` to track test history; `.gitignore` the `runs/` directory
- Run `skills-validate-skill` before `skills-eval-pipeline` — static issues should be fixed first
- Add new test cases when you discover unexpected behaviors, not just after regressions

---

## Common Pitfalls

1. **No baseline divergence**: Skill and baseline produce identical outputs → assertions don't differentiate.
   Fix: Add more specific `llm_grade` rubrics tied to skill-specific behaviors.

2. **Grader gaming**: Overly simple `contains` assertions (e.g., `contains: "the"`) pass for any response.
   Fix: Use skill-specific structural markers that only appear in well-formed outputs.

3. **Single run conclusions**: One run is insufficient for variable LLM (Large Language Model) outputs.
   Fix: Run 3+ times and check mean/stddev before concluding. Single-run verdict is signal, not proof.

4. **Evals directory not committed**: Losing test cases breaks reproducibility.
   Fix: Commit `evals/<skill_id>/evals.json`; add `runs/` and `viewer.html` to `.gitignore`.

---

## Preflight Checklist

- [ ] SKILL.md for the target skill exists at `skills/<skill_id>/SKILL.md`
- [ ] `evals/<skill_id>/evals.json` is valid JSON with ≥3 test cases
- [ ] Each test case has ≥1 `llm_grade` assertion
- [ ] `skills-validate-skill` has passed on the target skill
- [ ] Python 3.10+ available (`python --version`)

---

## Quick Reference

```
Step 1: Design evals.json (≥3 cases, include llm_grade)
Step 2: runner.md → parallel with_skill + baseline runs
Step 3: aggregate_benchmark.py → benchmark_summary.json
Step 4: generate_viewer.py → viewer.html (open in browser)
Step 5: analyzer.md → feedback.json (KPT + next_action)
Step 6: Act on next_action (accept / revise / add cases)
```

---

## Resources

- `references/schemas.md` — JSON contracts for all data files
- `agents/runner.md` — Execution protocol for with_skill + baseline runs
- `agents/grader.md` — Assertion evaluation + scoring formula
- `agents/analyzer.md` — KPT feedback generation from benchmark data
