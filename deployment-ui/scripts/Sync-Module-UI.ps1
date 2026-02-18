# Sync-Module-UI.ps1
# Non-interactive script to sync a module from an environment
# Called by the Deployment UI

param(
    [Parameter(Mandatory=$true)]
    [string]$Deployment,
    
    [Parameter(Mandatory=$true)]
    [string]$Category,
    
    [Parameter(Mandatory=$true)]
    [string]$Module
)

$ErrorActionPreference = "Stop"

# Get project root (go up from deployment-ui/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Sync Module: $Category/$Module ===" -ForegroundColor Cyan
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
    
    # Sync the module
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    Write-Host ""
    Write-Host "Syncing module from environment..." -ForegroundColor Yellow
    Write-Host "Path: $modulePath" -ForegroundColor Gray
    Write-Host ""
    
    Set-Location $modulePath
    pac solution sync
    
    Write-Host ""
    Write-Host "Building unmanaged and managed solution packages..." -ForegroundColor Yellow
    
    # Build to create both unmanaged and managed zip files
    dotnet build /p:configuration=Release
    
    # Verify both zip files were created
    $cdsprojFile = Get-ChildItem -Path $modulePath -Filter *.cdsproj | Select-Object -First 1
    $baseName = $cdsprojFile.BaseName
    $unmanagedZip = Join-Path $modulePath "bin\debug\${baseName}.zip"
    $managedZip = Join-Path $modulePath "bin\debug\${baseName}_managed.zip"
    
    if (Test-Path $unmanagedZip) {
        Write-Host "[OK] Unmanaged solution package created" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Unmanaged solution package not found: $unmanagedZip" -ForegroundColor Yellow
    }
    
    if (Test-Path $managedZip) {
        Write-Host "[OK] Managed solution package created" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Managed solution package not found: $managedZip" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "=== Sync Complete ===" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
