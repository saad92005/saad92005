"""Builds the five profile SVGs in assets/.

    python src/build.py

Every SVG is self-contained: the photo is an inline PNG, fonts are subset WOFF2
(Barlow Condensed, Barlow, JetBrains Mono, all SIL OFL; licences in src/fonts/),
brand marks are Simple Icons (CC0, https://simpleicons.org) except LinkedIn, whose
mark Simple Icons no longer ships; that path is LinkedIn's official "in" logo.
Motion is CSS + SMIL only. Every element's un-animated state is its final, readable
state, so a viewer that ignores animation still shows a complete card.
"""
import base64
import io
import math
import random
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SRC = Path(__file__).parent
OUT = SRC.parent / "assets"
W = 1200

BG, CARD, LINE = "#070b16", "#0d1426", "#1b2540"
BLUE, RED, INK, MUTED, DOT = "#247bff", "#ff354f", "#eef2ff", "#8b95b0", "#141d33"

AS_OF = "06 OCT 2026"
ROLES = ["AI Engineer", "Full-Stack Developer", "RAG & Agent Builder", "Flutter Developer"]
PITCH = "I build AI software that has to work for someone other than me."

# ── fonts ────────────────────────────────────────────────────────────
FONTS = {"D": ("BarlowCondensed-ExtraBold.ttf", None), "T": ("Barlow-Medium.ttf", None),
         "R": ("Barlow-Regular.ttf", None), "M": ("JetBrainsMono[wght].ttf", 500)}


def font_css(text):
    css = []
    for fam, (file, wght) in FONTS.items():
        f = TTFont(SRC / "fonts" / file)
        s = subset.Subsetter(subset.Options())
        s.populate(text="".join(sorted(set(text + " "))))
        s.subset(f)
        if wght:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        f.flavor = "woff2"
        f["head"].modified = f["head"].created  # deterministic output
        b = io.BytesIO()
        f.save(b)
        css.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format('woff2')}}")
    return "".join(css)


# ── icons ────────────────────────────────────────────────────────────
HEX = {"python": "3776AB", "typescript": "3178C6", "dart": "0175C2", "react": "61DAFB", "nextdotjs": "EEF2FF",
       "flutter": "02569B", "fastapi": "009688", "nodedotjs": "5FA04E", "postgresql": "4169E1", "prisma": "EEF2FF",
       "firebase": "DD2C00", "pytorch": "EE4C2C", "docker": "2496ED", "githubactions": "2088FF", "tauri": "24C8D8",
       "vercel": "EEF2FF", "whatsapp": "25D366", "gmail": "EA4335", "linkedin": "0A66C2"}
NAMES = {"python": "Python", "typescript": "TypeScript", "dart": "Dart", "react": "React", "nextdotjs": "Next.js",
         "flutter": "Flutter", "fastapi": "FastAPI", "nodedotjs": "Node.js", "postgresql": "PostgreSQL", "prisma": "Prisma",
         "firebase": "Firebase", "pytorch": "PyTorch", "docker": "Docker", "githubactions": "GitHub Actions", "tauri": "Tauri",
         "vercel": "Vercel"}
LINKEDIN = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 "
            "1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 "
            "1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 "
            "1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z")


def icon(slug):
    if slug == "linkedin":
        return LINKEDIN
    import re
    return re.search(r' d="([^"]+)"', (SRC / "icons" / f"{slug}.svg").read_text(encoding="utf-8")).group(1)


def png(name):
    return "data:image/png;base64," + base64.b64encode((SRC / name).read_bytes()).decode()


