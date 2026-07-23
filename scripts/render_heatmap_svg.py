#!/usr/bin/env python3
"""
Renders data/contributions.json as an animated contribution heatmap SVG.
Boxes reveal diagonally on load, then freeze — no loop.
Output: contrib-heatmap.svg

Usage:
  python scripts/render_heatmap_svg.py
"""
import json
import os
from datetime import date, timedelta

# ── theme ─────────────────────────────────────────────────────────────────────
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none      → level 5 (neon top-end for visibility)
BG      = "#0d1117"
BORDER  = "#30363d"
TEXT    = "#8b949e"
FONT    = "'Courier New', Courier, monospace"
# ── layout ────────────────────────────────────────────────────────────────────
BOX      = 11   # px, box size
GAP      = 3    # px, gap between boxes
STEP     = BOX + GAP
MONTH_H  = 18   # px, space above grid for month labels
DAY_W    = 26   # px, space left of grid for day labels
PAD_X    = 14
PAD_Y    = 10
FOOT_H   = 28   # px, stats footer
# ── animation ─────────────────────────────────────────────────────────────────
DIAG_STEP = 0.010   # seconds per diagonal wave step
BOX_DUR   = 0.14    # seconds per box reveal
# ─────────────────────────────────────────────────────────────────────────────

MONTHS  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DOW     = ["", "Mon", "", "Wed", "", "Fri", ""]   # empty strings = no label


def load(path: str = "data/contributions.json") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found — run fetch_contributions.py first.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_grid(days: list[dict]) -> list[list[dict]]:
    """Return 53 columns × 7 rows (Sun=row 0) covering last 52 weeks."""
    day_map = {d["date"]: d for d in days}
    today = date.today()

    # Rewind to the Sunday that starts the oldest visible week
    start = today - timedelta(weeks=52)
    while start.weekday() != 6:   # Python: Mon=0 … Sun=6
        start -= timedelta(days=1)

    cols: list[list[dict]] = []
    cur = start
    while cur <= today + timedelta(days=6):
        col: list[dict] = []
        for _ in range(7):
            key = cur.isoformat()
            col.append(day_map.get(key, {"date": key, "level": 0, "count": 0}))
            cur += timedelta(days=1)
        cols.append(col)
        if len(cols) >= 53:
            break
    return cols


def month_labels(cols: list[list[dict]]) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    prev = None
    for i, col in enumerate(cols):
        m = int(col[0]["date"][5:7])
        if m != prev:
            labels.append((i, MONTHS[m - 1]))
            prev = m
    return labels


def render(data: dict) -> str:
    cols = build_grid(data["days"])
    n_cols = len(cols)
    mlabels = month_labels(cols)

    svg_w = PAD_X * 2 + DAY_W + n_cols * STEP
    svg_h = PAD_Y * 2 + MONTH_H + 7 * STEP + FOOT_H

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}">',
        f'  <rect width="100%" height="100%" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>',
    ]

    # Month labels
    for ci, label in mlabels:
        x = PAD_X + DAY_W + ci * STEP
        y = PAD_Y + MONTH_H - 4
        parts.append(f'  <text x="{x}" y="{y}" font-family="{FONT}" font-size="10" fill="{TEXT}">{label}</text>')

    # Day-of-week labels
    for ri, label in enumerate(DOW):
        if not label:
            continue
        x = PAD_X + DAY_W - 4
        y = PAD_Y + MONTH_H + ri * STEP + BOX
        parts.append(f'  <text x="{x}" y="{y}" font-family="{FONT}" font-size="9" fill="{TEXT}" text-anchor="end">{label}</text>')

    # Grid boxes
    for ci, col in enumerate(cols):
        for ri, day in enumerate(col):
            level = min(day["level"], len(PALETTE) - 1)
            color = PALETTE[level]
            x = PAD_X + DAY_W + ci * STEP
            y = PAD_Y + MONTH_H + ri * STEP
            delay = f"{(ci + ri) * DIAG_STEP:.3f}s"
            tip = f"{day['count']} contributions on {day['date']}"
            parts.append(
                f'  <rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" values="0;1" dur="{BOX_DUR}s" begin="{delay}" fill="freeze"/>'
                f"<title>{tip}</title></rect>"
            )

    # Legend
    leg_box_w = BOX + 2
    leg_total_w = 6 * leg_box_w + 36  # 6 boxes + labels
    leg_x = svg_w - PAD_X - leg_total_w
    leg_y = svg_h - PAD_Y - 4
    parts.append(
        f'  <text x="{leg_x}" y="{leg_y}" font-family="{FONT}" font-size="10" fill="{TEXT}" text-anchor="end">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        bx = leg_x + i * leg_box_w
        parts.append(f'  <rect x="{bx}" y="{leg_y - BOX + 2}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
    parts.append(
        f'  <text x="{leg_x + 6 * leg_box_w + 4}" y="{leg_y}" font-family="{FONT}" font-size="10" fill="{TEXT}">More</text>'
    )

    # Stats footer
    total   = data.get("total_contributions", 0)
    streak  = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    stats   = f"{total:,} contributions · {streak}d current streak · {longest}d best"
    parts.append(
        f'  <text x="{PAD_X}" y="{svg_h - PAD_Y - 4}" font-family="{FONT}" font-size="10" fill="{TEXT}">{stats}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = load()
    svg = render(data)
    out = os.environ.get("OUTPUT", "contrib-heatmap.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Heatmap -> {out}")
