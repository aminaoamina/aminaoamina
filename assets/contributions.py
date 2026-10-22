"""Draw the contribution calendar as an SVG in the profile's flame colors.

Input: the JSON returned by GitHub's GraphQL API (see .github/workflows/contributions.yml).
Usage:  python assets/contributions.py contributions.json dist/contributions.svg
"""
import json
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
TEXT = "#8B949E"     # readable on GitHub's light and dark themes
EMPTY = "#8B949E"    # drawn at low opacity so it works on both themes
LEVELS = {           # GitHub's quartiles, mapped to the hero's flame colors
    "FIRST_QUARTILE": "#7A2E0E",
    "SECOND_QUARTILE": "#C2410C",
    "THIRD_QUARTILE": "#F97316",
    "FOURTH_QUARTILE": "#FFB454",
}

CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 34, 46


def calendar(data):
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def square(x, y, level):
    if level in LEVELS:
        return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[level]}"/>'
    return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{EMPTY}" fill-opacity="0.16"/>'


def render(cal):
    weeks = cal["weeks"]
    width = LEFT + len(weeks) * STEP + 8
    height = TOP + 7 * STEP + 34
    parts = [
        f'<text x="0" y="16" font-size="15" font-weight="600" fill="{TEXT}">'
        f'{cal["totalContributions"]} contributions in the last year</text>'
    ]

    last_month = None
    for col, week in enumerate(weeks):
        x = LEFT + col * STEP
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and col < len(weeks) - 2:
            parts.append(f'<text x="{x}" y="{TOP - 8}" font-size="11" fill="{TEXT}">{first.strftime("%b")}</text>')
            last_month = first.month
        for day in week["contributionDays"]:
            parts.append(square(x, TOP + day["weekday"] * STEP, day["contributionLevel"]))

    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="0" y="{TOP + row * STEP + 9}" font-size="11" fill="{TEXT}">{label}</text>')

    lx = width - 8 - 5 * STEP - 34
    ly = TOP + 7 * STEP + 14
    parts.append(f'<text x="{lx - 32}" y="{ly + 9}" font-size="11" fill="{TEXT}">Less</text>')
    for i, level in enumerate(["NONE", *LEVELS]):
        parts.append(square(lx + i * STEP, ly, level))
    parts.append(f'<text x="{lx + 5 * STEP + 4}" y="{ly + 9}" font-size="11" fill="{TEXT}">More</text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{escape(FONT)}">\n  '
            + "\n  ".join(parts) + "\n</svg>\n")


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    cal = calendar(json.loads(src.read_text(encoding="utf-8")))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render(cal), encoding="utf-8")
    print(f"wrote {dst}: {cal['totalContributions']} contributions, {len(cal['weeks'])} weeks")


if __name__ == "__main__":
    main()
