#!/usr/bin/env pwsh
# PowerShell version of backup script for Windows
param(
    [Parameter(Mandatory=$true)]
    [string]$PhaseName
)

$BACKUP_DIR = "migration_backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

if (-not $PhaseName) {
    Write-Host "Usage: .\backup_migration_point.ps1 <phase_name>"
    exit 1
}

# Create backup directory if it doesn't exist
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR
}

# Create tar archive excluding git and cache files
$archiveName = "$BACKUP_DIR\${PhaseName}_${TIMESTAMP}.tar.gz"

# Use git archive for a clean backup (excludes .git, __pycache__, etc. automatically)
git archive --format=tar.gz --output="$archiveName" HEAD

Write-Host "✅ Backup created: $archiveName"
