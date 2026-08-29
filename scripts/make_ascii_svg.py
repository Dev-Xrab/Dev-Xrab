from pathlib import Path
from html import escape
from PIL import Image, ImageOps

SOURCE = Path("source-prepped.png")
OUTPUT = Path("profile-ascii.svg")

COLS = 82
ROWS = 48
RAMP = " .`:-=+*cs#%@"

CHAR_W = 7.2
CHAR_H = 12.0
PAD_X = 12
PAD_Y = 16

FG = "#c9d1d9"
CURSOR = "#39d353"
BG = "#0d1117"

def pixel_to_char(value: int) -> str:
    # white -> sparse; black -> dense
    darkness = 255 - value
    index = round((darkness / 255) * (len(RAMP) - 1))
    return RAMP[index]

def main():
    if not SOURCE.exists():
        raise SystemExit(
            "source-prepped.png does not exist.\n"
            "Run: python scripts/prep_photo.py source-photo.jpg"
        )

    image = Image.open(SOURCE).convert("L")
    image = ImageOps.fit(image, (COLS, ROWS), method=Image.Resampling.LANCZOS)

    width = PAD_X * 2 + COLS * CHAR_W
    height = PAD_Y * 2 + ROWS * CHAR_H

    rows = []
    pixels = image.load()

    for y in range(ROWS):
        text = "".join(pixel_to_char(pixels[x, y]) for x in range(COLS)).rstrip()
        rows.append(text)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
        "<style>",
        f"text{{font-family:'Cascadia Mono','Consolas','Courier New',monospace;font-size:11px;fill:{FG};white-space:pre}}",
        "</style>",
        f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{width-1:.0f}" height="{height-1:.0f}" rx="14" fill="none" stroke="#30363d"/>',
        "<defs>",
    ]

    for i in range(ROWS):
        y = PAD_Y + i * CHAR_H
        parts.append(
            f'<clipPath id="clip{i}">'
            f'<rect x="{PAD_X}" y="{y-10:.2f}" width="0" height="{CHAR_H:.2f}">'
            f'<animate attributeName="width" from="0" to="{COLS*CHAR_W:.2f}" '
            f'begin="{i*0.035:.3f}s" dur="0.55s" fill="freeze"/>'
            f'</rect></clipPath>'
        )

    parts.append("</defs>")

    for i, row in enumerate(rows):
        y = PAD_Y + i * CHAR_H
        safe = escape(row)
        parts.append(
            f'<text x="{PAD_X}" y="{y:.2f}" clip-path="url(#clip{i})">{safe}</text>'
        )

    # Cursor sweeps across each row and disappears after the final row.
    for i, row in enumerate(rows):
        y = PAD_Y + i * CHAR_H - 10
        row_width = max(6, len(row) * CHAR_W)
        begin = i * 0.035
        parts.append(
            f'<rect x="{PAD_X}" y="{y:.2f}" width="5" height="11" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin:.3f}s"/>'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + row_width:.2f}" '
            f'begin="{begin:.3f}s" dur="0.55s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + 0.56:.3f}s"/>'
            f'</rect>'
        )

    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
