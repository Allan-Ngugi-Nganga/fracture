"""Textual TUI dashboard for fracture — shows fragmentation stats."""

import os
import time
from datetime import datetime
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, RichLog

from .watcher import ActivityStore, ZONES, SWITCH_COST_SECONDS


class MetricCard(Static):
    """A big stat card."""

    value = reactive("—")
    label: str
    color: str

    def __init__(self, label: str, color: str = "#10b981", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.color = color

    def watch_value(self, val: str):
        self.update(f"[bold {self.color}]{val}[/]\n[dim]{self.label}[/]")


class FractureDashboard(App):
    """Textual dashboard showing fragmentation stats."""

    CSS = """
    Screen {
        background: #0a0f16;
    }

    #layout {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        padding: 1;
        height: 100%;
    }

    #title-area {
        column-span: 2;
        border: solid #10b981;
        padding: 0 1;
        background: #0d1a12;
        height: 5;
    }

    #stats-grid {
        column-span: 2;
        layout: grid;
        grid-size: 4 1;
        grid-gutter: 1;
        height: 4;
    }

    .stat-card {
        border: solid #333;
        padding: 1;
        text-align: center;
        background: #111a22;
    }

    #zone-panel {
        border: solid #f59e0b;
        padding: 0 1;
        background: #1a1405;
    }

    #insight-panel {
        border: solid #444;
        padding: 0 1;
        background: #0a0a0a;
    }

    #zone-list {
        height: 100%;
    }

    #insight-log {
        height: 100%;
    }

    #footer-bar {
        column-span: 2;
        dock: bottom;
        height: 1;
        background: #10b981;
        color: #000;
        text-align: center;
    }

    #title-text {
        text-align: center;
        text-style: bold;
        color: #10b981;
    }

    #subtitle {
        text-align: center;
        color: #666;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.store = ActivityStore()
        self._refresh_interval = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="layout"):
            with Vertical(id="title-area"):
                yield Static("[bold]fracture — fragmentation dashboard[/]", id="title-text")
                yield Static("measuring your brain's context switch tax", id="subtitle")
            with Container(id="stats-grid"):
                yield MetricCard("Switches Today", color="#10b981", id="m-switches", classes="stat-card")
                yield MetricCard("Lost to Switching", color="#ef4444", id="m-lost", classes="stat-card")
                yield MetricCard("Effective Work", color="#f59e0b", id="m-effective", classes="stat-card")
                yield MetricCard("Active Window Time", color="#6366f1", id="m-active", classes="stat-card")
            with Vertical(id="zone-panel"):
                yield Static("[bold orange1]Zone Breakdown[/]", id="zone-title")
                yield RichLog(id="zone-list", markup=True, highlight=True)
            with Vertical(id="insight-panel"):
                yield Static("[bold #888]Insights[/]", id="insight-title")
                yield RichLog(id="insight-log", markup=True, highlight=True)
            yield Static("", id="footer-bar")
        yield Footer()

    def on_mount(self):
        self._refresh_interval = self.set_interval(5, self._refresh)
        self._refresh()

    def _refresh(self):
        stats = self.store.get_today_stats()

        # Update metric cards
        def set_card(wid: str, val: str):
            try:
                self.query_one(f"#{wid}", MetricCard).value = val
            except Exception:
                pass

        set_card("m-switches", str(stats["total_switches"]))
        set_card("m-lost", f"{stats['lost_minutes']:.0f}m")
        set_card("m-effective", f"{stats['effective_hours']:.1f}h")
        set_card("m-active", f"{stats['active_hours']:.1f}h")

        # Zone breakdown
        zones = self.query_one("#zone-list", RichLog)
        zones.clear()
        for zone_id, config in ZONES.items():
            count = stats["zone_counts"].get(zone_id, 0)
            pct = count / max(stats["total_switches"], 1) * 100
            bar = "█" * max(1, int(pct / 5))
            zones.write(f"[{config.color}]{bar}[/] [{config.color}]{config.label}[/] {count} ({pct:.0f}%)")

        # Insights
        insight = self.query_one("#insight-log", RichLog)
        insight.clear()

        if stats["total_switches"] > 0:
            insight.write(f"[dim]Today: {stats['total_switches']} switches[/]")
            insight.write(f"[dim]Lost: {stats['lost_minutes']:.0f} min to fragmentation[/]")

            if stats["effective_hours"] < 1:
                insight.write(f"[red]⚠ Effective work: {stats['effective_hours']:.1f}h[/]")
                insight.write("[red]   You've spent more time switching than working.[/]")
            elif stats["effective_hours"] < 3:
                insight.write(f"[yellow]Effective work: {stats['effective_hours']:.1f}h[/]")
                insight.write("[yellow]   Typical knowledge worker range.[/]")
            else:
                insight.write(f"[green]Effective work: {stats['effective_hours']:.1f}h[/]")
                insight.write("[green]   Strong focus day.[/]")

            # Show worst zone
            worst_zone = max(stats["zone_counts"], key=stats["zone_counts"].get)
            if worst_zone in ("consumption", "communication"):
                insight.write(f"\n[orange1]Top zone: {ZONES[worst_zone].label}[/]")
                insight.write(f"[orange1]   {stats['zone_counts'][worst_zone]} switches wasted here.[/]")

            # Quotable
            if stats["lost_minutes"] > 120:
                insight.write(f"\n[dim bold]\"Your brain is not a browser tab.\"[/]")
        else:
            insight.write("[dim]No activity recorded yet today.[/]")
            insight.write("[dim]Start fracture and switch between windows.[/]")

        # Footer
        footer = self.query_one("#footer-bar", Static)
        pct_lost = stats["lost_minutes"] / max(stats["active_hours"] * 60, 1) * 100
        footer.update(f"Fragmentation: {stats['total_switches']} switches | "
                      f"{stats['lost_minutes']:.0f}m lost ({pct_lost:.0f}% of active time) | "
                      f"{stats['effective_hours']:.1f}h effective")


def run_dashboard():
    app = FractureDashboard()
    app.run()
