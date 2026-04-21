# Import-Data.ps1
# Non-interactive script to import sample data for a module into an environment
# Called by the Data Importer UI

param(
    [Parameter(Mandatory=$true)]
    [string]$Deployment,
    
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentKey,
    
    [Parameter(Mandatory=$true)]
    [string]$ModulePath
)

$ErrorActionPreference = "Stop"

# Get project root (go up from ui-tools/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Import Sample Data ===" -ForegroundColor Cyan
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
    
    # Get environment
    if (-not $deploymentConfig.Environments.$EnvironmentKey) {
        throw "Environment '$EnvironmentKey' not found in deployment '$Deployment'"
    }
    
    $targetEnv = $deploymentConfig.Environments.$EnvironmentKey
    Write-Host "Environment: $targetEnv" -ForegroundColor Green
    
    # Validate module path
    $fullModulePath = Join-Path $projectRoot $ModulePath
    if (-not (Test-Path $fullModulePath)) {
        throw "Module path not found: $fullModulePath"
    }
    
    $moduleName = Split-Path $ModulePath -Leaf
    Write-Host "Module: $moduleName" -ForegroundColor Green
    Write-Host ""
    
    # Check for sample data
    $sampleDataPath = Join-Path $fullModulePath "sample-data"
    $dataZipPath = Join-Path $sampleDataPath "data.zip"
    $govDataZipPath = Join-Path $sampleDataPath "gov-data.zip"
    
    # Determine which data file to use
    $dataFile = $null
    if (Test-Path $dataZipPath) {
        $dataFile = $dataZipPath
        Write-Host "Found data.zip" -ForegroundColor Green
    } elseif (Test-Path $govDataZipPath) {
        $dataFile = $govDataZipPath
        Write-Host "Found gov-data.zip" -ForegroundColor Green
    } else {
        throw "No sample data found. Expected data.zip or gov-data.zip in $sampleDataPath"
    }
    
    Write-Host "Data file: $dataFile" -ForegroundColor Gray
    Write-Host ""
    
    # Connect to tenant
    Write-Host "Connecting to tenant ($tenant)..." -ForegroundColor Yellow
    Connect-DataverseTenant -authProfile $tenant
    
    # Connect to environment
    Write-Host "Connecting to environment ($targetEnv)..." -ForegroundColor Yellow
    Connect-DataverseEnvironment -envName $targetEnv
    
    # Import the data
    Write-Host ""
    Write-Host "Importing sample data..." -ForegroundColor Yellow
    Write-Host ""
    
    pac data import --data $dataFile --verbose
    
    if ($LASTEXITCODE -ne 0) {
        throw "Data import failed with exit code: $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Data import complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    exit 0
}
catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
