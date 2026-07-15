#!/usr/bin/env python3
"""Generate a realistic SVG mockup of the fracture dashboard for the README.
Matches the real Textual TUI: dark theme, green borders, zone bars, metric cards."""

import os

DASHBOARD_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600" width="900" height="600">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');
      text { font-family: 'JetBrains Mono', 'Courier New', monospace; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="900" height="600" fill="#0a0f16" rx="4"/>

  <!-- Title area with green border -->
  <rect x="10" y="10" width="880" height="50" fill="#0d1a12" stroke="#10b981" stroke-width="1.5" rx="3"/>
  <text x="450" y="35" fill="#10b981" font-size="16" font-weight="bold" text-anchor="middle">fracture — fragmentation dashboard</text>
  <text x="450" y="50" fill="#666" font-size="10" text-anchor="middle">measuring your brain's context switch tax</text>

  <!-- Metric cards (4-column grid) -->
  <!-- Switches Today -->
  <rect x="10" y="70" width="215" height="60" fill="#111a22" stroke="#333" stroke-width="1" rx="3"/>
  <text x="117" y="98" fill="#10b981" font-size="22" font-weight="bold" text-anchor="middle">214</text>
  <text x="117" y="120" fill="#666" font-size="11" text-anchor="middle">Switches Today</text>

  <!-- Lost to Switching -->
  <rect x="235" y="70" width="215" height="60" fill="#111a22" stroke="#333" stroke-width="1" rx="3"/>
  <text x="342" y="98" fill="#ef4444" font-size="22" font-weight="bold" text-anchor="middle">492m</text>
  <text x="342" y="120" fill="#666" font-size="11" text-anchor="middle">Lost to Switching</text>

  <!-- Effective Work -->
  <rect x="460" y="70" width="215" height="60" fill="#111a22" stroke="#333" stroke-width="1" rx="3"/>
  <text x="567" y="98" fill="#f59e0b" font-size="22" font-weight="bold" text-anchor="middle">1.3h</text>
  <text x="567" y="120" fill="#666" font-size="11" text-anchor="middle">Effective Work</text>

  <!-- Active Window Time -->
  <rect x="685" y="70" width="205" height="60" fill="#111a22" stroke="#333" stroke-width="1" rx="3"/>
  <text x="787" y="98" fill="#6366f1" font-size="22" font-weight="bold" text-anchor="middle">9.5h</text>
  <text x="787" y="120" fill="#666" font-size="11" text-anchor="middle">Active Window Time</text>

  <!-- Zone panel (left side) -->
  <rect x="10" y="140" width="530" height="310" fill="#1a1405" stroke="#f59e0b" stroke-width="1.5" rx="3"/>
  <text x="25" y="165" fill="#ffaa33" font-size="12" font-weight="bold">Zone Breakdown</text>

  <!-- Zone bars -->
  <!-- Creation: 47 switches -->
  <text x="25" y="200" fill="#10b981" font-size="13">███</text>
  <text x="90" y="200" fill="#10b981" font-size="12">Creation</text>
  <text x="480" y="200" fill="#888" font-size="12" text-anchor="end">47 (22%)</text>

  <!-- Communication: 89 switches -->
  <text x="25" y="230" fill="#f59e0b" font-size="13">███████</text>
  <text x="135" y="230" fill="#f59e0b" font-size="12">Communication</text>
  <text x="480" y="230" fill="#888" font-size="12" text-anchor="end">89 (42%)</text>

  <!-- Consumption: 62 switches -->
  <text x="25" y="260" fill="#ef4444" font-size="13">█████</text>
  <text x="120" y="260" fill="#ef4444" font-size="12">Consumption</text>
  <text x="480" y="260" fill="#888" font-size="12" text-anchor="end">62 (29%)</text>

  <!-- Admin: 16 switches -->
  <text x="25" y="290" fill="#6366f1" font-size="13">██</text>
  <text x="70" y="290" fill="#6366f1" font-size="12">Admin</text>
  <text x="480" y="290" fill="#888" font-size="12" text-anchor="end">16 (7%)</text>

  <!-- Insight panel (right side) -->
  <rect x="550" y="140" width="340" height="310" fill="#0a0a0a" stroke="#444" stroke-width="1.5" rx="3"/>
  <text x="565" y="165" fill="#888" font-size="12" font-weight="bold">Insights</text>

  <text x="565" y="195" fill="#666" font-size="11">Today: 214 switches</text>
  <text x="565" y="215" fill="#666" font-size="11">Lost: 492 min to fragmentation</text>

  <text x="565" y="245" fill="#ef4444" font-size="11" font-weight="bold">⚠ Effective work: 1.3h</text>
  <text x="565" y="263" fill="#ef4444" font-size="11">You've spent more time switching</text>
  <text x="565" y="279" fill="#ef4444" font-size="11">than working.</text>

  <text x="565" y="309" fill="#f59e0b" font-size="11">Top zone: Communication</text>
  <text x="565" y="327" fill="#f59e0b" font-size="11">89 switches wasted here.</text>

  <text x="565" y="357" fill="#555" font-size="11" font-style="italic">"Your brain is not a browser tab."</text>

  <!-- Footer bar -->
  <rect x="10" y="460" width="880" height="22" fill="#10b981" rx="2"/>
  <text x="450" y="476" fill="#000" font-size="11" font-weight="bold" text-anchor="middle">
    Fragmentation: 214 switches | 492m lost (86% of active time) | 1.3h effective
  </text>

  <!-- App border at bottom -->
  <rect x="10" y="490" width="880" height="100" fill="#0a0f16" stroke="#333" stroke-width="1" rx="3"/>
  <text x="450" y="530" fill="#444" font-size="11" text-anchor="middle">fracture — background daemon running (PID 14976)</text>
  <text x="450" y="555" fill="#333" font-size="10" text-anchor="middle">
    [f] fracture menu  [q] quit  [r] refresh  [?] toggle help
  </text>

  <!-- Watermark -->
  <text x="890" y="590" fill="#222" font-size="8" text-anchor="end">fragwatch v0.1.0</text>
</svg>'''

def generate(output_path: str = None) -> str:
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fracture_dashboard.svg")
    output_path = os.path.normpath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(DASHBOARD_SVG)
    return output_path


if __name__ == "__main__":
    path = generate()
    print(f"Dashboard SVG: {path}")
