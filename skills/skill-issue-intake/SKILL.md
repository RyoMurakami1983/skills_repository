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
- **`skills-validate-skill`** - Validate documentation quality

---

## Dependencies

- GitHub account with repo access
- GitHub CLI (gh) for CLI workflow (optional)
- Team label/priority taxonomy

---

## Core Principles

1. **Actionable First** - Every issue includes clear next steps (基礎と型)
2. **Scope Separation** - Track later work without blocking now (ニュートラル)
3. **Traceability** - Link issues to PRs and evidence (成長の複利)
4. **Consistency** - Use standard labels, priorities, and templates (温故知新)
5. **Low Friction** - Capture fast to avoid forgotten work (継続は力)

---

## Workflow: Capture Deferred Work as Issues

### Step 1: Decide Fix Now or File Issue

Determine whether to fix inline or defer. Use a simple decision matrix based on impact, effort, and scope relevance. If the fix is out of scope or exceeds a 30-minute timebox, file an issue instead.

```text
# ✅ CORRECT - File issue when out of scope
Issue: "Bug: CSV import fails on UTF-8 BOM"
Scope: Not required for current PR
Action: Create issue and continue

# ❌ WRONG - Hide in TODO
// TODO: fix later
```

**When**: You discover scope creep during a PR or a fix risks delaying the current release.

### Step 2: Write Title and Body

Write a clear, searchable title with a type prefix and a structured body. A good title starts with `Bug:`, `Feature:`, or `Chore:` followed by a specific description. Use a template body with Summary, Steps to Reproduce, Expected/Actual Result, and Impact sections.

```markdown
Title: "Bug: CSV import fails on UTF-8 BOM"

## Summary
CSV import rejects files with UTF-8 BOM encoding.

## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import

## Expected Result
Import succeeds.

## Actual Result
"Invalid encoding" error displayed.

## Impact
Blocks users with Excel-exported CSVs.
```

**When**: Every new issue — never skip the template even for small bugs.

### Step 3: Apply Labels and Priority

Assign labels for type, priority, and area so the backlog is sortable. At minimum, every issue needs a type label and a priority label.

| Priority | Meaning | SLA |
|----------|---------|-----|
| P0 | Production down | Same day |
| P1 | Major user impact | 1–3 days |
| P2 | Standard bug | 1–2 sprints |
| P3 | Minor/cleanup | Backlog |

```yaml
# ✅ CORRECT
labels: [bug, priority/P1, area/import]

# ❌ WRONG
labels: []
```

**When**: Before triage meetings or when handing off to another team member.

### Step 4: Add Repro Steps and Evidence

Include numbered reproduction steps, expected vs actual results, and supporting evidence (logs, screenshots, request IDs). The next owner should be able to reproduce the problem without asking follow-up questions.

```markdown
## Steps to Reproduce
1. Upload CSV with UTF-8 BOM
2. Click Import
3. Observe error in UI

## Expected
Import succeeds

## Actual
"Invalid encoding" error

## Evidence
Log: 2026-02-12T12:03:11Z ERROR import failed (BOM detected)
```

**When**: Always for bugs; for features, include user-scenario context instead.

### Step 5: Create Issue via CLI

Use `gh issue create` for fast, repeatable issue creation from the terminal. Add labels, assignees, and a body file in one command.

```bash
gh issue create \
  --title "Bug: CSV import fails on UTF-8 BOM" \
  --body-file issue.md \
  --label bug,priority/P1,area/import \
  --assignee @me
```

**When**: You are already in the terminal and want speed over formatting.

### Step 6: Create Issue via Web UI

Use the GitHub web interface when you need drag-and-drop screenshots, rich Markdown preview, or template selection. Navigate to Issues → New issue, select a template, fill required fields, and add labels and milestone before submitting.

```text
1. Open repository → Issues → New issue
2. Select template (e.g., Bug Report)
3. Fill required fields, attach screenshots
4. Add labels, milestone, and assignee
5. Submit
```

**When**: The issue needs embedded images, complex formatting, or you are triaging from the browser.

### Step 7: Link Issues to PRs

Reference issues in PR descriptions using closing keywords so issues close automatically on merge. Use `Closes #N` for direct fixes and `Refs #N` for related context.

```markdown
## Related
Closes #123
Refs #130
```

For cross-repo references, use the full `owner/repo#N` syntax:

```markdown
Fixes owner/repo#123
```

**When**: Every PR that resolves or relates to a tracked issue.

---

## Best Practices

- Use action verbs in titles (Fix, Add, Remove)
- Keep one issue per problem
- Add impact and priority before triage meetings
- Include repro steps or evidence whenever possible
- Link PRs with closing keywords
- Use the template and add labels before assigning an owner

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
| 2 | Write title and body | Searchable issue |
| 3 | Apply labels and priority | Sortable backlog |
| 4 | Add repro steps and evidence | Reproducible report |
| 5 | Create via CLI | Fast terminal workflow |
| 6 | Create via Web UI | Rich formatted issue |
| 7 | Link to PR | Auto-close on merge |

```bash
# CLI quick create
gh issue create --title "Bug: ..." --body-file issue.md --label bug,priority/P1
```

---

## Resources

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Closing issues with keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [GitHub CLI issue create](https://cli.github.com/manual/gh_issue_create)

---

## Changelog

### Version 2.0.0 (2026-02-12)
- Migrated from 7-pattern format to single-workflow with 7 steps
- Compressed examples: one best example per step
- Added Japanese value tags to all Core Principles

### Version 1.0.0 (2026-02-12)
- Initial release
- Decision, template, labeling, and PR linking patterns
- CLI and GUI issue creation workflows
