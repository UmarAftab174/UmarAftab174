# scripts/make_ascii_svg.py
"""Render an ASCII-art portrait as an animated terminal-window SVG.

The portrait is sampled to a roughly *square* aspect (correcting for the tall
monospace character cell, which is what made the old output vertically long)
and each row wipes in left-to-right, staggered top-to-bottom, like a script
typing into a terminal. Output is well-formed XML because GitHub serves SVGs
as image/svg+xml and a strict parser silently drops a malformed document.
"""

# 10 ramp steps, dense (dark pixels) -> light (bright pixels)
ASCII_CHARS = "@%#*+=-:. "

# ---- geometry ----------------------------------------------------------
COLS = 140            # sampled columns (higher = more facial detail)
CHAR_W = 8.0          # px width of one monospace cell at FONT_SIZE
LINE_H = 15.0         # px height of one text row
FONT_SIZE = 12.9
PAD = 20              # left/right padding inside the window
TITLE_H = 30          # title-bar height

PROMPT = "umar@github: ~$ ./portrait.sh"
WHOAMI_USER = "umar@github"
WHOAMI_NAME = "Umar Aftab"

ACCENT = "#39d353"    # green prompt accent (GitHub contribution green)
FG = "#c9d1d9"        # ascii glyph color
MUTED = "#7d8590"     # title / prompt chrome


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def image_to_ascii(image_path, cols=COLS):
    from PIL import Image, ImageOps, ImageEnhance
    import numpy as np

    img = Image.open(image_path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.5)  # separate face from background
    # center-crop to a square so the face keeps its proportions
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    # rows chosen so cols*CHAR_W ~= rows*LINE_H -> square once rendered
    rows = max(1, round(cols * CHAR_W / LINE_H))
    img = img.resize((cols, rows))
    arr = np.asarray(img)
    scale = (len(ASCII_CHARS) - 1) / 255.0
    return ["".join(ASCII_CHARS[int(p * scale)] for p in row) for row in arr]


def ascii_to_svg(lines):
    cols = max((len(ln) for ln in lines), default=COLS)
    text_w = cols * CHAR_W
    W = round(PAD * 2 + text_w)
    y0 = TITLE_H + 18                       # first baseline
    last = y0 + (len(lines) - 1) * LINE_H
    whoami_y = last + LINE_H * 2
    H = round(whoami_y + 22)
    dur = 0.05                              # per-row wipe duration

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#111722"/>'
        '<stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
        f'fill="none" stroke="#30363d" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="#30363d"/>',
        '<circle cx="20" cy="15" r="5" fill="#ff5f56"/>'
        '<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="52" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{W / 2:.1f}" y="19" fill="{MUTED}" font-size="12" '
        f'text-anchor="middle">{_esc(PROMPT)}</text>',
    ]

    for i, line in enumerate(lines):
        begin = round(i * dur, 3)
        y = y0 + i * LINE_H
        clip = f"r{i}"
        p.append(
            f'<clipPath id="{clip}"><rect x="{PAD}" y="{y - 12:.1f}" '
            f'height="{LINE_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{text_w}" '
            f'begin="{begin}s" dur="{dur}s" fill="freeze"/></rect></clipPath>'
        )
        p.append(
            f'<g clip-path="url(#{clip})"><text xml:space="preserve" x="{PAD}" '
            f'y="{y:.1f}" fill="{FG}" font-size="{FONT_SIZE}" '
            f'textLength="{text_w}" lengthAdjust="spacing">{_esc(line)}</text></g>'
        )

    # bottom whoami prompt, revealed after the portrait finishes
    reveal = round(len(lines) * dur + 0.1, 3)
    prefix = f"{WHOAMI_USER}:~$ whoami "
    whoami_chars = len(prefix) + len(WHOAMI_NAME)
    whoami_w = whoami_chars * 7.4
    cursor_x = PAD + whoami_w + 3
    p.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{reveal}s"/>'
        f'<text xml:space="preserve" x="{PAD}" y="{whoami_y:.1f}" font-size="13" '
        f'textLength="{whoami_w:.1f}" lengthAdjust="spacing">'
        f'<tspan fill="{ACCENT}">{_esc(WHOAMI_USER)}</tspan>'
        f'<tspan fill="{MUTED}">:~$ whoami </tspan>'
        f'<tspan fill="{FG}">{_esc(WHOAMI_NAME)}</tspan></text>'
        f'<rect x="{cursor_x:.1f}" y="{whoami_y - 11:.1f}" width="7" height="13" '
        f'fill="{FG}"><animate attributeName="opacity" values="1;0;1" dur="1s" '
        f'repeatCount="indefinite"/></rect></g>'
    )
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python make_ascii_svg.py <prepped_photo> <output_svg>")
        sys.exit(1)
    svg = ascii_to_svg(image_to_ascii(sys.argv[1]))
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"ASCII SVG saved to {sys.argv[2]}")
