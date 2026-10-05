"""Stage 2: dot data (.npy) -> animated terminal banner SVGs (dark + light).

    python assets/banner/banner.py assets   # needs data/ from portrait.py
"""
import base64
import io
import sys
from pathlib import Path

import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).parent
DATA = HERE / "data"
W, H = 1180, 610
GW, GH = 300, 340

THEMES = {
    "dark": dict(win="#121214", bar="#18181b", line="#2a292e", dots="#ece7df", chrome="#ff7a45",
                 label="#8b867d", value="#ece7df", leader="#3a3940", live="#ef4444", pill_text="#121214"),
    "light": dict(win="#f7f4ee", bar="#efebe3", line="#e0dbd1", dots="#1c1b18", chrome="#d9541e",
                  label="#76716a", value="#1c1b18", leader="#cfc9be", live="#dc2626", pill_text="#ffffff"),
}

INFO = [
    [("Subject", "Muhammad Saad"),
     ("Role", "AI Engineer & Full-Stack Developer"),
     ("Origin", "Lahore, Pakistan"),
     ("Education", "BS Computer Science · UMT"),
     ("Status", "Building + Shipping + Learning"),
     ("ToolChain", "VS Code, Git, Docker, Claude Code")],
    [("Core.Lang", "TypeScript, Python, Dart"),
     ("Core.Frontend", "React, Next.js, Flutter, Tauri"),
     ("Core.Backend", "FastAPI, Fastify, Node.js"),
     ("Core.Database", "PostgreSQL, Prisma, Firebase"),
     ("Core.Infra", "Vercel, Netlify, GitHub Actions")],
    [("Grid.Mail", "saad39587@gmail.com"),
     ("Grid.Portfolio", "saadshahid-portfolio.vercel.app"),
     ("Grid.LinkedIn", "in/saadshahidpk"),
     ("Grid.GitHub", "github.com/saad92005")],
]

# Loop timeline (seconds): portrait 3.0 | 1.3 | logo 2.0 | 1.3 | logo 2.0 | 1.3 | logo 2.0 | 1.3
LOOP = 14.2
INTRO = 3.2


def kt(*secs):
    return ";".join(f"{s / LOOP:.4f}" for s in secs)


def mono_face(text):
    f = TTFont(HERE.parent / "src" / "fonts" / "JetBrainsMono[wght].ttf")
    f = instancer.instantiateVariableFont(f, {"wght": 500})
    s = subset.Subsetter(subset.Options())
    s.populate(text="".join(sorted(set(text + " "))))
    s.subset(f)
    b = io.BytesIO()
    f.save(b)
    return f"@font-face{{font-family:'M';src:url(data:font/ttf;base64,{base64.b64encode(b.getvalue()).decode()}) format('truetype');}}"


def runs_path(xy):
    """Horizontal runs of grid cells -> compact path data (1x1 cells, crisp)."""
    if len(xy) == 0:
        return ""
    order = np.lexsort((xy[:, 0], xy[:, 1]))
    pts = xy[order]
    out, i = [], 0
    while i < len(pts):
        x, y = pts[i]
        j = i
        while j + 1 < len(pts) and pts[j + 1, 1] == y and pts[j + 1, 0] == pts[j, 0] + 1:
            j += 1
        out.append(f"M{x} {y}h{j - i + 1}v1h-{j - i + 1}z")
        i = j + 1
    return "".join(out)


def portrait_layers(theme, t, scale, ox, oy):
    xy = np.load(DATA / f"{theme}_xy.npy")
    intro = np.load(DATA / f"{theme}_intro.npy")
    bands = np.load(DATA / f"{theme}_bands.npy")
    travel = np.load(DATA / f"{theme}_travel.npy")  # (4, N, 2)
    rng = np.random.default_rng(3)

    # Intro: 60 interleaved random groups, each fading in at its own moment within ~2s
    intro_paths = []
    for g in range(60):
        d = rng.uniform(0.15, 2.0)
        intro_paths.append(f'<path class="ig" style="animation-delay:{d:.2f}s" d="{runs_path(xy[intro == g])}"/>')

    # Loop: 94 drift bands translate ~42% toward the first logo's centroid while fading, then return
    target = travel[1].mean(0)
    band_paths = []
    for b in np.unique(bands):
        pts = xy[bands == b]
        dx, dy = 0.42 * (target - pts.mean(0))
        band_paths.append(
            f'<path d="{runs_path(pts)}">'
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="{kt(0, 3.0, 4.3, 12.9, LOOP)}" '
            f'dur="{LOOP}s" begin="{INTRO}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1;.5 0 .3 1"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{dx:.1f} {dy:.1f};{dx:.1f} {dy:.1f};0 0" '
            f'keyTimes="{kt(0, 3.0, 4.3, 12.9, LOOP)}" dur="{LOOP}s" begin="{INTRO}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1;.5 0 .3 1"/></path>')

    # Travellers: ~900 dots, portrait -> python -> typescript -> flutter -> portrait (OT-matched)
    stops = [travel[0], travel[0], travel[1], travel[1], travel[2], travel[2], travel[3], travel[3], travel[0]]
    times = [0, 3.0, 4.3, 6.3, 7.6, 9.6, 10.9, 12.9, LOOP]
    spl = ";".join(["0 0 1 1" if i % 2 == 0 else ".55 0 .25 1" for i in range(len(times) - 1)])
    trav = []
    for k in range(travel.shape[1]):
        vals = ";".join(f"{p[k, 0]:.1f} {p[k, 1]:.1f}" for p in stops)
        trav.append(f'<rect width="1.7" height="1.7" x="-.35" y="-.35"><animateTransform attributeName="transform" type="translate" '
                    f'values="{vals}" keyTimes="{kt(*times)}" calcMode="spline" keySplines="{spl}" dur="{LOOP}s" begin="{INTRO}s" repeatCount="indefinite"/></rect>')
    trav_op = (f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt(0, 3.0, 4.3, 12.9, LOOP)}" '
               f'dur="{LOOP}s" begin="{INTRO}s" repeatCount="indefinite"/>')

    return f"""
<g transform="translate({ox} {oy}) scale({scale})" fill="{t['dots']}" shape-rendering="crispEdges">
  <g class="intro">{''.join(intro_paths)}</g>
  <g class="loop">{''.join(band_paths)}</g>
  <g opacity="0">{trav_op}{''.join(trav)}</g>
</g>"""


