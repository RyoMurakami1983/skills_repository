---
name: github
description: >
  Route broad GitHub requests to the right existing GitHub workflow skill.
  Use when the user says "GitHub", "プルリクして", "PRレビュー待機して",
  "レビュー対応して", or "Issue登録して" without naming the exact skill yet.
---

# GitHub Entry Skill

Use this skill as a thin entry point when the user clearly needs GitHub delivery help but the best existing skill is still ambiguous. Why: daily delivery requests often arrive as short natural phrases before the user names whether they need PR creation, review response, issue intake, or a full issue session workflow.

This skill does not replace concrete skills such as `github-pr-workflow` or `github-pr-review-response`. Its job is to route quickly, then hand off to the canonical workflow.

## When to Use This Skill

Use this skill when:
- Interpreting a broad GitHub request before the right concrete skill is obvious
- Routing "プルリクして" into the canonical PR creation and review-wait flow
- Routing "PRレビュー待機して" or "レビュー対応して" into the right review-phase skill
- Mapping "Issue登録して" or vague backlog-capture requests to the issue intake workflow
- Directing a greeting-driven issue execution session into the end-to-end issue autopilot
- Redirecting "コミットして" to `git-commit-practices` when clean atomic commits are needed before PR work

## Decision Table

| Your intent | Route | What to do |
| --- | --- | --- |
| Open a PR, link an issue, or enter review waiting | `github-pr-workflow` | Use the canonical PR workflow from branch/state detection through review waiting. |
| Respond to new PR review comments or request re-review | `github-pr-review-response` | Enter only when there is a real review signal that needs action. |
| Capture deferred work or create a follow-up issue | `github-issue-intake` | Turn scope expansion or vague work into a structured GitHub issue. |
| Run one issue end-to-end in the current session | `session-issue-autopilot` | Use the session orchestrator when the user wants guided issue execution through PR flow. |
| Standardize labels or quality gates at the repo level | `github-repo-label-setup`, `github-quality-gate-setup` | Treat these as repository bootstrap or hardening concerns, not PR concerns. |
| Prepare commits before PR work | `git-commit-practices` | Interpret "コミットして" as a request for atomic commits by default. |

## Related Skills

- **`github-pr-workflow`** — Primary route for PR creation, issue linkage, and review waiting
- **`github-pr-review-response`** — Primary route for review feedback handling
- **`github-issue-intake`** — Primary route for issue capture and defer/triage work
- **`session-issue-autopilot`** — End-to-end session wrapper for issue execution
- **`git-commit-practices`** — Upstream commit hygiene route when PR-ready history is not prepared yet

## Routing Notes

- Prefer direct skill invocation once the user's intent is clear; this entry skill exists only for early ambiguity.
- Treat "コミットして" as a `git-commit-practices` route with atomic commit expectations, not as a generic GitHub action.
- Keep merge decisions human-in-the-loop; this skill should route to the right workflow, not blur merge ownership.

## Pitfalls

- **Staying in the router too long**: once the user's real concern is clear, switch to the concrete skill instead of repeating a category explanation.
- **Using `github` as a mega-workflow**: this is an entry skill, not a replacement for `github-pr-workflow`, `github-pr-review-response`, or `github-issue-intake`.
- **Forgetting commit hygiene**: if the branch is not clean enough for review, route to `git-commit-practices` first and split into atomic commits before PR creation.