# ── shared frame ─────────────────────────────────────────────────────
def frame(ns, h, text, css, defs, body):
    """Navy card, dot texture, gradient hairline border. ns prefixes every id."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<style>{font_css(text)}
.d{{font-family:D,sans-serif}} .t{{font-family:T,sans-serif}} .r{{font-family:R,sans-serif}} .m{{font-family:M,monospace}}
@keyframes {ns}up{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes {ns}fade{{from{{opacity:0}}to{{opacity:1}}}}
{css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
<linearGradient id="{ns}g" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{RED}"/></linearGradient>
<linearGradient id="{ns}hair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity=".9"/><stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{RED}" stop-opacity=".9"/></linearGradient>
<pattern id="{ns}dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{DOT}"/></pattern>
<radialGradient id="{ns}gl1"><stop offset="0" stop-color="{BLUE}" stop-opacity=".16"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<radialGradient id="{ns}gl2"><stop offset="0" stop-color="{RED}" stop-opacity=".11"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<linearGradient id="{ns}top" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset=".3" stop-color="{BLUE}"/><stop offset=".7" stop-color="{RED}"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>
<clipPath id="{ns}frame"><rect width="{W}" height="{h}" rx="22"/></clipPath>
{defs}
</defs>
<g clip-path="url(#{ns}frame)">
<rect width="{W}" height="{h}" fill="{BG}"/><rect width="{W}" height="{h}" fill="url(#{ns}dots)"/>
<circle cx="0" cy="0" r="520" fill="url(#{ns}gl1)"/><circle cx="{W}" cy="{h}" r="520" fill="url(#{ns}gl2)"/>
<rect x="80" width="{W - 160}" height="1" fill="url(#{ns}top)"/>
{body}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{h - 1.5}" rx="22" fill="none" stroke="url(#{ns}hair)" stroke-width="1.5"/>
</svg>
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def stagger(ns, delay, anim="up", dur=.7):
    return f'style="animation:{ns}{anim} {dur}s cubic-bezier(.2,.7,.2,1) {delay:.2f}s both"'


# ── 1. hero ──────────────────────────────────────────────────────────
def hero():
    ns, h = "hr", 480
    greet = "// hello, world. I'm"
    n = len(greet)
    # typed greeting: SMIL steps the clip width one character at a time; base width is the full line
    cw = 16 * 0.6
    t0, per = 0.3, 0.055
    dur = t0 + n * per
    widths = ";".join(f"{i * cw:.1f}" for i in [0] + list(range(n + 1)))
    kts = ";".join(f"{x / dur:.4f}" for x in [0, t0] + [t0 + i * per for i in range(1, n + 1)])
    roles_css, roles = [], []
    cyc = 3.0 * len(ROLES)
    for i, r in enumerate(ROLES):
        a, b = i * 3.0 / cyc * 100, (i + 1) * 3.0 / cyc * 100
        roles_css.append(
            f"@keyframes {ns}r{i}{{0%,{a:.2f}%{{transform:translateY(40px)}}{a + 3:.2f}%,{b - 3:.2f}%{{transform:none}}"
            f"{b:.2f}%,100%{{transform:translateY(-40px)}}}}"
            f".{ns}r{i}{{animation:{ns}r{i} {cyc}s cubic-bezier(.6,0,.2,1) 1.6s infinite}}")
        roles.append(f'<text class="t {ns}r{i}" x="96" y="356" font-size="28" fill="{INK}"'
                     f'{"" if i == 0 else " transform=" + chr(34) + "translate(0 40)" + chr(34)}>{esc(r)}</text>')
    row = [("pin", "Lahore, Pakistan"), ("cap", "BS Computer Science · UMT"), ("bolt", "Python · TypeScript · Dart")]
    glyph = {
        "pin": f'<path d="M0-7a6 6 0 0 1 6 6c0 4.5-6 10-6 10s-6-5.5-6-10a6 6 0 0 1 6-6z" fill="none" stroke="{BLUE}" stroke-width="1.8"/><circle cy="-1" r="2" fill="{BLUE}"/>',
        "cap": f'<path d="M-8-2 0-6 8-2 0 2z M-5 0v4c2 2 8 2 10 0v-4" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-linejoin="round"/>',
        "bolt": f'<path d="M1-8-5 1h5l-1 7 6-9H0z" fill="{RED}"/>'}
    chips, x = [], 64
    for k, (g, label) in enumerate(row):
        w = 46 + len(label) * 8.6
        chips.append(f'<g {stagger(ns, 1.3 + k * .12)}><rect x="{x}" y="414" width="{w:.0f}" height="36" rx="18" fill="{CARD}" stroke="{LINE}"/>'
                     f'<g transform="translate({x + 22} 432)">{glyph[g]}</g><text class="r" x="{x + 38}" y="438" font-size="16" fill="{MUTED}">{esc(label)}</text></g>')
        x += w + 12
    px, py, pw, ph = 846, 54, 296, 344
    term, term_text = terminal(ns, 752, 50, 392, 344)
    css = f"""
.{ns}rise1{{animation:{ns}rise 1s cubic-bezier(.2,.8,.2,1) .7s both}} .{ns}rise2{{animation:{ns}rise 1s cubic-bezier(.2,.8,.2,1) .85s both}}
@keyframes {ns}rise{{from{{transform:translateY(130px)}}to{{transform:none}}}}
.{ns}caret{{animation:{ns}blink 1s steps(1) infinite}} @keyframes {ns}blink{{50%{{opacity:0}}}}
.{ns}float{{animation:{ns}float 6s ease-in-out 1.4s infinite}} @keyframes {ns}float{{50%{{transform:translateY(-6px)}}}}
.{ns}glow{{transform-origin:{px + pw / 2}px {py + ph / 2}px;animation:{ns}breathe 7s ease-in-out infinite}}
@keyframes {ns}breathe{{50%{{transform:scale(1.1);opacity:.6}}}}
{''.join(roles_css)}"""
    defs = (f'<clipPath id="{ns}l1"><rect x="40" y="96" width="780" height="118"/></clipPath>'
            f'<clipPath id="{ns}l2"><rect x="40" y="206" width="780" height="118"/></clipPath>'
            f'<clipPath id="{ns}role"><rect x="60" y="326" width="700" height="40"/></clipPath>'
            f'<clipPath id="{ns}type"><rect x="64" y="56" width="{n * cw:.1f}" height="32">'
            f'<animate attributeName="width" values="{widths}" keyTimes="{kts}" calcMode="discrete" dur="{dur:.2f}s" begin="0s" fill="freeze"/></rect></clipPath>'
            f'<clipPath id="{ns}photo"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="24"/></clipPath>'
            f'<radialGradient id="{ns}rg"><stop offset="0" stop-color="{BLUE}" stop-opacity=".55"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{ns}shade" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".85"/></linearGradient>')
    body = f"""
