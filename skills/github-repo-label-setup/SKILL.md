---
name: github-repo-label-setup
description: Standardize repository labels with prefix-based naming conventions. Use when setting up or migrating repository labels for consistent issue and PR management.
metadata:
  author: RyoMurakami1983
  tags: [github, labels, issue-management, repository-setup, conventions]
  invocable: false
---

# GitHub Repository Label Setup

Standardize repository labels using prefix-based naming conventions (`p/`, `t/`, `s/`, `a/`) for consistent issue and PR management across projects.

## When to Use This Skill

Use this skill when:
- Setting up a new GitHub repository and defining its label taxonomy
- Migrating from GitHub default labels to a prefix-based convention
- Standardizing labels across multiple repositories in an organization
- Onboarding a team to a consistent issue triage workflow
- Auditing existing labels for inconsistency or duplication
- Documenting label conventions in CONTRIBUTING.md or README

## Related Skills

- **`github-issue-intake`** - Issue creation and triage using labels
- **`github-pr-workflow`** - PR creation and merge flow
- **`git-initial-setup`** - Repository bootstrap and protection
- **`skills-author-skill`** - Skill documentation standards

---

## Dependencies

- GitHub CLI (`gh`) — verify with `gh auth status`
- GitHub repository with admin or write access
- Bash or PowerShell (for batch label creation scripts)

## Core Principles

1. **Prefix Convention** (基礎と型) - Use `p/`, `t/`, `s/`, `a/` prefixes for machine-sortable, human-readable labels
2. **Idempotent Creation** (継続は力) - Use `--force` flag so scripts can run repeatedly without errors
3. **Color Semantics** (ニュートラル) - Assign color spectrums by category for instant visual recognition
4. **Minimal Viable Set** (余白の設計) - Start with essential labels; add more only when a real need emerges
5. **Documentation First** (成長の複利) - Record label conventions so new contributors apply them consistently

---

## Workflow: Repository Label Setup

### Step 1: Audit Existing Labels

List current labels and compare with GitHub defaults. Identify labels to keep, rename, or delete before applying the new convention.

```bash
# List all labels in the repository
gh label list --repo OWNER/REPO

# Count existing labels
gh label list --repo OWNER/REPO --json name --jq 'length'
```

```powershell
# PowerShell equivalent
gh label list --repo OWNER/REPO
gh label list --repo OWNER/REPO --json name --jq 'length'
```

| Default Label | Decision | Reason |
|---------------|----------|--------|
| bug | Replace with `t/bug` | Prefix convention |
| enhancement | Replace with `t/feature` | Consistent naming |
| documentation | Replace with `t/docs` | Shorter prefix |
| good first issue | Keep as-is | Community convention |
| help wanted | Keep as-is | Community convention |
| duplicate | Delete | Use issue close reason instead |
| invalid | Delete | Use issue close reason instead |
| wontfix | Delete | Use issue close reason instead |
| question | Delete | Use Discussions instead |

Use when setting up a new repository or migrating an existing one to the prefix convention.

> **Values**: 基礎と型 / 温故知新

### Step 2: Select Label Set

Choose the label categories and specific labels for your repository. Use the prefix convention below as the standard set.

| Category | Labels | Color | Purpose |
|----------|--------|-------|---------|
| Priority | `p/critical`, `p/high`, `p/medium`, `p/low` | Red spectrum (`#B60205`, `#D93F0B`, `#FBCA04`, `#0E8A16`) | Triage priority |
| Type | `t/bug`, `t/feature`, `t/docs`, `t/chore`, `t/refactor` | Blue spectrum (`#1D76DB`, `#0075CA`, `#5319E7`, `#006B75`, `#0366D6`) | Work classification |
| Status | `s/in-progress`, `s/review`, `s/blocked` | Yellow spectrum (`#FEF2C0`, `#D4C5F9`, `#E4E669`) | Workflow state |
| Area | `a/skills`, `a/dotnet`, `a/python`, `a/docs` | Green spectrum (`#22863A`, `#1A7F37`, `#2DA44E`, `#3FB950`) | Domain ownership |

Adapt the Area labels to match your project domains. Keep Priority, Type, and Status labels consistent across repositories. Why prefixes? — Free-form labels become inconsistent across projects and resist automation. Prefixes enable machine filtering (`gh issue list --label "p/"`) and visual grouping in the GitHub UI.

