<#
.SYNOPSIS
    Deploy dotnet skills from skills_repository to a target project.

.DESCRIPTION
    Copies selected dotnet skills to a project's .github/skills/ directory.
    Skills can be selected by category or individually by name.

.PARAMETER SourceRoot
    Path to the dotnet skills source directory (e.g., C:\tools\skills_repository\dotnet).

.PARAMETER Target
    Path to the target project root. Skills are copied to <Target>\.github\skills\.

.PARAMETER Category
    Deploy all skills in a category. Valid: foundation, data, testing, wpf, infra, wpf-app, all.

.PARAMETER Skills
    Comma-separated list of individual skill names to deploy.

.PARAMETER List
    Show available categories and skills, then exit.

.PARAMETER Force
    Overwrite existing skills in the target directory.

.PARAMETER WhatIf
    Show what would be copied without actually copying.

.EXAMPLE
    .\Deploy-DotnetSkills.ps1 -SourceRoot C:\tools\skills_repository\dotnet -List

.EXAMPLE
    .\Deploy-DotnetSkills.ps1 -SourceRoot C:\tools\skills_repository\dotnet -Target C:\my-project -Category wpf-app

.EXAMPLE
    .\Deploy-DotnetSkills.ps1 -SourceRoot C:\tools\skills_repository\dotnet -Target C:\my-project -Skills dotnet-wpf-secure-config,dotnet-oracle-wpf-integration
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$SourceRoot,

    [Parameter()]
    [string]$Target,

    [Parameter()]
    [ValidateSet('foundation', 'data', 'testing', 'wpf', 'infra', 'wpf-app', 'all')]
    [string]$Category,

    [Parameter()]
    [string[]]$Skills,

    [switch]$List,

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Category Definitions (aligned with dotnet-shihan.agent.md) ---

$CategoryMap = [ordered]@{
    'foundation' = @(
        'dotnet-modern-csharp-coding-standards'
        'dotnet-type-design-performance'
        'dotnet-project-structure'
        'dotnet-slopwatch'
        'dotnet-csharp-api-design'
    )
    'data' = @(
        'dotnet-efcore-patterns'
        'dotnet-database-performance'
        'dotnet-serialization'
    )
    'testing' = @(
        'dotnet-csharp-concurrency-patterns'
        'dotnet-testcontainers'
        'dotnet-snapshot-testing'
        'dotnet-verify-email-snapshots'
        'dotnet-crap-analysis'
        'dotnet-playwright-blazor'
        'dotnet-playwright-ci-caching'
    )
    'wpf' = @(
        'dotnet-wpf-mvvm-patterns'
        'dotnet-wpf-secure-config'
        'dotnet-oracle-wpf-integration'
        'dotnet-wpf-dify-api-integration'
        'dotnet-wpf-comparison-view'
        'dotnet-wpf-employee-input'
        'dotnet-wpf-pdf-preview'
        'dotnet-wpf-ocr-parameter-input'
        'dotnet-ocr-matching-workflow'
        'dotnet-generic-matching'
        'dotnet-access-to-oracle-migration'
    )
    'infra' = @(
        'dotnet-extensions-dependency-injection'
        'dotnet-extensions-configuration'
        'dotnet-local-tools'
        'dotnet-package-management'
        'dotnet-marketplace-publishing'
        'dotnet-mjml-email-templates'
    )
}

# Composite category: wpf-app = foundation subset + wpf + infra subset
$CategoryMap['wpf-app'] = @(
    'dotnet-modern-csharp-coding-standards'
    'dotnet-project-structure'
) + $CategoryMap['wpf'] + @(
    'dotnet-extensions-dependency-injection'
    'dotnet-extensions-configuration'
)

# --- Validation ---

if (-not (Test-Path $SourceRoot -PathType Container)) {
    Write-Error "SourceRoot not found: $SourceRoot"
    exit 1
}

# Discover all available skills from the source directory
$AvailableSkills = Get-ChildItem -Path $SourceRoot -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
    Select-Object -ExpandProperty Name |
    Sort-Object

# --- List Mode ---

