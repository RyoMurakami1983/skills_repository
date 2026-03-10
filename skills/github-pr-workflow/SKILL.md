---
name: github-pr-workflow
description: "Create and manage pull requests with the canonical flow from branch validation to PR creation, review waiting, and human merge handoff. Use when implementation is validated and ready for the PR lifecycle."
---

# GitHub PR Workflow

A state-driven workflow that routes from validated implementation through PR creation, issue linkage, review waiting, and human merge handoff.

Canonical route: implementation -> `github-pr-workflow` -> wait for a real review signal -> `github-pr-review-response` -> human merge decision/handoff.

**Pull Request (PR)**: A reviewed change proposal in GitHub.

Detect state first. Create the PR only from a feature branch. Use `--body-file` for any non-trivial body.

## When to Use This Skill

Use this skill when:
- Creating a PR after feature-branch work is ready for review
- Routing uncommitted or unpushed changes before opening a PR
- Linking issues with `Closes #N` or `Refs #N` during PR creation
- Verifying branch and authentication state before running `gh pr create`
- Handing off a review-ready PR without automating the merge decision

> **Scope**: This skill covers state detection through PR creation, issue linkage, low-cost handoff into review waiting, and confirmed post-merge sync for remaining PR branches. Detailed review handling and the merge decision itself stay out of scope.

## Related Skills

- **`github-pr-review-response`** - Review comment triage, fixes, replies, and re-review request after a real review signal
- **`git-commit-practices`** - Commit formatting and atomic changes (delegated from Step 1)
- **`git-initial-setup`** - Branch protection defaults
- **`github-issue-intake`** - Issue creation and triage

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — verify with `gh auth status`
- GitHub repository with push access

---

## Core Principles

1. **Branch First, Clean Main** (基礎と型) - Keep work off main until review and only let verified changes reach main
2. **Traceability** (成長の複利) - Link PRs to issues so future developers learn why
3. **Japanese PR Body** (ニュートラル) - Write PR descriptions in Japanese for the team
4. **State-Driven** (温故知新) - Detect current state and route to the right action
5. **Event-Driven Waiting** (余白の設計) - Wait for review signals instead of repeatedly re-checking the same PR

---

## Decision Table

Use this table to choose the next action at a glance.

| Current state | Next move | Why |
|---|---|---|
| On `main` | Create a feature branch first | Keeps reviewable work off default branch |
| Uncommitted changes exist | Commit before PR creation | Preserves traceable state |
| Commits are local only | Push branch first | `gh pr create` needs the remote branch |
| PR does not exist yet | Create the PR | Opens review flow and issue links |
| PR already exists | Report status and stop | Avoids duplicate PRs |

---

## Responsibility Boundaries

Keep the merge boundary explicit so automation does not overreach.

| Phase | Agent responsibility | Human responsibility |
|---|---|---|
| Before PR | Detect state, create branch, prepare validated changes | Confirm the work is ready to propose |
| PR creation | Open the PR, link issues, summarize evidence | Decide who reviews and when |
| Review waiting | Record the PR URL once, stop polling, and wait for a real review signal | Decide whether to reprioritize before a signal arrives |
| Review response | Hand off to `github-pr-review-response` when a review signal arrives | Review the response and decide whether approval is sufficient |
| Merge decision | Summarize readiness only | Decide whether and when to merge on GitHub |
| After merge | Help with local sync only after merge is confirmed | Confirm the merge actually happened |
| Parallel PR cleanup | Sync remaining PR branches from `origin/main`, rerun checks, summarize re-review needs | Decide merge order and resolve any product-level reprioritization |

Use when the user asks what this skill will and will not automate.

> **Values**: ニュートラル / 余白の設計
## Workflow: Ship via Pull Request

### Step 1: Detect State and Route

Check the current git state and take the appropriate action.

