"""Quick test for fracture imports and zone classification."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fracture.watcher import classify_window, ActivityStore, SWITCH_COST_MINUTES

tests = [
    ("main.py - VS Code", "creation"),
    ("Slack | #general", "communication"),
    ("Twitter / X", "consumption"),
    ("Settings", "admin"),
    ("Untitled", "unknown"),
]

all_pass = True
for title, expected in tests:
    got = classify_window(title)
    status = "OK" if got == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{status:4s} {title:30s} -> {got:15s} (expected {expected})")

store = ActivityStore()
stats = store.get_today_stats()
print(f"\nStore OK — today: {stats['total_switches']} switches")
print(f"Lost: {stats['lost_minutes']:.0f} min")

if all_pass:
    print("\nOK")
else:
    print("\nSome tests failed")
    sys.exit(1)
