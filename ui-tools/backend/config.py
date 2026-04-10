"""
Configuration constants and paths for Industry Apps Backend.

This module contains all project-wide configuration values, paths, and constants.
"""

from pathlib import Path


# ============================================================================
# Project Paths
# ============================================================================

# Get project root (go up from backend to repo root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Cache directory for pending option sets
CACHE_DIR = Path(__file__).parent / ".cache"
PENDING_CACHE_FILE = CACHE_DIR / "pending_optionsets.json"


# ============================================================================
# CORS Settings
# ============================================================================

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173"
]


# ============================================================================
# Configuration File Paths
# ============================================================================

def get_deployments_config_path():
    """Get path to deployments.json configuration file"""
    return PROJECT_ROOT / ".config" / "deployments.json"


def get_scripts_path():
    """Get path to scripts directory"""
    return PROJECT_ROOT / "ui-tools" / "scripts"


# ============================================================================
# Excluded Folders (for scanning)
# ============================================================================

EXCLUDE_FOLDERS = {
    "__pycache__",
    ".scripts",
    ".config",
    ".git",
    ".vscode",
    "bin",
    "obj",
    "ui-tools"
}
