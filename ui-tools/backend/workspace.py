"""
Workspace management for multi-repo support.

This module handles discovery and management of multiple solution repositories.
Repos can be configured in .config/repos.json relative to the main repo.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class RepoInfo:
    """Information about a solution repository."""
    name: str
    path: Path
    enabled: bool
    type: str
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary with string paths."""
        return {
            "name": self.name,
            "path": str(self.path),
            "enabled": self.enabled,
            "type": self.type,
            "description": self.description
        }


class WorkspaceManager:
    """
    Manages multiple solution repositories.
    
    Reads configuration from .config/repos.json to determine which
    repositories are available and enabled.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize workspace manager.
        
        Args:
            project_root: Root path of the primary repository (industry-apps)
        """
        self.project_root = project_root
        self.repos: List[RepoInfo] = []
        self._load_repos()
    
    def _load_repos(self):
        """Load repository configuration from repos.json."""
        config_path = self.project_root / ".config" / "repos.json"
        
        if not config_path.exists():
            # Fallback: Just use current repo
            logger.info("No repos.json found, using single-repo mode")
            self.repos = [RepoInfo(
                name="industry-apps",
                path=self.project_root,
                enabled=True,
                type="model-driven-apps",
                description="Primary repository"
            )]
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for repo_config in config.get('repos', []):
                repo_path = self.project_root / repo_config['path']
                
                # Resolve relative paths
                repo_path = repo_path.resolve()
                
                # Check if repo exists and is enabled
                if repo_config.get('enabled', False):
                    if not repo_path.exists():
                        logger.warning(f"Repo path does not exist: {repo_path} (from config: {repo_config['path']})")
                        continue
                    
                    # Verify it has .config/deployments.json
                    deployment_config = repo_path / ".config" / "deployments.json"
                    if not deployment_config.exists():
                        logger.warning(f"Repo missing deployments.json: {repo_path}")
                        continue
                    
                    repo_info = RepoInfo(
                        name=repo_config['name'],
                        path=repo_path,
                        enabled=True,
                        type=repo_config.get('type', 'unknown'),
                        description=repo_config.get('description', '')
                    )
                    self.repos.append(repo_info)
                    logger.info(f"Loaded repo: {repo_info.name} at {repo_path}")
            
            if not self.repos:
                logger.warning("No enabled repos found, falling back to current repo only")
                self.repos = [RepoInfo(
                    name="industry-apps",
                    path=self.project_root,
                    enabled=True,
                    type="model-driven-apps",
                    description="Primary repository"
                )]
        
        except Exception as e:
            logger.error(f"Error loading repos.json: {e}")
            # Fallback to single repo mode
            self.repos = [RepoInfo(
                name="industry-apps",
                path=self.project_root,
                enabled=True,
                type="model-driven-apps",
                description="Primary repository"
            )]
    
    def get_all_repos(self) -> List[RepoInfo]:
        """Get all enabled repositories."""
        return self.repos
    
    def get_repo_by_name(self, name: str) -> Optional[RepoInfo]:
        """Get a specific repository by name."""
        for repo in self.repos:
            if repo.name == name:
                return repo
        return None
    
    def get_deployment_config_path(self, repo_name: str) -> Optional[Path]:
        """
        Get the path to deployments.json for a specific repo.
        
        Args:
            repo_name: Name of the repository
            
        Returns:
            Path to deployments.json, or None if repo not found
        """
        repo = self.get_repo_by_name(repo_name)
        if repo:
            return repo.path / ".config" / "deployments.json"
        return None
    
    def is_multi_repo(self) -> bool:
        """Check if running in multi-repo mode."""
        return len(self.repos) > 1
    
    def get_repo_summary(self) -> Dict:
        """Get summary of all repositories for logging/debugging."""
        return {
            "count": len(self.repos),
            "multi_repo_mode": self.is_multi_repo(),
            "repos": [repo.to_dict() for repo in self.repos]
        }
