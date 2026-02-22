<#
.SYNOPSIS
    Batch validation for all skills in the repository.

.DESCRIPTION
    Enumerates all SKILL.md files under skills/ and runs validate_skill.py
    on each. Produces a summary with pass/fail counts and exit codes for CI.

.PARAMETER SkillsDir
    Root directory containing skill subdirectories (default: skills/)

.EXAMPLE
    .\validate_all_skills.ps1
    .\validate_all_skills.ps1 -SkillsDir C:\tools\skills_repository\skills

.NOTES
    Exit codes: 0 = all pass, 1 = failures exist, 2 = borderline only
    Related: Issue #12
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SkillsDir = ''
)

$ErrorActionPreference = 'Stop'

# Resolve paths
$scriptDir = $PSScriptRoot
$validatorScript = Join-Path $scriptDir "validate_skill.py"

if (-not $SkillsDir) {
    # Default: skills/ at repo root (2 levels up from scripts/)
    $SkillsDir = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
}

if (-not (Test-Path $validatorScript)) {
    Write-Host "❌ validate_skill.py not found at: $validatorScript" -ForegroundColor Red
    exit 1
}

# Find all SKILL.md files (EN only, skip references/)
$skillFiles = Get-ChildItem -Path $SkillsDir -Filter "SKILL.md" -Recurse |
    Where-Object { $_.DirectoryName -notmatch '\\references(\\|$)' } |
    Sort-Object DirectoryName

if ($skillFiles.Count -eq 0) {
    Write-Host "❌ No SKILL.md files found under: $SkillsDir" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔍 Batch Skill Validation" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Skills directory: $SkillsDir"
Write-Host "Skills found: $($skillFiles.Count)"
Write-Host ""

# Track results
$results = @()
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($file in $skillFiles) {
    $skillName = Split-Path (Split-Path $file.FullName -Parent) -Leaf
    Write-Host "  ▶ $skillName ... " -NoNewline

    try {
        $output = uv run python $validatorScript $file.FullName 2>&1 | Out-String

        # Parse score from output (format: "Overall: 60/60 (100.0%) ... PASS")
        $score = $null
        $verdict = 'UNKNOWN'
        if ($output -match 'Overall:.*\(([\d.]+)%\)') {
            $score = [double]$Matches[1]
        }
        if ($output -match 'Overall:.*\b(PASS|FAIL|BORDERLINE)\b') {
            $verdict = $Matches[1]
        }

        $results += [PSCustomObject]@{
            Name    = $skillName
            Score   = $score
            Verdict = $verdict
            Output  = $output
        }

        switch ($verdict) {
            'PASS'       { Write-Host "$verdict ($score%)" -ForegroundColor Green }
            'BORDERLINE' { Write-Host "$verdict ($score%)" -ForegroundColor Yellow }
            'FAIL'       { Write-Host "$verdict ($score%)" -ForegroundColor Red }
            default      { Write-Host "$verdict" -ForegroundColor Gray }
        }
    } catch {
        $results += [PSCustomObject]@{
            Name    = $skillName
            Score   = $null
            Verdict = 'ERROR'
            Output  = $_.Exception.Message
        }
        Write-Host "ERROR" -ForegroundColor Red
    }
}

$stopwatch.Stop()

# Summary
$passCount = ($results | Where-Object { $_.Verdict -eq 'PASS' }).Count
$failCount = ($results | Where-Object { $_.Verdict -eq 'FAIL' }).Count
$borderlineCount = ($results | Where-Object { $_.Verdict -eq 'BORDERLINE' }).Count
$errorCount = ($results | Where-Object { $_.Verdict -eq 'ERROR' }).Count
$unknownCount = ($results | Where-Object { $_.Verdict -eq 'UNKNOWN' }).Count

Write-Host "`n=========================" -ForegroundColor Cyan
Write-Host "📊 Summary" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "  Total:      $($results.Count)"
Write-Host "  ✅ PASS:      $passCount" -ForegroundColor Green
if ($borderlineCount -gt 0) {
    Write-Host "  ⚠️ BORDERLINE: $borderlineCount" -ForegroundColor Yellow
    $results | Where-Object { $_.Verdict -eq 'BORDERLINE' } | ForEach-Object {
        Write-Host "    - $($_.Name) ($($_.Score)%)" -ForegroundColor Yellow
    }
}
if ($failCount -gt 0) {
    Write-Host "  ❌ FAIL:      $failCount" -ForegroundColor Red
    $results | Where-Object { $_.Verdict -eq 'FAIL' } | ForEach-Object {
        Write-Host "    - $($_.Name) ($($_.Score)%)" -ForegroundColor Red
    }
}
if ($errorCount -gt 0) {
    Write-Host "  💥 ERROR:     $errorCount" -ForegroundColor Red
    $results | Where-Object { $_.Verdict -eq 'ERROR' } | ForEach-Object {
        Write-Host "    - $($_.Name)" -ForegroundColor Red
    }
}
Write-Host "  ⏱️ Time:      $([math]::Round($stopwatch.Elapsed.TotalSeconds, 1))s"

# Exit code
if ($failCount -gt 0 -or $errorCount -gt 0) {
    exit 1
} elseif ($borderlineCount -gt 0) {
    exit 2
} else {
    exit 0
}