if ($List) {
    Write-Host "`n=== Available Dotnet Skill Categories ===" -ForegroundColor Cyan
    Write-Host ""

    foreach ($cat in $CategoryMap.Keys) {
        $skills = $CategoryMap[$cat]
        $label = switch ($cat) {
            'foundation' { '技術基盤 (Technical Foundation)' }
            'data'       { 'データ・永続化 (Data & Persistence)' }
            'testing'    { '並行・テスト・CI (Concurrency, Testing & CI)' }
            'wpf'        { 'WPF・デスクトップ (WPF & Desktop)' }
            'infra'      { 'インフラ・パッケージ (Infrastructure & Packages)' }
            'wpf-app'    { '【複合】WPFアプリ開発一式 (WPF App Development Bundle)' }
            default      { $cat }
        }
        Write-Host "  $cat ($($skills.Count) skills) — $label" -ForegroundColor Yellow
        foreach ($s in $skills) {
            $marker = if ($AvailableSkills -contains $s) { '  ✓' } else { '  ✗' }
            $color = if ($AvailableSkills -contains $s) { 'Green' } else { 'Red' }
            Write-Host "    $marker $s" -ForegroundColor $color
        }
        Write-Host ""
    }

    # Show uncategorized skills
    $allCategorized = @($CategoryMap.Values | ForEach-Object { $_ } | Sort-Object -Unique)
    $uncategorized = @($AvailableSkills | Where-Object { $_ -notin $allCategorized })
    if ($uncategorized.Count -gt 0) {
        Write-Host "  uncategorized ($($uncategorized.Count) skills)" -ForegroundColor DarkYellow
        foreach ($s in $uncategorized) {
            Write-Host "    ✓ $s" -ForegroundColor DarkGreen
        }
        Write-Host ""
    }

    Write-Host "Total available: $($AvailableSkills.Count) skills" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

# --- Resolve Target Skills ---

if (-not $Target) {
    Write-Error "Target is required when not using -List. Specify -Target <project-path>."
    exit 1
}

if (-not $Category -and -not $Skills) {
    Write-Error "Specify -Category or -Skills to select which skills to deploy."
    exit 1
}

$targetSkills = @()

if ($Category) {
    if ($Category -eq 'all') {
        $targetSkills = @($AvailableSkills)
    }
    else {
        $targetSkills = @($CategoryMap[$Category])
    }
}

if ($Skills) {
    $targetSkills = @(($targetSkills + $Skills) | Sort-Object -Unique)
}

# Validate all requested skills exist
$invalidSkills = @($targetSkills | Where-Object { $_ -notin $AvailableSkills })
if ($invalidSkills.Count -gt 0) {
    Write-Error "Skills not found in source: $($invalidSkills -join ', ')"
    exit 1
}

# --- Deploy ---

$destBase = Join-Path $Target '.github' 'skills'

$copied = @()
$skipped = @()
$overwritten = @()

foreach ($skillName in $targetSkills) {
    $srcPath = Join-Path $SourceRoot $skillName
    $destPath = Join-Path $destBase $skillName
    $exists = Test-Path $destPath

    if ($exists -and -not $Force) {
        $skipped += $skillName
        if ($WhatIfPreference) {
            Write-Host "  SKIP  $skillName (already exists, use -Force to overwrite)" -ForegroundColor DarkYellow
        }
        continue
    }

    if ($WhatIfPreference) {
        $action = if ($exists) { 'OVERWRITE' } else { 'COPY' }
        Write-Host "  $action  $skillName -> $destPath" -ForegroundColor Cyan
        if ($exists) { $overwritten += $skillName } else { $copied += $skillName }
        continue
    }

    if ($PSCmdlet.ShouldProcess($destPath, "Deploy skill '$skillName'")) {
        if ($exists) {
            Remove-Item -Path $destPath -Recurse -Force
            $overwritten += $skillName
        }
        else {
            $copied += $skillName
        }

        # Ensure parent directory exists
        $parentDir = Split-Path $destPath -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }

        Copy-Item -Path $srcPath -Destination $destPath -Recurse
    }
}

# --- Summary ---

Write-Host "`n=== Deploy Summary ===" -ForegroundColor Cyan
Write-Host "  Source:  $SourceRoot"
Write-Host "  Target:  $destBase"
if ($Category) { Write-Host "  Category: $Category" }
Write-Host ""

if ($copied.Count -gt 0) {
    Write-Host "  Copied ($($copied.Count)):" -ForegroundColor Green
    foreach ($s in $copied) { Write-Host "    + $s" -ForegroundColor Green }
}

if ($overwritten.Count -gt 0) {
    Write-Host "  Overwritten ($($overwritten.Count)):" -ForegroundColor Yellow
    foreach ($s in $overwritten) { Write-Host "    ~ $s" -ForegroundColor Yellow }
}

if ($skipped.Count -gt 0) {
    Write-Host "  Skipped ($($skipped.Count)):" -ForegroundColor DarkYellow
    foreach ($s in $skipped) { Write-Host "    - $s (already exists)" -ForegroundColor DarkYellow }
}

$totalActions = $copied.Count + $overwritten.Count
Write-Host "`n  Total deployed: $totalActions skill(s)" -ForegroundColor Cyan

if ($WhatIfPreference) {
    Write-Host "  (Dry run — no files were copied)" -ForegroundColor Magenta
}

Write-Host ""
