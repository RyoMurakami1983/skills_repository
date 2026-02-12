---
name: skill-git-commit-practices
description: Commit practices with Conventional Commits and atomic changes. Use when standardizing team history.
author: RyoMurakami1983
tags: [git, commits, conventional-commits, workflow, quality]
invocable: false
version: 1.0.0
---

# Git Commit Practices

Practical patterns for consistent commit messages, atomic changes, and durable history.

**Conventional Commits**: A standardized commit message format (feat, fix, docs).
**Atomic Commit**: A single-purpose change that can be reverted independently.
**Pull Request (PR)**: A reviewed change proposal in GitHub.

Progression: Simple → Intermediate → Advanced examples improve clarity because each step adds more context.
Reason: The extra context makes future reviews and rollbacks safer.

## When to Use This Skill

Use this skill when:
- Standardizing commit messages across a multi-developer repository
- Writing Japanese commit subjects that stay clear in long histories
- Splitting work into atomic commits for safe reviews and rollbacks
- Documenting "why" in commit bodies for future maintainers
- Preparing clean commit history before Pull Request (PR) review
- Teaching new teammates a repeatable commit workflow

## Related Skills

- **`skill-github-pr-workflow`** - PR creation and merge flow
- **`skill-git-review-standards`** - Review quality and PR sizing
- **`skill-git-history-learning`** - Learning from commit history
- **`skill-issue-intake`** - Issue capture and triage

---

## Dependencies

- Git 2.30+
- Team agreement on Conventional Commits
- Pull Request (PR) workflow for review

---

## Core Principles

1. **Single Intent** - One commit equals one logical change
2. **Explain Why** - Reasons outlive implementation details
3. **Consistent Format** - Predictable history for automation
4. **Reviewable Chunks** - Small commits reduce risk
5. **Learning Asset** - Commit history teaches future teams

---

## Pattern 1: Conventional Commits Structure

### Overview

Conventional Commits provides a predictable commit message format for teams.

### Basic Example

```bash
# ✅ CORRECT
git commit -m "feat: 通知設定を追加"

# ❌ WRONG
git commit -m "update stuff"
```

### Intermediate Example

```bash
git commit -m "fix: CSVインポートの文字化けを修正

Why: UTF-8 BOM付きCSVで失敗していたため"
```

### Advanced Example

```bash
git commit -m "feat(auth)!: OAuth2を導入

BREAKING CHANGE: /auth/login を /oauth/authorize に変更"
```

### When to Use

- When you want automated changelogs from commit history
- When multiple contributors need consistent commit messages

---

## Pattern 2: Type and Scope Selection

### Overview

Choose a type and optional scope to clarify intent and impact.

### Basic Example

| Type | Use | Example |
|------|-----|---------|
| `feat` | New feature | `feat: 通知を追加` |
| `fix` | Bug fix | `fix: 文字化け修正` |
| `docs` | Docs update | `docs: 手順追加` |
| `test` | Tests | `test: E2E追加` |
| `refactor` | Internal change | `refactor: 命名整理` |

E2E means end-to-end (E2E) tests.

### Intermediate Example

```bash
# ✅ CORRECT - scoped change
git commit -m "feat(api): 決済APIを追加"
```

### Advanced Example

```bash
# Monorepo scope
git commit -m "fix(web): 404画面の導線修正"
```

### When to Use

- When modules are clearly separated
- When the repo has multiple domains

---

## Pattern 3: Japanese Message Clarity

### Overview

Write Japanese commit subjects that are specific and searchable.

### Basic Example

```bash
# ✅ CORRECT
git commit -m "fix: ログイン失敗時のエラーメッセージを明確化"

# ❌ WRONG
git commit -m "fix: バグ修正"
```

### Intermediate Example

```bash
git commit -m "feat: 注文履歴画面に検索フィルタを追加

Why: サポート対応で検索要求が多かったため"
```

### Advanced Example

```bash
git commit -m "refactor: 配送計算ロジックを整理

Why: 例外処理の分岐が増えたため"
```

### When to Use

- When Japanese is the primary team language
- When commit history will be used for audits

---

## Pattern 4: Atomic Commits

### Overview

Atomic commits keep each change focused and reversible.

