# New-Module-UI.ps1
# Non-interactive script to create a new module
# Called by the Deployment UI

param(
    [Parameter(Mandatory=$true)]
    [string]$Category,
    
    [Parameter(Mandatory=$true)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$false)]
    [switch]$Deploy
)

$ErrorActionPreference = "Stop"

# Get project root (go up from deployment-ui/scripts to repo root)
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

# Source utility functions
. "$projectRoot\.scripts\Util.ps1"

try {
    Write-Host "=== Create New Module ===" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Category: $Category" -ForegroundColor Green
    Write-Host "Module Name: $ModuleName" -ForegroundColor Green
    Write-Host ""
    
    # Ensure category folder exists
    $categoryPath = Join-Path $projectRoot $Category
    if (-not (Test-Path $categoryPath)) {
        Write-Host "Creating category folder: $Category" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $categoryPath -Force | Out-Null
    }
    
    # Clean up module folder name 
    $solutionFolderName = $ModuleName -replace '[^a-zA-Z0-9]', '-'
    $solutionFolderName = $solutionFolderName -replace '-+', '-'
    $solutionFolderName = $solutionFolderName.Trim('-')
    $solutionFolderName = $solutionFolderName.ToLower()
    
    # PAC CLI project name (no spaces or special chars)
    $pacFriendlyName = $ModuleName -replace '[^a-zA-Z0-9]', ''
    
    # Build Proper-Cased, hyphenated name for the .cdsproj filename
    $projectCasedHyphenName = $ModuleName -replace '[^a-zA-Z0-9]', '-'
    $projectCasedHyphenName = $projectCasedHyphenName -replace '-+', '-'
    $projectCasedHyphenName = $projectCasedHyphenName.Trim('-')
    
    # Capitalize each token and join with hyphens
    $tokens = $projectCasedHyphenName.Split('-') | Where-Object { $_ -ne '' }
    $tokens = $tokens | ForEach-Object { if ($_.Length -gt 1) { $_.Substring(0,1).ToUpper() + $_.Substring(1).ToLower() } else { $_.ToUpper() } }
    $projectCasedHyphenName = ($tokens -join '-')
    
    # Solution unique name
    $solutionUniqueName = $ModuleName -replace '[^a-zA-Z0-9\-]', ''
    $solutionUniqueName = $solutionUniqueName.ToLower().Replace("-", "_")
    
    $customizationPrefix = "appbase"
    $publisherSchemaName = "appbase"
    $publisherName = "Base Industry Modules"
    $friendlyPrefix = "Base Industry Module"
    $pacFriendlyPrefix = "App-Base"
    
    $solutionUniqueName = "${publisherSchemaName}_${solutionUniqueName}"
    $projectName = "${pacFriendlyPrefix}-${projectCasedHyphenName}"
    
    # Module path
    $moduleFolderPath = Join-Path $categoryPath $solutionFolderName
    
    # Check if module already exists
    if (Test-Path $moduleFolderPath) {
        throw "Module already exists at: $moduleFolderPath"
    }
    
    Write-Host "Creating module folder: $moduleFolderPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $moduleFolderPath -Force | Out-Null
    
    # Create solution using PAC CLI
    Write-Host "Creating solution structure..." -ForegroundColor Yellow
    Set-Location $moduleFolderPath
    
    pac solution init --publisher-name $publisherName --publisher-prefix $customizationPrefix --outputDirectory .
    
    # Rename the .cdsproj file
    $defaultProjectFile = Get-ChildItem -Path $moduleFolderPath -Filter "*.cdsproj" | Select-Object -First 1
    if ($defaultProjectFile) {
        $newProjectFileName = "$projectName.cdsproj"
        Rename-Item -Path $defaultProjectFile.FullName -NewName $newProjectFileName
        Write-Host "Created project file: $newProjectFileName" -ForegroundColor Green
    }
    
    # Update Solution.xml
    $solutionXmlPath = Join-Path $moduleFolderPath "src\Other\Solution.xml"
    if (Test-Path $solutionXmlPath) {
        Write-Host "Updating Solution.xml..." -ForegroundColor Yellow
        
        [xml]$solutionXml = Get-Content $solutionXmlPath
        $solutionXml.ImportExportXml.SolutionManifest.UniqueName = $solutionUniqueName
        $solutionXml.ImportExportXml.SolutionManifest.LocalizedNames.LocalizedName.description = "$friendlyPrefix $ModuleName"
        $solutionXml.Save($solutionXmlPath)
        
        Write-Host "Solution unique name: $solutionUniqueName" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "=== Module Created Successfully ===" -ForegroundColor Green
    Write-Host "Location: $moduleFolderPath" -ForegroundColor Cyan
    
    # Optionally deploy to development
    if ($Deploy) {
        Write-Host ""
        Write-Host "Deploying to development environment..." -ForegroundColor Yellow
        
        # Load config to get default deployment settings
        $configPath = "$projectRoot\.config\deployments.json"
        if (Test-Path $configPath) {
            $config = Get-Content $configPath | ConvertFrom-Json
            $defaultDeployment = $config.DefaultModule.Tenant
            $defaultEnv = $config.DefaultModule.Environment
            
            if ($defaultDeployment -and $defaultEnv) {
                $deploymentConfig = $config.Deployments.$defaultDeployment
                $tenant = $deploymentConfig.Tenant
                $targetEnv = $deploymentConfig.Environments.$defaultEnv
                
                Connect-DataverseTenant -authProfile $tenant
                Connect-DataverseEnvironment -envName $targetEnv
                
                Deploy-Solution $moduleFolderPath -AutoConfirm
            }
        }
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
