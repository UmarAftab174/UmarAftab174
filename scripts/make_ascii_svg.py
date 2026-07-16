# scripts/make_ascii_svg.py
import cv2
import numpy as np

ASCII_CHARS = "@%#*+=-:. "

def image_to_ascii(image_path, width=80):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    # Resize to fixed width, maintain aspect ratio
    height = int(img.shape[0] * width / img.shape[1])
    img = cv2.resize(img, (width, height))

    # Normalize and map to ASCII
    ascii_str = ""
    for row in img:
        for pixel in row:
            index = int(pixel / 255 * (len(ASCII_CHARS) - 1))
            ascii_str += ASCII_CHARS[index]
        ascii_str += "\n"

    # Generate SVG with typing animation
    svg = f"""<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes type {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
    text {{
      font-family: "Courier New", monospace;
      font-size: 12px;
      fill: white;
      animation: type 0.1s steps(1) forwards;
    }}
  </style>
  <text x="10" y="20" font-size="12">
{ascii_str.replace("\n", '<tspan x="10" dy="1.2em">')}
  </text>
</svg>"""
    return svg

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python make_ascii_svg.py <prepped_photo> <output_svg>")
        sys.exit(1)
    svg_content = image_to_ascii(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"ASCII SVG saved to {sys.argv[2]}")