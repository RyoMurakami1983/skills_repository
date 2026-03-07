---
name: python-skill-deploy
description: >
  Deploy selected Python skills to a project's .github/skills/ directory.
  Use when setting up a new Python project, onboarding a team to Python skills,
  or updating project-level skills from the skills_repository.
allowed-tools:
  - powershell
metadata:
  author: RyoMurakami1983
  tags: [python, deployment, skills, project-setup, automation]
  invocable: false
  tool_versions:
    powershell: ">=5.1"
  last_reviewed: "2026-03-07"
---

# Deploy Python Skills to Project

Interactive workflow for deploying selected Python skills from `skills_repository/python/` to a target project's `.github/skills/` directory.

## When to Use This Skill

Use this skill when:
- Setting up a new Python project that needs project-level Python workflow skills
- Onboarding a team member who needs Python guidance inside the target repository
- Updating an existing project with the latest Python skills from this repository
- Responding to "python skills をプロジェクトに追加して" or "deploy python skills"
- Previewing which Python skills would be copied before touching the target project

## Related Skills

- **`python-setup-dev-environment`** — Common first deployment target for Python projects
- **`python-debug-tdd`** — Optional debugging workflow that may be deployed with `all`
- **`git-initial-setup`** — Often paired with new-project bootstrap
- **`skills-validate-skill`** — Validate this skill after edits

---

## Dependencies

- PowerShell 5.1+ (`pwsh` recommended for cross-platform use)
- `skills_repository` cloned locally
- `$env:SKILLS_REPO` (PowerShell) or `$SKILLS_REPO` (bash/WSL) set to the repository root

---

## Core Principles

1. **Selective deployment** — Copy only skills that improve the target project right now (余白の設計)
2. **Category-first guidance** — Recommend a small default category before individual overrides (基礎と型)
3. **Safe re-runs** — Skip existing skills unless `-Force` makes overwrite intent explicit (継続は力)
4. **Transparent execution** — Show list/preview output before file changes so users understand scope (ニュートラル)

---

## Workflow: Deploy Python Skills

### Step 1 — Confirm Target Project and Python Context

Confirm where the skills should be deployed and what kind of Python work the project does.

```powershell
# Questions to ask before deployment
# - Which project root should receive .github/skills/?
# - Is this mainly setup/onboarding work, or do you also want debug workflows?
```

Recommended decision rule:
- Default to `dev-env` for a fresh Python project
- Use `all` only when the project wants every currently available Python project skill
- Add individual `-Skills` entries when the category is almost right but not complete

Use when starting deployment or clarifying vague requests like "add Python skills".

> **Values**: ニュートラル / 基礎と型

### Step 2 — Recommend Category or Individual Skills

Recommend the smallest useful skill set, then show the available choices.

| Project situation | Recommended selection | Why |
|---|---|---|
| New Python repository | `dev-env` | Establishes reproducible environment practices first |
| Team wants every current Python project skill | `all` | Copies all discoverable skills from `python/` |
| Team needs one extra workflow beyond the default | `-Category dev-env -Skills ...` | Keeps defaults while adding a precise exception |

```powershell
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -List
```

Current categories:

| Category | Count | Contents |
|---|---:|---|
| `dev-env` | 1 | `python-setup-dev-environment` |
| `all` | dynamic | All Python source skills currently present under `python/` |

Use when the user needs a recommendation before copying files.

> **Values**: 基礎と型 / 成長の複利

### Step 3 — Execute Deployment Safely

Run the deploy script with the confirmed selection. Offer `-WhatIf` first when the user wants a preview.

```powershell
# Preview category deployment
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env `
    -WhatIf

# Execute category deployment
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env

# Add an extra skill explicitly
& "<skills_repository>\skills\python-skill-deploy\scripts\Deploy-PythonSkills.ps1" `
    -SourceRoot "<skills_repository>\python" `
    -Target "<project_path>" `
    -Category dev-env `
    -Skills python-debug-tdd