```bash
# 1. Check current branch
BRANCH=$(git branch --show-current)

# 2. Check for uncommitted changes
git status --short

# 3. Check for unpushed commits
git log "origin/${BRANCH}..HEAD" --oneline 2>/dev/null

# 4. Check for existing PR
gh pr list --head "$BRANCH" --state open
```

```powershell
# PowerShell equivalent
$Branch = git branch --show-current

git status --short

git log "origin/$Branch..HEAD" --oneline 2>$null

gh pr list --head $Branch --state open
```

| State | Action |
|-------|--------|
| On main | Create feature branch (Step 2) |
| Uncommitted changes | Delegate to `git-commit-practices`, then return |
| Committed but not pushed | `git push -u origin BRANCH`, then Step 3 |
| Pushed but no PR | Proceed to Step 3 |
| PR already exists | Report PR status and URL |

> **Important**: If uncommitted changes exist, delegate to `git-commit-practices` first. If on main, create a feature branch before any commits.

Use when any PR-related request is received. Why: state detection prevents wrong branching, pushing, or duplicate PR creation.

> **Values**: 基礎と型 / 継続は力

### Step 2: Create Feature Branch

Branch from the latest main. Use descriptive prefixes (`feature/`, `fix/`, `docs/`) with the issue number.

```bash
# Verify authentication before branching (catches push failures early)
gh auth status
git switch main
git pull --ff-only
git switch -c feature/issue-123
git push -u origin feature/issue-123
```

Use when starting new work or when Step 1 detected you are on main. Why: creating the branch first keeps later commits clean and reviewable.

> **Values**: 基礎と型

### Step 3: Open PR and Link Issues

Create a PR with a Japanese body (team policy). Use `Closes` to auto-close issues on merge.

**Inline body** (single-line only):

```bash
gh pr create \
  --title "feat: 支払い画面にフィルタを追加" \
  --body "注文履歴画面に検索フィルタを追加。Closes #123. Refs #130."
```

**File-based body** (standard default for multiline Markdown, code fences, or backticks):

```bash
# Write body to a unique temp file with a quoted heredoc.
# Why: mktemp avoids filename collisions, and trap cleans up on failure paths too.
BODY_FILE="$(mktemp "${TMPDIR:-/tmp}/pr_body.XXXXXX")" || {
  echo "Failed to create temporary file for PR body" >&2
  exit 1
}
cleanup() {
  [ -n "$BODY_FILE" ] && rm -f "$BODY_FILE"
}
trap cleanup EXIT
cat > "$BODY_FILE" <<'EOF'
## 概要
注文履歴画面に検索フィルタを追加し、本文内の `int(order_id)` 例もそのまま残す。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130
EOF

gh pr create --title "feat: 支払い画面にフィルタを追加" --body-file "$BODY_FILE"
```

Prefer this pattern for any non-trivial body. For reusable shell-safe templates (PowerShell + Bash), see `docs/patterns/environment-portability.md` (Template 2).

✅ **Good**: Generate the body file, inspect it, then call `gh pr create --body-file`.
❌ **Bad**: Paste multiline Markdown with backticks directly into `--body` and hope shell quoting survives.
Why: the file-based path is reproducible, reviewable, and safe across shells.

| Keyword | Effect |
|---------|--------|
| `Closes #N` | Auto-closes Issue #N on merge |
| `Refs #N` | Links to Issue #N without closing |

Use when the branch is pushed and no PR exists yet.

> **Values**: 成長の複利 / ニュートラル

✅ **Good**: Create the PR once, record the URL, and hand it off to waiting mode.
❌ **Bad**: Re-run PR creation commands or re-check the same branch with no state change.
Why: one clean handoff preserves traceability and avoids duplicate effort.

### Step 4: Enter Review Waiting Mode Efficiently

After the PR is open, stop active polling. Wait for a concrete trigger, then hand off to `github-pr-review-response` exactly once per new signal.

