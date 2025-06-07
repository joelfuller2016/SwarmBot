#!/usr/bin/env pwsh
# SwarmBot Unified Launcher for PowerShell
# Single entry point for all modes

param(
    [Parameter(Position=0)]
    [ValidateSet('standard', 'enhanced', 'auto', '--help', '--check', '--clean')]
    [string]$Mode,
    
    [switch]$Help,
    [switch]$Check,
    [switch]$Clean
)

# Set UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONWARNINGS = "ignore::ResourceWarning"

# Check if we're in scripts directory and move to parent
if (Test-Path ..\swarmbot.py) {
    Set-Location ..
}

# Check if swarmbot.py exists
if (-not (Test-Path swarmbot.py)) {
    Write-Host "`n❌ ERROR: swarmbot.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the SwarmBot directory.`n"
    pause
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ".venv\Scripts\Activate.ps1"
}

# Display header
Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                 🤖 SwarmBot Launcher                     " -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Build command arguments
$args = @()

if ($Mode) {
    $args += $Mode
}

if ($Help) {
    $args += "--help"
}

if ($Check) {
    $args += "--check"
}

if ($Clean) {
    $args += "--clean"
}

# Run SwarmBot
if ($args.Count -eq 0) {
    # No arguments - run interactive mode
    python swarmbot.py
} else {
    # Pass arguments to swarmbot.py
    python swarmbot.py $args
}

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ SwarmBot exited with an error." -ForegroundColor Red
    Write-Host ""
}

# Pause to see any messages
pause
