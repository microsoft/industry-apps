# Ship-Module-UI.ps1
# Non-interactive script to ship a module to an external tenant/environment
# Called by the Deployment UI

param(
    [Parameter(Mandatory=$true)][string]$Deployment,
    [Parameter(Mandatory=$true)][string]$Environment,
    [Parameter(Mandatory=$true)][string]$Category,
    [Parameter(Mandatory=$true)][string]$Module
)

$ErrorActionPreference = "Stop"

# Get project root (go up from deployment-ui/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Ship Module: $Category/$Module ===" -ForegroundColor Cyan
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
    
    # Get target environment
    if (-not $deploymentConfig.Environments.$Environment) {
        throw "Environment '$Environment' not found in deployment '$Deployment'"
    }
    
    $targetEnv = $deploymentConfig.Environments.$Environment
    Write-Host "Environment: $targetEnv" -ForegroundColor Green
    Write-Host ""
    
    # Connect to tenant
    Write-Host "Connecting to tenant ($tenant)..." -ForegroundColor Yellow
    Connect-DataverseTenant -authProfile $tenant
    
    # Connect to environment
    Write-Host "Connecting to environment ($targetEnv)..." -ForegroundColor Yellow
    Connect-DataverseEnvironment -envName $targetEnv
    
    # Ship the module (managed)
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    Write-Host ""
    Write-Host "Shipping managed solution to external tenant..." -ForegroundColor Yellow
    Write-Host "Path: $modulePath" -ForegroundColor Gray
    
    # Construct settings file path
    $settingsFolder = "$projectRoot\.config\$tenant"
    $envFileName = $Environment -replace ' ', '-'
    $settingsFile = "$settingsFolder\$envFileName.json"
    
    # Debug: Show settings file path and whether it exists
    Write-Host "Settings file path: $settingsFile" -ForegroundColor Gray
    if (Test-Path $settingsFile) {
        Write-Host "Settings file found" -ForegroundColor Green
    } else {
        Write-Host "Settings file not found (will deploy without settings)" -ForegroundColor Yellow
    }
    Write-Host ""
    
    Deploy-Solution $modulePath -Managed -AutoConfirm -SettingsFile $settingsFile
    
    Write-Host ""
    Write-Host "=== Ship Complete ===" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
