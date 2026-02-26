param(
    [Parameter(Mandatory=$true)]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$true)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

# Get project root and source utility functions
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. "$projectRoot\.scripts\Util.ps1"

function Get-SolutionFriendlyName {
    param([string]$SolutionPath)
    
    $solutionXmlPath = Join-Path $SolutionPath "src\Other\Solution.xml"
    
    if (-not (Test-Path $solutionXmlPath)) {
        return $null
    }
    
    try {
        [xml]$solutionXml = Get-Content $solutionXmlPath
        $localizedName = $solutionXml.SelectSingleNode("//LocalizedName[@languagecode='1033']")
        
        if ($localizedName -and $localizedName.description) {
            $displayName = $localizedName.description.Trim()
            
            # Remove "App Base - " prefix if present
            if ($displayName.StartsWith("App Base - ")) {
                $displayName = $displayName.Substring(11)
            }
            
            # Convert spaces to hyphens while preserving capitalization
            $displayName = $displayName -replace ' ', '-'
            
            return $displayName
        }
    } catch {
        Write-Host "Warning: Could not read friendly name from Solution.xml" -ForegroundColor Yellow
    }
    
    return $null
}

try {
    # Convert relative path to absolute path
    $fullModulePath = (Resolve-Path $ModulePath).Path
    
    Write-Host "Building solution packages for $ModuleName v$Version..." -ForegroundColor Cyan
    Write-Host "Module Path: $fullModulePath" -ForegroundColor Gray
    Write-Host ""
    
    # Get the project name from .cdsproj file
    $projectFile = Get-ChildItem -Path $fullModulePath -Filter "*.cdsproj" | Select-Object -First 1
    if (-not $projectFile) {
        throw "No .cdsproj file found in module directory"
    }
    
    $projectName = $projectFile.BaseName
    Write-Host "Project: $projectName" -ForegroundColor Gray
    
    # Get friendly name for package naming
    $friendlyName = Get-SolutionFriendlyName -SolutionPath $fullModulePath
    if (-not $friendlyName) {
        # Fallback to ModuleName if we can't get friendly name
        $friendlyName = $ModuleName
        Write-Host "Using module name for package: $friendlyName" -ForegroundColor Yellow
    } else {
        Write-Host "Using friendly name for package: $friendlyName" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Clean up old package files from .releases folder
    $releasesFolder = Join-Path $projectRoot ".releases"
    $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
    
    if (Test-Path $moduleReleasesFolder) {
        Write-Host "Cleaning up old package files..." -ForegroundColor Yellow
        Get-ChildItem -Path $moduleReleasesFolder -Filter "*.zip" | Where-Object {
            $_.Name -match "^App-Base-.*-v$([regex]::Escape($Version))\.zip$"
        } | ForEach-Object {
            Write-Host "  Removing: $($_.Name)" -ForegroundColor Gray
            Remove-Item $_.FullName -Force
        }
    }
    
    # Build the solution using the shared Build-Solution function
    Write-Host "Building solution..." -ForegroundColor Yellow
    Write-Host ""
    Build-Solution -SolutionPath $fullModulePath -Configuration Release
    Write-Host ""
    
    # Check if build artifacts were created
    $artifactFolder = Join-Path $fullModulePath "bin\Release"
    $unmanagedZip = Join-Path $artifactFolder "$projectName.zip"
    $managedZip = Join-Path $artifactFolder "${projectName}_managed.zip"
    
    Write-Host "Checking build artifacts in: $artifactFolder" -ForegroundColor Gray
    
    if (-not (Test-Path $unmanagedZip) -and -not (Test-Path $managedZip)) {
        throw "Failed to build solution: No package files were generated in bin\Release"
    }
    
    Write-Host ""
    
    # Rename packages to standard format
    # Format: App-Base-{ModuleName}-v{version}.zip
    #         App-Base-{ModuleName}-Managed-v{version}.zip
    
    if (Test-Path $unmanagedZip) {
        $newUnmanagedName = "App-Base-$friendlyName-v$Version.zip"
        $newUnmanagedPath = Join-Path $artifactFolder $newUnmanagedName
        
        # Remove old file if it exists
        if (Test-Path $newUnmanagedPath) {
            Remove-Item $newUnmanagedPath -Force
        }
        
        Rename-Item $unmanagedZip $newUnmanagedName
        Write-Host "[OK] Created: $newUnmanagedName" -ForegroundColor Green
        
        # Copy to .releases folder
        $releasesFolder = Join-Path $projectRoot ".releases"
        $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
        
        if (-not (Test-Path $moduleReleasesFolder)) {
            New-Item -Path $moduleReleasesFolder -ItemType Directory -Force | Out-Null
        }
        
        $destUnmanaged = Join-Path $moduleReleasesFolder $newUnmanagedName
        Copy-Item $newUnmanagedPath $destUnmanaged -Force
        Write-Host "  Copied to: .releases\$ModuleName\$newUnmanagedName" -ForegroundColor Gray
    }
    
    if (Test-Path $managedZip) {
        $newManagedName = "App-Base-$friendlyName-Managed-v$Version.zip"
        $newManagedPath = Join-Path $artifactFolder $newManagedName
        
        # Remove old file if it exists
        if (Test-Path $newManagedPath) {
            Remove-Item $newManagedPath -Force
        }
        
        Rename-Item $managedZip $newManagedName
        Write-Host "[OK] Created: $newManagedName" -ForegroundColor Green
        
        # Copy to .releases folder
        $releasesFolder = Join-Path $projectRoot ".releases"
        $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
        
        if (-not (Test-Path $moduleReleasesFolder)) {
            New-Item -Path $moduleReleasesFolder -ItemType Directory -Force | Out-Null
        }
        
        $destManaged = Join-Path $moduleReleasesFolder $newManagedName
        Copy-Item $newManagedPath $destManaged -Force
        Write-Host "  Copied to: .releases\$ModuleName\$newManagedName" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "[OK] Solution packages built successfully" -ForegroundColor Green
    
    exit 0
} catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
