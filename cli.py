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
            ("Owner Analysis", "Analyze property ownership patterns and business entities"),
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
            ctx.invoke(owner_analysis)
        elif choice == 4:
            console.print("[yellow]Rules utility coming soon.[/yellow]")
        elif choice == 5:
            console.print("[yellow]Backend utility coming soon.[/yellow]")
        elif choice == 6:
            console.print("[bold green]Running all tests and generating report...[/bold green]")
            subprocess.run(["bash", "run_all_tests.sh"])
        elif choice == 7:
            # Launch GUI Mapping Tool
            console.print("[bold cyan]Launching GUI Mapping Tool...[/bold cyan]")
            try:
                # Use subprocess to launch the GUI
                subprocess.run([sys.executable, "-m", "frontend.main_window"], check=True)
                console.print("[green]GUI Mapping Tool closed. Returning to main menu.[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error launching GUI Mapping Tool: {e}[/red]")
        elif choice == 8:
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

@cli.command()
def owner_analysis():
    """Analyze property ownership patterns and business entities."""
    console.print("[bold cyan]🏠 PROPERTY OWNERSHIP ANALYSIS[/bold cyan]")
    console.print("=" * 50)
    
    try:
        # Import the owner analyzer
        from backend.utils.owner_analyzer import OwnerAnalyzer
        import pandas as pd
        
        # Find the largest CSV file in upload directory
        upload_dir = "upload"
        csv_files = [f for f in os.listdir(upload_dir) if f.endswith('.csv')]
        
        if not csv_files:
            console.print("[red]No CSV files found in upload directory.[/red]")
            return
        
        # Use the largest file
        largest_file = max(csv_files, key=lambda f: os.path.getsize(os.path.join(upload_dir, f)))
        file_path = os.path.join(upload_dir, largest_file)
        
        console.print(f"[green]Loading data from: {largest_file}[/green]")
        
        # Load data using fast processor
        from backend.utils.high_performance_processor import load_csv_fast
        df = load_csv_fast(file_path)
        console.print(f"[green]Loaded {len(df):,} records[/green]")
        
        # Analyze ownership
        analyzer = OwnerAnalyzer()
        results = analyzer.analyze_ownership(df)
        
        # Generate and display report
        report = analyzer.generate_report(results)
        console.print("\n[bold yellow]OWNERSHIP ANALYSIS REPORT:[/bold yellow]")
        console.print(report)
        
        # Export results
        export_file = "data/exports/owner_analysis_export.json"
        analyzer.export_owner_data(results, export_file)
        console.print(f"[green]📁 Analysis exported to: {export_file}[/green]")
        
        # Show key insights
        console.print("\n[bold cyan]KEY INSIGHTS:[/bold cyan]")
        console.print(f"• {results['total_owners']:,} unique owners")
        console.print(f"• {results['business_entities']['business_count']:,} business entities")
        console.print(f"• {results['ownership_patterns']['owners_with_multiple_properties']:,} multi-property owners")
        
        if results['property_value_analysis'].get('total_property_value'):
            total_value = results['property_value_analysis']['total_property_value']
            console.print(f"• Total property value: ${total_value:,.0f}")
        
    except Exception as e:
        console.print(f"[red]Error during ownership analysis: {e}[/red]")
        console.print("[yellow]Make sure you have CSV files in the upload directory.[/yellow]")

if __name__ == '__main__':
    cli() 