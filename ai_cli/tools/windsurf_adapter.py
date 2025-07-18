"""Windsurf tool adapter for content management."""
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Set, Optional, List

from ai_cli.core.content import (
    ToolAdapter, ContentItem, Rule, Workflow, ContentType
)

logger = logging.getLogger(__name__)

class WindsurfAdapter(ToolAdapter):
    """Adapter for Windsurf tool."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the Windsurf adapter.
        
        Args:
            config_dir: Base configuration directory. Defaults to ~/.windsurf
        """
        if config_dir is None:
            config_dir = Path.home() / '.windsurf'
        
        super().__init__("windsurf", config_dir)
        
        # Windsurf specific directories
        self.personas_dir = self.config_dir / 'personas'  # Rules in Windsurf are called "personas"
        self.workflows_dir = self.config_dir / 'workflows'
        
        # Create directories if they don't exist
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(exist_ok=True)
    
    def get_supported_content_types(self) -> Set[ContentType]:
        """Get the content types supported by Windsurf."""
        return {
            ContentType.RULE,          # For global rules
            ContentType.WORKFLOW,      # For workflows
            ContentType.WINDSURF_WORKFLOW  # For Windsurf-specific workflows
        }
    
    def sync_item(self, item: ContentItem) -> bool:
        """Sync a single content item to Windsurf configuration.
        
        Args:
            item: The content item to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            if item.content_type in [ContentType.RULE, ContentType.GLOBAL_RULE, ContentType.PROJECT_RULE]:
                return self._sync_persona(item)
            elif item.content_type in [ContentType.WORKFLOW, ContentType.WINDSURF_WORKFLOW]:
                return self._sync_workflow(item)
            else:
                logger.warning(
                    f"Content type {item.content_type} not supported by Windsurf"
                )
                return False
        except Exception as e:
            logger.error(f"Error syncing {item.content_type.value} '{item.name}' to Windsurf: {e}")
            return False
    
    def _sync_persona(self, rule: ContentItem) -> bool:
        """Sync a rule as a Windsurf persona.
        
        Args:
            rule: The rule to sync as a persona.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Windsurf uses JSON for persona configuration
            persona_path = self.personas_dir / f"{rule.name}.json"
            
            # Convert to Windsurf persona format
            persona_config = {
                'name': rule.name,
                'description': rule.content.get('description', ''),
                'config': rule.content
            }
            
            # Save the persona
            with open(persona_path, 'w', encoding='utf-8') as f:
                json.dump(persona_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Synced Windsurf persona '{rule.name}' to {persona_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Windsurf persona '{rule.name}': {e}")
            return False
    
    def _sync_workflow(self, workflow: ContentItem) -> bool:
        """Sync a workflow to Windsurf configuration.
        
        Args:
            workflow: The workflow to sync.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            # Windsurf uses JSON for workflow configuration
            workflow_path = self.workflows_dir / f"{workflow.name}.json"
            
            # Convert to Windsurf workflow format
            workflow_config = {
                'name': workflow.name,
                'description': workflow.content.get('description', ''),
                'steps': workflow.content.get('steps', [])
            }
            
            # Save the workflow
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Synced Windsurf workflow '{workflow.name}' to {workflow_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing Windsurf workflow '{workflow.name}': {e}")
            return False
    
    def list_personas(self) -> Dict[str, Dict[str, Any]]:
        """List all Windsurf personas.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of persona names to their configurations.
        """
        personas = {}
            
        for persona_file in self.personas_dir.glob('*.json'):
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
                    if isinstance(persona_data, dict):
                        persona_name = persona_data.get('name', persona_file.stem)
                        personas[persona_name] = persona_data
                    
            except Exception as e:
                logger.error(f"Error loading Windsurf persona from {persona_file}: {e}")
        
        return personas
    
    def get_persona(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific Windsurf persona.
        
        Args:
            name: Name of the persona to get.
            
        Returns:
            Optional[Dict[str, Any]]: The persona configuration, or None if not found.
        """
        persona_path = self.personas_dir / f"{name}.json"
        if not persona_path.exists():
            # Try to find by name in the persona files
            for file_path in self.personas_dir.glob('*.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get('name') == name:
                            return data
                except Exception:
                    continue
            return None
            
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading Windsurf persona '{name}': {e}")
            return None
    
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all Windsurf workflows.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of workflow names to their configurations.
        """
        workflows = {}
            
        for workflow_file in self.workflows_dir.glob('*.json'):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    if isinstance(workflow_data, dict):
                        workflow_name = workflow_data.get('name', workflow_file.stem)
                        workflows[workflow_name] = workflow_data
                    
            except Exception as e:
                logger.error(f"Error loading Windsurf workflow from {workflow_file}: {e}")
        
        return workflows
