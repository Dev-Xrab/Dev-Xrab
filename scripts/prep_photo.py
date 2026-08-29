from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUTPUT = Path("source-prepped.png")

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py source-photo.jpg")

    source = Path(sys.argv[1])
    if not source.exists():
        raise SystemExit(f"File not found: {source}")

    image = Image.open(source).convert("RGBA")
    cutout = remove(image)

    # Composite the transparent subject onto white.
    white = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, cutout).convert("RGB")

    rgb = np.array(composited)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Local contrast enhancement.
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Mild contrast stretch.
    p2, p98 = np.percentile(enhanced, (2, 98))
    if p98 > p2:
        enhanced = np.clip((enhanced - p2) * 255.0 / (p98 - p2), 0, 255).astype(np.uint8)

    Image.fromarray(enhanced, mode="L").save(OUTPUT)
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
