---
name: dotnet-skill-deploy
description: >
  Deploy selected dotnet skills to a project's .github/skills/ directory.
  Use when setting up a new .NET project, onboarding a team to dotnet skills,
  or updating project-level skills from the skills_repository.
allowed-tools:
  - powershell
metadata:
  author: RyoMurakami1983
  tags: [dotnet, deployment, skills, project-setup, automation]
  invocable: false
---

# Deploy Dotnet Skills to Project

Interactive workflow for deploying selected dotnet skills from `skills_repository/dotnet/` to a target project's `.github/skills/` directory. The agent guides the user through project analysis, category selection, and execution via `Deploy-DotnetSkills.ps1`.

## When to Use This Skill

Use this skill when:
- Setting up a new .NET project that needs relevant dotnet skills deployed
- Onboarding a team member who needs project-level coding standards
- Updating project-level skills from the latest skills_repository
- Responding to "dotnet skills をプロジェクトに追加して" or "deploy skills to my project"
- Starting a new WPF, Blazor, or class library project with standardized patterns

## Related Skills

- **`dotnet-modern-csharp-coding-standards`** — One of the foundation skills frequently deployed
- **`dotnet-wpf-mvvm-patterns`** — WPF MVVM foundation skill
- **`dotnet-project-structure`** — Project structure skill
- **`git-initial-setup`** — Often used alongside skill deployment for new projects

---

## Dependencies

- PowerShell 5.1+ (Windows)
- `skills_repository` cloned locally (typically at `C:\tools\skills_repository`)

## Core Principles

1. **Selective Deployment** — Copy only relevant skills to avoid agent context noise (余白の設計)
2. **Category-Driven Selection** — Use predefined categories aligned with `dotnet-shihan` jurisdiction for consistent grouping (基礎と型)
3. **Idempotent Operations** — Safe to re-run; existing skills are skipped unless `-Force` is specified (継続は力)
4. **Transparency First** — Always show what will be deployed before executing; support `-WhatIf` for dry runs (ニュートラルな視点)

---

## Workflow: Deploy Dotnet Skills

### Step 1 — Confirm Project Information

Gather deployment context from the user:

1. **Target project path**: Confirm where `.github/skills/` should be created
2. **Project type**: Identify the project category to recommend skills

```
Questions to ask:
- "Which project should I deploy skills to? (provide the project root path)"
- "What type of .NET project is this?"
  Options: WPF application, Class library, Blazor app, Console app, Other
```

**Output**: Target path and project type confirmed.

> **Values**: ニュートラルな視点（先入観なく、プロジェクトの実態に合わせる）

### Step 2 — Recommend Categories and Skills

Based on the project type, recommend appropriate skill categories:

| Project Type | Recommended Categories | Typical Skill Count |
|-------------|----------------------|-------------------|
| WPF Application | `wpf-app` (composite) | 15 |
| Class Library | `foundation` + `data` | 8 |
| Blazor App | `foundation` + `testing` (playwright) | 12 |
| Console App | `foundation` | 5 |
| Full Stack | `all` | 31 |

**Run `-List` to show all options**:

```powershell
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -List
```

**Available categories** (aligned with `dotnet-shihan.agent.md`):

| Category | Count | Description |
|----------|-------|-------------|
| `foundation` | 5 | Technical foundation (modern-csharp, type-design, project-structure, slopwatch, api-design) |
| `data` | 3 | Data & persistence (efcore, database-performance, serialization) |
| `testing` | 7 | Concurrency, testing & CI (concurrency, testcontainers, snapshot-testing, verify-email, crap-analysis, playwright-blazor, playwright-ci-caching) |
| `wpf` | 11 | WPF & desktop (mvvm, secure-config, oracle, dify, UI components, matching) |
| `infra` | 6 | Infrastructure & packages (DI, configuration, local-tools, package-management, marketplace, mjml) |
| `wpf-app` | 15 | **Composite**: foundation subset + wpf + infra subset |
| `all` | 31 | All dotnet skills |

Present the recommendation and let the user adjust:

```
"For a WPF application, I recommend the 'wpf-app' category (15 skills).
This includes coding standards, MVVM patterns, secure config, and all WPF UI components.
Would you like to proceed, or adjust the selection?"
```

**Output**: Selected categories and/or individual skills confirmed.

> **Values**: 基礎と型（カテゴリが選択の型を提供）/ 成長の複利（必要なスキルだけで精度向上）

### Step 3 — Execute Deployment

Run the deployment script with confirmed parameters:

**Category deployment**:

```powershell
# Why: category deployment is the recommended default — ensures consistent skill sets
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category>
```

**Individual skills deployment**:

```powershell
# Why: use individual selection when only specific skills are needed
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Skills <skill1>,<skill2>,<skill3>
```

**For updates (overwrite existing)**:

```powershell
# Why: -Force ensures latest skill versions replace outdated copies
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category> `
    -Force
