import os
import re

# Define the project root
project_root = r"c:\Users\jeremyho\repos\industry-apps"

# Mapping of module folders to their display names
modules = {
    "administrative/executive-coordination": "Executive Coordination",
    "administrative/member-organizations": "Member Organizations",
    "compliance-security/investigations": "Investigations",
    "compliance-security/personnel-security": "Personnel Security",
    "external-engagement/event-management": "Event Management",
    "external-engagement/programs-and-services": "Programs and Services",
    "financial/financial-management": "Financial Management",
    "government/court-case-management": "Court Case Management",
    "operations/asset-management": "Asset Management",
    "operations/it-service-management": "IT Service Management",
    "operations/operational-excellence": "Operational Excellence",
    "operations/project-tracking": "Project Tracking",
    "operations/request-tracker": "Request Tracker",
    "workforce/dispute-resolution": "Dispute Resolution",
    "workforce/gamification": "Gamification",
    "workforce/hr-administration": "HR Administration",
    "workforce/hr-benefits": "HR Benefits",
    "workforce/hr-recruiting": "HR Recruiting",
    "workforce/time-travel-expenses": "Time, Travel, and Expenses",
    "workforce/training-and-certification": "Training and Certification",
}

def create_changelog(module_folder, module_name):
    """Create a CHANGELOG.md file for a module"""
    target_path = os.path.join(project_root, module_folder, "CHANGELOG.md")
    
    content = f"""# {module_name} Changelog

## Unreleased

### Added
- 

### Changed
- 
"""
    
    # Write the CHANGELOG.md file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created: {target_path}")

# Process all modules
for module_folder, module_name in modules.items():
    try:
        create_changelog(module_folder, module_name)
    except Exception as e:
        print(f"✗ Error creating CHANGELOG for {module_folder}: {e}")

print(f"\n✅ All {len(modules)} CHANGELOG.md files created successfully!")
