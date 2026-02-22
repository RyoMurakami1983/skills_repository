# Advanced Examples: .NET Project Structure

Detailed examples and scripts referenced from the main SKILL.md.

## Version Management Scripts

### getReleaseNotes.ps1

Parses `RELEASE_NOTES.md` and extracts the latest version, date, and release notes content.

```powershell
function Get-ReleaseNotes {
    param (
        [Parameter(Mandatory=$true)]
        [string]$MarkdownFile
    )

    $content = Get-Content -Path $MarkdownFile -Raw
    $sections = $content -split "####"

    $result = [PSCustomObject]@{
        Version      = $null
        Date         = $null
        ReleaseNotes = $null
    }

    if ($sections.Count -ge 3) {
        $header = $sections[1].Trim()
        $releaseNotes = $sections[2].Trim()

        $headerParts = $header -split " ", 2
        if ($headerParts.Count -eq 2) {
            $result.Version = $headerParts[0]
            $result.Date = $headerParts[1]
        }

        $result.ReleaseNotes = $releaseNotes
    }

    return $result
}
```

### bumpVersion.ps1

Updates `VersionPrefix` and `PackageReleaseNotes` in an MSBuild XML file.

```powershell
function UpdateVersionAndReleaseNotes {
    param (
        [Parameter(Mandatory=$true)]
        [PSCustomObject]$ReleaseNotesResult,
        [Parameter(Mandatory=$true)]
        [string]$XmlFilePath
    )

    $xmlContent = New-Object XML
    $xmlContent.Load($XmlFilePath)

    # Update VersionPrefix
    $versionElement = $xmlContent.SelectSingleNode("//VersionPrefix")
    $versionElement.InnerText = $ReleaseNotesResult.Version

    # Update PackageReleaseNotes
    $notesElement = $xmlContent.SelectSingleNode("//PackageReleaseNotes")
    $notesElement.InnerText = $ReleaseNotesResult.ReleaseNotes

    $xmlContent.Save($XmlFilePath)
}
```

### build.ps1 (Full Version)

Orchestrates version update and build using the helper scripts above.

```powershell
# Load helper scripts
. "$PSScriptRoot\scripts\getReleaseNotes.ps1"
. "$PSScriptRoot\scripts\bumpVersion.ps1"

# Parse release notes and update Directory.Build.props
$releaseNotes = Get-ReleaseNotes -MarkdownFile (Join-Path -Path $PSScriptRoot -ChildPath "RELEASE_NOTES.md")
UpdateVersionAndReleaseNotes -ReleaseNotesResult $releaseNotes -XmlFilePath (Join-Path -Path $PSScriptRoot -ChildPath "Directory.Build.props")

Write-Output "Updated to version $($releaseNotes.Version)"
```

---

## NuGet.Config Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <solution>
    <add key="disableSourceControlIntegration" value="true" />
  </solution>

  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <!-- Add private feeds if needed -->
    <!-- <add key="MyCompany" value="https://pkgs.dev.azure.com/myorg/_packaging/myfeed/nuget/v3/index.json" /> -->
  </packageSources>
</configuration>
```

**Key Settings:**

- `<clear />` — Remove inherited/default sources for reproducible builds
- `disableSourceControlIntegration` — Prevents TFS/Git integration issues

---

## CI/CD Pipeline Example

Full GitHub Actions workflow for version management and NuGet publishing:

```yaml
name: Release

on:
  push:
    tags: ['*']

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          global-json-file: global.json

      - name: Update version from release notes
        shell: pwsh
        run: ./build.ps1

      - name: Build
        run: dotnet build -c Release

      - name: Test
        run: dotnet test -c Release --no-build

      - name: Pack with tag version
        run: dotnet pack -c Release /p:PackageVersion=${{ github.ref_name }}

      - name: Push to NuGet
        run: dotnet nuget push **/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
```

---

## Directory.Build.props with SourceLink (Complete)

Full `Directory.Build.props` combining all configuration from Steps 2 and 4:

```xml
<Project>
  <!-- Metadata -->
  <PropertyGroup>
    <Authors>Your Team</Authors>
    <Company>Your Company</Company>
    <Copyright>Copyright © 2020-$([System.DateTime]::Now.Year) Your Company</Copyright>
    <Product>Your Product</Product>
    <PackageProjectUrl>https://github.com/yourorg/yourrepo</PackageProjectUrl>
    <RepositoryUrl>https://github.com/yourorg/yourrepo</RepositoryUrl>
    <PackageLicenseExpression>Apache-2.0</PackageLicenseExpression>
    <PackageTags>your;tags;here</PackageTags>
  </PropertyGroup>

  <!-- C# Language Settings -->
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <NoWarn>$(NoWarn);CS1591</NoWarn>
  </PropertyGroup>

  <!-- Version Management -->
  <PropertyGroup>
    <VersionPrefix>1.0.0</VersionPrefix>
    <PackageReleaseNotes>See RELEASE_NOTES.md</PackageReleaseNotes>
  </PropertyGroup>

  <!-- Target Framework Definitions -->
  <PropertyGroup>
    <NetStandardLibVersion>netstandard2.0</NetStandardLibVersion>
    <NetLibVersion>net8.0</NetLibVersion>
    <NetTestVersion>net9.0</NetTestVersion>
  </PropertyGroup>

  <!-- SourceLink Configuration -->
  <PropertyGroup>
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.SourceLink.GitHub" PrivateAssets="All" />
  </ItemGroup>

  <!-- NuGet Package Assets -->
  <ItemGroup>
    <None Include="$(MSBuildThisFileDirectory)logo.png" Pack="true" PackagePath="\" />
    <None Include="$(MSBuildThisFileDirectory)README.md" Pack="true" PackagePath="\" />
  </ItemGroup>

  <PropertyGroup>
    <PackageIcon>logo.png</PackageIcon>
    <PackageReadmeFile>README.md</PackageReadmeFile>
  </PropertyGroup>

  <!-- Global Using Statements -->
  <ItemGroup>
    <Using Include="System.Collections.Immutable" />
  </ItemGroup>
</Project>
```

---

## .slnx vs .sln Comparison

| Aspect | .sln (Legacy) | .slnx (Modern) |
|--------|---------------|----------------|
| Format | Custom text format | Standard XML |
| Readability | GUIDs, cryptic syntax | Clean, human-readable |
| Version control | Hard to diff/merge | Easy to diff/merge |
| Editing | IDE required | Any text editor |
| Default since | Always | .NET 10+ |

## Roll Forward Policy Reference

| Policy | Behavior |
|--------|----------|
| `disable` | Exact version required |
| `patch` | Same major.minor, latest patch |
| `feature` | Same major, latest minor.patch |
| `latestFeature` | Same major, latest feature band |
| `minor` | Same major, latest minor |
| `latestMinor` | Same major, latest minor |
| `major` | Latest SDK (not recommended) |