<g clip-path="url(#{ns}type)"><text class="m" x="64" y="78" font-size="16" fill="{BLUE}">{greet}</text></g>
<rect class="{ns}caret" x="{64 + n * cw + 4:.1f}" y="62" width="9" height="20" fill="{RED}"/>
<g clip-path="url(#{ns}l1)"><text class="d {ns}rise1" x="60" y="204" font-size="132" fill="{INK}" letter-spacing="1">MUHAMMAD</text></g>
<g clip-path="url(#{ns}l2)"><text class="d {ns}rise2" x="60" y="314" font-size="132" fill="{BLUE}" letter-spacing="1">SAAD.</text></g>
<g {stagger(ns, 1.2)}><text class="m" x="64" y="355" font-size="20" fill="{RED}">&gt;</text></g>
<g clip-path="url(#{ns}role)" {stagger(ns, 1.2, "fade")}>{''.join(roles)}</g>
<g {stagger(ns, 1.3)}><text class="r" x="64" y="394" font-size="19" fill="{MUTED}">{PITCH}</text></g>
{''.join(chips)}
{term}"""
    text = greet + "MUHAMMADSAAD.>" + "".join(ROLES) + PITCH + "".join(l for _, l in row) + term_text
    return frame(ns, h, text, css, defs, body)


CMDS = [("whoami", "Muhammad Saad · AI engineer, Lahore"),
        ("ls ~/projects", "thinkdesk  omnira  aes-app  arabic-mt"),
        ("cat focus.txt", "agents · retrieval · applied NLP")]


def terminal(ns, x, y, w, h):
    """A terminal window that types three commands. SMIL only; base state is the finished session."""
    cw, t, per = 14 * 0.6, 1.6, 0.06
    out, text = [], "saad@lahore: ~$" + "".join(c + o for c, o in CMDS)
    for i, (cmd, res) in enumerate(CMDS):
        ly = y + 84 + i * 76
        n = len(cmd)
        dur = t + n * per + 0.35
        widths = ";".join(f"{k * cw:.1f}" for k in [0] + list(range(n + 1)) + [n])
        kts = ";".join(f"{v / dur:.4f}" for v in [0, t] + [t + k * per for k in range(1, n + 1)] + [dur])
        out.append(f'<clipPath id="{ns}c{i}"><rect x="{x + 46}" y="{ly - 16}" width="{n * cw:.1f}" height="22">'
                   f'<animate attributeName="width" values="{widths}" keyTimes="{kts}" calcMode="discrete" dur="{dur:.2f}s" begin="0s" fill="freeze"/></rect></clipPath>'
                   f'<text class="m" x="{x + 24}" y="{ly}" font-size="14" fill="{RED}">$</text>'
                   f'<g clip-path="url(#{ns}c{i})"><text class="m" x="{x + 46}" y="{ly}" font-size="14" fill="{INK}">{esc(cmd)}</text></g>'
                   f'<text class="m" x="{x + 46}" y="{ly + 26}" font-size="14" fill="{MUTED}">{esc(res)}'
                   f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{(dur - .05) / dur:.4f};1" dur="{dur:.2f}s" begin="0s" fill="freeze"/></text>')
        t = dur + 0.35
    fy = y + 84 + len(CMDS) * 76
    out.append(f'<text class="m" x="{x + 24}" y="{fy}" font-size="14" fill="{RED}">$</text>'
               f'<rect class="{ns}caret" x="{x + 46}" y="{fy - 14}" width="9" height="18" fill="{BLUE}"/>')
    bar = "#111a30"
    win = (f'<g {stagger(ns, .5)}><g class="{ns}float">'
           f'<rect x="{x - 30}" y="{y + 20}" width="{w + 60}" height="{h}" rx="40" fill="url(#{ns}rg)" opacity=".35"/>'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{CARD}"/>'
           f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="18" fill="{bar}"/><rect x="{x}" y="{y + 22}" width="{w}" height="18" fill="{bar}"/>'
           f'<line x1="{x}" y1="{y + 40}" x2="{x + w}" y2="{y + 40}" stroke="{LINE}"/>'
           + "".join(f'<circle cx="{x + 24 + k * 18}" cy="{y + 20}" r="5.5" fill="{c}"/>' for k, c in enumerate((RED, "#f5b83d", "#2bd576")))
           + f'<text class="m" x="{x + w / 2}" y="{y + 25}" font-size="12" fill="{MUTED}" text-anchor="middle">saad@lahore: ~</text>'
           + "".join(out)
           + f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="18" fill="none" stroke="url(#{ns}hair)" stroke-width="1.5"/></g></g>')
    return win, text


# ── 2. about + interests carousel ───────────────────────────────────
CAPS = [("AI agents", "Tool-calling agents that ask permission before they act."),
        ("Retrieval (RAG)", "Hybrid search over your documents that cites its sources."),
        ("Full-stack products", "Next.js, FastAPI, Flutter and Postgres, from auth to CI."),
        ("Applied NLP", "Fine-tuning MT models and evaluating them honestly.")]
SLIDES = [("LOW-RESOURCE NLP", ["Dialect Arabic is barely served by", "translation models, so I fine-tuned one."], "bleu"),
          ("AGENTS THAT ASK FIRST", ["Omnira, my desktop agent, needs your", "permission before every tool call."], "perm"),
          ("REAL BUSINESS SOFTWARE", ["AES App runs daily operations for an", "engineering services company."], "ops")]


def about():
    ns, h = "ab", 440
    caps = []
    for i, (t, s) in enumerate(CAPS):
        y = 150 + i * 68
        caps.append(f'<g {stagger(ns, .3 + i * .12)}><text class="m" x="64" y="{y}" font-size="15" fill="{RED}">0{i + 1}</text>'
                    f'<text class="t" x="104" y="{y}" font-size="22" fill="{INK}">{esc(t)}</text>'
                    f'<text class="r" x="104" y="{y + 26}" font-size="16" fill="{MUTED}">{esc(s)}</text></g>')
    cx, cy, cw_, ch = 640, 40, 500, 360
    slide_t, nsl = 4.0, len(SLIDES)
    cyc = slide_t * nsl
    css, slides, bars = [], [], []
    for i, (title, lines, kind) in enumerate(SLIDES):
        a, b = i * slide_t / cyc * 100, (i + 1) * slide_t / cyc * 100
        css.append(f"@keyframes {ns}s{i}{{0%,{max(a - .01, 0):.2f}%{{opacity:0;transform:translateX(24px)}}{a + 3:.2f}%,{b - 3:.2f}%{{opacity:1;transform:none}}"
                   f"{b:.2f}%,100%{{opacity:0;transform:translateX(-24px)}}}}.{ns}s{i}{{animation:{ns}s{i} {cyc}s ease-in-out infinite}}")
        css.append(f"@keyframes {ns}p{i}{{0%,{a:.2f}%{{transform:scaleX(0)}}{b:.2f}%,100%{{transform:scaleX(1)}}}}"
                   f".{ns}p{i}{{transform-box:fill-box;transform-origin:left;animation:{ns}p{i} {cyc}s linear infinite}}")
        bw = (cw_ - 64 - 12 * (nsl - 1)) / nsl
        bx = cx + 32 + i * (bw + 12)
        bars.append(f'<rect x="{bx:.1f}" y="{cy + 30}" width="{bw:.1f}" height="4" rx="2" fill="{LINE}"/>'
                    f'<rect class="{ns}p{i}" x="{bx:.1f}" y="{cy + 30}" width="{bw:.1f}" height="4" rx="2" fill="url(#{ns}g)"/>')
        vis = visual(kind, cx + 32, cy + 216)
        txt = "".join(f'<text class="r" x="{cx + 32}" y="{cy + 150 + k * 26}" font-size="18" fill="{MUTED}">{esc(l)}</text>' for k, l in enumerate(lines))
        slides.append(f'<g class="{ns}s{i}"{"" if i == 0 else " opacity=" + chr(34) + "0" + chr(34)}>'
                      f'<text class="m" x="{cx + 32}" y="{cy + 74}" font-size="14" fill="{BLUE}">0{i + 1} / 0{nsl}</text>'
                      f'<text class="d" x="{cx + 32}" y="{cy + 118}" font-size="40" fill="{INK}">{title}</text>{txt}{vis}</g>')
    body = f"""
