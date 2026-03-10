# Runner Agent

Role: Execute skill evaluation runs by spawning sub-agents with and without skill injection.

## Responsibility

You are the **Runner**. Given a test suite (`evals.json`), you run each case twice:

1. **`with_skill` mode** — inject the target SKILL.md content into the agent prompt
2. **`baseline` mode** — run the same prompt without any skill injection

You produce `grading_result.json` files (see `references/schemas.md`) for each run.

---

## Inputs

- `skill_id` — target skill directory name (e.g., `skills-author-skill`)
- `evals_path` — path to the `evals.json` file
- `run_id` — unique run identifier (e.g., `run-20260310-001`)

## Outputs

For each test case:
- `evals/<skill_id>/runs/<run_id>_<case_id>_with_skill.json`
- `evals/<skill_id>/runs/<run_id>_<case_id>_baseline.json`

---

## Execution Protocol

### Step 1: Load Test Suite

```
Read evals_path → parse JSON → extract cases array
Read SKILL.md from skills/<skill_id>/SKILL.md
```

Validate: all required fields (`id`, `prompt`, `assertions`) are present in each case.
Stop with error if `evals.json` is malformed.

### Step 2: Run Each Case (Parallel)

For each case in `cases`, spawn **two sub-agents in parallel**:

**with_skill sub-agent prompt template**:
```
You are an AI assistant. Use the following skill definition to guide your response.

<skill>
{SKILL_MD_CONTENT}
</skill>

User request: {case.prompt}

{case.context if present}
```

**baseline sub-agent prompt template**:
```
You are an AI assistant.

User request: {case.prompt}

{case.context if present}
```

### Step 3: Collect Responses

For each response:
- Capture first 500 chars as `response_snippet`
- Pass full response + `case.assertions` → `agents/grader.md`
- Receive `grading_result.json` back

### Step 4: Write Results

Write each result to:
- `evals/<skill_id>/runs/<run_id>_<case_id>_with_skill.json`
- `evals/<skill_id>/runs/<run_id>_<case_id>_baseline.json`

Report: `{N} cases completed, {M} failed assertion checks`

---

## Error Handling

| Error | Action |
|-------|--------|
| SKILL.md not found | Stop, report: "skill_id '{id}' not found at skills/{id}/SKILL.md" |
| evals.json parse error | Stop, report line/column of JSON error |
| Sub-agent spawn failure | Log error, mark case as `score: null`, continue |
| Grader returns malformed result | Mark as `score: null`, log and continue |

> **Values**: 基礎と型 — Fail fast on setup errors; tolerate partial failures at case level.
