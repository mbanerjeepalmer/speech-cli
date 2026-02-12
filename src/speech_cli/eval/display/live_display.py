"""Rich Live TUI for side-by-side transcription display."""

import math
import threading
from typing import Optional

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from speech_cli.eval.providers.base import TranscriptionResult


class TranscriptionDisplay:
    """Thread-safe Rich Live display for transcription results.

    Supports two modes:
    - single-line: one row per provider, text tailed to terminal width
    - multi-line: one Panel per provider with full wrapped text

    Also supports partial (streaming) text and recording status.
    """

    def __init__(self, mode: str = "single-line") -> None:
        self.mode = mode
        self.console = Console()
        self._providers: list[str] = []
        self._results: dict[str, TranscriptionResult] = {}
        self._partials: dict[str, str] = {}
        self._lock = threading.Lock()
        self._live: Optional[Live] = None

        # Recording status
        self._recording = False
        self._rec_elapsed = 0.0
        self._rec_level = 0.0

    def set_providers(self, provider_names: list[str]) -> None:
        """Set the list of providers being evaluated."""
        self._providers = list(provider_names)

    def update_result(self, provider_name: str, result: TranscriptionResult) -> None:
        """Thread-safe update of a provider's final result."""
        with self._lock:
            self._results[provider_name] = result
            self._partials.pop(provider_name, None)
            if self._live:
                self._live.update(self._render())

    def update_partial(self, provider_name: str, text: str) -> None:
        """Thread-safe update of a provider's partial (in-progress) text."""
        with self._lock:
            self._partials[provider_name] = text
            if self._live:
                self._live.update(self._render())

    def update_recording_status(
        self, elapsed: float, level: float, is_recording: bool
    ) -> None:
        """Update the recording indicator shown as a header."""
        with self._lock:
            self._recording = is_recording
            self._rec_elapsed = elapsed
            self._rec_level = level
            if self._live:
                self._live.update(self._render())

    def _render(self):
        """Render current state based on display mode."""
        parts = []

        if self._recording:
            parts.append(self._render_recording_status())

        if self.mode == "multi-line":
            parts.append(self._render_multi_line())
        else:
            parts.append(self._render_single_line())

        if len(parts) == 1:
            return parts[0]
        return Group(*parts)

    def _render_recording_status(self):
        """Render a recording indicator bar."""
        mins, secs = divmod(int(self._rec_elapsed), 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # sqrt-scaled level bar so it responds to normal speech levels
        bar_width = 20
        scaled = math.sqrt(min(self._rec_level * 5.0, 1.0))
        filled = int(scaled * bar_width)
        bar = "\u2588" * filled + "\u2591" * (bar_width - filled)

        return Text.from_markup(
            f"  [bold red]\u25cf REC[/bold red]  {time_str}  [{bar}]"
        )

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
            partial = self._partials.get(name)

            if result:
                text = result.text
                if len(text) > text_width:
                    text = text[-text_width:]
                time_str = f"{result.processing_time_seconds:.1f}s" if result.processing_time_seconds else "..."
                table.add_row(name, time_str, text)
            elif partial:
                text = partial
                if len(text) > text_width:
                    text = text[-text_width:]
                table.add_row(name, "[dim]...[/dim]", text + " \u2588")
            else:
                table.add_row(name, "[dim]...[/dim]", "[dim]waiting...[/dim]")

        return table

    def _render_multi_line(self):
        """One Panel per provider with full wrapped text."""
        panels = []
        for name in self._providers:
            result = self._results.get(name)
            partial = self._partials.get(name)

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
            elif partial:
                panels.append(
                    Panel(
                        partial + " \u2588",
                        title=f"[bold]{name}[/bold]",
                        subtitle="streaming...",
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