<g {stagger(ns, .1)}><text class="m" x="64" y="66" font-size="14" fill="{BLUE}" letter-spacing="2">WHAT I DO</text>
<text class="d" x="64" y="108" font-size="44" fill="{INK}">BUILD IT. SHIP IT. <tspan fill="{RED}">PROVE IT.</tspan></text></g>
{''.join(caps)}
<g {stagger(ns, .4)}>
<rect x="{cx}" y="{cy}" width="{cw_}" height="{ch}" rx="20" fill="{CARD}" stroke="{LINE}"/>
<text class="m" x="{cx + cw_ - 32}" y="{cy + 74}" font-size="13" fill="{MUTED}" text-anchor="end" letter-spacing="2">WHAT I'M INTO</text>
{''.join(bars)}{''.join(slides)}
</g>"""
    text = "WHAT I DOBUILD IT. SHIP IT. PROVE IT.WHAT I'M INTO0123/" + "".join(a + b for a, b in CAPS) + "".join(t + "".join(l) for t, l, _ in SLIDES) + VIS_TEXT
    return frame(ns, h, text, "".join(css), "", body)


VIS_TEXT = "BLEU zero-shot fine-tuned13.029.0Tatoeba held-out testAllow tool call?send_emailDenyAllowWork ordersAttendancePayroll"


def visual(kind, x, y):
    if kind == "bleu":
        rows = [("zero-shot", 13.0, MUTED), ("fine-tuned", 29.0, BLUE)]
        out = [f'<text class="m" x="{x}" y="{y}" font-size="12" fill="{MUTED}">BLEU · Tatoeba held-out test</text>']
        for k, (lab, v, c) in enumerate(rows):
            yy = y + 22 + k * 34
            out.append(f'<text class="r" x="{x}" y="{yy + 15}" font-size="15" fill="{INK}">{lab}</text>'
                       f'<rect x="{x + 96}" y="{yy + 3}" width="{v * 9:.0f}" height="16" rx="4" fill="{c}"/>'
                       f'<text class="m" x="{x + 104 + v * 9:.0f}" y="{yy + 16}" font-size="14" fill="{INK}">{v}</text>')
        return "".join(out)
    if kind == "perm":
        return (f'<rect x="{x}" y="{y - 6}" width="380" height="96" rx="12" fill="{BG}" stroke="{LINE}"/>'
                f'<text class="t" x="{x + 18}" y="{y + 22}" font-size="16" fill="{INK}">Allow tool call?</text>'
                f'<text class="m" x="{x + 18}" y="{y + 46}" font-size="13" fill="{BLUE}">send_email</text>'
                f'<rect x="{x + 196}" y="{y + 52}" width="80" height="28" rx="8" fill="none" stroke="{LINE}"/><text class="t" x="{x + 236}" y="{y + 71}" font-size="14" fill="{MUTED}" text-anchor="middle">Deny</text>'
                f'<rect x="{x + 286}" y="{y + 52}" width="80" height="28" rx="8" fill="{BLUE}"/><text class="t" x="{x + 326}" y="{y + 71}" font-size="14" fill="#fff" text-anchor="middle">Allow</text>')
    out, xx = [], x
    for k, lab in enumerate(["Work orders", "Attendance", "Payroll"]):
        w = 30 + len(lab) * 8.5
        out.append(f'<rect x="{xx}" y="{y + 10}" width="{w:.0f}" height="34" rx="17" fill="none" stroke="{BLUE if k == 0 else LINE}"/>'
                   f'<text class="t" x="{xx + w / 2:.0f}" y="{y + 32}" font-size="15" fill="{INK}" text-anchor="middle">{lab}</text>')
        xx += w + 10
    return "".join(out)


# ── 3. stack ─────────────────────────────────────────────────────────
ORBITS = [(100, 46, -6, 24, ["python", "typescript", "dart", "pytorch"]),
          (186, 98, 10, 34, ["react", "nextdotjs", "flutter", "fastapi", "nodedotjs", "tauri"]),
          (272, 150, -10, 46, ["postgresql", "prisma", "firebase", "docker", "githubactions", "vercel"])]
GROUPS = [("AI / ML", ["PyTorch", "MarianMT", "RAG", "Groq LLMs", "Tool calling"]),
          ("BACKEND", ["FastAPI", "Node.js", "Fastify", "PostgreSQL", "Prisma"]),
          ("FRONTEND & MOBILE", ["React", "Next.js", "Tauri", "Flutter", "Dart"]),
          ("INFRA", ["Docker", "GitHub Actions", "Vercel", "Firebase", "n8n"])]


def ellipse_path(cx, cy, rx, ry, rot, start, reverse):
    pts = []
    for k in range(73):
        a = start + (-1 if reverse else 1) * 2 * math.pi * k / 72
        x, y = rx * math.cos(a), ry * math.sin(a)
        r = math.radians(rot)
        pts.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def stack():
    ns, h = "st", 560
    cx, cy = 320, 300
    rings, icons = [], []
    for oi, (rx, ry, rot, dur, slugs) in enumerate(ORBITS):
        rings.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" fill="none" stroke="{LINE}" stroke-width="1.2" stroke-dasharray="{"4 6" if oi == 1 else "none"}"/>')
        for k, s in enumerate(slugs):
            start = 2 * math.pi * k / len(slugs) + oi * .5
            path = ellipse_path(cx, cy, rx, ry, rot, start, oi % 2 == 1)
            x0, y0 = map(float, path[1:].split(" L")[0].split())
            icons.append(
                f'<g transform="translate({x0:.1f} {y0:.1f})"><animateTransform attributeName="transform" type="translate" '
                f'values="{";".join(p.replace(" ", ",") for p in path[1:].split(" L"))}" dur="{dur}s" begin="0s" repeatCount="indefinite"/>'
                f'<circle r="20" fill="{CARD}" stroke="{LINE}" stroke-width="1.2"/>'
                f'<g transform="translate(-11 -11) scale(.917)" fill="#{HEX[s]}"><path d="{icon(s)}"/></g>'
                f'<text class="m" y="34" font-size="10" fill="{MUTED}" text-anchor="middle">{NAMES[s]}</text></g>')
    chips, y = [], 120
    for gi, (title, items) in enumerate(GROUPS):
        chips.append(f'<text class="m" x="660" y="{y}" font-size="13" fill="{BLUE if gi % 2 == 0 else RED}" letter-spacing="2" {stagger(ns, .3 + gi * .15)}>{esc(title)}</text>')
        x = 660
        for k, it in enumerate(items):
            w = 28 + len(it) * 8.4
            chips.append(f'<g {stagger(ns, .4 + gi * .15 + k * .05)}><rect x="{x:.0f}" y="{y + 14}" width="{w:.0f}" height="34" rx="10" fill="{CARD}" stroke="{LINE}"/>'
                         f'<text class="t" x="{x + w / 2:.0f}" y="{y + 36}" font-size="15" fill="{INK}" text-anchor="middle">{esc(it)}</text></g>')
            x += w + 10
        y += 102
    css = f".{ns}core{{transform-origin:{cx}px {cy}px;animation:{ns}pulse 3s ease-in-out infinite}}@keyframes {ns}pulse{{50%{{transform:scale(1.08)}}}}"
    body = f"""
