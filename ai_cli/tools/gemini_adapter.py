"""Gemini tool adapter for content management."""
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Set, Optional, List

from ai_cli.core.content import (
    ToolAdapter, ContentItem, Profile, ContentType
)

logger = logging.getLogger(__name__)

class GeminiAdapter(ToolAdapter):
    """Adapter for Gemini tool."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the Gemini adapter.
        
        Args:
            config_dir: Base configuration directory. Defaults to ~/.gemini
        """
        if config_dir is None:
            config_dir = Path.home() / '.gemini'
        
        super().__init__("gemini", config_dir)
        
        # Gemini specific directories and files
        self.prompts_dir = self.config_dir / 'prompts'  # For prompt templates
        self.config_file = self.config_dir / 'config.json'  # Main config file
        
        # Create directories if they don't exist
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize config file if it doesn't exist
        if not self.config_file.exists():
            self._init_config()
    
    def _init_config(self) -> None:
        """Initialize the Gemini config file with defaults."""
        default_config = {
            "api_key": "",
            "model": "gemini-pro",
            "temperature": 0.7,
            "max_tokens": 2048,
            "prompt_templates": {}
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
    
    def get_supported_content_types(self) -> Set[ContentType]:
        """Get the content types supported by Gemini."""
        return {
            ContentType.PROFILE,  # For model configuration
            ContentType.RULE,     # For prompt templates
            ContentType.WORKFLOW  # For multi-step interactions
        }
    
    def sync_item(self, item: ContentItem) -> bool:
        """Sync a single content item to Gemini configuration.
        
        Args:
            item: The content item to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            if item.content_type == ContentType.PROFILE:
                return self._sync_config(item)
            elif item.content_type == ContentType.RULE:
                return self._sync_prompt_template(item)
            elif item.content_type == ContentType.WORKFLOW:
                return self._sync_workflow(item)
            else:
                logger.warning(
                    f"Content type {item.content_type} not supported by Gemini"
                )
                return False
        except Exception as e:
            logger.error(f"Error syncing {item.content_type.value} '{item.name}' to Gemini: {e}")
            return False
    
    def _sync_config(self, profile: Profile) -> bool:
        """Sync configuration to Gemini.
        
        Args:
            profile: The profile containing configuration.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Load current config
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update with profile settings
            for key, value in profile.content.items():
                if key in config:
                    config[key] = value
            
            # Save updated config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated Gemini configuration from profile '{profile.name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Gemini configuration: {e}")
            return False
    
    def _sync_prompt_template(self, rule: ContentItem) -> bool:
        """Sync a prompt template to Gemini configuration.
        
        Args:
            rule: The rule containing the prompt template.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Save prompt template to a file
            prompt_path = self.prompts_dir / f"{rule.name}.txt"
            
            # Extract prompt template from rule content
            prompt_template = rule.content.get('template', '')
            if not prompt_template and isinstance(rule.content, str):
                prompt_template = rule.content
            
            # Save the prompt template
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt_template)
            
            # Update config to include the prompt template reference
            with open(self.config_file, 'r+', encoding='utf-8') as f:
                config = json.load(f)
                if 'prompt_templates' not in config:
                    config['prompt_templates'] = {}
                config['prompt_templates'][rule.name] = str(prompt_path)
                f.seek(0)
                json.dump(config, f, indent=2)
                f.truncate()
            
            logger.info(f"Synced Gemini prompt template '{rule.name}' to {prompt_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Gemini prompt template '{rule.name}': {e}")
            return False
    
    def _sync_workflow(self, workflow: ContentItem) -> bool:
        """Sync a workflow to Gemini configuration.
        
        Args:
            workflow: The workflow to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Gemini workflows are stored as JSON files in the config directory
            workflow_path = self.config_dir / f"workflow_{workflow.name}.json"
            
            # Convert to Gemini workflow format
            workflow_config = {
                'name': workflow.name,
                'description': workflow.content.get('description', ''),
                'steps': workflow.content.get('steps', []),
                'parameters': workflow.content.get('parameters', {})
            }
            
            # Save the workflow
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_config, f, indent=2)
            
            logger.info(f"Synced Gemini workflow '{workflow.name}' to {workflow_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Gemini workflow '{workflow.name}': {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current Gemini configuration.
        
        Returns:
            Dict[str, Any]: The current configuration.
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading Gemini configuration: {e}")
            return {}
    
    def list_prompt_templates(self) -> Dict[str, str]:
        """List all available prompt templates.
        
        Returns:
            Dict[str, str]: Dictionary of template names to their file paths.
        """
        config = self.get_config()
        return config.get('prompt_templates', {})
    
    def get_prompt_template(self, name: str) -> Optional[str]:
        """Get a specific prompt template.
        
        Args:
            name: Name of the template to get.
            
        Returns:
            Optional[str]: The template content, or None if not found.
        """
        templates = self.list_prompt_templates()
        template_path = templates.get(name)
        
        if not template_path:
            return None
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template '{name}': {e}")
            return None
    
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all Gemini workflows.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of workflow names to their configurations.
        """
        workflows = {}
            
        for workflow_file in self.config_dir.glob('workflow_*.json'):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    if isinstance(workflow_data, dict):
                        workflow_name = workflow_data.get('name', workflow_file.stem.replace('workflow_', ''))
                        workflows[workflow_name] = workflow_data
                    
            except Exception as e:
                logger.error(f"Error loading Gemini workflow from {workflow_file}: {e}")
        
        return workflows
