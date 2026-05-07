# Script to add descriptions to BUILD.md files from backups

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
    $designFolder = Join-Path $modulePath ".design"
    $folderName = Split-Path $module.Path -Leaf
    $backupFile = Join-Path $designFolder "$folderName-build.md"
    $buildFile = Join-Path $modulePath "BUILD.md"
    
    Write-Host "Processing $($module.Name)..." -ForegroundColor Cyan
    
    if (Test-Path $backupFile) {
        $backupContent = Get-Content -Path $backupFile -Raw
        
        # Try multiple patterns to extract description
        $description = ""
        
        # Pattern 1: After header, before "---"
        if ($backupContent -match '(?s)^#[^\n]*\n\n(The \*\*[^\n]*\*\*.*?)\n\n---') {
            $description = $matches[1].Trim()
        }
        # Pattern 2: Just the paragraph after header
        elseif ($backupContent -match '(?s)^#[^\n]*\n\n(The \*\*.*?)\n\n') {
            $description = $matches[1].Trim()
        }
        # Pattern 3: For simpler headers without "The **"
        elseif ($backupContent -match '(?s)^#[^\n]*\n\n([^\n#]+.*?)\n\n') {
            $text = $matches[1].Trim()
            # Only use if it looks like a description (not a section header or bullet list)
            if ($text -notmatch '^##' -and $text -notmatch '^\s*-' -and $text.Length -gt 50) {
                $description = $text
            }
        }
        
        if ($description) {
            $newContent = "# $($module.Emoji) $($module.Name)`n`n$description`n`n# Completed`n`n# Planned`n"
            Set-Content -Path $buildFile -Value $newContent -NoNewline
            Write-Host "  Updated with description" -ForegroundColor Green
        } else {
            Write-Host "  No description found - kept as is" -ForegroundColor Yellow
        }
    }
}

Write-Host "`nAll modules processed!" -ForegroundColor Green
