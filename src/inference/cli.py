from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .inference import load_model, prompt, clear_mem

console = Console()

COMMANDS = {
    "/help": "показать эту справку",
    "/clearmem": "очистить память диалога",
    "/clear": "очистить экран",
    "exit": "выйти",
}


def show_help() -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Команда", style="green")
    table.add_column("Описание")
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(Panel(table, title="Помощь", border_style="yellow", expand=False))


def main() -> None:
    with console.status("загружаю модель..."):
        load_model()
    console.print("[dim]модель загружена, /help для списка команд[/dim]")

    while True:
        try:
            user_input = console.input("\n[green]>[/green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]пока![/dim]")
            break

        if not user_input:
            continue

        match user_input:
            case "exit":
                break
            case "/help":
                show_help()
            case "/clear":
                console.clear()
            case "/clearmem":
                clear_mem()
                console.print("[dim]память очищена[/dim]")
            case _:
                console.rule(style="cyan")
                prompt(user_input)   # стримит сам через print
                print()
                console.rule(style="cyan")


if __name__ == "__main__":
    main()
