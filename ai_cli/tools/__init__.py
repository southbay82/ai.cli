"""Tool adapters for different AI tools."""
from pathlib import Path
from typing import Dict, Type, Optional

from ai_cli.core.content import ToolAdapter
from ai_cli.tools.qcli_adapter import QCLIAdapter
from ai_cli.tools.windsurf_adapter import WindsurfAdapter
from ai_cli.tools.gemini_adapter import GeminiAdapter

# Map of tool names to their adapter classes
TOOL_ADAPTERS: Dict[str, Type[ToolAdapter]] = {
    'q-cli': QCLIAdapter,
    'windsurf': WindsurfAdapter,
    'gemini': GeminiAdapter,
}

def get_tool_adapter(tool_name: str, config_dir: Optional[Path] = None) -> Optional[ToolAdapter]:
    """Get a tool adapter instance for the specified tool.
    
    Args:
        tool_name: Name of the tool to get an adapter for.
        config_dir: Optional base configuration directory. If not provided,
                   the default for each tool will be used.
                   
    Returns:
        Optional[ToolAdapter]: An instance of the appropriate adapter, or None if not found.
    """
    adapter_class = TOOL_ADAPTERS.get(tool_name.lower())
    if not adapter_class:
        return None
    
    return adapter_class(config_dir)

def get_supported_tools() -> Dict[str, Type[ToolAdapter]]:
    """Get a dictionary of supported tools and their adapter classes.
    
    Returns:
        Dict[str, Type[ToolAdapter]]: Dictionary mapping tool names to their adapter classes.
    """
    return TOOL_ADAPTERS.copy()
