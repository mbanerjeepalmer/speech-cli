"""Rich Live TUI for side-by-side transcription display."""

import threading
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from speech_cli.eval.providers.base import TranscriptionResult


class TranscriptionDisplay:
    """Thread-safe Rich Live display for transcription results.

    Supports two modes:
    - single-line: one row per provider, text tailed to terminal width
    - multi-line: one Panel per provider with full wrapped text
    """

    def __init__(self, mode: str = "single-line") -> None:
        self.mode = mode
        self.console = Console()
        self._providers: list[str] = []
        self._results: dict[str, TranscriptionResult] = {}
        self._lock = threading.Lock()
        self._live: Optional[Live] = None

    def set_providers(self, provider_names: list[str]) -> None:
        """Set the list of providers being evaluated."""
        self._providers = list(provider_names)

    def update_result(self, provider_name: str, result: TranscriptionResult) -> None:
        """Thread-safe update of a provider's result."""
        with self._lock:
            self._results[provider_name] = result
            if self._live:
                self._live.update(self._render())

    def _render(self):
        """Render current state based on display mode."""
        if self.mode == "multi-line":
            return self._render_multi_line()
        return self._render_single_line()

    def _render_single_line(self):
        """One row per provider, text tailed to terminal width."""
        table = Table(
            show_header=True,
            header_style="bold",
            expand=True,
            show_edge=False,
            pad_edge=False,
        )
        table.add_column("Provider", style="cyan", width=20, no_wrap=True)
        table.add_column("Time", style="yellow", width=8, no_wrap=True)
        table.add_column("Text", ratio=1)

        # Calculate available width for text
        term_width = self.console.width or 80
        text_width = max(term_width - 30, 20)

        for name in self._providers:
            result = self._results.get(name)
            if result:
                text = result.text
                if len(text) > text_width:
                    text = text[-text_width:]
                time_str = f"{result.processing_time_seconds:.1f}s" if result.processing_time_seconds else "..."
                table.add_row(name, time_str, text)
            else:
                table.add_row(name, "[dim]...[/dim]", "[dim]waiting...[/dim]")

        return table

    def _render_multi_line(self):
        """One Panel per provider with full wrapped text."""
        from rich.columns import Columns
        from rich.console import Group

        panels = []
        for name in self._providers:
            result = self._results.get(name)
            if result:
                subtitle = (
                    f"{result.model_name} | {result.processing_time_seconds:.1f}s"
                    if result.processing_time_seconds
                    else result.model_name
                )
                panels.append(
                    Panel(
                        result.text,
                        title=f"[bold]{name}[/bold]",
                        subtitle=subtitle,
                        expand=True,
                    )
                )
            else:
                panels.append(
                    Panel(
                        "[dim]waiting...[/dim]",
                        title=f"[bold]{name}[/bold]",
                        expand=True,
                    )
                )

        return Group(*panels)

    def __enter__(self):
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=4,
        )
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        if self._live:
            self._live.__exit__(*args)
            self._live = None
