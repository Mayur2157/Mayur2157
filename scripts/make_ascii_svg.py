#!/usr/bin/env python3
"""
Convert source-prepped.png into an animated ASCII SVG.
Each row wipes left-to-right; the portrait prints once and freezes.
Output: mayur-ascii.svg

Usage:
  python scripts/make_ascii_svg.py
  SOURCE=my-photo.png OUTPUT=mayur-ascii.svg python scripts/make_ascii_svg.py
"""
import os
import numpy as np
from PIL import Image

# ── tunables ──────────────────────────────────────────────────────────────────
RAMP = " .'-^:\";!iI?l1t[]{}()|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#%@"
COLS = 130                  # character columns
CHAR_ASPECT = 2.1          # terminal chars are ~2× taller than wide
SVG_CHAR_W = 7.0           # px per character column
SVG_CHAR_H = 13            # px per character row
FILL_COLOR = "#c9d1d9"     # GitHub dark-mode text gray
BG_COLOR = "transparent"
ROW_DUR = 0.028            # seconds per row wipe
# ─────────────────────────────────────────────────────────────────────────────


def img_to_ascii_color(img_path: str) -> list[list[tuple[str, str]]]:
    # Load grayscale image for character mapping
    img_gray = Image.open(img_path).convert("L")
    rows = max(1, int(COLS / CHAR_ASPECT * img_gray.height / img_gray.width))
    img_gray = img_gray.resize((COLS, rows), Image.LANCZOS)
    pixels_gray = np.array(img_gray)
    
    # Load RGB image for color mapping
    img_rgb = Image.open(img_path).convert("RGB")
    img_rgb = img_rgb.resize((COLS, rows), Image.LANCZOS)
    pixels_rgb = np.array(img_rgb)
    
    lines_data = []
    for r_idx in range(rows):
        row_data = []
        for c_idx in range(COLS):
            g = pixels_gray[r_idx, c_idx]
            char = RAMP[int((255 - g) / 255 * (len(RAMP) - 1))]
            rgb = pixels_rgb[r_idx, c_idx]
            r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            
            # Boost brightness for dark background visibility (minimum luminance of 50)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 50:
                if lum == 0:
                    r, g, b = 40, 40, 40
                else:
                    scale = 50.0 / lum
                    r = min(255, max(40, int(r * scale)))
                    g = min(255, max(40, int(g * scale)))
                    b = min(255, max(40, int(b * scale)))
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            row_data.append((char, hex_color))
        lines_data.append(row_data)
    return lines_data


def make_svg(lines_data: list[list[tuple[str, str]]]) -> str:
    n_rows = len(lines_data)
    n_cols = max(len(row) for row in lines_data)
    svg_w = n_cols * SVG_CHAR_W
    svg_h = n_rows * SVG_CHAR_H

    defs, texts = [], []

    for i, row in enumerate(lines_data):
        clip_id = f"clip{i}"
        start = f"{i * ROW_DUR:.3f}s"

        # Clip rect wipes left → right over one row duration
        defs.append(
            f'  <clipPath id="{clip_id}">'
            f'<rect x="0" y="{i * SVG_CHAR_H:.1f}" width="0" height="{SVG_CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{svg_w:.1f}" '
            f'dur="{ROW_DUR}s" begin="{start}" fill="freeze"/>'
            f"</rect></clipPath>"
        )

        row_content = ""
        current_color = None
        current_chars = []

        for char, color in row:
            escaped_char = (
                char.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            
            if char == " ":
                if current_chars:
                    row_content += (
                        f'<tspan fill="{current_color}">'
                        + "".join(current_chars)
                        + "</tspan>"
                    )
                    current_chars = []
                    current_color = None
                row_content += escaped_char
                continue

            if color == current_color:
                current_chars.append(escaped_char)
            else:
                if current_chars:
                    row_content += (
                        f'<tspan fill="{current_color}">'
                        + "".join(current_chars)
                        + "</tspan>"
                    )
                current_color = color
                current_chars = [escaped_char]

        if current_chars:
            row_content += (
                f'<tspan fill="{current_color}">'
                + "".join(current_chars)
                + "</tspan>"
            )

        y = (i + 1) * SVG_CHAR_H - 2
        texts.append(
            f'  <text clip-path="url(#{clip_id})" x="0" y="{y:.1f}" '
            f'font-family="\'Courier New\', Courier, monospace" '
            f'font-size="{SVG_CHAR_H - 1}" '
            f'xml:space="preserve">{row_content}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">\n'
        f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>\n'
        f"  <defs>\n" + "\n".join(defs) + "\n  </defs>\n"
        + "\n".join(texts)
        + "\n</svg>"
    )


if __name__ == "__main__":
    src = os.environ.get("SOURCE", "source-prepped.png")
    out = os.environ.get("OUTPUT", "mayur-ascii.svg")

    if not os.path.exists(src):
        print(f"✗ Source image not found: {src}")
        print("  Run prep_photo.py first, or set SOURCE= to your image path.")
        raise SystemExit(1)

    lines = img_to_ascii_color(src)
    svg = make_svg(lines)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] ASCII SVG -> {out}  ({len(lines)} rows x {len(lines[0])} cols)")
