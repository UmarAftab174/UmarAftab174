# scripts/make_info_card.py
"""Render a neofetch-style info card as a terminal-window SVG.

Content is mapped from the existing profile (nothing invented). Lines fade in
staggered top-to-bottom to match the portrait's "loads from top" feel, and the
document is well-formed XML so GitHub renders it as image/svg+xml.
"""

ACCENT = "#39d353"    # green labels / section headers (brand accent)
FG = "#c9d1d9"        # values
MUTED = "#7d8590"     # chrome / rule
TITLE = "umar@github: ~$ neofetch"

# ---- geometry ----------------------------------------------------------
FONT_SIZE = 19
CHAR_W = FONT_SIZE * 0.6
LINE_H = 32
PAD = 26
TITLE_H = 34

# Each line is a list of (text, color, bold) segments. [] renders as a gap.
LINES = [
    [("umar@github", ACCENT, True)],
    [("-----------", MUTED, False)],
    [("Role   ", ACCENT, False), ("AI Engineer · Full-Stack Developer", FG, False)],
    [("Club   ", ACCENT, False), ("BU AI Club President", FG, False)],
    [("Edu    ", ACCENT, False), ("BS Artificial Intelligence, Bahria University", FG, False)],
    [],
    [("─ Stack", ACCENT, True)],
    [("Python, FastAPI, React, TensorFlow, Docker", FG, False)],
    [],
    [("─ Highlights", ACCENT, True)],
    [("LLM Agents · Computer Vision · Healthcare AI", FG, False)],
]


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_info_card(output_path):
    cols = max((sum(len(t) for t, _, _ in segs) for segs in LINES), default=40)
    text_w = cols * CHAR_W
    W = round(PAD * 2 + text_w)
    y0 = TITLE_H + 24
    H = round(y0 + len(LINES) * LINE_H + 8)
    dur = 0.12

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs><linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#111722"/>'
        '<stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg2)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
        f'fill="none" stroke="#30363d" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="#30363d"/>',
        '<circle cx="20" cy="17" r="5" fill="#ff5f56"/>'
        '<circle cx="36" cy="17" r="5" fill="#ffbd2e"/>'
        '<circle cx="52" cy="17" r="5" fill="#27c93f"/>',
        f'<text x="{W / 2:.1f}" y="21" fill="{MUTED}" font-size="12" '
        f'text-anchor="middle">{_esc(TITLE)}</text>',
    ]

    for i, segs in enumerate(LINES):
        if not segs:
            continue
        y = y0 + i * LINE_H
        begin = round(i * dur, 3)
        spans = []
        for text, color, bold in segs:
            weight = ' font-weight="bold"' if bold else ""
            spans.append(f'<tspan fill="{color}"{weight}>{_esc(text)}</tspan>')
        p.append(
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
            f'font-size="{FONT_SIZE}" opacity="0">{"".join(spans)}'
            f'<set attributeName="opacity" to="1" begin="{begin}s"/></text>'
        )

    p.append("</svg>")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(p))
    print(f"Info card SVG saved to {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python make_info_card.py <output_svg>")
        sys.exit(1)
    generate_info_card(sys.argv[1])
