---
name: dotnet-project-structure
description: >
  Modern .NET project structure with .slnx, Directory.Build.props, central package management,
  SourceLink, version management, and SDK pinning. Use when setting up or modernizing a .NET solution.
metadata:
  author: RyoMurakami1983
  tags: [dotnet, msbuild, nuget, slnx, sourcelink, project-structure]
  invocable: false
  version: 1.0.0
---

# .NET Project Structure and Build Configuration

End-to-end workflow for setting up a modern .NET solution: .slnx migration, centralized build properties, Central Package Management (CPM), SourceLink debugging, RELEASE_NOTES-driven versioning, and SDK pinning with global.json.

## When to Use This Skill

Use this skill when:

- Setting up a new .NET solution from scratch with modern project structure conventions
- Migrating an existing .sln solution file to the modern XML-based .slnx format
- Configuring centralized build properties across multiple projects via Directory.Build.props
- Implementing central NuGet package version management with Directory.Packages.props
- Adding SourceLink support to enable step-through debugging of published NuGet packages
- Automating version management by parsing RELEASE_NOTES.md during the build process
- Pinning the .NET SDK version across all developer machines and CI/CD environments

---

## Related Skills

- **`dotnet-local-tools`** — Managing local .NET tools with dotnet-tools.json
- **`microsoft-extensions-configuration`** — Configuration validation patterns
- **`git-commit-practices`** — Commit each step as an atomic change
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor

---

## Core Principles

1. **Single Source of Truth** — Each configuration concern lives in exactly one file; no duplication across projects (基礎と型)
2. **Reproducible Builds** — SDK version and package versions are pinned so every environment produces identical output (基礎と型)
3. **Human-Readable Configuration** — .slnx XML and Directory.Build.props replace cryptic GUIDs and scattered settings (温故知新)
4. **Progressive Modernization** — Migrate one concern at a time: solution → build props → packages → SourceLink → versioning → SDK (継続は力)
5. **Debuggability by Default** — SourceLink and symbol packages ship with every NuGet package for step-through debugging (成長の複利)

---

## Workflow: Set Up Modern .NET Project

### Step 1 — Migrate to .slnx Format

Use when converting an existing .sln solution to the modern XML-based .slnx format introduced in .NET 9.

**Version requirements:**

| Tool | Minimum Version |
|------|-----------------|
| .NET SDK | 9.0.200 |
| Visual Studio | 17.13 |

**Migrate an existing solution:**

```bash
# Migrate a specific solution file
dotnet sln MySolution.sln migrate

# If only one .sln exists in the directory
dotnet sln migrate
```

**Create a new .slnx solution:**

```bash
# .NET 10+: Creates .slnx by default
dotnet new sln --name MySolution

# .NET 9: Specify the format explicitly
dotnet new sln --name MySolution --format slnx

# Add projects
dotnet sln add src/MyApp/MyApp.csproj
```

**Example .slnx file:**

```xml
<Solution>
  <Folder Name="/build/">
    <File Path="Directory.Build.props" />
    <File Path="Directory.Packages.props" />
    <File Path="global.json" />
  </Folder>
  <Folder Name="/src/">
    <Project Path="src/MyApp/MyApp.csproj" />
  </Folder>
  <Folder Name="/tests/">
    <Project Path="tests/MyApp.Tests/MyApp.Tests.csproj" />
  </Folder>
</Solution>
```

**Why .slnx**: No random GUIDs, clean XML diffs in pull requests, editable in any text editor. Starting with .NET 10, `dotnet new sln` creates `.slnx` by default.

⚠️ **Important**: Delete the old `.sln` after migration. Keeping both causes automatic solution detection issues.

> **Values**: 温故知新（modern format replaces legacy conventions） / 基礎と型

### Step 2 — Configure Directory.Build.props

Use when centralizing build properties that apply to all projects in the solution tree.

Place `Directory.Build.props` at the solution root. All projects inherit these settings automatically.

```xml
<Project>
  <!-- Metadata -->
  <PropertyGroup>
    <Authors>Your Team</Authors>
    <Company>Your Company</Company>
    <!-- Dynamic copyright year — updates automatically at build time -->
    <Copyright>Copyright © 2020-$([System.DateTime]::Now.Year) Your Company</Copyright>
    <RepositoryUrl>https://github.com/yourorg/yourrepo</RepositoryUrl>
    <PackageLicenseExpression>Apache-2.0</PackageLicenseExpression>
  </PropertyGroup>

  <!-- C# Language Settings -->
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>

  <!-- Version Management -->
  <PropertyGroup>
    <VersionPrefix>1.0.0</VersionPrefix>
    <PackageReleaseNotes>See RELEASE_NOTES.md</PackageReleaseNotes>
  </PropertyGroup>

  <!-- Reusable Target Framework Properties -->
  <PropertyGroup>
    <NetLibVersion>net8.0</NetLibVersion>
    <NetTestVersion>net9.0</NetTestVersion>
  </PropertyGroup>
</Project>
```

