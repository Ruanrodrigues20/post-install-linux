from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.progress import track
from time import sleep
from src.post_install_linux.backend.controller import Controller

console = Console()
controller = Controller()

def show_title():
    title = Panel(
        Align.center("[bold cyan]Post Install Linux[/bold cyan]", vertical="middle"),
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 4),
        subtitle="[italic]Installation Manager[/italic]",
        subtitle_align="right"
    )
    console.print(title)

def show_menu():
    table = Table(title="Installation Menu", box=box.ROUNDED, show_lines=True, border_style="bright_magenta")
    table.add_column("Option", style="bold yellow", justify="center", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("1", "Minimal Installation")
    table.add_row("2", "Complete Installation")
    table.add_row("3", "Full Installation")
    table.add_row("4", "Install Wallpapers")
    table.add_row("5", "Install GTK Theme")
    table.add_row("0", "Exit")

    console.print(table)

def execute_task(task_name, task_function):
    console.print(f"\n[bold green]Starting:[/bold green] {task_name}...\n")
    for _ in track(range(20), description=f"[yellow]{task_name} in progress...[/yellow]"):
        sleep(0.1)  # Simulate progress

    try:
        task_function()
        console.print(f"\n[bold green]Success:[/bold green] {task_name} completed!\n")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {task_name} failed: {e}\n")

def main():
    show_title()

    while True:
        show_menu()
        choice = Prompt.ask("[bold green]Choose an option[/bold green]", choices=["0", "1", "2", "3", "4", "5"])

        if choice == "1":
            execute_task("Minimal Installation", controller.install_minimal)
        elif choice == "2":
            execute_task("Complete Installation", controller.install_complete)
        elif choice == "3":
            execute_task("Full Installation", controller.install_full)
        elif choice == "4":
            execute_task("Install Wallpapers", controller.install_wallpapers)
        elif choice == "5":
            execute_task("Install GTK Theme", controller.install_gtk_theme)
        elif choice == "0":
            console.print(Panel("[bold red]Exiting Post Install Linux[/bold red]", border_style="red", box=box.DOUBLE))
            break

        console.print("\n[dim]Press Enter to continue...[/dim]", end="")
        input()

if __name__ == "__main__":
    main()
