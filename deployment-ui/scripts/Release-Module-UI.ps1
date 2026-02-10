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

function Get-NewFileName ($originalName, $newVersion, $solutionName) {
    if (-not [string]::IsNullOrEmpty($newVersion)) {
        $extension = [System.IO.Path]::GetExtension($originalName)
        
        # Extract the module name from the solution name (remove "App-Base-" prefix)
        $moduleName = $solutionName -replace '^App-Base-', ''
        
        # Check if this is a managed solution
        if ($originalName -like "*_managed*") {
            return "AppBase-{0}_managed - {1}{2}" -f $moduleName, $newVersion, $extension
        } else {
            return "AppBase-{0} - {1}{2}" -f $moduleName, $newVersion, $extension
        }
    }
    return $originalName
}

try {
    Write-Host "=== Create Release: $Category/$Module ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Get module path
    $modulePath = Join-Path $projectRoot $Category
    $modulePath = Join-Path $modulePath $Module
    
    if (-not (Test-Path $modulePath)) {
        throw "Module path not found: $modulePath"
    }
    
    # Get solution version from Solution.xml
    $solutionXmlPath = Join-Path $modulePath "src\Other\Solution.xml"
    if (-not (Test-Path $solutionXmlPath)) {
        throw "Solution.xml not found at: $solutionXmlPath"
    }
    
    [xml]$solutionXml = Get-Content $solutionXmlPath
    $version = $solutionXml.ImportExportXml.SolutionManifest.Version.Version
    
    if ([string]::IsNullOrEmpty($version)) {
        throw "Could not read version from Solution.xml"
    }
    
    Write-Host "Module: $Module" -ForegroundColor Green
    Write-Host "Version: $version" -ForegroundColor Green
    Write-Host ""
    
    # Create releases folder structure
    $releasesFolder = Join-Path $projectRoot "releases"
    $versionFolder = Join-Path $releasesFolder "v$version"
    
    if (-not (Test-Path $releasesFolder)) {
        New-Item -ItemType Directory -Path $releasesFolder -Force | Out-Null
    }
    
    if (Test-Path $versionFolder) {
        Write-Host "Release folder already exists: $versionFolder" -ForegroundColor Yellow
        Write-Host "Removing existing release folder..." -ForegroundColor Yellow
        Remove-Item -Path $versionFolder -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $versionFolder -Force | Out-Null
    Write-Host "Created release folder: $versionFolder" -ForegroundColor Green
    Write-Host ""
    
    # Build the solution
    Write-Host "Building solution..." -ForegroundColor Yellow
    Build-Solution -SolutionPath $modulePath
    
    # Get the project name from .cdsproj file
    $projectFile = Get-ChildItem -Path $modulePath -Filter "*.cdsproj" | Select-Object -First 1
    if (-not $projectFile) {
        throw "No .cdsproj file found in module directory"
    }
    
    $solutionName = $projectFile.BaseName
    
    # Find artifact folder
    $artifactFolder = Join-Path $modulePath "bin\Debug"
    if (-not (Test-Path $artifactFolder)) {
        throw "Build artifacts not found at: $artifactFolder"
    }
    
    # Copy solution artifacts
    Write-Host ""
    Write-Host "Copying solution artifacts..." -ForegroundColor Yellow
    
    $artifacts = Get-ChildItem -Path $artifactFolder -Filter "*.zip"
    
    foreach ($artifact in $artifacts) {
        $sourceFile = $artifact.FullName
        $newFileName = Get-NewFileName $artifact.Name $version $solutionName
        $destinationPath = Join-Path $versionFolder $newFileName
        
        # Retry logic for file copy in case of file locking issues
        $maxRetries = 5
        $retryCount = 0
        $copySuccessful = $false
        
        while (-not $copySuccessful -and $retryCount -lt $maxRetries) {
            if (Test-FileInUse $sourceFile) {
                Write-Host "Source file $($artifact.Name) is currently in use (attempt $($retryCount + 1) of $maxRetries)..." -ForegroundColor Yellow
                Start-Sleep -Seconds (3 + $retryCount * 2)
                $retryCount++
                continue
            }
            
            try {
                Copy-Item -Path $sourceFile -Destination $destinationPath
                $copySuccessful = $true
                Write-Host "✓ Copied: $newFileName" -ForegroundColor Green
            }
            catch {
                $retryCount++
                if ($retryCount -ge $maxRetries) {
                    Write-Host "✗ Failed to copy $($artifact.Name) after $maxRetries attempts" -ForegroundColor Red
                    throw
                }
                else {
                    Write-Host "Copy failed (attempt $retryCount of $maxRetries), retrying..." -ForegroundColor Yellow
                    Start-Sleep -Seconds (3 + $retryCount * 2)
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "=== Release Created Successfully ===" -ForegroundColor Green
    Write-Host "Location: $versionFolder" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Release artifacts:" -ForegroundColor Cyan
    Get-ChildItem -Path $versionFolder | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
