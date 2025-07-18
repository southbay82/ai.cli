import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Any, Set
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress

from .config import config, GLOBAL_CONFIG_DIR, PROJECT_CONFIG_DIR_NAME, RESOURCE_DIRS
from .core.content import (
    ContentType, 
    ContentItem, 
    Rule, 
    Workflow, 
    Profile, 
    ContentManager,
    get_content_manager as get_core_content_manager
)
from .core.adapters import (
    ToolAdapter,
    get_tool_adapter,
    get_supported_tools
)

console = Console()

def get_content_type(resource_type: str) -> ContentType:
    """Map resource type string to ContentType enum."""
    type_map = {
        'rule': ContentType.RULE,
        'workflow': ContentType.WORKFLOW,
        'profile': ContentType.PROFILE,
        'global_rule': ContentType.GLOBAL_RULE,
        'project_rule': ContentType.PROJECT_RULE,
        'amazonq_profile': ContentType.AMAZONQ_PROFILE,
        'windsurf_workflow': ContentType.WINDSURF_WORKFLOW
    }
    return type_map.get(resource_type.lower(), ContentType.RULE)

def get_resource_manager(scope: str = None) -> ContentManager:
    """Get the appropriate content manager based on scope."""
    if scope is None:
        scope = "project" if config.project_config_path else "global"
    
    if scope == "project" and not config.project_config_path:
        console.print("[yellow]Not in a project directory. Using global scope instead.[/yellow]")
        scope = "global"
    
    base_dir = GLOBAL_CONFIG_DIR if scope == "global" else config.project_config_path.parent
    return get_core_content_manager(base_dir)

def list_resources(resource_type: str, scope: str = None, tool: str = None):
    """List all resources of a given type and scope.
    
    Args:
        resource_type: Type of resource to list (e.g., 'rule', 'workflow', 'profile').
        scope: Scope of resources ('global' or 'project').
        tool: Optional tool name to filter resources by tool.
    """
    content_type = get_content_type(resource_type)
    content_manager = get_resource_manager(scope)
    
    # List all items of the specified type
    items = content_manager.list_items(content_type)
    
    # Filter by tool if specified
    if tool:
        items = [item for item in items if hasattr(item, 'tool') and item.tool == tool]
    
    if not items:
        scope_str = scope or "current"
        tool_str = f" for tool '{tool}'" if tool else ""
        console.print(f"[yellow]No {resource_type} resources found in {scope_str} scope{tool_str}.[/yellow]")
        return []
    
    # Display resources in a table
    table = Table(title=f"{resource_type.capitalize()} Resources ({scope or 'current'} scope)")
    table.add_column("Name", style="cyan")
    table.add_column("Tool", style="magenta")
    table.add_column("Path", style="green")
    
    for item in items:
        tool_name = getattr(item, 'tool', 'N/A')
        path = str(item.path) if item.path else "N/A"
        table.add_row(item.name, tool_name, path)
    
    console.print(table)
    return items

