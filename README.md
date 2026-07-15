<h1 align="center">fracture</h1>
<p align="center">
  <em>Measure your brain's fragmentation tax.</em>
  <br>
  <br>
  <img src="https://img.shields.io/badge/python-≥3.10-10b981" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT License">
  <img src="https://img.shields.io/badge/version-0.1.0-10b981" alt="Version 0.1.0">
</p>

---

Every time you switch windows, your brain pays a tax. Research shows it takes ~23 minutes to fully regain deep focus after a context switch. Most knowledge workers switch windows **200+ times a day**. Nobody tracks the cumulative cost.

fracture is a background daemon that watches your active windows and measures your **fragmentation score** — the real cost of all those micro-switches you don't notice.

## Quick Start

```bash
pip install fracture
fracture             # start tracking (foreground)
fracture --daemon    # run in background
fracture --dashboard # open the fragmentation dashboard
fracture --status    # show today's stats
```

## How It Works

A lightweight daemon polls your active window title once per second via `pygetwindow`. Every time the window changes, it classifies the switch by zone and records it to a local SQLite database. No cloud, no telemetry, no accounts.

## Zones

| Zone | Examples | Classification |
|------|----------|---------------|
| **Creation** | VS Code, terminal, Obsidian, Figma | ✅ Productive |
| **Communication** | Slack, Teams, Discord, Outlook, Zoom | ❌ Fragmentation |
| **Consumption** | Chrome, Twitter, YouTube, Reddit | ❌ Fragmentation |
| **Admin** | Settings, Explorer, Finder, task manager | ❌ Fragmentation |

## The Dashboard

Run `fracture --dashboard` to see:
- Total window switches today
- Minutes lost to context switching
- Effective work hours (active time minus fragmentation tax)
- Zone breakdown with visual bars
- Contextual insights and recommendations

## Example Output

```
fracture — today's fragmentation
  total switches:   214
  productive:       47 (creation)
  lost to switching: 492 min (8.2 h)
  active window:    9.5 h
  effective work:   1.3 h
  breakdown:
    creation: 47
    communication: 89
    consumption: 62
    admin: 16
```

## FAQ

**Q: How accurate is the 23-minute number?**
A: It's based on peer-reviewed research (Mark et al., 2005, UC Irvine). The actual cost varies by person and task, but 23 minutes is the widely cited empirical finding.

**Q: Does this send data anywhere?**
A: No. All data stays in `~/.fracture/events.db`. No network requests, no tracking, no accounts.

**Q: What platforms are supported?**
A: Windows, macOS, and Linux. Requires a GUI environment (window title tracking doesn't work over SSH).

**Q: Can I reset my data?**
A: Delete `~/.fracture/events.db` to wipe all history.

## License

MIT

---

*Your brain is not a browser tab.*
