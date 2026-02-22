---
name: github-pr-review-response
description: "Systematic workflow for responding to PR review feedback. Use when addressing reviewer comments with fixes and replies."
metadata:
  author: RyoMurakami1983
  license: MIT
  compatibility:
    platforms: [windows, macos, linux]
    tools: [github-cli, git]
---

# GitHub PR Review Response

A single-workflow skill for systematically responding to PR (Pull Request) review feedback — from analysis through fix implementation to reviewer reply.

**Review Response**: The structured process of reading, categorizing, fixing, and replying to PR review comments.

## When to Use This Skill

Use this skill when:

- Receiving review comments on a pull request that require code changes or replies
- Categorizing review feedback by severity to decide fix order and priority level
- Implementing fixes for critical bugs or security issues found during code review
- Creating a structured response plan for multiple review comments on a single PR
- Replying to reviewer questions with clear explanations of why a design was chosen
- Requesting re-review after all review comments have been addressed with commits

> **Scope**: This skill covers review comment triage through re-review request. Merge strategy, CI gates, and post-merge sync are out of scope.

## Related Skills

- **`github-pr-workflow`** — PR creation and issue linking (upstream workflow)
- **`git-commit-practices`** — Commit formatting and atomic changes (delegated from Step 5)
- **`github-issue-intake`** — Creating follow-up issues for deferred review items

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — verify with `gh auth status`
- GitHub repository with push access
- An open PR with review comments to address

---

## Core Principles

1. **Actionable First** (基礎と型) — Address review comments with code, not just words
2. **Traceability** (成長の複利) — Every fix links back to the review comment that triggered it
3. **Quality Maintenance** (継続は力) — Fixes must not regress existing quality or break tests
4. **Respectful Dialogue** (ニュートラル) — Reply to every comment, even if you disagree, with reason
5. **Systematic Triage** (温故知新) — Categorize before acting to avoid fixing low-priority items first

---

## Decision Table

How to categorize review comments and decide the correct action:

| Comment Type | Action | Priority | Example |
|---|---|---|---|
| Bug/Security | Must fix before merge | Critical | "This has an SQL injection vulnerability" |
| Logic Error | Must fix before merge | Critical | "This condition is inverted" |
| Missing Feature | Fix or create follow-up issue | High | "Error handling is missing here" |
| Improvement | Fix if straightforward | Medium | "Consider using a guard clause" |
| Style/Formatting | Fix unless team disagrees | Low | "Inconsistent indentation" |
| Question/Clarification | Reply with explanation | Low | "Why did you choose this approach?" |

Use this table in Step 1 to classify each comment before writing any code.

---

## Workflow: PR Review Response

### Step 1: Receive and Categorize Review Comments

Read all review comments on the PR. Classify each comment using the Decision Table above.

```bash
# Fetch all review comments for the current PR
gh pr view --json reviews,reviewRequests --jq '.reviews'

# List review threads with resolution status
gh pr view --json reviewThreads --jq '.reviewThreads[] | {path: .path, body: .comments[0].body, isResolved: .isResolved}'
```

```powershell
# PowerShell: list review comments
gh pr view --json reviews,reviewRequests --jq '.reviews'
```

Create a categorized list:

```markdown
## Review Comment Analysis
| # | File | Comment | Type | Priority |
|---|------|---------|------|----------|
| 1 | src/auth.py | Missing input validation | Bug | Critical |
| 2 | src/utils.py | Consider guard clause | Improvement | Medium |
| 3 | README.md | Typo in heading | Style | Low |
```

Use when you first open a PR that has received review feedback.

> **Values**: 温故知新 / 基礎と型

### Step 2: Create Response Plan

Document the analysis in plan.md with a problem table, fix strategy, and task list. This prevents ad-hoc fixes and ensures nothing is missed.

```markdown
# PR Review Response Plan

## Problem Table
| # | Comment | Category | Fix Strategy | Estimated Effort |
|---|---------|----------|-------------|-----------------|
| 1 | SQL injection in query | Critical/Bug | Use parameterized queries | 15 min |
| 2 | Guard clause suggestion | Medium/Improvement | Refactor to early return | 5 min |
| 3 | Missing error handling | High/Missing Feature | Add try-catch with logging | 10 min |

## Task Order
1. Fix #1 — Critical bug (SQL injection)
2. Fix #3 — High priority (error handling)
3. Fix #2 — Medium improvement (guard clause)

## Out of Scope (create follow-up issues)
- Performance optimization suggested in review (not blocking merge)
```

Use when multiple review comments need coordination to avoid conflicts.

> **Values**: 基礎と型 / 余白の設計

### Step 3: Implement Fixes

Address critical issues first, then work down through high and medium priority items. Each fix should be a focused, atomic change.

```bash
# Fix critical issues first — one logical change at a time
# Why: atomic fixes are easier to review and revert if needed

# Example: fix SQL injection (Critical)
git add src/auth.py
git commit -m "fix: use parameterized queries to prevent SQL injection

Addresses review comment on src/auth.py regarding
unsafe string interpolation in database queries."
```

```powershell
# PowerShell: same git commands apply
git add src/auth.py
git commit -m "fix: use parameterized queries to prevent SQL injection"
```

✅ **Do**: Fix one issue per commit for clear traceability
❌ **Don't**: Bundle all review fixes into a single large commit

Use when your response plan is ready and you begin writing code fixes.

> **Values**: 基礎と型 / 成長の複利

### Step 4: Run Quality Checks

Run linters, tests, and validation scripts to ensure fixes do not regress existing quality. Never push without verifying.

