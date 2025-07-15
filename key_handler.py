import rich
from rich.console import Console
from rich.prompt import Prompt
import keyboard
import os
from rich.panel import Panel


def display_screen_for_key(title_content, additional_content=None):
    """Display the screen with title and additional content"""
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()

    # Display title
    console.print(Panel(title_content, border_style="green", expand=False))

    # Display additional content if provided
    if additional_content:
        console.print(additional_content)


def get_key(model, title_content):
    """Ask user for API key based on model selection"""
    console = Console()

    # Display the API key question
    display_screen_for_key(
        title_content, f"[bold blue]You selected {model}[/bold blue]")
    console.print(
        "[bold green]Do you have an API key for this model? (y/n)[/bold green]")

    # Get user response
    response = Prompt.ask("", choices=["y", "n"], default="n")

    if response.lower() == "y":
        # User has API key, ask for it
        display_screen_for_key(
            title_content, f"[bold blue]You selected {model}[/bold blue]")
        console.print("[bold green]Please enter your API key:[/bold green]")
        api_key = Prompt.ask("", password=True)

        # Display confirmation
        display_screen_for_key(title_content)
        console.print("[bold green]API key received. Thank you![/bold green]")
        return api_key
    else:
        # User doesn't have API key
        display_screen_for_key(title_content)
        console.print(
            "[bold red]You need an API key to use this model.[/bold red]")
        console.print(
            "[bold yellow]Please restart the application and select a different model.[/bold yellow]")

        # Wait for any key to exit
        console.print("\n[italic]Press any key to exit...[/italic]")
        keyboard.read_event(suppress=True)
        return None
