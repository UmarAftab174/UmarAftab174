# scripts/prep_photo.py
"""Prepare a source photo for ASCII conversion: grayscale + contrast boost."""
from PIL import Image, ImageOps


def preprocess_photo(input_path, output_path):
    img = Image.open(input_path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img.save(output_path)
    print(f"Prepped photo saved to {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python prep_photo.py <input_photo> <output_prepped>")
        sys.exit(1)
    preprocess_photo(sys.argv[1], sys.argv[2])
