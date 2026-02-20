# Release-Module-UI.ps1
# Non-interactive script to create a release for a module
# Called by the Deployment UI

param(
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
    Write-Host "=== Create Release: $Category/$Module ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Get module path
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    # Get current version from Solution.xml
    $solutionXmlPath = Join-Path $modulePath "src\Other\Solution.xml"
    if (-not (Test-Path $solutionXmlPath)) {
        throw "Solution.xml not found: $solutionXmlPath"
    }
    
    $version = Read-SolutionVersion -xmlFilePath $solutionXmlPath
    
    if ([string]::IsNullOrEmpty($version)) {
        throw "Could not read version from Solution.xml"
    }
    
    Write-Host "Module: $Module" -ForegroundColor Green
    Write-Host "Version: $version" -ForegroundColor Green
    Write-Host ""
    
    # Get the project name from .cdsproj file first
    $projectFile = Get-ChildItem -Path $modulePath -Filter "*.cdsproj" | Select-Object -First 1
    if (-not $projectFile) {
        throw "No .cdsproj file found in module directory"
    }
    
    $projectName = $projectFile.BaseName
    Write-Host "Project Name: $projectName" -ForegroundColor Gray
    Write-Host ""
    
    # Build the solution
    Write-Host "Building solution packages..." -ForegroundColor Yellow
    Set-Location $modulePath
    dotnet build /p:configuration=Release
    
    # Check if build artifacts were created (ignore exit code since cleanup can fail)
    $artifactFolder = Join-Path $modulePath "bin\Release"
    $unmanagedZip = Join-Path $artifactFolder "$projectName.zip"
    $managedZip = Join-Path $artifactFolder "${projectName}_managed.zip"
    
    if (-not (Test-Path $unmanagedZip) -and -not (Test-Path $managedZip)) {
        throw "Failed to build solution: No package files were generated"
    }
    
    Write-Host "[OK] Solution packages built" -ForegroundColor Green
    Write-Host ""
    
    # Create project-level releases folder organized by module
    $projectReleasesFolder = Join-Path $projectRoot ".releases"
    $moduleReleasesFolder = Join-Path $projectReleasesFolder $Module
    
    if (-not (Test-Path $projectReleasesFolder)) {
        New-Item -ItemType Directory -Path $projectReleasesFolder -Force | Out-Null
    }
    
    if (-not (Test-Path $moduleReleasesFolder)) {
        New-Item -ItemType Directory -Path $moduleReleasesFolder -Force | Out-Null
        Write-Host "Created releases folder: $moduleReleasesFolder" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Copy solution artifacts with new naming format
    Write-Host "Copying solution artifacts..." -ForegroundColor Yellow
    
    # Naming format: App-Base-Module-Name-v1.0.0.0.zip
    $unmanagedTarget = Join-Path $moduleReleasesFolder "$projectName-v$version.zip"
    $managedTarget = Join-Path $moduleReleasesFolder "$projectName-Managed-v$version.zip"
    
    if (Test-Path $unmanagedZip) {
        Copy-Item -Path $unmanagedZip -Destination $unmanagedTarget -Force
        Write-Host "[OK] Copied: $(Split-Path $unmanagedTarget -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Unmanaged package not found: $unmanagedZip" -ForegroundColor Yellow
    }
    
    if (Test-Path $managedZip) {
        Copy-Item -Path $managedZip -Destination $managedTarget -Force
        Write-Host "[OK] Copied: $(Split-Path $managedTarget -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Managed package not found: $managedZip" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "=== Release Created Successfully ===" -ForegroundColor Green
    Write-Host "Version: $version" -ForegroundColor Cyan
    Write-Host "Location: $moduleReleasesFolder" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Release artifacts:" -ForegroundColor Cyan
    Get-ChildItem -Path $moduleReleasesFolder -Filter "*-v$version.zip" | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
