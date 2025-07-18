"""Unit tests for tool adapters."""
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from ai_cli.core.content import ContentType, Rule, Workflow, Profile
from ai_cli.tools import (
    get_tool_adapter, get_supported_tools,
    QCLIAdapter, WindsurfAdapter, GeminiAdapter
)

@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for testing tool adapters."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

class TestQCLIAdapter:
    """Test cases for QCLIAdapter."""
    
    def test_init_creates_directories(self, temp_config_dir):
        """Test that QCLIAdapter creates required directories."""
        # When
        adapter = QCLIAdapter(temp_config_dir)
        
        # Then
        assert (temp_config_dir / 'profiles').exists()
        assert (temp_config_dir / 'rules').exists()
        assert (temp_config_dir / 'workflows').exists()
    
    def test_sync_profile(self, temp_config_dir):
        """Test syncing a profile to Q CLI."""
        # Given
        adapter = QCLIAdapter(temp_config_dir)
        profile = Profile(
            "test_profile", 
            "q-cli", 
            {"api_key": "test_key", "region": "us-west-2"}
        )
        
        # When
        result = adapter.sync_item(profile)
        
        # Then
        assert result is True
        profile_path = temp_config_dir / 'profiles' / 'test_profile.yaml'
        assert profile_path.exists()
        
        # Verify the content
        with open(profile_path, 'r') as f:
            import yaml
            content = yaml.safe_load(f)
            assert content['name'] == 'test_profile'
            assert content['config']['api_key'] == 'test_key'
            assert content['config']['region'] == 'us-west-2'
    
    def test_list_profiles(self, temp_config_dir):
        """Test listing Q CLI profiles."""
        # Given
        adapter = QCLIAdapter(temp_config_dir)
        profile_path = temp_config_dir / 'profiles' / 'test_profile.yaml'
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(profile_path, 'w') as f:
            import yaml
            yaml.dump({
                'name': 'test_profile',
                'config': {'api_key': 'test_key'}
            }, f)
        
        # When
        profiles = adapter.list_profiles()
        
        # Then
        assert 'test_profile' in profiles
        assert profiles['test_profile']['api_key'] == 'test_key'

class TestWindsurfAdapter:
    """Test cases for WindsurfAdapter."""
    
    def test_init_creates_directories(self, temp_config_dir):
        """Test that WindsurfAdapter creates required directories."""
        # When
        adapter = WindsurfAdapter(temp_config_dir)
        
        # Then
        assert (temp_config_dir / 'personas').exists()
        assert (temp_config_dir / 'workflows').exists()
    
    def test_sync_persona(self, temp_config_dir):
        """Test syncing a rule as a Windsurf persona."""
        # Given
        adapter = WindsurfAdapter(temp_config_dir)
        rule = Rule(
            "test_persona",
            {"description": "A test persona", "behavior": "helpful"}
        )
        
        # When
        result = adapter.sync_item(rule)
        
        # Then
        assert result is True
        persona_path = temp_config_dir / 'personas' / 'test_persona.json'
        assert persona_path.exists()
        
        # Verify the content
        with open(persona_path, 'r') as f:
            content = json.load(f)
            assert content['name'] == 'test_persona'
            assert content['description'] == 'A test persona'
            assert content['config']['behavior'] == 'helpful'
    
    def test_list_personas(self, temp_config_dir):
        """Test listing Windsurf personas."""
        # Given
        adapter = WindsurfAdapter(temp_config_dir)
        persona_path = temp_config_dir / 'personas' / 'test_persona.json'
        persona_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(persona_path, 'w') as f:
            json.dump({
                'name': 'test_persona',
                'description': 'A test persona',
                'config': {'behavior': 'helpful'}
            }, f)
        
        # When
        personas = adapter.list_personas()
        
        # Then
        assert 'test_persona' in personas
        assert personas['test_persona']['config']['behavior'] == 'helpful'

class TestGeminiAdapter:
    """Test cases for GeminiAdapter."""
    
    def test_init_creates_directories_and_config(self, temp_config_dir):
        """Test that GeminiAdapter creates required directories and config file."""
        # When
        adapter = GeminiAdapter(temp_config_dir)
        
        # Then
        assert (temp_config_dir / 'prompts').exists()
        assert (temp_config_dir / 'config.json').exists()
        
        # Verify default config
        with open(temp_config_dir / 'config.json', 'r') as f:
            config = json.load(f)
            assert 'api_key' in config
            assert config['model'] == 'gemini-pro'
    
    def test_sync_prompt_template(self, temp_config_dir):
        """Test syncing a prompt template to Gemini."""
        # Given
        adapter = GeminiAdapter(temp_config_dir)
        rule = Rule(
            "test_template",
            {"template": "Translate this to French: {text}"}
        )
        
        # When
        result = adapter.sync_item(rule)
        
        # Then
        assert result is True
        prompt_path = temp_config_dir / 'prompts' / 'test_template.txt'
        assert prompt_path.exists()
        
        # Verify the content
        with open(prompt_path, 'r') as f:
            assert f.read() == "Translate this to French: {text}"
        
        # Verify config was updated
        with open(temp_config_dir / 'config.json', 'r') as f:
            config = json.load(f)
            assert 'test_template' in config['prompt_templates']
            assert str(prompt_path) in config['prompt_templates']['test_template']
    
    def test_get_prompt_template(self, temp_config_dir):
        """Test getting a prompt template."""
        # Given
        adapter = GeminiAdapter(temp_config_dir)
        prompt_path = temp_config_dir / 'prompts' / 'test_template.txt'
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(prompt_path, 'w') as f:
            f.write("Translate this to French: {text}")
        
        # Update config
        with open(temp_config_dir / 'config.json', 'r+') as f:
            config = json.load(f)
            config['prompt_templates'] = {'test_template': str(prompt_path)}
            f.seek(0)
            json.dump(config, f)
            f.truncate()
        
        # When
        template = adapter.get_prompt_template('test_template')
        
        # Then
        assert template == "Translate this to French: {text}"

class TestToolFactory:
    """Test cases for the tool factory functions."""
    
    def test_get_supported_tools(self):
        """Test getting supported tools."""
        # When
        tools = get_supported_tools()
        
        # Then
        assert 'q-cli' in tools
        assert 'windsurf' in tools
        assert 'gemini' in tools
        assert tools['q-cli'] == QCLIAdapter
        assert tools['windsurf'] == WindsurfAdapter
        assert tools['gemini'] == GeminiAdapter
    
    def test_get_tool_adapter(self, temp_config_dir):
        """Test getting a tool adapter instance."""
        # When
        qcli_adapter = get_tool_adapter('q-cli', temp_config_dir)
        windsurf_adapter = get_tool_adapter('windsurf', temp_config_dir)
        gemini_adapter = get_tool_adapter('gemini', temp_config_dir)
        
        # Then
        assert isinstance(qcli_adapter, QCLIAdapter)
        assert isinstance(windsurf_adapter, WindsurfAdapter)
        assert isinstance(gemini_adapter, GeminiAdapter)
        assert qcli_adapter.config_dir == temp_config_dir
        assert windsurf_adapter.config_dir == temp_config_dir
        assert gemini_adapter.config_dir == temp_config_dir
    
    def test_get_unknown_tool_adapter(self):
        """Test getting an adapter for an unknown tool."""
        # When
        adapter = get_tool_adapter('unknown_tool')
        
        # Then
        assert adapter is None