```

**Important**: Always run with `-WhatIf` first if the user wants to preview:

```powershell
# Why: preview prevents accidental overwrites and confirms scope
& "<skills_repository>\skills\dotnet-skill-deploy\scripts\Deploy-DotnetSkills.ps1" `
    -SourceRoot "<skills_repository>\dotnet" `
    -Target "<project_path>" `
    -Category <selected_category> `
    -WhatIf
```

**Output**: Skills copied to `<project_path>\.github\skills\`.

> **Values**: 継続は力（繰り返し実行可能な自動化）

### Step 4 — Verify and Guide Next Steps

After deployment, verify and provide guidance:

1. **Verify deployment**: List the deployed skills directory

```powershell
Get-ChildItem "<project_path>\.github\skills" -Directory | Select-Object Name
```

2. **Advise on git tracking**: The user decides whether to git-track the deployed skills

```
"Skills have been deployed to .github/skills/.
These skills are NOT git-tracked by default.
If you want to track them in your project repository, run:
  git add .github/skills/
  git commit -m 'feat: add dotnet skills for project-level guidance'"
```

3. **Suggest next steps**:
   - Review deployed skills in the project
   - Run `git-initial-setup` if this is a new repository
   - Start coding with `@dotnet-shihan` referencing the deployed skills

**Output**: Deployment confirmed with actionable next steps.

> **Values**: 成長の複利（デプロイ後のアクション案内で学習を加速）

---

## Best Practices

- ✅ **Start with categories, refine with individual skills** — Use `-Category` for bulk, `-Skills` to add extras. Why: categories provide the right defaults for 80% of cases.
- ✅ **Preview first** — Always offer `-WhatIf` before actual deployment. Why: transparency builds trust and prevents accidental overwrites.
- ✅ **Deploy fewer, not more** — Extra skills add context noise for the agent. Why: Copilot's context window is finite; irrelevant skills dilute relevant guidance.
- ✅ **Update periodically** — Re-run with `-Force` when skills_repository is updated. Why: skills evolve with new patterns and best practices.
- ✅ **Match project type** — A WPF app doesn't need Blazor/Playwright skills. Why: precision > coverage for agent-assisted development.

## Anti-Patterns

- ❌ **Deploy `all` by default** → Fix: select relevant categories based on project type
- ❌ **Skip verification** → Fix: always confirm deployed skills in Step 4
- ❌ **Hardcode paths** → Fix: use `-SourceRoot` and `-Target` parameters
- ❌ **Forget `-Force` on updates** → Fix: explicitly add `-Force` when updating existing skills

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Wrong `-SourceRoot` path | "SourceRoot not found" error | Verify `skills_repository\dotnet` path exists |
| Missing `.github\skills\` directory | No skills visible to agent | Script creates it automatically; verify `-Target` path |
| Deploying without `-WhatIf` first | Unexpected files in project | Always preview first, then deploy |
| Mixing categories with overlap | Duplicate copy attempts | Script deduplicates automatically; no action needed |

---

## Quick Reference

```
# List available categories and skills
Deploy-DotnetSkills.ps1 -SourceRoot <dotnet_path> -List

# Deploy by category (preview first)
Deploy-DotnetSkills.ps1 -SourceRoot <dotnet_path> -Target <project> -Category wpf-app -WhatIf
Deploy-DotnetSkills.ps1 -SourceRoot <dotnet_path> -Target <project> -Category wpf-app

# Deploy individual skills
Deploy-DotnetSkills.ps1 -SourceRoot <dotnet_path> -Target <project> -Skills skill1,skill2

# Update existing skills
Deploy-DotnetSkills.ps1 -SourceRoot <dotnet_path> -Target <project> -Category wpf-app -Force
```

---

## Script Reference

The deployment script is located at `scripts/Deploy-DotnetSkills.ps1`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `-SourceRoot` | string | Yes | Path to dotnet skills source directory |
| `-Target` | string | For deploy | Path to target project root |
| `-Category` | string | For deploy* | Category name: foundation, data, testing, wpf, infra, wpf-app, all |
| `-Skills` | string[] | For deploy* | Comma-separated skill names |
| `-List` | switch | No | Show available categories and skills |
| `-Force` | switch | No | Overwrite existing skills |
| `-WhatIf` | switch | No | Preview without copying |

\* At least one of `-Category` or `-Skills` is required for deployment.

---

## FAQ

**Q: Where should skills_repository be cloned?**
A: The recommended location is `C:\tools\skills_repository`. The `-SourceRoot` parameter points to its `dotnet/` subdirectory.

**Q: Can I combine `-Category` and `-Skills`?**
A: Yes. The script merges both selections (deduplicates automatically).

**Q: What happens if a skill already exists in the target?**
A: Without `-Force`, it's skipped. With `-Force`, it's overwritten (deleted and re-copied).

**Q: Are copied skills git-tracked?**
A: Not automatically. The user decides whether to `git add` them.

**Q: Can I deploy production/ skills too?**
A: This skill is dotnet-specific. For production skills, copy them manually: `Copy-Item -Recurse production\* .github\skills\`.