<g {stagger(ns, .1)}><text class="m" x="64" y="66" font-size="14" fill="{BLUE}" letter-spacing="2">TOOLKIT</text>
<text class="d" x="64" y="104" font-size="40" fill="{INK}">WHAT I BUILD WITH</text></g>
<text class="d" x="660" y="80" font-size="22" fill="{MUTED}" {stagger(ns, .2)}>GROUPED BY WHERE IT SITS</text>
<g {stagger(ns, .2, "fade", 1.2)}>{''.join(rings)}
<circle cx="{cx}" cy="{cy}" r="56" fill="url(#{ns}rg)"/>
<g class="{ns}core"><circle cx="{cx}" cy="{cy}" r="30" fill="url(#{ns}g)"/><text class="d" x="{cx}" y="{cy + 9}" font-size="26" fill="#fff" text-anchor="middle">AI</text></g>
{''.join(icons)}</g>
{''.join(chips)}"""
    defs = f'<radialGradient id="{ns}rg"><stop offset="0" stop-color="{BLUE}" stop-opacity=".45"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
    text = "TOOLKITWHAT I BUILD WITHGROUPED BY WHERE IT SITSAI" + "".join(NAMES.values()) + "".join(t + "".join(i) for t, i in GROUPS)
    return frame(ns, h, text, css, defs, body)


# ── 4. ID + verified numbers ─────────────────────────────────────────
METRICS = [("29.0", "BLEU", "Fine-tuned MarianMT on held-out dialect", "Arabic, up from 13.0 zero-shot"),
           ("105", "TESTS", "Passing in ThinkDesk's CI suite", "on every push"),
           ("5", "PUBLIC REPOS", "Project repositories with full", "source on GitHub"),
           ("6", "PLATFORM TARGETS", "Android, iOS, web and desktop from", "one Flutter codebase (AES App)")]
LANGS = [("Dart", 1294347), ("TypeScript", 587409), ("Python", 318425), ("Other", 59400 + 27210 + 19964)]


def id_dashboard():
    ns, h = "id", 500
    pcx, top, cw_, ch = 250, 120, 270, 340
    x0 = pcx - cw_ / 2
    rnd = random.Random(92005)
    bars, x = [], x0 + 34
    while x < x0 + cw_ - 38:
        w = rnd.choice((1.5, 1.5, 3, 4.5))
        bars.append(f'<rect x="{x:.1f}" y="{top + 278}" width="{w}" height="26"/>')
        x += w + rnd.choice((1.5, 3))
    badge = f"""
