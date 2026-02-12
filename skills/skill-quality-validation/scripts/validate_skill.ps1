<#
.SYNOPSIS
    SKILL.md Quality Validator (PowerShell Wrapper)

.DESCRIPTION
    Validates GitHub Copilot agent skills by calling the Python validation script.
    Provides Windows-friendly interface with automatic Python environment detection.

.PARAMETER SkillPath
    Path to SKILL.md file or skill directory

.PARAMETER Json
    Output results in JSON format

.PARAMETER OutputFile
    Optional output file path for report

.EXAMPLE
    .\validate_skill.ps1 -SkillPath ..\SKILL.md
    
.EXAMPLE
    .\validate_skill.ps1 -SkillPath ..\SKILL.md -Json -OutputFile report.json

.NOTES
    Author: RyoMurakami1983
    Version: 3.0.0
    Last Updated: 2026-02-12
    
    This is a wrapper script that calls validate_skill.py.
    Requires Python 3.7+ to be installed.
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$SkillPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$Json,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = ''
)

# Color output functions
function Write-ColorOutput {
    param([string]$Message, [string]$ForegroundColor)
    if ($ForegroundColor) {
        Write-Host $Message -ForegroundColor $ForegroundColor
    } else {
        Write-Host $Message
    }
}

function Write-Info { param([string]$Message) Write-ColorOutput $Message 'Cyan' }
function Write-Success { param([string]$Message) Write-ColorOutput $Message 'Green' }
function Write-Error { param([string]$Message) Write-ColorOutput $Message 'Red' }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message 'Yellow' }

# Find Python executable
function Find-Python {
    $pythonCommands = @('python3', 'python', 'py')
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1 | Out-String
            if ($version -match 'Python 3\.(\d+)') {
                $minorVersion = [int]$Matches[1]
                if ($minorVersion -ge 7) {
                    Write-Info "✅ Found Python: $($version.Trim())"
                    return $cmd
                }
            }
        } catch {
            continue
        }
    }
    
    return $null
}

# Main execution
try {
    Write-Info "`n🔍 SKILL.md Quality Validator (PowerShell Wrapper)"
    Write-Info "=================================================="
    Write-Host ""
    
    # Check Python availability
    Write-Info "Checking Python environment..."
    $python = Find-Python
    
    if (-not $python) {
        Write-Error "❌ Python 3.7+ not found!"
        Write-Host ""
        Write-Host "Please install Python 3.7 or later from:"
        Write-Host "  - https://www.python.org/downloads/"
        Write-Host "  - Microsoft Store (search 'Python')"
        Write-Host "  - winget install Python.Python.3.11"
        Write-Host ""
        exit 1
    }
    
    # Locate Python script
    $scriptDir = $PSScriptRoot
    $pythonScript = Join-Path $scriptDir "validate_skill.py"
    
    if (-not (Test-Path $pythonScript)) {
        Write-Error "❌ validate_skill.py not found at: $pythonScript"
        exit 1
    }
    
    # Resolve skill path
    if (Test-Path $SkillPath -PathType Container) {
        $SkillPath = Join-Path $SkillPath "SKILL.md"
    }
    
    if (-not (Test-Path $SkillPath)) {
        Write-Error "❌ SKILL.md not found at: $SkillPath"
        exit 1
    }
    
    # Build Python command arguments
    $args = @($pythonScript, $SkillPath)
    
    if ($Json) {
        $args += '--json'
    }
    
    if ($OutputFile) {
        $args += '--output', $OutputFile
    }
    
    # Execute Python script
    Write-Info "Running validation..."
    Write-Host ""
    
    & $python @args
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Success "✅ Validation completed successfully"
    } else {
        Write-Warning "⚠️ Validation completed with issues (exit code: $exitCode)"
    }
    
    exit $exitCode
    
} catch {
    Write-Error "`n❌ Error: $_"
    Write-Host $_.ScriptStackTrace
    exit 1
}
