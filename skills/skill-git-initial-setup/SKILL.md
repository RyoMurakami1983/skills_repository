---
name: skill-git-initial-setup
description: Default git setup to protect main after git init/clone. Use when standardizing repo bootstrap.
author: RyoMurakami1983
tags: [git, github, branch-protection, hooks, bootstrap]
invocable: false
version: 1.2.0
---

# Git Initial Setup for Main Protection

Standardize main-branch protection for repositories created by git init/clone. Combine GitHub branch protection (Option A) with global hook defaults and local pre-commit/pre-push hooks (Option B) for defense in depth.

## When to Use This Skill

Use this skill when:
- Defining default protections for new repos created by git init/clone
- Rolling out global hook defaults across developer machines
- Enforcing Pull Request (PR)-only merges for main in team repositories
- Preventing accidental commits/pushes during release preparation
- Adding local safeguards for private repos without protection rules
- Auditing protection coverage before a major release

## Related Skills

- **`skill-git-japanese-practices`** - Git workflow and code review practices
- **`skill-writing-guide`** - Skill documentation standards
- **`skill-quality-validation`** - Validate skill quality

---

## Dependencies

- Git 2.30+ (required)
- Bash or PowerShell (for hook scripts)
- GitHub account with repo admin access (for branch protection rules)

## Core Principles

1. **Defense in Depth** - Combine server-side and local protections (基礎と型)
2. **Least Privilege** - Minimize who can push to main
3. **Clear Workflow** - Make PR-only flow explicit (成長の複利)
4. **Transparent Exceptions** - Document emergency paths (ニュートラル)
5. **Automation First** - Reduce human error with repeatable scripts (継続は力)

---

## Pattern 1: Baseline Branch Protection Rule

### Overview

Create a minimal branch protection rule for main that requires pull requests.

### Basic Example

```txt
# ✅ CORRECT - Require PRs for main
Settings > Branches > Add rule
Branch name pattern: main
Enable: Require a pull request before merging

# ❌ WRONG - Leaving main unprotected
No branch protection rule set
```

### Intermediate Example

- Require 1 approval
- Require review from Code Owners
- Require conversation resolution

### Advanced Example

- Include administrators
- Require linear history
- Restrict who can push to matching branches (empty list blocks direct pushes)

Why: PR-only merges create traceability and reduce accidental changes.

### When to Use

| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Small team repo | Basic rule | Fast protection with minimal overhead |
| Larger teams | Intermediate | Adds review accountability |
| Regulated environments | Advanced | Strong enforcement and auditability |

**Values**: 基礎と型 / 継続は力

---

## Pattern 2: Pull Request Review Standards

### Overview

Define review requirements so main merges are intentional and traceable.

### Basic Example

- Require 1 approval
- Assign default reviewers

### Intermediate Example

- Enable Code Owners
- Dismiss stale approvals on new commits

### Advanced Example

- Require Code Owner review for protected paths
- Require all conversations to be resolved

### When to Use

- You need accountability for every main merge
- You want consistent review quality across teams

**Values**: 成長の複利 / ニュートラル

---

## Pattern 3: Required Status Checks

### Overview

Gate merges on continuous integration (CI) checks so broken builds never land in main.

### Basic Example

- Require a single build check (e.g., `ci/build`)

```yaml
# ✅ CORRECT - Require build + test checks
required_status_checks:
  - ci/build
  - ci/test

# ❌ WRONG - No required checks
required_status_checks: []
```

Why: Checks stop broken changes before they reach main.

### Intermediate Example

- Require tests + lint checks
- Require branches to be up to date before merging

### Advanced Example

- Separate required checks by platform
- Add release-specific checks for protected tags

Why: Required checks keep main green and reduce rollback risk.

### When to Use

| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Fast-moving repo | Basic | Keeps velocity without sacrificing quality |
| Production services | Intermediate | Prevents regressions |
| Multi-platform apps | Advanced | Ensures cross-platform stability |

**Values**: 継続は力 / 基礎と型

---

## Pattern 4: Restrict Push Access and Admin Coverage

### Overview

Limit direct push access and ensure protections apply to administrators.

### Basic Example

- Enable "Include administrators"

### Intermediate Example

- Restrict who can push to matching branches
- Allow only release automation accounts

### Advanced Example

- Document emergency bypass process
- Require written approval for admin bypass

### When to Use

- You need strong guarantees that main is protected
- You operate in regulated or audited environments

**Values**: ニュートラル / 基礎と型

---

## Pattern 5: Local Pre-commit/Pre-push Hooks (Option B)

### Overview

Install local hooks to block commits and pushes to main before changes reach the remote.

### Basic Example

```bash
# ✅ CORRECT - Install hooks for this repo
./scripts/setup.sh

# ❌ WRONG - Expecting hooks to run without installation
git push origin main
```

This installs both pre-commit and pre-push hooks.

### Intermediate Example

Customize protected branches:

```bash
protected_branches=("main" "release")
```

### Advanced Example

Use a shared Git template so new repos inherit the hook automatically.

Why: Local hooks prevent mistakes before they reach the remote.

### When to Use

- Private repos without branch protection rules
- Local safety net for new contributors
- Block commits on main during release windows
- Temporary protection before GitHub settings are configured

**Values**: 継続は力 / 基礎と型

---

## Pattern 6: Git Init/Clone Defaults (Global Hooks)

### Overview

Configure global hook defaults so new repositories inherit protections automatically.

### Basic Example

Set a global hooks path (applies to existing repos too):

```bash
# ✅ CORRECT - Use a global hooks directory
git config --global core.hooksPath "~/.githooks"
```

