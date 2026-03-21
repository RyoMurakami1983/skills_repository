# Eval and Validation Schemas

以下の path は `skills/skill/` からの相対表記です。

この文書は eval 関連 artifact の**説明用リファレンス**です。見出しや説明文は日本語化してよい一方で、JSON の key 名、file 名、enum 値、path 断片は互換性のため英語のまま扱います。
標準の variant 名は `baseline / legacy / current` です。旧 `with_skill` は `current` の互換名として扱います。

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

1 回の採点結果を保存します。各 assertion の pass/fail と score、応答抜粋、variant 情報を含みます。

```json
{
  "case_id": "tc-001",
  "run_id": "run-001",
  "mode": "current",
  "variant_id": "current",
  "source_ref": "worktree:feature/skill-improve",
  "skill_snapshot_hash": "0123abcd...",
  "score": 1.0,
  "assertions": [
    { "type": "contains", "passed": true, "weight": 1.0, "detail": "" }
  ],
  "response_snippet": "First 500 characters",
  "timestamp": "2026-03-15T00:00:00Z"
}
```

## `benchmark_summary.json`

複数 run の集計結果を表します。`baseline / legacy / current` の比較に使います。

```json
{
  "skill_id": "skill-name",
  "eval_version": "1.0.0",
  "suite_hash": "89ab0123...",
  "variants": {
    "baseline": { "count": 8, "mean": 0.71, "stddev": 0.12, "min": 0.45, "max": 0.9 },
    "legacy": { "count": 8, "mean": 0.80, "stddev": 0.08, "min": 0.60, "max": 0.95 },
    "current": { "count": 8, "mean": 0.92, "stddev": 0.04, "min": 0.85, "max": 1.0 }
  },
  "variant_metadata": {
    "legacy": { "source_ref": "git:abc123", "skill_snapshot_hash": "4567cdef..." },
    "current": { "source_ref": "worktree:feature/skill-improve", "skill_snapshot_hash": "0123abcd..." }
  },
  "comparisons": {
    "current_vs_legacy": { "lhs": "current", "rhs": "legacy", "delta": 0.12, "improvement_pct": 15.0, "verdict": "improved" },
    "current_vs_baseline": { "lhs": "current", "rhs": "baseline", "delta": 0.21, "improvement_pct": 29.58, "verdict": "improved" },
    "legacy_vs_baseline": { "lhs": "legacy", "rhs": "baseline", "delta": 0.09, "improvement_pct": 12.68, "verdict": "improved" }
  },
  "summary": { "delta": 0.12, "improvement_pct": 15.0, "verdict": "improved", "primary_comparison": "current_vs_legacy" }
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

## `benchmark_history.jsonl`

append-only の履歴 ledger です。各行に 1 campaign の集計結果を記録します。

```json
{"skill_id":"skill-name","campaign_id":"campaign-001","run_id":"run-001","eval_version":"1.0.0","generated_at":"2026-03-15T00:00:00Z","summary":{"delta":0.12,"improvement_pct":15.0,"verdict":"improved","primary_comparison":"current_vs_legacy"},"variants":{"baseline":{"count":8,"mean":0.71},"legacy":{"count":8,"mean":0.80},"current":{"count":8,"mean":0.92}},"comparisons":{"current_vs_legacy":{"lhs":"current","rhs":"legacy","delta":0.12,"improvement_pct":15.0,"verdict":"improved"}}}
```

## Promotion Rule

- `baseline` は常に固定の no-skill 基準です。
- `legacy` は「前回 accept した版」です。
- `current` を accept したら、次回 campaign ではその snapshot を `legacy` として扱います。
- 過去の `legacy` は `benchmark_history.jsonl` に残り続けるため、継続改善の trend を失いません。

## Workspace Layout

想定する artifact 配置は次のとおりです。

```text
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-descriptive-name/
│   │   ├── baseline/
│   │   ├── legacy/
│   │   ├── current/
│   │   ├── eval_metadata.json
│   │   ├── grading.json
│   │   └── timing.json
│   ├── benchmark.json
│   └── benchmark.md
└── skill-snapshot/
```
