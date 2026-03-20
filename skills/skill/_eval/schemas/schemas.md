# Eval and Validation Schemas

以下の path は `skills/skill/` からの相対表記です。

この文書は eval 関連 artifact の**説明用リファレンス**です。見出しや説明文は日本語化してよい一方で、JSON の key 名、file 名、enum 値、path 断片は互換性のため英語のまま扱います。

## `evals.json`

評価対象の skill、version、test case 一覧を定義します。

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

1 回の採点結果を保存します。各 assertion の pass/fail と score、応答抜粋を含みます。

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

複数 run の集計結果を表します。with-skill と baseline の比較に使います。

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

token 使用量と処理時間を記録します。

```json
{
  "total_tokens": 12345,
  "duration_ms": 9200,
  "total_duration_seconds": 9.2
}
```

## `feedback.json`

benchmark を読んだ結果として、改善提案と次アクションをまとめます。

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

想定する artifact 配置は次のとおりです。

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
