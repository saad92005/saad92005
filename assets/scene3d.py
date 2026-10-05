"""3D pieces, projected into plain animated SVG (GitHub can't run WebGL).

- header-3d-{theme}.svg : name block + a rotating, tilted point-sphere with orbiting satellites
- stack-{theme}.svg     : isometric exploded architecture of each featured project

Every point on the sphere rides its own projected ellipse (one animateMotion each,
phase set with a negative begin), and depth drives size + opacity, so a real
3D rotation costs a few KB instead of hundreds of keyframes.

    python assets/scene3d.py
"""
import math
from pathlib import Path

from header import H, THEMES, W, face, fonts, text_block

HERE = Path(__file__).parent
TILT = math.radians(22)
R = 118
CX, CY = 930, 170
SPIN = 28  # seconds per revolution


def f(v):
    return f"{v:.1f}"


def sphere(t):
    out = []
    # faint latitude rings: rotation about Y leaves them fixed on screen
    lats = [math.radians(a) for a in range(-75, 76, 15)]
    for phi in lats:
        rx, ry = R * math.cos(phi), R * math.cos(phi) * math.sin(TILT)
        yc = R * math.sin(phi) * math.cos(TILT)
        out.append(f'<ellipse cx="0" cy="{f(-yc)}" rx="{f(rx)}" ry="{f(ry)}" class="lat"/>')
    # points
    for phi in lats:
        n = max(4, round(22 * math.cos(phi)))
        rx, ry = R * math.cos(phi), R * math.cos(phi) * math.sin(TILT)
        yc = -R * math.sin(phi) * math.cos(TILT)
        path = f"M0 {f(yc - ry)}A{f(rx)} {f(ry)} 0 1 1 0 {f(yc + ry)}A{f(rx)} {f(ry)} 0 1 1 0 {f(yc - ry)}"
        # depth as a function of u (u=0 at the top of the projected ellipse = far side)
        steps = 12
        depth = []
        for k in range(steps + 1):
            u = 2 * math.pi * k / steps
            z = R * math.sin(phi) * math.sin(TILT) - R * math.cos(phi) * math.cos(u) * math.cos(TILT)
            depth.append((z + R) / (2 * R))
        ops = ";".join(f"{0.12 + 0.88 * d:.2f}" for d in depth)
        rs = ";".join(f"{0.9 + 2.1 * d:.2f}" for d in depth)
        for i in range(n):
            beg = -SPIN * i / n - (SPIN * 0.37 if lats.index(phi) % 2 else 0)
            hot = (i * 7 + lats.index(phi) * 3) % 11 == 0
            out.append(
                f'<circle class="{"hot" if hot else "pt"}" r="1.5">'
                f'<animateMotion path="{path}" dur="{SPIN}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{ops}" dur="{SPIN}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="{rs}" dur="{SPIN}s" begin="{beg:.2f}s" repeatCount="indefinite"/></circle>')
    # orbit rings with satellites (drawn tilted around the sphere)
    for k, (rx, ry, rot, dur) in enumerate(((172, 44, -16, 9), (150, 30, 24, 13))):
        p = f"M{-rx} 0A{rx} {ry} 0 1 1 {rx} 0A{rx} {ry} 0 1 1 {-rx} 0"
        out.append(
            f'<g transform="rotate({rot})"><path d="{p}" class="orbit"/>'
            f'<circle r="4.5" fill="url(#grad)" filter="url(#glow)"><animateMotion path="{p}" dur="{dur}s" repeatCount="indefinite" begin="-{k * 3}s"/></circle></g>')
    return "".join(out)


