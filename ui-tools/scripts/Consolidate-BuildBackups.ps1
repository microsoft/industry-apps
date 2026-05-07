# Script to consolidate backup BUILD.md files to root .design folder

$rootPath = "c:\Users\jeremyho\repos\industry-apps"
$rootDesignFolder = Join-Path $rootPath ".design"

# Create root .design folder if it doesn't exist
if (-not (Test-Path $rootDesignFolder)) {
    New-Item -ItemType Directory -Path $rootDesignFolder -Force | Out-Null
    Write-Host "Created root .design folder" -ForegroundColor Green
}

$modules = @(
    "external-engagement\programs-and-services",
    "compliance-security\personnel-security",
    "shared\shift-scheduling",
    "administrative\executive-coordination",
    "operations\project-tracking",
    "administrative\member-organizations",
    "shared\process-automation",
    "external-engagement\external-interaction",
    "financial\financial-management",
    "workforce\training-and-certification",
    "government\court-case-management",
    "external-engagement\event-management",
    "workforce\time-travel-expenses",
    "operations\operational-excellence",
    "compliance-security\investigations",
    "operations\it-service-management",
    "workforce\hr-recruiting",
    "workforce\hr-benefits",
    "operations\asset-management",
    "workforce\gamification",
    "workforce\hr-administration",
    "operations\request-tracker"
)

foreach ($modulePath in $modules) {
    $moduleFullPath = Join-Path $rootPath $modulePath
    $moduleDesignFolder = Join-Path $moduleFullPath ".design"
    $folderName = Split-Path $modulePath -Leaf
    $buildFile = Join-Path $moduleDesignFolder "$folderName-build.md"
    
    if (Test-Path $buildFile) {
        # Move the build file to root .design folder
        $targetFile = Join-Path $rootDesignFolder "$folderName-build.md"
        Move-Item -Path $buildFile -Destination $targetFile -Force
        Write-Host "Moved $folderName-build.md to root .design folder" -ForegroundColor Cyan
        
        # Check if module .design folder is now empty
        $remainingFiles = Get-ChildItem -Path $moduleDesignFolder -File -Force
        if ($remainingFiles.Count -eq 0) {
            # Check for subdirectories
            $remainingDirs = Get-ChildItem -Path $moduleDesignFolder -Directory -Force
            if ($remainingDirs.Count -eq 0) {
                # Folder is empty, remove it
                Remove-Item -Path $moduleDesignFolder -Force
                Write-Host "  Removed empty .design folder from $folderName" -ForegroundColor Green
            } else {
                Write-Host "  Kept .design folder (contains subdirectories)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  Kept .design folder (contains other files)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Build file not found for $folderName" -ForegroundColor Gray
    }
}

Write-Host "`nConsolidation complete!" -ForegroundColor Green
Write-Host "All backup BUILD.md files are now in: $rootDesignFolder" -ForegroundColor Cyan
