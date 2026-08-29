from __future__ import annotations

from datetime import date, timedelta
from html import escape
from pathlib import Path
import json

SOURCE = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
BORDER = "#30363d"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 4
STEP = CELL + GAP
LEFT = 58
TOP = 62
WEEKS = 53
DAYS = 7
WIDTH = 950
HEIGHT = 235

DAY_LABELS = [(1, "Mon"), (3, "Wed"), (5, "Fri")]

def contribution_level(count: int, level: int) -> int:
    if level:
        return max(0, min(5, level))
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    if count <= 15:
        return 4
    return 5

def sunday_on_or_before(d: date) -> date:
    # Python weekday: Monday=0 ... Sunday=6
    return d - timedelta(days=(d.weekday() + 1) % 7)

def main():
    if not SOURCE.exists():
        raise SystemExit(
            "data/contributions.json missing.\n"
            "Run: python scripts/fetch_contributions.py"
        )

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    Dev-Xrab = data["Dev-Xrab"]
    raw_days = data["days"]
    stats = data["stats"]

    by_date = {
        date.fromisoformat(d["date"]): {
            "count": int(d.get("count", 0)),
            "level": int(d.get("level", 0)),
        }
        for d in raw_days
    }

    if not by_date:
        raise SystemExit("No contribution days found.")

    last_day = max(by_date)
    end_sunday = sunday_on_or_before(last_day) + timedelta(days=6)
    start_sunday = end_sunday - timedelta(weeks=WEEKS - 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        f"text{{font-family:'Cascadia Mono','Consolas','Courier New',monospace;fill:{FG}}}",
        f".muted{{fill:{MUTED};font-size:11px}}",
        ".title{font-size:16px;font-weight:700}",
        "@keyframes enter{0%{opacity:0;transform:translateY(-8px)}100%{opacity:1;transform:translateY(0)}}",
        ".day{opacity:0;animation:enter .32s ease-out forwards}",
        "</style>",
        f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="14" fill="none" stroke="{BORDER}"/>',
        f'<text x="24" y="30" class="title">{escape(Dev-Xrab)} / contributions</text>',
        f'<text x="24" y="48" class="muted">last 53 weeks · regenerated automatically</text>',
    ]

    for row, label in DAY_LABELS:
        y = TOP + row * STEP + CELL - 1
        parts.append(f'<text x="18" y="{y}" class="muted">{label}</text>')

    # Month labels at the first week where a month appears.
    shown_months = set()
    for week in range(WEEKS):
        d = start_sunday + timedelta(weeks=week)
        month_key = (d.year, d.month)
        if month_key not in shown_months and d.day <= 7:
            shown_months.add(month_key)
            x = LEFT + week * STEP
            parts.append(f'<text x="{x}" y="{TOP-10}" class="muted">{d.strftime("%b")}</text>')

    for week in range(WEEKS):
        for dow in range(DAYS):
            current = start_sunday + timedelta(weeks=week, days=dow)
            item = by_date.get(current, {"count": 0, "level": 0})
            level = contribution_level(item["count"], item["level"])
            x = LEFT + week * STEP
            y = TOP + dow * STEP
            delay = min(2.4, week * 0.025 + dow * 0.018)

            parts.append(
                f'<rect class="day" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{current.isoformat()}: {item["count"]} contributions</title>'
                f'</rect>'
            )

    footer_y = 203
    total = int(stats.get("total", 0))
    current = int(stats.get("current_streak", 0))
    longest = int(stats.get("longest_streak", 0))

    parts.append(
        f'<text x="24" y="{footer_y}" class="muted">'
        f'{total:,} contributions · current streak {current}d · longest {longest}d'
        f'</text>'
    )

    legend_x = 735
    parts.append(f'<text x="{legend_x}" y="{footer_y}" class="muted">Less</text>')
    for i, colour in enumerate(PALETTE):
        x = legend_x + 34 + i * 18
        parts.append(f'<rect x="{x}" y="{footer_y-10}" width="12" height="12" rx="2" fill="{colour}"/>')
    parts.append(f'<text x="{legend_x+148}" y="{footer_y}" class="muted">More</text>')

    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
