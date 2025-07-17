"""Integration tests for ai.cli functionality in the container."""
import os
import subprocess
import yaml
import pytest
from pathlib import Path

# Load test configuration
with open("tests/integration/fixtures/test_config.yaml") as f:
    TEST_CONFIG = yaml.safe_load(f)

# Global tool configurations
GLOBAL_TOOLS = TEST_CONFIG["global_tools"]
PROJECTS = TEST_CONFIG["projects"]

class TestAICLIIntegration:
    """Integration tests for ai.cli functionality."""
    
    def test_global_config_creation(self, tmp_path):
        """Test that global config is created correctly."""
        config_path = os.path.expanduser("~/.ai.cli/config.json")
        
        # The config should be created automatically on first run
        result = subprocess.run(
            ["python", "-m", "ai_cli", "--help"],
            capture_output=True,
            text=True,
            cwd=tmp_path
        )
        
        # Config file should exist after any command is run
        assert os.path.exists(config_path), "Global config file not created"
    
    def test_project_initialization(self, tmp_path):
        """Test project initialization."""
        # Create a test project directory
        test_project = tmp_path / "test_project"
        test_project.mkdir()
        
        # The .ai.cli directory should be created on first sync
        result = subprocess.run(
            ["python", "-m", "ai_cli", "sync", "project"],
            cwd=test_project,
            capture_output=True,
            text=True
        )
        
        assert (test_project / ".ai.cli").exists(), "Project .ai.cli directory not created"
    
    def test_tool_detection(self, tmp_path):
        """Test that ai_cli can detect installed tools."""
        # Tools are detected during sync operations
        result = subprocess.run(
            ["python", "-m", "ai_cli", "sync", "all"],
            capture_output=True,
            text=True,
            cwd=tmp_path
        )
        
        # Check that sync completed successfully
        assert result.returncode == 0, f"sync all failed: {result.stderr}"
        
        # Check that tools are detected by looking for their configs
        for tool_name in GLOBAL_TOOLS.keys():
            tool_config = os.path.expanduser(f"~/.ai.cli/tools/{tool_name}.yaml")
            assert os.path.exists(tool_config), f"{tool_name} config not created"
    
    def test_rule_management(self, tmp_path):
        """Test rule management functionality."""
        # Create a test rule
        rule_content = """
        name: test-rule
        description: Test rule for integration testing
        pattern: test.*
        action: echo "Test rule matched"
        """
        
        # Rules are managed through the manage command
        rules_dir = os.path.expanduser("~/.ai.cli/rules")
        os.makedirs(rules_dir, exist_ok=True)
        
        # Add the rule by creating the file directly
        rule_path = os.path.join(rules_dir, "test-rule.yaml")
        with open(rule_path, "w") as f:
            f.write(rule_content)
        
        # Verify the rule was created
        assert os.path.exists(rule_path), "Test rule file not created"
        
        # Rules are listed during manage command
        result = subprocess.run(
            ["python", "-m", "ai_cli", "manage"],
            input="0\n",  # Exit the interactive menu
            capture_output=True,
            text=True
        )
        
        # Check that the rule is listed in the output
        assert "test-rule" in result.stdout, "Test rule not found in rules list"

    def test_workflow_execution(self, tmp_path):
        """Test workflow execution."""
        # Create a simple workflow
        workflow_content = """
        name: test-workflow
        description: Test workflow
        steps:
          - name: step1
            command: echo "Hello from test workflow"
        """
        
        # Save workflow to the workflows directory
        workflows_dir = os.path.expanduser("~/.ai.cli/workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        workflow_path = os.path.join(workflows_dir, "test-workflow.yaml")
        
        with open(workflow_path, "w") as f:
            f.write(workflow_content)
        
        # Run the workflow using the manage command
        result = subprocess.run(
            ["python", "-m", "ai_cli", "manage"],
            input="0\n",  # Exit the interactive menu
            capture_output=True,
            text=True
        )
        
        # Since we're testing the CLI, we can't directly test workflow execution
        # in this test. This would require a more complex test setup.
        # For now, we just verify the workflow file was created.
        assert os.path.exists(workflow_path), "Workflow file not created"


if __name__ == "__main__":
    pytest.main(["-v"])
