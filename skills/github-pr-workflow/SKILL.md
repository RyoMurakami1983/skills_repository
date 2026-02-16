---
name: github-pr-workflow
description: "Create a PR and close linked issues. State-driven routing from uncommitted changes to PR creation."
version: 2.0.0
metadata:
  author: RyoMurakami1983
  tags: [github, pull-requests, workflow, git, pr-create]
  invocable: false
---

# GitHub PR Workflow

A state-driven workflow that routes from uncommitted changes through PR creation and Issue close.

**Pull Request (PR)**: A reviewed change proposal in GitHub.

## When to Use This Skill

Use this skill when:
- The user requests PR creation (see Glossary in `copilot-instructions.md` for trigger phrases)
- Work on a feature branch is ready to be proposed for merge
- You need to push a branch and open a PR with issue links
- Uncommitted or unpushed changes need routing before PR creation

> **Scope**: This skill covers state detection through PR creation and Issue close. Review handling, CI gates, merge strategy, and post-merge sync are out of scope (future skill).

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

Use when any PR-related request is received.

> **Values**: 基礎と型 / 継続は力

### Step 2: Create Feature Branch

Branch from the latest main. Use descriptive prefixes (`feature/`, `fix/`, `docs/`) with the issue number.

```bash
git switch main
git pull --ff-only
git switch -c feature/issue-123
git push -u origin feature/issue-123
```

Use when starting new work or when Step 1 detected you are on main.

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

---

## Best Practices

- Write PR body in Japanese (team policy)
- Use Conventional Commits format for titles (`feat:`, `fix:`, etc.)
- Always include `Closes #N` to auto-close linked issues
- Use `--body-file` on Windows for reliable UTF-8 handling
- Verify authentication with `gh auth status` before creating PRs

---

## Common Pitfalls

1. **PR body written in English**
   Fix: Use the Japanese template headings (概要/理由/テスト/関連).

2. **Missing issue link**
   Fix: Always include `Closes #N` in the Related section.

3. **Creating PR from main branch**
   Fix: Step 1 state detection routes to feature branch creation first.

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
