---
name: github-pr-workflow
description: "Use when you need to create a PR from repo state, link issues, and hand off a review-ready branch."
metadata:
  author: RyoMurakami1983
  tags: [github, pull-requests, workflow, git, pr-create]
  invocable: false
  tool_versions:
    git: ">=2.30"
    gh: ">=2.0"
  last_reviewed: "2026-03-01"
---

# GitHub PR Workflow

A state-driven workflow that routes from uncommitted changes through PR creation and Issue close.

**Pull Request (PR)**: A reviewed change proposal in GitHub.

Detect state first. Create the PR only from a feature branch. Use `--body-file` for any non-trivial body.

## When to Use This Skill

Use this skill when:
- Creating a PR after feature-branch work is ready for review
- Routing uncommitted or unpushed changes before opening a PR
- Linking issues with `Closes #N` or `Refs #N` during PR creation
- Verifying branch and authentication state before running `gh pr create`
- Handing off a review-ready PR without automating the merge decision

> **Scope**: This skill covers state detection through PR creation, issue linkage, and low-cost handoff into review waiting. Detailed review handling, merge strategy, and post-merge sync are out of scope.

## Related Skills

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

1. **Branch First** (基礎と型) - Work stays off main until reviewed
2. **Traceability** (成長の複利) - Link PRs to issues so future developers learn why
3. **Japanese PR Body** (ニュートラル) - Write PR descriptions in Japanese for the team
4. **Clean Main** (継続は力) - Only verified changes reach main
5. **State-Driven** (温故知新) - Detect current state and route to the right action
6. **Event-Driven Waiting** (余白の設計) - Wait for review signals instead of repeatedly re-checking the same PR

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

**Inline body** (short PRs):

```bash
gh pr create \
  --title "feat: 支払い画面にフィルタを追加" \
  --body "## 概要
注文履歴画面に検索フィルタを追加。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130"
```

**File-based body** (recommended for UTF-8 safety on Windows):

```bash
# Write body to a temp file
cat > pr_body.md << 'EOF'
## 概要
注文履歴画面に検索フィルタを追加。

## 理由
サポートから検索要求が多く、対応工数を削減するため。

## テスト
ローカルで動作確認済み。

## 関連
Closes #123
Refs #130
EOF

gh pr create --title "feat: 支払い画面にフィルタを追加" --body-file pr_body.md
```

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

After the PR is open, stop active polling. Wait for a concrete trigger, then hand off to `github-pr-review-response`.

```bash
# Capture the PR URL once, then stop looping on checks
gh pr view --json url,updatedAt --jq '{url: .url, updatedAt: .updatedAt}'

# Optional low-frequency batch check during a natural pause
gh pr status
```

| Trigger | Action | Avoid |
|---------|--------|-------|
| New review notification or user says review arrived | Open `github-pr-review-response` and inspect comments once | Re-checking before any signal |
| Planned batch check after finishing another task | Run one consolidated `gh pr status` | Per-PR polling loops |
| No new activity signal | Stay idle | "Just checking again" behavior |
| PR closed or merged | Exit waiting mode | Continuing review checks |

Exit waiting mode when one of these happens:
- A new review or review request needs action
- The PR is closed or merged
- The user explicitly reprioritizes the session

Use when the PR exists and work has shifted from creation to waiting.

> **Values**: 余白の設計 / 継続は力

---

## Best Practices

- Write PR body in Japanese (team policy)
- Use Conventional Commits format for titles (`feat:`, `fix:`, etc.)
- Always include `Closes #N` to auto-close linked issues
- Use `--body-file` on Windows for reliable UTF-8 handling
- Verify authentication with `gh auth status` before creating PRs
- Prefer event-driven review waiting; do not burn cycles on repeated checks with no signal
- Batch PR status checks at natural context switches instead of polling one PR at a time

### Preflight Checklist (Before `gh pr create`)

- [ ] You are on a feature branch (not `main`)
- [ ] `gh auth status` succeeds for the intended account
- [ ] Branch can be pushed to remote (no protection conflict)
- [ ] If changes include `.github/workflows/*`, token includes `workflow` scope
- [ ] Existing open PR for the branch is checked (`gh pr list --head BRANCH --state open`)

---

## Common Pitfalls

1. **PR body written in English**
   Fix: Use the Japanese template headings (概要/理由/テスト/関連).

2. **Missing issue link**
   Fix: Always include `Closes #N` in the Related section.

3. **Creating PR from main branch**
   Fix: Step 1 state detection routes to feature branch creation first.

4. **Polling for review every few minutes**
   Fix: Switch to event-driven waiting and batch status checks only at planned pauses.

## Troubleshooting

- **`workflow ... not found on the default branch` when dispatching Actions**
  - Cause: `workflow_dispatch` targets workflows present on the default branch.
  - Fix: Merge the workflow file into default branch first, then dispatch.

- **Push rejected for `.github/workflows/*` due to scope**
  - Cause: Token lacks `workflow` scope.
  - Fix: Re-authenticate with `gh auth refresh -h github.com -s workflow`.

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
- [ ] Record the PR URL once, then wait for review signals instead of polling

### Self-Review Checklist (Before finishing)

- [ ] PR body includes intent, reason, test, and issue links
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
A: No. This skill covers PR creation only. Review and merge will be a separate skill.

**Q: What if `gh` is not installed?**
A: `gh auth status` will fail. Install [GitHub CLI](https://cli.github.com/) first.

---

## Resources

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
