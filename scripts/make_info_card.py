from pathlib import Path
from html import escape
import os

OUTPUT = Path("info-card.svg")

# EDIT THESE VALUES.
USERNAME = "Dev-Xrab"
DISPLAY_NAME = "Ben David"
ROLE = "Developer"
FOCUS = "Front and Backend  Development"
TOOLS = "Git · Linux · AI"
HOBBY = "BEMBANG"

ROWS = [
    ("name", DISPLAY_NAME),
    ("role", ROLE),
    ("focus", FOCUS),
    ("tools", TOOLS),
    ("hobby", HOBBY),
]

BG = "#0d1117"
FG = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#39d353"
BLUE = "#58a6ff"
BORDER = "#30363d"

WIDTH = 560
HEIGHT = 250

def main():
    static = os.getenv("STATIC") == "1"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        "text{font-family:'Cascadia Mono','Consolas','Courier New',monospace}",
        f".title{{font-size:18px;font-weight:700;fill:{GREEN}}}",
        f".key{{font-size:14px;font-weight:700;fill:{BLUE}}}",
        f".value{{font-size:14px;fill:{FG}}}",
        f".muted{{font-size:12px;fill:{MUTED}}}",
        "</style>",
        f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="14" fill="none" stroke="{BORDER}"/>',
        f'<circle cx="22" cy="20" r="5" fill="#ff5f56"/>',
        f'<circle cx="40" cy="20" r="5" fill="#ffbd2e"/>',
        f'<circle cx="58" cy="20" r="5" fill="#27c93f"/>',
        f'<text x="24" y="58" class="title">{escape(USERNAME)}@github</text>',
        f'<text x="24" y="80" class="muted">profile://whoami</text>',
    ]

    y = 116
    for i, (key, value) in enumerate(ROWS):
        delay = 0 if static else 0.15 + i * 0.12
        opacity = "1" if static else "0"
        transform = "" if static else ' transform="translate(0,8)"'
        parts.append(f'<g opacity="{opacity}"{transform}>')
        parts.append(f'<text x="24" y="{y}" class="key">{escape(key):<12}</text>')
        parts.append(f'<text x="142" y="{y}" class="value">{escape(value)}</text>')
        if not static:
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.28s" fill="freeze"/>'
            )
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" '
                f'begin="{delay:.2f}s" dur="0.28s" fill="freeze"/>'
            )
        parts.append("</g>")
        y += 27

    parts.extend([
        f'<line x1="24" y1="326" x2="536" y2="326" stroke="{BORDER}"/>',
        f'<text x="24" y="346" class="muted">$ build → debug → understand → repeat</text>',
        "</svg>",
    ])

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
