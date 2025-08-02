import os
import sys
import click
import subprocess
from rich.console import Console
from rich.table import Table

# Ensure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Pete Main CLI - Manage workspace, standardize data, rules, backend, and run tests."""
    if ctx.invoked_subcommand is None:
        # Display interactive menu
        options = [
            ("Workspace", "Manage Google Sheets workspace (list, search, add, select, browse)"),
            ("Standardize", "Standardize uploaded data files to Pete template"),
            ("Rules", "Rule management utilities (coming soon)"),
            ("Backend", "Backend/analysis utilities (coming soon)"),
            ("Test", "Run all tests and show what's working"),
            ("GUI Mapping Tool", "Launch the GUI mapping tool for visual column mapping"),
            ("Exit", "Exit the application")
        ]
        
        # Create a rich table for menu display
        table = Table(title="Pete Main Menu", show_lines=True)
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        
        for i, (name, desc) in enumerate(options, 1):
            table.add_row(f"{i}. {name}", desc)
        
        console.print(table)
        
        # Prompt for selection
        choice = click.prompt("Select an option", type=int, default=1)
        
        # Handle menu selection
        if choice == 1:
            ctx.invoke(workspace_cli)
        elif choice == 2:
            ctx.invoke(standardize)
        elif choice == 3:
            console.print("[yellow]Rules utility coming soon.[/yellow]")
        elif choice == 4:
            console.print("[yellow]Backend utility coming soon.[/yellow]")
        elif choice == 5:
            console.print("[bold green]Running all tests and generating report...[/bold green]")
            subprocess.run(["bash", "run_all_tests.sh"])
        elif choice == 6:
            # Launch GUI Mapping Tool
            console.print("[bold cyan]Launching GUI Mapping Tool...[/bold cyan]")
            try:
                # Use subprocess to launch the GUI
                subprocess.run([sys.executable, "-m", "frontend.main_window"], check=True)
                console.print("[green]GUI Mapping Tool closed. Returning to main menu.[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error launching GUI Mapping Tool: {e}[/red]")
        elif choice == 7:
            console.print("[bold red]Exiting Pete CLI...[/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid selection. Use --help for more options.[/red]")

# Existing CLI commands remain the same
@cli.command()
def workspace():
    """Manage Google Sheets workspace."""
    # Existing workspace command implementation
    pass

@cli.command()
def standardize():
    """Standardize uploaded data files."""
    # Existing standardize command implementation
    pass

if __name__ == '__main__':
    cli() 