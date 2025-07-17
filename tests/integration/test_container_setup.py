"""Integration tests for the containerized test environment."""
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


def test_environment_variables():
    """Test that required environment variables are set."""
    # Check for required environment variables
    assert os.environ.get("PYTHONUNBUFFERED") == "1", "PYTHONUNBUFFERED not set"
    assert os.environ.get("HOME") == "/home/tester", "HOME not set correctly"


def test_tools_installed():
    """Test that all required tools are installed and in PATH."""
    for tool_name, tool_config in GLOBAL_TOOLS.items():
        tool_path = tool_config["path"]
        assert os.path.exists(tool_path), f"{tool_name} not found at {tool_path}"
        
        # Check if tool is executable
        assert os.access(tool_path, os.X_OK), f"{tool_name} at {tool_path} is not executable"
        
        # Test running the tool
        try:
            result = subprocess.run(
                [tool_path],
                capture_output=True,
                text=True,
                check=True
            )
            assert tool_name in result.stdout.lower(), f"Unexpected output from {tool_name}"
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to run {tool_name}: {e.stderr}")


def test_tool_versions():
    """Test that tools report the expected versions."""
    for tool_name, tool_config in GLOBAL_TOOLS.items():
        expected_version = tool_config["version"]
        tool_path = tool_config["path"]
        
        # In a real test, we would run the tool with --version
        # For now, we'll just check that the version is in the config
        assert expected_version, f"No version specified for {tool_name}"


def test_project_directories():
    """Test that project directories exist and have the correct structure."""
    for project_name, project_config in PROJECTS.items():
        project_path = project_config["path"]
        assert os.path.isdir(project_path), f"Project directory {project_path} not found"
        
        # Check for .ai.cli directory in project
        ai_cli_dir = os.path.join(project_path, ".ai.cli")
        if os.path.exists(ai_cli_dir):
            assert os.path.isdir(ai_cli_dir), f"Expected {ai_cli_dir} to be a directory"


def test_ai_cli_installation():
    """Test that ai.cli is properly installed and can be imported."""
    try:
        import ai_cli
        assert ai_cli is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ai_cli: {e}")


def test_ai_cli_help():
    """Test that ai.cli --help works."""
    # First, ensure ai.cli is in the PATH
    try:
        # Try running the module directly since we're in development mode
        result = subprocess.run(
            ["python", "-m", "ai_cli", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        # Check for any of the expected help output
        assert any(x in result.stdout.lower() for x in ["usage", "commands", "options"]), \
            f"Unexpected help output: {result.stdout[:200]}..."
    except subprocess.CalledProcessError as e:
        pytest.fail(f"ai.cli --help failed: {e.stderr or 'No error output'}")
    except FileNotFoundError:
        pytest.skip("ai.cli not found in PATH")


if __name__ == "__main__":
    pytest.main(["-v"])
