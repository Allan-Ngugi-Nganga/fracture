"""fracture daemon — entry point for window tracking."""

import argparse
import os
import signal
import sys
import time
from pathlib import Path

from .watcher import ActivityWatcher, ActivityStore, SWITCH_COST_MINUTES

PID_PATH = Path.home() / ".fracture" / "daemon.pid"


def run_watcher(foreground: bool = True):
    """Start the activity watcher."""
    watcher = ActivityWatcher()
    watcher.start()

    print(f"fracture — tracking window switches")
    print(f"  data: ~/.fracture/events.db")
    print(f"  switch cost: {SWITCH_COST_MINUTES} min per switch (research)")
    if foreground:
        print(f"  press Ctrl+C to stop")

    if not foreground:
        return

    def _handle(sig, frame):
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()


def main():
    parser = argparse.ArgumentParser(
        description="fracture — measure your brain's fragmentation tax",
    )
    parser.add_argument(
        "--daemon", action="store_true",
        help="Run in background",
    )
    parser.add_argument(
        "--stop", action="store_true",
        help="Stop background daemon",
    )
    parser.add_argument(
        "--dashboard", action="store_true",
        help="Open the fragmentation dashboard",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show today's stats and exit",
    )
    parser.add_argument(
        "--_bg", action="store_true",
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    if args.stop:
        if PID_PATH.exists():
            try:
                pid = int(PID_PATH.read_text().strip())
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped fracture (PID {pid})")
            except (ProcessLookupError, OSError):
                print("Daemon not running")
            PID_PATH.unlink(missing_ok=True)
        else:
            print("No daemon running")
        return

    if args.daemon:
        if PID_PATH.exists():
            try:
                pid = int(PID_PATH.read_text().strip())
                os.kill(pid, 0)
                print(f"Daemon already running (PID {pid})")
                return
            except (ProcessLookupError, ValueError):
                PID_PATH.unlink(missing_ok=True)

        import subprocess
        cmd = [sys.executable, "-m", "fracture.daemon", "--_bg"]
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
        PID_PATH.write_text(str(proc.pid))
        print(f"Daemon started (PID {proc.pid})")
        return

    if getattr(args, "_bg", False):
        run_watcher(foreground=False)
        return

    if args.dashboard:
        from .dashboard import run_dashboard
        run_dashboard()
        return

    if args.status:
        store = ActivityStore()
        stats = store.get_today_stats()
        print(f"\nfracture — today's fragmentation")
        print(f"  total switches:   {stats['total_switches']}")
        print(f"  productive:       {stats['productive_switches']} (creation)")
        print(f"  lost to switching: {stats['lost_minutes']:.0f} min ({stats['lost_hours']:.1f} h)")
        print(f"  active window:    {stats['active_hours']:.1f} h")
        print(f"  effective work:   {stats['effective_hours']:.1f} h")
        if stats["zone_counts"]:
            print(f"  breakdown:")
            for zone, count in sorted(stats["zone_counts"].items()):
                print(f"    {zone}: {count}")
        return

    # Default: run in foreground
    run_watcher(foreground=True)


if __name__ == "__main__":
    main()
