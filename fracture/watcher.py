"""Window activity tracker with zone classification.

Watches active window titles via pygetwindow, classifies each window
into a zone (creation/communication/consumption/admin), and stores
every switch in SQLite with timestamps."""

import os
import re
import sqlite3
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_DIR = Path.home() / ".fracture"
DB_PATH = DATA_DIR / "events.db"


# Zone classification rules — window title patterns mapped to zones
ZONE_RULES: list[tuple[str, str]] = [
    # Creation
    ("code", "creation"), ("vim", "creation"), ("neovim", "creation"),
    ("nvim", "creation"), ("emacs", "creation"), ("terminal", "creation"),
    ("powershell", "creation"), ("cmd.exe", "creation"), ("bash", "creation"),
    ("zsh", "creation"), ("vscode", "creation"), ("visual studio code", "creation"),
    ("cursor", "creation"), ("jetbrains", "creation"), ("pycharm", "creation"),
    ("intellij", "creation"), ("webstorm", "creation"), ("sublime text", "creation"),
    ("notepad++", "creation"), ("obsidian", "creation"), ("logseq", "creation"),
    ("notion", "creation"), ("figma", "creation"), ("canva", "creation"),
    ("photoshop", "creation"), ("ableton", "creation"),
    # Communication
    ("slack", "communication"), ("teams", "communication"), ("discord", "communication"),
    ("telegram", "communication"), ("whatsapp", "communication"), ("messenger", "communication"),
    ("signal", "communication"), ("zoom", "communication"), ("meet", "communication"),
    ("outlook", "communication"), ("thunderbird", "communication"), ("mail", "communication"),
    ("gmail", "communication"), ("calendar", "communication"), ("google chat", "communication"),
    ("mattermost", "communication"), ("skype", "communication"),
    # Consumption
    ("chrome", "consumption"), ("firefox", "consumption"), ("edge", "consumption"),
    ("safari", "consumption"), ("brave", "consumption"), ("opera", "consumption"),
    ("twitter", "consumption"), ("x.com", "consumption"), ("reddit", "consumption"),
    ("youtube", "consumption"), ("netflix", "consumption"), ("spotify", "consumption"),
    ("instagram", "consumption"), ("facebook", "consumption"), ("tiktok", "consumption"),
    ("linkedin", "consumption"), ("news", "consumption"), ("medium", "consumption"),
    ("mastodon", "consumption"), ("bluesky", "consumption"), ("hacker news", "consumption"),
    # Admin
    ("explorer", "admin"), ("finder", "admin"), ("settings", "admin"),
    ("control panel", "admin"), ("preferences", "admin"), ("file explorer", "admin"),
    ("task manager", "admin"), ("activity monitor", "admin"), ("system preferences", "admin"),
    ("steam", "admin"), ("epic games", "admin"),
]

# Classification cache to avoid re-parsing every poll
_classify_cache: dict[str, str] = {}


def classify_window(title: str) -> str:
    """Classify a window title into a zone.

    Returns one of: creation, communication, consumption, admin, unknown.
    """
    if not title:
        return "unknown"
    title_lower = title.lower()

    # Check cache
    if title in _classify_cache:
        return _classify_cache[title]

    # Match against rules
    for pattern, zone in ZONE_RULES:
        if pattern in title_lower:
            _classify_cache[title] = zone
            return zone

    # Heuristic: if title contains a file extension or IDE-like patterns
    if re.search(r'\.[a-z]{2,4}\s', title_lower) or re.search(r'[-–—].*edit', title_lower):
        _classify_cache[title] = "creation"
        return "creation"

    # Default
    _classify_cache[title] = "unknown"
    return "unknown"


@dataclass
class ZoneConfig:
    """Per-zone configuration."""
    name: str
    label: str
    color: str
    is_productive: bool = False

ZONES = {
    "creation":      ZoneConfig("creation", "Creation",      "#10b981", is_productive=True),
    "communication": ZoneConfig("communication", "Communication", "#f59e0b", is_productive=False),
    "consumption":   ZoneConfig("consumption",   "Consumption",   "#ef4444", is_productive=False),
    "admin":         ZoneConfig("admin",         "Admin",         "#6366f1", is_productive=False),
    "unknown":       ZoneConfig("unknown",       "Unknown",       "#94a3b8", is_productive=False),
}

SWITCH_COST_MINUTES = 23  # research: ~23 min to regain deep focus
SWITCH_COST_SECONDS = SWITCH_COST_MINUTES * 60


class ActivityStore:
    """Thread-safe SQLite store for window activity events."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self._db_path = str(db_path)
        self._local = threading.local()
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not getattr(self._local, "conn", None):
            self._local.conn = sqlite3.connect(self._db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone TEXT NOT NULL,
                title TEXT NOT NULL,
                timestamp REAL NOT NULL,
                session_id TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)
        """)
        conn.commit()
        conn.close()

    def record_switch(self, zone: str, title: str, session_id: str, ts: Optional[float] = None):
        if ts is None:
            ts = time.time()
        with self._lock:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "INSERT INTO events (zone, title, timestamp, session_id) VALUES (?, ?, ?, ?)",
                (zone, title, ts, session_id),
            )
            conn.commit()
            conn.close()

    def get_today_stats(self) -> dict:
        """Get today's fragmentation stats."""
        today_start = time.mktime(datetime.now().date().timetuple())
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        total = conn.execute(
            "SELECT COUNT(*) as c FROM events WHERE timestamp >= ?", (today_start,)
        ).fetchone()["c"]

        zone_counts = {}
        for row in conn.execute(
            "SELECT zone, COUNT(*) as c FROM events WHERE timestamp >= ? GROUP BY zone",
            (today_start,),
        ).fetchall():
            zone_counts[row["zone"]] = row["c"]

        # First event today
        first = conn.execute(
            "SELECT timestamp FROM events WHERE timestamp >= ? ORDER BY timestamp ASC LIMIT 1",
            (today_start,),
        ).fetchone()
        first_ts = first["timestamp"] if first else None

        # Last event today
        last = conn.execute(
            "SELECT timestamp FROM events WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 1",
            (today_start,),
        ).fetchone()
        last_ts = last["timestamp"] if last else None

        conn.close()

        # Calculate productive switches
        productive = sum(zone_counts.get(z, 0) for z in ["creation"])
        switches = total
        lost_minutes = switches * SWITCH_COST_MINUTES
        active_hours = (last_ts - first_ts) / 3600 if first_ts and last_ts else 0

        return {
            "total_switches": switches,
            "zone_counts": zone_counts,
            "productive_switches": productive,
            "lost_minutes": lost_minutes,
            "lost_hours": lost_minutes / 60,
            "active_hours": active_hours,
            "first_event": first_ts,
            "last_event": last_ts,
            "effective_hours": max(0, active_hours - (lost_minutes / 60)),
        }

    def get_current_session_id(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")


class ActivityWatcher:
    """Background thread that polls active window and records switches."""

    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval
        self.store = ActivityStore()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_title: Optional[str] = None
        self._current_zone: Optional[str] = None
        self._session_id = self.store.get_current_session_id()

    def _poll_loop(self):
        import pygetwindow as gw

        while self._running:
            try:
                active = gw.getActiveWindow()
                if active and active.title:
                    title = active.title
                    zone = classify_window(title)

                    if title != self._current_title:
                        self._current_title = title
                        self._current_zone = zone
                        self.store.record_switch(zone, title, self._session_id)

                # Rotate session daily
                new_sid = self.store.get_current_session_id()
                if new_sid != self._session_id:
                    self._session_id = new_sid

            except Exception:
                pass

            time.sleep(self.poll_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
