<#
.SYNOPSIS
    Deploy Python skills from skills_repository to a target project.

.DESCRIPTION
    Copies selected Python skills to a project's .github/skills/ directory.
    Skills can be selected by category or individually by name.

.PARAMETER SourceRoot
    Path to the Python skills source directory (for example: C:\tools\skills_repository\python).

.PARAMETER Target
    Path to the target project root. Skills are copied to <Target>\.github\skills\.

.PARAMETER Category
    Deploy all skills in a category. Valid: dev-env, all.

.PARAMETER Skills
    Comma-separated list of individual skill names to deploy.

.PARAMETER List
    Show available categories and skills, then exit.

.PARAMETER Force
    Overwrite existing skills in the target directory.

.PARAMETER WhatIf
    Show what would be copied without actually copying.

.EXAMPLE
    .\Deploy-PythonSkills.ps1 -SourceRoot C:\tools\skills_repository\python -List

.EXAMPLE
    .\Deploy-PythonSkills.ps1 -SourceRoot C:\tools\skills_repository\python -Target C:\my-project -Category dev-env
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$SourceRoot,

    [Parameter()]
    [string]$Target,

    [Parameter()]
    [ValidateSet('dev-env', 'all')]
    [string]$Category,

    [Parameter()]
    [string[]]$Skills,

    [switch]$List,

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$CategoryMap = [ordered]@{
    'dev-env' = @(
        'python-setup-dev-environment'
    )
}

function Get-AvailableSkills {
    param([string]$Root)

    return Get-ChildItem -Path $Root -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
        Select-Object -ExpandProperty Name |
        Sort-Object
}

function Resolve-CategorySkills {
    param(
        [string]$CategoryName,
        [string[]]$AvailableSkills
    )

    if ($CategoryName -eq 'all') {
        return @($AvailableSkills)
    }

    return @($CategoryMap[$CategoryName])
}

if (-not (Test-Path $SourceRoot -PathType Container)) {
    Write-Error "SourceRoot not found: $SourceRoot"
    exit 1
}

$AvailableSkills = @(Get-AvailableSkills -Root $SourceRoot)

if ($List) {
    Write-Host "`n=== Available Python Skill Categories ===" -ForegroundColor Cyan
    Write-Host ""

    $listCategories = @($CategoryMap.Keys) + 'all'
    foreach ($cat in $listCategories) {
        $skillsInCategory = @(Resolve-CategorySkills -CategoryName $cat -AvailableSkills $AvailableSkills)
        $label = switch ($cat) {
            'dev-env' { 'Development Environment Foundation' }
            'all'     { 'All Available Python Skills' }
            default   { $cat }
        }

        Write-Host "  $cat ($($skillsInCategory.Count) skills) - $label" -ForegroundColor Yellow
        foreach ($skillName in $skillsInCategory) {
            $marker = if ($AvailableSkills -contains $skillName) { '  [ok]' } else { '  [missing]' }
            $color = if ($AvailableSkills -contains $skillName) { 'Green' } else { 'Red' }
            Write-Host "    $marker $skillName" -ForegroundColor $color
        }
        Write-Host ""
    }

    Write-Host "=== Available Individual Python Skills ===" -ForegroundColor Cyan
    foreach ($skillName in $AvailableSkills) {
        Write-Host "  - $skillName" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "Total available: $($AvailableSkills.Count) skills" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

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
    $targetSkills = @(Resolve-CategorySkills -CategoryName $Category -AvailableSkills $AvailableSkills)
}

if ($Skills) {
    $targetSkills = @(($targetSkills + $Skills) | Sort-Object -Unique)
}

$invalidSkills = @($targetSkills | Where-Object { $_ -notin $AvailableSkills })
if ($invalidSkills.Count -gt 0) {
    Write-Error "Skills not found in source: $($invalidSkills -join ', ')"
    exit 1
}

$destBase = Join-Path (Join-Path $Target '.github') 'skills'

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

        $parentDir = Split-Path $destPath -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }

        Copy-Item -Path $srcPath -Destination $destPath -Recurse
    }
}

Write-Host "`n=== Deploy Summary ===" -ForegroundColor Cyan
Write-Host "  Source:  $SourceRoot"
Write-Host "  Target:  $destBase"
if ($Category) { Write-Host "  Category: $Category" }
Write-Host ""

if ($copied.Count -gt 0) {
    Write-Host "  Copied ($($copied.Count)):" -ForegroundColor Green
    foreach ($skillName in $copied) { Write-Host "    + $skillName" -ForegroundColor Green }
}

if ($overwritten.Count -gt 0) {
    Write-Host "  Overwritten ($($overwritten.Count)):" -ForegroundColor Yellow
    foreach ($skillName in $overwritten) { Write-Host "    ~ $skillName" -ForegroundColor Yellow }
}

if ($skipped.Count -gt 0) {
    Write-Host "  Skipped ($($skipped.Count)):" -ForegroundColor DarkYellow
    foreach ($skillName in $skipped) { Write-Host "    - $skillName (already exists)" -ForegroundColor DarkYellow }
}

$totalActions = $copied.Count + $overwritten.Count
Write-Host "`n  Total deployed: $totalActions skill(s)" -ForegroundColor Cyan

if ($WhatIfPreference) {
    Write-Host "  (Dry run - no files were copied)" -ForegroundColor Magenta
}

Write-Host ""
