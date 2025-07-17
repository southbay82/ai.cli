import os
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from .config import config, GLOBAL_CONFIG_DIR, PROJECT_CONFIG_DIR_NAME, RESOURCE_DIRS

console = Console()

def list_resources(resource_type: str, scope: str = None):
    """List all resources of a given type and scope."""
    if scope is None:
        scope = "project" if config.project_config_path else "global"
    
    if scope == "project" and not config.project_config_path:
        console.print("[yellow]Not in a project directory. Showing global resources instead.[/yellow]")
        scope = "global"
    
    if scope == "global":
        resource_dir = GLOBAL_CONFIG_DIR / f"{resource_type}s"
    else:
        resource_dir = config.project_config_path.parent / f"{resource_type}s"
    
    if not resource_dir.exists():
        console.print(f"[yellow]No {resource_type} resources found in {scope} scope.[/yellow]")
        return []
    
    resources = [f.stem for f in resource_dir.glob("*.yml")]
    
    if not resources:
        console.print(f"[yellow]No {resource_type} resources found in {scope} scope.[/yellow]")
        return []
    
    # Display resources in a table
    table = Table(title=f"{resource_type.capitalize()} Resources ({scope} scope)")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    
    for resource in resources:
        table.add_row(resource, str(resource_dir / f"{resource}.yml"))
    
    console.print(table)
    return resources

def add_resource(resource_type: str):
    """Add a new resource of the specified type."""
    name = Prompt.ask(f"Enter a name for the new {resource_type}")
    scope = Prompt.ask("Scope", choices=["global", "project"], default="global")
    
    if scope == "project" and not config.project_config_path:
        console.print("[bold red]Error:[/bold red] Not in a project directory. No `.ai.cli` directory found.")
        return False
    
    if scope == "global":
        resource_dir = GLOBAL_CONFIG_DIR / f"{resource_type}s"
    else:
        resource_dir = config.project_config_path.parent / f"{resource_type}s"
    
    # Create the directory if it doesn't exist
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    resource_file = resource_dir / f"{name}.yml"
    
    if resource_file.exists():
        if not Confirm.ask(f"{resource_type.capitalize()} '{name}' already exists. Overwrite?"):
            console.print("Operation cancelled.")
            return False
    
    # Create a basic template
    template = f"# {resource_type.capitalize()}: {name}\n# Add your {resource_type} configuration here\n"
    
    try:
        with open(resource_file, 'w') as f:
            f.write(template)
        
        # Open the file in the default editor
        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, resource_file])
        
        console.print(f"[green]Successfully created {resource_type} '{name}' in {scope} scope.[/green]")
        return True
    except Exception as e:
        console.print(f"[bold red]Error creating {resource_type}: {str(e)}[/bold red]")
        return False

def remove_resource(resource_type: str):
    """Remove a resource of the specified type."""
    scope = Prompt.ask("Scope", choices=["global", "project"], default="global")
    
    if scope == "project" and not config.project_config_path:
        console.print("[bold red]Error:[/bold red] Not in a project directory. No `.ai.cli` directory found.")
        return False
    
    # List available resources
    resources = list_resources(resource_type, scope)
    if not resources:
        return False
    
    name = Prompt.ask(f"Enter the name of the {resource_type} to remove", choices=resources)
    
    if scope == "global":
        resource_dir = GLOBAL_CONFIG_DIR / f"{resource_type}s"
    else:
        resource_dir = config.project_config_path.parent / f"{resource_type}s"
    
    resource_file = resource_dir / f"{name}.yml"
    
    if not resource_file.exists():
        console.print(f"[bold red]Error:[/bold red] {resource_type.capitalize()} '{name}' not found in {scope} scope.")
        return False
    
    if Confirm.ask(f"Are you sure you want to delete {resource_type} '{name}'?"):
        try:
            resource_file.unlink()
            console.print(f"[green]Successfully removed {resource_type} '{name}' from {scope} scope.[/green]")
            return True
        except Exception as e:
            console.print(f"[bold red]Error removing {resource_type}: {str(e)}[/bold red]")
            return False
    
    console.print("Operation cancelled.")
    return False

def create_backup(resource_type: str):
    """Create a backup of a resource before editing."""
    # Implementation for creating backups
    # This is a placeholder - actual implementation would depend on your backup strategy
    pass

def edit_resource(resource_type: str):
    """Edit an existing resource of the specified type."""
    scope = Prompt.ask("Scope", choices=["global", "project"], default="global")
    
    if scope == "project" and not config.project_config_path:
        console.print("[bold red]Error:[/bold red] Not in a project directory. No `.ai.cli` directory found.")
        return False
    
    # List available resources
    resources = list_resources(resource_type, scope)
    if not resources:
        return False
    
    name = Prompt.ask(f"Enter the name of the {resource_type} to edit", choices=resources)
    
    if scope == "global":
        resource_dir = GLOBAL_CONFIG_DIR / f"{resource_type}s"
    else:
        resource_dir = config.project_config_path.parent / f"{resource_type}s"
    
    resource_file = resource_dir / f"{name}.yml"
    
    if not resource_file.exists():
        console.print(f"[bold red]Error:[/bold red] {resource_type.capitalize()} '{name}' not found in {scope} scope.")
        return False
    
    # Create a backup before editing
    create_backup(resource_type)
    
    # Open the file in the default editor
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, resource_file], check=True)
        console.print(f"[green]Successfully updated {resource_type} '{name}' in {scope} scope.[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error editing {resource_type}: {str(e)}[/bold red]")
        return False
