import os
import re

# Define the project root
project_root = r"c:\Users\jeremyho\repos\industry-apps"
design_folder = os.path.join(project_root, ".design")

# Mapping of design files to their target folders
file_mappings = {
    "financial-management.md": "financial/financial-management",
    "hr-benefits.md": "workforce/hr-benefits",
    "hr-recruiting.md": "workforce/hr-recruiting",
    "investigations.md": "compliance-security/investigations",
    "it-service-management.md": "operations/it-service-management",
    "member-organizations.md": "administrative/member-organizations",
    "operational-excellence.md": "operations/operational-excellence",
    "personnel-security.md": "compliance-security/personnel-security",
    "programs-and-services.md": "external-engagement/programs-and-services",
    "time-travel-expenses.md": "workforce/time-travel-expenses",
    "training-and-certification.md": "workforce/training-and-certification",
}

def transform_content(content):
    """Transform the content by replacing **Fields:** with tracking sections"""
    # Pattern to match **Fields:** sections
    pattern = r'(\*\*Fields:\*\*)'
    
    # Replacement: add Completed section, then change Fields to Planned
    replacement = r'**Completed:**\n\n**Planned:**'
    
    transformed = re.sub(pattern, replacement, content)
    return transformed

def process_file(design_file, target_folder):
    """Process a single design file and create BUILD.md"""
    design_path = os.path.join(design_folder, design_file)
    target_path = os.path.join(project_root, target_folder, "BUILD.md")
    
    # Read the design file
    with open(design_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Transform the content
    transformed_content = transform_content(content)
    
    # Ensure target directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # Write the BUILD.md file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(transformed_content)
    
    print(f"✓ Created: {target_path}")

# Process all files
for design_file, target_folder in file_mappings.items():
    try:
        process_file(design_file, target_folder)
    except Exception as e:
        print(f"✗ Error processing {design_file}: {e}")

print("\nAll BUILD.md files created successfully!")
