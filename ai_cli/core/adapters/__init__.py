"""Tool adapters for different AI tools."""
from pathlib import Path
from typing import Dict, Type
from ..core.content import ToolAdapter

# Import all adapters here
from .q_cli import QCLIAdapter
from .windsurf import WindsurfAdapter
from .gemini import GeminiAdapter

# Map tool names to their adapter classes
ADAPTERS: Dict[str, Type[ToolAdapter]] = {
    'q-cli': QCLIAdapter,
    'windsurf': WindsurfAdapter,
    'gemini': GeminiAdapter,
}

def get_adapter(tool_name: str, config_dir: Path) -> ToolAdapter:
    """Get an adapter for the specified tool.
    
    Args:
        tool_name: Name of the tool (e.g., 'q-cli', 'windsurf', 'gemini')
        config_dir: Base configuration directory for the tool
        
    Returns:
        An instance of the appropriate adapter class
        
    Raises:
        ValueError: If no adapter is available for the specified tool
    """
    adapter_class = ADAPTERS.get(tool_name.lower())
    if not adapter_class:
        raise ValueError(f"No adapter available for tool: {tool_name}")
    return adapter_class(tool_name, config_dir)
