"""Test configuration and fixtures for ai-cli tests."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock the config module before any other imports
class MockConfig:
    HOME = Path.home()
    GLOBAL_CONFIG_DIR = HOME / ".ai.cli"
    PROJECT_CONFIG_DIR_NAME = ".ai.cli"
    
    # Define resource directories
    RESOURCE_DIRS = {
        'rules': 'rules',
        'workflows': 'workflows',
        'profiles': 'profiles',
    }
    
    class Config:
        def __init__(self):
            self.project_config_path = None
    
    config = Config()

# Apply the mock config
sys.modules['ai_cli.config'] = MockConfig

# Mock the adapters module
sys.modules['ai_cli.core.adapters'] = MagicMock()
sys.modules['ai_cli.core.adapters'].ToolAdapter = MagicMock()

# Import the real content module
import ai_cli.core.content

# Don't mock the content module - use the real implementations
# This ensures all classes like ContentManager, Rule, etc. are the real implementations
sys.modules['ai_cli.core.content'] = ai_cli.core.content
