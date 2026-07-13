# scripts/make_info_card.py
def generate_info_card(output_path):
    # Customize these fields
    name = "Umar Aftab"
    title = "AI Engineer · Full-Stack Developer"
    experience = "2+ years building AI systems"
    stack = "Python, FastAPI, React, TensorFlow, Docker"
    highlights = "LLM Agents, Computer Vision, Healthcare AI"

    svg = f"""<svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font-size: 24px; font-weight: bold; fill: #00ff88; }}
    .label {{ font-size: 14px; fill: #888; }}
    .value {{ font-size: 16px; fill: #fff; }}
    .section {{ margin-bottom: 20px; }}
  </style>
  <text x="20" y="30" class="title">{name}</text>
  <text x="20" y="60" class="value">{title}</text>
  <text x="20" y="90" class="label">Experience:</text>
  <text x="20" y="110" class="value">{experience}</text>
  <text x="20" y="140" class="label">Stack:</text>
  <text x="20" y="160" class="value">{stack}</text>
  <text x="20" y="190" class="label">Highlights:</text>
  <text x="20" y="210" class="value">{highlights}</text>
  <rect x="10" y="240" width="480" height="1" fill="#444" />
  <text x="20" y="260" class="label">GitHub: UmarAftab174</text>
</svg>"""
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"Info card SVG saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python make_info_card.py <output_svg>")
        sys.exit(1)
    generate_info_card(sys.argv[1])