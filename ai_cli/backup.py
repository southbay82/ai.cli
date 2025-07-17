import os
import shutil
import zipfile
import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress
from .config import GLOBAL_CONFIG_DIR, PROJECT_CONFIG_DIR_NAME, RESOURCE_DIRS

console = Console()

def create_backup(resource_type: str = None):
    """
    Create a backup of the specified resource type or all resources if none specified.
    
    Args:
        resource_type: Type of resource to backup (e.g., 'rule', 'workflow'). If None, backs up all resources.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = GLOBAL_CONFIG_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    if resource_type:
        backup_file = backup_dir / f"{resource_type}_{timestamp}.zip"
        resource_dirs = [(resource_type, GLOBAL_CONFIG_DIR / f"{resource_type}s")]
    else:
        backup_file = backup_dir / f"ai_cli_backup_{timestamp}.zip"
        resource_dirs = [(rt, GLOBAL_CONFIG_DIR / f"{rt}s") for rt in RESOURCE_DIRS]
    
    try:
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for rt, resource_dir in resource_dirs:
                if resource_dir.exists():
                    for root, _, files in os.walk(resource_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(GLOBAL_CONFIG_DIR)
                            zipf.write(file_path, arcname)
        
        console.print(f"[green]Backup created successfully: {backup_file}[/green]")
        return str(backup_file)
    except Exception as e:
        console.print(f"[red]Error creating backup: {str(e)}[/red]")
        return None

def restore_backup(backup_path: str = None):
    """
    Restore resources from a backup file.
    
    Args:
        backup_path: Path to the backup file. If None, prompts user to select from available backups.
    """
    if not backup_path:
        backups = list(GLOBAL_CONFIG_DIR.glob("backups/*.zip"))
        if not backups:
            console.print("[yellow]No backup files found.[/yellow]")
            return False
            
        backup = Prompt.ask(
            "Select a backup to restore",
            choices=[str(b) for b in backups],
            default=str(backups[0])
        )
        backup_path = Path(backup)
    else:
        backup_path = Path(backup_path)
        if not backup_path.exists():
            console.print(f"[red]Backup file not found: {backup_path}[/red]")
            return False
    
    if not Confirm.ask(f"Are you sure you want to restore from {backup_path.name}? This will overwrite existing files."):
        console.print("Restore cancelled.")
        return False
    
    try:
        # Create a temporary directory for extraction
        temp_dir = GLOBAL_CONFIG_DIR / "temp_restore"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Extract the backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Restore each resource type
        restored = 0
        for item in temp_dir.iterdir():
            if item.is_dir() and item.name.endswith('s'):  # e.g., 'rules', 'workflows'
                resource_type = item.name[:-1]  # Remove 's' to get singular form
                target_dir = GLOBAL_CONFIG_DIR / item.name
                
                # Remove existing directory if it exists
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                # Copy the restored files
                shutil.copytree(item, target_dir)
                restored += 1
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        if restored > 0:
            console.print(f"[green]Successfully restored {restored} resource types from backup.[/green]")
            return True
        else:
            console.print("[yellow]No valid resources found in backup.[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error restoring backup: {str(e)}[/red]")
        return False

def list_backups():
    """List all available backups with details."""
    backup_dir = GLOBAL_CONFIG_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)  # Ensure the directory exists
    
    backups = sorted(backup_dir.glob("*.zip"), key=os.path.getmtime, reverse=True)
    
    if not backups:
        console.print("[yellow]No backup files found.[/yellow]")
        return []
    
    table = Table(title="Available Backups", show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=4, justify="right")
    table.add_column("Name", style="green", min_width=30)
    table.add_column("Size", style="magenta", width=12, justify="right")
    table.add_column("Created", style="blue", width=20)
    table.add_column("Type", style="yellow", width=10)
    
    for idx, backup in enumerate(backups, 1):
        size = backup.stat().st_size
        created = datetime.datetime.fromtimestamp(backup.stat().st_ctime)
        
        # Determine backup type from filename
        name = backup.stem
        if name.startswith("ai_cli_backup_"):
            btype = "Full"
        else:
            btype = name.split('_')[0].capitalize()
        
        table.add_row(
            str(idx),
            backup.name,
            f"{size/1024/1024:.1f} MB",
            created.strftime("%Y-%m-%d %H:%M"),
            btype
        )
    
    console.print(table)
    return backups