```

For updates, add `-Force` so overwrite intent is explicit.

✅ **Good**: Run `-WhatIf` first for a new target project, then execute the same command without `-WhatIf`.
❌ **Bad**: Jump straight to `-Force` on the first run or guess the source path from memory.
Why: preview-first deployment catches path mistakes and reduces accidental overwrite risk.

Use when the target path and selection are confirmed.

> **Values**: 継続は力 / 基礎と型

### Step 4 — Verify Deployment and Guide Next Steps

Verify the deployed directories, then tell the user what to do next.

```powershell
Get-ChildItem "<project_path>\.github\skills" -Directory | Select-Object Name
```

Follow-up guidance:
1. Review the copied skills in `.github/skills/`
2. Decide whether to `git add .github/skills/`
3. Start the target project session with `@python-shihan`

Use when the copy step is complete and the user needs confirmation plus next actions.

> **Values**: 成長の複利 / ニュートラル

---

## Best Practices

- Start with `dev-env`, then add individual skills only if a real need exists.
- Offer `-WhatIf` before the first live deployment into an unfamiliar repository.
- Keep `all` dynamic so newly added Python source skills become deployable without manual duplication.
- Sync category definitions with `agents/python-shihan.agent.md` when Python project skills change.
- Re-run with `-Force` only when the user explicitly wants to replace copied skills.

---

## Common Pitfalls

1. **Using the wrong `-SourceRoot`**
   Fix: Point `-SourceRoot` to the repository's `python/` directory, not `skills/`.

2. **Deploying everything by habit**
   Fix: Default to `dev-env`; use `all` only when the team truly wants every current Python project skill.

3. **Forgetting overwrite intent during updates**
   Fix: Add `-Force` when refreshing already-copied skills.

4. **Skipping verification after copy**
   Fix: List `.github/skills/` immediately after deployment and confirm the expected directories exist.

---

## Anti-Patterns

- Copying Python skills manually from Explorer/Finder instead of using a repeatable script
- Hardcoding repository paths in the script instead of passing `-SourceRoot` and `-Target`
- Treating deployment as complete without telling the user whether the copied skills should be git-tracked

## Troubleshooting

- **`SourceRoot not found`**
  - Cause: The command points at the wrong repository path.
  - Fix: Set `$env:SKILLS_REPO` correctly and use `-SourceRoot "$env:SKILLS_REPO\python"`.

- **`Skills not found in source`**
  - Cause: The requested skill name does not match a directory under `python/`.
  - Fix: Run `-List`, copy the exact skill name, then retry.

- **No visible change in the target project**
  - Cause: The run used `-WhatIf`, or existing skills were skipped without `-Force`.
  - Fix: Check the summary output, then rerun without `-WhatIf` or with `-Force` as needed.

---

## Quick Reference

### Preflight Checklist

- [ ] `skills_repository` path is known and `python/` exists under it
- [ ] Target project root is confirmed
- [ ] Intended selection (`dev-env`, `all`, or specific `-Skills`) is confirmed
- [ ] Preview requirement (`-WhatIf`) is decided before live copy

### Self-Review Checklist

- [ ] The command uses `skills/python-skill-deploy/scripts/Deploy-PythonSkills.ps1`
- [ ] `-SourceRoot` points to `python/`, not another category directory
- [ ] The copy summary matches expected deployed skills
- [ ] The target `.github/skills/` directories were listed after deployment

### Decision Table

| Situation | Action | Why |
|---|---|---|
| New Python project with no existing skills | Deploy `dev-env` | Establish the base workflow with minimal noise |
| Team wants every current Python project skill | Deploy `all` | Mirror all currently available source skills |
| Existing copied skills need refresh | Add `-Force` | Make overwrite intent explicit |
| User is unsure about impact | Add `-WhatIf` first | Preview copy scope before changing files |

### Command Summary

```powershell
# List categories and skills
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -List

# Preview deploy
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env -WhatIf

# Deploy category
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env

# Deploy category + extra skill
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category dev-env -Skills python-debug-tdd

# Refresh existing copied skills
Deploy-PythonSkills.ps1 -SourceRoot <python_path> -Target <project> -Category all -Force
```

---

## Resources

- [PowerShell documentation](https://learn.microsoft.com/powershell/)
- [uv documentation](https://docs.astral.sh/uv/)
- [Python Setup Dev Environment](../../python/python-setup-dev-environment/SKILL.md)
- [Deploy Dotnet Skills to Project](../dotnet-skill-deploy/SKILL.md)
