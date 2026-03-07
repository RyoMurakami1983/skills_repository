---
name: github-issue-intake
description: Capture deferred work as actionable GitHub issues. Use when triaging scope.
metadata:
  author: RyoMurakami1983
  tags: [github, issues, triage, workflow, documentation]
  invocable: false
---

# Issue Intake

Turn out-of-scope bugs or improvements into actionable GitHub issues with consistent structure, ownership, and priority.

## When to Use This Skill

Use this skill when:
- Capturing out-of-scope bugs discovered during a Pull Request (PR) review
- Deferring non-critical fixes to a later sprint or milestone
- Standardizing issue titles, labels, and priority across teams
- Clarifying existing issues that are vague or hard to act on (rewrite title/body)
- Recording reproducible steps for intermittent production failures
- Converting support requests into trackable engineering work
- Handing off follow-up tasks to another owner or team

## Related Skills

- **`git-commit-practices`** - Commit workflow and conventions
- **`github-pr-workflow`** - PR workflow and merge policies
- **`git-initial-setup`** - Default repo protections for new repos
- **`skills-revise-skill`** - Revision and change log practices
- **`skills-validate-skill`** - Validate documentation quality
- **`knowledge-capture`** - Anonymization gate for public-repo content

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
Issue: "🟡 CSV import: UTF-8 BOM を受け付けない"
Scope: Not required for current PR
Action: Create issue and continue

# ❌ WRONG - Hide in TODO
// TODO: fix later
```

**When**: You discover scope creep during a PR or a fix risks delaying the current release.

### Step 1.5: Apply Anonymization Gate (Public Repo)

Before writing any content, check whether the destination repository is **public**. If yes, apply the [Anonymization Checklist from `knowledge-capture`](../knowledge-capture/SKILL.md#anonymization-checklist) (AC-1 through AC-4):

| Check | What to scan in the issue |
|-------|--------------------------|
| AC-1 | Project names, org names, private repo names (e.g., `MyOrg/my-private-repo`) |
| AC-2 | Internal IDs, data formats, function/class names specific to a private codebase |
| AC-3 | Domain-specific terminology that identifies the internal system or client |
| AC-4 | Real numeric thresholds, config values, or business-specific numbers |

Replace private details with generic equivalents before writing the issue body.

```markdown
# ❌ WRONG — private repo details exposed
## Background
Practiced during `internal_project` bug fix. See: MyOrg/my-private-repo PR #3

# ✅ CORRECT — anonymized
## Background
Practiced during a numerical optimization library bug fix session.
See: (private repo / internal PR)
```

**Decision Rule**: Is the destination repository public? → Yes = Apply AC-1 through AC-4 before writing.

> **Values**: ニュートラルな視点（固有知識を普遍化して公開する）

**When**: Every time you create an issue in a public repository that references internal project work.

### Step 2: Write (or Refactor) Title and Body

Write a clear, searchable title and a structured body.
In this repository, default to Japanese issue titles and bodies. Keep proper nouns, CLI commands, code identifiers, and external service names in English when that improves recognition.

#### Recommended: priority markers in the title

Use color-circle markers for quick scanning during triage. Keep labels as the source of truth; the emoji is for visibility.

| Marker | Meaning | Typical mapping |
|--------|---------|-----------------|
| 🔴 | Urgent / P0 | Production down |
| 🟡 | High / P1 | Major user impact |
| 🟢 | Medium / P2 | Standard bug / improvement |
| 🔵 | Low / P3 | Minor / cleanup |

Examples:
- `🟡 validate_skill.py: Workflow/Router向けのセクション抽出を堅牢化する`
- `🟢 github-issue-intake: Issueは日本語で起票する方針を明記する`

#### Body template

A good title in this repository uses a priority marker plus a short Japanese summary. Keep English only where it improves recognition, such as product names, CLI commands, or code identifiers.

```markdown
Title: "🟢 github-issue-intake: Issueは日本語で起票する方針を明記する"

## 背景
Issue #123 / #124 を英語で起票した後、日本語へ修正する手戻りが発生した。

## 問題
Issue の言語方針が明文化されておらず、起票者ごとに英語 / 日本語が揺れる。

## 提案
このリポジトリでは Issue を日本語で起票する方針を `github-issue-intake` に追記する。

