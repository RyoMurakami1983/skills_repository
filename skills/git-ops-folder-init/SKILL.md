---
name: git-ops-folder-init
description: "Set up and configure operational folders as git repositories that selectively track tool and config directories (.github, .claude, .codex) while ignoring binary business files. Use when adding version control to manufacturing records, quality documentation, or any mixed-content folder where only knowledge artifacts — Markdown, scripts, config — should be versioned."
---

# Git Ops Folder Init

Initialize an operational or business folder as a git repository that tracks **only knowledge artifacts** — Markdown documents, scripts, and configuration files — while automatically ignoring all binary files (Office documents, PDFs, images, videos, etc.).

**Prerequisites**: Git 2.30+ required (no additional package dependencies). This skill has no npm, pip, or NuGet dependencies.

## When to Use This Skill

Use this skill when:

- Initializing version control for a **business or operational folder** (manufacturing, quality docs)
- Managing a folder with **mixed content** — some files versioned, most intentionally ignored
- Implementing **zero-surprise git management** where nothing unexpected ever gets committed
- Transitioning from "just files on a network drive" to **docs-as-code** for knowledge artifacts only
- Setting up git for **non-developer teams** who must not accidentally commit large binary files

**Do NOT use this skill when:**
- Using a standard language-specific gitignore when the folder is primarily a code repository
- Tracking binary files across the repository — use Git LFS instead of this allowlist approach
- Initializing a text-only folder where all files should be tracked — use `git init` directly

---

## Related Skills

- **`git-initial-setup`** — Standard git setup and branch protection for conventional repositories
- **`git-init-to-github`** — Initialize a local directory as a git repo and push to GitHub
- **`git-commit-practices`** — Conventional commit standards for tracking ops folder changes

---

## Core Principles

1. **Allowlist over blocklist** — "Ignore everything, allow only what you intend" prevents accidental commits of sensitive or large files (基礎と型の追求)
2. **Explicit intent** — Every tracked file type is a conscious decision, creating intentional structure (余白の設計)
3. **Knowledge-layer separation** — Binary documents contain "what"; scripts and Markdown contain "how and why" — only the latter grows in value under version control (温故知新)
4. **Safe for non-developers** — Simple rules that anyone can understand and maintain (成長の複利)

---

## How It Works: Allowlist vs. Blocklist

### Blocklist (traditional — fragile)
```gitignore
# Problems:
# 1. New file types you didn't think of get tracked accidentally
# 2. Requires updating whenever new binary types are introduced
*.xlsx
*.pdf
*.png
# ... never-ending list
```

### Allowlist (this skill's approach — robust)
```gitignore
# Ignore everything by default
*
# Allow directory traversal
!*/
# Allow ONLY what you explicitly want
!*.md
!*.py
!*.ps1
# Done. Anything not listed is automatically ignored.
```

**Key insight**: With the allowlist approach, **adding a new file type accidentally is impossible**. You must explicitly opt in. This is why it is safer in operational folders where new binary file types appear unpredictably.

---

## Workflow:

### Step 1: Assess the Folder

> **Values**: 余白の設計 — Assess deliberately before committing to a structure.

Before initializing, answer these questions:

