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

- **`skill-git-commit-practices`** - Commit workflow and conventions
- **`skill-github-pr-workflow`** - PR creation and merge flow
- **`skill-git-review-standards`** - Review quality and PR sizing
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

## Workflow: Protect Main Branch

### Step 1: Set Branch Protection Rule

Create a minimal branch protection rule for main that requires pull requests. This is the foundation — without it, anyone can push directly to main.

```txt
Settings > Branches > Add rule
Branch name pattern: main
Enable: Require a pull request before merging
```

Use when setting up any new repository or adding protection to an existing one.

> **Values**: 基礎と型 / 継続は力

### Step 2: Configure Review Requirements

Define review requirements so main merges are intentional and traceable. Enable Code Owners and dismiss stale approvals on new commits to maintain accountability.

```txt
Require a pull request before merging:
  ✅ Require approvals: 1
  ✅ Dismiss stale pull request approvals when new commits are pushed
  ✅ Require review from Code Owners
```

Use when you need accountability for every main merge and consistent review quality.

> **Values**: 成長の複利 / ニュートラル

### Step 3: Require Status Checks

Gate merges on CI checks so broken builds never land in main. Required checks keep main green and reduce rollback risk.

```yaml
required_status_checks:
  - ci/build
  - ci/test
```

Use when your repository has CI pipelines and you want to prevent regressions.

> **Values**: 継続は力 / 基礎と型

### Step 4: Restrict Push Access

Limit direct push access and ensure protections apply to administrators. Enable "Include administrators" and restrict who can push to matching branches.

```txt
✅ Include administrators
✅ Restrict who can push to matching branches
   Allowed: release-bot only
```

Use in regulated or audited environments where strong guarantees are needed.

> **Values**: ニュートラル / 基礎と型

### Step 5: Install Local Hooks

Install local pre-commit and pre-push hooks to block commits and pushes to main before changes reach the remote.

```bash
# Install hooks for this repo
./scripts/setup.sh
```

Use for private repos without branch protection rules, as a local safety net, or during release windows.

> **Values**: 継続は力 / 基礎と型

### Step 6: Set Global Hook Defaults

Configure global hook defaults so new repositories inherit protections automatically via `core.hooksPath`.

```bash
git config --global core.hooksPath "~/.githooks"
```

Use when you manage multiple repositories on the same workstation and want automatic protection.

> **Values**: 基礎と型 / 継続は力

### Step 7: Roll Out to Team

Roll out protections with clear communication: announce the PR-only policy, share setup scripts, and update onboarding docs.

```markdown
## Onboarding Checklist
- [ ] Run `./scripts/setup.sh` to install hooks
- [ ] Confirm branch protection is enabled on main
- [ ] Review PR workflow in skill-github-pr-workflow
```

Use when you manage multiple repositories or need consistent protections across teams.

> **Values**: 成長の複利 / 継続は力

### Step 8: Handle Emergencies

Handle common failures without disabling protections permanently. For emergency hotfixes, use a documented admin bypass with post-incident review.

```bash
# Emergency hotfix: bypass hook with explicit approval only
git push --no-verify origin hotfix/critical-fix
# Post-incident: review and document the bypass
```

Use when protections block an urgent fix or hook behavior differs across environments.

> **Values**: ニュートラル / 温故知新

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

### Step Summary

| Step | Focus | Use When |
|------|-------|----------|
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
