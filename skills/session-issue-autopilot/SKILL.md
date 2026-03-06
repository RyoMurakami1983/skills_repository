---
name: session-issue-autopilot
description: End-to-end issue handling autopilot for a working session. Use when a greeting indicates you want to start focused Issue work and carry it through PR, review response, and collaborative retrospective.
metadata:
  author: RyoMurakami1983
  tags: [session, issue, workflow, github, pr, retrospective, kpt, ywt, autopilot]
  invocable: false
---

# Session Issue Autopilot

Single-workflow skill for running an issue-focused session from trigger detection to implementation, PR, review response, and collaborative retrospective.

## When to Use This Skill

Use this skill when:
- A user greeting also signals issue handling intent and asks to begin immediate, focused execution.
- You need one guided flow from issue selection through coding, PR creation, review handling, and closure.
- You want to prioritize one issue with high compound impact that still fits a one-day implementation scope.
- You must keep human checkpoints explicit, especially agent selection and collaborative retrospective decisions.

## Core Principles

1. **Intent First, Then Execution** — Detect the greeting-trigger correctly before touching implementation work (基礎と型)
2. **One Day, High Compound Impact** — Choose one issue that compounds future speed, quality, or learning (成長の複利)
3. **Human-in-the-Loop Checkpoints** — Mandatory user confirmation for agent choice and retrospective participation (ニュートラル)
4. **Traceable Conversation to Artifact** — Move decisions into issues, PRs, and records so progress survives sessions (継続は力)
5. **Safe Automation Boundaries** — Automate mechanics, never bypass collaborative reflection and consent checkpoints (余白の設計)
6. **Human Merge Decision** — Merge on GitHub stays with a human; automation resumes only for confirmed post-merge sync (基礎と型)

## Workflow: Run Session Issue Autopilot

### Step 1: Detect Trigger and Confirm Issue-Focused Mode

Detect combined intent: greeting + issue handling start signal.

Trigger examples:
- "Good morning, let's solve Issues"
- "Hello, start issue handling now"

Reply with explicit mode confirmation before doing work.

```markdown
Detected trigger: greeting + issue-handling intent.
Switching to **Issue-Focused Session Mode**.
Proceed? (yes/no)
```

Use when starting the session. Why: wrong mode detection causes unnecessary branching and wasted work.

> **Values**: 基礎と型 / ニュートラル

### Step 2: Build Issue Inventory and Detect Resolved Candidates

Collect open issues and infer if any are likely already resolved by merged PRs, commits, or completed behavior.

```bash
git --no-pager log --oneline -20
# optional: gh issue list --state open --limit 30
```

Create a triage table:

| Issue | State | Evidence | Action |
|---|---|---|---|
| #101 | Open | PR #220 merged, tests cover acceptance | Mark resolved-candidate |
| #108 | Open | No linked PR | Keep active |

Use when multiple open issues exist. Why: inventory first avoids duplicate work and stale queue noise.

> **Values**: 温故知新 / ニュートラル

### Step 3: Select One High-Compound Issue Within 1 Day

From active issues, choose exactly one with highest compound effect and one-day scope.

```markdown
Selection rubric (score 1-5 each):
- Compound leverage (future speed/quality impact)
- User value
- Confidence to complete in one day
- Dependency risk (reverse score)
```

Decision rule: pick top score that is feasible today; defer others to backlog comments.

Use when prioritizing execution. Why: one finished high-leverage issue beats many half-done threads.

> **Values**: 成長の複利 / 継続は力

### Step 4: Mandatory Agent Selection Checkpoint

Before implementation, ask the user which specialist to involve. Include `skill-shihan` as an explicit option.

```markdown
Mandatory checkpoint — choose execution agent:
1) skill-shihan (skill/workflow quality)
2) dotnet-shihan
3) python-shihan
4) typescript-shihan
5) Proceed without specialist

Which do you want? I will wait for your selection.
```

Do not continue until user answers.

Use when crossing from planning into execution. Why: explicit role assignment improves accountability and fit.

> **Values**: ニュートラル / 基礎と型

### Step 5: Implement and Validate

Implement the selected issue in a focused branch, then run relevant tests/lint/validation.

```bash
git checkout -b feature/issue-<id>-short-title
# implement changes
# run project tests/lint relevant to changed area
```

Capture validation evidence in plain text summary (what passed, what failed, next fix).

Use when coding is approved. Why: implementation without validation creates review churn.

> **Values**: 基礎と型 / 継続は力

### Step 6: Create PR (with Body File Safety)

Open a PR with clear context, test evidence, and issue linkage.

**Use body-file for `gh` commands** to avoid shell quoting/backtick breakage in multiline markdown.

```bash
cat > /tmp/pr_body.md <<'MD'
## Summary
- Implemented #<issue-id>

## Validation
- [x] tests
- [x] lint

## Link
- Closes #<issue-id>
MD

gh pr create --title "feat: resolve #<issue-id> <short-title>" --body-file /tmp/pr_body.md
```

Use when validation is green. Why: body-file prevents fragile CLI escaping issues and preserves markdown fidelity.

> **Values**: 基礎と型 / 温故知新