def info_panel(t, x0, x1, y0):
    cw = 14 * 0.6  # JetBrains Mono advance at 14px
    width = x1 - x0
    cols = int(width // cw)
    rows, y, i = [], y0, 0
    for gi, group in enumerate(INFO):
        for label, value in group:
            n_lead = cols - len(label) - len(value) - 2
            leader = "." * max(3, n_lead)
            delay = 0.35 + i * 0.07
            rows.append(
                f'<text class="row" style="animation-delay:{delay:.2f}s" x="{x0}" y="{y}" textLength="{width}" lengthAdjust="spacingAndGlyphs">'
                f'<tspan fill="{t["label"]}">{label}</tspan><tspan fill="{t["leader"]}"> {leader} </tspan>'
                f'<tspan fill="{t["value"]}">{value.replace("&", "&amp;")}</tspan></text>')
            y += 23
            i += 1
        y += 15
    return "".join(rows)


def build(theme):
    t = THEMES[theme]
    text = "profile.sh --live VISUAL.MAP SYSTEM.INFO LIVE @saad92005 " + "".join(l + v for g in INFO for l, v in g) + ". +·&"
    css = mono_face(text)
    px, py, pw, ph = 30, 78, 436, 500           # portrait frame
    scale = min((pw - 28) / GW, (ph - 28) / GH)
    ox = px + (pw - GW * scale) / 2
    oy = py + (ph - GH * scale) / 2
    rx0, rx1 = 500, 1148
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{css}
text{{font-family:M,monospace}}
.ig{{opacity:0;animation:in .9s ease-out forwards}}
@keyframes in{{to{{opacity:1}}}}
.intro{{animation:hide 0s {INTRO}s forwards}}
@keyframes hide{{to{{opacity:0}}}}
.loop{{opacity:0;animation:show 0s {INTRO}s forwards}}
@keyframes show{{to{{opacity:1}}}}
.row{{font-size:14px;opacity:0;animation:row .5s ease-out forwards}}
@keyframes row{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
.live{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.25}}}}
</style>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="14" fill="{t['win']}" stroke="{t['line']}"/>
<path d="M8 50V22a14 14 0 0 1 14-14h{W - 44}a14 14 0 0 1 14 14v28z" fill="{t['bar']}"/>
<line x1="8" y1="50" x2="{W - 8}" y2="50" stroke="{t['line']}"/>
<circle cx="34" cy="29" r="6" fill="{t['line']}"/><circle cx="54" cy="29" r="6" fill="{t['line']}"/><circle cx="74" cy="29" r="6" fill="{t['chrome']}"/>
<text x="{W / 2}" y="34" text-anchor="middle" font-size="13" fill="{t['label']}">profile.sh --live</text>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="none" stroke="{t['line']}"/>
<rect x="{px + 14}" y="{py - 9}" width="96" height="18" fill="{t['win']}"/>
<text x="{px + 20}" y="{py + 4}" font-size="12" fill="{t['chrome']}" letter-spacing="1.5">VISUAL.MAP</text>
{portrait_layers(theme, t, scale, ox, oy)}
<text x="{rx0}" y="98" font-size="13" fill="{t['chrome']}" letter-spacing="1.5">SYSTEM.INFO</text>
<g class="live"><circle cx="{rx1 - 52}" cy="94" r="5" fill="{t['live']}"/></g>
<text x="{rx1}" y="98" text-anchor="end" font-size="12" fill="{t['live']}" letter-spacing="1.5">LIVE</text>
<line x1="{rx0}" y1="112" x2="{rx1}" y2="112" stroke="{t['line']}"/>
<rect x="{rx0}" y="128" width="124" height="28" rx="14" fill="{t['chrome']}"/>
<text x="{rx0 + 62}" y="147" text-anchor="middle" font-size="14" fill="{t['pill_text']}">@saad92005</text>
{info_panel(t, rx0, rx1, 190)}
</svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for th in THEMES:
        p = out / f"banner-{th}.svg"
        p.write_text(build(th), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size / 1024:.0f} KB")
