"""Core content management for AI CLI tools."""
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Generic
from dataclasses import dataclass, field
import yaml
import json
import shutil

T = TypeVar('T', bound='ContentItem')

@dataclass
class ContentItem:
    """Base class for all content items (rules, workflows, profiles)."""
    name: str
    content: Dict
    path: Optional[Path] = None
    
    def to_dict(self) -> Dict:
        """Convert the content item to a dictionary."""
        return {
            'name': self.name,
            'content': self.content
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict) -> T:
        """Create a content item from a dictionary."""
        return cls(
            name=data['name'],
            content=data['content']
        )
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save the content item to a file."""
        path = path or self.path
        if not path:
            raise ValueError("No path specified for saving content item")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            if path.suffix in ('.yaml', '.yml'):
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(self.to_dict(), f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")

@dataclass
class Rule(ContentItem):
    """A rule defines behavior or constraints for AI tools."""
    pass

@dataclass
class Workflow(ContentItem):
    """A workflow defines a sequence of steps or actions."""
    pass

@dataclass
class Profile(ContentItem):
    """A profile contains tool-specific configuration."""
    tool: str

class ContentManager:
    """Manages content items (rules, workflows, profiles) for AI tools."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.rules_dir = base_dir / 'rules'
        self.workflows_dir = base_dir / 'workflows'
        self.profiles_dir = base_dir / 'profiles'
        
        # Create directories if they don't exist
        for directory in [self.rules_dir, self.workflows_dir, self.profiles_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def add_rule(self, rule: Rule) -> None:
        """Add a new rule."""
        rule.path = self.rules_dir / f"{rule.name}.yaml"
        rule.save()
    
    def get_rule(self, name: str) -> Optional[Rule]:
        """Get a rule by name."""
        path = self.rules_dir / f"{name}.yaml"
        if not path.exists():
            return None
        with open(path) as f:
            data = yaml.safe_load(f)
        return Rule.from_dict(data)
    
    def list_rules(self) -> List[Rule]:
        """List all rules."""
        rules = []
        for path in self.rules_dir.glob('*.yaml'):
            with open(path) as f:
                data = yaml.safe_load(f)
                rules.append(Rule.from_dict(data))
        return rules
    
    # Similar methods for workflows and profiles...
    
    def sync_to_tool(self, tool_name: str, tool_adapter: 'ToolAdapter') -> None:
        """Sync content to a specific tool using the provided adapter."""
        tool_adapter.sync(self)

class ToolAdapter(Generic[T]):
    """Base class for tool-specific content adapters."""
    
    def __init__(self, tool_name: str, config_dir: Path):
        self.tool_name = tool_name
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def sync(self, content_manager: ContentManager) -> None:
        """Sync content to the tool's configuration."""
        raise NotImplementedError

class QCLIAdapter(ToolAdapter):
    """Adapter for Amazon Q CLI tool."""
    
    def sync(self, content_manager: ContentManager) -> None:
        """Sync content to Q CLI configuration."""
        # Sync rules
        rules_dir = self.config_dir / 'rules'
        rules_dir.mkdir(exist_ok=True)
        
        for rule in content_manager.list_rules():
            # Convert rule to Q CLI format and save
            q_rule = {
                'name': rule.name,
                'description': rule.content.get('description', ''),
                'conditions': rule.content.get('conditions', []),
                'actions': rule.content.get('actions', [])
            }
            with open(rules_dir / f"{rule.name}.yaml", 'w') as f:
                yaml.dump(q_rule, f, default_flow_style=False)

# Add more tool adapters as needed

def get_content_manager() -> ContentManager:
    """Get a content manager instance with the default configuration."""
    from .config import GLOBAL_CONFIG_DIR
    return ContentManager(GLOBAL_CONFIG_DIR)
