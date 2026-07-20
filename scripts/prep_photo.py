#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion.
Run once per photo: python scripts/prep_photo.py source-photo.jpg
Uses rembg for background removal + OpenCV CLAHE for local contrast.
"""

import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(input_path, output_path="assets/source-prepped.png"):
    # Load image
    img = Image.open(input_path).convert("RGBA")

    # Remove background with rembg
    print("Removing background...")
    img_no_bg = remove(img)

    # Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(img_no_bg), cv2.COLOR_RGBA2BGRA)

    # Split channels
    b, g, r, a = cv2.split(cv_img)

    # Apply CLAHE to each RGB channel for local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    b = clahe.apply(b)
    g = clahe.apply(g)
    r = clahe.apply(r)

    # Merge back with alpha
    cv_enhanced = cv2.merge([b, g, r, a])

    # Convert back to PIL
    enhanced = Image.fromarray(cv2.cvtColor(cv_enhanced, cv2.COLOR_BGRA2RGBA))

    # Composite onto pure white background
    white_bg = Image.new("RGBA", enhanced.size, (255, 255, 255, 255))
    white_bg.paste(enhanced, mask=enhanced.split()[3])  # use alpha as mask

    # Convert to grayscale
    gray = white_bg.convert("L")

    # Resize preserving aspect ratio (max 400px)
    gray.thumbnail((400, 400), Image.LANCZOS)

    # Final autocontrast
    from PIL import ImageOps

    gray = ImageOps.autocontrast(gray, cutoff=2)

    gray.save(output_path)
    print(f"Saved prepped image: {output_path} ({gray.size})")


if __name__ == "__main__":
    photo = sys.argv[1] if len(sys.argv) > 1 else "assets/portrait.jpg"
    prep(photo)
