from modelPrompt import CHAT_GPT_PROMPT, CLAUDE_SONNET_4_PROMPT, GEMINI_2_5_FLASH_PROMPT, DEEPSEEK_R1_PROMPT
import random
import anthropic
import rich
from rich.console import Console
from rich.panel import Panel
from google import genai
from openai import OpenAI


def gpt_move(move: str, prompt_text: str, api_key: str):
    console = Console()

    # If prompt_text is not provided, build it from scratch
    if not prompt_text.startswith("here is your prompt"):
        game_state = open("logger.txt", "r").read()
        prompt_text = f"here is your prompt: {prompt_text}\n\n"
        prompt_text += f"here is the current state of the board: {move}\n\n"
        prompt_text += f"here is the current state of the game: {game_state}\n\n"

    console.print(f"[bold green]GPT is thinking...[/bold green]")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=50  # Limit tokens to encourage brief responses
    )
    return response.choices[0].message.content


def gemini_move(move: str, prompt_text: str, api_key: str):
    console = Console()

    # If prompt_text is not provided, build it from scratch
    if not prompt_text.startswith("here is your prompt"):
        game_state = open("logger.txt", "r").read()
        prompt_text = f"here is your prompt: {prompt_text}\n\n"
        prompt_text += f"here is the current state of the board: {move}\n\n"
        prompt_text += f"here is the current state of the game: {game_state}\n\n"

    console.print(f"[bold green]Gemini is thinking...[/bold green]")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        # Limit tokens for brief responses
        generation_config={"max_output_tokens": 50}
    )
    return response.text


def claude_move(move: str, prompt_text: str, api_key: str):
    console = Console()

    # If prompt_text is not provided, build it from scratch
    if not prompt_text.startswith("here is your prompt"):
        game_state = open("logger.txt", "r").read()
        prompt_text = f"here is your prompt: {prompt_text}\n\n"
        prompt_text += f"here is the current state of the board: {move}\n\n"
        prompt_text += f"here is the current state of the game: {game_state}\n\n"

    console.print(f"[bold green]Claude is thinking...[/bold green]")
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-3-7-sonnet-latest",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=50  # Limit tokens to encourage brief responses
        )
        return response.content[0].text
    except Exception as e:
        console.print(f"[bold red]Claude API error: {str(e)}[/bold red]")
        console.print("[yellow]Returning default move...[/yellow]")
        return "e4"  # Return a default opening move as last resort


def model_move_benchmark(model: str, move_list, prompt: str, api_key: str):
    console = Console()

    # Convert the move list to a string if it's a list
    if isinstance(move_list, list):
        if not move_list:  # If the list is empty
            move_str = "Starting position"
        else:
            # Filter out None values and convert all items to strings
            valid_moves = [str(move) for move in move_list if move is not None]
            if valid_moves:
                move_str = ", ".join(valid_moves)  # Join moves with commas
            else:
                move_str = "Starting position"  # If all moves were None
    else:
        move_str = str(
            move_list) if move_list is not None else "Starting position"

    game_state = open("logger.txt", "r").read()

    # Create a more explicit prompt for the benchmark mode
    prompt_text = f"here is your prompt: {prompt}\n\n"
    prompt_text += f"You are playing chess in a benchmark. Please make a valid chess move.\n\n"
    prompt_text += f"Previous moves: {move_str}\n\n"
    prompt_text += f"Game state: {game_state}\n\n"
    prompt_text += f"Respond ONLY with your next chess move in standard notation (e.g., 'e4', 'Nf3', etc.).\n"
    prompt_text += f"Do not include any explanations or additional text. Just the move."

    # Debug output to see what's being sent to the model
    console.print(f"[dim]Sending prompt to {model}...[/dim]")

    response = None
    try:
        match model:
            case "claude sonnet 4":
                response = claude_move(move_str, prompt_text, api_key)
            case "gemini 2.5 flash":
                response = gemini_move(move_str, prompt_text, api_key)
            case "chatgpt 4o":
                response = gpt_move(move_str, prompt_text, api_key)
            case "gpt 4o":
                response = gpt_move(move_str, prompt_text, api_key)

        # Clean up the response - extract just the move
        if response:
            # Strip whitespace and extract only the first word (likely the move)
            response = response.strip()
            # If response contains multiple words/lines, take just the first word
            if ' ' in response or '\n' in response:
                response = response.split()[0]

            console.print(f"[dim]Raw response: {response}[/dim]")

        return response
    except Exception as e:
        console.print(
            f"[bold red]Error getting move from {model}: {str(e)}[/bold red]")
        return "error"


def model_move(model: str, move: str, prompt: str, api_key: str):
    # Create a more explicit prompt for chess moves
    game_state = open("logger.txt", "r").read()

    enhanced_prompt = f"here is your prompt: {prompt}\n\n"
    enhanced_prompt += f"You are playing chess. Please make a valid chess move.\n\n"
    enhanced_prompt += f"Current board state: {move}\n\n"
    enhanced_prompt += f"Game state: {game_state}\n\n"
    enhanced_prompt += f"Respond ONLY with your next chess move in standard notation (e.g., 'e4', 'Nf3', etc.).\n"
    enhanced_prompt += f"Do not include any explanations or additional text. Just the move."

    match model:
        case "gpt 4o":
            return gpt_move(move, enhanced_prompt, api_key)
        case "claude sonnet 4":
            return claude_move(move, enhanced_prompt, api_key)
        case "gemini 2.5 flash":
            return gemini_move(move, enhanced_prompt, api_key)
        case "chatgpt 4o":
            return gpt_move(move, enhanced_prompt, api_key)
        # case "deepseek":
        #     return deepseek_move(move, enhanced_prompt)


def chess_match(name: str, model: str, api_key: str):
    console = Console()
    game_over = False

    match model:
        case "gpt 4o":
            prompt = CHAT_GPT_PROMPT
        case "claude sonnet 4":
            prompt = CLAUDE_SONNET_4_PROMPT
        case "gemini 2.5 flash":
            prompt = GEMINI_2_5_FLASH_PROMPT
        case "deepseek":
            prompt = DEEPSEEK_R1_PROMPT

    console.print(
        f"[bold blue]Let's play chess with:[/bold blue] [bold green]{model}[/bold green]")

    console.print("[yellow]Tossing coin to see who gets white...[/yellow]")

    if random.choice([True, False]):
        console.print("[bold green]You got the white side![/bold green]")
    else:
        console.print("[bold green]You got the black side![/bold green]")

    # Create a logger file to track the chess match
    log_filename = f"chess_match_{name}_{model.replace(' ', '_')}.txt"

    try:
        with open(log_filename, "w") as logger:
            logger.write(f"Starting game...\n\n")
        console.print(f"[dim]Created log file: {log_filename}[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error creating log file: {e}[/bold red]")

    console.print(
        Panel("[bold green]The board is set up[/bold green]", border_style="green"))

    # Create a logger.txt file for tracking game state
    with open("logger.txt", "w") as game_logger:
        game_logger.write("Game started\n")

    while not game_over:
        console.print("[bold blue]What is your move?[/bold blue]")
        move = console.input("[bold cyan]> [/bold cyan]")

        # Open the log file in append mode
        with open(log_filename, "a") as logger:
            logger.write(f"You played: {move}\n")

        console.print(f"[bold cyan]You played:[/bold cyan] {move}")

        try:
            computer_move = model_move(model, move, prompt, api_key)

            if computer_move == "checkmate":
                console.print("[bold red]You lost![/bold red]")
                game_over = True
                break

            with open(log_filename, "a") as logger:
                logger.write(f"The computer played: {computer_move}\n")

            # Update the game state logger
            with open("logger.txt", "a") as game_logger:
                game_logger.write(f"Your move: {move}\n")
                game_logger.write(f"Computer move: {computer_move}\n")

            console.print(
                f"[bold green]Computer played:[/bold green] {computer_move}")

        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            console.print(
                "[yellow]Please try again or restart the game.[/yellow]")


