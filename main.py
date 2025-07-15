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
            "[bold green]Starting with the following configuration:[/bold green]")
        console.print(f"[bold]Name:[/bold] {name}")
        console.print(f"[bold]Model:[/bold] {model}")
        console.print(
            f"[bold]API Key:[/bold] {'*' * 5 + api_key[-4:] if api_key else 'None'}")

        # Ask user if they want to play chess or benchmark the LLM
        console.print(
            "\n[bold yellow]What would you like to do?[/bold yellow]")
        console.print("[1] Play chess against the AI")
        console.print("[2] Run an AI benchmark (AI vs AI)")

        choice = console.input(
            "[bold cyan]Enter your choice (1/2): [/bold cyan]")

        from chess import chess_match, chessmatch_benchmark

        if choice == "1":
            console.print("\n[bold green]Starting chess game...[/bold green]")
            console.print(
                "\n[bold green]Press any key to begin...[/bold green]")
            keyboard.read_event(suppress=True)
            chess_match(name, model, api_key)
        elif choice == "2":
            console.print(
                "\n[bold green]Starting benchmark mode...[/bold green]")
            console.print(
                "\n[bold green]Press any key to begin...[/bold green]")
            keyboard.read_event(suppress=True)
            chessmatch_benchmark(model, api_key)
        else:
            console.print(
                "[bold red]Invalid choice. Defaulting to chess game.[/bold red]")
            console.print(
                "\n[bold green]Press any key to begin...[/bold green]")
            keyboard.read_event(suppress=True)
            chess_match(name, model, api_key)

        if Confirm.ask("Do you want to play again?"):
            main()
        else:
            print("Thanks for playing!")
            exit(0)


if __name__ == "__main__":
    main()
