"""Adapter for Amazon Q CLI tool."""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import shutil
import os
from ..content import ToolAdapter, Rule, Workflow, Profile

class QCLIAdapter(ToolAdapter):
    """Adapter for Amazon Q CLI tool."""
    
    def __init__(self, tool_name: str, config_dir: Path):
        super().__init__(tool_name, config_dir)
        self.rules_dir = self.config_dir / 'rules'
        self.profiles_dir = self.config_dir / 'profiles'
        self.workflows_dir = self.config_dir / 'workflows'
        
        # Create required directories
        for directory in [self.rules_dir, self.profiles_dir, self.workflows_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def sync_rule(self, rule: Rule) -> None:
        """Sync a single rule to Q CLI format."""
        q_rule = {
            'name': rule.name,
            'description': rule.content.get('description', ''),
            'enabled': rule.content.get('enabled', True),
            'conditions': rule.content.get('conditions', []),
            'actions': rule.content.get('actions', [])
        }
        
        # Save to Q CLI rules directory
        rule_path = self.rules_dir / f"{rule.name}.yaml"
        with open(rule_path, 'w') as f:
            yaml.dump(q_rule, f, default_flow_style=False)
    
    def sync_profile(self, profile: Profile) -> None:
        """Sync a profile to Q CLI format."""
        if profile.tool != 'q-cli':
            return  # Skip profiles for other tools
            
        q_profile = {
            'name': profile.name,
            'description': profile.content.get('description', ''),
            'settings': profile.content.get('settings', {})
        }
        
        # Save to Q CLI profiles directory
        profile_path = self.profiles_dir / f"{profile.name}.yaml"
        with open(profile_path, 'w') as f:
            yaml.dump(q_profile, f, default_flow_style=False)
    
    def sync_workflow(self, workflow: Workflow) -> None:
        """Sync a workflow to Q CLI format."""
        q_workflow = {
            'name': workflow.name,
            'description': workflow.content.get('description', ''),
            'steps': workflow.content.get('steps', [])
        }
        
        # Save to Q CLI workflows directory
        workflow_path = self.workflows_dir / f"{workflow.name}.yaml"
        with open(workflow_path, 'w') as f:
            yaml.dump(q_workflow, f, default_flow_style=False)
    
    def sync(self, content_manager) -> None:
        """Sync all content to Q CLI configuration."""
        # Sync rules
        for rule in content_manager.list_rules():
            self.sync_rule(rule)
        
        # Sync profiles (only Q-CLI specific ones)
        for profile in content_manager.list_profiles():
            self.sync_profile(profile)
        
        # Sync workflows
        for workflow in content_manager.list_workflows():
            self.sync_workflow(workflow)
        
        # Create or update main Q CLI config
        self._update_main_config()
    
    def _update_main_config(self) -> None:
        """Update the main Q CLI configuration file."""
        config_path = self.config_dir / 'config.yaml'
        config = {}
        
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        
        # Ensure default sections exist
        config.setdefault('rules', {})
        config.setdefault('profiles', {})
        config.setdefault('workflows', {})
        
        # Update with current rules, profiles, and workflows
        config['rules'] = {
            f.name[:-5]: {'enabled': True}  # Remove .yaml extension
            for f in self.rules_dir.glob('*.yaml')
        }
        
        config['profiles'] = {
            f.name[:-5]: {'enabled': True}  # Remove .yaml extension
            for f in self.profiles_dir.glob('*.yaml')
        }
        
        config['workflows'] = {
            f.name[:-5]: {'enabled': True}  # Remove .yaml extension
            for f in self.workflows_dir.glob('*.yaml')
        }
        
        # Save updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