Why: core.hooksPath enforces hooks across repos on the same machine.

### Intermediate Example

Use an init template for git init (new repos only):

```bash
# ✅ CORRECT - Init template for new repos
git config --global init.templateDir "~/.git-template"
mkdir -p ~/.git-template/hooks
cp scripts/pre-commit scripts/pre-push ~/.git-template/hooks/
```

Why: init.templateDir ensures new repos inherit hooks by default.

### Advanced Example

Provide a team bootstrap script that sets core.hooksPath and copies hooks once.

```python
# ✅ CORRECT - Bootstrap hooks for a workstation
import shutil
from pathlib import Path

# Dependencies: Python 3.9+, Git 2.30+
hooks_dir = Path.home() / ".githooks"
hooks_dir.mkdir(parents=True, exist_ok=True)
shutil.copy("scripts/pre-commit", hooks_dir / "pre-commit")
shutil.copy("scripts/pre-push", hooks_dir / "pre-push")
```

Why: One-time bootstrap reduces manual setup errors.

Optional automation tool (with dependency injection):

```csharp
// ✅ CORRECT - Inject hook settings for a bootstrap tool
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

services.Configure<HookOptions>(config.GetSection("Hooks"));
services.AddSingleton<HookInstaller>();
```

### When to Use

- You want git init/clone to pick up protections by default
- You manage multiple repositories across the same workstation

**Values**: 基礎と型 / 継続は力

---

## Pattern 7: Team Rollout Strategy

### Overview

Roll out protections with clear communication and onboarding steps.

### Basic Example

- Announce the PR-only policy
- Share the setup scripts
- Update onboarding docs

### Intermediate Example

- Add a PR checklist template
- Record protection settings in a runbook

### Advanced Example

- Review protection settings quarterly
- Audit repos for missing protections

### When to Use

- You manage multiple repositories
- You need consistent protections across teams

**Values**: 成長の複利 / 継続は力

---

## Pattern 8: Troubleshooting and Emergency Procedures

### Overview

Handle common failures without disabling protections permanently.

### Basic Example

- Hook not running: verify `core.hooksPath` and executable bit

### Intermediate Example

- Branch name mismatch: confirm rule matches `main`
- CI checks missing: re-run or update required checks list

### Advanced Example

- Emergency hotfix: use a documented admin bypass with post-incident review
- Local bypass: allow `git push --no-verify` only with explicit approval

### When to Use

- Protections block an urgent fix
- Hook behavior differs across environments

**Values**: ニュートラル / 温故知新

---

## Best Practices

- Set global hook defaults before creating new repos
- Use Pull Request (PR) reviews for all main merges
- Set branch protection after the remote exists
- Require at least one approval for main merges
- Keep a written record of protection settings
- Review protections after org or team changes
- Document emergency bypass steps in a runbook

Use core.hooksPath for all repos.  
Set init.templateDir for new repos.  
Avoid direct pushes to main.

---

## Common Pitfalls

- Forgetting to include administrators in protection rules
- Allowing direct pushes for convenience and never removing it
- Relying only on local hooks for team-wide enforcement

Fix: Enable "Include administrators" and document who can push.  
Fix: Remove direct push permissions from main once PR flow is stable.  
Fix: Add GitHub branch protection to enforce team-wide rules.

---

## Anti-Patterns

- Disabling branch protection to make a quick change
- Using `--no-verify` as a default workflow
- Allowing unrestricted direct pushes to main

---

## FAQ

**Q: Can I protect private repositories on the free plan?**  
A: GitHub branch protection for private repos requires a paid plan. Use local hooks as a fallback.

**Q: Will the PowerShell hook run automatically on Windows?**  
A: Git for Windows runs hooks via Bash by default. Use the Bash hook or copy it into a shared hook path.

**Q: Does git init automatically install these hooks?**  
A: Only if you set core.hooksPath or init.templateDir globally. Otherwise, hooks are not installed by default.

**Q: Does this block admins?**  
A: Only if "Include administrators" is enabled in the branch protection rule.

---

## Quick Reference

### Pattern Summary

| Pattern | Focus | Use When |
|---------|-------|----------|
| 1 | Branch protection rule | You need PR-only merges |
| 3 | Required status checks | You need build/test gates |
| 5 | Local hooks | You need local safety nets |
| 6 | Global defaults | You want git init/clone defaults |

### Decision Table

| Situation | Recommendation | Why |
|-----------|----------------|-----|
| New repo setup | Set core.hooksPath | Default protection everywhere |
| Only new repos | Set init.templateDir | Avoid touching existing repos |
| Private repo on free plan | Use local hooks | Server rules unavailable |
| Team workflow | Enable PR-only merges | Traceable changes |

```bash
# Install hooks (pre-commit + pre-push) (macOS/Linux/Git Bash)
./scripts/setup.sh

# Install hooks (PowerShell)
.\scripts\setup.ps1

# Set global hooks path (all repos)
git config --global core.hooksPath "~/.githooks"

# Set init template (new repos only)
git config --global init.templateDir "~/.git-template"

# Verify current branch
git branch --show-current
```

---

## Resources

- [GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)

---

## Changelog

### Version 1.2.0 (2026-02-12)
- Renamed skill to git initial setup scope
- Added global hook defaults for git init/clone

### Version 1.1.0 (2026-02-12)
- Added pre-commit hook to block commits on main
- Setup scripts install pre-commit + pre-push

### Version 1.0.0 (2026-02-12)
- Initial release
- Branch protection rules + pre-push hook guidance
- Bash and PowerShell scripts included
