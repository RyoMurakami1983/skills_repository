---
name: github-quality-gate-setup
description: "Add gitleaks + textlint quality gate CI to any GitHub repository. Use when setting up a new repo or hardening an existing one against secret leaks and Markdown issues."
---

# GitHub Quality Gate Setup

Workflow for adding a quality gate CI pipeline — secret detection (gitleaks) and optional Markdown linting (textlint) — to any GitHub repository.

**Quality Gate**: Automated checks that run on every PR to catch security issues and content problems before merge.

## When to Use This Skill

Use this skill when:
- Adding quality gate CI to an existing repository for the first time
- Customizing the quality gate received from a template repository
- Reviewing what the `github-repo-template` pre-configures out of the box
- Updating or extending quality gate rules as the project evolves
- Investigating a gitleaks false positive and tuning the allowlist
- Deciding whether to add textlint based on Markdown content volume

> **Tip**: For brand-new repositories, start from [`github-repo-template`](https://github.com/RyoMurakami1983/github-repo-template) instead — it pre-configures everything.

## Related Skills

- **`git-initial-setup`** — Branch protection and `.gitattributes`/`.editorconfig` setup (prerequisite)
- **`knowledge-capture`** — Anonymization gate before committing documents
- **`github-issue-intake`** — Issue intake with anonymization check

---

## Dependencies

- Git 2.30+
- GitHub CLI (`gh`) — verify with `gh auth status`
- For textlint: Node.js 18+

---

## Core Principles

1. **Defense in Depth** (基礎と型) — Multiple layers: secret detection + content lint
2. **Fail Fast on PR** (継続は力) — Gate every PR; never let issues reach main
3. **Low Noise** (余白の設計) — Allowlists prevent false positives from doc examples
4. **Language Agnostic Core** (ニュートラル) — gitleaks works for any repo type; textlint is opt-in
5. **Grow the Allowlist** (温故知新) — Tuning `.gitleaks.toml` over time makes the gate smarter

---

## Workflow: Add Quality Gate CI

### Step 1: Determine Scope

Decide which jobs to add based on the repository content.

| Job | When to add |
|-----|-------------|
| **gitleaks** | Always — every repository |
| **textlint** | When the repo has significant Markdown (docs, skills, README-heavy) |

```bash
# Quick check: does the repo have Markdown files beyond README?
find . -name "*.md" | grep -v "^./README.md" | head -5
```

If more than a few `.md` files exist, add textlint. For pure code repositories (dotnet, Python with no docs), gitleaks only is sufficient.

**Why?** Adding textlint to a repo with no Markdown increases CI time and maintenance cost with zero benefit. Keeping the gate lean means engineers respect it.

> **Values**: 基礎と型

### Step 2: Add Gitleaks

Copy the workflow template and customize the allowlist.

```bash
mkdir -p .github/workflows
cp /path/to/skills/github-quality-gate-setup/scripts/quality.yml \
   .github/workflows/quality.yml
cp /path/to/skills/github-quality-gate-setup/scripts/.gitleaks.toml \
   .gitleaks.toml
```

Open `.gitleaks.toml` and add project-specific allowlist entries:

```toml
[[allowlists]]
description = "Project-specific placeholders"
regexes = [
  # Add patterns that appear in your docs/examples but are not real secrets
  '''YOUR[_-]?API[_-]?KEY''',
]
```

**Why tune the allowlist early?** False positives that aren't addressed quickly cause developers to distrust the gate. Tuning upfront builds confidence in the signal.

> **Note**: gitleaks scans only the PR diff when triggered by `pull_request` — no extra config needed.

> **Values**: 基礎と型 / 余白の設計

### Step 3: Add Textlint (Optional)

Skip this step if the repository has no significant Markdown content.

```bash
cp /path/to/skills/github-quality-gate-setup/scripts/.textlintrc.json .
cp /path/to/skills/github-quality-gate-setup/scripts/package.json .
npm install
```

Then **uncomment the textlint job** in `.github/workflows/quality.yml`:

```yaml
# Remove the comment markers around the textlint job
  textlint:
    name: textlint
    ...
```

Verify locally (optional — CI is the authoritative check):

```bash
npx textlint "**/*.md" --ignore-path .gitignore
```

> **Values**: ニュートラル

### Step 4: Commit and Push

```bash
# Add files to a feature branch
git switch -c feature/add-quality-gate

git add .github/workflows/quality.yml .gitleaks.toml

# If textlint was added:
git add .textlintrc.json package.json package-lock.json

git commit -m "feat: gitleaks + textlint 品質ゲートCIを追加

Why: PR での固有名詞・シークレット漏洩を自動検出するゲートを設置。

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git push -u origin feature/add-quality-gate
```

Then create a PR via `github-pr-workflow`.

> **Values**: 継続は力

### Step 5: Configure Branch Protection

After the CI workflow is merged to main, manually configure branch protection to require the status checks:

1. Go to GitHub → Settings → Branches → Edit rule for `main`
2. Enable **Require status checks to pass before merging**
3. Search and add: `gitleaks`
4. If textlint was added, also add: `textlint`
5. Save

> **Values**: 基礎と型

---

## Best Practices

- Always start with gitleaks; add textlint only when there is Markdown to lint
- Grow the `.gitleaks.toml` allowlist incrementally — add entries when you encounter false positives
- Use `YOUR_API_KEY_HERE`-style placeholders in doc examples to avoid false positives
- Commit `package-lock.json` when using textlint — required for `npm ci` in CI
- For non-Markdown repos, keep only the gitleaks job to minimize CI overhead

### Preflight Checklist

- [ ] `gh auth status` succeeds (workflow scope required for `.github/workflows/` push)
- [ ] Feature branch created (not on main)
- [ ] `.gitleaks.toml` allowlist tuned for this repo's doc examples
- [ ] textlint: decided whether to include based on Markdown volume

### Self-Review Checklist

- [ ] `.github/workflows/quality.yml` triggers on `pull_request`
- [ ] gitleaks job uses `gitleaks-action@v2` with `GITHUB_TOKEN`
- [ ] If textlint: `package-lock.json` committed; textlint rules pass on existing files
- [ ] Branch protection updated after merge

---

## Common Pitfalls

1. **Push rejected for `.github/workflows/*`**
   ❌ Token lacks `workflow` scope — push is rejected with a remote error.
   ✅ Fix: `gh auth refresh -h github.com -s workflow`

2. **textlint "No rules found"**
   ❌ A filter rule (e.g., `filters.comments`) references an uninstalled package — textlint exits with error.
   ✅ Fix: Remove or install the missing filter package.

3. **gitleaks false positives on doc examples**
   ❌ Example API keys/tokens in Markdown match gitleaks patterns — every PR fails.
   ✅ Fix: Add patterns to `[[allowlists]]` in `.gitleaks.toml`.

4. **textlint `no-empty-section` error on existing files**
   ❌ A heading exists with no content before the next heading — CI fails on unrelated files.
   ✅ Fix: Remove the empty heading or add placeholder content.

---

## Anti-Patterns

- Merging `.github/workflows/` changes without requiring status checks in branch protection
- Leaving the allowlist empty and suppressing all gitleaks findings with global ignores
- Running textlint on repos with no meaningful Markdown (unnecessary CI overhead)

---

## Quick Reference

### Decision Table: gitleaks only vs. gitleaks + textlint

```
repo has many .md files?
  ├── YES → gitleaks + textlint
  └── NO  → gitleaks only
```

### Minimal gitleaks-only workflow

```yaml
name: Quality Gate
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  gitleaks:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Template files location

```
skills/github-quality-gate-setup/scripts/
├── quality.yml         # Full workflow (textlint job commented out)
├── .gitleaks.toml      # Base allowlist
├── .textlintrc.json    # Textlint rules
└── package.json        # Textlint npm deps
```

---

## FAQ

**Q: Does gitleaks need a paid license?**
A: No. For public repositories, `gitleaks-action@v2` works with just `GITHUB_TOKEN`.

**Q: How do I add a prohibited terms dictionary to textlint?**
A: Install `textlint-rule-no-restricted-syntax` or create a custom wordlist file and reference it in `.textlintrc.json`.

**Q: What if gitleaks finds a real secret already in history?**
A: Rotate the secret immediately. Then use `git filter-repo` or BFG to remove it from history, and force-push.

**Q: Can I use detect-secrets instead of gitleaks?**
A: Yes, but gitleaks is simpler to start with. detect-secrets adds a baseline file (`detect-secrets scan > .secrets.baseline`) which is useful for managing known false positives over time.

---

## Resources

- [gitleaks-action](https://github.com/gitleaks/gitleaks-action)
- [gitleaks configuration](https://github.com/gitleaks/gitleaks#configuration)
- [textlint rules](https://github.com/textlint/textlint/wiki/Collection-of-textlint-rule)
- [github-repo-template](https://github.com/RyoMurakami1983/github-repo-template)
