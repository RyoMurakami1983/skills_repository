---
name: github-pr-workflow
description: "PRを作成しIssueをクローズする。「プルリクして」「PR作成」で使う。"
author: RyoMurakami1983
tags: [github, pull-requests, workflow, git, pr-create]
invocable: false
version: 2.0.0
---

# GitHub PR Workflow

状態検知からPR作成・Issueクローズまでを自動化するワークフロー。

**Pull Request (PR)**: A reviewed change proposal in GitHub.

## When to Use This Skill

Use this skill when:
- The user says "プルリクして", "PR作成して", "PRを作って", or "create a PR"
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

Use when the user says "プルリクして", "PR作成して", or any PR-related request.

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

Create a PR with a Japanese body. Use `Closes` to auto-close issues on merge.

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
| `Closes #N` | Merges時にIssue #N を自動クローズ |
| `Refs #N` | Issue #N へのリンク（クローズしない） |

Use when the branch is pushed and no PR exists yet.

> **Values**: 成長の複利 / ニュートラル

---

## Best Practices

- PR本文は日本語で記述する（チーム標準）
- タイトルは Conventional Commits 形式（`feat:`, `fix:` 等）
- `Closes #N` で Issue を自動クローズする
- Windows では `--body-file` で UTF-8 を確実に扱う
- `gh auth status` で認証を事前確認する

---

## Common Pitfalls

1. **PR body が英語になる**
   Fix: テンプレ見出しを日本語で統一（概要/理由/テスト/関連）。

2. **Issue リンクの忘れ**
   Fix: `## 関連` セクションに `Closes #N` を必ず含める。

3. **main ブランチから直接 PR を作る**
   Fix: Step 1 の状態検知で feature branch 作成に誘導。

---

## Anti-Patterns

- main に直接 push してから PR を作る
- Issue 番号なしで PR を作成する
- PR 本文を空にする

---

## Quick Reference

### PR Flow Checklist

- [ ] `gh auth status` で認証を確認
- [ ] 状態を検知（未コミット / 未push / PR無し）
- [ ] 必要なら `git-commit-practices` でコミット
- [ ] ブランチを origin に push
- [ ] `gh pr create` で PR 作成（日本語本文 + `Closes #N`）

### PR Body Template

```markdown
## 概要
（何を変更したか）

## 理由
（なぜこの変更が必要か）

## テスト
（どう検証したか）

## 関連
Closes #N
```

---

## FAQ

**Q: PR本文は英語でも良い？**
A: チームポリシーとして日本語で統一しています。

**Q: レビューやマージはこのスキルで扱う？**
A: このスキルはPR作成までです。レビュー対応・マージは将来の別スキルで扱います。

**Q: `gh` が未インストールの場合は？**
A: `gh auth status` でエラーになります。[GitHub CLI](https://cli.github.com/) をインストールしてください。

---

## Resources

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
