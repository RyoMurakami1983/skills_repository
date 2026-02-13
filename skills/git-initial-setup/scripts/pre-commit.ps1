# Prevent direct commits to protected branches (PowerShell version).

$protectedBranches = @('main')
$currentBranch = (git symbolic-ref --short HEAD 2>$null).Trim()

if (-not $currentBranch) {
    exit 0
}

if ($protectedBranches -contains $currentBranch) {
    Write-Host ""
    Write-Host "❌ ERROR: Direct commits to '$currentBranch' are not allowed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Use a feature branch instead:" -ForegroundColor Yellow
    Write-Host "  1. git checkout -b feature/your-change"
    Write-Host ""
    exit 1
}

exit 0