def header_3d(t):
    st, tb = text_block(t)
    style = st + f"""
.lat{{fill:none;stroke:{t['node']};stroke-opacity:.08}}
.pt{{fill:{t['node']}}} .hot{{fill:{t['a1']}}}
.orbit{{fill:none;stroke:url(#grad);stroke-opacity:.35;stroke-width:1}}
.globe{{animation:gin 1.4s cubic-bezier(.2,.7,.2,1) .2s both}}
@keyframes gin{{from{{opacity:0;transform:translate({CX}px,{CY + 16}px) scale(.85)}}to{{opacity:1;transform:translate({CX}px,{CY}px)}}}}
.halo{{animation:breathe 6s ease-in-out infinite}} @keyframes breathe{{50%{{opacity:.55}}}}"""
    halo_op = ".35" if t["bg"] != "#ffffff" else ".18"
    defs = (f'<radialGradient id="halo"><stop offset="0" stop-color="{t["a2"]}" stop-opacity="{halo_op}"/><stop offset="1" stop-color="{t["a2"]}" stop-opacity="0"/></radialGradient>'
            '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    body = (f'<g class="globe" transform="translate({CX} {CY})"><circle class="halo" r="{R + 70}" fill="url(#halo)"/>{sphere(t)}</g>{tb}')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{fonts()}{style}</style>
<defs><linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>{defs}</defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t['bg']}"/>{body}</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['faint']}"/>
</svg>
"""


# ── isometric architecture stacks ─────────────────────────────────
STACKS = [
    ("ThinkDesk", ["Next.js UI", "FastAPI", "Hybrid RAG + Groq", "PostgreSQL"]),
    ("Omnira", ["Tauri + React", "Fastify API", "Agent · tool calls", "Postgres · Prisma"]),
    ("AES App", ["Flutter · 4 platforms", "Firebase Auth", "Cloud Firestore", "n8n → Groq"]),
    ("Arabic MT", ["Tatoeba dialects", "MarianMT", "Fine-tuning", "BLEU · chrF eval"]),
]


def slab(cx, cy, w, d, h, top, side1, side2, stroke):
    """Isometric box centred at (cx, cy) top-face centre."""
    a = math.radians(30)
    dx, dy = math.cos(a), math.sin(a)
    p = lambda u, v: (cx + (u - v) * dx, cy + (u + v) * dy)  # noqa: E731
    t0, t1, t2, t3 = p(-w / 2, -d / 2), p(w / 2, -d / 2), p(w / 2, d / 2), p(-w / 2, d / 2)
    pts = lambda *q: " ".join(f"{x:.1f},{y:.1f}" for x, y in q)  # noqa: E731
    down = lambda q: (q[0], q[1] + h)  # noqa: E731
    return (f'<polygon points="{pts(t3, t2, down(t2), down(t3))}" fill="{side1}" stroke="{stroke}"/>'
            f'<polygon points="{pts(t2, t1, down(t1), down(t2))}" fill="{side2}" stroke="{stroke}"/>'
            f'<polygon points="{pts(t0, t1, t2, t3)}" fill="{top}" stroke="{stroke}"/>')


def stack_card(t):
    w_total, h_total = W, 480
    dark = t["bg"] != "#ffffff"
    tops = ["url(#gtop)", "#1e293b" if dark else "#eef2f7", "#1e293b" if dark else "#eef2f7", "#1e293b" if dark else "#eef2f7"]
    s1, s2 = ("#0f172a", "#131c2e") if dark else ("#dfe5ee", "#e8edf4")
    texts = "HOW THEY'RE BUILT " + "".join(n + "".join(ls) for n, ls in STACKS)
    parts = []
    col = w_total / len(STACKS)
    for k, (name, layers) in enumerate(STACKS):
        cx = col * k + col / 2
        base = 108
        gap = 76
        parts.append(f'<ellipse cx="{cx}" cy="{base + 3 * gap + 62}" rx="86" ry="20" fill="url(#shadow)"/>')
        for i, lab in reversed(list(enumerate(layers))):  # bottom first, so upper slabs occlude lower
            y = base + i * gap
            parts.append(
                f'<g style="animation:float{i} 5s ease-in-out {k * 0.35:.2f}s infinite, rise .7s cubic-bezier(.2,.7,.2,1) {0.15 + k * 0.12 + i * 0.08:.2f}s both">'
                f'{slab(cx, y, 92, 92, 14, tops[i] if i == 0 else tops[1], s1, s2, t["faint"])}'
                f'<text class="lab{" on" if i == 0 else ""}" x="{cx}" y="{y + 5}" text-anchor="middle">{lab}</text></g>')
        # data pulse travelling down through the layers
        parts.append(
            f'<circle r="4" fill="url(#grad)" filter="url(#glow)"><animateMotion dur="3.2s" begin="{1 + k * 0.6:.1f}s" repeatCount="indefinite" path="M{cx} {base - 6} L{cx} {base + 3 * gap + 6}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3.2s" begin="{1 + k * 0.6:.1f}s" repeatCount="indefinite"/></circle>')
        parts.append(f'<text class="pname" x="{cx}" y="{base + 3 * gap + 118}" text-anchor="middle">{name}</text>')
    floats = "".join(f"@keyframes float{i}{{50%{{transform:translateY({-3 - i * 2}px)}}}}" for i in range(4))
    css = f"""
.lab{{font-family:M,sans-serif;font-size:12.5px;fill:{t['ink']}}} .lab.on{{fill:#ffffff}}
.pname{{font-family:B,sans-serif;font-size:20px;fill:{t['ink']};letter-spacing:-.3px}}
.ttl{{font-family:M,sans-serif;font-size:13px;fill:{t['muted']};letter-spacing:2px}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
{floats}"""
    defs = (f'<linearGradient id="gtop" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{t["a1"]}" stop-opacity=".9"/><stop offset="1" stop-color="{t["a2"]}" stop-opacity=".9"/></linearGradient>'
            f'<radialGradient id="shadow"><stop offset="0" stop-color="{t["a2"]}" stop-opacity=".28"/><stop offset="1" stop-color="{t["a2"]}" stop-opacity="0"/></radialGradient>'
            '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    fnt = face("B", 800, texts) + face("M", 500, texts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w_total}" height="{h_total}" viewBox="0 0 {w_total} {h_total}">
<style>{fnt}{css}</style>
<defs><linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
<clipPath id="card"><rect width="{w_total}" height="{h_total}" rx="18"/></clipPath>{defs}</defs>
<g clip-path="url(#card)"><rect width="{w_total}" height="{h_total}" fill="{t['bg']}"/>
<text class="ttl" x="72" y="56">HOW THEY'RE BUILT</text>{''.join(parts)}</g>
<rect x=".5" y=".5" width="{w_total - 1}" height="{h_total - 1}" rx="18" fill="none" stroke="{t['faint']}"/>
</svg>
"""


if __name__ == "__main__":
    for theme, t in THEMES.items():
        for name, fn in (("header-3d", header_3d), ("stack", stack_card)):
            p = HERE / f"{name}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print(f"{p.name}: {p.stat().st_size / 1024:.0f} KB")
