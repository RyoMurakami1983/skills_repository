# Eval Pipeline JSON Schemas

JSON contracts for the eval pipeline. All files are UTF-8. Paths are relative to `skills/skills-eval-pipeline/`.

---

## 1. `evals.json` — Test Cases

Defines the test cases for a skill. One file per skill being evaluated.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EvalSuite",
  "type": "object",
  "required": ["skill_id", "version", "cases"],
  "properties": {
    "skill_id": {
      "type": "string",
      "description": "Skill directory name (e.g., 'skills-author-skill')"
    },
    "version": {
      "type": "string",
      "description": "Semantic version of this eval suite (e.g., '1.0.0')"
    },
    "description": {
      "type": "string",
      "description": "Human-readable purpose of this test suite"
    },
    "cases": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "prompt", "assertions"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique test case ID (e.g., 'tc-001')"
          },
          "prompt": {
            "type": "string",
            "description": "The input prompt sent to the agent"
          },
          "context": {
            "type": "string",
            "description": "Optional: additional context injected with the prompt"
          },
          "assertions": {
            "type": "array",
            "minItems": 1,
            "items": { "$ref": "#/$defs/assertion" }
          },
          "tags": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Optional: labels for grouping/filtering (e.g., 'happy-path', 'edge-case')"
          }
        }
      }
    }
  },
  "$defs": {
    "assertion": {
      "type": "object",
      "required": ["type", "value"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["contains", "not_contains", "starts_with", "ends_with", "regex", "llm_grade"],
          "description": "Assertion strategy"
        },
        "value": {
          "type": "string",
          "description": "Expected string/pattern, or grading rubric for llm_grade"
        },
        "weight": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "default": 1.0,
          "description": "Relative importance for score calculation"
        }
      }
    }
  }
}
```

### Example

```json
{
  "skill_id": "skills-author-skill",
  "version": "1.0.0",
  "description": "新規スキル作成フローの動作テスト",
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
      "tags": ["happy-path", "frontmatter"]
    }
  ]
}
```

---

## 2. `grading_result.json` — Single Run Grade

Output from `agents/grader.md` for one test case run.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GradingResult",
  "type": "object",
  "required": ["case_id", "run_id", "mode", "score", "assertions", "timestamp"],
  "properties": {
    "case_id": { "type": "string" },
    "run_id": {
      "type": "string",
      "description": "Unique ID for this execution (e.g., 'run-20260310-001')"
    },
    "mode": {
      "type": "string",
      "enum": ["with_skill", "baseline"],
      "description": "Whether the skill was injected for this run"
    },
    "score": {
      "oneOf": [
        { "type": "number", "minimum": 0, "maximum": 1 },
        { "type": "null" }
      ],
      "description": "Weighted average of all assertion results. null when agent failed to respond."
    },
    "assertions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "passed", "weight"],
        "properties": {
          "type": { "type": "string" },
          "passed": { "type": "boolean" },
          "weight": { "type": "number" },
          "detail": { "type": "string", "description": "Optional: grader explanation" }
        }
      }
    },
    "response_snippet": {
      "type": "string",
      "description": "First 500 chars of the agent response (for debugging)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

---

## 3. `benchmark_summary.json` — Aggregated Results

Output from `scripts/aggregate_benchmark.py`. Summarizes multiple runs across both modes.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BenchmarkSummary",
  "type": "object",
  "required": ["skill_id", "eval_version", "runs", "summary", "generated_at"],
  "properties": {
    "skill_id": { "type": "string" },
    "eval_version": { "type": "string" },
    "runs": {
      "type": "object",
      "properties": {
        "with_skill": {
          "type": "object",
          "required": ["count", "mean", "stddev", "min", "max"],
          "properties": {
            "count": { "type": "integer" },
            "mean": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "stddev": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "min": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "max": { "oneOf": [{ "type": "number" }, { "type": "null" }] }
          }
        },
        "baseline": {
          "type": "object",
          "required": ["count", "mean", "stddev", "min", "max"],
          "properties": {
            "count": { "type": "integer" },
            "mean": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "stddev": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "min": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
            "max": { "oneOf": [{ "type": "number" }, { "type": "null" }] }
          }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["delta", "improvement_pct", "verdict"],
      "properties": {
        "delta": {
          "oneOf": [{ "type": "number" }, { "type": "null" }],
          "description": "with_skill.mean - baseline.mean"
        },
        "improvement_pct": {
          "oneOf": [{ "type": "number" }, { "type": "null" }],
          "description": "delta / baseline.mean * 100"
        },
        "verdict": {
          "type": "string",
          "enum": ["improved", "neutral", "degraded"],
          "description": "delta > 0.05 → improved, < -0.05 → degraded, else neutral"
        }
      }
    },
    "case_breakdown": {
      "type": "array",
      "description": "Per-case score comparison",
      "items": {
        "type": "object",
        "properties": {
          "case_id": { "type": "string" },
          "with_skill_mean": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
          "baseline_mean": { "oneOf": [{ "type": "number" }, { "type": "null" }] },
          "delta": { "oneOf": [{ "type": "number" }, { "type": "null" }] }
        }
      }
    },
    "generated_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 4. `feedback.json` — Human Feedback Loop

Structured feedback from the human-in-the-loop review (余白の設計). Written by the user or `agents/analyzer.md`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FeedbackRecord",
  "type": "object",
  "required": ["skill_id", "eval_version", "items", "created_at"],
  "properties": {
    "skill_id": { "type": "string" },
    "eval_version": { "type": "string" },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "content"],
        "properties": {
          "type": {
            "type": "string",
            "enum": ["keep", "problem", "improve"],
            "description": "KPT classification: Keep / Problem / Try(improve)"
          },
          "content": { "type": "string" },
          "case_id": {
            "type": "string",
            "description": "Optional: link to specific test case"
          },
          "priority": {
            "type": "integer",
            "minimum": 1,
            "maximum": 3,
            "description": "1=high, 2=medium, 3=low"
          }
        }
      }
    },
    "next_action": {
      "type": "string",
      "enum": ["revise_skill", "add_cases", "accept", "escalate"],
      "description": "Recommended next step"
    },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## Schema Compatibility Matrix

| Producer | Consumer | Schema |
|----------|----------|--------|
| `agents/runner.md` | `agents/grader.md` | `grading_result.json` |
| `agents/grader.md` | `scripts/aggregate_benchmark.py` | `grading_result.json` |
| `scripts/aggregate_benchmark.py` | `scripts/generate_viewer.py` | `benchmark_summary.json` |
| `scripts/generate_viewer.py` | `viewer/index.html` | `benchmark_summary.json` |
| `agents/analyzer.md` | `skills-revise-skill` | `feedback.json` |
| Human review | `agents/analyzer.md` | `feedback.json` |

---

## File Naming Conventions

```
evals/
  <skill_id>/
    evals.json                              # Test cases
    runs/
      <run_id>_<case_id>_with_skill.json   # grading_result (with skill)
      <run_id>_<case_id>_baseline.json     # grading_result (baseline)
    benchmark_summary.json                  # Aggregated (generated by script)
    feedback.json                           # Human feedback
```

> **Values**: 基礎と型 — スキーマファーストで設計することで、全コンポーネントが独立して開発・テスト可能になる。