**Why reusable framework properties**: Define `<NetLibVersion>` once, reference `$(NetLibVersion)` in every `.csproj`. Upgrading target frameworks requires changing a single line.

**Why dynamic copyright**: `$([System.DateTime]::Now.Year)` inserts the current year at build time — no manual updates needed.

> **Values**: 基礎と型（centralize once, reference everywhere） / 成長の複利

### Step 3 — Set Up Central Package Management

Use when consolidating all NuGet package versions into a single Directory.Packages.props file.

Create `Directory.Packages.props` at the solution root:

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <PropertyGroup>
    <AkkaVersion>1.5.35</AkkaVersion>
  </PropertyGroup>

  <ItemGroup Label="App Dependencies">
    <PackageVersion Include="Akka" Version="$(AkkaVersion)" />
    <PackageVersion Include="Akka.Cluster" Version="$(AkkaVersion)" />
    <PackageVersion Include="Microsoft.Extensions.Hosting" Version="9.0.0" />
  </ItemGroup>

  <ItemGroup Label="Test Dependencies">
    <PackageVersion Include="xunit" Version="2.9.3" />
    <PackageVersion Include="FluentAssertions" Version="7.0.0" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
  </ItemGroup>
</Project>
```

**Consuming packages** — no version attribute needed in `.csproj`:

```xml
<!-- In MyApp.csproj -->
<ItemGroup>
  <PackageReference Include="Akka" />
  <PackageReference Include="Microsoft.Extensions.Hosting" />
</ItemGroup>
```

**Why CPM**: Eliminates version drift across projects, groups related packages with version variables, and makes dependency updates a single-line change.

> **Values**: 基礎と型（single source of truth for versions） / ニュートラル

### Step 4 — Configure SourceLink

Use when enabling step-through debugging for published NuGet packages.

Add SourceLink configuration to `Directory.Build.props`:

```xml
<!-- SourceLink Configuration -->
<PropertyGroup>
  <PublishRepositoryUrl>true</PublishRepositoryUrl>
  <EmbedUntrackedSources>true</EmbedUntrackedSources>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>
</PropertyGroup>

<ItemGroup>
  <!-- Choose the provider matching your source control -->
  <PackageReference Include="Microsoft.SourceLink.GitHub" PrivateAssets="All" />
  <!-- Or: Microsoft.SourceLink.AzureRepos.Git -->
  <!-- Or: Microsoft.SourceLink.GitLab -->
</ItemGroup>

<!-- NuGet Package Assets -->
<ItemGroup>
  <None Include="$(MSBuildThisFileDirectory)README.md" Pack="true" PackagePath="\" />
</ItemGroup>

<PropertyGroup>
  <PackageReadmeFile>README.md</PackageReadmeFile>
</PropertyGroup>
```

**Why SourceLink**: Consumers can step into your library source code during debugging without downloading the repository. Symbol packages (`.snupkg`) are automatically uploaded to NuGet.org.

> **Values**: 成長の複利（debugging experience compounds across consumers） / 基礎と型

### Step 5 — Set Up Version Management

Use when automating version bumps by parsing a RELEASE_NOTES.md file during the build process.

**RELEASE_NOTES.md format:**

```markdown
#### 1.2.0 January 15th 2025 ####

- Added new feature X
- Fixed bug in Y

#### 1.1.0 December 10th 2024 ####

- Initial release
```

**Build script** parses the latest version and updates `Directory.Build.props`:

```powershell
# build.ps1 — parse release notes and update VersionPrefix
$content = Get-Content -Path "RELEASE_NOTES.md" -Raw
$sections = $content -split "####"
$version = ($sections[1].Trim() -split " ", 2)[0]

$xml = New-Object XML
$xml.Load("Directory.Build.props")
$xml.SelectSingleNode("//VersionPrefix").InnerText = $version
$xml.Save("Directory.Build.props")
Write-Output "Updated to version $version"
```

**CI/CD integration** (GitHub Actions):

```yaml
- name: Update version
  shell: pwsh
  run: ./build.ps1

- name: Pack
  run: dotnet pack -c Release /p:PackageVersion=${{ github.ref_name }}