<g class="{ns}drop"><g class="{ns}swing">
  <path d="M200 -30 L{pcx - 10} 100 M300 -30 L{pcx + 10} 100" stroke="url(#{ns}g)" stroke-width="15" stroke-linecap="round" fill="none"/>
  <path d="M206 -30 L{pcx - 8} 96" stroke="#ffffff" stroke-opacity=".18" stroke-width="2" fill="none"/>
  <rect x="{pcx - 16}" y="92" width="32" height="20" rx="5" fill="url(#{ns}metal)"/>
  <rect x="{pcx - 9}" y="98" width="18" height="6" rx="3" fill="{BG}" opacity=".5"/>
  <path d="M{pcx - 7} 112 v6 a7 7 0 0 0 14 0 v-6" fill="none" stroke="url(#{ns}metal)" stroke-width="3.5"/>
  <g clip-path="url(#{ns}card)">
    <rect x="{x0}" y="{top}" width="{cw_}" height="{ch}" fill="{CARD}"/>
    <rect x="{x0}" y="{top}" width="{cw_}" height="{ch}" fill="url(#{ns}dots)"/>
    <rect x="{x0}" y="{top}" width="{cw_}" height="40" fill="url(#{ns}g)"/>
    <rect x="{pcx - 22}" y="{top + 14}" width="44" height="8" rx="4" fill="{BG}"/>
    <rect x="{pcx - 78}" y="{top + 54}" width="156" height="156" rx="18" fill="{BG}"/>
    <image x="{pcx - 78}" y="{top + 54}" width="156" height="156" xlink:href="{png('portrait-id.png')}" clip-path="url(#{ns}photo)"/>
    <text class="d" x="{pcx}" y="{top + 244}" font-size="30" fill="{INK}" text-anchor="middle">MUHAMMAD SAAD</text>
    <text class="m" x="{pcx}" y="{top + 266}" font-size="12" fill="{BLUE}" text-anchor="middle" letter-spacing="1">AI ENGINEER · LAHORE</text>
    <g fill="{INK}" opacity=".85">{''.join(bars)}</g>
    <text class="m" x="{pcx}" y="{top + 326}" font-size="11" fill="{MUTED}" text-anchor="middle" letter-spacing="2">@SAAD92005</text>
    <rect class="{ns}foil" x="{x0 - 140}" y="{top - 30}" width="80" height="{ch + 60}" fill="url(#{ns}foilg)"/>
  </g>
  <rect x="{x0 + .75}" y="{top + .75}" width="{cw_ - 1.5}" height="{ch - 1.5}" rx="18" fill="none" stroke="url(#{ns}hair)" stroke-width="1.5"/>
</g></g>"""
    rx_ = 500
    tiles = []
    for i, (val, unit, l1, l2) in enumerate(METRICS):
        tx, ty = rx_ + (i % 2) * 320, 140 + (i // 2) * 128
        tiles.append(f'<g {stagger(ns, 1.6 + i * .12)}><rect x="{tx}" y="{ty}" width="304" height="112" rx="16" fill="{CARD}" stroke="{LINE}"/>'
                     f'<text class="d" x="{tx + 22}" y="{ty + 54}" font-size="46" fill="{INK}">{val}</text>'
                     f'<text class="m" x="{tx + 30 + sum(9 if c == "." else 23 for c in val)}" y="{ty + 52}" font-size="13" fill="{RED if i % 2 else BLUE}" letter-spacing="1">{unit}</text>'
                     f'<text class="r" x="{tx + 22}" y="{ty + 80}" font-size="15" fill="{MUTED}">{esc(l1)}</text>'
                     f'<text class="r" x="{tx + 22}" y="{ty + 99}" font-size="15" fill="{MUTED}">{esc(l2)}</text></g>')
    tot = sum(b for _, b in LANGS)
    segs, leg, x = [], [], rx_
    cols = [BLUE, RED, "#7aa7ff", "#3a4766"]
    for i, (n_, b) in enumerate(LANGS):
        w = 624 * b / tot
        segs.append(f'<rect x="{x:.1f}" y="420" width="{max(w - 3, 2):.1f}" height="10" rx="3" fill="{cols[i]}" '
                    f'style="transform-box:fill-box;transform-origin:left;animation:{ns}grow .9s cubic-bezier(.6,0,.2,1) {2.1 + i * .1:.2f}s both"/>')
        leg.append(f'<circle cx="{rx_ + i * 156 + 5}" cy="{452}" r="5" fill="{cols[i]}"/><text class="r" x="{rx_ + i * 156 + 16}" y="457" font-size="15" fill="{MUTED}">{n_} <tspan fill="{INK}">{b / tot * 100:.0f}%</tspan></text>')
        x += w
    css = f"""
