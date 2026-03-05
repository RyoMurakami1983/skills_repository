---
name: notion-safe-operations
description: Use when you need reliable and secure Notion MCP operations with preflight checks, DS ID handling, and fallback payloads.
metadata:
  author: RyoMurakami1983
  tags: [notion, mcp, workflow, security, reliability]
  invocable: false
  last_reviewed: "2026-03-05"
---

# Notion Safe Operations

Use one reusable workflow for Notion operations instead of duplicating ad-hoc steps per skill.

## When to Use This Skill

Use this skill when:
- Saving retrospective records to Notion from another skill
- Updating page properties in a Notion data source
- Validating tool availability after agent/model changes
- Resolving a Data Source (DS) ID from local secure config
- Handling create/update failures without blocking user progress
- Standardizing Notion operation behavior across skills

## Related Skills

- **`furikaeri-practice`** - Stores retrospective logs to Notion
- **`knowledge-capture`** - Applies anonymization before public outputs
- **`skills-revise-skill`** - Applies this base pattern to existing skills

---

## Dependencies

- Notion MCP tools (`notion-notion-fetch`, `notion-notion-create-pages`)
- Local environment variable for DS ID (example: `NOTION_FURIKAERI_DS_ID`)
- Target Notion database access permissions

---

## Core Principles

1. **Run Preflight First** - Execute a real call before writing (基礎と型)
2. **Store IDs Locally** - Keep DS IDs outside repository files (ニュートラル)
3. **Fail with Context** - Return actionable fallback payloads (継続は力)
4. **Reuse One Workflow** - Eliminate duplicated Notion procedures (温故知新)
5. **Explain Rationale** - Always include why each guard exists (成長の複利)

---

## Workflow: Safe Notion Execution

### Step 1: Run Tool Preflight

Run a real fetch call before any write operation.

```text
# ✅ CORRECT - verify callable tool path
notion-notion-fetch(id="collection://<your-data-source-id>")

# ❌ WRONG - trust static listing only
/mcp show
```

| Signal | Decision |
|---|---|
| Fetch succeeds | Continue to Step 2 |
| Tool missing / fetch fails | Stop writes and use Step 5 fallback |

Why: `/mcp show` can list integrations while current runtime still cannot invoke the tool.

> **Values**: 基礎と型 / 継続は力

### Step 2: Resolve DS ID Securely

Load DS ID from local environment variables first.

```bash
# preferred local config
export NOTION_FURIKAERI_DS_ID="collection://..."
```

If missing, fetch the database URL and read `collection://...` from the `<data-source>` tag.

```text
notion-notion-fetch(id="https://www.notion.so/...database-url...")
```

Why: local configuration is reproducible and avoids leaking workspace identifiers.

> **Values**: ニュートラル / 基礎と型

### Step 3: Validate Schema Before Write

Fetch the target data source and verify property names before creating pages.

```text
notion-notion-fetch(id="collection://...")
# Check required properties exist with exact names:
# タイトル, ステータス, 実施内容, 学び・気づき, 課題・問題点, 次回アクション
```

Why: property name mismatch is the most common source of create/update failures.

> **Values**: 成長の複利 / 基礎と型

### Step 4: Execute Create/Update

Use explicit property keys and expanded date fields.

```json
{
  "parent": { "data_source_id": "<resolved-id>" },
  "pages": [
    {
      "properties": {
        "タイトル": "Session title",
        "ステータス": "完了",
        "実施内容": "...",
        "学び・気づき": "...",
        "課題・問題点": "...",
        "次回アクション": "...",
        "関連タグ": "[\"開発\", \"レビュー\"]",
        "date:セッション日時:start": "2026-03-05",
        "date:セッション日時:is_datetime": 0
      }
    }
  ]
}
```

Why: explicit keys reduce ambiguity and improve repeatability across sessions.

> **Values**: 基礎と型 / 温故知新

### Step 5: Return Deterministic Fallback

If write execution fails, return a copy-paste payload and retry guidance.

```markdown
## Notion write failed
- Error: <exact error>
- Retry:
  1. Reset agent/model context
  2. Re-run Step 1 preflight
  3. Re-submit the same payload

Payload:
{ ...ready-to-paste JSON... }
```

Why: a structured fallback preserves momentum even when tools are unstable.

> **Values**: 継続は力 / 成長の複利

---

## Common Pitfalls

1. **Using `/mcp show` as the only health check**
   Fix: Always run `notion-notion-fetch` preflight before writes.

2. **Hardcoding DS ID in committed markdown**
   Fix: Store DS ID in local environment variables.

3. **Guessing property names**
   Fix: Fetch schema and copy exact field names.

---

## Best Practices

- Run preflight in every write flow
- Reuse this skill from other skills instead of duplicating procedures
- Keep fallback payloads short and executable
- Keep sensitive identifiers in local-only configuration

## Anti-Patterns

- Proceeding after preflight failure
- Returning generic "failed" messages without retry steps
- Mixing inline Notion logic into unrelated workflow skills

---

## Quick Reference

### Decision Table

| Situation | Action |
|---|---|
| Need to write Notion data | Run Step 1 preflight first |
| DS ID unknown | Run Step 2 resolution flow |
| Property error occurs | Re-run Step 3 schema check |
| Tool call fails in runtime | Use Step 5 fallback payload |

### Minimal Checklist

- [ ] Preflight fetch succeeded
- [ ] DS ID resolved from local config
- [ ] Schema verified
- [ ] Payload uses exact property names
- [ ] Fallback payload prepared

---

## FAQ

**Q: Why not save DS IDs in repository docs?**
A: DS IDs are workspace-specific identifiers; local-only storage is safer and cleaner.

**Q: Why run preflight every time?**
A: Model/agent context changes can affect callable tool availability.

**Q: What is MCP?**
A: MCP means Model Context Protocol, the tool bridge used to call integrations like Notion.

---

## Resources

- https://developers.notion.com/reference/intro
