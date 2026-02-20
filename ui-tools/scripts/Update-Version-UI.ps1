# Update-Version-UI.ps1
# Non-interactive script to update a module's version (online and local)
# Called by the Deployment UI

param(
    [Parameter(Mandatory=$true)]
    [string]$Deployment,
    
    [Parameter(Mandatory=$true)]
    [string]$Category,
    
    [Parameter(Mandatory=$true)]
    [string]$Module,
    
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

# Get project root (go up from deployment-ui/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Update Version: $Category/$Module ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Validate version format (4-part)
    if ($Version -notmatch '^\d+\.\d+\.\d+\.\d+$') {
        throw "Invalid version format. Expected format: Major.Minor.Build.Revision (e.g., 1.0.0.0)"
    }
    
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
    Write-Host "New Version: $Version" -ForegroundColor Green
    
    # Get module config to determine source environment
    $moduleConfig = if ($config.Modules.$Module) {
        $config.Modules.$Module
    } else {
        $config.DefaultModule
    }
    $sourceEnvKey = $moduleConfig.Environment
    
    if (-not $deploymentConfig.Environments.$sourceEnvKey) {
        throw "Source environment '$sourceEnvKey' not found in deployment '$Deployment'"
    }
    
    $sourceEnv = $deploymentConfig.Environments.$sourceEnvKey
    Write-Host "Source Environment: $sourceEnv" -ForegroundColor Green
    Write-Host ""
    
    # Get module path
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    # Get solution unique name from Solution.xml
    $solutionXmlPath = Join-Path $modulePath "src\Other\Solution.xml"
    if (-not (Test-Path $solutionXmlPath)) {
        throw "Solution.xml not found: $solutionXmlPath"
    }
    
    [xml]$solutionXml = Get-Content $solutionXmlPath
    $solutionName = $solutionXml.SelectSingleNode("/ImportExportXml/SolutionManifest/UniqueName").InnerText
    
    if (-not $solutionName) {
        throw "Could not read solution unique name from Solution.xml"
    }
    
    Write-Host "Solution Name: $solutionName" -ForegroundColor Gray
    Write-Host ""
    
    # Connect to tenant
    Write-Host "Connecting to tenant ($tenant)..." -ForegroundColor Yellow
    Connect-DataverseTenant -authProfile $tenant
    
    # Connect to source environment
    Write-Host "Connecting to source environment ($sourceEnv)..." -ForegroundColor Yellow
    Connect-DataverseEnvironment -envName $sourceEnv
    
    # Update online version
    Write-Host ""
    Write-Host "Updating online version to $Version..." -ForegroundColor Yellow
    pac solution online-version --solution-name $solutionName --solution-version $Version
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to update online version"
    }
    
    Write-Host "[OK] Online version updated successfully" -ForegroundColor Green
    Write-Host ""
    
    # Sync to local
    Write-Host "Syncing solution to local..." -ForegroundColor Yellow
    Set-Location $modulePath
    pac solution sync
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to sync solution to local"
    }
    
    Write-Host "[OK] Solution synced to local" -ForegroundColor Green
    Write-Host ""
    
    # Verify local version was updated
    $localVersion = Read-SolutionVersion -xmlFilePath $solutionXmlPath
    if ($localVersion -eq $Version) {
        Write-Host "[OK] Local version verified: $localVersion" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Local version mismatch. Expected: $Version, Got: $localVersion" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "=== Version Update Complete ===" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
