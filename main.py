from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print
from rich.prompt import Confirm
import os
import sys
import keyboard


def get_title_content():
    """Get the ASCII art title content from title.txt"""
    try:
        with open("title.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        console = Console()
        console.print("[bold red]Error: title.txt not found![/bold red]")
        exit(1)


def display_screen(title_content, additional_content=None):
    """Display the screen with title and additional content"""
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()

    # Display title
    console.print(Panel(title_content, border_style="green", expand=False))

    # Display additional content if provided
    if additional_content:
        console.print(additional_content)


def select_from_menu(options, prompt_text, title_content):
    """Create a custom selection menu where user navigates with arrow keys and selects with space"""
    console = Console()
    selected_index = 0

    def print_menu():
        # Display screen with title and menu
        display_screen(title_content)
        console.print(prompt_text)

        for i, option in enumerate(options):
            if i == selected_index:
                console.print(f"[bold green]> {option} <[/bold green]")
            else:
                console.print(f"  {option}  ")

        console.print(
            "\n[italic]Use arrow keys to navigate and press SPACE to select[/italic]")

    print_menu()

    while True:
        key_event = keyboard.read_event(suppress=True)

        if key_event.event_type == keyboard.KEY_DOWN:
            if key_event.name == "down" and selected_index < len(options) - 1:
                selected_index += 1
                print_menu()
            elif key_event.name == "up" and selected_index > 0:
                selected_index -= 1
                print_menu()
            elif key_event.name == "space":
                return options[selected_index]


def get_user_input(title_content):
    """Get user name and model selection"""
    console = Console()

    # Ask for name
    display_screen(
        title_content, "[bold blue]Please enter your name[/bold blue]")
    name = Prompt.ask("")

    # Model selection using custom menu
    model_choices = ["gpt 4o", "claude sonnet 4",
                     "gemini 2.5 flash", "deepseek"]
    model = select_from_menu(
        model_choices, "[bold blue]Select a model:[/bold blue]", title_content)

    return name, model


def main():
    """Main function to run the application"""
    console = Console()
    title_content = get_title_content()
    display_screen(title_content)
    name, model = get_user_input(title_content)

    # Display the final selections
    display_screen(title_content)
    console.print("[bold green]These are your selections:[/bold green]")
    console.print(
        f"[bold red]NOTICE:[/bold red] you cannot change any of the selections once the game has started")
    console.print(f"[bold green]Name:[/bold green] {name}")
    console.print(f"[bold green]Model:[/bold green] {model}")

    from key_handler import get_key
    api_key = get_key(model, title_content)

    # If API key was provided, output it to terminal
    if api_key:
        display_screen(title_content)
        console.print(
            "[bold green]Starting game with the following configuration:[/bold green]")
        console.print(f"[bold]Name:[/bold] {name}")
        console.print(f"[bold]Model:[/bold] {model}")
        console.print(
            f"[bold]API Key:[/bold] {'*' * 5 + api_key[-4:] if api_key else 'None'}")
        console.print(
            "\n[bold green]Press any key to start the game...[/bold green]")
        keyboard.read_event(suppress=True)

        from chess import chess_match

        chess_match(name, model, api_key)


if __name__ == "__main__":
    main()
