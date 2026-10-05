"""Animated profile headers. Self-contained SVGs: Inter (OFL) is subset and embedded,
animation is CSS + SMIL, nothing loads at view time.

    python assets/header.py        # writes assets/header-{a,b,c}-{dark,light}.svg
"""
import base64
import io
import math
import random
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).parent
FONT = HERE / "fonts" / "Inter[opsz,wght].ttf"
W, H = 1200, 340

NAME = "Muhammad Saad"
ROLE = "AI Engineer · Full-Stack Developer"
LINES = [
    "building AI agents that ask before they act",
    "shipping RAG that cites its sources",
    "turning business workflows into software",
]

THEMES = {
    "dark": dict(bg="#0b0f17", ink="#f2f4f8", muted="#8b95a7", faint="#1c2433", a1="#38bdf8", a2="#a78bfa", node="#cbd5e1"),
    "light": dict(bg="#ffffff", ink="#0f172a", muted="#5b6474", faint="#e6eaf0", a1="#0284c7", a2="#7c3aed", node="#334155"),
}


def face(family, weight, text):
    # Subset first (a few dozen glyphs), THEN instance: instancing the full variable
    # font is extremely slow.
    f = TTFont(FONT)
    s = subset.Subsetter(subset.Options())
    s.populate(text="".join(sorted(set(text + " "))))
    s.subset(f)
    f = instancer.instantiateVariableFont(f, {"wght": weight, "opsz": 32})
    f.recalcTimestamp = False  # deterministic bytes: no needless README commits
    f["head"].modified = f["head"].created
    b = io.BytesIO()
    f.save(b)
    return f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{base64.b64encode(b.getvalue()).decode()}) format('truetype');}}"


def text_block(t, x=72):
    """Name, role and the rotating line. Shared by all three designs."""
    n, cyc = len(LINES), 4.2 * len(LINES)
    css, svg = [], []
    for i, line in enumerate(LINES):
        a, b = i / n * 100, (i + 1) / n * 100
        css.append(
            f"@keyframes l{i}{{0%,{a:.2f}%{{opacity:0;clip-path:inset(0 100% 0 0)}}"
            f"{a + 0.2:.2f}%{{opacity:1;clip-path:inset(0 100% 0 0)}}"
            f"{a + 9:.2f}%,{b - 4:.2f}%{{opacity:1;clip-path:inset(0 0 0 0)}}"
            f"{b - 1:.2f}%,100%{{opacity:0;clip-path:inset(0 0 0 0)}}}}"
            f".l{i}{{animation:l{i} {cyc}s linear 1.1s infinite}}")
        svg.append(f'<text class="line l{i}" x="{x}" y="232">{line}</text>')
    style = f"""
.name{{font-family:B,sans-serif;font-size:62px;fill:{t['ink']};letter-spacing:-1.5px}}
.role{{font-family:M,sans-serif;font-size:21px;fill:{t['muted']}}}
.line{{font-family:M,sans-serif;font-size:19px;fill:url(#grad);opacity:0}}
.caret{{fill:{t['a1']};animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.u1{{animation:up .8s cubic-bezier(.2,.7,.2,1) .1s both}} .u2{{animation:up .8s cubic-bezier(.2,.7,.2,1) .3s both}}
.bar{{transform-origin:{x}px 0;animation:grow 1s cubic-bezier(.6,0,.2,1) .5s both}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
{''.join(css)}"""
    body = f"""
<g class="u1"><text class="name" x="{x - 3}" y="140">{NAME}</text></g>
<g class="u2"><text class="role" x="{x}" y="180">{ROLE}</text></g>
<rect class="bar" x="{x}" y="200" width="56" height="3" rx="1.5" fill="url(#grad)"/>
{''.join(svg)}"""
    return style, body


_fonts = None


def fonts():
    global _fonts
    if _fonts is None:
        _fonts = face("B", 800, NAME) + face("M", 500, ROLE + "".join(LINES) + "DataModelAgentProduct")
    return _fonts


def wrap(t, style, defs, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{fonts()}{style}</style>
<defs><linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>{defs}</defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t['bg']}"/>{body}</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['faint']}"/>
</svg>
"""


# ── A: neural network ──────────────────────────────────────────────
def design_a(t):
    rnd = random.Random(4)
    nodes = []
    for _ in range(5000):  # bounded: random packing may not fit a fixed count
        if len(nodes) >= 30:
            break
        x, y = rnd.uniform(640, 1160), rnd.uniform(30, H - 30)
        if all(math.dist((x, y), p) > 56 for p in nodes):
            nodes.append((x, y))
    edges = [(i, j) for i in range(len(nodes)) for j in range(i + 1, len(nodes)) if math.dist(nodes[i], nodes[j]) < 120]
    lines = "".join(f'<line x1="{nodes[i][0]:.0f}" y1="{nodes[i][1]:.0f}" x2="{nodes[j][0]:.0f}" y2="{nodes[j][1]:.0f}"/>' for i, j in edges)
    dots, pulses = [], []
    for k, (x, y) in enumerate(nodes):
        r = 2.4 if k % 5 else 4
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" class="n" style="animation-delay:{rnd.uniform(0, 4):.1f}s"/>')
    for k in range(9):
        i, j = edges[rnd.randrange(len(edges))]
        (x1, y1), (x2, y2) = nodes[i], nodes[j]
        dur, beg = rnd.uniform(2.2, 3.6), rnd.uniform(0, 3)
        pulses.append(
            f'<circle r="3" fill="url(#grad)"><animate attributeName="cx" values="{x1:.0f};{x2:.0f}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y1:.0f};{y2:.0f}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')
    st, tb = text_block(t)
    style = st + f"""
