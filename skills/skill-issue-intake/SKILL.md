---
name: skill-issue-intake
description: Capture deferred work as actionable GitHub issues. Use when triaging scope.
author: RyoMurakami1983
tags: [github, issues, triage, workflow, documentation]
invocable: false
version: 1.0.0
---

# Issue Intake

Turn out-of-scope bugs or improvements into actionable GitHub issues with consistent structure, ownership, and priority.

## When to Use This Skill

Use this skill when:
- Capturing out-of-scope bugs discovered during a Pull Request (PR) review
- Deferring non-critical fixes to a later sprint or milestone
- Standardizing issue titles, labels, and priority across teams
- Recording reproducible steps for intermittent production failures
- Converting support requests into trackable engineering work
- Handing off follow-up tasks to another owner or team

## Related Skills

- **`skill-git-commit-practices`** - Commit workflow and conventions
- **`skill-github-pr-workflow`** - PR workflow and merge policies
- **`skill-git-review-standards`** - Review quality and PR sizing
- **`skill-git-initial-setup`** - Default repo protections for new repos
- **`skill-revision-guide`** - Revision and change log practices
- **`skill-quality-validation`** - Validate documentation quality

---

## Dependencies

- GitHub account with repo access
- GitHub CLI (gh) for CLI workflow (optional)
- Team label/priority taxonomy

---

## Core Principles

1. **Actionable First** - Every issue includes clear next steps (基礎と型)
2. **Scope Separation** - Track later work without blocking now
3. **Traceability** - Link issues to PRs and evidence (成長の複利)
4. **Consistency** - Use standard labels, priorities, and templates
5. **Low Friction** - Capture fast to avoid forgotten work (継続は力)

---

## Pattern 1: Decide Fix Now vs File Issue

### Overview

Decide whether to fix immediately or capture the work as a tracked issue.

### Basic Example

| Question | If Yes | If No |
|----------|--------|-------|
| Breaks release or main? | Fix now | Create issue |
| Needs design discussion? | Create issue | Fix now |
| >30 minutes to resolve? | Create issue | Fix now |

```text
# ✅ CORRECT - File issue when out of scope
Issue: "Bug: CSV import fails on UTF-8 BOM"
Scope: Not required for current PR
Action: Create issue and continue

# ❌ WRONG - Hide in TODO
// TODO: fix later
```

### Intermediate Example

- Timebox quick fixes to 30 minutes
- If timebox is exceeded, stop and file an issue

### Advanced Example

| Impact | Effort | Decision |
|--------|--------|----------|
| High | High | Create issue + schedule |
| High | Low | Fix now |
| Low | High | Create issue |

### When to Use

- When you discover scope creep during a PR
- When a fix risks delaying the current release

**Why**: Separating scope keeps PRs focused and predictable.

---

## Pattern 2: Issue Title and Body Template

### Overview

Standardize titles and bodies so issues are searchable and actionable.

### Basic Example

```markdown
# ✅ CORRECT - Clear title
Title: "Bug: CSV import fails on UTF-8 BOM"

# ❌ WRONG - Vague title
Title: "Bug"
```

### Intermediate Example

```markdown
## Summary
## Steps to Reproduce
## Expected Result
## Actual Result
## Impact
```

### Advanced Example

```markdown
## Acceptance Criteria
- [ ] Repro steps documented
- [ ] Fix implemented
- [ ] Tests added
```

```yaml
# .github/ISSUE_TEMPLATE/bug.yml
name: Bug Report
description: Report a reproducible bug
body:
  - type: textarea
    id: repro
    attributes:
      label: Steps to Reproduce
      required: true
```

**Why**: Clear titles and structure reduce back-and-forth.

---

## Pattern 3: Labels and Priority Triage

### Overview

Apply consistent labels and priorities so work can be sorted and scheduled.

### Basic Example

```yaml
# ✅ CORRECT
labels: [bug, priority/P1, area/import]

# ❌ WRONG
labels: []
```

### Intermediate Example

| Priority | Meaning | SLA |
|----------|---------|-----|
| P0 | Production down | Same day |
| P1 | Major user impact | 1-3 days |
| P2 | Standard bug | 1-2 sprints |
| P3 | Minor/cleanup | Backlog |

### Advanced Example

- Add `type/bug`, `type/debt`, `type/feature`
- Add `status/triage`, `status/ready`, `status/blocked`

