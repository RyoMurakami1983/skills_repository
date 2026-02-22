---
name: agent-batch-workflow
description: >
  Run multi-file batch operations with parallel agents and structured progress reporting.
  Use when processing multiple skills, files, or components in a single session with
  quality gates and branch-first discipline.
metadata:
  author: RyoMurakami1983
  tags: [agent, batch, parallel, workflow, horenso, branch-management]
  invocable: true
---

# Agent Batch Workflow

A sequential workflow for large-scale batch operations using parallel AI agents. Codifies three proven practices from the cosmos migration furikaeri: branch-first discipline, 3-agent parallel execution (2 workers + 1 reviewer), and 5-minute progress reporting (報連相).

## When to Use This Skill

Use this skill when:
- Processing 5+ files or skills in a single session
- Modernizing, refactoring, or migrating multiple components at once
- Running batch validation, update, or generation across a codebase
- Wanting structured progress visibility during long agent operations
- Needing quality gates (review agent) between work and commit

Do **not** use when:
- Working on a single file or skill (standard workflow suffices)
- The task requires deep domain research before any changes (use explore agents first)
- Changes are interdependent and must be sequential (no parallelism benefit)

## Related Skills

- **`github-pr-workflow`** — PR creation after batch completion (Step 5)
- **`git-commit-practices`** — Commit formatting for batch commits
- **`git-initial-setup`** — Branch protection that this workflow respects
- **`furikaeri-practice`** — The retrospective that produced this workflow

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — verify with `gh auth status`
- SQL tool (session database for task tracking)
- Task tool with `general-purpose` and `code-review` agent types

---

## Core Principles

1. **Branch First** (基礎と型) — No work starts on main. `git switch -c` is the first command.
2. **Decompose Before Executing** (温故知新) — Break work into trackable units before starting.
3. **Parallel With Review** (成長の複利) — 2 workers produce, 1 reviewer validates. Quality scales with speed.
4. **Report Without Stopping** (継続は力) — Progress is visible, but agents don't pause for status updates.
5. **Batch Commits** (ニュートラルな視点) — Group related changes into atomic, reviewable commits.

---

## Workflow: Run a Batch Operation

### Step 1: Branch First

Create a feature branch before any changes. This is a non-negotiable gate.

Use when starting any batch operation. Always execute this step first.

> **Values**: 基礎と型 — The branch is the foundation. No branch, no work.

```bash
# Verify clean state
git status --short

# Create and switch to feature branch
git switch -c feature/<operation-summary>
```

**Naming conventions:**
- `feature/cosmos-migration-phase-2` — new capability or migration
- `refactor/modernize-wpf-skills` — structural improvement
- `fix/validate-frontmatter-all` — batch bug fixes

**Gate**: If `git switch -c` fails (dirty working tree), stash or commit first. Never proceed on main.

### Step 2: Task Decomposition

Break the batch into trackable units using SQL todos. Group into batches of 2–3 items for parallel execution.

Use when you have identified the full scope of work. Do this before launching any agents.

> **Values**: 温故知新 — Past experience shows that untracked batch work leads to missed items and duplicated effort.

```sql
-- Register all work items
INSERT INTO todos (id, title, description, status) VALUES
  ('skill-a', 'Modernize skill A', 'Update frontmatter, add JA, validate', 'pending'),
  ('skill-b', 'Modernize skill B', 'Update frontmatter, add JA, validate', 'pending'),
  ('skill-c', 'Modernize skill C', 'Update frontmatter, add JA, validate', 'pending');

-- Define dependencies if needed
INSERT INTO todo_deps (todo_id, depends_on) VALUES
  ('skill-c', 'skill-a');  -- C depends on A

-- Group into batches
-- Batch 1: skill-a + skill-b (independent, can parallelize)
-- Batch 2: skill-c (depends on skill-a)
```

**Batching rules:**
- Group independent items into batches of 2–3
- Items with dependencies go into later batches
- Similar items (same type of change) batch together

### Step 3: Parallel Execution

Launch 2 worker agents and 1 review agent per batch. Workers execute changes; the reviewer validates completed work.

Use when a batch is ready for execution. This is the core processing step.

> **Values**: 成長の複利 — Parallel execution multiplies throughput. The review agent ensures quality compounds, not just speed.

**Agent topology:**

```
Worker Agent 1 (general-purpose) ──→ Item A ──→ Done
Worker Agent 2 (general-purpose) ──→ Item B ──→ Done
Review Agent   (code-review)     ──→ Validates A & B after completion
```

**Worker agent prompt template:**

```
You are processing a batch operation in [repo]. Your task:

1. [Specific change description for this item]
2. [Quality criteria to meet]
3. [Files to create/modify]

Work independently. Do not modify files outside your assigned scope.
Report success/failure clearly at the end.
```

**Review agent prompt template:**

```
Review the changes made to [files]. Check for:
1. [Quality gate 1 — e.g., frontmatter format]
2. [Quality gate 2 — e.g., line count ≤500]
3. [Quality gate 3 — e.g., structural parity]

Only flag genuine issues. Do not comment on style.
```

**Execution flow:**
1. Launch Worker 1 + Worker 2 as `mode: "sync"` tasks
2. After both complete, launch Review Agent on their output
3. If review finds issues → fix with a targeted agent → re-review
4. Mark items as `done` in SQL

```sql
UPDATE todos SET status = 'in_progress' WHERE id IN ('skill-a', 'skill-b');
-- After agents complete:
UPDATE todos SET status = 'done' WHERE id IN ('skill-a', 'skill-b');
```

### Step 4: Progress Reporting (報連相)

