---
name: dotnet-package-management
description: >
  Manage NuGet packages using Central Package Management (CPM) and dotnet CLI commands.
  Use when adding, removing, updating, or centralizing NuGet package versions across .NET projects.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, nuget, cpm, package-management, cli]
  invocable: false
  version: 1.0.0
---

# NuGet Package Management

End-to-end workflow for managing NuGet packages in .NET solutions: Central Package Management (CPM) setup, dotnet CLI operations, shared version variables, package source configuration, and dependency auditing.

## When to Use This Skill

Use this skill when:

- Adding or removing NuGet packages from a .NET project using dotnet CLI commands
- Setting up Central Package Management (CPM) to unify versions across a solution
- Organizing related NuGet packages under shared version variables in Directory.Packages.props
- Configuring private NuGet feeds or solution-specific package sources via NuGet.Config
- Auditing outdated, vulnerable, or deprecated packages with dotnet list commands
- Updating NuGet package versions centrally without editing individual .csproj files
- Troubleshooting package restore failures by clearing caches and reviewing dependency trees

---

## Related Skills

- **`dotnet-project-structure`** — Solution-level build configuration and Directory.Build.props setup
- **`dotnet-local-tools`** — Managing local .NET tools with dotnet-tools.json manifest
- **`dotnet-slopwatch`** — Detecting slop patterns including unnecessary VersionOverride usage
- **`git-commit-practices`** — Commit each package change as an atomic Conventional Commit

---

## Core Principles

1. **CLI-First Operations** — Always use `dotnet add/remove/list` commands instead of editing XML manually; the CLI validates packages, resolves versions, and updates lock files (基礎と型)
2. **Single Source of Truth** — Centralize all package versions in `Directory.Packages.props` so every project references one authoritative version registry (基礎と型)
3. **Grouped Version Variables** — Related packages share a single version variable to prevent drift between packages that must stay in sync (継続は力)
4. **Audit Before Deploy** — Run `dotnet list package --outdated --vulnerable --deprecated` regularly to catch security and compatibility issues early (温故知新)
5. **Reproducible Restores** — Pin package sources in `NuGet.Config` with `<clear />` and use lock files so every environment produces identical dependency graphs (ニュートラル)

---

## Workflow: Manage NuGet Packages

### Step 1 — Enable Central Package Management

Use when centralizing all NuGet package versions into a single `Directory.Packages.props` file.

**Prerequisites:**

| Requirement | Minimum Version |
|-------------|-----------------|
| .NET SDK | 6.0.300 |
| NuGet | 6.2 |
| Visual Studio | 2022 17.2 |

Create `Directory.Packages.props` at the solution root:

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="Serilog" Version="4.0.0" />
    <PackageVersion Include="xunit" Version="2.9.2" />
  </ItemGroup>
</Project>
```

**Project files** reference packages without versions:

```xml
<!-- src/MyApp/MyApp.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" />
    <PackageReference Include="Serilog" />
  </ItemGroup>
</Project>
```

**Why CPM**: Eliminates version drift across projects. Updating one line in `Directory.Packages.props` propagates to every project that consumes the package.

> **Values**: 基礎と型（single source of truth for all package versions） / ニュートラル

### Step 2 — Add and Remove Packages via CLI

Use when installing or uninstalling NuGet packages in a project. Never edit `.csproj` or `Directory.Packages.props` XML by hand.

**Adding packages:**

```bash
# Add latest stable version
dotnet add package Serilog

# Add specific version
dotnet add package Serilog --version 4.0.0

# Add prerelease package
dotnet add package Serilog --prerelease

# Add to a specific project
dotnet add src/MyApp/MyApp.csproj package Serilog
```

**With CPM enabled**, `dotnet add package` updates both `Directory.Packages.props` and the project file automatically.

**Removing packages:**

```bash
# Remove from current project
dotnet remove package Serilog

