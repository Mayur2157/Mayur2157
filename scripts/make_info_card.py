#!/usr/bin/env python3
"""
Generates a neofetch-style animated info card SVG — customised for Mayur Gadekar.
Each line fades in and slides up with a short stagger.
Output: info-card.svg

Usage:
  python scripts/make_info_card.py
  STATIC=1 python scripts/make_info_card.py   # frozen frame for local preview
"""
import os

STATIC = os.environ.get("STATIC", "0") == "1"

# ── theme ─────────────────────────────────────────────────────────────────────
BG          = "#0d1117"
BORDER      = "#30363d"
TITLE_COLOR = "#58a6ff"   # blue
KEY_COLOR   = "#79c0ff"   # lighter blue
VAL_COLOR   = "#c9d1d9"   # light gray
DIM_COLOR   = "#8b949e"   # muted gray
FONT        = "'Courier New', Courier, monospace"
FONT_SIZE   = 13
LINE_H      = 22
PAD_X       = 20
PAD_Y       = 16
SVG_W       = 490
STAGGER     = 0.055       # seconds between lines
# ─────────────────────────────────────────────────────────────────────────────

# (kind, key, value)
#   kind: "title" | "sep" | "kv" | "blank"
#   For "kv": key is left col, value is right col
LINES = [
    ("title", "mayur@imperative",               None),
    ("sep",   "─" * 32,                         None),
    ("kv",    "role",     "AI/ML Engineer"),
    ("kv",    "company",  "Imperative Business Ventures"),
    ("kv",    "edu",      "M.Tech AI · VNIT Nagpur"),
    ("blank", None,                              None),
    ("kv",    "stack",    "LangGraph · FastAPI · Gemini"),
    ("kv",    "        ", "RAG · Voice AI · LayoutLMv3"),
    ("kv",    "db",       "FAISS · ChromaDB · pgvector"),
    ("kv",    "infra",    "Docker · AWS · GCP Vertex AI"),
    ("blank", None,                              None),
    ("kv",    "building", "AI Voice Agents + Doc Intelligence"),
    ("kv",    "paper",    "IEEE 2025 · Vision-Language + RL"),
    ("kv",    "based",    "Pune, India"),
    ("blank", None,                              None),
    ("kv",    "github",   "github.com/Mayur2157"),
    ("kv",    "linkedin", "mayur-gadekar-a30619319"),
    ("kv",    "web",      "starlit-banoffee-727add.netlify.app"),
]

KEY_W = 76  # px reserved for key column


def _anim(idx: int) -> str:
    if STATIC:
        return ""
    begin = f"{idx * STAGGER:.3f}s"
    return (
        f'<animate attributeName="opacity" values="0;1" dur="0.2s" begin="{begin}" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0,6;0,0" dur="0.2s" begin="{begin}" fill="freeze"/>'
    )


def render() -> str:
    n = len(LINES)
    svg_h = PAD_Y * 2 + n * LINE_H + 4

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{svg_h}" '
        f'viewBox="0 0 {SVG_W} {svg_h}">',
        f'  <rect width="100%" height="100%" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>',
    ]

    for idx, (kind, key, val) in enumerate(LINES):
        y = PAD_Y + idx * LINE_H + LINE_H
        opacity_init = "1" if STATIC else "0"
        anim = _anim(idx)

        if kind == "title":
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE + 1}" '
                f'font-weight="bold" fill="{TITLE_COLOR}" opacity="{opacity_init}">'
                f'{anim}{key}</text>'
            )
        elif kind == "sep":
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}" '
                f'fill="{DIM_COLOR}" opacity="{opacity_init}" xml:space="preserve">'
                f'{anim}{key}</text>'
            )
        elif kind == "kv":
            parts.append(
                f'  <g opacity="{opacity_init}">{anim}'
                f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}" '
                f'fill="{KEY_COLOR}" xml:space="preserve">{key.rstrip()}</text>'
                f'<text x="{PAD_X + KEY_W}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}" '
                f'fill="{VAL_COLOR}" xml:space="preserve">: {val}</text>'
                f'</g>'
            )
        # "blank" → nothing rendered, just spacing

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    out = os.environ.get("OUTPUT", "info-card.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(render())
    print(f"[OK] Info card -> {out}")
