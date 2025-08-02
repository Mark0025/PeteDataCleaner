import os
import json
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rapidfuzz import process
from backend.sheets_client import SheetsClient

TEMPLATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'addresformater', 'propertiesTemplate', 'peteTemplate.json'))
MAPPING_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DEV_MAN', 'header_mapping.json'))
console = Console()

@click.command()
def map_headers():
    """Map spreadsheet headers to Pete template headers interactively."""
    # Load Pete template headers
    if not os.path.exists(TEMPLATE_PATH):
        console.print(f"[red]Pete template not found at {TEMPLATE_PATH}[/red]")
        return
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        pete_headers = [line.strip() for line in f if line.strip()]
    if pete_headers and pete_headers[0].startswith('{'):
        # If it's a JSON array
        pete_headers = json.loads(''.join(pete_headers))
    console.print(f"[bold]Pete Template Headers:[/bold] {pete_headers}")

    # Select a Google Sheet and tab
    client = SheetsClient()
    SheetsClient.print_workspace()
    sheet_id = SheetsClient.select_sheet_from_workspace()
    if not sheet_id:
        sheet_id = Prompt.ask("Enter Google Sheet ID")
    client.set_sheet_id(sheet_id)
    client.log_sheet_to_workspace()
    sheet_names = client.get_sheet_names()
    if not sheet_names:
        console.print("[red]No sheets found in this spreadsheet.[/red]")
        return
    table = Table(title="Select a Sheet Tab")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Tab Name", style="bold")
    for i, name in enumerate(sheet_names, 1):
        table.add_row(str(i), name)
    console.print(table)
    idx = Prompt.ask("Enter the number of the tab to map", choices=[str(i) for i in range(1, len(sheet_names)+1)])
    tab_name = sheet_names[int(idx)-1]
    sheet_headers = client.get_headers(tab_name)
    console.print(f"[bold]Sheet Headers:[/bold] {sheet_headers}")

    # Fuzzy match and manual mapping
    mapping = {}
    for sh in sheet_headers:
        match, score, _ = process.extractOne(sh, pete_headers)
        console.print(f"[cyan]{sh}[/cyan] best match: [green]{match}[/green] (score: {score:.0f})")
        use_match = Prompt.ask(f"Map '{sh}' to '{match}'? (y/n/other Pete header)", default='y')
        if use_match.lower() == 'y':
            mapping[sh] = match
        elif use_match.lower() == 'n':
            mapping[sh] = None
        else:
            # User entered a different Pete header
            mapping[sh] = use_match
    # Save mapping
    with open(MAPPING_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    console.print(f"[green]Header mapping saved to {MAPPING_OUTPUT}[/green]")

if __name__ == "__main__":
    map_headers() 