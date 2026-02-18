---
name: git-init-to-github
description: >
  Initialize a local directory as a git repo and push to GitHub in one workflow.
  Use when starting a new project from scratch with no existing git history
  and creating the corresponding GitHub repository.
metadata:
  author: RyoMurakami1983
  tags: [git, github, repository, bootstrap, push]
  invocable: false
---

# Git Init to GitHub Push

End-to-end workflow for turning an untracked local directory into a GitHub-hosted repository. Covers `.gitignore` creation, initial commit, remote repo creation via `gh`, first push, and optional main-branch protection hooks.

## When to Use This Skill

Use this skill when:
- Initializing a brand-new project directory that has no `.git/` folder
- Creating a GitHub repository and pushing local files for the first time
- Setting up `.gitignore` appropriate for the project's tech stack
- Deciding between public and private repository visibility
- Adding local branch-protection hooks after the initial push

## Related Skills

- **`git-initial-setup`** — Comprehensive main-branch protection (server + local hooks)
- **`git-commit-practices`** — Conventional Commits and atomic changes
- **`github-pr-workflow`** — PR creation and merge flow

---

## Core Principles

1. **Ask Before Assuming** — Repository name, owner, and visibility are user decisions; always confirm interactively (ニュートラル)
2. **Simple Commands First** — Use only `git` and `gh` CLI; avoid complex scripting when the toolchain handles it (基礎と型)
3. **Incremental Safety** — Start with a working push, then layer protection hooks; never block the first push with over-engineering (余白の設計)
4. **Defense in Depth** — After the initial push, install local pre-commit/pre-push hooks to prevent accidental direct commits to main (基礎と型)

---

## Workflow: Init and Push to GitHub

### Step 1 — Gather Information from User

Use when starting a new project and need to collect repository settings interactively.

Ask the user for each of these, one at a time:

| Question | Example | Default |
|----------|---------|---------|
| GitHub owner (user or org) | `RyoMurakami1983` | — (required) |
| Repository name | `my-project` | current directory name |
| Visibility | `private` or `public` | `private` |
| Description | `"My awesome project"` | `""` (empty) |
| Install main-branch protection hooks? | `yes` / `no` | `yes` |

```markdown
// ✅ CORRECT - Ask one question at a time with choices
ask_user: "Should the repository be public or private?"
  choices: ["private (Recommended)", "public"]

// ❌ WRONG - Dump all questions at once
"Please provide: owner, name, visibility, description, and hook preference"
```

> **Values**: ニュートラルな視点 / 余白の設計

### Step 2 — Create `.gitignore`

Use when the project has no `.gitignore` or the existing one is incomplete for the tech stack.

Detect the project's tech stack from existing files and generate an appropriate `.gitignore`.

**Detection heuristic**:

| Indicator file | Add to `.gitignore` |
|----------------|---------------------|
| `package.json` | `node_modules/` |
| `requirements.txt` / `pyproject.toml` | `__pycache__/`, `.venv/`, `*.egg-info/` |
| `*.csproj` / `*.sln` | `bin/`, `obj/` |
| `go.mod` | (Go binaries are not typically committed) |
| `Cargo.toml` | `target/` |

Always include:
```gitignore
# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

If `.gitignore` already exists, confirm with the user before overwriting.

> **Values**: 基礎と型の追求 / ニュートラルな視点

### Step 3 — Initialize Git and Create Initial Commit

Use when `.gitignore` is ready and all files are prepared for the first commit.

```bash
# ✅ CORRECT - Simple sequential commands
git init
git add .
git commit -m "feat: initial commit

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**Commit message rules**:
- Use Conventional Commits format (`feat:`, `chore:`, etc.)
- Include `Co-authored-by` trailer when Copilot assisted
- Keep subject line ≤ 50 characters if possible

> **Values**: 基礎と型の追求 / 継続は力

### Step 4 — Create GitHub Repository

Use when the initial commit exists and you are ready to create the remote repository.

```bash
# ✅ CORRECT - gh repo create with explicit flags
gh repo create <owner>/<repo> --private --description "<description>"

# ❌ WRONG - Interactive mode (unpredictable in agent context)
gh repo create
```

**Pre-flight checks**:
1. Verify `gh auth status` shows logged-in state
2. Verify repository name doesn't already exist: `gh repo view <owner>/<repo>` should return an error

**Error handling**:
- If `gh auth status` fails → ask user to run `gh auth login`
- If repo already exists → ask user whether to use existing or choose a new name

> **Values**: ニュートラルな視点 / 基礎と型の追求

### Step 5 — Add Remote and Push

Use when the GitHub repository is created and ready for the first push.

Try HTTPS first (most reliable with `gh` auth):

```bash
# ✅ CORRECT - HTTPS with gh credential helper
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

**Fallback strategy** (if HTTPS fails):
```bash
# Try SSH if HTTPS credential fails
git remote set-url origin git@github.com:<owner>/<repo>.git
git push -u origin main
```

**If SSH also fails**, inform user:
```
SSH key not configured. Run: gh auth setup-git
Then retry: git push -u origin main
```

> **Values**: 基礎と型の追求 / 余白の設計

### Step 6 — Verify

Use when the push completed and you need to confirm everything is correct.

```bash
# Confirm remote is set and push succeeded
gh repo view <owner>/<repo>
git --no-pager log --oneline -1
```

Report to the user:
- Repository URL
- Visibility (public/private)
- Branch name
- Number of files committed

> **Values**: 継続は力 / 成長の複利

### Step 7 — Install Main-Branch Protection Hooks (Optional)

Use when the user opted in at Step 1 and you want to add local branch protection.

Install local git hooks to prevent direct commits and pushes to `main`.

**Pre-commit hook** (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
# Block direct commits to main
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" = "main" ]; then
  echo "ERROR: Direct commits to main are not allowed."
  echo "Create a feature branch: git checkout -b <branch-name>"
  exit 1
fi
```

