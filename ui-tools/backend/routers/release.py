"""
Release Router - API endpoints for release management.

This module contains endpoints for:
- Building solution packages
- Version management 
- Changelog operations (get, preview, extract)
- Release validation and execution
- Package checking
- Step-by-step release execution
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pathlib import Path
import sys
import subprocess
import json

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    BuildPackagesRequest,
    ReleaseValidationRequest,
    ReleaseExecutionRequest,
    StepExecutionRequest,
    ReleaseRequest
)

# Import helper functions from utils
from utils import stream_powershell_output, read_solution_version


router = APIRouter(prefix="/api/release", tags=["Release Management"])


@router.post("/build")
async def build_packages(request: BuildPackagesRequest):
    """Build solution packages with streaming output"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Build-Packages-UI.ps1"
    
    args = [
        str(script_path),
        "-ModulePath", request.module_path,
        "-ModuleName", request.module_name,
        "-Version", request.version
    ]
    
    # Add repo root if provided (for multi-repo support)
    if request.repoPath:
        args.extend(["-RepoRoot", request.repoPath])
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )

@router.post("/modules/release")
async def create_release(request: ReleaseRequest):
    """Create a release for a module"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Release-Module-UI.ps1"
    
    args = [
        str(script_path),
        "-Category", request.category,
        "-Module", request.module
    ]
    
    # Add repo root if provided (for multi-repo support)
    if request.repoPath:
        args.extend(["-RepoRoot", request.repoPath])
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )
# Release Manager Endpoints
# ============================================================================

@router.get("/get-version")
async def get_module_version(module_path: str, repo_path: str = None):
    """Get current version from a module's Solution.xml"""
    try:
        # Use provided repo_path or default to PROJECT_ROOT
        base_path = Path(repo_path) if repo_path else PROJECT_ROOT
        full_path = base_path / module_path
        version = read_solution_version(full_path)
        return {"success": True, "version": version}
    except Exception as e:
        print(f"Error getting version: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "version": "Unknown"}

@router.post("/validate")
async def validate_release(request: ReleaseValidationRequest):
    """Validate pre-flight checks for release"""
    errors = []
    warnings = []
    
    try:
        # Use provided repo_path or default to PROJECT_ROOT
        repo_root = Path(request.repoPath) if request.repoPath else PROJECT_ROOT
        
        # Check for uncommitted changes
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if git_status.returncode == 0 and git_status.stdout.strip():
            errors.append("Repository has uncommitted changes. Please commit or stash changes before creating a release.")
        
        # Check for CHANGELOG.md with Unreleased section
        changelog_path = repo_root / request.module_path / "CHANGELOG.md"
        if not changelog_path.exists():
            errors.append(f"CHANGELOG.md not found at {changelog_path}")
        else:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "## Unreleased" not in content:
                    errors.append("CHANGELOG.md does not contain an '## Unreleased' section")
                else:
                    # Check if Unreleased section has content
                    import re
                    unreleased_section = re.search(r'## Unreleased\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
                    if unreleased_section:
                        section_content = unreleased_section.group(1).strip()
                        if not section_content or len(section_content) < 10:
                            warnings.append("Unreleased section appears to be empty")
        
        return {
            "success": True,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    except Exception as e:
        print(f"Error validating release: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "valid": False,
            "errors": [f"Validation failed: {str(e)}"],
            "warnings": []
        }

@router.get("/get-changelog")
async def get_changelog(module_path: str, repo_path: str = None):
    """Get the full CHANGELOG.md content"""
    try:
        # Use provided repo_path or default to PROJECT_ROOT
        base_path = Path(repo_path) if repo_path else PROJECT_ROOT
        changelog_path = base_path / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found", "content": ""}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"success": True, "content": content}
    except Exception as e:
        print(f"Error reading changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "content": ""}

@router.post("/preview-changelog")
async def preview_changelog(request: dict):
    """Preview the changelog transformation (before/after)"""
    try:
        from datetime import datetime
        import re
        
        module_path = request.get("module_path")
        new_version = request.get("new_version")
        repo_path = request.get("repo_path")
        
        # Use provided repo_path or default to PROJECT_ROOT
        base_path = Path(repo_path) if repo_path else PROJECT_ROOT
        changelog_path = base_path / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found"}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if there's an Unreleased section
        if '## Unreleased' not in original_content:
            return {
                "success": False, 
                "error": "CHANGELOG.md does not contain an '## Unreleased' section. Please add one before creating a release."
            }
        
        # Transform the changelog
        current_date = datetime.now().strftime("%Y-%m-%d")
        transformed_content = re.sub(
            r'## Unreleased',
            f'## [{new_version}] - {current_date}',
            original_content,
            count=1
        )
        
        return {
            "success": True,
            "before": original_content,
            "after": transformed_content
        }
    except Exception as e:
        print(f"Error previewing changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

@router.get("/extract-changelog")
async def extract_changelog(module_path: str, version: str = None, repo_path: str = None):
    """Extract release notes from CHANGELOG.md - either Unreleased or specific version"""
    try:
        # Use provided repo_path or default to PROJECT_ROOT
        base_path = Path(repo_path) if repo_path else PROJECT_ROOT
        changelog_path = base_path / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found", "content": ""}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        if version:
            # Try versioned section first, fall back to Unreleased if not found
            # Extract from versioned section like ## [1.0.0.0] - 2026-02-26
            escaped_version = version.replace('.', r'\.')
            # Match the version header, then capture everything until the next ## header (not ###)
            version_section = re.search(rf'## \[{escaped_version}\][^\n]*\n+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if version_section:
                section_content = version_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "versioned"}
            
            # Fall back to Unreleased if version section not found
            unreleased_section = re.search(r'## Unreleased\s+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if unreleased_section:
                section_content = unreleased_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "unreleased"}
            else:
                return {"success": True, "content": "", "source": "none"}
        else:
            # Extract Unreleased section
            unreleased_section = re.search(r'## Unreleased\s+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if unreleased_section:
                section_content = unreleased_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "unreleased"}
            else:
                return {"success": True, "content": "", "source": "none"}
    except Exception as e:
        print(f"Error extracting changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "content": ""}

@router.get("/check-packages")
async def check_packages(module_path: str, repo_path: str = None):
    """Check for built solution packages in .releases folder and return their metadata"""
    try:
        from datetime import datetime
        import os
        
        # Use provided repo_path or default to PROJECT_ROOT
        base_path = Path(repo_path) if repo_path else PROJECT_ROOT
        
        # Extract module name from path (e.g., "shared/core" -> "core")
        module_name = Path(module_path).name
        
        # Check .releases/<module> folder instead of bin/Release
        releases_path = base_path / ".releases" / module_name
        
        if not releases_path.exists():
            return {"success": True, "packages": [], "message": "No .releases folder found yet"}
        
        # Find .zip files in the .releases/<module> folder
        packages = []
        for file_path in releases_path.glob("*.zip"):
            stat_info = file_path.stat()
            modified_dt = datetime.fromtimestamp(stat_info.st_mtime)
            created_dt = datetime.fromtimestamp(stat_info.st_ctime)
            
            # Format: "Thu Feb-26, 2026 2:30 PM"
            modified_formatted = modified_dt.strftime("%a %b-") + str(modified_dt.day) + modified_dt.strftime(", %Y %I:%M %p")
            created_formatted = created_dt.strftime("%a %b-") + str(created_dt.day) + created_dt.strftime(", %Y %I:%M %p")
            
            packages.append({
                "name": file_path.name,
                "size": stat_info.st_size,
                "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                "created": created_formatted,
                "modified": modified_formatted,
                "modified_timestamp": stat_info.st_mtime
            })
        
        # Sort by modification time (newest first)
        packages.sort(key=lambda x: x["modified_timestamp"], reverse=True)
        
        return {
            "success": True,
            "packages": packages,
            "count": len(packages),
            "folder": str(releases_path.relative_to(base_path))
        }
    except Exception as e:
        print(f"Error checking packages: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "packages": []}

@router.post("/execute")
async def execute_release(request: ReleaseExecutionRequest):
    """Execute the full release workflow"""
    try:
        from datetime import datetime
        
        # Use provided repo_path or default to PROJECT_ROOT
        repo_root = Path(request.repoPath) if request.repoPath else PROJECT_ROOT
        
        # Build the script path
        script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Full-Release-UI.ps1"
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Release script not found: {script_path}",
                "steps": []
            }
        
        # Build PowerShell command
        ps_command = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script_path),
            "-ModulePath", request.module_path,
            "-ModuleName", request.module_name,
            "-ReleaseType", request.release_type,
            "-NewVersion", request.new_version,
            "-ReleaseNotes", request.release_notes,
            "-EnabledSteps", ",".join(request.enabled_steps)
        ]
        
        # Add repo root if provided (for multi-repo support)
        if request.repoPath:
            ps_command.extend(["-RepoRoot", request.repoPath])
        
        # Add optional display name if provided
        if request.module_display_name:
            ps_command.extend(["-ModuleFriendlyName", request.module_display_name])
        
        print(f"Executing release command: {' '.join(ps_command)}", file=sys.stderr)
        
        # Execute the PowerShell script
        result = subprocess.run(
            ps_command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"PowerShell stdout: {result.stdout}", file=sys.stderr)
        print(f"PowerShell stderr: {result.stderr}", file=sys.stderr)
        print(f"PowerShell return code: {result.returncode}", file=sys.stderr)
        
        # Try to parse JSON output from the script
        try:
            output_data = json.loads(result.stdout)
            return output_data
        except json.JSONDecodeError:
            # If not JSON, return a structured error
            if result.returncode == 0:
                return {
                    "success": True,
                    "steps": [{
                        "label": "Release execution",
                        "status": "success",
                        "message": result.stdout
                    }],
                    "github_release_url": ""
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout or "Unknown error",
                    "steps": [{
                        "label": "Release execution",
                        "status": "error",
                        "message": result.stderr or "Failed to execute release"
                    }]
                }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Release execution timed out after 5 minutes",
            "steps": []
        }
    except Exception as e:
        print(f"Error executing release: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "steps": []
        }

@router.post("/execute-step")
async def execute_single_step(request: StepExecutionRequest):
    """Execute a single release step with streaming output"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Full-Release-UI.ps1"
    
    # Build args list for stream_powershell_output
    args = [
        str(script_path),
        "-ModulePath", request.module_path,
        "-ModuleName", request.module_name,
        "-ReleaseType", "standard",  # Doesn't matter for single steps
        "-NewVersion", request.version,
        "-ReleaseNotes", request.release_notes,
        "-EnabledSteps", request.step  # Only this step
    ]
    
    # Add repo root if provided (for multi-repo support)
    if request.repoPath:
        args.extend(["-RepoRoot", request.repoPath])
    
    # Add optional display name if provided
    if request.module_display_name:
        args.extend(["-ModuleFriendlyName", request.module_display_name])
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )

