# Full-Release-UI.ps1
# Orchestrates the complete release workflow for a module
# Called by the Release Manager UI

param(
    [Parameter(Mandatory=$true)]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$true)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$false)]
    [string]$ModuleFriendlyName = "",
    
    [Parameter(Mandatory=$true)]
    [ValidateSet('standard', 'hotfix')]
    [string]$ReleaseType,
    
    [Parameter(Mandatory=$true)]
    [string]$NewVersion,
    
    [Parameter(Mandatory=$true)]
    [string]$ReleaseNotes,
    
    [Parameter(Mandatory=$true)]
    [string]$EnabledSteps  # Comma-separated list
)

$ErrorActionPreference = "Stop"

# Get project root
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# Source utility functions
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

# Parse enabled steps
$steps = $EnabledSteps -split ','

# Initialize results
$results = @{
    success = $true
    steps = @()
    github_release_url = ""
}

function Add-StepResult {
    param(
        [string]$Label,
        [string]$Status,
        [string]$Message = ""
    )
    
    $results.steps += @{
        label = $Label
        status = $Status
        message = $Message
    }
}

try {
    Write-Host "=== Full Release: $ModuleName v$NewVersion ===" -ForegroundColor Cyan
    Write-Host "Release Type: $ReleaseType" -ForegroundColor Gray
    Write-Host "Enabled Steps: $EnabledSteps" -ForegroundColor Gray
    Write-Host ""
    
    $fullModulePath = Join-Path $projectRoot $ModulePath
    
    if (-not (Test-Path $fullModulePath)) {
        throw "Module path not found: $fullModulePath"
    }
    
    # Step 1: Update Version in Dataverse and Sync
    if ($steps -contains 'updateVersion') {
        Write-Host "Step 1: Updating version in Dataverse and syncing to local..." -ForegroundColor Yellow
        Add-StepResult -Label "Update version and sync" -Status "running"
        
        try {
            # Get solution unique name from Solution.xml
            $solutionXmlPath = Join-Path $fullModulePath "src\Other\Solution.xml"
            [xml]$solutionXml = Get-Content $solutionXmlPath
            $solutionUniqueName = $solutionXml.ImportExportXml.SolutionManifest.UniqueName
            
            if ([string]::IsNullOrEmpty($solutionUniqueName)) {
                throw "Could not find UniqueName in Solution.xml"
            }
            
            Write-Host "Solution: $solutionUniqueName" -ForegroundColor Gray
            
            # Update version online using pac solution online-version
            Set-Location $fullModulePath
            $pacOutput = pac solution online-version --solution-name $solutionUniqueName --solution-version $NewVersion 2>&1 | Out-String
            Write-Host $pacOutput
            
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to update version online: $pacOutput"
            }
            
            # Sync solution back to local
            $syncOutput = pac solution sync 2>&1 | Out-String
            Write-Host $syncOutput
            
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to sync solution: $syncOutput"
            }
            
            # Verify the version was updated locally
            $actualVersion = Read-SolutionVersion -xmlFilePath $solutionXmlPath
            if ($actualVersion -ne $NewVersion) {
                throw "Version verification failed. Expected: $NewVersion, Got: $actualVersion"
            }
            
            Write-Host "[OK] Version updated and synced" -ForegroundColor Green
            Add-StepResult -Label "Update version and sync" -Status "success" -Message "Updated to v$NewVersion"
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Update version and sync" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    # Step 2: Update CHANGELOG.md
    if ($steps -contains 'updateChangelog') {
        Write-Host "Step 2: Updating CHANGELOG.md..." -ForegroundColor Yellow
        Add-StepResult -Label "Update CHANGELOG.md" -Status "running"
        
        try {
            $changelogPath = Join-Path $fullModulePath "CHANGELOG.md"
            
            if (-not (Test-Path $changelogPath)) {
                throw "CHANGELOG.md not found at $changelogPath"
            }
            
            $changelogContent = Get-Content $changelogPath -Raw
            
            # Get current date
            $currentDate = Get-Date -Format "yyyy-MM-dd"
            
            # Replace ## Unreleased with new Unreleased section followed by versioned section
            $versionedSection = "## [$NewVersion] - $currentDate"
            $newChangelog = $changelogContent -replace '## Unreleased', "## Unreleased`n`n$versionedSection"
            
            # Write updated changelog
            Set-Content -Path $changelogPath -Value $newChangelog -NoNewline
            
            Write-Host "[OK] CHANGELOG.md updated" -ForegroundColor Green
            Add-StepResult -Label "Update CHANGELOG.md" -Status "success" -Message "Added version $NewVersion section"
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Update CHANGELOG.md" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    # Step 3: Create Release Notes (UI-only step - no action needed)
    # Release notes are already prepared and edited in the UI
    # This step just exists as a checkpoint in the UI workflow
    
    # Step 4: Build Solution Packages
    if ($steps -contains 'buildPackages') {
        Write-Host "Step 4: Building solution packages..." -ForegroundColor Yellow
        Add-StepResult -Label "Build solution packages" -Status "running"
        
        try {
            # Get the project name from .cdsproj file
            $projectFile = Get-ChildItem -Path $fullModulePath -Filter "*.cdsproj" | Select-Object -First 1
            if (-not $projectFile) {
                throw "No .cdsproj file found in module directory"
            }
            
            $projectName = $projectFile.BaseName
            
            # Get friendly name for package naming
            $friendlyName = Get-SolutionFriendlyName -SolutionPath $fullModulePath
            if (-not $friendlyName) {
                # Fallback to ModuleName if we can't get friendly name
                $friendlyName = $ModuleName
            }
            
            # Clean up old package files from .releases folder
            $releasesFolder = Join-Path $projectRoot ".releases"
            $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
            
            if (Test-Path $moduleReleasesFolder) {
                Write-Host "Cleaning up old package files..." -ForegroundColor Yellow
                Get-ChildItem -Path $moduleReleasesFolder -Filter "*.zip" | Where-Object {
                    $_.Name -match "^App-Base-.*-v$([regex]::Escape($NewVersion))\.zip$"
                } | ForEach-Object {
                    Write-Host "  Removing: $($_.Name)" -ForegroundColor Gray
                    Remove-Item $_.FullName -Force
                }
            }
            
            # Build the solution using the shared Build-Solution function
            Write-Host ""
            Build-Solution -SolutionPath $fullModulePath -Configuration Release
            Write-Host ""
            
            # Check if build artifacts were created
            $artifactFolder = Join-Path $fullModulePath "bin\Release"
            $unmanagedZip = Join-Path $artifactFolder "$projectName.zip"
            $managedZip = Join-Path $artifactFolder "${projectName}_managed.zip"
            
            if (-not (Test-Path $unmanagedZip) -and -not (Test-Path $managedZip)) {
                throw "Failed to build solution: No package files were generated"
            }
            
            # Rename packages to standard format
            # Format: App-Base-{ModuleName}-v{version}.zip
            #         App-Base-{ModuleName}-Managed-v{version}.zip
            
            if (Test-Path $unmanagedZip) {
                $newUnmanagedName = "App-Base-$friendlyName-v$NewVersion.zip"
                $newUnmanagedPath = Join-Path $artifactFolder $newUnmanagedName
                
                # Remove old file if it exists
                if (Test-Path $newUnmanagedPath) {
                    Remove-Item $newUnmanagedPath -Force
                }
                
                Rename-Item $unmanagedZip $newUnmanagedName
                Write-Host "Created: $newUnmanagedName" -ForegroundColor Gray
                
                # Copy to .releases folder
                $releasesFolder = Join-Path $projectRoot ".releases"
                $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
                
                if (-not (Test-Path $moduleReleasesFolder)) {
                    New-Item -Path $moduleReleasesFolder -ItemType Directory -Force | Out-Null
                }
                
                $destUnmanaged = Join-Path $moduleReleasesFolder $newUnmanagedName
                Copy-Item $newUnmanagedPath $destUnmanaged -Force
                Write-Host "Copied to: .releases\$ModuleName\$newUnmanagedName" -ForegroundColor Gray
            }
            
            if (Test-Path $managedZip) {
                $newManagedName = "App-Base-$friendlyName-Managed-v$NewVersion.zip"
                $newManagedPath = Join-Path $artifactFolder $newManagedName
                
                # Remove old file if it exists
                if (Test-Path $newManagedPath) {
                    Remove-Item $newManagedPath -Force
                }
                
                Rename-Item $managedZip $newManagedName
                Write-Host "Created: $newManagedName" -ForegroundColor Gray
                
                # Copy to .releases folder
                $releasesFolder = Join-Path $projectRoot ".releases"
                $moduleReleasesFolder = Join-Path $releasesFolder $ModuleName
                
                if (-not (Test-Path $moduleReleasesFolder)) {
                    New-Item -Path $moduleReleasesFolder -ItemType Directory -Force | Out-Null
                }
                
                $destManaged = Join-Path $moduleReleasesFolder $newManagedName
                Copy-Item $newManagedPath $destManaged -Force
                Write-Host "Copied to: .releases\$ModuleName\$newManagedName" -ForegroundColor Gray
            }
            
            Write-Host "[OK] Solution packages built and copied" -ForegroundColor Green
            Add-StepResult -Label "Build solution packages" -Status "success" -Message "Created managed and unmanaged packages"
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Build solution packages" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    # Step 5: Git Commit
    if ($steps -contains 'gitCommit') {
        Write-Host "Step 5: Committing changes to git..." -ForegroundColor Yellow
        Add-StepResult -Label "Git commit" -Status "running"
        
        try {
            Set-Location $projectRoot
            
            # Stage all module files except .zip packages
            # Suppress line ending warnings (LF/CRLF) as they're informational only
            $prevErrorAction = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            $gitAddOutput = git add "$ModulePath/" -- ':!*.zip' 2>&1 | Out-String
            $ErrorActionPreference = $prevErrorAction
            
            # Only show output if it's not just line ending warnings
            if ($gitAddOutput -and $gitAddOutput -notmatch "LF will be replaced by CRLF") {
                Write-Host $gitAddOutput -ForegroundColor Gray
            }
            Write-Host "git add $ModulePath/ (excluding .zip files)" -ForegroundColor Gray
            
            # Get friendly name for commit message (with spaces, not hyphens)
            $commitModuleName = $ModuleFriendlyName
            if (-not $commitModuleName) {
                # Try to extract from Solution.xml
                $solutionXmlPath = Join-Path $fullModulePath "src\Other\Solution.xml"
                if (Test-Path $solutionXmlPath) {
                    try {
                        [xml]$solutionXml = Get-Content $solutionXmlPath
                        $localizedName = $solutionXml.SelectSingleNode("//LocalizedName[@languagecode='1033']")
                        if ($localizedName -and $localizedName.description) {
                            $commitModuleName = $localizedName.description.Trim()
                            # Remove "App Base - " prefix if present
                            if ($commitModuleName.StartsWith("App Base - ")) {
                                $commitModuleName = $commitModuleName.Substring(11)
                            }
                        }
                    } catch {
                        # Fallback to ModuleName if extraction fails
                        $commitModuleName = $ModuleName
                    }
                } else {
                    $commitModuleName = $ModuleName
                }
            }
            
            # Commit
            $commitMessage = "Release $commitModuleName v$NewVersion"
            $prevErrorAction = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            $gitCommit = git commit -m $commitMessage 2>&1 | Out-String
            $commitExitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevErrorAction
            
            # Filter out line ending warnings from output
            $filteredOutput = ($gitCommit -split "`n" | Where-Object { 
                $_ -and $_ -notmatch "LF will be replaced by CRLF" 
            }) -join "`n"
            if ($filteredOutput) {
                Write-Host $filteredOutput
            }
            
            if ($commitExitCode -ne 0) {
                # Check if there were no changes to commit
                if ($gitCommit -match "nothing to commit") {
                    Write-Host "[OK] No changes to commit" -ForegroundColor Yellow
                    Add-StepResult -Label "Git commit" -Status "success" -Message "No changes to commit"
                } else {
                    throw "Git commit failed (exit code: $commitExitCode): $gitCommit"
                }
            } else {
                Write-Host "[OK] Changes committed" -ForegroundColor Green
                
                # Push the commit to remote
                Write-Host "Pushing to remote..." -ForegroundColor Yellow
                
                # Temporarily disable strict error mode for git (stderr doesn't mean failure)
                $prevErrorAction = $ErrorActionPreference
                $ErrorActionPreference = 'SilentlyContinue'
                $gitPush = git push 2>&1 | Out-String
                $pushExitCode = $LASTEXITCODE
                $ErrorActionPreference = $prevErrorAction
                
                # Filter out line ending warnings and benign remote messages
                $filteredPushOutput = ($gitPush -split "`n" | Where-Object { 
                    $_ -and 
                    $_ -notmatch "LF will be replaced by CRLF" -and
                    $_.Trim() -ne "remote:" -and
                    $_.Trim() -ne ""
                }) -join "`n"
                if ($filteredPushOutput) {
                    Write-Host $filteredPushOutput
                }
                
                if ($pushExitCode -ne 0) {
                    throw "Git push failed (exit code: $pushExitCode): $gitPush"
                }
                
                Write-Host "[OK] Changes pushed to remote" -ForegroundColor Green
                Add-StepResult -Label "Git commit" -Status "success" -Message "$commitMessage (pushed)"
            }
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Git commit" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    # Step 6: Create Git Tag
    if ($steps -contains 'gitTag') {
        Write-Host "Step 6: Creating git tag..." -ForegroundColor Yellow
        Add-StepResult -Label "Create git tag" -Status "running"
        
        try {
            Set-Location $projectRoot
            
            $tagName = "$ModuleName/v$NewVersion"
            $prevErrorAction = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            $gitTag = git tag $tagName 2>&1 | Out-String
            $tagExitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevErrorAction
            
            if ($tagExitCode -ne 0) {
                throw "Failed to create tag (exit code: $tagExitCode): $gitTag"
            }
            
            Write-Host "[OK] Tag created: $tagName" -ForegroundColor Green
            
            # Push the tag to remote
            Write-Host "Pushing tag to remote..." -ForegroundColor Yellow
            $prevErrorAction = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            $gitPushTag = git push origin $tagName 2>&1 | Out-String
            $pushTagExitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevErrorAction
            
            # Filter out line ending warnings and benign remote messages
            $filteredTagOutput = ($gitPushTag -split "`n" | Where-Object { 
                $_ -and 
                $_ -notmatch "LF will be replaced by CRLF" -and
                $_.Trim() -ne "remote:" -and
                $_.Trim() -ne ""
            }) -join "`n"
            if ($filteredTagOutput) {
                Write-Host $filteredTagOutput
            }
            
            if ($pushTagExitCode -ne 0) {
                throw "Failed to push tag (exit code: $pushTagExitCode): $gitPushTag"
            }
            
            Write-Host "[OK] Tag pushed to remote" -ForegroundColor Green
            Add-StepResult -Label "Create git tag" -Status "success" -Message "Tag: $tagName (pushed)"
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Create git tag" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    # Step 7: Create GitHub Release
    if ($steps -contains 'githubRelease') {
        Write-Host "Step 7: Creating GitHub release..." -ForegroundColor Yellow
        Add-StepResult -Label "Create GitHub release" -Status "running"
        
        try {
            Set-Location $projectRoot
            
            # Check if gh CLI is available
            try {
                gh --version 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    throw "GitHub CLI (gh) is not installed or not in PATH. Please install from https://cli.github.com/"
                }
            } catch {
                throw "GitHub CLI (gh) is not installed or not in PATH. Please install from https://cli.github.com/"
            }
            
            $tagName = "$ModuleName/v$NewVersion"
            
            # Use friendly name for release title if provided, otherwise capitalize module name
            if ($ModuleFriendlyName) {
                $releaseTitle = "$ModuleFriendlyName $NewVersion"
            } else {
                $ModuleNameCapitalized = $ModuleName.Substring(0,1).ToUpper() + $ModuleName.Substring(1)
                $releaseTitle = "$ModuleNameCapitalized $NewVersion"
            }
            
            # Save release notes to temp file
            $tempNotesFile = Join-Path $env:TEMP "release-notes-$ModuleName-$NewVersion.md"
            Set-Content -Path $tempNotesFile -Value $ReleaseNotes -Encoding UTF8
            
            # Get package files
            $moduleReleasesFolder = Join-Path $projectRoot ".releases\$ModuleName"
            
            # Get friendly name for package file names
            $friendlyName = Get-SolutionFriendlyName -SolutionPath $fullModulePath
            if (-not $friendlyName) {
                $friendlyName = $ModuleName
            }
            
            $unmanagedPackage = Join-Path $moduleReleasesFolder "App-Base-$friendlyName-v$NewVersion.zip"
            $managedPackage = Join-Path $moduleReleasesFolder "App-Base-$friendlyName-Managed-v$NewVersion.zip"
            
            # Build gh release create command
            $ghCommand = @(
                "gh", "release", "create", $tagName,
                "--title", $releaseTitle,
                "--notes-file", $tempNotesFile
            )
            
            # Add package files if they exist
            if (Test-Path $unmanagedPackage) {
                $ghCommand += $unmanagedPackage
            }
            if (Test-Path $managedPackage) {
                $ghCommand += $managedPackage
            }
            
            # Push tags first (if not already pushed)
            Write-Host "Pushing tags to GitHub..." -ForegroundColor Gray
            $prevErrorAction = $ErrorActionPreference
            $ErrorActionPreference = 'SilentlyContinue'
            $gitPush = git push origin --tags 2>&1 | Out-String
            $pushTagsExitCode = $LASTEXITCODE
            $ErrorActionPreference = $prevErrorAction
            
            # Filter out line ending warnings and benign remote messages
            $filteredPushTagsOutput = ($gitPush -split "`n" | Where-Object { 
                $_ -and 
                $_ -notmatch "LF will be replaced by CRLF" -and
                $_.Trim() -ne "remote:" -and
                $_.Trim() -ne ""
            }) -join "`n"
            if ($filteredPushTagsOutput) {
                Write-Host $filteredPushTagsOutput
            }
            
            # Check exit code only if command completed (up-to-date is success)
            if ($pushTagsExitCode -ne 0 -and $gitPush -notmatch "Everything up-to-date") {
                throw "Failed to push tags (exit code: $pushTagsExitCode): $gitPush"
            }
            
            # Create the release
            Write-Host "Creating GitHub release: $tagName" -ForegroundColor Gray
            $ghOutput = & $ghCommand[0] $ghCommand[1..($ghCommand.Length-1)] 2>&1 | Out-String
            Write-Host $ghOutput
            
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create GitHub release: $ghOutput"
            }
            
            # Extract release URL from output (gh outputs the URL)
            $releaseUrl = $ghOutput.Trim()
            $results.github_release_url = $releaseUrl
            
            # Clean up temp file
            Remove-Item $tempNotesFile -ErrorAction SilentlyContinue
            
            Write-Host "[OK] GitHub release created: $releaseUrl" -ForegroundColor Green
            Add-StepResult -Label "Create GitHub release" -Status "success" -Message "Release URL: $releaseUrl"
        } catch {
            Write-Host "[FAILED] $($_.Exception.Message)" -ForegroundColor Red
            Add-StepResult -Label "Create GitHub release" -Status "error" -Message $_.Exception.Message
            throw
        }
        Write-Host ""
    }
    
    Write-Host "=== Release Complete ===" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "=== Release Failed ===" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    $results.success = $false
    $results.error = $_.Exception.Message
}

# Output JSON result for the backend to parse
$jsonOutput = $results | ConvertTo-Json -Depth 10 -Compress
Write-Output $jsonOutput