Report progress at 5-minute intervals. Use the 報連相 (horenso) protocol to keep work visible without blocking agents.

Use when batch execution spans more than 5 minutes. Maintain visibility throughout.

> **Values**: 継続は力 — Continuous small reports build trust and catch problems early. Stopping for every update wastes the compounding effect of sustained work.

**報連相 (Horenso) Protocol:**

| Type | Japanese | Action | When |
|------|----------|--------|------|
| **報告** (Hōkoku) | Report | Share status — do NOT stop work | Every 5 minutes or batch completion |
| **連絡** (Renraku) | Inform | Share facts/changes — do NOT stop work | When something unexpected happens |
| **相談** (Sōdan) | Consult | Stop and ask for direction | When a decision is needed |

**Report format (every 5 minutes):**

```markdown
## Progress — [timestamp]
- ✅ Done: skill-a, skill-b (batch 1)
- 🔄 In progress: skill-c, skill-d (batch 2)
- ⏳ Pending: skill-e, skill-f (batch 3)
- ⚠️ Issues: [none | description]
```

**Decision rules:**
- Agent fails on a single item → 連絡 (inform), skip item, continue batch
- Agent fails on 3+ items → 相談 (consult), stop and ask for guidance
- Unexpected scope change discovered → 相談 (consult), confirm with user
- All items in batch succeed → 報告 (report), proceed to next batch

### Step 5: Commit and PR

Commit completed batches using Conventional Commits, then create a PR.

Use when all batches are done and review agent has validated the changes.

> **Values**: ニュートラルな視点 — Each commit represents a reviewable unit. The PR tells the complete story.

**Commit per batch:**

```bash
# Batch 1 commit
git add <batch-1-files>
git commit -m "refactor(scope): modernize items A and B

- Updated frontmatter to nested metadata format
- Added JA version for bilingual support
- Validated ≥90% PASS

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**Final status check:**

```sql
-- Verify all items are done
SELECT id, status FROM todos WHERE status != 'done';
-- Should return 0 rows
```

**PR creation:** Delegate to `github-pr-workflow` skill or use `gh pr create` directly.

---

## Best Practices

- **Start small**: First batch should be the simplest items to validate the process
- **Homogeneous batches**: Group items requiring the same type of change
- **Review before commit**: Never commit without the review agent's approval
- **Track everything**: SQL todos are the single source of truth for progress
- **Fail fast, skip gracefully**: If one item blocks, skip it and continue the batch

## Common Pitfalls

1. **Skipping the branch step**
   Fix: Make `git switch -c` the literal first command. No exceptions.

2. **Overloading batches**
   Fix: Keep batches at 2–3 items. More than 4 parallel agents reduces quality.

3. **Stopping work for every report**
   Fix: Use 報告/連絡 (report/inform) by default. Only 相談 (consult) requires stopping.

4. **No review agent**
   Fix: Always include 1 code-review agent. Speed without quality creates rework.

5. **Committing everything at once**
   Fix: Commit per batch. Atomic commits make rollback and review manageable.

## Anti-Patterns

- Running on main without a branch (defeats the purpose of this workflow)
- Launching 5+ parallel agents (diminishing returns, context confusion)
- Treating 報連相 as optional (invisible progress leads to duplicated effort)
- Skipping SQL tracking ("I'll remember" — you won't at item 15)
- Merging without final review (the last batch is often the sloppiest)

---

## Quick Reference

### Startup Checklist

```markdown
1. [ ] `git switch -c feature/xxx`
2. [ ] SQL todos registered with dependencies
3. [ ] Batches grouped (2-3 items each)
4. [ ] Worker agent prompts prepared
5. [ ] Review agent criteria defined
```

### 報連相 Decision Table

| Situation | Type | Action |
|-----------|------|--------|
| Batch completed successfully | 報告 | Report progress, continue |
| Unexpected file format found | 連絡 | Inform, adapt, continue |
| 3+ items failing same way | 相談 | Stop, ask user for guidance |
| Scope larger than expected | 相談 | Stop, confirm new scope |
| Single item fails | 連絡 | Inform, skip item, continue |

### Agent Topology

```
┌─────────────────────────────────────────┐
│           Batch Controller              │
│  (you — orchestrates the workflow)      │
├──────────┬──────────┬───────────────────┤
│ Worker 1 │ Worker 2 │  Review Agent     │
│ (gen-p)  │ (gen-p)  │  (code-review)    │
│ Item A   │ Item B   │  Validates A & B  │
└──────────┴──────────┴───────────────────┘
```

---

## FAQ

**Q: How many items can I process in one session?**
A: Tested up to 22 items (cosmos migration). Batches of 2–3 with 5-minute reporting kept everything manageable.

**Q: What if the review agent finds issues?**
A: Launch a targeted fix agent for the specific issue, then re-run the review agent on the fixed file only.

**Q: Can I use more than 2 worker agents?**
A: Not recommended. 2 workers + 1 reviewer is the tested sweet spot. More agents increase context confusion and merge conflicts.

**Q: Should I use `git checkout -b` instead of `git switch -c`?**
A: No. `git switch -c` is the modern Git command (2.23+). This workflow standardizes on it.

**Q: What if an item is blocked by an external dependency?**
A: Mark it as `blocked` in SQL, add a note in the description, and skip it in batching. Address blocked items after the batch completes.

---

## Resources

- [Cosmos Migration Furikaeri](../../docs/furikaeri/2026-02-22-cosmos-migration.md) — Origin of this workflow
- [Git Switch Documentation](https://git-scm.com/docs/git-switch) — Modern branch commands
- [報連相 (Horenso)](https://en.wikipedia.org/wiki/Horenso) — Japanese business communication protocol
