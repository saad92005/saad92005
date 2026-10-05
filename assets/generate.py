"""Builds the profile README artwork.

Every SVG is self-contained: fonts (OFL: Instrument Serif, Caveat, JetBrains Mono) are
subset to the glyphs actually used and embedded, screenshots are embedded as JPEG, and
animation is plain CSS. Nothing is fetched at view time, so GitHub's image proxy renders
them exactly as designed. Each piece comes in a dark and a light variant.

    python assets/generate.py            # needs fonttools + Pillow
"""
import base64
import io
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

HERE = Path(__file__).parent
SRC = HERE / "src"          # fonts/ and screenshots/ live here
OUT = HERE

THEMES = {
    "dark": dict(bg="#0f0f11", ink="#ece7df", muted="#8b867d", faint="#26252a", accent="#ff7a45", paper="#17171a", grain=0.07),
    "light": dict(bg="#f7f4ee", ink="#1c1b18", muted="#76716a", faint="#e4dfd6", accent="#d9541e", paper="#ffffff", grain=0.05),
}

# ───────────────────────────── fonts ─────────────────────────────
FONT_FILES = {
    "serif": ("InstrumentSerif-Regular.ttf", None),
    "serif-italic": ("InstrumentSerif-Italic.ttf", None),
    "hand": ("Caveat[wght].ttf", 600),
    "mono": ("JetBrainsMono[wght].ttf", 500),
}
_font_cache = {}


def _base_font(key):
    if key not in _font_cache:
        file, weight = FONT_FILES[key]
        f = TTFont(SRC / "fonts" / file)
        if weight is not None and "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": weight})
        _font_cache[key] = f
    return _font_cache[key]


def width(key, text, size):
    f = _base_font(key)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap.get(ord("?")))][0] for c in text) * size / upm


def font_face(key, family, text):
    f = TTFont(io.BytesIO(_dump(_base_font(key))))
    opts = subset.Options()
    opts.layout_features = ["kern", "liga"]
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(set(text + " "))))
    s.subset(f)
    data = base64.b64encode(_dump(f)).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{data}) format('truetype');}}"


def _dump(f):
    b = io.BytesIO()
    f.save(b)
    return b.getvalue()


def faces(texts):
    """texts: {font_key: all strings rendered in that font}"""
    fam = {"serif": "S", "serif-italic": "SI", "hand": "H", "mono": "M"}
    return "".join(font_face(k, fam[k], t) for k, t in texts.items() if t)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def grain(t):
    return f"""<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 {t['grain'] * 2.2} 0"/></filter>"""


def jpeg_data(path, w, crop=None, q=82):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}", im.width, im.height


# ───────────────────────────── hero ─────────────────────────────
NOW = [
    "fine-tuning MT models for low-resource Arabic dialects",
    "keeping API keys out of client apps",
    "writing tests for the parts that handle money",
]