```

**Why RELEASE_NOTES.md**: Human-readable changelog that doubles as the version source. Developers update one markdown file and the build script handles the rest.

See `references/advanced-examples.md` for the full modular PowerShell scripts (`getReleaseNotes.ps1`, `bumpVersion.ps1`).

> **Values**: 継続は力（release notes accumulate project history） / 余白の設計

### Step 6 — Pin SDK with global.json

Use when ensuring all developers and CI environments use the same .NET SDK version.

```json
{
  "sdk": {
    "version": "9.0.200",
    "rollForward": "latestFeature"
  }
}
```

**Roll forward policies:**

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `disable` | Exact version required | Strict reproducibility |
| `patch` | Same major.minor, latest patch | Security fixes only |
| `latestFeature` | Same major, latest feature band | ✅ Recommended default |
| `major` | Latest SDK available | Not recommended |

**Why `latestFeature`**: Allows automatic patch updates for security fixes while preventing breaking changes from major SDK upgrades.

> **Values**: 基礎と型（SDK pinning prevents environment drift） / ニュートラル

---

## Good Practices

### 1. Use Version Variables for Related Packages

**What**: Group related NuGet packages under a single version variable in `Directory.Packages.props`.

**Why**: Prevents version mismatches between packages that must stay in sync (e.g., all Akka packages at the same version).

**Values**: 基礎と型（version consistency as a structural constraint）

### 2. Clear Package Sources in NuGet.Config

**What**: Use `<clear />` before defining package sources to remove inherited defaults.

**Why**: Ensures reproducible restores regardless of machine-level NuGet configuration.

**Values**: ニュートラル（environment-independent builds）

### 3. Define Reusable Target Framework Properties

**What**: Create properties like `<NetLibVersion>net8.0</NetLibVersion>` and reference `$(NetLibVersion)` in `.csproj` files.

**Why**: Upgrading the target framework for all projects requires changing a single line in `Directory.Build.props`.

**Values**: 成長の複利（one change propagates to all projects）

---

## Common Pitfalls

### 1. Keeping Both .sln and .slnx Files

**Problem**: Both files exist in the repository after migration, causing tool confusion.

**Solution**: Delete the old `.sln` file immediately after running `dotnet sln migrate`.

```bash
# ❌ WRONG — Both files coexist
# MySolution.sln + MySolution.slnx in same directory

# ✅ CORRECT — Only .slnx remains
dotnet sln MySolution.sln migrate
Remove-Item MySolution.sln
```

### 2. Specifying Version in .csproj with CPM Enabled

**Problem**: Adding `Version="x.y.z"` to `<PackageReference>` when Central Package Management is active causes build errors.

**Solution**: Remove the `Version` attribute from all `.csproj` `<PackageReference>` elements.

```xml
<!-- ❌ WRONG — Version conflicts with CPM -->
<PackageReference Include="Akka" Version="1.5.35" />

<!-- ✅ CORRECT — Version managed centrally -->
<PackageReference Include="Akka" />
```

### 3. Missing global.json in Repository Root

**Problem**: Different developers use different SDK versions, causing inconsistent build behavior.

**Solution**: Always commit `global.json` at the repository root with a pinned SDK version and `rollForward` policy.

---

## Anti-Patterns

### Scattering Build Properties Across .csproj Files

**What**: Duplicating `<LangVersion>`, `<Nullable>`, and metadata in every `.csproj` file.

**Why It's Wrong**: Changes require editing every project file; properties drift apart over time; increases merge conflict surface.

**Better Approach**: Define shared properties once in `Directory.Build.props` at the solution root.

### Hardcoding Version Numbers in Directory.Build.props

**What**: Manually editing `<VersionPrefix>` before every release instead of automating from RELEASE_NOTES.md.

**Why It's Wrong**: Error-prone, easy to forget, version and changelog can desynchronize.

**Better Approach**: Use a build script that parses `RELEASE_NOTES.md` and updates `Directory.Build.props` automatically.

---

## Quick Reference

### Project Structure Overview

```
MySolution/
├── Directory.Build.props           # Centralized build config
├── Directory.Packages.props        # Central package versions
├── MySolution.slnx                 # Modern solution file
├── global.json                     # SDK version pinning
├── NuGet.Config                    # Package source config
├── build.ps1                       # Build orchestration
├── RELEASE_NOTES.md                # Version history
├── src/
│   └── MyApp/MyApp.csproj
└── tests/
    └── MyApp.Tests/MyApp.Tests.csproj
```

### File Decision Table

| File | Purpose | When to Create |
|------|---------|----------------|
| `MySolution.slnx` | Modern XML solution file | Always — replaces .sln |
| `Directory.Build.props` | Shared build properties | Always — centralize metadata and settings |
| `Directory.Packages.props` | Central NuGet versions | When ≥2 projects share packages |
| `global.json` | SDK version pinning | Always — ensures reproducible builds |
| `NuGet.Config` | Package source config | When using `<clear />` or private feeds |
| `RELEASE_NOTES.md` | Version changelog | When publishing NuGet packages |

---

## Resources

- [.slnx Format Documentation](https://learn.microsoft.com/en-us/visualstudio/ide/solution-file) — Modern solution format reference
- [Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management) — NuGet CPM documentation
- [SourceLink](https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/sourcelink) — Source debugging configuration
- [global.json Overview](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json) — SDK version pinning reference
- See `references/advanced-examples.md` for full PowerShell version management scripts and NuGet.Config templates

<!--
Japanese version available at references/SKILL.ja.md
日本語版は references/SKILL.ja.md を参照してください
-->
