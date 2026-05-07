# Script to backup BUILD.md files and create new simplified versions

$modules = @(
    @{Path="external-engagement\programs-and-services"; Name="Programs and Services"; Emoji="🎁"},
    @{Path="compliance-security\personnel-security"; Name="Personnel Security"; Emoji="🔐"},
    @{Path="shared\shift-scheduling"; Name="Shift Scheduling"; Emoji="🔧"},
    @{Path="administrative\executive-coordination"; Name="Executive Coordination"; Emoji="🎯"},
    @{Path="operations\project-tracking"; Name="Project Tracking"; Emoji="📋"},
    @{Path="administrative\member-organizations"; Name="Member Organizations"; Emoji="👥"},
    @{Path="shared\process-automation"; Name="Process Automation"; Emoji="⚙️"},
    @{Path="external-engagement\external-interaction"; Name="External Interaction"; Emoji="💬"},
    @{Path="financial\financial-management"; Name="Financial Management"; Emoji="💰"},
    @{Path="workforce\training-and-certification"; Name="Training and Certification"; Emoji="🎓"},
    @{Path="government\court-case-management"; Name="Court Case Management"; Emoji="⚖️"},
    @{Path="external-engagement\event-management"; Name="Event Management"; Emoji="🎊"},
    @{Path="workforce\time-travel-expenses"; Name="Time, Travel, and Expenses"; Emoji="⏱️"},
    @{Path="operations\operational-excellence"; Name="Operational Excellence"; Emoji="🎯"},
    @{Path="compliance-security\investigations"; Name="Investigations"; Emoji="🔍"},
    @{Path="operations\it-service-management"; Name="IT Service Management"; Emoji="💻"},
    @{Path="workforce\hr-recruiting"; Name="HR Recruiting"; Emoji="🎯"},
    @{Path="workforce\hr-benefits"; Name="HR Benefits"; Emoji="💼"},
    @{Path="operations\asset-management"; Name="Asset Management"; Emoji="🏗️"},
    @{Path="workforce\gamification"; Name="Gamification"; Emoji="🎮"},
    @{Path="workforce\hr-administration"; Name="HR Administration"; Emoji="👥"}
)

$rootPath = "c:\Users\jeremyho\repos\industry-apps"

foreach ($module in $modules) {
    $modulePath = Join-Path $rootPath $module.Path
    $buildFile = Join-Path $modulePath "BUILD.md"
    $designFolder = Join-Path $modulePath ".design"
    $folderName = Split-Path $module.Path -Leaf
    $backupFile = Join-Path $designFolder "$folderName-build.md"
    
    Write-Host "Processing $($module.Name)..." -ForegroundColor Cyan
    
    # Create .design folder if it doesn't exist
    if (-not (Test-Path $designFolder)) {
        New-Item -ItemType Directory -Path $designFolder -Force | Out-Null
        Write-Host "  Created .design folder" -ForegroundColor Green
    }
    
    # Copy BUILD.md to backup
    if (Test-Path $buildFile) {
        Copy-Item -Path $buildFile -Destination $backupFile -Force
        Write-Host "  Backed up to $folderName-build.md" -ForegroundColor Green
        
        # Extract description from original file
        $content = Get-Content -Path $buildFile -Raw
        
        # Try to extract description (text between header and first "---" or "##")
        if ($content -match '(?s)^#[^#\n]*\n\n(The \*\*.*?\*\*.*?)(?:\n\n---|\n\n##)') {
            $description = $matches[1]
        } elseif ($content -match '(?s)^#[^#\n]*\n\n([^\n]+.*?)(?:\n\n---|\n\n##)') {
            $description = $matches[1]
        } else {
            $description = ""
        }
        
        # Create new simplified BUILD.md content
        $newContent = "# $($module.Emoji) $($module.Name)`n`n"
        if ($description) {
            $newContent += "$description`n`n"
        }
        $newContent += "# Completed`n`n# Planned`n"
        
        # Write new BUILD.md
        Set-Content -Path $buildFile -Value $newContent -NoNewline
        Write-Host "  Created new simplified BUILD.md" -ForegroundColor Green
    } else {
        Write-Host "  BUILD.md not found!" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "All modules processed successfully!" -ForegroundColor Green