.edges line{{stroke:{t['node']};stroke-opacity:.14;stroke-width:1}}
.n{{fill:{t['node']};opacity:.55;animation:tw 4s ease-in-out infinite}}
@keyframes tw{{50%{{opacity:1}}}}
.net{{animation:drift 18s ease-in-out infinite alternate}}
@keyframes drift{{to{{transform:translate(-14px,6px)}}}}
.fadein{{animation:fi 1.6s .2s both}} @keyframes fi{{from{{opacity:0}}}}"""
    defs = f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}"/><stop offset=".35" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>'
    body = f'<g class="fadein"><g class="net"><g class="edges">{lines}</g>{"".join(dots)}{"".join(pulses)}</g></g><rect x="600" width="220" height="{H}" fill="url(#fade)"/>{tb}'
    return wrap(t, style, defs, body)


# ── B: aurora ──────────────────────────────────────────────────────
def design_b(t):
    st, tb = text_block(t)
    style = st + """
.glow{filter:url(#blur)}
.g1{animation:m1 16s ease-in-out infinite alternate} .g2{animation:m2 20s ease-in-out infinite alternate}
@keyframes m1{to{transform:translate(-160px,40px) scale(1.15)}}
@keyframes m2{to{transform:translate(120px,-30px) scale(.9)}}"""
    op = ".42" if t["bg"] != "#ffffff" else ".22"
    defs = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>'
    body = (f'<g class="glow" opacity="{op}"><ellipse class="g1" cx="930" cy="120" rx="230" ry="130" fill="{t["a1"]}"/>'
            f'<ellipse class="g2" cx="1050" cy="250" rx="200" ry="110" fill="{t["a2"]}"/></g>{tb}')
    return wrap(t, style, defs, body)


# ── C: pipeline ────────────────────────────────────────────────────
def design_c(t):
    st, tb = text_block(t)
    labels = ["Data", "Model", "Agent", "Product"]
    xs = [700, 820, 940, 1060]
    ys = [110, 230, 110, 230]
    boxes, links = [], []
    for k, (x, y, lab) in enumerate(zip(xs, ys, labels)):
        boxes.append(
            f'<g class="node" style="animation-delay:{0.4 + k * 0.25:.2f}s"><rect x="{x - 48}" y="{y - 26}" width="96" height="52" rx="12"/>'
            f'<text x="{x}" y="{y + 6}" text-anchor="middle">{lab}</text></g>')
    for k in range(3):
        x1, y1, x2, y2 = xs[k] + 48, ys[k], xs[k + 1] - 48, ys[k + 1]
        d = f"M{x1} {y1} C {x1 + 40} {y1}, {x2 - 40} {y2}, {x2} {y2}"
        links.append(f'<path class="link" d="{d}"/><path class="flow" d="{d}" style="animation-delay:{k * 0.4:.1f}s"/>'
                     f'<circle r="4" fill="url(#grad)"><animateMotion dur="2.4s" begin="{1.2 + k * 0.8:.1f}s" repeatCount="indefinite" path="{d}"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="2.4s" begin="{1.2 + k * 0.8:.1f}s" repeatCount="indefinite"/></circle>')
    style = st + f"""
.node rect{{fill:{t['bg']};stroke:{t['faint']};stroke-width:1.5}}
.node text{{font-family:M,sans-serif;font-size:16px;fill:{t['ink']}}}
.node{{animation:pop .6s cubic-bezier(.2,.8,.2,1.2) both}}
@keyframes pop{{from{{opacity:0;transform:translateY(10px)}}}}
.link{{fill:none;stroke:{t['faint']};stroke-width:1.5}}
.flow{{fill:none;stroke:url(#grad);stroke-width:1.5;stroke-dasharray:6 10;animation:dash 1.2s linear infinite}}
@keyframes dash{{to{{stroke-dashoffset:-16}}}}"""
    return wrap(t, style, "", "".join(links) + "".join(boxes) + tb)


if __name__ == "__main__":
    for key, fn in (("a", design_a), ("b", design_b), ("c", design_c)):
        for theme, t in THEMES.items():
            p = HERE / f"header-{key}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print(f"{p.name}: {p.stat().st_size / 1024:.0f} KB")
