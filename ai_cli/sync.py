import os
import shutil
import git
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress

from .config import config, GLOBAL_CONFIG_DIR, PROJECT_CONFIG_DIR_NAME, RESOURCE_DIRS
from .core.content import ContentManager, Rule, Workflow, Profile
from .core.adapters import get_adapter

console = Console()

# Supported tools and their configuration directories
SUPPORTED_TOOLS = {
    'q-cli': {
        'config_dir': Path('~/.q').expanduser(),
        'description': 'Amazon Q CLI'
    },
    'windsurf': {
        'config_dir': Path('~/.windsurf').expanduser(),
        'description': 'Windsurf AI'
    },
    'gemini': {
        'config_dir': Path('~/.gemini').expanduser(),
        'description': 'Google Gemini'
    },
    'cursor': {
        'config_dir': Path('~/.cursor').expanduser(),
        'description': 'Cursor AI'
    }
}

def sync_tool(tool_name: str, content_manager: ContentManager) -> bool:
    """Synchronize content for a specific tool.
    
    Args:
        tool_name: Name of the tool to sync
        content_manager: Content manager instance
        
    Returns:
        bool: True if sync was successful, False otherwise
    """
    if tool_name not in SUPPORTED_TOOLS:
        console.print(f"[yellow]Warning:[/yellow] Unsupported tool: {tool_name}")
        return False
    
    tool_info = SUPPORTED_TOOLS[tool_name]
    tool_dir = tool_info['config_dir']
    
    try:
        # Create tool config directory if it doesn't exist
        tool_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the appropriate adapter for this tool
        adapter = get_adapter(tool_name, tool_dir)
        
        # Sync content using the adapter
        with console.status(f"[bold]Synchronizing {tool_info['description']}...") as status:
            adapter.sync(content_manager)
            
        console.print(f"[green]✓[/green] Synchronized {tool_info['description']} configuration")
        return True
        
    except Exception as e:
        console.print(f"[red]Error synchronizing {tool_name}: {str(e)}[/red]")
        return False

def sync_all():
    """Synchronize all resources and tool configurations.
    
    Returns:
        bool: True if sync was successful, False otherwise
    """
    # Initialize content manager
    content_manager = ContentManager(GLOBAL_CONFIG_DIR)
    
    # Create global config directory if it doesn't exist
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sync each supported tool
    results = {}
    with Progress() as progress:
        task = progress.add_task("[cyan]Synchronizing tools...", total=len(SUPPORTED_TOOLS))
        
        for tool_name in SUPPORTED_TOOLS:
            progress.update(task, description=f"[cyan]Synchronizing {tool_name}...")
            results[tool_name] = sync_tool(tool_name, content_manager)
            progress.update(task, advance=1)
    
    # Check if we're in a project directory
    project_ai_dir = Path.cwd() / ".ai.cli"
    if project_ai_dir.exists():
        config.project_config_path = project_ai_dir / "config.json"
        project_dir = project_ai_dir.parent
        console.print(f"\n[bold]Synchronizing project resources to {project_dir}...[/bold]")
        
        # Create project content manager
        project_content_manager = ContentManager(project_ai_dir)
        
        # Sync project-specific content
        for resource_dir in RESOURCE_DIRS:
            source_dir = GLOBAL_CONFIG_DIR / resource_dir
            dest_dir = project_ai_dir / resource_dir
            
            if not source_dir.exists():
                console.print(f"[yellow]Warning:[/yellow] Source directory not found: {source_dir}")
                continue
                
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files from source to destination
            for item in source_dir.glob('*'):
                if item.is_file():
                    shutil.copy2(item, dest_dir)
                elif item.is_dir():
                    dest_subdir = dest_dir / item.name
                    if not dest_subdir.exists():
                        shutil.copytree(item, dest_subdir)
        
        console.print("[bold green]✓ Project synchronization complete![/bold green]")
    else:
        console.print("[bold]Synchronizing global resources only...[/bold]")
    
    # Check for any failures
    failed_tools = [name for name, success in results.items() if not success]
    if failed_tools:
        console.print(f"[yellow]Warning:[/yellow] Failed to sync some tools: {', '.join(failed_tools)}")
        return False
    
    console.print("[bold green]✓ All tools synchronized successfully![/bold green]")
    return True

def sync_project():
    """Initialize a new project with AI CLI configuration.
    
    Returns:
        bool: True if project initialization was successful, False otherwise
    """
    cwd = Path.cwd()
    project_ai_dir = cwd / ".ai.cli"
    
    # Check if project already exists
    if project_ai_dir.exists():
        console.print(f"[yellow]Project already exists at {project_ai_dir}[/yellow]")
        return True
    
    console.print(f"[bold]Initializing new AI CLI project in {cwd}...[/bold]")
    
    try:
        # Create project directory structure
        project_ai_dir.mkdir()
        (project_ai_dir / "rules").mkdir()
        (project_ai_dir / "workflows").mkdir()
        (project_ai_dir / "profiles").mkdir()
        
        # Initialize project config
        config.project_config_path = project_ai_dir / "config.json"
        config.save_project_config()
        
        # Create basic project files
        readme_path = project_ai_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write("# AI CLI Project\n\n")
            f.write("This directory contains AI CLI configuration for your project.\n\n")
            f.write("- `rules/`: Project-specific rules\n")
            f.write("- `workflows/`: Project-specific workflows\n")
            f.write("- `profiles/`: Project-specific tool profiles\n")
        
        console.print(f"[green]✓ Project initialized in {project_ai_dir}[/green]")
        console.print("\nNext steps:")
        console.print("1. Add rules, workflows, and profiles to the respective directories")
        console.print("2. Run `ai-cli sync` to apply configurations to your tools")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error initializing project: {str(e)}[/red]")
        if project_ai_dir.exists():
            shutil.rmtree(project_ai_dir)
        return False

    console.print("[bold green]Project sync complete.[/bold green]")
