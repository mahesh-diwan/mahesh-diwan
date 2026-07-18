#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion.
Run once per photo: python scripts/prep_photo.py source-photo.jpg
"""
import sys
from PIL import Image, ImageEnhance, ImageOps

def prep(input_path, output_path="source-prepped.png"):
    img = Image.open(input_path)

    # Resize for processing
    img = img.resize((400, 400), Image.LANCZOS)

    # Convert to grayscale
    gray = img.convert("L")

    # Boost contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.5)

    # Auto contrast
    gray = ImageOps.autocontrast(gray, cutoff=2)

    gray.save(output_path)
    print(f"Saved prepped image: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
