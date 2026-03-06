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

A state-driven workflow that routes from uncommitted changes through PR creation and issue linkage.

**Pull Request (PR)**: A reviewed change proposal in GitHub.

Detect state first. Create the PR only from a feature branch. Use `--body-file` for any non-trivial body.

## When to Use This Skill

Use this skill when:
- Creating a PR after feature-branch work is ready for review
- Routing uncommitted or unpushed changes before opening a PR
- Linking issues with `Closes #N` or `Refs #N` during PR creation
- Verifying branch and authentication state before running `gh pr create`
- Handing off a review-ready PR without automating the merge decision

> **Scope**: This skill covers state detection through PR creation and issue linkage. The final merge decision stays with a human, and post-merge sync is a separate follow-up step after merge confirmation.

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
| Merge decision | Summarize readiness only | Decide whether and when to merge on GitHub |
| After merge | Help with local sync only after merge is confirmed | Confirm the merge actually happened |

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

**File-based body** (recommended default for multiline Markdown, code fences, or backticks):

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

Prefer this pattern for any non-trivial body, especially when Markdown contains backticks, shell examples, or multiple paragraphs.

✅ **Good**: Generate the body file, inspect it, then call `gh pr create --body-file`.
❌ **Bad**: Paste multiline Markdown with backticks directly into `--body` and hope shell quoting survives.
Why: the file-based path is reproducible, reviewable, and safe across shells.

| Keyword | Effect |
|---------|--------|
| `Closes #N` | Auto-closes Issue #N on merge |
| `Refs #N` | Links to Issue #N without closing |

Use when the branch is pushed and no PR exists yet.

> **Values**: 成長の複利 / ニュートラル

✅ **Good**: Open the PR, summarize readiness, then stop before the human merge decision.
❌ **Bad**: Treat PR creation as implicit permission to merge or sync `main`.
Why: explicit handoff preserves the human decision boundary and keeps automation safe.

---

## Best Practices

- Write PR body in Japanese (team policy)
- Use Conventional Commits format for titles (`feat:`, `fix:`, etc.)
- Always include `Closes #N` to auto-close linked issues
- Prefer `--body-file` for any multiline or shell-sensitive body; on Windows, make it the default
- Use `mktemp` + `trap` with a single-quoted heredoc (`<<'EOF'`) when generating body files in Bash
- Verify authentication with `gh auth status` before creating PRs

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

4. **Backticks or `$()` break the PR body**
   Fix: Generate the body with a single-quoted heredoc and pass it via `--body-file`.

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
A: It handles PR creation only. Review response is handled by `github-pr-review-response`, merge remains a human decision, and post-merge sync is a separate follow-up step.

**Q: What if `gh` is not installed?**
A: `gh auth status` will fail. Install [GitHub CLI](https://cli.github.com/) first.

---

## Resources

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