.{ns}drop{{transform-origin:250px -30px;animation:{ns}drop 2.8s cubic-bezier(.3,.6,.4,1) both}}
@keyframes {ns}drop{{0%{{transform:translateY(-520px) rotate(0)}}26%{{transform:translateY(0) rotate(9deg)}}42%{{transform:translateY(0) rotate(-6deg)}}
57%{{transform:translateY(0) rotate(3.8deg)}}71%{{transform:translateY(0) rotate(-2.3deg)}}85%{{transform:translateY(0) rotate(1.2deg)}}100%{{transform:translateY(0) rotate(0)}}}}
.{ns}swing{{transform-origin:250px -30px;animation:{ns}swing 5s ease-in-out 2.8s infinite}}
@keyframes {ns}swing{{0%,100%{{transform:rotate(0)}}25%{{transform:rotate(1.7deg)}}75%{{transform:rotate(-1.7deg)}}}}
.{ns}foil{{animation:{ns}foil 6s ease-in-out 2.6s infinite}}
@keyframes {ns}foil{{0%{{transform:translateX(0) skewX(-18deg)}}35%,100%{{transform:translateX(520px) skewX(-18deg)}}}}
@keyframes {ns}grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}"""
    defs = (f'<clipPath id="{ns}card"><rect x="{x0}" y="{top}" width="{cw_}" height="{ch}" rx="18"/></clipPath>'
            f'<clipPath id="{ns}photo"><rect x="{pcx - 78}" y="{top + 54}" width="156" height="156" rx="18"/></clipPath>'
            f'<linearGradient id="{ns}metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e5e9f2"/><stop offset=".5" stop-color="#8a93a8"/><stop offset="1" stop-color="#cfd5e2"/></linearGradient>'
            f'<linearGradient id="{ns}foilg" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#bcd4ff" stop-opacity=".3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    body = (badge
            + f'<g {stagger(ns, 1.4)}><text class="m" x="{rx_}" y="66" font-size="13" fill="{BLUE}" letter-spacing="2">VERIFIED · AS OF {AS_OF}</text>'
              f'<text class="d" x="{rx_}" y="112" font-size="44" fill="{INK}">BY THE NUMBERS<tspan fill="{RED}">.</tspan></text></g>'
            + "".join(tiles)
            + f'<text class="m" x="{rx_}" y="406" font-size="12" fill="{MUTED}" letter-spacing="2" {stagger(ns, 2)}>LANGUAGES ACROSS PUBLIC REPOS</text>'
            + "".join(segs) + f'<g {stagger(ns, 2.3)}>{"".join(leg)}</g>')
    text = ("MUHAMMAD SAADAI ENGINEER · LAHORE@SAAD92005VERIFIED · AS OF " + AS_OF + "BY THE NUMBERS.LANGUAGES ACROSS PUBLIC REPOS%0123456789"
            + "".join("".join(m) for m in METRICS) + "".join(n_ for n_, _ in LANGS))
    return frame(ns, h, text, css, defs, body)


# ── 5. selected work ────────────────────────────────────────────────
PROJECTS = [("ThinkDesk", "LIVE", ["AI knowledge workspace: hybrid RAG search that", "cites its sources, plus a research mode."], ["Next.js", "FastAPI", "PostgreSQL", "Groq"]),
            ("Omnira", "DESKTOP", ["Desktop AI agent with voice and chat that asks", "your permission before every tool call."], ["Tauri", "React", "Fastify", "Prisma"]),
            ("AES App", "CLIENT", ["Operations platform for an engineering services", "company: work orders, GPS attendance, payroll."], ["Flutter", "Firebase", "n8n"]),
            ("Arabic MT", "RESEARCH", ["Dialect Arabic → English. Fine-tuned MarianMT:", "BLEU 29.0 vs 13.0 zero-shot on held-out data."], ["PyTorch", "MarianMT", "Tatoeba"])]


def projects():
    ns, h = "pj", 580
    cards = []
    for i, (name, tag, desc, stack_) in enumerate(PROJECTS):
        x, y = 64 + (i % 2) * 548, 150 + (i // 2) * 206
        w, hh, acc = 524, 186, BLUE if i in (0, 3) else RED
        chips, cx_ = [], x + 28
        for s_ in stack_:
            cwid = 22 + len(s_) * 7.4
            chips.append(f'<rect x="{cx_:.0f}" y="{y + 140}" width="{cwid:.0f}" height="26" rx="13" fill="{BG}" stroke="{LINE}"/>'
                         f'<text class="m" x="{cx_ + cwid / 2:.0f}" y="{y + 157}" font-size="12" fill="{INK}" text-anchor="middle">{s_}</text>')
            cx_ += cwid + 8
        tw = 30 + len(tag) * 8.4 + (14 if tag == "LIVE" else 0)
        tx = x + w - 28 - tw
        dot = f'<circle class="{ns}live" cx="{tx + 16:.0f}" cy="{y + 33}" r="4" fill="#2bd576"/>' if tag == "LIVE" else ""
        cards.append(
            f'<g {stagger(ns, .4 + i * .14)}>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{hh}" rx="20" fill="{CARD}" stroke="{LINE}"/>'
            f'<rect x="{x + 28}" y="{y}" width="120" height="2" fill="{acc}"/>'
            f'<rect class="{ns}beam" x="{x + 28}" y="{y}" width="40" height="2" fill="#fff" opacity="0" style="animation-delay:{i * .9:.1f}s"/>'
            f'<text class="m" x="{x + 28}" y="{y + 38}" font-size="13" fill="{acc}" letter-spacing="2">0{i + 1}</text>'
            f'<rect x="{tx:.0f}" y="{y + 20}" width="{tw:.0f}" height="26" rx="13" fill="none" stroke="{LINE}"/>{dot}'
            f'<text class="m" x="{tx + tw / 2 + (7 if dot else 0):.0f}" y="{y + 38}" font-size="11" fill="{MUTED}" text-anchor="middle" letter-spacing="1.5">{tag}</text>'
            f'<text class="d" x="{x + 64}" y="{y + 41}" font-size="30" fill="{INK}">{name.upper()}</text>'
            + "".join(f'<text class="r" x="{x + 28}" y="{y + 84 + k * 24}" font-size="16" fill="{MUTED}">{esc(l)}</text>' for k, l in enumerate(desc))
            + "".join(chips) + '</g>')
    css = (f".{ns}beam{{animation:{ns}beam 4.5s ease-in-out infinite}}@keyframes {ns}beam{{0%{{transform:translateX(0);opacity:0}}20%{{opacity:.8}}60%,100%{{transform:translateX(80px);opacity:0}}}}"
           f".{ns}live{{animation:{ns}pulse 1.6s ease-in-out infinite}}@keyframes {ns}pulse{{50%{{opacity:.25}}}}")
    body = (f'<g {stagger(ns, .1)}><text class="m" x="64" y="66" font-size="14" fill="{BLUE}" letter-spacing="2">SELECTED WORK</text>'
            f'<text class="d" x="64" y="110" font-size="44" fill="{INK}">THINGS I&#39;VE SHIPPED<tspan fill="{RED}">.</tspan></text>'
            f'<text class="r" x="{W - 64}" y="110" font-size="16" fill="{MUTED}" text-anchor="end">Source links are just below.</text></g>'
            + "".join(cards))
    text = "SELECTED WORKTHINGS I'VE SHIPPED.Source links are just below.01234" + "".join(n.upper() + t + "".join(d) + "".join(s_) for n, t, d, s_ in PROJECTS)
    return frame(ns, h, text, css, "", body)


# ── 6. connect ───────────────────────────────────────────────────────
LINKS = [("linkedin", "LinkedIn", "in/saadshahidpk"),
         ("whatsapp", "WhatsApp", "Message me directly"),
         ("vercel", "Portfolio", "Projects and write-ups"),
         ("gmail", "Email", "saad39587@gmail.com")]


def connect():
    ns, h = "cn", 360
    cards = []
    for i, (slug, name, handle) in enumerate(LINKS):
        x, y = 610 + (i % 2) * 272, 74 + (i // 2) * 116
        cards.append(
            f'<g {stagger(ns, .8 + i * .12)}><rect x="{x}" y="{y}" width="258" height="100" rx="18" fill="{CARD}" stroke="{LINE}"/>'
            f'<rect x="{x + 20}" y="{y + 26}" width="48" height="48" rx="14" fill="#{HEX[slug] if slug != "vercel" else "1b2540"}"/>'
            f'<g transform="translate({x + 32} {y + 38})" fill="#ffffff"><path d="{icon(slug)}"/></g>'
            f'<text class="t" x="{x + 84}" y="{y + 46}" font-size="19" fill="{INK}">{name}</text>'
            f'<text class="r" x="{x + 84}" y="{y + 70}" font-size="14" fill="{MUTED}">{esc(handle)}</text>'
            f'<g class="{ns}nudge" style="animation-delay:{i * .25:.2f}s"><path d="M{x + 228} {y + 42} l8 8 -8 8" stroke="{BLUE if i % 2 == 0 else RED}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g></g>')
    css = f".{ns}nudge{{animation:{ns}nudge 1.6s ease-in-out infinite}} @keyframes {ns}nudge{{50%{{transform:translateX(5px)}}}}"
    defs = (f'<linearGradient id="{ns}div" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LINE}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{LINE}" stop-opacity="0"/></linearGradient>')
    body = f"""
