"""Generates the animated SVGs used in the profile README.

Pure SVG + CSS animations (no external fonts/scripts), so GitHub renders
them reliably. Run: python assets/generate.py
"""
from pathlib import Path

OUT = Path(__file__).parent
FONT = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, 'Courier New', monospace"


def header() -> str:
    roles = [
        "building AI agents that ask before they act",
        "shipping RAG systems that cite their sources",
        "turning business workflows into software",
    ]
    cycle = 12  # seconds for the full rotation
    slot = cycle / len(roles)
    role_css, role_svg = [], []
    for i, text in enumerate(roles):
        start = i * slot / cycle * 100
        end = (i + 1) * slot / cycle * 100
        type_end = start + (slot * 0.45) / cycle * 100
        role_css.append(f"""
      @keyframes r{i} {{
        0%, {start:.2f}% {{ opacity: 0; clip-path: inset(0 100% 0 0); }}
        {start + 0.01:.2f}% {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        {type_end:.2f}% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        {end - 1.5:.2f}% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
        {end:.2f}%, 100% {{ opacity: 0; clip-path: inset(0 0 0 0); }}
      }}
      .r{i} {{ animation: r{i} {cycle}s linear infinite; }}""")
        role_svg.append(f'<text class="role r{i}" x="64" y="252">&gt; {text}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="340" viewBox="0 0 1200 340">
  <style>
    .title {{ font: 800 64px {FONT}; fill: #fff; letter-spacing: -1.5px; }}
    .sub {{ font: 600 26px {FONT}; fill: url(#text); }}
    .role {{ font: 500 22px {MONO}; fill: #a5f3fc; opacity: 0; }}
    .meta {{ font: 500 17px {FONT}; fill: #94a3b8; }}
    .blob {{ mix-blend-mode: screen; filter: blur(60px); }}
    @keyframes driftA {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(120px,40px) scale(1.2); }} }}
    @keyframes driftB {{ 0%,100% {{ transform: translate(0,0) scale(1.1); }} 50% {{ transform: translate(-140px,-30px) scale(0.9); }} }}
    @keyframes driftC {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(60px,-50px); }} }}
    .a {{ animation: driftA 14s ease-in-out infinite; }}
    .b {{ animation: driftB 18s ease-in-out infinite; }}
    .c {{ animation: driftC 11s ease-in-out infinite; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
    .in1 {{ animation: rise .9s ease-out both; }}
    .in2 {{ animation: rise .9s .25s ease-out both; }}
    .in3 {{ animation: rise .9s .5s ease-out both; }}
    @keyframes blink {{ 0%,49% {{ opacity: 1; }} 50%,100% {{ opacity: 0; }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; fill: #a5f3fc; }}
    @keyframes pulse {{ 0%,100% {{ r: 5; opacity: 1; }} 50% {{ r: 9; opacity: .35; }} }}
    .dot {{ animation: pulse 2s ease-in-out infinite; }}
    @keyframes scan {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY(380px); }} }}
    .scan {{ animation: scan 6s linear infinite; }}
    {''.join(role_css)}
  </style>
  <defs>
    <linearGradient id="text" x1="0" x2="1">
      <stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/>
    </linearGradient>
    <linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#22d3ee" stop-opacity="0"/><stop offset="1" stop-color="#22d3ee" stop-opacity=".12"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".05"/>
    </pattern>
    <clipPath id="card"><rect width="1200" height="340" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1200" height="340" fill="#070b18"/>
    <circle class="blob a" cx="220" cy="80" r="190" fill="#4f46e5" opacity=".55"/>
    <circle class="blob b" cx="980" cy="260" r="210" fill="#db2777" opacity=".40"/>
    <circle class="blob c" cx="760" cy="40" r="150" fill="#0891b2" opacity=".50"/>
    <rect width="1200" height="340" fill="url(#grid)"/>
    <rect class="scan" width="1200" height="40" fill="url(#scanG)"/>
    <g class="in1">
      <circle class="dot" cx="72" cy="66" r="5" fill="#34d399"/>
      <text class="meta" x="90" y="72">open to AI / software engineering roles · Lahore, Pakistan</text>
    </g>
    <text class="title in2" x="60" y="152">Muhammad Saad</text>
    <text class="sub in3" x="62" y="196">AI Engineer &amp; Full-Stack Developer</text>
    {''.join(role_svg)}
    <text class="meta" x="64" y="300">TypeScript · Python · Flutter — agents, RAG, automation, SaaS</text>
  </g>
  <rect x=".5" y=".5" width="1199" height="339" rx="24" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</svg>
"""


def card(name, tagline, lines, tags, accent1, accent2, badge):
    tag_svg, x = [], 32
    for t in tags:
        w = 16 + len(t) * 8.4
        tag_svg.append(
            f'<rect x="{x}" y="232" width="{w:.0f}" height="28" rx="14" fill="#ffffff" fill-opacity=".06" stroke="#ffffff" stroke-opacity=".1"/>'
            f'<text class="tag" x="{x + w / 2:.0f}" y="251" text-anchor="middle">{t}</text>')
        x += w + 8
    body = "".join(f'<text class="body" x="32" y="{132 + i * 26}">{l}</text>' for i, l in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="580" height="290" viewBox="0 0 580 290">
  <style>
    .name {{ font: 800 30px {FONT}; fill: #fff; letter-spacing: -.5px; }}
    .tagline {{ font: 600 16px {FONT}; fill: url(#acc); }}
    .body {{ font: 400 15px {FONT}; fill: #cbd5e1; }}
    .tag {{ font: 600 12.5px {MONO}; fill: #e2e8f0; }}
    .badge {{ font: 700 11px {MONO}; fill: #070b18; letter-spacing: 1px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .spin {{ transform-origin: 290px 145px; animation: spin 8s linear infinite; }}
    @keyframes glow {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: .7; }} }}
    .glow {{ animation: glow 5s ease-in-out infinite; filter: blur(40px); }}
    @keyframes shine {{ from {{ transform: translateX(-200px) skewX(-20deg); }} to {{ transform: translateX(800px) skewX(-20deg); }} }}
    .shine {{ animation: shine 7s ease-in-out infinite; }}
  </style>
  <defs>
    <linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{accent1}"/><stop offset="1" stop-color="{accent2}"/></linearGradient>
    <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <clipPath id="outer"><rect width="580" height="290" rx="20"/></clipPath>
    <clipPath id="inner"><rect x="2" y="2" width="576" height="286" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#outer)">
    <g class="spin"><rect x="-200" y="-200" width="980" height="690" fill="url(#acc)"/><rect x="-200" y="145" width="980" height="345" fill="#1e293b"/></g>
  </g>
  <g clip-path="url(#inner)">
    <rect width="580" height="290" fill="#0b1022"/>
    <circle class="glow" cx="520" cy="30" r="110" fill="{accent1}"/>
    <rect class="shine" x="0" y="0" width="120" height="290" fill="url(#sh)"/>
    <rect x="32" y="34" width="{len(badge) * 8 + 20}" height="22" rx="11" fill="url(#acc)"/>
    <text class="badge" x="{32 + (len(badge) * 8 + 20) / 2}" y="49.5" text-anchor="middle">{badge}</text>
    <text class="name" x="32" y="94">{name}</text>
    <text class="tagline" x="{40 + len(name) * 17}" y="93">{tagline}</text>
    {body}
    {''.join(tag_svg)}
  </g>
</svg>
"""


def divider() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="12" viewBox="0 0 1200 12">
  <style>
    @keyframes flow { from { transform: translateX(-400px); } to { transform: translateX(1200px); } }
    .f { animation: flow 4s linear infinite; }
  </style>
  <defs>
    <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity="0"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6" stop-opacity="0"/></linearGradient>
  </defs>
  <rect y="5" width="1200" height="2" rx="1" fill="#64748b" fill-opacity=".25"/>
  <rect class="f" y="4" width="400" height="4" rx="2" fill="url(#g)"/>
</svg>
"""


CARDS = {
    "card-thinkdesk": ("ThinkDesk", "AI knowledge workspace", [
        "Hybrid RAG: vector + BM25, RRF fusion, cross-encoder rerank",
        "Research mode verifies claims across separate documents",
        "Agents draft actions, humans approve, then they execute",
        "Multi-tenant SaaS · real billing · 105 pytest tests · CI",
    ], ["FastAPI", "Next.js", "PostgreSQL", "Groq"], "#22d3ee", "#818cf8", "LIVE · FLAGSHIP"),
    "card-omnira": ("Omnira", "permission-gated AI agent", [
        "Voice + chat assistant that acts on your desktop",
        "Tool calling behind user-granted capabilities",
        "Vendor-agnostic LLM layer · OAuth PKCE · encrypted tokens",
        "8 ADRs · 128 unit tests · CI · Windows installer",
    ], ["Tauri", "React", "Fastify", "Prisma"], "#a78bfa", "#f472b6", "AI AGENT"),
    "card-aes": ("AES App", "field operations platform", [
        "Built for a real engineering services company",
        "Work orders auto-imported from Gmail · GPS attendance",
        "Payroll engine · double-entry accounting · inventory",
        "12 roles with tailored access · PDF/Excel exports",
    ], ["Flutter", "Dart", "Firebase", "Gmail API"], "#34d399", "#22d3ee", "PRODUCTION SOFTWARE"),
    "card-arabic": ("Arabic MT", "low-resource NLP", [
        "Dialect → English translation for 4 Arabic dialects",
        "GRU Seq2Seq baseline vs fine-tuned AraBERT encoder",
        "Transfer learning pipeline in PyTorch",
        "Written up as an IEEE-format research paper",
    ], ["PyTorch", "Transformers", "AraBERT"], "#fbbf24", "#f472b6", "NLP RESEARCH"),
}

if __name__ == "__main__":
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "divider.svg").write_text(divider(), encoding="utf-8")
    for fname, args in CARDS.items():
        (OUT / f"{fname}.svg").write_text(card(*args), encoding="utf-8")
    print("generated", sorted(p.name for p in OUT.glob("*.svg")))
