# scripts/make_contribution_graph.py
"""Render the last year of GitHub contributions as a self-hosted area-chart SVG.

Replaces the previously-embedded third-party service (github-readme-activity-graph
on Vercel), which went offline. Contribution counts come straight from GitHub's
GraphQL API for the given user; nothing here depends on an external renderer.
"""
import os
import sys

import requests

BG = "#0d1117"
LINE = "#00ff88"
AREA = "#00ff8833"
POINT = "#ffffff"
TITLE = "#ffffff"
MUTED = "#7d8590"

W, H = 860, 220
PAD_L, PAD_R, PAD_T, PAD_B = 40, 20, 36, 30

GRAPHQL_URL = "https://api.github.com/graphql"
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch_contributions(login, token):
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"login": login}},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        (day["date"], day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    return calendar["totalContributions"], days


def render_svg(login, total, days):
    counts = [c for _, c in days]
    n = len(counts)
    max_count = max(counts) if any(counts) else 1

    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B
    step = plot_w / max(n - 1, 1)

    def x(i):
        return PAD_L + i * step

    def y(v):
        return PAD_T + plot_h - (v / max_count) * plot_h

    line_points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(counts))
    area_points = (
        f"{x(0):.1f},{PAD_T + plot_h:.1f} {line_points} "
        f"{x(n - 1):.1f},{PAD_T + plot_h:.1f}"
    )

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
        f'fill="none" stroke="#30363d" stroke-width="1"/>',
        f'<text x="{PAD_L}" y="24" fill="{TITLE}" font-size="15" font-weight="bold">'
        f'{_esc(login)}\'s GitHub contribution graph</text>',
        f'<text x="{W - PAD_R}" y="24" fill="{MUTED}" font-size="12" '
        f'text-anchor="end">{total} contributions in the last year</text>',
        f'<polygon points="{area_points}" fill="{AREA}"/>',
        f'<polyline points="{line_points}" fill="none" stroke="{LINE}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>',
    ]

    # markers on days with contributions (all-day markers would be too dense at this width)
    for i, v in enumerate(counts):
        if v > 0:
            p.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="1.8" fill="{LINE}"/>')

    # a handful of x-axis month labels, evenly spaced
    label_idxs = sorted(set([0] + [round(i * (n - 1) / 5) for i in range(1, 5)] + [n - 1]))
    for i in label_idxs:
        month = days[i][0][:7]  # YYYY-MM
        p.append(
            f'<text x="{x(i):.1f}" y="{H - 8}" fill="{MUTED}" font-size="10" '
            f'text-anchor="middle">{month}</text>'
        )

    # dot on the most recent day
    p.append(f'<circle cx="{x(n - 1):.1f}" cy="{y(counts[-1]):.1f}" r="3" fill="{POINT}"/>')

    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_contribution_graph.py <github_login> <output_svg>")
        sys.exit(1)

    login, output_path = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    total, days = fetch_contributions(login, token)
    svg = render_svg(login, total, days)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Contribution graph SVG saved to {output_path}")
