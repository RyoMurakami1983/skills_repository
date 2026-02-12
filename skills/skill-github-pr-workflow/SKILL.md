---
name: skill-github-pr-workflow
description: PR workflow from branch to merge and main sync. Use when standardizing GitHub Flow.
author: RyoMurakami1983
tags: [github, pull-requests, workflow, git, collaboration]
invocable: false
version: 1.0.0
---

# GitHub PR Workflow

A repeatable Pull Request (PR) workflow: branch, push, review, merge, and sync main safely.

**Pull Request (PR)**: A reviewed change proposal in GitHub.
**Branch Protection**: Repository rules that block unsafe merges or direct pushes.
**Continuous Integration (CI)**: Automated checks that run on pull requests.

Progression: Simple → Intermediate → Advanced examples improve clarity because each step adds safeguards.
Reason: More safeguards reduce rework and protect main from risky merges.

## When to Use This Skill

Use this skill when:
- Standardizing PR flow across multiple repositories and teams with shared ownership
- Creating PRs with consistent titles, bodies, and issue links for traceability
- Enforcing review and continuous integration (CI) checks before merge to main
- Closing issues automatically on merge to keep planning boards up to date
- Syncing local main after reviewers merge to avoid working on stale history
- Handling hotfixes without bypassing protections or skipping required approvals

## Related Skills

- **`skill-git-commit-practices`** - Commit formatting and atomic changes
- **`skill-git-review-standards`** - Review quality and PR sizing
- **`skill-git-initial-setup`** - Branch protection defaults
- **`skill-issue-intake`** - Issue creation and triage

---

## Dependencies

- Git 2.30+
- GitHub repository access
- GitHub CLI (gh) for CLI workflow (optional)

---

## Core Principles

1. **Branch First** - Work stays off main until reviewed
2. **Traceability** - Link PRs to issues and evidence
3. **Review Gates** - Approvals and CI checks protect main
4. **Clean Main** - Merge only verified changes
5. **Fast Sync** - Update local main after merge

---

## Pattern 1: Branch and Push Workflow

### Overview

Create a feature branch from main and push it before opening a PR.

### Basic Example

```bash
# ✅ CORRECT
git checkout main
git pull --ff-only
git checkout -b feature/issue-123
git push -u origin feature/issue-123

# ❌ WRONG
git checkout main
git push origin main
```

### Intermediate Example

- Use prefixes like `feature/`, `fix/`, `docs/`
- Include issue number in the branch name

### Advanced Example

- Protect main with branch rules before creating branches

### When to Use

- When you want a repeatable PR workflow
- When multiple developers collaborate on the same repo

---

## Pattern 2: Create a PR with Clear Context

### Overview

Create a PR with a clear title, body, and linked issue.

### Basic Example

```bash
# ✅ CORRECT
gh pr create --title "feat: 支払い画面を改善" --body "Closes #123"

# ❌ WRONG
gh pr create --title "update" --body ""
```

### Intermediate Example

```markdown
## Summary
## Why
## Testing
## Related
Closes #123

Why: Give reviewers context and reduce re-review cycles.
```

### Advanced Example

```bash
# Fail fast if PR creation fails
if ! gh pr create --title "feat: 支払い画面を改善" --body "Closes #123"; then
  echo "PR creation failed"; exit 1
fi
```

### When to Use

- When you want consistent PR content
- When reviewers need context quickly

---

## Pattern 3: Review Gates and CI Checks

### Overview

Require approvals and CI checks before merging.

### Basic Example

CI configuration file example:

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

### Intermediate Example

- Require 1-2 approvals
- Require conversations to be resolved

### Advanced Example

```csharp
// ✅ CORRECT - Register a PR gate
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<PullRequestGate>();
```

### When to Use

- When main must stay deployable
- When you need audit-ready review evidence

---

## Pattern 4: Link Issues with Closing Keywords

### Overview

Use closing keywords so issues are auto-closed on merge.

### Basic Example

```markdown
## Related
Closes #123
```

### Intermediate Example

```markdown
## Related
Closes #123
Refs #130

Why: Keep issue traceability visible in the PR body.
```

### Advanced Example

```markdown
## Related
Fixes owner/repo#123
Relates-to owner/repo#130
```

### When to Use

- When work starts from an issue
- When you need end-to-end traceability

---

## Pattern 5: Merge Strategy Selection

### Overview

Choose the merge strategy that fits your repo policy.

### Basic Example

| Strategy | Use When | Result |
|----------|----------|--------|
| Squash | Small PRs | Single commit |
| Merge | Preserve history | Full commits |
| Rebase | Linear history | No merge commit |

### Intermediate Example

- Use squash for feature branches
- Use merge for release branches

### Advanced Example

- Enforce linear history in branch protection settings

### When to Use

- When you need consistent history patterns
- When compliance requires specific merge types

---

## Pattern 6: Post-Merge Sync and Cleanup

### Overview

Sync main locally and remove branches after merge.

### Basic Example

```bash
# ✅ CORRECT
git checkout main
git pull --ff-only
git branch -d feature/issue-123

# ❌ WRONG
git checkout main
git pull
```

### Intermediate Example

```bash
# Delete remote branch
git push origin --delete feature/issue-123
```

### Advanced Example

- Update changelog or release notes after merge

### When to Use

- After reviewers merge your PR
- When you want main to stay current locally

---

## Pattern 7: Hotfix Workflow

### Overview

Handle urgent fixes without bypassing protection.

### Basic Example

```bash
# ✅ CORRECT
git checkout -b hotfix/issue-999
```

### Intermediate Example

```bash
# Cherry-pick into release branch
git cherry-pick <commit>
```

### Advanced Example

```python
# ✅ CORRECT - record hotfix evidence
from pathlib import Path

Path("hotfix.txt").write_text("hotfix applied", encoding="utf-8")
```

### When to Use

- When production is down
- When main protections must remain intact

---

## Best Practices

- Use action-oriented PR titles for quick scanning
- Define required testing notes in the PR template
- Apply closing keywords to keep issues updated
- Avoid merging without approvals or passing CI
- Consider syncing main after every merge

---

## Common Pitfalls

1. **Skipping CI checks**  
Fix: Require CI in branch protection.

2. **Merging without review**  
Fix: Require approvals and code owners.

3. **Forgetting main sync**  
Fix: Pull main after merge.

---

## Anti-Patterns

- Direct push to main without branch protection architecture
- Merging failed checks
- Leaving merged branches undeleted

---

## Quick Reference

### PR Flow Checklist

- [ ] Branch from latest main
- [ ] Push branch and open PR
- [ ] Add `Closes #` keywords
- [ ] Pass CI and get approvals
- [ ] Merge via policy
- [ ] Pull main after merge

### Merge Decision Table

| Situation | Merge Type | Decision |
|-----------|------------|----------|
| Small feature | Squash | Decision: reduce noise |
| Release branch | Merge | Decision: preserve commits |
| Linear history required | Rebase | Decision: avoid merge commit |

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