Use when defining label conventions for the first time or reviewing the label set for completeness.

> **Values**: 基礎と型 / 余白の設計

### Step 3: Batch Create Labels

Create all labels using `gh label create` with the `--force` flag for idempotency. The `--force` flag updates existing labels instead of failing on duplicates.

```bash
# Priority labels
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force

# Type labels
gh label create "t/bug"      --color "1D76DB" --description "Bug report" --force
gh label create "t/feature"  --color "0075CA" --description "Feature request" --force
gh label create "t/docs"     --color "5319E7" --description "Documentation" --force
gh label create "t/chore"    --color "006B75" --description "Maintenance task" --force
gh label create "t/refactor" --color "0366D6" --description "Code refactoring" --force

# Status labels
gh label create "s/in-progress" --color "FEF2C0" --description "Work in progress" --force
gh label create "s/review"      --color "D4C5F9" --description "Ready for review" --force
gh label create "s/blocked"     --color "E4E669" --description "Blocked by dependency" --force

# Area labels (customize per project)
gh label create "a/skills"  --color "22863A" --description "Skills domain" --force
gh label create "a/dotnet"  --color "1A7F37" --description ".NET domain" --force
gh label create "a/python"  --color "2DA44E" --description "Python domain" --force
gh label create "a/docs"    --color "3FB950" --description "Documentation domain" --force
```

```powershell
# PowerShell — same commands work cross-platform with gh CLI
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force
```

Use when labels are defined and ready to be applied. Safe to re-run at any time.

> **Values**: 継続は力 / 基礎と型

### Step 4: Triage Existing Issues

Optionally assign labels to existing unlabeled issues. Use `gh issue list` with `--json` to identify issues without labels and apply appropriate ones.

```bash
# List unlabeled issues
gh issue list --label "" --json number,title --jq '.[] | "\(.number)\t\(.title)"'

# Add a label to a specific issue
gh issue edit 42 --add-label "t/bug,p/medium"

# Bulk label issues by keyword (example)
for issue in $(gh issue list --search "is:open no:label" --json number --jq '.[].number'); do
  echo "Review issue #$issue"
done
```

```powershell
# PowerShell equivalent
$issues = gh issue list --search "is:open no:label" --json number --jq '.[].number'
foreach ($issue in $issues) {
    Write-Host "Review issue #$issue"
}
```

Use when migrating to the new label convention and existing issues need classification. Manual review is recommended — avoid fully automated bulk labeling.

> **Values**: ニュートラル / 成長の複利

### Step 5: Document Label Convention

Record the label convention in CONTRIBUTING.md or README so contributors apply labels consistently. Include the label table and triage guidelines.

```markdown
## Label Convention

This repository uses prefix-based labels for consistent triage:

| Prefix | Category | Example | When to Use |
|--------|----------|---------|-------------|
| `p/` | Priority | `p/high` | During triage to set urgency |
| `t/` | Type | `t/bug` | When creating or classifying issues |
| `s/` | Status | `s/review` | When updating workflow state |
| `a/` | Area | `a/python` | To assign domain ownership |

### Triage Checklist
- [ ] Assign one `t/` label (required)
- [ ] Assign one `p/` label (required for bugs)
- [ ] Assign one `a/` label (recommended)
- [ ] Update `s/` label as work progresses
```

Use after labels are created, so contributors and maintainers have a shared reference.

> **Values**: 成長の複利 / 継続は力

---

## Decision Table

| Situation | Label Categories | Why |
|-----------|-----------------|-----|
| Solo project | `t/` + `p/` only | Why not all four? — Overhead exceeds benefit for one person |
| Small team (2-5) | `t/` + `p/` + `a/` | Why add area? — Domain ownership helps routing work |
| Cross-functional team | All four categories | Why all four? — Full triage workflow reduces coordination cost |
| Open source project | All four + community labels | Why keep defaults? — `good first issue` is recognized by GitHub |
| Monorepo | All four with expanded `a/` | Why expand area? — Labels map to package paths for filtering |

---

## Best Practices

