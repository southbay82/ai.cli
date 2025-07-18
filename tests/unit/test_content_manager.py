"""Unit tests for the content manager module."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import the real ContentManager and other classes
from ai_cli.core.content import (
    ContentManager, ContentItem, Rule, Workflow, Profile, 
    ContentType, ToolAdapter
)

@pytest.fixture
def temp_content_dir(tmp_path):
    """Create a temporary directory with content structure for testing."""
    # Create content directories
    content_dirs = [
        'rules', 'workflows', 'profiles', 
        'global_rules', 'project_rules', 
        'amazonq_profiles', 'windsurf_workflows'
    ]
    for dir_name in content_dirs:
        (tmp_path / dir_name).mkdir()
    
    return tmp_path

class TestContentManager:
    """Test cases for the ContentManager class."""
    
    def test_init_creates_directories(self, temp_content_dir):
        """Test that ContentManager creates required directories."""
        # When
        manager = ContentManager(temp_content_dir)
        
        # Then
        for content_type in ContentType.__members__.values():
            dir_path = temp_content_dir / content_type.value
            assert dir_path.exists(), f"Directory {dir_path} does not exist"
            assert dir_path.is_dir(), f"{dir_path} is not a directory"
    
    def test_add_and_get_item(self, temp_content_dir):
        """Test adding and retrieving a content item."""
        # Create a real ContentManager instance
        manager = ContentManager(temp_content_dir)
        
        # Create a real Rule instance
        rule = Rule("test_rule", {"description": "A test rule"})
        
        # When
        print(f"Adding rule: {rule}")
        saved_path = manager.add_item(rule)
        print(f"Saved path: {saved_path}")
        
        # Verify the file was created
        assert saved_path is not None
        print(f"Content dir: {manager.content_dirs[ContentType.RULE]}")
        print("Files in content dir:", list(manager.content_dirs[ContentType.RULE].glob('*')))
        
        # Get the rule back
        retrieved_rule = manager.get_item(ContentType.RULE, "test_rule")
        print(f"Retrieved rule: {retrieved_rule}")
        
        # Then
        assert saved_path.exists()
        assert retrieved_rule is not None
        assert retrieved_rule.name == "test_rule"
        assert retrieved_rule.content == {"description": "A test rule"}
    
    def test_list_items(self, temp_content_dir):
        """Test listing content items."""
        # Given
        manager = ContentManager(temp_content_dir)
        rule1 = Rule("rule1", {"description": "Rule 1"})
        rule2 = Rule("rule2", {"description": "Rule 2"})
        
        # When
        manager.add_item(rule1)
        manager.add_item(rule2)
        rules = manager.list_items(ContentType.RULE)
        
        # Then
        assert len(rules) == 2
        assert {r.name for r in rules} == {"rule1", "rule2"}
    
    def test_delete_item(self, temp_content_dir):
        """Test deleting a content item."""
        # Given
        manager = ContentManager(temp_content_dir)
        rule = Rule("test_rule", {"description": "A test rule"})
        manager.add_item(rule)
        
        # When
        result = manager.delete_item(ContentType.RULE, "test_rule")
        
        # Then
        assert result is True
        assert manager.get_item(ContentType.RULE, "test_rule") is None
    
    def test_sync_to_tool(self, temp_content_dir):
        """Test syncing content to a tool."""
        # Given
        manager = ContentManager(temp_content_dir)
        rule = Rule("test_rule", {"description": "A test rule"})
        manager.add_item(rule)
        
        mock_adapter = MagicMock(spec=ToolAdapter)
        mock_adapter.get_supported_content_types.return_value = {ContentType.RULE}
        
        # When
        result = manager.sync_to_tool("test_tool", mock_adapter)
        
        # Then
        assert result is True
        mock_adapter.sync_item.assert_called_once()
        called_item = mock_adapter.sync_item.call_args[0][0]
        assert called_item.name == "test_rule"

class TestToolAdapter:
    """Test cases for the ToolAdapter base class."""
    
    def test_sync_calls_sync_to_tool(self, temp_content_dir):
        """Test that sync() calls sync_to_tool on the content manager."""
        # Given
        adapter = ToolAdapter("test_tool", temp_content_dir / "config")
        mock_manager = MagicMock()
        mock_progress_callback = MagicMock()
        
        # When
        adapter.sync(mock_manager, mock_progress_callback)
        
        # Then
        mock_manager.sync_to_tool.assert_called_once_with(
            "test_tool", adapter, mock_progress_callback
        )

class TestContentItemSerialization:
    """Test serialization and deserialization of content items."""
    
    def test_rule_serialization(self, temp_content_dir):
        """Test serializing and deserializing a Rule."""
        # Given
        rule = Rule("test_rule", {"description": "A test rule"})
        file_path = temp_content_dir / "test_rule.yaml"
        
        # When
        rule.save(file_path)
        loaded_rule = ContentItem.load(file_path)
        
        # Then
        assert isinstance(loaded_rule, Rule)
        assert loaded_rule.name == "test_rule"
        assert loaded_rule.content == {"description": "A test rule"}
    
    def test_workflow_serialization(self, temp_content_dir):
        """Test serializing and deserializing a Workflow."""
        # Given
        workflow = Workflow("test_workflow", {"steps": ["step1", "step2"]})
        file_path = temp_content_dir / "test_workflow.yaml"
        
        # When
        workflow.save(file_path)
        loaded_workflow = ContentItem.load(file_path)
        
        # Then
        assert isinstance(loaded_workflow, Workflow)
        assert loaded_workflow.name == "test_workflow"
        assert loaded_workflow.content == {"steps": ["step1", "step2"]}
    
    def test_profile_serialization(self, temp_content_dir):
        """Test serializing and deserializing a Profile."""
        # Given
        profile = Profile("test_profile", "test_tool", {"api_key": "12345"})
        file_path = temp_content_dir / "test_profile.yaml"
        
        # When
        profile.save(file_path)
        loaded_profile = ContentItem.load(file_path)
        
        # Then
        assert isinstance(loaded_profile, Profile)
        assert loaded_profile.name == "test_profile"
        assert loaded_profile.tool == "test_tool"
        assert loaded_profile.content == {"api_key": "12345"}
