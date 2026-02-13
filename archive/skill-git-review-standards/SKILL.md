---
name: skill-git-review-standards
description: Review standards for PR quality, size, and communication.
author: RyoMurakami1983
tags: [github, code-review, workflow, quality, collaboration]
invocable: false
version: 1.0.0
---

# Git Review Standards

Define clear review goals, size limits, and communication rules for reliable PR reviews.

**Service Level Agreement (SLA)**: Expected time window for completing reviews.
**LGTM (Looks Good To Me)**: Informal approval that still needs evidence.
**CODEOWNERS**: A GitHub file that assigns review ownership.

Progression: Simple → Intermediate → Advanced examples improve consistency because each stage adds rigor.
Reason: The added rigor reduces review ambiguity.

## When to Use This Skill

Use this skill when:
- Standardizing review expectations across multiple teams and shared repositories
- Defining PR size limits so reviews stay focused and finish on time
- Reducing emotional feedback by using explicit tone and blocker labels
- Improving approval latency when reviews stall or are skipped under pressure
- Creating a repeatable review checklist for onboarding new reviewers quickly
- Keeping review quality high as team size grows and ownership spreads

## Related Skills

- **`skill-github-pr-workflow`** - PR flow and merge policies
- **`skill-git-commit-practices`** - Commit formatting and atomic changes
- **`skill-git-history-learning`** - Learning from commit history

---

## Dependencies

- GitHub review permissions
- CODEOWNERS configuration (optional)

---

## Core Principles

1. **Quality First** - Reviews protect users and main
2. **Small PRs** - Smaller PRs improve review accuracy
3. **Respectful Feedback** - Tone affects team velocity
4. **Evidence-Based** - Check tests, logs, and risk
5. **Shared Ownership** - Everyone reviews and learns

---

## Pattern 1: Define Review Objectives

### Overview

Clarify what reviewers must check and what they can skip.

### Basic Example

```text
Review goals:
- Correctness
- Security
- Maintainability
- Tests
```

### Intermediate Example

- Add a team review checklist
- Use labels like `needs-review`

### Advanced Example

- Assign specialists via CODEOWNERS

### When to Use

- When reviews are inconsistent
- When critical areas are missed

---

## Pattern 2: PR Size Standards

### Overview

Set clear size limits to keep reviews efficient.

### Basic Example

| Size | Diff | Expectation |
|------|------|-------------|
| S | <200 lines | Review in 1 day |
| M | <500 lines | Review in 2 days |
| L | 500+ lines | Split PR |

Why: Smaller PRs improve review accuracy and reduce re-review time.

```text
# ✅ CORRECT
Split a 700-line change into feature and refactor PRs.

# ❌ WRONG
Ship a 900-line PR with mixed concerns.
```

### Intermediate Example

- Require PR splitting for L size
- Use `size/L` labels

### Advanced Example

- Block merges over size limits unless approved by lead

### When to Use

- When reviews are delayed
- When PRs are too large to understand

---

## Pattern 3: Review Checklist Template

### Overview

Use a checklist to keep reviews consistent.

### Basic Example

```markdown
## Review Checklist
- [ ] Tests added
- [ ] Error handling
- [ ] Logs included
- [ ] Security impact reviewed
```

### Intermediate Example

```text
Focus: data loss, performance, and API changes
```

### Advanced Example

```csharp
// ✅ CORRECT - register review checklist
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<ReviewChecklist>();
```

### When to Use

- When reviewers miss required checks
- When onboarding new reviewers

---

## Pattern 4: Feedback Style Rules

### Overview

Use consistent and respectful feedback patterns.

### Basic Example

```text
# ✅ CORRECT
"Could you add a test for the null case?"

# ❌ WRONG
"Why did you forget the test?"
```

### Intermediate Example

- Use "suggestion" vs "blocker" labels
- Explain the reason behind requests

### Advanced Example

- Use shared templates for blocking feedback

### When to Use

- When review comments cause friction
- When feedback is unclear or emotional

---

## Pattern 5: Responding to Feedback

### Overview

Address feedback with clear follow-up and re-request review.

### Basic Example

```bash
# ✅ CORRECT - run tests before re-request
if ! npm test; then
  echo "Tests failed"; exit 1
fi
```

```text
# ❌ WRONG
"Please re-review" without test evidence.
```

Why: Evidence-first responses prevent back-and-forth cycles.

### Intermediate Example

- Reply to each blocking comment
- Mark conversations as resolved after fixes

### Advanced Example

- Summarize changes in a follow-up comment

### When to Use

- When rework is required
- When reviewers need visibility on fixes

---

## Pattern 6: Approvals and SLA

### Overview

Define how many approvals are needed and expected timing.

### Basic Example

```text
# ✅ CORRECT
- 1 approval for normal PRs
- 2 approvals for risky changes

# ❌ WRONG
- 0 approvals for risky changes
```

Why: Explicit approval rules keep responsibility visible.

### Intermediate Example

- Define 1-2 day review SLA
- Use rotating review duty

### Advanced Example

- Escalate overdue reviews to leads

### When to Use

- When reviews stall
- When approvals are inconsistent

---

## Pattern 7: Detect Review Anti-Patterns

### Overview

Stop rubber-stamp reviews and drive-by approvals.

### Basic Example

```text
Anti-patterns:
- "LGTM" without reading
- Approving without tests
```

### Intermediate Example

- Require review notes for complex PRs

### Advanced Example

- Audit approvals in postmortems

### When to Use

- When production bugs slip through reviews
- When review quality is low

---

## Best Practices

- Keep PRs small and reviewable
- Focus on risk, not style
- Require evidence (tests/logs)
- Keep tone respectful

---

## Common Pitfalls

1. **Reviewing too late**  
Fix: Set a review SLA.

2. **Commenting without context**  
Fix: Explain why a change is needed.

3. **Rubber-stamp approvals**  
Fix: Require review notes for risky PRs.

---

## Anti-Patterns

- Approving without reading or breaking review architecture
- Ignoring failing tests
- Debating style over correctness

---

## Quick Reference

### Review Checklist

- [ ] Understand purpose and scope
- [ ] Validate tests and error handling
- [ ] Check security impact
- [ ] Confirm PR size is reasonable
- [ ] Approve only with evidence

### Decision Table

| Situation | Action | Decision |
|-----------|--------|----------|
| Large PR | Split | Decision: reduce review risk |
| Risky change | 2 approvals | Decision: add safeguards |
| No tests | Block | Decision: require evidence |

---

## FAQ

**Q: How many approvals should we require?**  
A: Start with 1 for normal PRs and 2 for risky changes.

**Q: What if a reviewer is slow?**  
A: Escalate after the SLA or rotate duty.

**Q: Do we comment on style?**  
A: Only if it affects readability or reliability.

---

## Resources

- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
