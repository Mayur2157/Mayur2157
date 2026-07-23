# Setup Guide — Mayur's Animated GitHub Profile

## Step 1 — Create the magic repo

GitHub renders `<username>/<username>/README.md` at the top of your profile.

```bash
gh repo create Mayur2157 --public --clone
cd Mayur2157
```

Or create it manually at github.com/new (name it exactly `Mayur2157`, tick "Add README").

## Step 2 — Copy these files in

Drop every file from this bundle into the repo root.

## Step 3 — Local Python environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r scripts/requirements.txt
```

## Step 4 — Prep your photo (run once)

Drop a clear, well-lit headshot (JPEG or PNG) in the repo root and run:

```bash
python scripts/prep_photo.py your-photo.jpg
# → source-prepped.png
```

Tips for best results:
- Plain or simple background works best (rembg handles messy ones too)
- Good lighting = high-contrast ASCII art
- Face should fill at least 60% of the frame

## Step 5 — Generate the ASCII SVG

```bash
python scripts/make_ascii_svg.py
# → mayur-ascii.svg
```

Open `mayur-ascii.svg` in a browser to preview the animation.

## Step 6 — Generate the info card

```bash
python scripts/make_info_card.py
# → info-card.svg
```

Edit `LINES` in `scripts/make_info_card.py` to update any details.
`STATIC=1 python scripts/make_info_card.py` gives a frozen preview.

## Step 7 — Generate the heatmap

```bash
python scripts/fetch_contributions.py
# → data/contributions.json

python scripts/render_heatmap_svg.py
# → contrib-heatmap.svg
```

## Step 8 — Commit everything

```bash
git add .
git commit -m "feat: animated profile README"
git push
```

Visit github.com/Mayur2157 — your animated profile is live.

## Step 9 — Enable the daily auto-refresh

Go to your repo → Actions tab → "Update profile art" → Run workflow.

This confirms the bot can commit. After that it runs automatically every day at 06:17 UTC.

## Updating details later

| What changed | Command to re-run |
|---|---|
| New photo | `prep_photo.py` → `make_ascii_svg.py` |
| Job / stack info | Edit `LINES` in `make_info_card.py` → `make_info_card.py` |
| Heatmap only | `fetch_contributions.py` → `render_heatmap_svg.py` (Actions does this daily) |