## Definition of Done
- [ ] 日本語起票ルールが明記されている
- [ ] 英語併記を許容する条件が分かる
```

**Note (Markdown gotcha)**: Avoid placeholders like `<path>` in issue bodies — they may be treated as HTML tags and disappear. Prefer `PATH` / `FILE` or fenced code blocks.

**When**: Every new issue and every “unclear issue” you choose to refactor.

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
labels: [t/bug, p/high, a/import]

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

### Step 5: Create or Edit Issues via CLI (Recommended)

Use `gh issue create` for fast, repeatable creation, and `gh issue edit` to refactor unclear issues.

```bash
# Create
gh issue create \
  --title "🟢 github-issue-intake: Issueは日本語で起票する方針を明記する" \
  --body-file issue.md \
  --label t/chore,p/medium,a/skills \
  --assignee @me

# Edit
gh issue edit 123 --title "🟢 Windows: UTF-8 入出力の標準化を行う" --body-file issue.md
```

#### Windows / PowerShell: safest body-file approach (UTF-8)

Avoid passing large multiline strings via `--body` (quoting can break or hang). Generate a UTF-8 body file and pass it.

```powershell
$bodyLines = @(
  '## 背景',
  '- 英語 Issue を後から日本語へ直す手戻りが発生した',
  '',
  '## Definition of Done (DoD)',
  '- [ ] ...'
)
$bodyFile = Join-Path $env:TEMP 'issue_body.md'
Set-Content -Path $bodyFile -Value $bodyLines -Encoding utf8

gh issue edit 123 --title '🟢 ...' --body-file $bodyFile
Remove-Item -LiteralPath $bodyFile -Force
```

**When**: You are already in the terminal and want speed, repeatability, and consistent formatting.

### Step 6: Create Issue via Web UI

Use the GitHub web interface when you need drag-and-drop screenshots, rich Markdown preview, or template selection.

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

- Refactor unclear issues into an actionable format (Background → Goal → Scope → DoD)
- In this repository, default to Japanese issue titles and bodies
- Keep proper nouns, CLI commands, code identifiers, and service names in English when that improves recognition
- Use the priority marker scheme (🔴🟡🟢🔵) consistently in titles
- Use explicit Japanese action phrases in titles when helpful (for example: `標準化する`, `明記する`, `棚卸しする`)
- Keep one issue per problem
- Add impact and priority before triage meetings
- Include repro steps or evidence whenever possible
- Link PRs with closing keywords
- Use `--body-file` for anything beyond one-line bodies

---

## Common Pitfalls

- Writing vague titles like "Bug" or "Fix later"
- Skipping repro steps for intermittent failures
- Mixing multiple problems into one issue
- Passing long bodies via `gh issue edit --body ...` on PowerShell
- Using placeholders like `<PATH>` that may disappear in Markdown rendering
- Mixing English-first and Japanese-first issue styles in the same repository without a policy

Fix: Use the standard template and split issues by scope.
Fix: Always add repro steps or evidence links.
Fix: Prefer `--body-file` with UTF-8 for CLI edits.

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
A: At minimum, include one type label (`t/*`) and one priority label (`p/*`).

**Q: Should issues in this repository be written in Japanese or English?**
A: Default to Japanese for titles and bodies. Keep proper nouns, CLI commands, code identifiers, and external service names in English when that improves recognition.

**Q: Can I edit existing issues to make them clearer?**
A: Yes — treat it as backlog maintenance. Update title/body (and add DoD) so the next owner can act without questions.

---

## Quick Reference

| Step | Action | Output |
|------|--------|--------|
| 1 | Decide fix vs issue | Decision logged |
| 1.5 | Apply anonymization gate (public repo) | No private data in issue |
| 2 | Write/refactor title + body (use 🔴🟡🟢🔵) | Searchable, actionable issue |
| 3 | Apply labels and priority | Sortable backlog |
| 4 | Add repro steps and evidence | Reproducible report |
| 5 | Create/edit via CLI (`--body-file`) | Fast, safe workflow |
| 6 | Create via Web UI | Rich formatted issue |
| 7 | Link to PR | Auto-close on merge |

```bash
# CLI quick create
gh issue create --title "🟢 改善: ..." --body-file issue.md --label t/feature,p/medium,a/skills

# CLI quick edit
gh issue edit 123 --title "🟢 〜を明記する" --body-file issue.md
```

---

## Resources

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues)
- [Closing issues with keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
- [GitHub CLI issue create](https://cli.github.com/manual/gh_issue_create)
- [GitHub CLI issue edit](https://cli.github.com/manual/gh_issue_edit)

---
