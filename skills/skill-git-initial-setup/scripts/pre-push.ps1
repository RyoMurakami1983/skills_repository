# Prevent direct pushes to protected branches (PowerShell version).

$protectedBranches = @('main')
$currentBranch = (git symbolic-ref --short HEAD 2>$null).Trim()

if (-not $currentBranch) {
    exit 0
}

if ($protectedBranches -contains $currentBranch) {
    Write-Host "" 
    Write-Host "❌ ERROR: Direct push to '$currentBranch' is not allowed." -ForegroundColor Red
    Write-Host "" 
    Write-Host "Use a feature branch and open a Pull Request:" -ForegroundColor Yellow
    Write-Host "  1. git checkout -b feature/your-change"
    Write-Host "  2. git push origin feature/your-change"
    Write-Host "" 
    exit 1
}

exit 0
