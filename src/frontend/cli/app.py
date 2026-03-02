"""CLI frontend for Vibe Translating.

Provides a rich terminal interface for translation tasks,
inspired by modern CLI tools like claude code.
"""

import sys
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from ...backend.service import BackendService
from ..common.protocol import Request


console = Console()


class CLIApp:
    """Command-line interface for Vibe Translating."""

    def __init__(self) -> None:
        """Initialize the CLI application."""
        self.service = BackendService()
        self.session = PromptSession(history=InMemoryHistory())
        self._running = False
        self._commands: dict[str, Any] = {
            "help": self._cmd_help,
            "translate": self._cmd_translate,
            "t": self._cmd_translate,
            "modes": self._cmd_modes,
            "config": self._cmd_config,
            "set": self._cmd_set,
            "plugins": self._cmd_plugins,
            "memory": self._cmd_memory,
            "terms": self._cmd_terms,
            "addterm": self._cmd_addterm,
            "bookmark": self._cmd_bookmark,
            "check": self._cmd_check_api,
            "save": self._cmd_save,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
        }

    def run(self) -> None:
        """Run the CLI application."""
        self._running = True
        self._show_welcome()

        while self._running:
            try:
                user_input = self.session.prompt(
                    "vibe> "
                ).strip()
                if not user_input:
                    continue
                self._handle_input(user_input)
            except KeyboardInterrupt:
                console.print("\n[dim]Use 'quit' to exit[/dim]")
            except EOFError:
                break

        console.print("[dim]Goodbye![/dim]")

    def _show_welcome(self) -> None:
        """Display welcome screen."""
        welcome = Text()
        welcome.append("Vibe Translating", style="bold cyan")
        welcome.append(" v0.1.0\n", style="dim")
        welcome.append(
            "AI-powered translation platform\n\n",
            style="italic",
        )
        welcome.append(
            "Type 'help' for commands, "
            "'translate <text>' to translate",
            style="dim",
        )
        console.print(Panel(welcome, border_style="cyan"))

    def _handle_input(self, user_input: str) -> None:
        """Handle user input.

        Args:
            user_input: Raw user input string.
        """
        parts = user_input.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        handler = self._commands.get(cmd)
        if handler:
            handler(args)
        else:
            self._cmd_translate(user_input)

    def _cmd_help(self, args: str = "") -> None:
        """Show help information."""
        table = Table(
            title="Commands",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        table.add_row("translate <text>", "Translate text (or just type text)")
        table.add_row("modes", "Show available translation modes")
        table.add_row("config [key]", "Show configuration")
        table.add_row("set <key> <value>", "Set configuration value")
        table.add_row("plugins", "Show plugins")
        table.add_row("memory", "Show agent memory")
        table.add_row("terms", "Show terminology")
        table.add_row("addterm <src> <tgt> [cat]", "Add terminology")
        table.add_row("bookmark <pos> [label]", "Add bookmark")
        table.add_row("check", "Check API availability")
        table.add_row("save", "Save config and memory")
        table.add_row("quit", "Exit application")
        console.print(table)

    def _cmd_translate(self, args: str = "") -> None:
        """Translate text."""
        if not args:
            console.print("[yellow]Usage: translate <text>[/yellow]")
            return
        console.print("[dim]Translating...[/dim]")
        response = self.service.handle_request(
            Request(method="translate", params={"text": args})
        )
        if response.success:
            src_lang = self.service.config.get(
                "translation.source_language", "ja"
            )
            tgt_lang = self.service.config.get(
                "translation.target_language", "zh-CN"
            )
            console.print(
                Panel(
                    f"[dim]{src_lang}:[/dim] {args}\n\n"
                    f"[bold]{tgt_lang}:[/bold] "
                    f"{response.data['translation']}",
                    title="Translation",
                    border_style="green",
                )
            )
        else:
            console.print(
                f"[red]Error: {response.error}[/red]"
            )

    def _cmd_modes(self, args: str = "") -> None:
        """Show available translation modes."""
        response = self.service.handle_request(
            Request(method="get_modes")
        )
        if not response.success:
            console.print(f"[red]Error: {response.error}[/red]")
            return
        table = Table(
            title="Translation Modes",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Name", style="cyan")
        table.add_column("Display Name")
        table.add_column("Formats")
        for name, info in response.data.items():
            table.add_row(
                name,
                info["display_name"],
                ", ".join(info["supported_formats"]),
            )
        console.print(table)

    def _cmd_config(self, args: str = "") -> None:
        """Show or get configuration."""
        if args:
            response = self.service.handle_request(
                Request(
                    method="get_config",
                    params={"key": args.strip()},
                )
            )
            if response.success:
                console.print(
                    f"[cyan]{args}[/cyan] = {response.data}"
                )
            else:
                console.print(
                    f"[red]Error: {response.error}[/red]"
                )
        else:
            flat = self.service.config.get_flat()
            table = Table(
                title="Configuration",
                show_header=True,
                header_style="bold",
            )
            table.add_column("Key", style="cyan")
            table.add_column("Value")
            for key, value in sorted(flat.items()):
                table.add_row(key, str(value))
            console.print(table)

    def _cmd_set(self, args: str = "") -> None:
        """Set configuration value."""
        parts = args.split(None, 1)
        if len(parts) < 2:
            console.print(
                "[yellow]Usage: set <key> <value>[/yellow]"
            )
            return
        key, raw_value = parts
        value: Any = raw_value
        if raw_value.lower() == "true":
            value = True
        elif raw_value.lower() == "false":
            value = False
        else:
            try:
                value = int(raw_value)
            except ValueError:
                try:
                    value = float(raw_value)
                except ValueError:
                    pass

        response = self.service.handle_request(
            Request(
                method="set_config",
                params={"key": key, "value": value},
            )
        )
        if response.success:
            console.print(f"[green]Set {key} = {value}[/green]")
        else:
            console.print(f"[red]Error: {response.error}[/red]")

    def _cmd_plugins(self, args: str = "") -> None:
        """Show plugins."""
        response = self.service.handle_request(
            Request(method="get_plugins")
        )
        if not response.success:
            console.print(f"[red]Error: {response.error}[/red]")
            return
        table = Table(
            title="Plugins",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Name", style="cyan")
        table.add_column("Version")
        table.add_column("Status")
        table.add_column("Description")
        for name, info in response.data.items():
            status = (
                "[green]Active[/green]"
                if info["active"]
                else "[dim]Inactive[/dim]"
            )
            table.add_row(
                name,
                info["version"],
                status,
                info["description"],
            )
        console.print(table)

    def _cmd_memory(self, args: str = "") -> None:
        """Show agent memory."""
        response = self.service.handle_request(
            Request(method="get_memory")
        )
        if not response.success:
            console.print(f"[red]Error: {response.error}[/red]")
            return
        data = response.data
        console.print(Panel(
            f"Terms: {len(data.get('terms', []))}\n"
            f"Summaries: {len(data.get('summaries', []))}\n"
            f"Notes: {len(data.get('notes', []))}\n"
            f"Bookmarks: {len(data.get('bookmarks', []))}",
            title="Agent Memory",
            border_style="blue",
        ))

    def _cmd_terms(self, args: str = "") -> None:
        """Show terminology."""
        response = self.service.handle_request(
            Request(method="get_terms")
        )
        if not response.success:
            console.print(f"[red]Error: {response.error}[/red]")
            return
        if not response.data:
            console.print("[dim]No terms stored yet[/dim]")
            return
        table = Table(
            title="Terminology",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Source", style="cyan")
        table.add_column("Target", style="green")
        table.add_column("Category")
        for t in response.data:
            table.add_row(
                t["source"], t["target"], t["category"]
            )
        console.print(table)

    def _cmd_addterm(self, args: str = "") -> None:
        """Add terminology entry."""
        parts = args.split()
        if len(parts) < 2:
            console.print(
                "[yellow]Usage: addterm <source> <target> "
                "[category][/yellow]"
            )
            return
        params = {
            "source": parts[0],
            "target": parts[1],
        }
        if len(parts) > 2:
            params["category"] = parts[2]
        response = self.service.handle_request(
            Request(method="add_term", params=params)
        )
        if response.success:
            console.print(
                f"[green]Added: {parts[0]} → {parts[1]}[/green]"
            )
        else:
            console.print(f"[red]Error: {response.error}[/red]")

    def _cmd_bookmark(self, args: str = "") -> None:
        """Add or list bookmarks."""
        if not args:
            response = self.service.handle_request(
                Request(method="get_bookmarks")
            )
            if response.success:
                if not response.data:
                    console.print("[dim]No bookmarks[/dim]")
                else:
                    for bm in response.data:
                        console.print(
                            f"  [{bm['position']}] "
                            f"{bm.get('label', '')}"
                        )
            return
        parts = args.split(None, 1)
        try:
            pos = int(parts[0])
        except ValueError:
            console.print(
                "[yellow]Usage: bookmark <position> "
                "[label][/yellow]"
            )
            return
        label = parts[1] if len(parts) > 1 else ""
        response = self.service.handle_request(
            Request(
                method="add_bookmark",
                params={"position": pos, "label": label},
            )
        )
        if response.success:
            console.print(
                f"[green]Bookmark added at {pos}[/green]"
            )

    def _cmd_check_api(self, args: str = "") -> None:
        """Check API availability."""
        response = self.service.handle_request(
            Request(method="check_api")
        )
        if response.success:
            data = response.data
            status = (
                "[green]Available[/green]"
                if data["available"]
                else "[red]Unavailable[/red]"
            )
            console.print(
                f"Provider: {data['provider']} - {status}"
            )

    def _cmd_save(self, args: str = "") -> None:
        """Save config and memory."""
        self.service.handle_request(
            Request(method="save_config")
        )
        self.service.handle_request(
            Request(method="save_memory")
        )
        console.print("[green]Configuration and memory saved[/green]")

    def _cmd_quit(self, args: str = "") -> None:
        """Exit the application."""
        self._running = False


def main() -> None:
    """Entry point for CLI frontend."""
    app = CLIApp()
    app.run()


if __name__ == "__main__":
    main()