### Step 7: Monitor and Reply to Review Comments

Track PR feedback and respond with fix commits or rationale. Keep replies concise and evidence-based.

**Also use body-file for long comments**.

```bash
cat > /tmp/review_reply.md <<'MD'
Thanks for the review.
Addressed in commit <sha>:
- Fixed null-handling path
- Added regression test
MD

gh pr comment <pr-number> --body-file /tmp/review_reply.md
```

Use when review starts. Why: fast, structured response shortens cycle time and prevents context loss.

> **Values**: 継続は力 / ニュートラル

### Step 8: Human Merge Gate and Safe Post-Merge Sync

After review response is complete, stop at the merge gate. A human decides whether to merge on GitHub.

Only after the merge is confirmed should you help with local sync, and only if the worktree is clean.

```bash
# Verify the merge already happened and local tree is safe to sync
git status --short
git switch main
git pull --ff-only
```

Safety rules:
- Do not perform the GitHub merge yourself
- If `git status --short` is not clean, stop and ask the user
- If `git pull --ff-only` fails, stop and surface the divergence

Use when review response is complete and the next step is merge or post-merge cleanup.

> **Values**: 基礎と型 / 余白の設計

### Step 9: Mandatory Collaborative Retrospective Checkpoint

After merge (or after review cycle pause), ask user to join retrospective.

```markdown
Mandatory checkpoint:
Shall we run a collaborative retrospective now? (yes/no)
I will wait for your participation.
```

**Do NOT auto-run retrospective without user join.** Wait for explicit yes.

Use when execution loop is complete. Why: reflection without participant alignment becomes shallow and non-actionable.

> **Values**: 余白の設計 / 成長の複利

### Step 10: Run KPT/YWT and Record Actions (Issue/Notion)

If user joined Step 9, run KPT or YWT and persist next actions.

```markdown
Choose format: KPT or YWT
- KPT: Keep / Problem / Try
- YWT: Yatta / Wakatta / Tsugi

Recording targets:
- GitHub Issue: concrete engineering/process actions
- Notion (if available): session log and learning history
```

At minimum, register actionable items as issues; include links between retrospective notes and issues.

Use when collaborative retrospective is approved. Why: recorded actions turn reflection into compounding execution.

> **Values**: 成長の複利 / 継続は力 / 温故知新

## Best Practices

- ✅ Start with explicit mode confirmation; never assume greeting intent equals immediate coding permission.
- Keep issue inventory visible as a table before prioritization.
- Enforce one-day scope hard; split oversized issues into follow-ups.
- Keep agent checkpoint mandatory and blocking.
- Prefer `--body-file` for all non-trivial `gh` issue/PR/comment content.
- Keep merge on GitHub human-only, then run post-merge sync only after merge confirmation
- Keep retrospective outputs linked to concrete tracking artifacts.

## Common Pitfalls

1. Jumping to code before confirming issue-focused mode.
   - Fix: always run Step 1 confirmation first.
2. Selecting a large issue that cannot finish in a day.
   - Fix: apply one-day feasibility gate and split scope.
3. Skipping agent selection checkpoint.
   - Fix: require explicit user answer before Step 5.
4. Posting multiline `gh` content inline and breaking markdown/backticks.
   - Fix: use temporary markdown files with `--body-file`.
5. Auto-merging or syncing before human confirmation.
   - Fix: stop at the merge gate, then verify merge confirmation and a clean tree before syncing.
6. Running retrospective automatically without user collaboration.
   - Fix: block on Step 9 yes/no response.

## Anti-Patterns

- ❌ Full automation with no human checkpoints for role selection or retrospective join.
- ❌ Automating the GitHub merge decision instead of handing it to a human.
- Issue roulette: switching targets mid-session without an explicit reprioritization decision.
- PR-first behavior with weak or missing validation evidence.
- Treating retrospective as optional decoration instead of a compounding design loop.

## Quick Reference

| Phase | Mandatory Output | Gate Question |
|---|---|---|
| Trigger | Issue-focused mode confirmation | "Proceed in Issue-Focused Session Mode?" |
| Inventory | Open + resolved-candidate table | "Any stale issues to close/update?" |
| Prioritize | One issue (1-day, high compound) | "Can we finish this today?" |
| Agent Checkpoint | User-selected agent (include skill-shihan) | "Which specialist should join?" |
| Build & Validate | Branch + passing evidence | "Are validations green?" |
| PR | PR created via `--body-file` | "Does PR body include link + evidence?" |
| Review Loop | Responses and fix commits | "Did we address all review threads?" |
| Merge Gate | Human merge decision + safe local sync | "Has a human merged this PR already?" |
| Retro Checkpoint | Explicit user yes/no | "Shall we run collaborative retrospective now?" |
| KPT/YWT Record | Action items in Issue/Notion | "Were actions recorded with links?" |

### Minimal Command Pattern

```bash
# safer GH text handling
cat > /tmp/body.md <<'MD'
<markdown with backticks and bullets>
MD

gh issue comment <issue-number> --body-file /tmp/body.md
gh pr comment <pr-number> --body-file /tmp/body.md
```
