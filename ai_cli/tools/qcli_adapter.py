"""Amazon Q CLI tool adapter for content management."""
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Set, Optional

from ai_cli.core.content import (
    ToolAdapter, ContentItem, Profile, ContentType
)

logger = logging.getLogger(__name__)

class QCLIAdapter(ToolAdapter):
    """Adapter for Amazon Q CLI tool."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the Q CLI adapter.
        
        Args:
            config_dir: Base configuration directory. Defaults to ~/.q
        """
        if config_dir is None:
            config_dir = Path.home() / '.q'
        
        super().__init__("q-cli", config_dir)
        
        # Q CLI specific directories
        self.profiles_dir = self.config_dir / 'profiles'
        self.rules_dir = self.config_dir / 'rules'
        self.workflows_dir = self.config_dir / 'workflows'
        
        # Create directories if they don't exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir.mkdir(exist_ok=True)
        self.workflows_dir.mkdir(exist_ok=True)
    
    def get_supported_content_types(self) -> Set[ContentType]:
        """Get the content types supported by Q CLI."""
        return {
            ContentType.PROFILE,
            ContentType.RULE,
            ContentType.WORKFLOW,
            ContentType.AMAZONQ_PROFILE
        }
    
    def sync_item(self, item: ContentItem) -> bool:
        """Sync a single content item to Q CLI configuration.
        
        Args:
            item: The content item to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            if item.content_type in [ContentType.PROFILE, ContentType.AMAZONQ_PROFILE]:
                return self._sync_profile(item)
            elif item.content_type == ContentType.RULE:
                return self._sync_rule(item)
            elif item.content_type == ContentType.WORKFLOW:
                return self._sync_workflow(item)
            else:
                logger.warning(
                    f"Content type {item.content_type} not supported by Q CLI"
                )
                return False
        except Exception as e:
            logger.error(f"Error syncing {item.content_type.value} '{item.name}' to Q CLI: {e}")
            return False
    
    def _sync_profile(self, profile: Profile) -> bool:
        """Sync a profile to Q CLI configuration.
        
        Args:
            profile: The profile to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Q CLI uses YAML for profile configuration
            profile_path = self.profiles_dir / f"{profile.name}.yaml"
            
            # Convert to Q CLI profile format
            q_profile = {
                'name': profile.name,
                'config': profile.content
            }
            
            # Save the profile
            with open(profile_path, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(q_profile, f, default_flow_style=False)
            
            logger.info(f"Synced Q CLI profile '{profile.name}' to {profile_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Q CLI profile '{profile.name}': {e}")
            return False
    
    def _sync_rule(self, rule: ContentItem) -> bool:
        """Sync a rule to Q CLI configuration.
        
        Args:
            rule: The rule to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Q CLI uses YAML for rule configuration
            rule_path = self.rules_dir / f"{rule.name}.yaml"
            
            # Save the rule
            with open(rule_path, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(rule.content, f, default_flow_style=False)
            
            logger.info(f"Synced Q CLI rule '{rule.name}' to {rule_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Q CLI rule '{rule.name}': {e}")
            return False
    
    def _sync_workflow(self, workflow: ContentItem) -> bool:
        """Sync a workflow to Q CLI configuration.
        
        Args:
            workflow: The workflow to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Q CLI uses YAML for workflow configuration
            workflow_path = self.workflows_dir / f"{workflow.name}.yaml"
            
            # Save the workflow
            with open(workflow_path, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(workflow.content, f, default_flow_style=False)
            
            logger.info(f"Synced Q CLI workflow '{workflow.name}' to {workflow_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Q CLI workflow '{workflow.name}': {e}")
            return False
    
    def list_profiles(self) -> Dict[str, Dict[str, Any]]:
        """List all Q CLI profiles.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of profile names to their configurations.
        """
        profiles = {}
            
        for profile_file in self.profiles_dir.glob('*.yaml'):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    import yaml
                    profile_data = yaml.safe_load(f) or {}
                    
                    # Extract profile name and config
                    profile_name = profile_data.get('name', profile_file.stem)
                    profiles[profile_name] = profile_data.get('config', {})
                    
            except Exception as e:
                logger.error(f"Error loading Q CLI profile from {profile_file}: {e}")
        
        return profiles
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific Q CLI profile.
        
        Args:
            name: Name of the profile to get.
            
        Returns:
            Optional[Dict[str, Any]]: The profile configuration, or None if not found.
        """
        profile_path = self.profiles_dir / f"{name}.yaml"
        if not profile_path.exists():
            return None
            
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                import yaml
                profile_data = yaml.safe_load(f) or {}
                return profile_data.get('config', {})
        except Exception as e:
            logger.error(f"Error loading Q CLI profile '{name}': {e}")
            return None