# Remove from specific project
dotnet remove src/MyApp/MyApp.csproj package Serilog
```

**Why CLI-first**: The CLI validates that the package exists on the feed, resolves the correct version, handles transitive dependencies, and updates lock files. Manual XML editing risks typos, missing packages, and malformed markup.

> **Values**: 基礎と型（CLI validates what manual edits cannot） / 温故知新

### Step 3 — Organize with Shared Version Variables

Use when multiple related packages must stay at the same version to avoid runtime incompatibilities.

Define version properties and reference them in `Directory.Packages.props`:

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <!-- Shared version variables -->
  <PropertyGroup Label="SharedVersions">
    <AkkaVersion>1.5.59</AkkaVersion>
    <OpenTelemetryVersion>1.11.0</OpenTelemetryVersion>
    <XunitVersion>2.9.2</XunitVersion>
  </PropertyGroup>

  <!-- Akka.NET packages — all use same version -->
  <ItemGroup Label="Akka.NET">
    <PackageVersion Include="Akka" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Cluster" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Persistence" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Streams" Version="$(AkkaVersion)" />
  </ItemGroup>

  <!-- OpenTelemetry packages -->
  <ItemGroup Label="OpenTelemetry">
    <PackageVersion Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="$(OpenTelemetryVersion)" />
    <PackageVersion Include="OpenTelemetry.Extensions.Hosting" Version="$(OpenTelemetryVersion)" />
    <PackageVersion Include="OpenTelemetry.Instrumentation.AspNetCore" Version="$(OpenTelemetryVersion)" />
  </ItemGroup>

  <!-- Testing -->
  <ItemGroup Label="Testing">
    <PackageVersion Include="xunit" Version="$(XunitVersion)" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="$(XunitVersion)" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
  </ItemGroup>
</Project>
```

**Why version variables**: Update all Akka packages by changing one line. Labeled `<ItemGroup>` elements provide clear organization and prevent accidental version mismatches.

> **Values**: 継続は力（consistent versions compound reliability over time） / 成長の複利

### Step 4 — Configure Package Sources

Use when adding private NuGet feeds or ensuring reproducible restores across machines.

**List current sources:**

```bash
dotnet nuget list source
```

**Add a private feed:**

```bash
dotnet nuget add source https://pkgs.dev.azure.com/myorg/_packaging/myfeed/nuget/v3/index.json \
  --name MyFeed \
  --username az \
  --password $PAT \
  --store-password-in-clear-text
```

**Solution-specific NuGet.Config** — create at the solution root for reproducible restores:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <!-- Clear inherited machine-level sources -->
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="MyPrivateFeed" value="https://pkgs.dev.azure.com/myorg/_packaging/myfeed/nuget/v3/index.json" />
  </packageSources>
  <packageSourceCredentials>
    <MyPrivateFeed>
      <add key="Username" value="az" />
      <add key="ClearTextPassword" value="%NUGET_PAT%" />
    </MyPrivateFeed>
  </packageSourceCredentials>
</configuration>
```

**Why `<clear />`**: Removes inherited machine-level NuGet sources so restores produce identical results regardless of developer machine configuration.

> **Values**: ニュートラル（environment-independent, reproducible restores） / 基礎と型

### Step 5 — Audit and Update Dependencies

Use when checking for outdated, vulnerable, or deprecated packages before a release.

**Listing packages:**

```bash
# List all packages in solution
dotnet list package

# Show outdated packages
dotnet list package --outdated

# Include transitive dependencies
dotnet list package --include-transitive

# Show vulnerable packages
dotnet list package --vulnerable

# Show deprecated packages
dotnet list package --deprecated
```

**Updating packages with CPM:**

```bash
# Edit the version in Directory.Packages.props, then restore
dotnet restore

# Or use dotnet-outdated tool for bulk upgrades
dotnet tool install --global dotnet-outdated-tool
dotnet outdated --upgrade
```

**Troubleshooting restore failures:**

```bash
# Clear all local caches
dotnet nuget locals all --clear

# Restore with detailed logging
dotnet restore --verbosity detailed

# Force restore ignoring cache
dotnet restore --force
```

**Enable lock files** for reproducible builds:

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
</PropertyGroup>
```

Commit `packages.lock.json` files to source control.

**Why regular audits**: Outdated packages accumulate technical debt; vulnerable packages expose security risks. Automated audit catches issues before they reach production.

> **Values**: 温故知新（learn from ecosystem updates to stay secure） / 余白の設計

---

## Good Practices

### 1. Use CLI for Every Package Operation

**What**: Run `dotnet add package` and `dotnet remove package` instead of editing XML.

**Why**: The CLI validates package existence, resolves compatible versions, updates lock files, and handles CPM integration automatically.

**Values**: 基礎と型（CLI as the reliable foundation for all operations）

### 2. Label ItemGroups by Domain

**What**: Use `Label="Akka.NET"` or `Label="Testing"` on `<ItemGroup>` elements in `Directory.Packages.props`.

**Why**: Clear labels make large dependency files scannable and help reviewers understand package groupings at a glance.