def hero(t):
    W, H = 1200, 470
    name, l2, l3 = "Muhammad Saad", "I build AI software that ships,", "and agents that ask before they act."
    note = ["CS student, Lahore —", "still shipping"]
    top_l, top_r = "SAAD92005 · LAHORE, PK", "AI ENGINEER / FULL-STACK"
    x0 = 72
    # underline the word "ships" in line 2
    pre = width("serif-italic", "I build AI software that ", 46)
    ships_w = width("serif-italic", "ships", 46)
    ux0, ux1 = x0 + pre - 4, x0 + pre + ships_w + 6
    name_w = width("serif", name, 112)

    n = len(NOW)
    cyc = 5.0 * n
    ticker_css, ticker_svg = [], []
    for i, line in enumerate(NOW):
        a, b = i / n * 100, (i + 1) / n * 100
        ticker_css.append(f"@keyframes t{i}{{0%,{a:.1f}%{{opacity:0;transform:translateY(8px)}}{a + 2.5:.1f}%,{b - 3:.1f}%{{opacity:1;transform:none}}{b:.1f}%,100%{{opacity:0;transform:translateY(-8px)}}}}"
                          f".t{i}{{animation:t{i} {cyc}s 3.2s infinite both}}")
        ticker_svg.append(f'<text class="mono now t{i}" x="{x0 + 118}" y="{H - 52}">{esc(line)}</text>')

    css = faces({
        "serif": name, "serif-italic": l2 + l3,
        "hand": "".join(note), "mono": top_l + top_r + "currently →" + "".join(NOW),
    })
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{css}
.serif{{font-family:S,serif}} .it{{font-family:SI,serif;font-style:normal}} .hand{{font-family:H,cursive}} .mono{{font-family:M,monospace;letter-spacing:.14em}}
.name{{font-size:112px;fill:{t['ink']};letter-spacing:-.02em}}
.line{{font-size:46px;fill:{t['muted']}}} .line .em{{fill:{t['ink']}}}
.top{{font-size:13px;fill:{t['muted']}}} .now{{font-size:15px;fill:{t['ink']};letter-spacing:.02em;opacity:0}}
.lbl{{font-size:13px;fill:{t['accent']}}} .note{{font-size:31px;fill:{t['accent']}}}
@keyframes rise{{from{{opacity:0;transform:translateY(26px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes rule{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes blink{{50%{{opacity:0}}}}
.r1{{animation:rise .9s cubic-bezier(.2,.7,.2,1) .15s both}} .r2{{animation:rise .9s cubic-bezier(.2,.7,.2,1) .55s both}} .r3{{animation:rise .9s cubic-bezier(.2,.7,.2,1) .8s both}}
.f0{{animation:fade 1s .05s both}} .f1{{animation:fade .8s 2.1s both}} .f2{{animation:fade .6s 3s both}}
.rule{{transform-origin:{x0}px 0;animation:rule 1.2s cubic-bezier(.6,0,.2,1) .1s both}}
.u{{stroke-dasharray:420;stroke-dashoffset:420;animation:draw .75s cubic-bezier(.5,0,.3,1) 1.45s forwards}}
.arrow{{stroke-dasharray:300;stroke-dashoffset:300;animation:draw .8s ease-out 2.35s forwards}}
.head{{stroke-dasharray:60;stroke-dashoffset:60;animation:draw .25s ease-out 3.1s forwards}}
.caret{{animation:blink 1.05s steps(1) infinite}}
{''.join(ticker_css)}
</style>
<defs>{grain(t)}</defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="1"/>
<g class="f0">
  <text class="mono top" x="{x0}" y="58">{top_l}</text>
  <text class="mono top" x="{W - x0}" y="58" text-anchor="end">{top_r}</text>
</g>
<rect class="rule" x="{x0}" y="76" width="{W - 2 * x0}" height="1" fill="{t['faint']}"/>
<text class="serif name r1" x="{x0 - 4}" y="210">{name}</text>
<text class="it line r2" x="{x0}" y="282">I build AI software that <tspan class="em">ships,</tspan></text>
<text class="it line r3" x="{x0}" y="338">and agents that <tspan class="em">ask before they act.</tspan></text>
<path class="u" d="M{ux0} 296 C {ux0 + 40} 290, {ux1 - 50} 300, {ux1} 292 M{ux0 + 14} 303 C {ux0 + 50} 299, {ux1 - 30} 305, {ux1 - 6} 300"
      fill="none" stroke="{t['accent']}" stroke-width="3" stroke-linecap="round"/>
<g class="f1">
  <text class="hand note" x="{x0 + name_w + 70}" y="132">{note[0]}</text>
  <text class="hand note" x="{x0 + name_w + 92}" y="166">{note[1]}</text>
</g>
<path class="arrow" d="M{x0 + name_w + 64} 146 C {x0 + name_w + 20} 150, {x0 + name_w + 4} 166, {x0 + name_w + 2} 186"
      fill="none" stroke="{t['accent']}" stroke-width="2.4" stroke-linecap="round"/>
<path class="head" d="M{x0 + name_w - 8} 174 L{x0 + name_w + 2} 188 L{x0 + name_w + 13} 176"
      fill="none" stroke="{t['accent']}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="{x0}" y="{H - 96}" width="{W - 2 * x0}" height="1" fill="{t['faint']}"/>
<g class="f2"><text class="mono lbl" x="{x0}" y="{H - 52}">CURRENTLY →</text></g>
{''.join(ticker_svg)}
</svg>
"""



def arrowhead(cx, cy, bx, by, size=13, spread=0.5):
    import math
    ang = math.atan2(by - cy, bx - cx)
    p1 = (bx - size * math.cos(ang - spread), by - size * math.sin(ang - spread))
    p2 = (bx - size * math.cos(ang + spread), by - size * math.sin(ang + spread))
    return f"M{p1[0]:.1f} {p1[1]:.1f} L{bx} {by} L{p2[0]:.1f} {p2[1]:.1f}"

# ───────────────────────────── project plates ─────────────────────────────
def plate(t, num, title, stack, shot, note, note_xy, arrow, phone=False):
    W, H = 1200, 640
    x0 = 56
    img_w = 330 if phone else 1000
    data, iw, ih = jpeg_data(shot["path"], img_w * 2 if not phone else img_w * 2, shot.get("crop"))
    iw, ih = iw / 2, ih / 2
    max_h = H - 150
    if ih > max_h:  # keep the frame inside the plate
        scale = max_h / ih
        iw, ih = iw * scale, ih * scale
    ix = W - x0 - iw - (120 if phone else 0)
    iy = 122
    css = faces({"serif": title, "serif-italic": num, "hand": "".join(note), "mono": stack})
    note_svg = "".join(f'<text class="hand" x="{note_xy[0]}" y="{note_xy[1] + i * 34}">{esc(l)}</text>' for i, l in enumerate(note))
    ax, ay, bx, by = arrow
    cx, cy = (ax + bx) / 2 + 30, min(ay, by) - 30
    head = arrowhead(cx, cy, bx, by)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{css}
.num{{font-family:SI,serif;font-size:64px;fill:{t['accent']}}}
.title{{font-family:S,serif;font-size:58px;fill:{t['ink']};letter-spacing:-.01em}}
.stack{{font-family:M,monospace;font-size:13px;letter-spacing:.14em;fill:{t['muted']}}}
.hand{{font-family:H,cursive;font-size:30px;fill:{t['accent']}}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
@keyframes wipe{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
@keyframes lift{{from{{transform:translate(0,0)}}to{{transform:translate(10px,10px)}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.a1{{animation:rise .8s cubic-bezier(.2,.7,.2,1) .1s both}} .a2{{animation:rise .8s cubic-bezier(.2,.7,.2,1) .3s both}}
.shot{{animation:wipe 1.1s cubic-bezier(.7,0,.2,1) .45s both}}
.shadow{{animation:lift .5s ease-out 1.4s both}}
.n{{animation:fade .6s 1.7s both}}
.arr{{stroke-dasharray:900;stroke-dashoffset:900;animation:draw .8s ease-out 1.9s forwards}}
.hd{{stroke-dasharray:60;stroke-dashoffset:60;animation:draw .2s ease-out 2.65s forwards}}
</style>
<defs>{grain(t)}<clipPath id="r"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{14 if phone else 6}"/></clipPath></defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<g class="a1"><text class="num" x="{x0}" y="92">{num}</text></g>
<g class="a2"><text class="title" x="{x0 + 82}" y="90">{esc(title)}</text>
<text class="stack" x="{W - x0}" y="84" text-anchor="end">{esc(stack)}</text></g>
<g class="shot">
  <rect class="shadow" x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{14 if phone else 6}" fill="none" stroke="{t['accent']}" stroke-width="1.5"/>
  <image href="{data}" x="{ix}" y="{iy}" width="{iw}" height="{ih}" clip-path="url(#r)" preserveAspectRatio="xMidYMid slice"/>
  <rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{14 if phone else 6}" fill="none" stroke="{t['ink']}" stroke-opacity=".18"/>
</g>
<g class="n">{note_svg}</g>
<path class="arr" d="M{ax} {ay} Q {cx} {cy} {bx} {by}" fill="none" stroke="{t['accent']}" stroke-width="2.4" stroke-linecap="round"/>
<path class="hd" d="{head}" fill="none" stroke="{t['accent']}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def chart_plate(t, metrics):
    """Plate 04: real held-out results from the Arabic MT experiment."""
    W, H, x0 = 1200, 640, 56
    systems = [("marian_finetuned", "Marian, fine-tuned"), ("marian_zero_shot", "Marian, zero-shot"),
               ("arabert_gru", "AraBERT + GRU"), ("gru_scratch", "GRU from scratch")]
    rows = [(label, metrics["systems"][k]) for k, label in systems if k in metrics["systems"]]
    n_test = rows[0][1]["n"]
    title, stack, num = "Arabic dialect MT", "PYTORCH · TRANSFORMERS", "04"
    note = ["pretraining does the", "heavy lifting"]
    labels = "".join(l for l, _ in rows)
    vals = "".join(f"{r['chrf']:.1f}{r['bleu']:.1f}" for _, r in rows)
    caption = f"chrF / BLEU ON {n_test} HELD-OUT TATOEBA SENTENCES"
    css = faces({"serif": title + labels, "serif-italic": num, "hand": "".join(note), "mono": stack + vals + caption + "chrFBLEU0123456789.·"})
    bar_x, bar_w, top, gap = 380, 640, 170, 98
    bars = []
    for i, (label, r) in enumerate(rows):
        y = top + i * gap
        w = max(4, bar_w * r["chrf"] / 100)
        delay = 0.5 + i * 0.18
        bars.append(f"""
<text class="lab a" style="animation-delay:{delay}s" x="{bar_x - 24}" y="{y + 30}" text-anchor="end">{esc(label)}</text>
<rect x="{bar_x}" y="{y}" width="{bar_w}" height="44" fill="{t['faint']}" opacity=".55"/>
<rect class="bar" style="animation-delay:{delay + .1}s" x="{bar_x}" y="{y}" width="{w:.1f}" height="44" fill="{t['accent'] if i == 0 else t['ink']}" opacity="{1 if i == 0 else .82}"/>
<text class="val a" style="animation-delay:{delay + .7}s" x="{bar_x + w + 14:.1f}" y="{y + 29}">{r['chrf']:.1f} · {r['bleu']:.1f}</text>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{css}
.num{{font-family:SI,serif;font-size:64px;fill:{t['accent']}}}
.title{{font-family:S,serif;font-size:58px;fill:{t['ink']}}}
.stack,.cap{{font-family:M,monospace;font-size:13px;letter-spacing:.14em;fill:{t['muted']}}}
.lab{{font-family:S,serif;font-size:28px;fill:{t['ink']}}}
.val{{font-family:M,monospace;font-size:16px;fill:{t['muted']}}}
.hand{{font-family:H,cursive;font-size:30px;fill:{t['accent']}}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
.a1{{animation:rise .8s cubic-bezier(.2,.7,.2,1) .1s both}} .a2{{animation:rise .8s cubic-bezier(.2,.7,.2,1) .3s both}}
.a{{animation:fade .6s both}} .bar{{transform-box:fill-box;transform-origin:left;animation:grow 1s cubic-bezier(.6,0,.2,1) both}}
.n{{animation:fade .6s 1.9s both}}
</style>
<defs>{grain(t)}</defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<g class="a1"><text class="num" x="{x0}" y="92">{num}</text></g>
<g class="a2"><text class="title" x="{x0 + 82}" y="90">{title}</text>
<text class="stack" x="{W - x0}" y="84" text-anchor="end">{stack}</text></g>
{''.join(bars)}
<text class="cap a" style="animation-delay:1.4s" x="{bar_x}" y="{top + len(rows) * gap + 10}">{caption}</text>
<g class="n"><text class="hand" x="{W - 330}" y="{top - 52}">{note[0]}</text><text class="hand" x="{W - 300}" y="{top - 20}">{note[1]}</text></g>
</svg>
"""


# ───────────────────────────── small pieces ─────────────────────────────
def squiggle(t):
    W = 1200
    pts = " ".join(f"{x} {14 + (6 if (x // 30) % 2 else -6)}" for x in range(0, 1201, 30))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="28" viewBox="0 0 {W} 28">
<style>@keyframes draw{{to{{stroke-dashoffset:0}}}}.s{{stroke-dasharray:1700;stroke-dashoffset:1700;animation:draw 1.6s cubic-bezier(.6,0,.2,1) .2s forwards}}</style>
<polyline class="s" points="{pts}" fill="none" stroke="{t['muted']}" stroke-opacity=".5" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
</svg>
"""


def signature(t):
    text = "— Saad"
    css = faces({"hand": text})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="110" viewBox="0 0 360 110">
<style>{css}
.sig{{font-family:H,cursive;font-size:72px;fill:{t['ink']};fill-opacity:0;stroke:{t['ink']};stroke-width:1.2;
stroke-dasharray:900;stroke-dashoffset:900;animation:write 2.2s ease-in-out .3s forwards, fill .8s 2.1s forwards}}
@keyframes write{{to{{stroke-dashoffset:0}}}} @keyframes fill{{to{{fill-opacity:1;stroke-width:0}}}}
</style>
<text class="sig" x="10" y="78">{text}</text>
</svg>
"""


PLATES = [
    dict(key="thinkdesk", num="01", title="ThinkDesk", stack="PYTHON · FASTAPI · POSTGRES · NEXT.JS",
         shot=dict(path=SRC / "screens" / "thinkdesk-chat.png", crop=(280, 60, 1160, 420)),
         note=["one question, two documents,", "every claim cited"], note_xy=(70, 560), arrow=(300, 548, 438, 470)),
    dict(key="omnira", num="02", title="Omnira", stack="TAURI · REACT · FASTIFY · PRISMA",
         shot=dict(path=SRC / "screens" / "omnira-chat.png", crop=(0, 60, 800, 640)),
         note=["it set the timer itself —", "a real tool call, not", "just a reply"], note_xy=(80, 300), arrow=(390, 318, 832, 236)),
    dict(key="aes", num="03", title="AES App", stack="FLUTTER · FIREBASE · GMAIL API", phone=True,
         shot=dict(path=SRC / "screens" / "aes-dashboard.jpg", crop=(0, 75, 1057, 1420)),
         note=["work orders, payroll,", "accounting, GPS attendance —", "one codebase, 12 roles"],
         note_xy=(90, 250), arrow=(420, 330, 680, 300)),
]

if __name__ == "__main__":
    written = []
    for theme, t in THEMES.items():
        (OUT / f"squiggle-{theme}.svg").write_text(squiggle(t), encoding="utf-8")
        (OUT / f"signature-{theme}.svg").write_text(signature(t), encoding="utf-8")
        for p in PLATES:
            args = {k: v for k, v in p.items() if k != "key"}
            (OUT / f"plate-{p['key']}-{theme}.svg").write_text(plate(t, **args), encoding="utf-8")
        metrics = SRC / "arabic-mt-metrics.json"
        if metrics.exists():
            m = json.loads(metrics.read_text(encoding="utf-8"))
            (OUT / f"plate-arabic-{theme}.svg").write_text(chart_plate(t, m), encoding="utf-8")
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name:32s} {f.stat().st_size / 1024:7.1f} KB")
