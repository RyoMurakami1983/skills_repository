---
name: git-ops-folder-init
description: >
  Initialize any operational or business folder as a git repository that tracks
  ONLY tool/config directories (.github, .claude, .codex, .cursor) while ignoring
  all business files (Office documents, PDFs, images, media). Uses a directory-based
  allowlist .gitignore for zero-surprise version control.
author: RyoMurakami1983
tags: [git, gitignore, allowlist, operational-folder, knowledge-management, manufacturing, business]
invocable: true
version: 1.0.0
values_alignment:
  - "基礎と型の追求: Allowlist approach prevents accidental tracking — the pattern itself is the safeguard"
  - "温故知新: Business folders already have history; git captures only the knowledge layer going forward"
  - "余白の設計: Explicit allowlist creates intentional space — only what matters is tracked"
---

# Git Ops Folder Init

Initialize an operational or business folder as a git repository that tracks **only knowledge artifacts** — Markdown documents, scripts, and configuration files — while automatically ignoring all binary files (Office documents, PDFs, images, videos, etc.).

## When to Use This Skill

Use this skill when:

- A **business or operational folder** (e.g., manufacturing records, quality documentation, project archives) needs version control for its **scripts and knowledge documents**
- The folder contains **mixed content** — some files you want to version control, most you don't
- You want **zero-surprise git management**: nothing unexpected gets committed
- Transitioning from "just files on a network drive" to **docs-as-code** for knowledge artifacts only
- Setting up git for **non-developer teams** who shouldn't worry about accidentally committing large binary files

**Do NOT use this skill when:**
- The folder is primarily a code repository (use standard language-specific gitignore instead)
- You need to track binary files (use Git LFS instead)
- All files in the folder are text-based and should be tracked (use `git init` directly)

---

## Core Principles

| Principle | Value Alignment | Why It Matters |
|-----------|----------------|----------------|
| Allowlist over blocklist | 基礎と型の追求 | "Ignore everything, allow only what you intend" prevents accidental commits of sensitive or large files |
| Explicit intent | 余白の設計 | Every tracked file type is a conscious decision, creating intentional structure |
| Knowledge-layer separation | 温故知新 | Binary documents contain the "what"; scripts and Markdown contain the "how and why" — only the latter grows in value under version control |
| Safe for non-developers | 成長の複利 | Simple rules that anyone can understand and maintain |

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

**Key insight**: With the allowlist approach, **adding a new file type accidentally is impossible**. You must explicitly opt in. This is safer in operational folders where new binary file types appear unpredictably.

---

## Setup Workflow

### Step 1: Assess the Folder

Before initializing, answer these questions:

| Question | Guidance |
|----------|---------|
| What text-based files do you want to track? | See [Allowlist Customization](#allowlist-customization) |
| Are there sensitive files (credentials, PII)? | Add them to the allowlist exclusions or use `.gitignore` to explicitly block |
| Is this a network share (UNC path)? | See [Network Drive Setup](#network-drive-setup) |
| Do you need a remote/GitHub? | This skill covers local git; use `git-init-to-github` for remote setup |

### Step 2: Create .gitignore

Create a `.gitignore` file in the folder root using the template below.
Customize the allowlist for your use case (see [Customization](#allowlist-customization)).

### Step 3: Initialize Git

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

When initializing git on a **UNC path** (Windows network share like `\\server\share\folder`):

```powershell
# Git requires explicit trust for network drives
# Run this ONCE for your specific path:
git config --global --add safe.directory '%(prefix)///server/share/folder'

# Or to trust all network drives (less secure, use with caution):
# git config --global --add safe.directory '*'
```

**Why this is needed**: Git 2.35.2+ requires explicit trust for directories whose ownership cannot be verified (network drives have no local ownership records).

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

## FAQ / Quick Reference

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
