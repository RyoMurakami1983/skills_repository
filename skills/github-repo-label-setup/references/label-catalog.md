# Repository Label Catalog — Reference

## Standard Label Prefixes

| Prefix | Category | Purpose | Example |
|--------|----------|---------|---------|
| `t/` | Type | What kind of work | `t/feature`, `t/bug`, `t/chore`, `t/docs` |
| `a/` | Area | Which domain/skill | `a/skills`, `a/python`, `a/dotnet`, `a/ci` |
| `s/` | Status | Current state | `s/blocked`, `s/review`, `s/in-progress` |
| `p/` | Priority | Urgency level | `p/critical`, `p/high`, `p/medium`, `p/low` |

## Standard Color Palette

| Label | Color hex | Visual |
|-------|-----------|--------|
| t/feature | `#0075CA` | Blue |
| t/bug | `#D73A4A` | Red |
| t/chore | `#006B75` | Teal |
| t/docs | `#0075CA` | Blue |
| a/skills | `#22863A` | Green |
| s/blocked | `#E4E669` | Yellow |
| p/critical | `#B60205` | Dark red |

## Migration Strategy

When migrating from an existing label system:
1. Export current labels with `gh label list --json name,color > labels-backup.json`
2. Create new labels first (no conflict)
3. Re-apply labels on open issues/PRs
4. Delete old labels (check for zero usage first)

## Cross-Repository Consistency

For organizations with multiple repos:
- Define labels in a shared `.github` repo
- Use `gh label clone <source-repo>` to copy label sets
- Automate with a workflow that syncs on push to `.github/labels.yml`