```bash
# Capture the PR URL once, then stop looping on checks
gh pr view --json url,updatedAt --jq '{url: .url, updatedAt: .updatedAt}'

# Optional low-frequency batch check during a natural pause
gh pr status
```

| Signal | Stay in waiting mode? | Next action | Avoid |
|---|---|---|---|
| New review submitted | No | Open `github-pr-review-response` and inspect comments once | Re-checking before any signal |
| Review requested from you | No | Open `github-pr-review-response` and inspect comments once | Re-checking before any signal |
| User reports new review activity | No | Verify once, then open `github-pr-review-response` | Re-checking before any signal |
| PR is still open but unchanged | Yes | Stay idle | "Just checking again" behavior |
| Only a CI status changed | Usually | Check once only if review work may be blocked | Treating CI noise as review input |
| PR closed or merged | Exit | Stop waiting and move to the next confirmed state | Continuing review checks |

Waiting rules:
- Do not re-check the PR just because it remains open
- If you must check manually, batch all PR checks into one pass at a natural pause
- After `github-pr-review-response` requests re-review, return to this signal-driven waiting mode until a new review signal or explicit human merge direction arrives

Use when the PR exists and work has shifted from creation to waiting.

> **Values**: 余白の設計 / 継続は力

### Step 5: Sync Remaining PR Branches After One PR Merges

If multiple PRs are in flight and one of them gets merged, sync each remaining PR branch with the latest `origin/main` before asking reviewers to continue.

```bash
# Start from a clean worktree and the remaining PR branch
git status --short
git fetch origin
git switch feature/issue-124-followup

# Bring in the newly merged main history
git merge origin/main

# If conflicts occur, resolve them first, then rerun validation
npm test          # or repo-equivalent checks
npm run lint      # or repo-equivalent checks

# Push the sync or conflict-resolution commit
git push origin HEAD
```

Parallel-PR checklist after one branch merges:

1. Confirm the first PR is actually merged on GitHub.
2. Switch to each remaining PR branch and merge `origin/main`.
3. Resolve conflicts immediately if they appear.
4. Rerun validator / lint / relevant tests after the merge.
5. Push the updated branch and request re-review if new commits were added.

✅ **Good**: Treat post-merge sync as a required follow-up whenever sibling PRs touch nearby files or the same workflow.
❌ **Bad**: Leave remaining PRs stale after a related merge, then discover conflicts only at the next merge attempt.
Why: immediate sync keeps review state honest and prevents hidden drift across parallel PRs.

Use when one PR from a parallel set has merged and other review branches still remain open.

> **Values**: 基礎と型 / 継続は力

---

## Best Practices

- Write PR body in Japanese (team policy)
- Use Conventional Commits format for titles (`feat:`, `fix:`, etc.)
- Always include `Closes #N` to auto-close linked issues
- Prefer `--body-file` for any multiline or shell-sensitive body; on Windows, make it the default
- Use `mktemp` + `trap` with a single-quoted heredoc (`<<'EOF'`) when generating body files in Bash
- Verify authentication with `gh auth status` before creating PRs
- Prefer event-driven review waiting; do not burn cycles on repeated checks with no signal
- Batch PR status checks at natural context switches instead of polling one PR at a time
- After one PR merges from a parallel set, sync every remaining branch with `origin/main` before continuing review
- Do not create stacked dependent PR branches from feature branches
- After a base PR merges, run `git fetch origin` and create the next work branch from latest `origin/main` before opening another PR

### Preflight Checklist (Before `gh pr create`)

- [ ] You are on a feature branch (not `main`)
- [ ] `gh auth status` succeeds for the intended account
- [ ] Branch can be pushed to remote (no protection conflict)
- [ ] If changes include `.github/workflows/*`, token includes `workflow` scope
- [ ] Existing open PR for the branch is checked (`gh pr list --head BRANCH --state open`)
- [ ] If `skills/**/SKILL.md` changed, run `uv run python skills/skill-quality-validation/scripts/validate_skill.py skills/<skill_id>/SKILL.md` before PR creation
- [ ] For skill changes, confirm validation gate: overall score ≥85% and each category ≥80% (review warnings and fix high-signal items before review)

