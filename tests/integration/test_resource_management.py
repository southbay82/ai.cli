"""Integration tests for resource management commands."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_cli.resources import (
    list_resources, add_resource, remove_resource, edit_resource,
    get_content_type, get_resource_manager
)
from ai_cli.core.content import ContentManager, ContentType, Rule, Workflow, Profile

# Mock classes for testing
class MockRule:
    def __init__(self, name, content=None, **kwargs):
        self.name = name
        self.content = content or {}
        self.type = 'rule'
        self.path = f"/mock/path/to/{name}.yaml"

class MockWorkflow:
    def __init__(self, name, content=None, **kwargs):
        self.name = name
        self.content = content or {}
        self.type = 'workflow'
        self.path = f"/mock/path/to/{name}.yaml"

class MockProfile:
    def __init__(self, name, tool, content=None, **kwargs):
        self.name = name
        self.tool = tool
        self.content = content or {}
        self.type = 'profile'
        self.path = f"/mock/path/to/{tool}/{name}.yaml"

class TestResourceManagement(unittest.TestCase):
    """Integration tests for resource management commands."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test content manager instance
        self.content_manager = ContentManager()
        
        # Patch the console to capture output
        self.console_patcher = patch('ai_cli.resources.console.print')
        self.mock_console_print = self.console_patcher.start()
        
        # Patch the rule and workflow creation
        self.rule_patcher = patch('ai_cli.resources.Rule', MockRule)
        self.workflow_patcher = patch('ai_cli.resources.Workflow', MockWorkflow)
        self.profile_patcher = patch('ai_cli.resources.Profile', MockProfile)
        
        self.rule_patcher.start()
        self.workflow_patcher.start()
        self.profile_patcher.start()
        
        # Patch get_supported_tools
        self.tools_patcher = patch(
            'ai_cli.resources.get_supported_tools', 
            return_value={"test_tool": "test_tool"}
        )
        self.mock_get_supported_tools = self.tools_patcher.start()
        
        # Patch get_resource_manager to return our test content manager
        self.resource_manager_patcher = patch(
            'ai_cli.resources.get_resource_manager',
            return_value=self.content_manager
        )
        self.mock_get_resource_manager = self.resource_manager_patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop patching
        self.console_patcher.stop()
        self.rule_patcher.stop()
        self.workflow_patcher.stop()
        self.profile_patcher.stop()
        self.tools_patcher.stop()
        self.resource_manager_patcher.stop()
    
    def test_get_content_type(self):
        """Test mapping resource type strings to ContentType enums."""
        self.assertEqual(get_content_type('rule'), 'rule')
        self.assertEqual(get_content_type('workflow'), 'workflow')
        self.assertEqual(get_content_type('profile'), 'profile')
        self.assertEqual(get_content_type('global_rule'), 'global_rule')
        self.assertEqual(get_content_type('project_rule'), 'project_rule')
        self.assertEqual(get_content_type('amazonq_profile'), 'amazonq_profile')
        self.assertEqual(get_content_type('windsurf_workflow'), 'windsurf_workflow')
        self.assertEqual(get_content_type('unknown'), 'rule')  # Default
    
    @patch('ai_cli.resources.edit_resource', return_value=True)
    def test_add_and_list_rule(self, mock_edit):
        """Test adding and listing a rule."""
        # Test adding a rule
        with patch('rich.prompt.Prompt.ask', side_effect=["test_rule", "global"]):
            result = add_resource('rule')
            self.assertTrue(result)
        
        # Verify the rule was created
        rules = list_resources('rule', 'global')
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, 'test_rule')
    
    @patch('ai_cli.resources.edit_resource', return_value=True)
    def test_add_and_list_workflow(self, mock_edit):
        """Test adding and listing a workflow."""
        # Test adding a workflow
        with patch('rich.prompt.Prompt.ask', side_effect=["test_workflow", "global"]):
            result = add_resource('workflow')
            self.assertTrue(result)
        
        # Verify the workflow was created
        workflows = list_resources('workflow', 'global')
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0].name, 'test_workflow')
    
    @patch('ai_cli.resources.edit_resource', return_value=True)
    def test_add_and_list_profile(self, mock_edit):
        """Test adding and listing a profile with tool selection."""
        # Mock tool selection
        with patch('rich.prompt.Prompt.ask', side_effect=["test_profile", "test_tool", "global"]):
            result = add_resource('profile')
            self.assertTrue(result)
        
        # Verify the profile was created with the correct tool
        profiles = list_resources('profile', 'global')
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].name, 'test_profile')
        self.assertEqual(profiles[0].tool, 'test_tool')
    
    @patch('subprocess.run')
    def test_edit_resource(self, mock_run):
        """Test editing a resource."""
        # Create a test rule
        rule = MockRule(name="test_rule", content={"description": "Test rule"})
        self.content_manager.add_item(rule)
        
        # Mock the editor and file operations
        with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_temp_file"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            # Mock the file reading after edit
            with patch('builtins.open', unittest.mock.mock_open(read_data='description: Updated test rule')):
                # Call edit_resource
                result = edit_resource('rule', 'test_rule', 'global')
                self.assertTrue(result)
        
        # Verify the rule was updated
        updated_rule = self.content_manager.get_item('rule', 'test_rule')
        self.assertEqual(updated_rule.content['description'], 'Updated test rule')
    
    def test_remove_resource(self):
        """Test removing a resource."""
        # Create a test rule
        rule = MockRule(name="test_rule", content={"description": "Test rule"})
        self.content_manager.add_item(rule)
        
        # Mock the confirmation
        with patch('rich.prompt.Confirm.ask', return_value=True):
            result = remove_resource('rule', 'test_rule', 'global')
            self.assertTrue(result)
        
        # Verify the rule was removed
        self.assertIsNone(self.content_manager.get_item('rule', 'test_rule'))

if __name__ == '__main__':
    unittest.main()
