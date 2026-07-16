# scripts/make_ascii_svg.py
ASCII_CHARS = "@%#*+=-:. "

def image_to_ascii(image_path, width=80):
    import cv2  # imported lazily so ascii_to_svg works without OpenCV installed

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

    return ascii_to_svg(ascii_str)


def ascii_to_svg(ascii_str):
    """Wrap ASCII art in a well-formed SVG document.

    Each line becomes its own *closed* <tspan> so the result is valid XML —
    GitHub serves SVGs as image/svg+xml and a strict XML parser silently
    rejects the whole file if any tag is left open. A dark background rect
    keeps the light text readable in both GitHub light and dark themes, and
    the viewBox is sized to the content so nothing is clipped.
    """
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = ascii_str.rstrip("\n").split("\n")
    char_w, line_h, margin = 7.3, 14.4, 12
    cols = max((len(line) for line in lines), default=0)
    vb_w = round(margin * 2 + cols * char_w)
    vb_h = round(margin * 2 + (len(lines) + 1) * line_h)
    tspans = "".join(
        f'<tspan x="{margin}" dy="{line_h}">{esc(line)}</tspan>' for line in lines
    )

    return f"""<svg viewBox="0 0 {vb_w} {vb_h}" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes type {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    text {{
      font-family: "Courier New", monospace;
      font-size: 12px;
      fill: #e6edf3;
      animation: type 0.4s ease forwards;
    }}
  </style>
  <rect width="{vb_w}" height="{vb_h}" fill="#0d1117" />
  <text x="{margin}" y="{margin}">{tspans}</text>
</svg>"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python make_ascii_svg.py <prepped_photo> <output_svg>")
        sys.exit(1)
    svg_content = image_to_ascii(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"ASCII SVG saved to {sys.argv[2]}")