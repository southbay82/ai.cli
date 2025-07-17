"""Adapter for Windsurf AI tool."""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import shutil
import os
from ..content import ToolAdapter, Rule, Workflow, Profile

class WindsurfAdapter(ToolAdapter):
    """Adapter for Windsurf AI tool."""
    
    def __init__(self, tool_name: str, config_dir: Path):
        super().__init__(tool_name, config_dir)
        self.personas_dir = self.config_dir / 'personas'  # Windsurf uses personas instead of profiles
        self.rules_dir = self.config_dir / 'rules'
        
        # Create required directories
        for directory in [self.personas_dir, self.rules_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def sync_rule(self, rule: Rule) -> None:
        """Sync a rule to Windsurf format."""
        windsurf_rule = {
            'name': rule.name,
            'description': rule.content.get('description', ''),
            'enabled': rule.content.get('enabled', True),
            'conditions': rule.content.get('conditions', []),
            'actions': rule.content.get('actions', [])
        }
        
        # Save to Windsurf rules directory
        rule_path = self.rules_dir / f"{rule.name}.json"
        with open(rule_path, 'w') as f:
            json.dump(windsurf_rule, f, indent=2)
    
    def sync_profile_as_persona(self, profile: Profile) -> None:
        """Sync a profile as a Windsurf persona."""
        if profile.tool != 'windsurf':
            return  # Skip profiles for other tools
            
        persona = {
            'name': profile.name,
            'description': profile.content.get('description', ''),
            'settings': profile.content.get('settings', {})
        }
        
        # Save to Windsurf personas directory
        persona_path = self.personas_dir / f"{profile.name}.json"
        with open(persona_path, 'w') as f:
            json.dump(persona, f, indent=2)
    
    def sync(self, content_manager) -> None:
        """Sync all content to Windsurf configuration."""
        # Sync rules
        for rule in content_manager.list_rules():
            self.sync_rule(rule)
        
        # Sync profiles as personas
        for profile in content_manager.list_profiles():
            self.sync_profile_as_persona(profile)
        
        # Update main Windsurf config
        self._update_main_config()
    
    def _update_main_config(self) -> None:
        """Update the main Windsurf configuration file."""
        config_path = self.config_dir / 'config.json'
        config = {}
        
        if config_path.exists():
            with open(config_path) as f:
                try:
                    config = json.load(f) or {}
                except json.JSONDecodeError:
                    config = {}
        
        # Ensure default sections exist
        config.setdefault('personas', {})
        config.setdefault('rules', {})
        
        # Update with current personas and rules
        config['personas'] = {
            f.stem: {'enabled': True}
            for f in self.personas_dir.glob('*.json')
        }
        
        config['rules'] = {
            f.stem: {'enabled': True}
            for f in self.rules_dir.glob('*.json')
        }
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
