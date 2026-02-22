---
name: dotnet-local-tools
description: >
  Managing local .NET tools with dotnet-tools.json for consistent, version-pinned tooling
  across development environments and CI/CD pipelines. Use when setting up or maintaining
  per-repository CLI tools.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, cli-tools, dotnet-tools-json, ci-cd, devops]
  invocable: false
  version: 1.0.0
---

# .NET Local Tools

Per-repository CLI tool management with `.config/dotnet-tools.json`: manifest initialization, tool installation, version pinning, CI/CD integration, and lifecycle maintenance.

## When to Use This Skill

Use this skill when:

- Setting up consistent CLI tooling across a development team via a shared manifest
- Ensuring CI/CD pipelines restore and use the same tool versions as local development
- Installing project-specific tools such as docfx, dotnet-ef, csharpier, or reportgenerator
- Avoiding global tool version conflicts between multiple projects on one machine
- Migrating from globally installed tools to per-repository local tool management
- Configuring Dependabot or Renovate to automate local tool version updates
- Troubleshooting tool-not-found errors after running dotnet tool restore

---

## Related Skills

- **`dotnet-project-structure`** — Solution setup with .slnx, Directory.Build.props, and global.json
- **`git-commit-practices`** — Commit each tool addition as an atomic change
- **`tdd-standard-practice`** — Validate tool outputs with automated tests

---

## Core Principles

1. **Per-Repository Isolation** — Each project owns its toolset; no global state leaks between repositories (基礎と型)
2. **Reproducible Tooling** — Exact versions are pinned in the manifest so every environment restores identical tools (基礎と型)
3. **Single Restore Command** — `dotnet tool restore` replaces N individual install commands in CI/CD (成長の複利)
4. **Progressive Adoption** — Start with one tool, add more as needed; the manifest grows incrementally (継続は力)
5. **Transparent Configuration** — `dotnet-tools.json` is human-readable JSON committed to source control (温故知新)

---

## Workflow: Manage .NET Local Tools

### Step 1 — Initialize the Tool Manifest

Use when creating a new repository or adding local tool support to an existing project.

```bash
# Create .config/dotnet-tools.json
dotnet new tool-manifest
```

This creates the manifest directory structure:

```
.config/
└── dotnet-tools.json
```

**Initial manifest content:**

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {}
}
```

| Field | Description | Default |
|-------|-------------|---------|
| `version` | Manifest schema version | `1` |
| `isRoot` | Prevents searching parent directories | `true` |
| `tools` | Dictionary of tool configurations | `{}` |

**Why `isRoot: true`**: Without this flag, MSBuild walks up the directory tree looking for additional manifests, causing unexpected tool resolution.

> **Values**: 基礎と型（manifest provides the structural foundation for all tooling） / 余白の設計

### Step 2 — Install Tools Locally

Use when adding project-specific CLI tools to the repository manifest.

```bash
# Install a tool locally (latest version)
dotnet tool install docfx

# Install a specific version
dotnet tool install docfx --version 2.78.3

# Install from a private feed
dotnet tool install MyTool --add-source https://pkgs.dev.azure.com/org/_packaging/feed/nuget/v3/index.json
```

**Common tools for .NET projects:**

| Tool | Package Name | Command | Purpose |
|------|-------------|---------|---------|
| DocFX | `docfx` | `dotnet docfx` | API documentation generation |
| EF Core CLI | `dotnet-ef` | `dotnet ef` | Database migrations |
| ReportGenerator | `dotnet-reportgenerator-globaltool` | `dotnet reportgenerator` | Code coverage reports |
| CSharpier | `csharpier` | `dotnet csharpier` | Opinionated C# formatting |
| Incrementalist | `incrementalist.cmd` | `incrementalist` | Build only changed projects |

Each `dotnet tool install` command automatically updates `dotnet-tools.json`.

> **Values**: 継続は力（add tools one at a time, building the manifest incrementally） / 基礎と型

### Step 3 — Configure Version Pinning

Use when ensuring reproducible tool versions across all environments.

**Example manifest with pinned versions:**

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "docfx": {
      "version": "2.78.3",
      "commands": ["docfx"],
      "rollForward": false
    },
    "dotnet-ef": {
      "version": "9.0.0",
      "commands": ["dotnet-ef"],
      "rollForward": false
    },
    "dotnet-reportgenerator-globaltool": {
      "version": "5.4.1",
      "commands": ["reportgenerator"],
      "rollForward": false
    },
    "csharpier": {
      "version": "0.30.3",
      "commands": ["dotnet-csharpier"],
      "rollForward": false
    }
  }
}
```

| Field | Description | Recommended |
|-------|-------------|-------------|
| `tools.<name>.version` | Exact version to install | Pin explicitly |
| `tools.<name>.commands` | CLI commands the tool provides | From NuGet |
| `tools.<name>.rollForward` | Allow newer versions | `false` |

**Why `rollForward: false`**: Ensures every developer and CI agent uses the exact same tool version, preventing "works on my machine" issues.

> **Values**: 基礎と型（version pinning eliminates environment drift） / ニュートラルな視点

### Step 4 — Integrate with CI/CD

Use when configuring automated pipelines to restore and use local tools.

**GitHub Actions:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          global-json-file: global.json

      - name: Restore tools
        run: dotnet tool restore

      - name: Format check
        run: dotnet csharpier --check .

      - name: Build and test
        run: dotnet build && dotnet test --collect:"XPlat Code Coverage"

      - name: Generate coverage report
        run: dotnet reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coveragereport
```

**Azure Pipelines:**

```yaml
steps:
  - task: UseDotNet@2
    inputs:
      useGlobalJson: true

  - script: dotnet tool restore
    displayName: 'Restore .NET tools'

  - script: dotnet csharpier --check .
    displayName: 'Format check'

  - script: dotnet build -c Release && dotnet test -c Release --collect:"XPlat Code Coverage"
    displayName: 'Build and test'