def add_resource(resource_type: str, scope: str = None):
    """Add a new resource of the specified type.
    
    Args:
        resource_type: Type of resource to add (e.g., 'rule', 'workflow', 'profile').
        scope: Scope of the resource ('global' or 'project').
    """
    print(f"[DEBUG] add_resource called with resource_type={resource_type}, scope={scope}")
    content_type = get_content_type(resource_type)
    print(f"[DEBUG] content_type={content_type}")
    
    # Determine scope if not provided
    if scope is None:
        print("[DEBUG] Scope not provided, determining scope...")
        scope = "project" if config.project_config_path else "global"
        if scope == "project" and not config.project_config_path:
            console.print("[yellow]Not in a project directory. Adding to global scope instead.[/yellow]")
            scope = "global"
    print(f"[DEBUG] Using scope: {scope}")
    
    # Get the appropriate content manager
    print("[DEBUG] Getting content manager...")
    content_manager = get_resource_manager(scope)
    print(f"[DEBUG] Got content manager: {content_manager}")
    
    # Get resource name and tool (if applicable)
    print("[DEBUG] Prompting for resource name...")
    name = Prompt.ask(f"Enter a name for the new {resource_type}")
    print(f"[DEBUG] Got resource name: {name}")
    
    # For profiles, ask which tool this profile is for
    tool = None
    if content_type in [ContentType.PROFILE, ContentType.AMAZONQ_PROFILE]:
        print("[DEBUG] Getting supported tools for profile...")
        supported_tools = list(get_supported_tools().keys())
        print(f"[DEBUG] Supported tools: {supported_tools}")
        if not supported_tools:
            error_msg = "[bold red]Error:[/bold red] No supported tools found."
            print(f"[DEBUG] {error_msg}")
            console.print(error_msg)
            return False
            
        print("[DEBUG] Prompting for tool selection...")
        tool = Prompt.ask(
            f"Which tool is this {resource_type} for?",
            choices=supported_tools,
            default=supported_tools[0]
        )
        print(f"[DEBUG] Selected tool: {tool}")
    
    # Create a basic template based on content type
    print("[DEBUG] Creating content template...")
    if content_type in [ContentType.RULE, ContentType.GLOBAL_RULE, ContentType.PROJECT_RULE]:
        content = {
            "description": f"{resource_type.capitalize()} for {name}",
            "conditions": [],
            "actions": []
        }
    elif content_type in [ContentType.WORKFLOW, ContentType.WINDSURF_WORKFLOW]:
        content = {
            "description": f"{resource_type.capitalize()} for {name}",
            "steps": []
        }
    elif content_type in [ContentType.PROFILE, ContentType.AMAZONQ_PROFILE]:
        content = {
            "description": f"{tool} profile for {name}",
            "config": {}
        }
    else:
        content = {"description": f"{resource_type.capitalize()} for {name}"}
    print(f"[DEBUG] Created content: {content}")
    
    # Create the appropriate content item
    print("[DEBUG] Creating content item...")
    try:
        if content_type in [ContentType.RULE, ContentType.GLOBAL_RULE, ContentType.PROJECT_RULE]:
            item = Rule(name=name, content=content)
        elif content_type in [ContentType.WORKFLOW, ContentType.WINDSURF_WORKFLOW]:
            item = Workflow(name=name, content=content)
        elif content_type in [ContentType.PROFILE, ContentType.AMAZONQ_PROFILE]:
            item = Profile(name=name, tool=tool, content=content)
        else:
            item = ContentItem(name=name, content=content, content_type=content_type)
        print(f"[DEBUG] Created item: {item}")
    except Exception as e:
        print(f"[DEBUG] Error creating item: {str(e)}")
        raise
    
    # Save the item
    print("[DEBUG] Saving item to content manager...")
    try:
        print("[DEBUG] Calling content_manager.add_item...")
        content_manager.add_item(item, overwrite=True)
        success_msg = f"[green]Successfully created {resource_type} '{name}' in {scope} scope.[/green]"
        print(f"[DEBUG] {success_msg}")
        console.print(success_msg)
        
        # Open for editing
        print("[DEBUG] Calling edit_resource...")
        result = edit_resource(resource_type, name, scope)
        print(f"[DEBUG] edit_resource returned: {result}")
        return True
    except Exception as e:
        error_msg = f"[bold red]Error creating {resource_type}: {str(e)}[/bold red]"
        print(f"[DEBUG] {error_msg}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        console.print(error_msg)
        return False

def remove_resource(resource_type: str, name: str = None, scope: str = None):
    """Remove a resource of the specified type.
    
    Args:
        resource_type: Type of resource to remove.
        name: Name of the resource to remove. If not provided, will prompt.
        scope: Scope of the resource ('global' or 'project').
    """
    content_type = get_content_type(resource_type)
    content_manager = get_resource_manager(scope)
    
    # List available resources if name not provided
    if name is None:
        items = list_resources(resource_type, scope)
        if not items:
            return False
        
        # Create a list of choices with name and tool (if applicable)
        choices = []
        for item in items:
            tool_str = f" ({getattr(item, 'tool', '')})" if hasattr(item, 'tool') else ""
            choices.append(f"{item.name}{tool_str}")
        
        # Prompt user to select a resource to delete
        selected = Prompt.ask(
            f"Select {resource_type} to remove",
            choices=choices,
            show_choices=True
        )
        
        # Extract the name from the selection (remove tool part if present)
        name = selected.split(" ")[0] if " " in selected else selected
    
    # Confirm deletion
    if not Confirm.ask(f"Are you sure you want to delete {resource_type} '{name}'?"):
        console.print("Operation cancelled.")
        return False
    
    # Delete the resource
    try:
        if content_manager.delete_item(content_type, name):
            console.print(f"[green]Successfully removed {resource_type} '{name}'.[/green]")
            return True
        else:
            console.print(f"[yellow]{resource_type.capitalize()} '{name}' not found.[/yellow]")
            return False
    except Exception as e:
        console.print(f"[bold red]Error removing {resource_type}: {str(e)}[/bold red]")
        return False

def create_backup(resource_type: str):
    """Create a backup of a resource before editing."""
    # Implementation for creating backups
    # This is a placeholder - actual implementation would depend on your backup strategy
    pass

def edit_resource(resource_type: str, name: str = None, scope: str = None):
    """Edit an existing resource of the specified type.
    
    Args:
        resource_type: Type of resource to edit.
        name: Name of the resource to edit. If not provided, will prompt.
        scope: Scope of the resource ('global' or 'project').
    """
    content_type = get_content_type(resource_type)
    content_manager = get_resource_manager(scope)
    
    # List available resources if name not provided
    if name is None:
        items = list_resources(resource_type, scope)
        if not items:
            return False
        
        # Create a list of choices with name and tool (if applicable)
        choices = []
        for item in items:
            tool_str = f" ({getattr(item, 'tool', '')})" if hasattr(item, 'tool') else ""
            choices.append(f"{item.name}{tool_str}")
        
        # Prompt user to select a resource to edit
        selected = Prompt.ask(
            f"Select {resource_type} to edit",
            choices=choices,
            show_choices=True
        )
        
        # Extract the name from the selection (remove tool part if present)
        name = selected.split(" ")[0] if " " in selected else selected
    
    # Get the item to edit
    item = content_manager.get_item(content_type, name)
    if not item:
        console.print(f"[bold red]Error:[/bold red] {resource_type.capitalize()} '{name}' not found.")
        return False
    
    # Create a temporary file for editing
    import tempfile
    import yaml
    
    with tempfile.NamedTemporaryFile(suffix='.yml', mode='w+', delete=False) as tmp:
        # Convert content to YAML and write to temp file
        yaml.dump(item.content, tmp, default_flow_style=False, sort_keys=False)
        tmp_path = tmp.name
    
    try:
        # Open the file in the default editor
        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, tmp_path], check=True)
        
        # Read the updated content
        with open(tmp_path, 'r') as f:
            updated_content = yaml.safe_load(f) or {}
        
        # Update the item
        item.content = updated_content
        content_manager.add_item(item, overwrite=True)
        
        console.print(f"[green]Successfully updated {resource_type} '{name}'.[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error editing {resource_type}: {str(e)}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error updating {resource_type}: {str(e)}[/bold red]")
        return False
    finally:
        # Clean up the temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass
