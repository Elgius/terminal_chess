import chess
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Initialize Rich console
console = Console()


def validate_chess_moves(benchmark_file):
    """
    Validates if the chess moves in the benchmark file are legal.

    Args:
        benchmark_file (str): Path to the benchmark file

    Returns:
        list: List of tuples containing (round_number, player, move, is_legal, reason)
    """
    # Read the benchmark file
    try:
        with open(benchmark_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        console.print(
            f"[bold red]Error: File {benchmark_file} not found![/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error reading file: {str(e)}[/bold red]")
        return []

    # Create a chess board
    board = chess.Board()

    # Extract player information
    player1_match = re.search(r"Player 1 \((.+?)\)", content)
    player2_match = re.search(r"Player 2 \((.+?)\)", content)

    player1_name = player1_match.group(1) if player1_match else "Player 1"
    player2_name = player2_match.group(1) if player2_match else "Player 2"

    # Extract moves using regex - handle different formats
    move_pattern = r"Round (\d+) - Player (\d+).*?move: (.+?)(?=\n|$)"
    moves = re.findall(move_pattern, content)

    results = []
    game_ended = False

    for round_num, player, move_text in moves:
        if game_ended:
            results.append((round_num, player, move_text,
                           False, "Game already ended"))
            continue

        # Clean up the move text (remove any extra text)
        clean_move = move_text.strip()

        # Handle special notation like checkmate
        is_checkmate = False
        if clean_move.endswith('#'):
            is_checkmate = True
            # Remove the # for parsing
            clean_move = clean_move[:-1]

        # Get the first word only if there are multiple words
        if ' ' in clean_move:
            clean_move = clean_move.split()[0]

        # Skip moves that are clearly comments or explanations
        if len(clean_move) > 5 or clean_move.lower() in ["checkmate", "stalemate", "draw"]:
            results.append((round_num, player, move_text, False,
                           "Not a valid chess move notation"))
            continue

        try:
            # Try to parse the move
            move = board.parse_san(clean_move)

            # Check if the move is legal
            if move in board.legal_moves:
                board.push(move)

                # Check if this move results in checkmate
                if board.is_checkmate():
                    results.append((round_num, player, move_text,
                                   True, "Legal move - Checkmate"))
                    game_ended = True
                elif board.is_stalemate():
                    results.append((round_num, player, move_text,
                                   True, "Legal move - Stalemate"))
                    game_ended = True
                else:
                    results.append(
                        (round_num, player, move_text, True, "Legal move"))
            else:
                results.append(
                    (round_num, player, move_text, False, "Illegal move"))
        except ValueError as e:
            results.append((round_num, player, move_text, False,
                           f"Invalid notation: {str(e)}"))
        except Exception as e:
            results.append((round_num, player, move_text,
                           False, f"Error: {str(e)}"))

    return results, player1_name, player2_name


def print_validation_results(results, player1_name, player2_name):
    """
    Prints the validation results in a readable format using Rich.

    Args:
        results (list): List of tuples containing (round_number, player, move, is_legal, reason)
        player1_name (str): Name of player 1
        player2_name (str): Name of player 2
    """
    table = Table(title="Chess Move Validation Results")

    table.add_column("Round", style="cyan", no_wrap=True)
    table.add_column("Player", style="magenta")
    table.add_column("Move", style="yellow")
    table.add_column("Legal", style="green")
    table.add_column("Reason", style="blue")

    for round_num, player, move, is_legal, reason in results:
        legal_status = "[green]✓[/green]" if is_legal else "[red]✗[/red]"
        player_name = player1_name if player == "1" else player2_name
        table.add_row(
            round_num, f"{player} ({player_name})", move, legal_status, reason)

    console.print(table)


def analyze_game(benchmark_file):
    """
    Analyzes the chess game in the benchmark file and prints a detailed report.

    Args:
        benchmark_file (str): Path to the benchmark file
    """
    console = Console()
    console.print(
        Panel(f"[bold blue]Analyzing chess moves in {benchmark_file}...[/bold blue]"))

    with console.status("[bold green]Validating chess moves...[/bold green]") as status:
        results, player1_name, player2_name = validate_chess_moves(
            benchmark_file)

    if not results:
        console.print("[bold red]No valid moves found to analyze![/bold red]")
        return

    print_validation_results(results, player1_name, player2_name)

    # Count legal and illegal moves
    legal_moves = sum(1 for _, _, _, is_legal, _ in results if is_legal)
    illegal_moves = sum(1 for _, _, _, is_legal, _ in results if not is_legal)

    # Count moves by player
    player1_moves = sum(1 for _, player, _, _, _ in results if player == "1")
    player2_moves = sum(1 for _, player, _, _, _ in results if player == "2")

    # Count legal moves by player
    player1_legal = sum(1 for _, player, _, is_legal,
                        _ in results if player == "1" and is_legal)
    player2_legal = sum(1 for _, player, _, is_legal,
                        _ in results if player == "2" and is_legal)

    # Calculate accuracy percentages safely
    p1_accuracy = (player1_legal / player1_moves *
                   100) if player1_moves > 0 else 0
    p2_accuracy = (player2_legal / player2_moves *
                   100) if player2_moves > 0 else 0
    total_accuracy = (legal_moves / len(results) * 100) if results else 0

    console.print()
    console.print(Panel(f"""[bold]Summary:[/bold]
[white]Total moves analyzed:[/white] [cyan]{len(results)}[/cyan]
[white]Legal moves:[/white] [green]{legal_moves}[/green] ({total_accuracy:.1f}%)
[white]Illegal moves:[/white] [red]{illegal_moves}[/red] ({100-total_accuracy:.1f}%)

[bold]Player Stats:[/bold]
[white]{player1_name}:[/white] {player1_moves} moves, {player1_legal} legal ({p1_accuracy:.1f}%)
[white]{player2_name}:[/white] {player2_moves} moves, {player2_legal} legal ({p2_accuracy:.1f}%)"""))

    # Check for game ending
    checkmate_move = next((move for _, _, move, is_legal,
                          reason in results if is_legal and "Checkmate" in reason), None)
    if checkmate_move:
        console.print(f"[bold green]Game ended with checkmate![/bold green]")
    else:
        console.print(
            f"[bold yellow]Game did not end with a clear result.[/bold yellow]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        benchmark_file = sys.argv[1]
    else:
        # Look for benchmark files in the current directory
        import glob
        benchmark_files = glob.glob("benchmark_*.txt")

        if benchmark_files:
            benchmark_file = "benchmark_claude_sonnet_4_vs_gpt_4o.txt"
            console.print(
                f"[yellow]No file specified, using: {benchmark_file}[/yellow]")
        else:
            benchmark_file = "benchmark_claude_sonnet_4_vs_gpt_4o.txt"
            console.print(
                f"[yellow]No benchmark files found, defaulting to: {benchmark_file}[/yellow]")

    analyze_game(benchmark_file)
