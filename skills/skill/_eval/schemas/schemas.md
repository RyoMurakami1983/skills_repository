# Eval and Validation Schemas

Paths below are relative to `skills/skill/`.

## `evals.json`

```json
{
  "skill_id": "skill-name",
  "version": "1.0.0",
  "description": "What this evaluation measures",
  "cases": [
    {
      "id": "tc-001",
      "prompt": "Create a new skill for ...",
      "assertions": [
        { "type": "contains", "value": "Use this skill when", "weight": 1.0 }
      ],
      "tags": ["should-trigger"]
    }
  ]
}
```

## `grading_result.json`

```json
{
  "case_id": "tc-001",
  "run_id": "run-001",
  "mode": "with_skill",
  "score": 1.0,
  "assertions": [
    { "type": "contains", "passed": true, "weight": 1.0, "detail": "" }
  ],
  "response_snippet": "First 500 characters",
  "timestamp": "2026-03-15T00:00:00Z"
}
```

## `benchmark_summary.json`

```json
{
  "skill_id": "skill-name",
  "eval_version": "1.0.0",
  "runs": {
    "with_skill": { "count": 8, "mean": 0.92, "stddev": 0.04, "min": 0.85, "max": 1.0 },
    "baseline": { "count": 8, "mean": 0.71, "stddev": 0.12, "min": 0.45, "max": 0.9 }
  },
  "summary": { "delta": 0.21, "improvement_pct": 29.58, "verdict": "improved" }
}
```

## `timing.json`

```json
{
  "total_tokens": 12345,
  "duration_ms": 9200,
  "total_duration_seconds": 9.2
}
```

## `feedback.json`

```json
{
  "skill_id": "skill-name",
  "eval_version": "1.0.0",
  "items": [
    { "type": "problem", "content": "Near-miss prompts still trigger", "priority": 1 }
  ],
  "next_action": "revise_skill",
  "created_at": "2026-03-15T00:00:00Z"
}
```

## Workspace Layout

```text
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-descriptive-name/
│   │   ├── with_skill/
│   │   ├── without_skill/
│   │   ├── eval_metadata.json
│   │   ├── grading.json
│   │   └── timing.json
│   ├── benchmark.json
│   └── benchmark.md
└── skill-snapshot/
```
