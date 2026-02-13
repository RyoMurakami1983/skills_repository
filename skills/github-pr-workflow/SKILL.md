---
name: github-pr-workflow
description: PR workflow from branch to merge and main sync. Use when standardizing GitHub Flow.
author: RyoMurakami1983
tags: [github, pull-requests, workflow, git, collaboration]
invocable: false
version: 1.0.0
---

# GitHub PR Workflow

A repeatable Pull Request workflow: branch, push, review, merge, and sync main safely.

**Pull Request (PR)**: A reviewed change proposal in GitHub.
**Branch Protection**: Repository rules that block unsafe merges or direct pushes.
**Continuous Integration (CI)**: Automated checks that run on pull requests.

## When to Use This Skill

Use this skill when:
- Standardizing PR flow across multiple repositories and teams with shared ownership
- Creating PRs with consistent titles, bodies, and issue links for traceability
- Enforcing review and continuous integration (CI) checks before merge to main
- Closing issues automatically on merge to keep planning boards up to date
- Syncing local main after reviewers merge to avoid working on stale history
- Handling hotfixes without bypassing protections or skipping required approvals

## Related Skills

- **`git-commit-practices`** - Commit formatting and atomic changes
- **`git-initial-setup`** - Branch protection defaults
- **`github-issue-intake`** - Issue creation and triage

---

## Dependencies

- Git 2.30+
- GitHub repository access
- GitHub CLI (gh) for CLI workflow (optional)

---

## Core Principles

1. **Branch First** (基礎と型) - Work stays off main until reviewed; the branch-first pattern is the foundation every PR builds on
2. **Traceability** (成長の複利) - Link PRs to issues so future developers learn why changes were made
3. **Review Gates** (ニュートラル) - Approvals and CI checks protect main with unbiased quality standards
4. **Clean Main** (継続は力) - Merge only verified changes; steady discipline keeps the codebase healthy
5. **Fast Sync** (温故知新) - Update local main after merge to build on the latest shared history

---

## Workflow: Ship via Pull Request

### Step 1: Create Feature Branch

Branch from the latest main before starting work. Use descriptive prefixes (`feature/`, `fix/`, `docs/`) with the issue number for traceability.

```bash
git checkout main
git pull --ff-only
git checkout -b feature/issue-123
git push -u origin feature/issue-123
```

Use when multiple developers collaborate on the same repository or when branch protection blocks direct pushes to main.

### Step 2: Open PR with Clear Context

Create a PR with an action-oriented title and a body that gives reviewers the full picture. Include Summary, Why, Testing, and linked issues.

```bash
gh pr create --title "feat: 支払い画面を改善" --body "## Summary
Redesigned payment form layout.

## Why
Current layout causes 15% drop-off at checkout.

## Testing
Manual test on staging.

## Related
Closes #123"
```

Use when reviewers need context quickly and you want consistent PR content across the team.

### Step 3: Pass Review and CI Gates

Require approvals and passing CI checks before merging. Configure branch protection to enforce these gates automatically.

```yaml
# .github/workflows/ci.yml
name: ci
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

Use when main must stay deployable and you need audit-ready review evidence.

### Step 4: Link Issues with Closing Keywords

Add closing keywords in the PR body so issues are auto-closed on merge. Use `Closes` for resolved issues and `Refs` for related context.

```markdown
## Related
Closes #123
Refs #130
```

Use when work originates from an issue and you need end-to-end traceability from issue to merged code.

### Step 5: Choose Merge Strategy

Select the merge strategy that matches your repository policy.

| Strategy | Use When | Result |
|----------|----------|--------|
| Squash | Small PRs | Single commit |
| Merge | Preserve history | Full commits |
| Rebase | Linear history | No merge commit |

Use when you need consistent history patterns or compliance requires a specific merge type.

### Step 6: Sync and Clean Up

After merge, sync your local main and delete the merged branch to keep your workspace clean.

```bash
git checkout main
git pull --ff-only
git branch -d feature/issue-123
git push origin --delete feature/issue-123
```

Use after every merged PR to avoid working on stale history.

### Step 7: Handle Hotfixes

Create a hotfix branch for urgent production fixes. Follow the same PR process — never bypass branch protection.

```bash
git checkout main
git pull --ff-only
git checkout -b hotfix/issue-999
# Fix, commit, push, then open PR as usual
git push -u origin hotfix/issue-999
```

Use when production is down but branch protections must remain intact.

---

## Best Practices

- Use action-oriented PR titles for quick scanning
- Define required testing notes in the PR template
- Apply closing keywords to keep issues updated
- Avoid merging without approvals or passing CI
- Sync main locally after every merge

---

## Common Pitfalls

1. **Skipping CI checks**
   Fix: Require CI in branch protection.

2. **Merging without review**
   Fix: Require approvals and code owners.

3. **Forgetting main sync**
   Fix: Pull main with `--ff-only` after every merge.

---

## Anti-Patterns

- Direct push to main without branch protection
- Merging with failed checks
- Leaving merged branches undeleted

---

## Quick Reference

### PR Flow Checklist

- [ ] Branch from latest main
- [ ] Push branch and open PR
- [ ] Add `Closes #` keywords
- [ ] Pass CI and get approvals
- [ ] Merge via policy
- [ ] Pull main and delete branch

### Merge Decision Table

| Situation | Merge Type | Reason |
|-----------|------------|--------|
| Small feature | Squash | Reduce noise |
| Release branch | Merge | Preserve commits |
| Linear history required | Rebase | Avoid merge commit |

---

## FAQ

**Q: Should every PR close an issue?**
A: Use closing keywords when work is issue-driven.

**Q: Can I merge if CI fails?**
A: No. Fix CI or document the exception.

**Q: When should I delete branches?**
A: After merge to keep remotes clean.

---

## Resources

- https://docs.github.com/en/pull-requests
- https://cli.github.com/manual/gh_pr_create