| Question | Guidance | Action |
|----------|---------|--------|
| What text-based files do you want to track? | See [Allowlist Customization](#allowlist-customization) below | Enumerate extensions for allowlist |
| Are there sensitive files (credentials, PII (Personally Identifiable Information))? | Add them to the allowlist exclusions | Explicitly block with `.gitignore` blocklist section |
| Is this a network drive (UNC (Universal Naming Convention) path)? | See [Network Drive Setup](#network-drive-setup) below | Run `safe.directory` config first |
| Do you need a remote/GitHub? | This skill covers local git only | Use `git-init-to-github` for remote |

### Step 2: Create .gitignore

> **Values**: 基礎と型の追求 — The `.gitignore` template is the pattern that protects all subsequent work.

Create a `.gitignore` file in the folder root using the template below.
Customize the allowlist for your use case (see [Customization](#allowlist-customization)).

### Step 3: Initialize Git

> **Values**: 継続は力 — Initialize once, configure correctly, maintain consistently from day one.

```powershell
# Navigate to the folder
Set-Location "path\to\your\folder"

# Initialize git
git init

# Configure identity (if not set globally)
git config user.name "Your Name"
git config user.email "your@email.com"
```

### Step 4: Initial Commit

> **Values**: 温故知新 — Commit your intentions clearly; future team members will read this as the origin of the knowledge structure.

```powershell
# Stage only the .gitignore and your knowledge files
git add .gitignore
git add ".github/"   # if you have skills/agents here

# Verify what will be committed (should be only text files)
git status
git add --dry-run .  # confirms no binaries sneak in

# Commit
git commit -m "chore: initialize git with knowledge-artifacts-only tracking

Allowlist-based .gitignore ensures only Markdown, scripts, and
config files are tracked. Binary files (Office, PDF, media) are
intentionally excluded.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Step 5: Verify

> **Values**: ニュートラルな視点 — Verify objectively that only intended files are tracked before pushing.

```powershell
# Confirm tracked files look correct
git ls-files

# Confirm binary files are NOT tracked
git check-ignore -v some-document.xlsx   # should output: ignored
```

---

## Allowlist Template

Copy and customize this `.gitignore` for your operational or business folder.

The **directory-based allowlist** tracks ONLY files inside explicitly named hidden tool/config directories (`.github/`, `.claude/`, etc.). Everything else — business documents, Excel files, PDFs, images — is automatically ignored.

This design is intentional: hidden directories (names starting with `.`) are not visible in Windows Explorer by default, so only tool configurations end up under version control. Business files in normal subfolders are never touched.

```gitignore
# ============================================================
# Git Allowlist: Tool/Config Directories Only
# Pattern: Ignore everything; allow only explicitly named hidden directories.
# Add new tool directories by adding "!.yourdir/**" lines below.
# ============================================================

# Default: ignore everything
*

# Allow directory traversal (required for allowlist to work)
!*/

# ── AI / Tool Configuration Directories ──────────────────────
# Only files inside these hidden directories are tracked.
# Business document folders (.xlsx, .pdf, etc.) are completely untouched.
!.github/**    # GitHub Actions, Skills, Copilot config
!.claude/**    # Claude / Anthropic agent config
!.codex/**     # OpenAI Codex config
!.cursor/**    # Cursor IDE config

# ── Root-level Config Files ───────────────────────────────────
!.gitignore
!.gitattributes
```

---

## Allowlist Customization

### Adding More Tool Directories

Add a line for each additional hidden directory you want to track:

```gitignore
# Add to template:
!.vscode/**    # VS Code workspace config
!.copilot/**   # GitHub Copilot config
```

### Manufacturing / Quality (IATF, ISO)
```gitignore
# Use the template above as-is.
# PDFs, Excel, Word documents in business subfolders are intentionally excluded.
# Place all skills and knowledge docs inside .github/skills/ or .claude/
```

---

## Network Drive Setup

When initializing git on a **UNC (Universal Naming Convention) path** (Windows network share like `\\server\share\folder`):

```powershell
# Git requires explicit trust for network drives
# Run this ONCE for your specific path:
git config --global --add safe.directory '%(prefix)///server/share/folder'

# Or to trust all network drives (less secure, use with caution):
# git config --global --add safe.directory '*'
```

**Why this is needed**: Git 2.35.2+ requires explicit trust for directories whose ownership cannot be verified (network drives have no local ownership records).

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Running `git add .` before creating `.gitignore` | Binary files get committed on first commit; cleanup requires `git rm --cached` to implement removal | Always create and commit `.gitignore` first, then use `git add --dry-run .` to verify |
| Missing `!*/` in allowlist | Subdirectories are not traversed; only root-level files are visible | Add `!*/` on its own line before any `!*.ext` entries to implement directory traversal |
| Allowlist pattern `!*.*` | Negates the allowlist entirely — all files become tracked | Use explicit extension patterns `!*.md`, `!*.py` to define each allowed file type method |
| Not running `safe.directory` on UNC path | Git refuses to initialize with "unsafe repository" error | Run `git config --global --add safe.directory '%(prefix)///server/share'` before `git init` |

- Use `git add --dry-run .` before every first commit to verify only intended files are staged
- Implement the allowlist `.gitignore` before running `git init`, not after
- Create `.gitignore` as the very first committed file to define the tracking function
- Avoid `git add .` without verifying the dry-run output first
- Consider `safe.directory` configuration before attempting git init on a UNC network drive
- Define the complete allowlist before committing any project files

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead | Why |
|----------|--------------|-----|
| Use a blocklist (exclude specific types) | Use this allowlist template | Blocklists have gaps; new binary types get accidentally tracked |
| Track large binary files | Exclude them; use Git LFS if needed | Binary files bloat the repository and don't diff meaningfully |
| Use `git add .` without dry-run check first | Run `git add --dry-run .` to preview | Verify nothing unexpected is staged, especially on first commit |
| Skip the `.gitignore` | Always create `.gitignore` before first commit | Adding `.gitignore` after first commit requires `git rm --cached` cleanup |
| Use `!*.*` to "allow all files" | Explicitly list each extension | `!*.*` breaks the allowlist entirely |
| Commit passwords or credentials | Add secret files to blocklist section | Even with allowlist, manually exclude `.env`, `secrets.yml`, etc. |

---

## Quick Reference

### When to Use Which Approach

| Scenario | Approach | Skill |
|----------|----------|-------|
| Business/ops folder with mixed content | Allowlist-based .gitignore | This skill |
| Pure code repository | Language-specific .gitignore | `git-initial-setup` |
| Need to track binary files | Git LFS + standard .gitignore | Git LFS docs |
| Push to GitHub after local setup | Remote repository setup | `git-init-to-github` |

---

**Q: Why does `git status` show untracked directories even though their files should be ignored?**
A: With `!*/`, directories themselves are not ignored, so git shows them when they contain content. This is cosmetic — running `git add --dry-run .` confirms only allowed file types would actually be staged.

**Q: I added a new script type (e.g., `.bat`) — do I need to change anything?**  
A: Yes — add `!*.bat` to your `.gitignore` allowlist. That's the point: you explicitly opt in to new types.

**Q: Can I track one specific binary file as an exception?**  
A: Yes — add `!specific-file.pdf` to the allowlist. Wildcards and exact filenames both work.

**Q: How do I check what's currently being tracked?**  
A: Run `git ls-files` to see all tracked files.

**Q: This skill covers local git only — how do I add a GitHub remote?**  
A: After setup, use the `git-init-to-github` skill for GitHub integration.

**Q: Does this work on macOS/Linux network shares (NFS, SMB)?**  
A: The `.gitignore` content is OS-agnostic. The `safe.directory` workaround is Windows-specific.