**Values**: 余白の設計（visual structure creates space for comprehension）

### 3. Commit Lock Files for Reproducible Builds

**What**: Enable `<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>` and commit `packages.lock.json`.

**Why**: Lock files ensure every developer and CI environment restores exactly the same dependency graph.

**Values**: ニュートラル（identical results regardless of environment）

---

## Common Pitfalls

### 1. Editing .csproj XML Instead of Using CLI

**Problem**: Manually adding `<PackageReference>` elements without CLI validation causes typos, missing packages, and malformed XML.

**Solution**: Always use `dotnet add package <name>` — the CLI validates the package exists and resolves the correct version.

```bash
# ❌ WRONG — manual XML editing
# <PackageReference Include="Typo.Package" Version="1.0.0" />

# ✅ CORRECT — CLI validates the package
dotnet add package Newtonsoft.Json
```

### 2. Specifying Versions in .csproj with CPM Enabled

**Problem**: Adding `Version="x.y.z"` to `<PackageReference>` when CPM is active causes build errors or silently bypasses central management.

**Solution**: Remove the `Version` attribute from all `.csproj` `<PackageReference>` elements.

```xml
<!-- ❌ WRONG — conflicts with CPM -->
<PackageReference Include="Serilog" Version="4.0.0" />

<!-- ✅ CORRECT — version managed centrally -->
<PackageReference Include="Serilog" />
```

### 3. Ignoring Transitive Dependency Conflicts

**Problem**: Two packages pull in different versions of a shared transitive dependency, causing runtime failures.

**Solution**: Inspect the full dependency tree and pin the conflicting package explicitly.

```bash
# Identify the conflict
dotnet list package --include-transitive

# Fix by adding explicit version in Directory.Packages.props
```

---

## Anti-Patterns

### Mixing Version Management Strategies

**What**: Some packages use CPM versions from `Directory.Packages.props` while others have inline versions in `.csproj` files.

**Why It's Wrong**: Creates confusion about which file controls each package version. Developers cannot rely on a single source of truth, and version updates require searching across multiple file types.

**Better Approach**: Adopt CPM for the entire solution. If a single project requires a different version, use `VersionOverride` sparingly and document the reason.

### Using VersionOverride as a Default Practice

**What**: Routinely adding `VersionOverride="x.y.z"` to escape CPM constraints instead of updating the central version.

**Why It's Wrong**: Undermines the purpose of central management. Each override is a design decision that erodes architectural consistency and makes dependency audits unreliable.

**Better Approach**: Update the central version in `Directory.Packages.props`. Reserve `VersionOverride` for documented, temporary exceptions only.

---

## Quick Reference

| Task | Command |
|------|---------|
| Add package | `dotnet add package <name>` |
| Add specific version | `dotnet add package <name> --version <ver>` |
| Add prerelease | `dotnet add package <name> --prerelease` |
| Remove package | `dotnet remove package <name>` |
| List all packages | `dotnet list package` |
| Show outdated | `dotnet list package --outdated` |
| Show vulnerable | `dotnet list package --vulnerable` |
| Show deprecated | `dotnet list package --deprecated` |
| Show transitive | `dotnet list package --include-transitive` |
| Restore packages | `dotnet restore` |
| Clear cache | `dotnet nuget locals all --clear` |
| Force restore | `dotnet restore --force` |
| List sources | `dotnet nuget list source` |

### When NOT to Use CPM — Decision Table

| Scenario | Use CPM? | Reason |
|----------|----------|--------|
| New solution with ≥2 projects | ✅ Yes | Prevents version drift from the start |
| Single-project solution | ✅ Optional | Low overhead, prepares for growth |
| Legacy solution with many conflicts | ⚠️ Incremental | Migrate project-by-project to avoid big-bang risk |
| Version ranges required | ❌ No | CPM requires exact versions |
| .NET SDK < 6.0.300 | ❌ No | CPM not supported on older SDKs |
| Multi-repo independent builds | ❌ Per-repo | Each repository needs its own Directory.Packages.props |

---

## Resources

- [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management) — Official NuGet CPM documentation
- [dotnet CLI Reference](https://learn.microsoft.com/en-us/dotnet/core/tools/) — Complete dotnet command reference
- [NuGet.Config Reference](https://learn.microsoft.com/en-us/nuget/reference/nuget-config-file) — Package source configuration
- [dotnet-outdated Tool](https://github.com/dotnet-outdated/dotnet-outdated) — Bulk package update tool

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
