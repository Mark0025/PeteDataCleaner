import os
import json
import click
from rich.console import Console
from rich.table import Table
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from backend.sheets_client import SheetsClient, WORKSPACE_FILE, SCOPES, CREDENTIALS_FILE

console = Console()

@click.group()
def cli():
    """Pete Google Sheets Workspace CLI"""
    pass

@cli.command()
def list():
    """List all known Google Sheets in your workspace."""
    workspace = SheetsClient.load_workspace()
    table = Table(title="Google Sheets Workspace")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Spreadsheet Name", style="bold")
    table.add_column("Sheet ID", style="magenta")
    table.add_column("Tabs", style="green")
    table.add_column("Last Used", style="yellow")
    for i, sheet in enumerate(workspace["sheets"]):
        table.add_row(
            str(i+1),
            sheet["spreadsheet_name"],
            sheet["sheet_id"],
            ", ".join(sheet["tabs"]),
            sheet["last_used"]
        )
    console.print(table)

@cli.command()
@click.argument('query')
def search(query):
    """Search Google Drive for Sheets by name."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES + ["https://www.googleapis.com/auth/drive.metadata.readonly"])
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.spreadsheet' and name contains '{query}'",
        fields="files(id, name)",
        pageSize=20
    ).execute()
    files = results.get('files', [])
    if not files:
        console.print(f"[red]No sheets found for query: {query}[/red]")
        return
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Spreadsheet Name", style="bold")
    table.add_column("Sheet ID", style="magenta")
    for i, f in enumerate(files):
        table.add_row(str(i+1), f["name"], f["id"])
    console.print(table)

@cli.command()
@click.argument('sheet_id')
def add(sheet_id):
    """Add a new Google Sheet to your workspace by ID."""
    client = SheetsClient()
    client.set_sheet_id(sheet_id)
    client.log_sheet_to_workspace()
    console.print(f"[green]Added sheet {sheet_id} to workspace.[/green]")

@cli.command()
def select():
    """Interactively select a sheet from your workspace."""
    workspace = SheetsClient.load_workspace()
    if not workspace["sheets"]:
        console.print("[red]No sheets in workspace. Use 'add' or 'search' first.[/red]")
        return
    table = Table(title="Select a Google Sheet")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Spreadsheet Name", style="bold")
    table.add_column("Sheet ID", style="magenta")
    for i, sheet in enumerate(workspace["sheets"]):
        table.add_row(str(i+1), sheet["spreadsheet_name"], sheet["sheet_id"])
    console.print(table)
    idx = click.prompt("Enter the number of the sheet to select", type=int)
    if 1 <= idx <= len(workspace["sheets"]):
        selected = workspace["sheets"][idx-1]
        console.print(f"[green]Selected:[/green] {selected['spreadsheet_name']} (ID: {selected['sheet_id']})")
    else:
        console.print("[red]Invalid selection.[/red]")

@cli.command()
def browse():
    """Browse all Google Sheets in your Drive and select one by number."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES + ["https://www.googleapis.com/auth/drive.metadata.readonly"])
    service = build('drive', 'v3', credentials=creds)
    # List all Google Sheets (up to 1000 for now)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        fields="files(id, name, parents)",
        pageSize=1000
    ).execute()
    files = results.get('files', [])
    if not files:
        console.print("[red]No Google Sheets found in your Drive.[/red]")
        return
    table = Table(title="All Google Sheets in Your Drive")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Spreadsheet Name", style="bold")
    table.add_column("Sheet ID", style="magenta")
    for i, f in enumerate(files):
        table.add_row(str(i), f["name"], f["id"])
    console.print(table)
    idx = click.prompt("Enter the number of the sheet to select", type=int)
    if 0 <= idx < len(files):
        selected = files[idx]
        console.print(f"[green]Selected:[/green] {selected['name']} (ID: {selected['id']})")
        # Optionally, add to workspace
        add_to_workspace = click.confirm("Add this sheet to your workspace?", default=True)
        if add_to_workspace:
            client = SheetsClient()
            client.set_sheet_id(selected['id'])
            client.log_sheet_to_workspace()
            console.print(f"[green]Added {selected['name']} to workspace.[/green]")
    else:
        console.print("[red]Invalid selection.[/red]")

if __name__ == "__main__":
    cli() 