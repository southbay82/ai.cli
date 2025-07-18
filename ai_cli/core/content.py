"""Core content management for AI CLI tools."""
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Generic, Any, Callable, Set, Union
from dataclasses import dataclass, field, asdict
import yaml
import json
import shutil
from enum import Enum, auto
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T', bound='ContentItem')

class ContentType(Enum):
    """Types of content that can be managed."""
    RULE = 'rules'
    WORKFLOW = 'workflows'
    PROFILE = 'profiles'
    GLOBAL_RULE = 'global_rules'
    PROJECT_RULE = 'project_rules'
    AMAZONQ_PROFILE = 'amazonq_profiles'
    WINDSURF_WORKFLOW = 'windsurf_workflows'
    
    def __str__(self):
        return self.value

    @classmethod
    def get_content_dir(cls, content_type: 'ContentType', base_dir: Path) -> Path:
        """Get the directory path for a content type."""
        return base_dir / content_type.value

@dataclass
class ContentItem:
    """Base class for all content items (rules, workflows, profiles)."""
    name: str
    content: Dict[str, Any]
    content_type: ContentType
    path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the content item after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate the content item.
        
        Raises:
            ValueError: If the content item is invalid.
        """
        if not self.name:
            raise ValueError("Content item must have a name")
        if not isinstance(self.content, dict):
            raise ValueError("Content must be a dictionary")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the content item to a dictionary."""
        return {
            'name': self.name,
            'content_type': self.content_type.value,
            'content': self.content,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a content item from a dictionary."""
        content_type = ContentType(data.get('content_type', 'rules'))
        return cls(
            name=data['name'],
            content_type=content_type,
            content=data['content'],
            metadata=data.get('metadata', {})
        )
    
    def save(self, base_dir: Optional[Path] = None, filename: Optional[str] = None) -> Path:
        """Save the content item to a file.
        
        Args:
            base_dir: Base directory to save the file in. If not provided, uses the item's path.
            filename: Name of the file to save. If not provided, generates one from the item name.
            
        Returns:
            Path: The path where the file was saved.
            
        Raises:
            ValueError: If no path can be determined.
        """
        if base_dir is None and self.path is None and filename is None:
            raise ValueError("Either base_dir or path must be provided")
        
        # Determine the save path
        logger.debug(f"save() called with filename={filename}, base_dir={base_dir}, self.path={self.path}")
        logger.debug(f"Type of filename: {type(filename)}")
        logger.debug(f"Content type: {self.content_type}")
        
        # Special case: user passed a single positional argument that is actually a file path
        if filename is None and base_dir is not None and Path(base_dir).suffix in {'.yaml', '.yml', '.json'}:
            save_path = Path(base_dir)
            logger.debug(f"Detected file path passed as base_dir positional arg: {save_path}")
            base_dir = None  # prevent further use
        
        if filename is not None:
            # If a filename is provided, use it as is
            filename = Path(filename)
            logger.debug(f"Processing filename: {filename}")
            logger.debug(f"Filename parts: name={filename.name}, suffix={filename.suffix}, parent={filename.parent}")
            
            if base_dir is not None:
                # If base_dir is provided, join it with the filename
                # But only if the filename is not already an absolute path
                if filename.is_absolute():
                    save_path = filename
                else:
                    # If the filename has an extension, treat it as a file
                    if filename.suffix:
                        save_path = base_dir / filename
                    else:
                        # If no extension, treat it as a directory and append a filename
                        ext = '.yaml' if self.content_type in [ContentType.RULE, ContentType.WORKFLOW, ContentType.PROFILE] else '.json'
                        default_filename = f"{self.name.lower().replace(' ', '_')}{ext}"
                        save_path = base_dir / filename / default_filename
                logger.debug(f"Combined with base_dir: {save_path}")
            else:
                # If no base_dir, use the filename as is
                save_path = filename
                logger.debug(f"Using filename as is: {save_path}")
                
        elif self.path is not None:
            # If the item already has a path, use it
            save_path = Path(self.path)
            logger.debug(f"Using existing path: {save_path}")
        else:
            # Generate a filename based on content type and name
            ext = '.yaml' if self.content_type in [ContentType.RULE, ContentType.WORKFLOW, ContentType.PROFILE] else '.json'
            filename = f"{self.name.lower().replace(' ', '_')}{ext}"
            save_path = base_dir / filename if base_dir else Path(filename)
            logger.debug(f"Generated save path: {save_path}")
        
        # Ensure the save path has the correct extension if it's not already set
        if not save_path.suffix:
            ext = '.yaml' if self.content_type in [ContentType.RULE, ContentType.WORKFLOW, ContentType.PROFILE] else '.json'
            save_path = save_path.with_suffix(ext)
        
        # Ensure the directory exists
        logger.debug(f"Ensuring directory exists: {save_path.parent}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Saving to file: {save_path}")
        
        # Convert the content item to a dictionary
        data = {
            'name': self.name,
            'content': self.content,
            'content_type': self.content_type.value,
            'metadata': self.metadata
        }
        
        # Save the file
        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.suffix in ('.yaml', '.yml'):
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            elif save_path.suffix == '.json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported file format: {save_path.suffix}")
        
        self.path = save_path
        logger.info(f"Saved {self.content_type.value} '{self.name}' to {save_path}")
        return save_path
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'ContentItem':
        """Load a content item from a file.
        
        Args:
            filepath: Path to the file to load.
            
        Returns:
            ContentItem: The loaded content item.
            
        Raises:
            ValueError: If the file format is not supported.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.suffix in ('.yaml', '.yml'):
                data = yaml.safe_load(f)
            elif filepath.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        # Determine content type from filepath if not in data
        if 'content_type' not in data:
            # Infer from parent directory name
            parent_dir = filepath.parent.name
            try:
                data['content_type'] = ContentType(parent_dir).value
            except ValueError:
                data['content_type'] = ContentType.RULE.value
        
        # Create the appropriate content item class
        content_type = ContentType(data['content_type'])
        if content_type in [ContentType.RULE, ContentType.GLOBAL_RULE, ContentType.PROJECT_RULE]:
            item = Rule.from_dict(data)
        elif content_type in [ContentType.WORKFLOW, ContentType.WINDSURF_WORKFLOW]:
            item = Workflow.from_dict(data)
        elif content_type in [ContentType.PROFILE, ContentType.AMAZONQ_PROFILE]:
            item = Profile.from_dict(data)
        else:
            item = cls.from_dict(data)
        
        item.path = filepath
        return item

@dataclass
class Rule(ContentItem):
    """A rule defines behavior or constraints for AI tools."""
    content_type: ContentType = field(default=ContentType.RULE, init=True)
    
    def __post_init__(self):
        """Set content type and validate."""
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)
        super().__post_init__()
    
    def validate(self) -> None:
        """Validate the rule content."""
        super().validate()
        if not isinstance(self.content, dict):
            raise ValueError("Rule content must be a dictionary")

