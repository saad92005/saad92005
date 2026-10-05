"""Stats card + contribution heatmap, drawn in the same style as the header.

Called by build_readme.py with real GitHub data; writes assets/{stats,activity}-{dark,light}.svg.
"""
from datetime import date
from pathlib import Path

from header import THEMES, face

HERE = Path(__file__).parent
W = 1200


def frame(t, h, css, defs, body, text):
    fonts = face("B", 800, text) + face("M", 500, text)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>{fonts}
.big{{font-family:B,sans-serif;font-size:44px;fill:{t['ink']};letter-spacing:-1px}}
.lbl{{font-family:M,sans-serif;font-size:15px;fill:{t['muted']}}}
.ttl{{font-family:M,sans-serif;font-size:13px;fill:{t['muted']};letter-spacing:2px}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
{css}</style>
<defs><linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{h}" rx="18"/></clipPath>{defs}</defs>
<g clip-path="url(#card)"><rect width="{W}" height="{h}" fill="{t['bg']}"/>{body}</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="{t['faint']}"/>
</svg>
"""


def stats_card(t, numbers, langs):
    """numbers: [(value, label)], langs: [(name, share 0..1)]"""
    h = 230
    x0 = 72
    cells, text = [], "BY THE NUMBERS LANGUAGES Other%0123456789.,"
    for i, (val, label) in enumerate(numbers):
        x = x0 + i * 190
        cells.append(f'<g style="animation:up .7s cubic-bezier(.2,.7,.2,1) {0.1 + i * 0.12:.2f}s both">'
                     f'<text class="big" x="{x}" y="128">{val}</text><text class="lbl" x="{x}" y="156">{label}</text></g>')
        text += str(val) + label
    # language bar
    bx, bw, by = 700, 428, 96
    shades = [t["a1"], t["a2"], "#60a5fa", "#c084fc", "#94a3b8", "#475569"] if t["bg"] != "#ffffff" else \
             [t["a1"], t["a2"], "#2563eb", "#9333ea", "#64748b", "#cbd5e1"]
    segs, legend, x = [], [], bx
    for i, (name, share) in enumerate(langs):
        w = bw * share
        segs.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{shades[i % len(shades)]}" '
                    f'style="transform-box:fill-box;transform-origin:left;animation:grow .9s cubic-bezier(.6,0,.2,1) {0.4 + i * 0.12:.2f}s both"/>')
        lx, ly = bx + (i % 2) * 214, 138 + (i // 2) * 26
        legend.append(f'<g style="animation:up .6s {0.7 + i * 0.08:.2f}s both"><circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{shades[i % len(shades)]}"/>'
                      f'<text class="lbl" x="{lx + 18}" y="{ly}">{name} <tspan fill="{t["ink"]}">{share * 100:.1f}%</tspan></text></g>')
        text += name
        x += w
    css = "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    body = (f'<text class="ttl" x="{x0}" y="62">BY THE NUMBERS</text><text class="ttl" x="{bx}" y="62">LANGUAGES</text>'
            + "".join(cells) + "".join(segs) + "".join(legend))
    return frame(t, h, css, "", body, text)


def activity_card(t, weeks, total, longest, current):
    """weeks: list of 7-length lists of (date, count)."""
    cell, gap = 15, 4
    cols = len(weeks)
    gw = cols * (cell + gap) - gap
    x0 = (W - gw) / 2
    y0 = 92
    mx = max([c for w in weeks for _, c in w] + [1])
    out = []
    for ci, wk in enumerate(weeks):
        for d, cnt in wk:
            ri = date.fromisoformat(d).isoweekday() % 7  # Sunday first, like GitHub
            if cnt == 0:
                fill, op = t["faint"], 1
            else:
                lvl = min(4, 1 + int(3 * cnt / mx + 0.0001)) if mx > 1 else 2
                fill, op = "url(#grad)", [0, .35, .55, .78, 1][lvl]
            out.append(f'<rect x="{x0 + ci * (cell + gap):.0f}" y="{y0 + ri * (cell + gap)}" width="{cell}" height="{cell}" rx="3.5" '
                       f'fill="{fill}" fill-opacity="{op}" style="animation-delay:{0.15 + ci * 0.018:.2f}s"/>')
    summary = f"{total:,} contributions in the last year  ·  longest streak {longest} days  ·  current streak {current} days"
    css = """.cells rect{animation:pop .5s ease-out both}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
.cells rect{transform-box:fill-box;transform-origin:center}"""
    body = (f'<text class="ttl" x="{x0}" y="62">ACTIVITY</text>'
            f'<text class="lbl" x="{x0 + gw}" y="62" text-anchor="end">{summary}</text>'
            f'<g class="cells">{"".join(out)}</g>')
    h = y0 + 7 * (cell + gap) + 40
    # gradient must span the grid, not each cell, so colours vary across the year
    defs = f'<linearGradient id="gridgrad" gradientUnits="userSpaceOnUse" x1="{x0}" x2="{x0 + gw}"><stop offset="0" stop-color="{t["a1"]}"/><stop offset="1" stop-color="{t["a2"]}"/></linearGradient>'
    svg = frame(t, h, css, defs, body, "ACTIVITY" + summary)
    return svg.replace('fill="url(#grad)" fill-opacity', 'fill="url(#gridgrad)" fill-opacity')


def streaks(days):
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c:
            current += 1
        elif i == 0:
            continue  # today with nothing yet doesn't break the streak
        else:
            break
    return longest, current


def write_all(numbers, langs, weeks, total):
    days = [d for w in weeks for d in w]
    longest, current = streaks(days)
    for theme, t in THEMES.items():
        (HERE / f"stats-{theme}.svg").write_text(stats_card(t, numbers, langs), encoding="utf-8")
        (HERE / f"activity-{theme}.svg").write_text(activity_card(t, weeks, total, longest, current), encoding="utf-8")
