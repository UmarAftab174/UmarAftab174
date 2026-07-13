# scripts/prep_photo.py
import cv2
import numpy as np
from PIL import Image

def preprocess_photo(input_path, output_path):
    # Read image
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image at {input_path}")

    # Remove background (simple thresholding for demo; use rembg for better results)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.bitwise_not(thresh)

    # Apply CLAHE for contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Save prepped image
    cv2.imwrite(output_path, enhanced)
    print(f"Prepped photo saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python prep_photo.py <input_photo> <output_prepped>")
        sys.exit(1)
    preprocess_photo(sys.argv[1], sys.argv[2])