```

**Why restore before use**: Local tools are not available until `dotnet tool restore` runs. Skipping this step causes "command not found" errors in CI.

> **Values**: 成長の複利（CI automation compounds quality across every build） / 基礎と型

### Step 5 — Maintain Tool Versions

Use when updating, listing, or removing tools from the repository manifest.

**Update tools:**

```bash
# Update to latest version
dotnet tool update docfx

# Update to specific version
dotnet tool update docfx --version 2.79.0
```

**List installed tools:**

```bash
# List local tools and versions
dotnet tool list

# Check for outdated tools
dotnet tool list --outdated
```

**Remove a tool:**

```bash
dotnet tool uninstall docfx
```

**Automate updates with Dependabot:**

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot automatically detects `.config/dotnet-tools.json` and creates pull requests for tool version updates.

> **Values**: 継続は力（regular updates keep tooling current） / 余白の設計

---

## Good Practices

### 1. Restore Tools as the First CI Step

**What**: Run `dotnet tool restore` immediately after SDK setup, before any build or test step.

- Use `dotnet tool restore` as the first step after SDK setup
- Avoid invoking tools before restore completes

**Why**: Local tools are unavailable until restored; later steps that invoke tools will fail silently or with cryptic errors.

**Values**: 基礎と型（reliable CI starts with a complete environment）

### 2. Run Format Checks in CI

**What**: Use `dotnet csharpier --check .` in CI to enforce consistent formatting without modifying files.

- Apply formatting checks in CI before merge
- Consider `--check` mode to avoid modifying files in pipelines

**Why**: Catches formatting drift early and keeps code reviews focused on logic rather than style.

**Values**: 成長の複利（automated formatting compounds code consistency）

### 3. Document Tool Requirements in README

**What**: Add a "Development Setup" section listing `dotnet tool restore` as a prerequisite.

- Define setup steps in README for new contributors
- Use a single restore command to simplify onboarding

**Why**: New team members can set up their environment with a single command instead of hunting for tool installation instructions.

**Values**: ニュートラルな視点（universally accessible onboarding）

---

## Common Pitfalls

### 1. Running Tools from a Subdirectory

**Problem**: Invoking a local tool from a subdirectory where the manifest is not found.

**Solution**: Always run local tool commands from the repository root where `.config/dotnet-tools.json` exists.

```bash
# ❌ WRONG — running from subdirectory
cd src/MyApp
dotnet docfx  # Error: tool not found

# ✅ CORRECT — run from solution root
cd ../..
dotnet docfx docs/docfx.json
```

### 2. Version Conflicts with Global Tools

**Problem**: A globally installed tool shadows the local version, causing unexpected behavior.

**Solution**: Check for global tool conflicts with `dotnet tool list -g` and uninstall the global version.

```bash
# ❌ WRONG — global and local versions coexist
dotnet tool install -g docfx           # global v2.77.0
dotnet tool install docfx --version 2.78.3  # local v2.78.3

# ✅ CORRECT — remove global, use local only
dotnet tool uninstall -g docfx
dotnet tool restore
```

### 3. Forgetting Tool Restore in CI

**Problem**: CI pipeline invokes tools without restoring them first, causing "command not found" errors.

**Solution**: Add `dotnet tool restore` as an explicit step before any tool usage.

---

## Anti-Patterns

### Using Global Tools for Project-Specific Tooling

**What**: Installing all CLI tools globally with `dotnet tool install -g` instead of using the local manifest.

**Why It's Wrong**: Global tools create version conflicts between projects, cannot be version-controlled, and require manual installation on every developer machine and CI agent.

**Better Approach**: Use `dotnet new tool-manifest` and `dotnet tool install` (without `-g`) to create a per-repository manifest that is committed to source control.

### Allowing Version Roll-Forward

**What**: Setting `"rollForward": true` or omitting the field to allow automatic version upgrades.

**Why It's Wrong**: Different environments may resolve different tool versions, breaking build reproducibility and causing intermittent CI failures.

**Better Approach**: Always set `"rollForward": false` and update versions explicitly with `dotnet tool update`.

---

## Quick Reference

### Local vs Global Tools Decision Table

| Aspect | Global Tools | Local Tools |
|--------|-------------|-------------|
| Installation | `dotnet tool install -g` | `dotnet tool restore` |
| Scope | Machine-wide | Per-repository |
| Version control | Manual tracking | `.config/dotnet-tools.json` |
| CI/CD setup | Install each tool individually | Single `dotnet tool restore` |
| Version conflicts | Possible between projects | Isolated per project |
| Recommendation | Avoid for projects | ✅ Use for all project tools |

### Common Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `dotnet new tool-manifest` | Initialize manifest | New repository setup |
| `dotnet tool install <name>` | Add tool to manifest | Adding a new tool |
| `dotnet tool restore` | Restore all tools | After clone or CI start |
| `dotnet tool update <name>` | Update tool version | Version bump needed |
| `dotnet tool list` | List installed tools | Audit current tools |
| `dotnet tool list --outdated` | Check for updates | Periodic maintenance |
| `dotnet tool uninstall <name>` | Remove tool | Tool no longer needed |

---

## Resources

- [.NET Local Tools Overview](https://learn.microsoft.com/en-us/dotnet/core/tools/local-tools-how-to-use) — Official local tools documentation
- [dotnet tool install](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-tool-install) — Tool installation reference
- [dotnet-tools.json Schema](https://learn.microsoft.com/en-us/dotnet/core/tools/local-tools-how-to-use#tool-manifest-file) — Manifest file format
- [Dependabot for .NET](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) — Automated tool version updates

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
