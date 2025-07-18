import os
import shutil
import git
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from .config import (
    config, GLOBAL_CONFIG_DIR, PROJECT_CONFIG_DIR_NAME, 
    CONTENT_DIR, RULES_DIR, GLOBAL_RULES_DIR, PROJECT_RULES_DIR,
    AMAZONQ_PROFILES_DIR, WINDSURF_WORKFLOWS_DIR, TOOL_CONFIGS
)
from .core.content import ContentManager
from .core.adapters import get_adapter

console = Console()

# Supported tools and their configuration directories
SUPPORTED_TOOLS = {
    'q-cli': {
        'config_dir': Path('~/.q').expanduser(),
        'description': 'Amazon Q CLI',
        'content_dirs': {
            'rules': AMAZONQ_PROFILES_DIR,
            'workflows': WINDSURF_WORKFLOWS_DIR,
            'profiles': AMAZONQ_PROFILES_DIR
        }
    },
    'windsurf': {
        'config_dir': Path('~/.windsurf').expanduser(),
        'description': 'Windsurf AI',
        'content_dirs': {
            'rules': GLOBAL_RULES_DIR,
            'workflows': WINDSURF_WORKFLOWS_DIR,
            'profiles': Path('~/.windsurf').expanduser()
        }
    },
    'gemini': {
        'config_dir': Path('~/.gemini').expanduser(),
        'description': 'Google Gemini',
        'content_dirs': {
            'rules': GLOBAL_RULES_DIR,
            'workflows': WINDSURF_WORKFLOWS_DIR,
            'profiles': Path('~/.gemini').expanduser()
        }
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
        
        # Create a progress bar
        with Progress(
            TextColumn(f"[bold blue]{tool_info['description']}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            console=console
        ) as progress:
            # Create a task for the sync operation
            task = progress.add_task("Syncing...", total=100)
            
            # Sync content using the adapter
            def progress_callback(progress_value: int, message: str = ""):
                progress.update(task, completed=progress_value, description=f"Syncing {message}")
            
            adapter.sync(content_manager, progress_callback)
            
            # Mark as complete
            progress.update(task, completed=100, description="[green]Done!")
        
        console.print(f"[green]✓[/green] Synchronized {tool_info['description']} configuration")
        return True
        
    except Exception as e:
        console.print(f"[red]Error synchronizing {tool_name}: {str(e)}[/red]")
        return False

def sync_content_dirs(source_dir: Path, dest_dir: Path, exclude: Set[str] = None) -> None:
    """Synchronize content between source and destination directories."""
    if exclude is None:
        exclude = set()
    
    # Ensure destination exists
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files and directories
    for item in source_dir.glob('*'):
        if item.name in exclude:
            continue
            
        dest_path = dest_dir / item.name
        
        if item.is_file():
            shutil.copy2(item, dest_path)
        elif item.is_dir():
            if not dest_path.exists():
                shutil.copytree(item, dest_path, dirs_exist_ok=True)


def sync_all():
    """Synchronize all resources and tool configurations.
    
    Returns:
        bool: True if sync was successful, False otherwise
    """
    # Initialize content manager with the content directory
    content_manager = ContentManager(CONTENT_DIR)
    
    # Create global config directory if it doesn't exist
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sync each supported tool
    results = {}
    with Progress(
        TextColumn("[bold blue]Synchronizing tools"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("", total=len(SUPPORTED_TOOLS))
        
        for i, tool_name in enumerate(SUPPORTED_TOOLS, 1):
            progress.update(task, description=f"Syncing {tool_name}...")
            results[tool_name] = sync_tool(tool_name, content_manager)
            progress.update(task, completed=i)
    
    # Check if we're in a project directory
    project_ai_dir = Path.cwd() / ".ai.cli"
    if project_ai_dir.exists():
        config.project_config_path = project_ai_dir / "config.json"
        project_dir = project_ai_dir.parent
        
        console.print("\n[bold]Synchronizing project resources...[/bold]")
        
        # Sync project-specific content from global to project
        for content_type in ['rules', 'workflows', 'profiles']:
            source_dir = CONTENT_DIR / content_type
            dest_dir = project_ai_dir / content_type
            
            if source_dir.exists():
                sync_content_dirs(source_dir, dest_dir)
        
        console.print("[bold green]✓ Project synchronization complete![/bold green]")
    
    # Check for any failures
    failed_tools = [name for name, success in results.items() if not success]
    if failed_tools:
        console.print(f"[yellow]Warning:[/yellow] Failed to sync some tools: {', '.join(failed_tools)}")
        return False
    
    console.print("\n[bold green]✓ All tools synchronized successfully![/bold green]")
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
        
        # Create content directories
        for content_type in ['rules', 'workflows', 'profiles']:
            (project_ai_dir / content_type).mkdir()
        
        # Initialize project config
        config.project_config_path = project_ai_dir / "config.json"
        
        # Create a basic project config
        project_config = {
            "name": project_ai_dir.parent.name,
            "content_dirs": {
                "rules": str(project_ai_dir / "rules"),
                "workflows": str(project_ai_dir / "workflows"),
                "profiles": str(project_ai_dir / "profiles")
            }
        }
        
        with open(config.project_config_path, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        # Create basic project files
        readme_path = project_ai_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write("# AI CLI Project\n\n")
            f.write("This directory contains AI CLI configuration for your project.\n\n")
            f.write("## Directory Structure\n")
            f.write("- `rules/`: Project-specific rules that override global rules\n")
            f.write("- `workflows/`: Project-specific workflows\n")
            f.write("- `profiles/`: Project-specific tool profiles\n\n")
            f.write("## Usage\n")
            f.write("1. Add your project-specific configurations to the appropriate directories\n")
            f.write("2. Run `ai-cli sync` to apply configurations to your tools\n")
        
        # Create .gitignore
        gitignore_path = project_ai_dir / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore everything in this directory\n*\n# Except these files\n!.gitignore\n!README.md\n!rules/\n!workflows/\n!profiles/\n")
        
        console.print(f"\n[green]✓ Project initialized in {project_ai_dir}[/green]")
        console.print("\nNext steps:")
        console.print("1. Add rules, workflows, and profiles to the respective directories")
        console.print("2. Run `ai-cli sync` to apply configurations to your tools")
        console.print("\nYour project configurations are now ready to be version controlled!")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Error initializing project: {str(e)}[/red]")
        if project_ai_dir.exists():
            shutil.rmtree(project_ai_dir)
        return False