**Why**: Labels make issue queues sortable and predictable.

---

## Pattern 4: Repro Steps and Evidence

### Overview

Provide reproducible steps and evidence so the next owner can fix quickly.

### Basic Example

```markdown
## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import
3. Observe error in UI

## Expected
Import succeeds

## Actual
"Invalid encoding" error
```

### Intermediate Example

Attach evidence:
- Logs or screenshots
- Request/response IDs

### Advanced Example

```text
Log: 2026-02-12T12:03:11Z ERROR import failed (BOM detected)
```

**Why**: Repro steps reduce time wasted on guesswork.

---

## Pattern 5: GitHub CLI Issue Creation

### Overview

Use the GitHub CLI (command-line interface, CLI) for fast issue creation.

### Basic Example

```bash
# ✅ CORRECT
gh issue create --title "Bug: CSV import fails on UTF-8 BOM" --body "See repro steps"
```

### Intermediate Example

```bash
gh issue create \
  --title "Bug: CSV import fails on UTF-8 BOM" \
  --body-file issue.md \
  --label bug,priority/P1,area/import \
  --assignee @me
```

Why: Intermediate adds labels and ownership for faster triage.

### Advanced Example

```python
# ✅ CORRECT - Generate issue body file
import textwrap
from pathlib import Path

body = textwrap.dedent("""\
## Summary
CSV import fails on UTF-8 BOM.

## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import

## Expected
Import succeeds

## Actual
"Invalid encoding" error
""")

try:
    Path("issue.md").write_text(body, encoding="utf-8")
except OSError as exc:
    raise SystemExit(f"Failed to write issue body: {exc}")
```

```csharp
// ✅ CORRECT - Register an issue template service
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<IssueTemplateService>();
```

**Why**: Advanced automation reduces manual errors and keeps templates consistent.

---

## Pattern 6: GitHub Web UI Issue Creation

### Overview

Use the GitHub web interface when you need rich formatting or quick screenshots.

### Basic Example

1. Open repository → Issues → New issue
2. Select template
3. Fill required fields and submit

### Intermediate Example

- Add labels and milestone
- Assign an owner and reviewer

### Advanced Example

- Convert a PR comment into an issue reference
- Link the issue to a project board

**Why**: The UI is best for context-rich reports.

---

## Pattern 7: Link Issues to PRs and Close

### Overview

Ensure issues close automatically when the PR merges.

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
```

### Advanced Example

```markdown
## Related
Fixes owner/repo#123
Relates-to owner/repo#130
```

### When to Use

- When a PR directly resolves a tracked issue
- When you need full traceability across repos

**Why**: Auto-closing keeps the backlog accurate.

---

## Best Practices

- Use action verbs in titles (Fix, Add, Remove)
- Keep one issue per problem
- Add impact and priority before triage meetings
- Include repro steps or evidence whenever possible
- Link PRs with closing keywords
Use the template and add labels before assigning an owner.

---

## Common Pitfalls

- Writing vague titles like "Bug" or "Fix later"
- Skipping repro steps for intermittent failures
- Mixing multiple problems into one issue

Fix: Use the standard template and split issues by scope.
Fix: Always add repro steps or evidence links.
Fix: Add labels before assigning ownership.

---

## Anti-Patterns

- Using TODO comments instead of filing issues
- Creating issues without a clear next action
- Closing issues without documenting resolution

---

## FAQ

**Q: When should I file an issue instead of fixing now?**  
A: File an issue when the fix is out of scope or exceeds your timebox.

**Q: What labels are mandatory?**  
A: At minimum, include type and priority labels.

**Q: Can I create issues from PRs?**  
A: Yes. Reference the issue in the PR and use closing keywords.

---

## Quick Reference

| Step | Action | Output |
|------|--------|--------|
| 1 | Decide fix vs issue | Decision logged |
| 2 | Use template | Clear issue body |
| 3 | Add labels | Priority visible |
| 4 | Link PR | Auto-close on merge |

```bash
# CLI quick create
gh issue create --title "Bug: ..." --body-file issue.md
```

---

## Resources

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Closing issues with keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [GitHub CLI issue create](https://cli.github.com/manual/gh_issue_create)

---

## Changelog

### Version 1.0.0 (2026-02-12)
- Initial release
- Decision, template, labeling, and PR linking patterns
- CLI and GUI issue creation workflows