### Basic Example

```bash
# ❌ WRONG - multiple concerns
git commit -m "feat: 認証追加とUI改善とテスト追加"

# ✅ CORRECT - split commits
git commit -m "feat: 認証機能を追加"
git commit -m "refactor: UIレイアウトを改善"
git commit -m "test: 認証フローのテストを追加"
```

### Intermediate Example

- Commit model changes separately from API changes
- Keep docs updates in a separate commit

### Advanced Example

```bash
# Use partial staging
git add -p src/user/service.py
git commit -m "feat: ユーザー検証を追加"
```

### When to Use

- When reviewers need to verify changes incrementally
- When you want safe rollbacks

---

## Pattern 5: Commit Body and Why

### Overview

Explain "why" so future readers understand the decision.

### Basic Example

```bash
git commit -m "fix: APIタイムアウトを10s→30sに変更

Why: 大量データ処理で10sでは不足していたため"
```

### Intermediate Example

```bash
git commit -m "refactor: キャッシュキー生成を整理

- 旧キーの衝突を回避
- 生成ロジックを共通化
Why: 監視で衝突率が増えたため"
```

### Advanced Example

```python
# ✅ CORRECT - attach evidence
import textwrap

message = textwrap.dedent("""\
fix: 画像圧縮率を調整

Why: 画像サイズが平均30%増加していたため
""")
```

### When to Use

- When a change might be questioned later
- When you need to preserve decision context

---

## Pattern 6: Pre-Commit Checklist

### Overview

Use a checklist to keep commits clean and reviewable.

### Basic Example

```bash
git diff
git status
git commit -m "feat: ..."
```

### Intermediate Example

```bash
# Run tests before committing
npm test
```

### Advanced Example

Commit lint configuration file (config) example:

```yaml
# .commitlintrc.yml
rules:
  type-enum: [2, "always", ["feat","fix","docs","test","refactor","chore"]]
```

```csharp
// ✅ CORRECT - Register commit policy checker
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<CommitPolicyChecker>();
```

```bash
# ✅ CORRECT - error handling for commit checks
if ! git diff --check --exit-code; then
  echo "Commit check failed"; exit 1
fi
```

### When to Use

- Before pushing a branch to open a PR
- When onboarding new contributors

---

## Pattern 7: Amend and Rebase Safely

### Overview

Rewrite history only before it is shared.

### Basic Example

```bash
git commit --amend -m "fix: 正しいメッセージ"
```

### Intermediate Example

```bash
git rebase -i HEAD~3
```

### Advanced Example

```bash
# After push: prefer a new commit
git commit -m "fix: 補足修正"
```

### When to Use

- When a commit needs cleanup before PR
- When you want to keep shared branches stable

---

## Best Practices

- Use action verbs in subject lines
- Define a 50-character subject limit
- Apply "Why" lines for non-obvious changes
- Avoid mixing documentation with code changes
- Consider splitting large changes into multiple commits

---

## Common Pitfalls

1. **Vague messages**  
Fix: Use specific nouns and actions in the subject.

2. **Mixing unrelated changes**  
Fix: Split work into atomic commits.

3. **Skipping context**  
Fix: Add a "Why" line for decisions.

---

## Anti-Patterns

- Using TODO comments instead of commits
- Rebasing shared branches after review
- Hiding multiple changes in one commit

---

## Quick Reference

### Commit Checklist

- [ ] Review `git diff`
- [ ] Ensure one logical change per commit
- [ ] Use Conventional Commits format
- [ ] Add "Why" when needed

### Decision Table

| Situation | Action | Why |
|----------|--------|-----|
| Change <30 minutes | Commit directly | Keep momentum |
| Multiple concerns | Split commits | Safer review |
| Shared branch | Avoid rebase | Preserve history |

---

## FAQ

**Q: Should I always add a scope?**  
A: Add scopes when modules are clear or the repo is large.

**Q: Can I use WIP commits?**  
A: WIP is ok locally, but clean up before PR.

**Q: What if I already pushed the wrong message?**  
A: Add a new fix commit instead of rewriting shared history.

---

## Resources

- https://www.conventionalcommits.org
- https://git-scm.com/docs/git-commit
