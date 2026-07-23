#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion:
  1. Remove background (rembg)
  2. Boost local contrast (CLAHE via OpenCV)
  3. Composite onto pure white so background → spaces in the ramp
Output: source-prepped.png
Run once per photo: python scripts/prep_photo.py source-photo.jpg
"""
import io
import sys
import numpy as np
from PIL import Image
import cv2
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png") -> None:
    with open(input_path, "rb") as f:
        raw = f.read()

    # Step 1 — remove background
    removed = remove(raw)
    img_rgba = Image.open(io.BytesIO(removed)).convert("RGBA")

    # Crop to the bounding box of the person to remove empty margins
    bbox = img_rgba.getbbox()
    if bbox:
        img_rgba = img_rgba.crop(bbox)
        # Zoom/crop to head & shoulders (top 60% of the bounding box)
        w, h = img_rgba.size
        img_rgba = img_rgba.crop((0, 0, w, int(h * 0.60)))
        # Re-crop to bounding box to remove left/right transparent padding after height crop
        bbox2 = img_rgba.getbbox()
        if bbox2:
            img_rgba = img_rgba.crop(bbox2)

    # Step 2 — composite onto white
    white_bg = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img_rgba).convert("RGB")

    # Step 3 — CLAHE contrast boost on L channel
    img_cv = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_eq = clahe.apply(l)
    result_bgr = cv2.cvtColor(cv2.merge([l_eq, a, b]), cv2.COLOR_LAB2BGR)

    Image.fromarray(cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)).save(output_path)
    print(f"[OK] Saved prepped photo -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
