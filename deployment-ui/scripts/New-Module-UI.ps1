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
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

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
    
    # Module paths
    $moduleFolderPath = Join-Path $categoryPath $solutionFolderName
    $tempModulePath = Join-Path $categoryPath $pacFriendlyName
    
    # Check if module already exists
    if (Test-Path $moduleFolderPath) {
        throw "Module already exists at: $moduleFolderPath"
    }
    
    Write-Host "Creating module folder: $tempModulePath" -ForegroundColor Yellow
    
    # Create solution using PAC CLI with schema name (no spaces)
    Write-Host "Creating solution structure..." -ForegroundColor Yellow
    
    pac solution init --publisher-name $publisherSchemaName --publisher-prefix $customizationPrefix --outputDirectory $tempModulePath
    
    # Rename folder to final name if needed (Windows requires two-step rename for case-only changes)
    if ($pacFriendlyName -cne $solutionFolderName) {
        Write-Host "Renaming to: $moduleFolderPath" -ForegroundColor Yellow
        
        # Two-step rename to handle case-only changes on Windows
        $tempRenamePath = Join-Path $categoryPath "$pacFriendlyName-temp-rename"
        Rename-Item $tempModulePath $tempRenamePath
        Rename-Item $tempRenamePath $solutionFolderName
    }
    
    # Update Solution.xml with friendly names
    $solutionXmlPath = Join-Path $moduleFolderPath "src\Other\Solution.xml"
    if (Test-Path $solutionXmlPath) {
        Write-Host "Updating Solution.xml..." -ForegroundColor Yellow
        
        [xml]$solutionXml = Get-Content $solutionXmlPath
        
        # Update solution unique name
        $solutionXml.ImportExportXml.SolutionManifest.UniqueName = $solutionUniqueName
        
        # Update solution friendly name
        $solutionXml.ImportExportXml.SolutionManifest.LocalizedNames.LocalizedName.description = "$friendlyPrefix - $ModuleName"
        
        # Update publisher display name
        $publisherNode = $solutionXml.ImportExportXml.SolutionManifest.Publisher
        if ($publisherNode) {
            $publisherNode.LocalizedNames.LocalizedName.description = $publisherName
        }
        
        $solutionXml.Save($solutionXmlPath)
        
        Write-Host "Solution unique name: $solutionUniqueName" -ForegroundColor Green
    }
    
    # Rename the .cdsproj file
    $defaultProjectFile = Get-ChildItem -Path $moduleFolderPath -Filter "*.cdsproj" | Select-Object -First 1
    if ($defaultProjectFile) {
        $newProjectFileName = "$projectName.cdsproj"
        Rename-Item -Path $defaultProjectFile.FullName -NewName $newProjectFileName
        Write-Host "Created project file: $newProjectFileName" -ForegroundColor Green
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
                
                Set-Location $moduleFolderPath
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