---

## Common Pitfalls

1. **PR body written in English**
   Fix: Use the team's Japanese PR template heading order shown in Step 3, not the English Summary/Reason/Test/Related sequence.

2. **Missing issue link**
   Fix: Always include `Closes #N` in the Related section.

3. **Creating PR from main branch**
   Fix: Step 1 state detection routes to feature branch creation first.

4. **Polling for review every few minutes**
   Fix: Switch to event-driven waiting and batch status checks only at planned pauses.

5. **Backticks or `$()` break the PR body**
   Fix: Generate the body with a single-quoted heredoc and pass it via `--body-file`.

6. **Remaining PR branches are left unsynced after a sibling PR merges**
   Fix: Merge `origin/main` into each open sibling branch, rerun checks, and request re-review if the branch changed.

7. **Creating a PR branch from another feature branch (stacked dependency)**
   Fix: Do not stack dependent PR branches. Merge the base PR first, run `git fetch origin`, then branch fresh from latest `origin/main`.

## Troubleshooting

- **`workflow ... not found on the default branch` when dispatching Actions**
  - Cause: `workflow_dispatch` targets workflows present on the default branch.
  - Fix: Merge the workflow file into default branch first, then dispatch.

- **Push rejected for `.github/workflows/*` due to scope**
  - Cause: Token lacks `workflow` scope.
  - Fix: Re-authenticate with `gh auth refresh -h github.com -s workflow`.

- **A remaining PR turns conflicted after another PR merged**
  - Cause: The branch still points to pre-merge main history.
  - Fix: `git fetch origin`, switch to the remaining branch, merge `origin/main`, resolve conflicts, rerun checks, and push before asking for more review.

---

## Anti-Patterns

- Pushing directly to main, then creating a PR
- Creating PRs without issue numbers
- Leaving PR body empty

---

## Quick Reference

### PR Flow Checklist

- [ ] Verify `gh auth status`
- [ ] Detect state (uncommitted / unpushed / no PR)
- [ ] Commit via `git-commit-practices` if needed
- [ ] Push branch to origin
- [ ] Create PR with `gh pr create` (Japanese body + `Closes #N`)
- [ ] Record the PR URL once, then enter signal-driven review waiting
- [ ] On a real review signal, hand off to `github-pr-review-response` for fixes, replies, and re-review request
- [ ] Hand the merge decision to a human after review work is complete
- [ ] If a sibling PR merges first, sync this branch with `origin/main`, rerun checks, and re-request review as needed

### Self-Review Checklist (Before finishing)

- [ ] PR body includes intent, reason, test, and issue links
- [ ] Body generation uses quoted heredoc + `--body-file` when Markdown contains backticks or shell examples
- [ ] New automation/workflow changes include required path preparation steps
- [ ] GitHub API create operations are idempotent (e.g., tolerate 422 race)
- [ ] Label names/colors follow repository conventions

### PR Body Template

```markdown
## 概要
(What changed)

## 理由
(Why this change is needed)

## テスト
(How it was verified)

## 関連
Closes #N
```

---

## FAQ

**Q: Can PR body be written in English?**
A: No. Team policy requires Japanese PR descriptions.

**Q: Does this skill handle reviews and merges?**
A: It handles PR creation, signal-driven review waiting, and confirmed post-merge sync for remaining PR branches. The standard route is implementation -> `github-pr-workflow` -> wait for review signal -> `github-pr-review-response` -> human merge decision/handoff.

**Q: What if `gh` is not installed?**
A: `gh auth status` will fail. Install [GitHub CLI](https://cli.github.com/) first.

---

## Resources

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
