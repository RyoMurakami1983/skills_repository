# Install pre-commit and pre-push hooks into the current repository (PowerShell).

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) {
    Write-Error "Not inside a git repository."
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$hookDir = Join-Path $repoRoot ".git\hooks"

New-Item -ItemType Directory -Force -Path $hookDir | Out-Null
Copy-Item (Join-Path $scriptDir "pre-commit") (Join-Path $hookDir "pre-commit") -Force
Copy-Item (Join-Path $scriptDir "pre-commit.ps1") (Join-Path $hookDir "pre-commit.ps1") -Force
Copy-Item (Join-Path $scriptDir "pre-push") (Join-Path $hookDir "pre-push") -Force
Copy-Item (Join-Path $scriptDir "pre-push.ps1") (Join-Path $hookDir "pre-push.ps1") -Force

Write-Host "✅ Installed pre-commit and pre-push hooks to $hookDir" -ForegroundColor Green