**Pre-push hook** (`.git/hooks/pre-push`):

```bash
#!/bin/sh
# Block direct pushes to main
branch="$(git rev-parse --abbrev-ref HEAD)"
remote_ref="$2"
while read local_ref local_sha remote_ref remote_sha; do
  if echo "$remote_ref" | grep -q "refs/heads/main"; then
    echo "ERROR: Direct pushes to main are not allowed."
    echo "Push to a feature branch and create a PR."
    exit 1
  fi
done
```

**PowerShell alternative** for Windows (if Git Bash hooks don't work):

Create `.git/hooks/pre-commit` and `.git/hooks/pre-push` with the shell scripts above. Git for Windows includes a POSIX shell that executes these.

**Important**: Hooks are local only — they do not push to the remote. Each collaborator must install them separately or use `git config core.hooksPath`.

After installing, verify:
```bash
# Should be blocked
git checkout main
echo "test" >> test.txt && git add test.txt && git commit -m "test"
# Expected: ERROR: Direct commits to main are not allowed.

# Clean up
git checkout -
git checkout main -- test.txt 2>/dev/null
```

> **Values**: 基礎と型の追求 / 成長の複利

---

## Good Practices

### 1. Always Use HTTPS First

**What**: Default to HTTPS remote URL; fall back to SSH only on failure.

**Why**: `gh` CLI configures HTTPS credential helpers automatically; SSH requires separate key setup.

**Values**: 基礎と型（最小構成で確実に動く）

### 2. Confirm Before Destructive Actions

**What**: Ask user before overwriting `.gitignore` or force-pushing.

**Why**: Prevent accidental data loss in the user's working directory.

**Values**: ニュートラル（偏らない判断）

### 3. Separate Concerns: Push First, Protect Later

**What**: Complete the push workflow before adding branch protection.

**Why**: Avoid blocking the first push with hook errors; build incrementally.

**Values**: 余白の設計（変化の起点を守る）

---

## Common Pitfalls

### 1. SSH Permission Denied on First Push

**Problem**: `git remote add origin git@github.com:...` fails because no SSH key is configured.

**Solution**: Use HTTPS URL first. If user prefers SSH, guide them to `gh auth setup-git` or `ssh-keygen`.

### 2. Forgetting `node_modules/` in `.gitignore`

**Problem**: Hundreds of thousands of files staged, commit takes forever or fails.

**Solution**: Always create `.gitignore` BEFORE `git add .`.

### 3. Hooks Not Executable on Unix

**Problem**: Pre-commit/pre-push hooks silently ignored because they lack execute permission.

**Solution**: `chmod +x .git/hooks/pre-commit .git/hooks/pre-push` after creation.

---

## Anti-Patterns

### 1. Interactive `gh repo create` Without Flags

```bash
# ❌ Anti-Pattern - Unpredictable in agent/CI context
gh repo create

# ✅ Fix - Always use explicit flags
gh repo create owner/repo --private --description "desc"
```

**Why**: Interactive mode relies on stdin prompts that agents cannot reliably handle.

### 2. Force-Pushing Without Confirmation

```bash
# ❌ Anti-Pattern - Data loss risk
git push --force origin main

# ✅ Fix - Never force-push without explicit user consent
ask_user: "Force push will overwrite remote history. Proceed?"
```

**Why**: Force-push to main can destroy collaborators' work irreversibly.

### 3. Skipping `.gitignore` Before First Commit

```bash
# ❌ Anti-Pattern - Commits secrets and build artifacts
git init && git add . && git commit -m "init"

# ✅ Fix - Always create .gitignore first
# Create .gitignore → git init → git add . → git commit
```

**Why**: Removing accidentally committed files (e.g., `node_modules/`, `.env`) from git history is painful and error-prone.

---

## Quick Reference

### Decision Table

| Situation | Action | Reason |
|-----------|--------|--------|
| No `.git/` folder exists | Start from Step 1 | Full workflow needed |
| `.git/` exists but no remote | Skip to Step 4 | Local repo already initialized |
| Remote exists but push fails | Check Step 5 fallback | HTTPS/SSH credential issue |
| User wants branch protection | Include Step 7 | Prevent accidental main commits |
| `.gitignore` already exists | Confirm before overwriting | Preserve user customizations |
| `gh auth status` fails | Ask user to run `gh auth login` | Cannot create repo without auth |

### Checklist

- [ ] Gathered: owner, repo name, visibility, description
- [ ] `.gitignore` created with tech-stack-appropriate entries
- [ ] `git init` completed
- [ ] `git add .` + initial commit created
- [ ] `gh repo create` succeeded
- [ ] `git remote add origin` (HTTPS)
- [ ] `git push -u origin main` succeeded
- [ ] `gh repo view` confirms repository exists
- [ ] (Optional) Pre-commit hook installed
- [ ] (Optional) Pre-push hook installed
- [ ] (Optional) Hooks verified with test commit on main

### Command Summary

```bash
# Full workflow (copy-paste ready)
git init
git add .
git commit -m "feat: initial commit"
gh repo create <owner>/<repo> --private --description "<desc>"
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
gh repo view <owner>/<repo>
```

---

## Resources

- [gh repo create documentation](https://cli.github.com/manual/gh_repo_create)
- [git init documentation](https://git-scm.com/docs/git-init)
- [gitignore patterns](https://git-scm.com/docs/gitignore)
- [Git Hooks documentation](https://git-scm.com/docs/githooks)
- **`git-initial-setup`** skill — For comprehensive server-side + local protection

---
