---
name: git-commit-practices
description: Commit practices with Conventional Commits and atomic changes. Use when standardizing team history.
metadata:
  author: RyoMurakami1983
  tags: [git, commits, conventional-commits, workflow, quality]
  invocable: false
---

# Git Commit Practices

Practical patterns for consistent commit messages, atomic changes, and durable history.

## When to Use This Skill

Use this skill when:
- Standardizing commit messages across a multi-developer repository
- Writing Japanese commit subjects that stay clear in long histories
- Splitting work into atomic commits for safe reviews and rollbacks
- Documenting "why" in commit bodies for future maintainers
- Preparing clean commit history before Pull Request (PR) review
- Teaching new teammates a repeatable commit workflow

## Related Skills

- **`github-pr-workflow`** - PR creation and merge flow
- **`github-issue-intake`** - Issue capture and triage

---

## Dependencies

- Git 2.30+
- Team agreement on Conventional Commits
- Pull Request (PR) workflow for review

## Core Principles

1. **Single Intent** - One commit equals one logical change (基礎と型)
2. **Explain Why** - Reasons outlive implementation details (成長の複利)
3. **Consistent Format** - Predictable history for automation (ニュートラル)
4. **Reviewable Chunks** - Small commits reduce risk (継続は力)
5. **Learning Asset** - Commit history teaches future teams (温故知新)

---

## Workflow: Write Quality Commits

### Step 1: Confirm Feature Branch

Verify you are on a feature branch before committing. Never commit directly to main.

```bash
# Check current branch
git branch --show-current

# If on main, create a feature branch first
git switch -c feature/your-change
```

Use when starting any new work, or when the agent begins a commit workflow.

> **Values**: 基礎と型 / 継続は力

### Step 2: Use Conventional Commits Format

Follow the `type(scope): subject` structure so every commit is parseable by humans and tools.

```bash
git commit -m "feat(auth)!: OAuth2を導入

BREAKING CHANGE: /auth/login を /oauth/authorize に変更"
```

Use when multiple contributors need consistent messages or you want automated changelogs.

### Step 3: Select Type and Scope

Pick the type that matches your intent, and add a scope when modules are clearly separated.

| Type | Use | Example |
|------|-----|---------|
| `feat` | New feature | `feat: 通知を追加` |
| `fix` | Bug fix | `fix: 文字化け修正` |
| `docs` | Docs update | `docs: 手順追加` |
| `test` | Tests | `test: E2E追加` |
| `refactor` | Internal change | `refactor: 命名整理` |

```bash
# Scoped change for multi-domain repos
git commit -m "feat(api): 決済APIを追加"
```

Use when the repo has multiple modules or domains that benefit from explicit scope labels.

### Step 4: Write Clear Japanese Subjects

Be specific so subjects are searchable and self-explanatory in `git log`.

```bash
# ✅ CORRECT - specific action and target
git commit -m "feat: 注文履歴画面に検索フィルタを追加

Why: サポート対応で検索要求が多かったため"

# ❌ WRONG - vague
git commit -m "fix: バグ修正"
```

Use when Japanese is the primary team language or commit history will be used for audits.

### Step 5: Split Into Atomic Commits

Each commit should address one concern so it can be reviewed and reverted independently.

```bash
# ❌ WRONG - multiple concerns
git commit -m "feat: 認証追加とUI改善とテスト追加"

# ✅ CORRECT - split into focused commits
git commit -m "feat: 認証機能を追加"
git commit -m "refactor: UIレイアウトを改善"
git commit -m "test: 認証フローのテストを追加"
```

Use when reviewers need to verify changes incrementally or you want safe rollbacks.

### Step 6: Add Body with Why

Explain "why" in the commit body so future readers understand the decision, not just the diff.

```bash
git commit -m "fix: APIタイムアウトを10s→30sに変更

- 大量データ処理で10sでは不足していたため
- 監視で504エラーが増加していたため
Why: SLA達成率が低下していたため"
```

Use when a change might be questioned later or you need to preserve decision context.

### Step 7: Run Pre-Commit Checks

Review your diff and run tests before committing to keep history clean.

```bash
git diff
git status
npm test
git commit -m "feat: ..."
```

```yaml
# .commitlintrc.yml
rules:
  type-enum: [2, "always", ["feat","fix","docs","test","refactor","chore"]]
```

Use before pushing a branch to open a PR or when onboarding new contributors.

### Step 8: Amend and Rebase Safely

Rewrite history only before it is shared. After pushing, prefer a new commit.

```bash
# Before push: amend or interactive rebase
git commit --amend -m "fix: 正しいメッセージ"
git rebase -i HEAD~3

# After push: add a new commit instead
git commit -m "fix: 補足修正"
```

Use when a commit needs cleanup before PR or when you want to keep shared branches stable.

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

- [ ] Confirm on feature branch (not main)
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