- Use `--force` flag on `gh label create` for idempotent scripts
- Create label descriptions under 100 characters
- Apply consistent color spectrums per category for visual scanning
- Avoid free-form label names — use prefixes (`p/`, `t/`) for sortability
- Define label conventions in CONTRIBUTING.md before creating labels
- Consider quarterly reviews to prune unused labels
- Use `good first issue` and `help wanted` as community standards

✅ Good: `t/bug`, `p/high`, `s/review` — prefixed, sortable, self-documenting
❌ Bad: `bug`, `urgent`, `needs review` — no prefix, inconsistent, unsortable

---

## Common Pitfalls

1. **Missing `--force` flag on re-run**
   Fix: Always include `--force` — it updates existing labels instead of erroring.

2. **Deleting community labels (`good first issue`, `help wanted`)**
   Fix: Keep these labels — they are recognized by GitHub's UI and contributor guides.

3. **Applying labels without documenting the convention**
   Fix: Update CONTRIBUTING.md before or immediately after label creation. This is why documentation comes last in the workflow — it captures the final state.

---

## Anti-Patterns

- Creating dozens of labels without a naming convention
- Using colors randomly without category semantics
- Deleting all default labels before understanding community conventions
- Fully automating bulk label assignment without manual review
- Adding labels that overlap in meaning (e.g., `bug` and `t/bug` coexisting)

---

## FAQ

**Q: Should I delete GitHub's default labels?**
A: Keep `good first issue` and `help wanted` (community standards). Replace `bug`, `enhancement`, and `documentation` with prefixed equivalents. Delete `duplicate`, `invalid`, `wontfix`, and `question`.

**Q: Can I run the label creation script on an existing repository?**
A: Yes. The `--force` flag updates existing labels without creating duplicates. It is safe to re-run at any time.

**Q: What if my project has custom domains beyond the standard `a/` labels?**
A: Add project-specific `a/` labels (e.g., `a/api`, `a/frontend`, `a/infra`). Keep the prefix convention consistent.

**Q: Do I need all four label categories?**
A: No. Start with `t/` and `p/` as the minimum. Add `s/` and `a/` when your workflow demands them. See the Decision Table.

---

## Quick Reference

### Step Summary

| Step | Focus | Use When |
|------|-------|----------|
| 1 | Audit existing labels | Setting up or migrating labels |
| 2 | Select label set | Defining the convention |
| 3 | Batch create labels | Applying labels to the repo |
| 4 | Triage existing issues | Migrating to the new convention |
| 5 | Document convention | Onboarding contributors |

### Label Setup Checklist

- [ ] Run `gh label list` to audit existing labels
- [ ] Define label set from the standard table
- [ ] Run batch creation script with `--force`
- [ ] Triage unlabeled issues (optional)
- [ ] Document convention in CONTRIBUTING.md

### Batch Creation Script (copy-paste ready)

```bash
# Priority
gh label create "p/critical" --color "B60205" --description "Critical priority" --force
gh label create "p/high"     --color "D93F0B" --description "High priority" --force
gh label create "p/medium"   --color "FBCA04" --description "Medium priority" --force
gh label create "p/low"      --color "0E8A16" --description "Low priority" --force

# Type
gh label create "t/bug"      --color "1D76DB" --description "Bug report" --force
gh label create "t/feature"  --color "0075CA" --description "Feature request" --force
gh label create "t/docs"     --color "5319E7" --description "Documentation" --force
gh label create "t/chore"    --color "006B75" --description "Maintenance task" --force
gh label create "t/refactor" --color "0366D6" --description "Code refactoring" --force

# Status
gh label create "s/in-progress" --color "FEF2C0" --description "Work in progress" --force
gh label create "s/review"      --color "D4C5F9" --description "Ready for review" --force
gh label create "s/blocked"     --color "E4E669" --description "Blocked by dependency" --force

# Area (customize per project)
gh label create "a/skills"  --color "22863A" --description "Skills domain" --force
gh label create "a/dotnet"  --color "1A7F37" --description ".NET domain" --force
gh label create "a/python"  --color "2DA44E" --description "Python domain" --force
gh label create "a/docs"    --color "3FB950" --description "Documentation domain" --force
```

---

## Resources

- [GitHub CLI Label Commands](https://cli.github.com/manual/gh_label)
- [Managing Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Default Labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels#about-default-labels)

---