def chessmatch_benchmark(model: str, api_key: str):
    console = Console()
    game_over = False

    match model:
        case "gpt 4o":
            prompt = CHAT_GPT_PROMPT
        case "claude sonnet 4":
            prompt = CLAUDE_SONNET_4_PROMPT
        case "gemini 2.5 flash":
            prompt = GEMINI_2_5_FLASH_PROMPT
        case "deepseek":
            prompt = DEEPSEEK_R1_PROMPT

    console.print(
        Panel(f"[bold yellow]AI BENCHMARK MODE[/bold yellow]", border_style="yellow"))
    console.print(
        f"[bold blue]Running benchmark with model:[/bold blue] [bold green]{model}[/bold green]")

    player1_side = random.choice([True, False])
    player1_side = "white" if player1_side else "black"

    console.print(
        f"[yellow]Player 1 will play as:[/yellow] [bold]{player1_side}[/bold]")
    console.print(
        f"[yellow]Player 2 will play as:[/yellow] [bold]{'black' if player1_side == 'white' else 'white'}[/bold]")

    # Create a logger file for the benchmark
    log_filename = f"benchmark_for_{model.replace(' ', '_')}.txt"

    try:
        with open(log_filename, "w") as logger:
            logger.write(f"Player1 side: {player1_side}\n")
            logger.write(f"Starting benchmark...\n\n")
        console.print(f"[dim]Created benchmark log file: {log_filename}[/dim]")
    except Exception as e:
        console.print(
            f"[bold red]Error creating benchmark log file: {e}[/bold red]")

    # Create a logger.txt file for tracking game state
    with open("logger.txt", "w") as game_logger:
        game_logger.write("Benchmark started\n")

    console.print(
        Panel("[bold green]The board is set up for benchmark[/bold green]", border_style="green"))
    console.print("[bold cyan]Starting AI vs AI match...[/bold cyan]")

    # Fix the game_over flag - it was initially set to False but loop checked "while game_over"
    # Changed to not game_over to make the loop run
    round_count = 1

    # Initialize move history for both players
    move_player1 = []
    move_player2 = []

    while not game_over:
        console.print(f"\n[bold magenta]Round {round_count}[/bold magenta]")
        console.print(
            f"[bold blue]Model {model} (Player 1) is thinking...[/bold blue]")

        try:
            computer_1_move = model_move_benchmark(
                model, move_player2, prompt, api_key)

            if computer_1_move == "checkmate":
                console.print("[bold red]Player 1 lost![/bold red]")
                game_over = True
                break

            move_player1.append(computer_1_move)
            console.print(
                f"[bold green]Player 1 move:[/bold green] {computer_1_move}")

            with open(log_filename, "a") as logger:
                logger.write(
                    f"Round {round_count} - Player 1 move: {computer_1_move}\n")

            # After Player 1's move
            with open("logger.txt", "a") as game_logger:
                game_logger.write(f"Player 1 move: {computer_1_move}\n")

            console.print(
                f"[bold blue]Model {model} (Player 2) is thinking...[/bold blue]")

            computer_2_move = model_move_benchmark(
                model, move_player1, prompt, api_key)

            if computer_2_move == "checkmate":
                console.print("[bold red]Player 2 lost![/bold red]")
                game_over = True
                break

            move_player2.append(computer_2_move)
            console.print(
                f"[bold green]Player 2 move:[/bold green] {computer_2_move}")

            with open(log_filename, "a") as logger:
                logger.write(
                    f"Round {round_count} - Player 2 move: {computer_2_move}\n\n")

            # After Player 2's move
            with open("logger.txt", "a") as game_logger:
                game_logger.write(f"Player 2 move: {computer_2_move}\n")

            round_count += 1

        except Exception as e:
            console.print(
                f"[bold red]Error during benchmark: {str(e)}[/bold red]")
            console.print("[yellow]Benchmark stopped due to error.[/yellow]")
            # Log the error to a file for debugging
            try:
                with open("error.txt", "w") as error_file:
                    error_file.write(f"Benchmark Error:\n{str(e)}\n")
                    error_file.write(f"Error type: {type(e).__name__}\n")
                    import traceback
                    error_file.write(f"Traceback:\n{traceback.format_exc()}")
                console.print("[dim]Error details saved to error.txt[/dim]")
            except Exception as log_error:
                console.print(
                    f"[bold red]Failed to log error: {str(log_error)}[/bold red]")
            game_over = True

    console.print(
        Panel("[bold yellow]Benchmark Complete![/bold yellow]", border_style="yellow"))
    console.print(f"[dim]Full log available in: {log_filename}[/dim]")