@dataclass
class Workflow(ContentItem):
    """A workflow defines a sequence of steps or actions."""
    content_type: ContentType = field(default=ContentType.WORKFLOW, init=False)
    
    def __post_init__(self):
        """Set content type and validate."""
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)
        super().__post_init__()
    
    def validate(self) -> None:
        """Validate the workflow content."""
        super().validate()
        if not isinstance(self.content, dict) or 'steps' not in self.content:
            raise ValueError("Workflow content must be a dictionary with a 'steps' key")

@dataclass(init=False)
class Profile(ContentItem):
    """A profile contains tool-specific configuration.
    
    Args:
        name: The name of the profile.
        tool: The name of the tool this profile is for.
        content: The profile configuration data.
        path: Optional path to the profile file.
        metadata: Optional metadata for the profile.
    """
    tool: str
    
    def __init__(self, 
                 name: str, 
                 tool: str, 
                 content: Dict[str, Any], 
                 path: Optional[Path] = None, 
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize a Profile instance.
        
        Note: We use a custom __init__ to ensure proper parameter ordering.
        """
        self.name = name
        self.tool = tool
        self.content = content
        self.path = path
        self.metadata = metadata or {}
        self.content_type = ContentType.PROFILE
        
        # Call post-init for validation
        self.__post_init__()
    
    def __post_init__(self):
        """Set content type and validate."""
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)
        super().__post_init__()
    
    def validate(self) -> None:
        """Validate the profile content."""
        super().validate()
        if not self.tool:
            raise ValueError("Profile must specify a tool")
        if not isinstance(self.content, dict):
            raise ValueError("Profile content must be a dictionary")


class ContentManager:
    """Manages content items (rules, workflows, profiles) for AI tools."""
    
    def __init__(self, base_dir: Path):
        """Initialize the content manager with a base directory.
        
        Args:
            base_dir: Base directory containing content subdirectories.
        """
        self.base_dir = base_dir.resolve()
        self.content_dirs = {}
        
        # Initialize content directories
        for content_type in ContentType.__members__.values():
            dir_path = base_dir / content_type.value
            dir_path.mkdir(parents=True, exist_ok=True)
            self.content_dirs[content_type] = dir_path
        
        logger.info(f"Initialized ContentManager with base directory: {self.base_dir}")
    
    def add_item(self, item: ContentItem, overwrite: bool = False) -> Path:
        """Add a new content item.
        
        Args:
            item: The content item to add.
            overwrite: Whether to overwrite an existing item with the same name.
            
        Returns:
            Path: The path where the item was saved.
            
        Raises:
            FileExistsError: If an item with the same name exists and overwrite is False.
        """
        # Check for existing item
        existing = self.get_item(item.content_type, item.name)
        if existing and not overwrite:
            raise FileExistsError(f"{item.content_type.value} '{item.name}' already exists")
        
        # Save the item
        logger.debug(f"Saving item of type {item.content_type} to {self.content_dirs[item.content_type]}")
        save_path = item.save(self.content_dirs[item.content_type])
        logger.debug(f"Item saved to: {save_path}")
        return save_path
    
    def get_item(self, content_type: Union[ContentType, str], name: str) -> Optional[ContentItem]:
        """Get a content item by type and name.
        
        Args:
            content_type: Type of content to get.
            name: Name of the content item.
            
        Returns:
            Optional[ContentItem]: The content item, or None if not found.
        """
        if isinstance(content_type, str):
            content_type = ContentType(content_type)
        
        # Search for the item in the appropriate directory and its subdirectories
        content_dir = self.content_dirs[content_type]
        for ext in ['.yaml', '.yml', '.json']:
            # Try direct path first (for backward compatibility)
            filepath = content_dir / f"{name}{ext}"
            if filepath.exists():
                return ContentItem.load(filepath)
                
            # Try subdirectories
            for filepath in content_dir.glob(f"**/{name}{ext}"):
                if filepath.is_file():
                    return ContentItem.load(filepath)
        
        return None
    
    def list_items(self, content_type: Union[ContentType, str], pattern: str = '*') -> List[ContentItem]:
        """List all content items of a specific type.
        
        Args:
            content_type: Type of content to list.
            pattern: Glob pattern to filter items.
            
        Returns:
            List[ContentItem]: List of content items.
        """
        if isinstance(content_type, str):
            content_type = ContentType(content_type)
        
        items = []
        for ext in ['*.yaml', '*.yml', '*.json']:
            for filepath in self.content_dirs[content_type].glob(f"{pattern}{ext[1:]}"):
                try:
                    items.append(ContentItem.load(filepath))
                except Exception as e:
                    logger.warning(f"Error loading {content_type.value} from {filepath}: {e}")
        
        return items
    
    def delete_item(self, content_type: Union[ContentType, str], name: str) -> bool:
        """Delete a content item.
        
        Args:
            content_type: Type of content to delete.
            name: Name of the content item to delete.
            
        Returns:
            bool: True if the item was deleted, False if not found.
        """
        item = self.get_item(content_type, name)
        if not item or not item.path:
            return False
        
        try:
            item.path.unlink()
            logger.info(f"Deleted {content_type.value} '{name}' from {item.path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {content_type.value} '{name}': {e}")
            return False
    
    def sync_to_tool(self, tool_name: str, tool_adapter: 'ToolAdapter', progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """Sync content to a specific tool using the provided adapter.
        
        Args:
            tool_name: Name of the tool to sync with.
            tool_adapter: The tool adapter to use for syncing.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            bool: True if sync was successful, False otherwise.
        """
        try:
            if progress_callback:
                progress_callback(0, f"Starting sync with {tool_name}")
            
            # Get the content types supported by this tool
            supported_types = tool_adapter.get_supported_content_types()
            
            # Collect all content items to sync
            items_to_sync = []
            for content_type in supported_types:
                items = self.list_items(content_type)
                items_to_sync.extend(items)
            
            if not items_to_sync:
                if progress_callback:
                    progress_callback(100, "No content to sync")
                return True
            
            # Sync each item
            total_items = len(items_to_sync)
            for i, item in enumerate(items_to_sync, 1):
                if progress_callback:
                    progress = int((i / total_items) * 100)
                    progress_callback(progress, f"Syncing {item.content_type.value} '{item.name}'")
                
                # Let the adapter handle the sync for this item
                tool_adapter.sync_item(item)
            
            if progress_callback:
                progress_callback(100, f"Sync with {tool_name} complete")
            
            return True
            
        except Exception as e:
            logger.error(f"Error syncing with {tool_name}: {e}")
            if progress_callback:
                progress_callback(0, f"Error syncing with {tool_name}: {str(e)}")
            return False

class ToolAdapter(Generic[T]):
    """Base class for tool-specific content adapters."""
    
    def __init__(self, tool_name: str, config_dir: Path):
        """Initialize the tool adapter.
        
        Args:
            tool_name: Name of the tool.
            config_dir: Base directory for the tool's configuration.
        """
        self.tool_name = tool_name
        self.config_dir = config_dir.resolve()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized {tool_name} adapter with config directory: {self.config_dir}")
    
    def get_supported_content_types(self) -> Set[ContentType]:
        """Get the content types supported by this adapter.
        
        Returns:
            Set[ContentType]: Set of supported content types.
        """
        return set()
    
    def sync_item(self, item: ContentItem) -> bool:
        """Sync a single content item to the tool's configuration.
        
        Args:
            item: The content item to sync.
            
        Returns:
            bool: True if the sync was successful, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement sync_item")
    
    def sync(self, content_manager: ContentManager, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """Sync all content to the tool's configuration.
        
        Args:
            content_manager: The content manager containing the content to sync.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            bool: True if the sync was successful, False otherwise.
        """
        return content_manager.sync_to_tool(self.tool_name, self, progress_callback)

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
