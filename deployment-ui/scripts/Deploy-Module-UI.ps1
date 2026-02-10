# Deploy-Module-UI.ps1
# Non-interactive script to deploy a module to an environment
# Called by the Deployment UI

param(
    [Parameter(Mandatory=$true)]
    [string]$Deployment,
    
    [Parameter(Mandatory=$true)]
    [string]$Category,
    
    [Parameter(Mandatory=$true)]
    [string]$Module,
    
    [Parameter(Mandatory=$false)]
    [switch]$Managed
)

$ErrorActionPreference = "Stop"

# Get project root (go up from deployment-ui/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Deploy Module: $Category/$Module ===" -ForegroundColor Cyan
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
    
    # Get module config to determine environment
    $moduleConfig = if ($config.Modules.$Module) {
        $config.Modules.$Module
    } else {
        $config.DefaultModule
    }
    
    $envKey = $moduleConfig.Environment
    
    if (-not $deploymentConfig.Environments.$envKey) {
        throw "Environment '$envKey' not found in deployment '$Deployment'"
    }
    
    $targetEnv = $deploymentConfig.Environments.$envKey
    Write-Host "Environment: $targetEnv" -ForegroundColor Green
    Write-Host ""
    
    # Connect to tenant
    Write-Host "Connecting to tenant ($tenant)..." -ForegroundColor Yellow
    Connect-DataverseTenant -authProfile $tenant
    
    # Connect to environment
    Write-Host "Connecting to environment ($targetEnv)..." -ForegroundColor Yellow
    Connect-DataverseEnvironment -envName $targetEnv
    
    # Deploy the module
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    Write-Host ""
    Write-Host "Building and deploying solution..." -ForegroundColor Yellow
    Write-Host "Path: $modulePath" -ForegroundColor Gray
    
    if ($Managed) {
        Write-Host "Type: Managed Solution" -ForegroundColor Cyan
    } else {
        Write-Host "Type: Unmanaged Solution" -ForegroundColor Cyan
    }
    
    Write-Host ""
    
    # Use the existing Deploy-Solution function from Util.ps1
    if ($Managed) {
        Deploy-Solution -SolutionPath $modulePath -Managed -AutoConfirm
    } else {
        Deploy-Solution -SolutionPath $modulePath -AutoConfirm
    }
    
    Write-Host ""
    Write-Host "=== Deployment Complete ===" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
