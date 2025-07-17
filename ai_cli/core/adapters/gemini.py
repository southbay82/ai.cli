"""Adapter for Google Gemini AI tool."""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import shutil
import os
from ..content import ToolAdapter, Rule, Workflow, Profile

class GeminiAdapter(ToolAdapter):
    """Adapter for Google Gemini AI tool."""
    
    def __init__(self, tool_name: str, config_dir: Path):
        super().__init__(tool_name, config_dir)
        self.prompts_dir = self.config_dir / 'prompts'
        self.config_file = self.config_dir / 'config.yaml'
        
        # Create required directories
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
    
    def sync_rule(self, rule: Rule) -> None:
        """Sync a rule to Gemini format."""
        # Gemini doesn't directly support rules, so we'll convert them to prompt templates
        gemini_prompt = {
            'name': f"rule_{rule.name}",
            'description': rule.content.get('description', ''),
            'template': self._rule_to_prompt(rule)
        }
        
        # Save as a prompt template
        prompt_path = self.prompts_dir / f"rule_{rule.name}.yaml"
        with open(prompt_path, 'w') as f:
            yaml.dump(gemini_prompt, f, default_flow_style=False)
    
    def _rule_to_prompt(self, rule: Rule) -> str:
        """Convert a rule to a prompt template string."""
        conditions = "\n".join([f"- {cond}" for cond in rule.content.get('conditions', [])])
        actions = "\n".join([f"- {action}" for action in rule.content.get('actions', [])])
        
        return (
            f"# Rule: {rule.name}\n"
            f"## Conditions\n{conditions}\n\n"
            f"## Actions\n{actions}"
        )
    
    def sync_profile(self, profile: Profile) -> None:
        """Sync a profile to Gemini format."""
        if profile.tool != 'gemini':
            return  # Skip profiles for other tools
            
        # For Gemini, we'll create a prompt template for the profile
        gemini_prompt = {
            'name': f"profile_{profile.name}",
            'description': profile.content.get('description', ''),
            'template': self._profile_to_prompt(profile)
        }
        
        # Save as a prompt template
        prompt_path = self.prompts_dir / f"profile_{profile.name}.yaml"
        with open(prompt_path, 'w') as f:
            yaml.dump(gemini_prompt, f, default_flow_style=False)
    
    def _profile_to_prompt(self, profile: Profile) -> str:
        """Convert a profile to a prompt template string."""
        settings = "\n".join([f"- {k}: {v}" for k, v in profile.content.get('settings', {}).items()])
        
        return (
            f"# Profile: {profile.name}\n"
            f"## Settings\n{settings}\n"
        )
    
    def sync_workflow(self, workflow: Workflow) -> None:
        """Sync a workflow to Gemini format."""
        # Convert workflow to a prompt template
        gemini_workflow = {
            'name': f"workflow_{workflow.name}",
            'description': workflow.content.get('description', ''),
            'template': self._workflow_to_prompt(workflow)
        }
        
        # Save as a prompt template
        workflow_path = self.prompts_dir / f"workflow_{workflow.name}.yaml"
        with open(workflow_path, 'w') as f:
            yaml.dump(gemini_workflow, f, default_flow_style=False)
    
    def _workflow_to_prompt(self, workflow: Workflow) -> str:
        """Convert a workflow to a prompt template string."""
        steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow.content.get('steps', []))])
        
        return (
            f"# Workflow: {workflow.name}\n"
            f"## Steps\n{steps}\n"
        )
    
    def sync(self, content_manager) -> None:
        """Sync all content to Gemini configuration."""
        # Clear existing prompts
        for f in self.prompts_dir.glob('*'):
            if f.is_file():
                f.unlink()
        
        # Sync rules as prompt templates
        for rule in content_manager.list_rules():
            self.sync_rule(rule)
        
        # Sync profiles as prompt templates
        for profile in content_manager.list_profiles():
            self.sync_profile(profile)
        
        # Sync workflows as prompt templates
        for workflow in content_manager.list_workflows():
            self.sync_workflow(workflow)
        
        # Update main Gemini config
        self._update_main_config()
    
    def _update_main_config(self) -> None:
        """Update the main Gemini configuration file."""
        config = {
            'prompts_dir': str(self.prompts_dir.relative_to(self.config_dir)),
            'prompts': {
                f.stem: {'enabled': True}
                for f in self.prompts_dir.glob('*.yaml')
            }
        }
        
        # Save updated config
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
