"""The two cards with my photo: a hanging ID badge beside live GitHub numbers, and a
contact card. Same rules as the other assets: photo and fonts are embedded, motion is
CSS only, and the final frame of every animation is a readable resting state.

Brand marks are from Simple Icons (CC0): https://simpleicons.org
"""
import base64
import random
from datetime import date
from pathlib import Path

from header import face

HERE = Path(__file__).parent
W = 1200

PANEL = {"dark": dict(card="#111827", strap="#1e293b", metal="#94a3b8", foil="#ffffff"),
         "light": dict(card="#f8fafc", strap="#cbd5e1", metal="#64748b", foil="#ffffff")}

LINKEDIN = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 "
            "1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 "
            "1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 "
            "1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z")
WHATSAPP = (HERE / "icons" / "whatsapp.path").read_text().strip() if (HERE / "icons" / "whatsapp.path").exists() else ""


def png(name):
    return "data:image/png;base64," + base64.b64encode((HERE / name).read_bytes()).decode()


def svg(t, h, text, css, defs, body):
    fonts = face("B", 800, text) + face("M", 500, text)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>{fonts}
.big{{font-family:B,sans-serif;font-size:40px;fill:{t['ink']};letter-spacing:-1px}}
.lbl{{font-family:M,sans-serif;font-size:15px;fill:{t['muted']}}}
.ttl{{font-family:M,sans-serif;font-size:13px;fill:{t['muted']};letter-spacing:2px}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<defs><linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
<clipPath id="frame"><rect width="{W}" height="{h}" rx="18"/></clipPath>{defs}</defs>
<g clip-path="url(#frame)"><rect width="{W}" height="{h}" fill="{t['bg']}"/>{body}</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="{t['faint']}"/>
</svg>
"""


def badge(t, p):
    """Lanyard + card, hanging from (250, -20)."""
    cx, top, cw, ch = 250, 112, 260, 320
    x0 = cx - cw / 2
    rnd = random.Random(92005)
    bars, x = [], x0 + 40
    while x < x0 + cw - 44:
        w = rnd.choice((1.5, 1.5, 3, 4.5))
        bars.append(f'<rect x="{x:.1f}" y="{top + 262}" width="{w}" height="26"/>')
        x += w + rnd.choice((1.5, 3))
    return f"""
<g class="drop"><g class="swing">
  <path d="M206 -20 L{cx - 9} 96 M294 -20 L{cx + 9} 96" stroke="url(#grad)" stroke-width="14" stroke-linecap="round" fill="none" opacity=".9"/>
  <rect x="{cx - 14}" y="88" width="28" height="18" rx="4" fill="{p['metal']}"/>
  <circle cx="{cx}" cy="{top - 1}" r="7" fill="none" stroke="{p['metal']}" stroke-width="3"/>
  <g clip-path="url(#badge)">
    <rect x="{x0}" y="{top}" width="{cw}" height="{ch}" fill="{p['card']}"/>
    <rect x="{x0}" y="{top}" width="{cw}" height="34" fill="url(#grad)"/>
    <rect x="{cx - 20}" y="{top + 12}" width="40" height="7" rx="3.5" fill="{t['bg']}"/>
    <image x="{cx - 75}" y="{top + 46}" width="150" height="150" xlink:href="{png('portrait-id.png')}" clip-path="url(#photo)"/>
    <text x="{cx}" y="{top + 222}" text-anchor="middle" font-family="B,sans-serif" font-size="22" fill="{t['ink']}">Muhammad Saad</text>
    <text x="{cx}" y="{top + 245}" text-anchor="middle" class="lbl" font-size="13">AI Engineer · Full-Stack</text>
    <g fill="{t['ink']}" opacity=".8">{''.join(bars)}</g>
    <text x="{cx}" y="{top + 308}" text-anchor="middle" class="ttl" font-size="11">@SAAD92005</text>
    <rect class="foil" x="{x0 - 120}" y="{top - 20}" width="70" height="{ch + 40}" fill="url(#foil)"/>
  </g>
  <rect x="{x0 + .5}" y="{top + .5}" width="{cw - 1}" height="{ch - 1}" rx="16" fill="none" stroke="{t['faint']}"/>
</g></g>"""


def id_card(t, p, numbers, langs, as_of):
    h = 470
    rx = 500
    text = "BY THE NUMBERS LANGUAGES Other%0123456789.,·@SAAD92005 as of Muhammad Saad AI Engineer Full-Stack Lahore, Pakistan BS Computer Science, UMT" + as_of
    cells = []
    for i, (val, label) in enumerate(numbers):
        x = rx + i * 215
        cells.append(f'<g style="animation:up .7s cubic-bezier(.2,.7,.2,1) {0.9 + i * 0.12:.2f}s both">'
                     f'<text class="big" x="{x}" y="152">{val}</text><text class="lbl" x="{x}" y="178">{label}</text></g>')
        text += str(val) + label
    shades = [t["a1"], t["a2"], "#60a5fa", "#c084fc", "#94a3b8", "#475569"] if t["bg"] != "#ffffff" else \
             [t["a1"], t["a2"], "#2563eb", "#9333ea", "#64748b", "#cbd5e1"]
    bw, by = 630, 250
    segs, legend, x = [], [], rx
    for i, (name, share) in enumerate(langs):
        w = bw * share
        col = shades[i % len(shades)]
        segs.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{col}" '
                    f'style="transform-box:fill-box;transform-origin:left;animation:grow .9s cubic-bezier(.6,0,.2,1) {1.3 + i * 0.1:.2f}s both"/>')
        lx, ly = rx + (i % 3) * 210, 296 + (i // 3) * 28
        legend.append(f'<g style="animation:up .6s {1.6 + i * 0.08:.2f}s both"><circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{col}"/>'
                      f'<text class="lbl" x="{lx + 18}" y="{ly}">{name} <tspan fill="{t["ink"]}">{share * 100:.1f}%</tspan></text></g>')
        text += name
        x += w
    css = """
.drop{transform-origin:250px -20px;animation:drop 2.6s cubic-bezier(.3,.6,.4,1) both}
@keyframes drop{0%{transform:translateY(-500px) rotate(0)}28%{transform:translateY(0) rotate(8deg)}
44%{transform:translateY(0) rotate(-5.5deg)}60%{transform:translateY(0) rotate(3.4deg)}
75%{transform:translateY(0) rotate(-2deg)}88%{transform:translateY(0) rotate(1deg)}100%{transform:translateY(0) rotate(0)}}
.swing{transform-origin:250px -20px;animation:swing 5s ease-in-out 2.6s infinite}
@keyframes swing{0%,100%{transform:rotate(0)}25%{transform:rotate(1.7deg)}75%{transform:rotate(-1.7deg)}}
.foil{animation:foil 6s ease-in-out 2.4s infinite both}
@keyframes foil{0%{transform:translateX(0) skewX(-18deg)}35%,100%{transform:translateX(480px) skewX(-18deg)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"""
    defs = (f'<clipPath id="badge"><rect x="120" y="112" width="260" height="320" rx="16"/></clipPath>'
            f'<clipPath id="photo"><circle cx="250" cy="233" r="75"/></clipPath>'
            f'<linearGradient id="foil" x1="0" x2="1"><stop offset="0" stop-color="{p["foil"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{p["foil"]}" stop-opacity=".28"/><stop offset="1" stop-color="{p["foil"]}" stop-opacity="0"/></linearGradient>')
    body = (badge(t, p)
            + f'<g style="animation:up .6s .8s both"><text class="ttl" x="{rx}" y="88">BY THE NUMBERS</text>'
              f'<text class="lbl" x="{rx + bw}" y="88" text-anchor="end" font-size="13">as of {as_of}</text></g>'
            + "".join(cells)
            + f'<text class="ttl" x="{rx}" y="232" style="animation:up .6s 1.2s both">LANGUAGES</text>'
            + "".join(segs) + "".join(legend)
            + f'<text class="lbl" x="{rx}" y="410" style="animation:up .6s 2s both">Lahore, Pakistan  ·  BS Computer Science, UMT</text>')
    return svg(t, h, text, css, defs, body)


def contact_card(t, p):
    h = 330
    links = [("LinkedIn", "in/saadshahidpk", LINKEDIN, "#0A66C2"),
             ("WhatsApp", "+92 321 4429267", WHATSAPP, "#25D366")]
    heading, sub = "Let's talk.", "Building something with AI, or hiring for it? I'd like to hear about it."
    text = heading + sub + "".join(a + b for a, b, _, _ in links) + "→"
    cards = []
    for i, (name, handle, path, brand) in enumerate(links):
        x, y = 470 + i * 340, 190
        cards.append(
            f'<g style="animation:up .7s cubic-bezier(.2,.7,.2,1) {0.9 + i * 0.15:.2f}s both">'
            f'<rect x="{x}" y="{y}" width="310" height="84" rx="16" fill="{p["card"]}" stroke="{t["faint"]}"/>'
            f'<circle cx="{x + 44}" cy="{y + 42}" r="24" fill="{brand}"/>'
            f'<g transform="translate({x + 32} {y + 30})" fill="#ffffff"><path transform="scale(1)" d="{path}"/></g>'
            f'<text x="{x + 84}" y="{y + 38}" font-family="B,sans-serif" font-size="18" fill="{t["ink"]}">{name}</text>'
            f'<text class="lbl" x="{x + 84}" y="{y + 61}">{handle}</text>'
            f'<text class="nudge" style="animation-delay:{i * 0.3:.1f}s" x="{x + 276}" y="{y + 50}" font-family="B,sans-serif" font-size="22" fill="url(#grad)">→</text></g>')
    css = """
.me{animation:rise 1s cubic-bezier(.2,.7,.2,1) .1s both}
@keyframes rise{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
.halo{transform-origin:220px 200px;animation:breathe 6s ease-in-out infinite}
@keyframes breathe{50%{transform:scale(1.08);opacity:.75}}
.nudge{animation:nudge 1.6s ease-in-out infinite}
@keyframes nudge{50%{transform:translateX(6px)}}
.chev{animation:chev 1.8s ease-in-out infinite both}
@keyframes chev{0%,100%{opacity:.15}40%{opacity:1}}"""
    op = ".35" if t["bg"] != "#ffffff" else ".18"
    defs = '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'
    chevrons = "".join(f'<path class="chev" style="animation-delay:{k * 0.2:.1f}s" d="M{396 + k * 18} 218 l10 14 l-10 14" '
                       f'stroke="url(#grad)" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for k in range(3))
    body = (f'<g opacity="{op}" filter="url(#soft)"><circle class="halo" cx="220" cy="200" r="120" fill="url(#grad)"/></g>'
            f'<image class="me" x="54" y="{h - 300}" width="332" height="300" xlink:href="{png("portrait-connect.png")}"/>'
            + chevrons
            + f'<g style="animation:up .7s .4s both"><text class="big" x="470" y="110" font-size="48">{heading}</text>'
              f'<text class="lbl" x="472" y="146" font-size="17">{sub}</text></g>'
            + "".join(cards))
    return svg(t, h, text, css, defs, body)


def write_all(themes, numbers, langs, as_of):
    for theme, t in themes.items():
        p = PANEL[theme]
        (HERE / f"id-card-{theme}.svg").write_text(id_card(t, p, numbers, langs, as_of), encoding="utf-8")
        (HERE / f"connect-{theme}.svg").write_text(contact_card(t, p), encoding="utf-8")
