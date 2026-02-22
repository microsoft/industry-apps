# Sync-Module-From-Environment-UI.ps1
# Non-interactive script to sync a module FROM a specific environment (bidirectional sync)
# Called by the Deployment UI for hotfix scenarios
# This overwrites local files with the solution from the specified environment

param(
    [Parameter(Mandatory=$true)]
    [string]$Deployment,
    
    [Parameter(Mandatory=$true)]
    [string]$Category,
    
    [Parameter(Mandatory=$true)]
    [string]$Module,
    
    [Parameter(Mandatory=$true)]
    [string]$SourceEnvironment
)

$ErrorActionPreference = "Stop"

# Get project root (go up from ui-tools/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Sync Module FROM Environment ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "WARNING: This will OVERWRITE local module files!" -ForegroundColor Yellow
    Write-Host "    Module: $Category/$Module" -ForegroundColor Yellow
    Write-Host "    Source: $SourceEnvironment" -ForegroundColor Yellow
    Write-Host ""
    
    # Load deployment config
    $configPath = "$projectRoot\.config\deployments.json"
    if (-not (Test-Path $configPath)) {
        throw "Configuration file not found: $configPath"
    }
    
    $config = Get-Content $configPath | ConvertFrom-Json
    
    # Get deployment info
    if (-not $config.Deployments.$Deployment) {
        throw "Deployment '$Deployment' not found in configuration"
    }
    
    $deploymentConfig = $config.Deployments.$Deployment
    $tenant = $deploymentConfig.Tenant
    
    Write-Host "Deployment: $Deployment" -ForegroundColor Green
    Write-Host "Tenant: $tenant" -ForegroundColor Green
    
    # Find the environment by name (not key!)
    $targetEnv = $null
    foreach ($envKey in $deploymentConfig.Environments.PSObject.Properties.Name) {
        if ($deploymentConfig.Environments.$envKey -eq $SourceEnvironment) {
            $targetEnv = $SourceEnvironment
            break
        }
    }
    
    if (-not $targetEnv) {
        throw "Environment '$SourceEnvironment' not found in deployment '$Deployment'"
    }
    
    Write-Host "Source Environment: $targetEnv" -ForegroundColor Green
    Write-Host ""
    
    # Connect to tenant
    Write-Host "Connecting to tenant ($tenant)..." -ForegroundColor Yellow
    Connect-DataverseTenant -authProfile $tenant
    
    # Connect to environment
    Write-Host "Connecting to environment ($targetEnv)..." -ForegroundColor Yellow
    Connect-DataverseEnvironment -envName $targetEnv
    
    # Sync the module (this will overwrite local files)
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    Write-Host ""
    Write-Host "Syncing module FROM environment (OVERWRITING local files)..." -ForegroundColor Yellow
    Write-Host "Path: $modulePath" -ForegroundColor Gray
    Write-Host ""
    
    Set-Location $modulePath
    pac solution sync
    
    if ($LASTEXITCODE -ne 0) {
        throw "pac solution sync failed with exit code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "=== Sync FROM Environment Complete ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Local module files have been updated with solution from $SourceEnvironment" -ForegroundColor Green
    Write-Host "Remember to commit these changes if you want to keep them!" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