<g {stagger(ns, .2)}><text class="m" x="64" y="84" font-size="14" fill="{BLUE}" letter-spacing="2">CONNECT</text>
<text class="d" x="60" y="170" font-size="92" fill="{INK}">LET&#39;S BUILD</text>
<text class="d" x="60" y="252" font-size="92" fill="{RED}">SOMETHING.</text>
<text class="r" x="64" y="296" font-size="18" fill="{MUTED}">Hiring, collaborating, or just curious about the work?</text></g>
<rect x="566" y="40" width="1" height="{h - 80}" fill="url(#{ns}div)"/>
<circle r="3" cx="566.5" cy="60" fill="{BLUE}"><animate attributeName="cy" values="60;{h - 60}" dur="4s" begin="0s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="4s" begin="0s" repeatCount="indefinite"/></circle>
{''.join(cards)}"""
    text = "CONNECTLET'S BUILDSOMETHING.Hiring, collaborating, or just curious about the work?" + "".join(a + b for _, a, b in LINKS)
    return frame(ns, h, text, css, defs, body)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in (("hero", hero), ("about-life", about), ("stack", stack), ("projects", projects), ("id-dashboard", id_dashboard), ("connect", connect)):
        p = OUT / f"{name}.svg"
        p.write_text(fn(), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size / 1024:.0f} KB")