```bash
# Run project tests to confirm no regression
# Why: review fixes can introduce new bugs if untested
npm test        # or: pytest, dotnet test, go test ./...

# Run linter to catch style issues
npm run lint    # or: flake8, dotnet format --verify-no-changes

# If this repo has a skill validator, run it
uv run python scripts/validate_skill.py path/to/SKILL.md
```

```powershell
# PowerShell: run tests and linter
npm test
npm run lint
```

If any check fails, fix the regression before proceeding to Step 5.

Use when all planned fixes are implemented and you need to verify correctness.

> **Values**: 継続は力 / 基礎と型

### Step 5: Commit with Conventional Format

Use Conventional Commits format. Reference the review context in the commit body so future developers understand why the change was made.

```bash
# Choose the correct commit type based on what changed
# fix:      bug fix or security fix from review
# refactor: code improvement suggested in review
# docs:     documentation fix from review
# style:    formatting fix from review

git commit -m "fix: add input validation for user email

Review feedback: reviewer flagged missing validation
on the email field in the registration form.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

| Commit Type | When to Use |
|---|---|
| `fix:` | Bug fix or security issue from review |
| `refactor:` | Code structure improvement from review |
| `docs:` | Documentation correction from review |
| `style:` | Formatting or style fix from review |

Use when each fix is complete and tests pass, ready to be committed.

> **Values**: 成長の複利 / 継続は力

### Step 6: Push and Reply to Comments

Push all fix commits, then reply to each review comment explaining what was done and why.

```bash
# Push fix commits to the PR branch
git push origin HEAD

# Add a general review comment summarizing changes
gh pr review --comment --body "All review comments addressed. See individual commits for details."

# For threaded replies to specific review comments, use GitHub web UI
# or the API: gh api repos/OWNER/REPO/pulls/comments/COMMENT_ID/replies -f body="Fixed in abc1234"
```

```powershell
# PowerShell: push and add review comment
git push origin HEAD

gh pr review --comment --body "All review comments addressed. See individual commits for details."
```

Reply guidelines:

- ✅ **Do**: Reference the specific commit that addresses the comment
- ✅ **Do**: Explain why you chose a particular fix approach
- ❌ **Don't**: Reply with just "Fixed" — explain what changed and why
- ❌ **Don't**: Ignore comments you disagree with — reply with your reasoning instead

Use when all commits are pushed and you need to close the feedback loop.

> **Values**: ニュートラル / 成長の複利

### Step 7: Request Re-review

After all comments are addressed and pushed, request a re-review from the original reviewer.

```bash
# Request re-review from the reviewer
gh pr edit --add-reviewer reviewer-username

# Optionally leave a summary comment
gh pr comment --body "All review comments addressed:
- Fixed SQL injection (commit abc1234)
- Added error handling (commit def5678)
- Refactored to guard clause (commit ghi9012)

Ready for re-review. Thank you for the feedback!"
```

```powershell
# PowerShell: request re-review
gh pr edit --add-reviewer reviewer-username

gh pr comment --body "All review comments addressed. Ready for re-review."
```

Use when every review comment has a fix commit or a reply, and all tests pass.

> **Values**: 成長の複利 / ニュートラル

---

## Best Practices

- Implement fixes in priority order: Critical → High → Medium → Low
- Use one commit per review comment for clear traceability
- Use `fix:` or `refactor:` commit types to distinguish bug fixes from improvements
- Avoid force-pushing after review — it hides review conversation history
- Create follow-up issues for suggestions that are out of scope for the current PR
- Use `gh pr review --comment` to reply directly in the review thread

---

## Common Pitfalls

1. **Fixing everything in one large commit**
   Fix: Use atomic commits — one commit per review comment for clear code history.

2. **Ignoring low-priority comments without replying**
   Fix: Reply to every comment, even to acknowledge and defer to a follow-up issue.

3. **Pushing fixes without running tests first**
   Fix: Always run the full test suite and linter before pushing (Step 4 method).

4. **Replying "Fixed" without context**
   Fix: Reference the commit hash and explain the fix approach in your reply.

---

## Anti-Patterns

- Pushing directly to main to bypass the review process — violates branch-first design
- Bundling unrelated changes with review fixes — breaks atomic commit structure
- Dismissing reviewer feedback without explanation — undermines team trust
- Force-pushing to hide review conversation history — destroys traceability

---

## Quick Reference

### Review Response Checklist

| Step | Action | Verify |
|------|--------|--------|
| 1 | Read and categorize all review comments | Decision Table applied |
| 2 | Create response plan in plan.md | All comments tracked |
| 3 | Implement fixes (Critical → Low) | One fix per commit |
| 4 | Run tests and linters | All checks pass |
| 5 | Commit with Conventional format | Review context in body |
| 6 | Push and reply to each comment | Every comment answered |
| 7 | Request re-review | Reviewer notified |

### Reply Template

```markdown
Fixed in commit `<hash>`.

**What changed**: <brief description of the fix>
**Why this approach**: <reasoning behind the chosen solution>
```

---

## FAQ

**Q: What if I disagree with a review comment?**
A: Reply with your reasoning. Explain why you chose a different approach. Never ignore the comment.

**Q: Should I create a new branch for review fixes?**
A: No. Push fixes to the same PR branch. This keeps the review conversation intact.

**Q: What if a suggestion is out of scope?**
A: Acknowledge the comment, create a follow-up issue via `github-issue-intake`, and link it in your reply.

**Q: Does this skill handle the initial PR creation?**
A: No. Use `github-pr-workflow` to create the PR. This skill starts after review comments arrive.

---

## Resources

- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests
- https://cli.github.com/manual/gh_pr_review
- https://www.conventionalcommits.org/
