import argparse
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from .config import config
from .sync import sync_all, sync_project
from .resources import list_resources, add_resource, remove_resource, edit_resource
from .backup import restore_backup, list_backups

class Menu:
    def __init__(self):
        self.console = Console()
        self.prompt = Prompt()
        self.running = True

    def display_menu(self):
        self.console.print("\n[bold]AI CLI Menu[/bold]")
        self.console.print("1. Sync all resources")
        self.console.print("2. Sync project resources")
        self.console.print("3. Manage resources")
        self.console.print("4. Backup operations")
        self.console.print("0. Exit")

    def handle_choice(self, choice):
        if choice == "1":
            sync_all()
        elif choice == "2":
            sync_project()
        elif choice == "3":
            self.manage_resources()
        elif choice == "4":
            self.backup_operations()
        elif choice == "0":
            self.running = False
        else:
            self.console.print("[red]Invalid choice. Please try again.[/red]")

    def manage_resources(self, non_interactive=False):
        """Display resource management menu and handle user input.
        
        Args:
            non_interactive (bool): If True, only list rules and return
        """
        # In non-interactive mode, just list the rules and return
        if non_interactive:
            rules_dir = os.path.expanduser("~/.ai.cli/rules")
            if os.path.exists(rules_dir):
                rules = [f"- {f.stem}" for f in Path(rules_dir).glob("*.yaml")]
                if rules:
                    self.console.print("\n[bold]Available Rules:[/bold]")
                    self.console.print("\n".join(rules))
                    return True
            return False
            
        # Interactive mode - show the menu
        while True:
            self.console.print("\n[bold]Resource Management[/bold]")
            self.console.print("1. List rules")
            self.console.print("2. Add rule")
            self.console.print("3. Edit rule")
            self.console.print("4. Remove rule")
            self.console.print("0. Back to main menu")
            
            choice = self.prompt.ask("\nChoose an option", choices=["0", "1", "2", "3", "4"])
            
            if choice == "1":
                rules = list_resources("rule")
                if not rules:
                    self.console.print("[yellow]No rules found.[/yellow]")
            elif choice == "2":
                add_resource("rule")
            elif choice == "3":
                edit_resource("rule")
            elif choice == "4":
                remove_resource("rule")
            elif choice == "0":
                break

    def backup_operations(self):
        self.console.print("\n[bold]Backup Operations[/bold]")
        list_backups()
        # Add more backup operations as needed

    def run(self):
        while self.running:
            self.display_menu()
            choice = self.prompt.ask("\nEnter your choice")
            self.handle_choice(choice)

def main():
    parser = argparse.ArgumentParser(description="AI CLI - Manage AI tools and resources")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Synchronize resources")
    sync_subparsers = sync_parser.add_subparsers(dest="sync_command", help="Sync subcommands")
    
    sync_all_parser = sync_subparsers.add_parser("all", help="Sync all resources")
    sync_project_parser = sync_subparsers.add_parser("project", help="Sync project resources")
    
    # Manage command
    manage_parser = subparsers.add_parser("manage", help="Manage resources")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup operations")
    backup_subparsers = backup_parser.add_subparsers(dest="action", help="Backup actions")
    
    backup_list_parser = backup_subparsers.add_parser("list", help="List available backups")
    backup_restore_parser = backup_subparsers.add_parser("restore", help="Restore from backup")
    
    args, unknown = parser.parse_known_args()
    console = Console()

    if args.command == "sync":
        if args.sync_command == "all":
            sync_all()
        elif args.sync_command == "project":
            sync_project()
        else:
            console.print("[yellow]Please specify a sync command (all/project)[/yellow]")
            parser.print_help()
    elif args.command == "manage":
        menu = Menu()
        # Check if we're running in non-interactive mode (no TTY)
        if not os.isatty(sys.stdin.fileno()):
            menu.manage_resources(non_interactive=True)
        else:
            menu.run()
    elif args.command == "backup":
        if args.action == "restore":
            restore_backup()
        elif args.action == "list":
            list_backups()
        else:
            console.print("[yellow]Please specify a backup action (list/restore)[/yellow]")
            backup_parser.print_help()
    elif not any(vars(args)) and not unknown:
        menu = Menu()
        menu.run()
    else:
        console.print(f"[yellow]Unknown command: {args.command}[/yellow]")
        parser.print_help()

if __name__ == "__main__":
    main()
