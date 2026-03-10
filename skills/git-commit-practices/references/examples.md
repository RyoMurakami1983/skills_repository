# Git Commit Practices — Examples

## Conventional Commit Examples

### Feature commits
```
feat: add user authentication with JWT
feat(api): implement rate limiting for public endpoints
feat!: redesign commit message format (BREAKING CHANGE)
```

### Fix commits
```
fix: resolve null pointer in user session handler
fix(ui): correct button alignment on mobile viewport
fix!: change default branch from master to main
```

### Chore / maintenance
```
chore: update dependencies to latest stable versions
chore(ci): switch from CircleCI to GitHub Actions
docs: add API endpoint documentation
refactor: extract validation logic to separate module
```

## Japanese Subject Examples (optional convention)

| English intent | Japanese subject |
|----------------|-----------------|
| Add feature X | X機能を追加 |
| Fix bug in Y | Yのバグを修正 |
| Update docs for Z | ZのドキュメントをUpdate |
| Refactor module A | モジュールAをリファクタリング |

## Atomic Commit Checklist

Before committing, verify:
- [ ] This commit does **one logical thing** only
- [ ] If reverted, no other unrelated feature breaks
- [ ] The commit message explains WHY, not just what changed
- [ ] Related tests are included in this same commit
- [ ] No debug code, console.logs, or TODO comments left in

## Commit Size Guidelines

| Lines changed | Assessment |
|---------------|------------|
| 1-50 | Ideal atomic commit |
| 51-200 | Acceptable, verify single purpose |
| 201-500 | Consider splitting |
| 500+ | Almost always should be split |

## Bad vs Good Examples

❌ Bad: `fix stuff`
✅ Good: `fix: prevent double-submission on payment form`

❌ Bad: `WIP`
✅ Good: `feat(auth): add password reset email flow (incomplete — reset endpoint pending)`

❌ Bad: one giant commit with 20 unrelated changes
✅ Good: one commit per logical unit of work
