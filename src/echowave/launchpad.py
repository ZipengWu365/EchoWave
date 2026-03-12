"""Unified compare-first launchpad page for EchoWave v0.16.0."""

from __future__ import annotations

from html import escape

from .copydeck import (
    DISPLAY_NAME,
    DOCTOR_HEADING,
    HEADLINE,
    LIVE_DEMO_HEADING,
    PACKAGE_VERSION,
    QUICKSTART_INSTALL,
    QUICKSTART_ONE_LINER,
    START_HERE_HEADING,
    TAGLINE,
    ZERO_INSTALL_OPTIONS,
)


def project_launchpad_html(*, version: str = PACKAGE_VERSION) -> str:
    cards = []
    for item in ZERO_INSTALL_OPTIONS:
        cards.append(
            f"<div class='card'><h3>{escape(item['title'])}</h3><p>{escape(item['why'])}</p></div>"
        )
    zero_cards = ''.join(cards)
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{DISPLAY_NAME} - {START_HERE_HEADING.lower()}</title>
<style>
:root {{ --bg:#f4f8fc; --ink:#102a43; --muted:#486581; --line:#d9e2ec; --card:#ffffff; --brand:#0b6cff; --accent:#dd6b20; --shadow:0 1px 2px rgba(16,42,67,.05),0 12px 24px rgba(16,42,67,.08); --max:1180px; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; line-height:1.6; }}
a {{ color:var(--brand); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
.container {{ width:min(var(--max), calc(100vw - 30px)); margin:0 auto; padding:28px 0 40px; }}
.hero {{ display:grid; grid-template-columns:1.05fr .95fr; gap:20px; align-items:start; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:20px 22px; box-shadow:var(--shadow); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px; }}
.grid3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:20px; }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--brand); font-size:.88rem; font-weight:700; margin-right:8px; }}
.pill.alt {{ background:#fff4e8; color:var(--accent); }}
.brand {{ display:flex; align-items:center; gap:12px; }} .brand-mark {{ width:20px; height:20px; border-radius:6px; background:linear-gradient(135deg,var(--brand),#9cc9ff); }}
.top {{ display:flex; justify-content:space-between; align-items:center; gap:18px; margin-bottom:16px; }}
pre {{ margin:0; padding:14px 16px; background:#f7fafc; border:1px solid var(--line); border-radius:12px; overflow:auto; white-space:pre-wrap; word-break:break-word; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
.small {{ color:var(--muted); font-size:.94rem; }}
h1 {{ margin:0; font-size:clamp(2.2rem,4.6vw,3.6rem); line-height:1.03; letter-spacing:-.04em; }} h2 {{ margin:0 0 8px; font-size:1.4rem; }} h3 {{ margin:0 0 8px; font-size:1.08rem; }}
.buttons {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:18px; }} .button {{ display:inline-flex; align-items:center; padding:10px 14px; border-radius:10px; border:1px solid var(--line); background:#fff; color:var(--ink); font-weight:600; }} .button.primary {{ background:var(--brand); color:#fff; border-color:var(--brand); }}
ul {{ margin:0; padding-left:1.2rem; }}
@media (max-width: 980px) {{ .hero,.grid2,.grid3 {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class='container'>
  <div class='top'>
    <div class='brand'><span class='brand-mark'></span><div><strong>{escape(DISPLAY_NAME)}</strong><div class='small'>{escape(TAGLINE)}</div></div></div>
    <div><span class='pill'>Version {escape(version)}</span><span class='pill alt'>{escape(START_HERE_HEADING)}</span></div>
  </div>
  <section class='hero'>
    <div class='card'>
      <h1>{escape(HEADLINE)}</h1>
      <p class='small'>This page unifies the most useful first steps: static preview, local compute-backed similarity demo, one-line quickstart, compatibility presets, and environment diagnostics.</p>
      <div class='buttons'>
        <a class='button primary' href='playground.html'>Open static playground</a>
        <a class='button' href='index.html'>Open docs homepage</a>
        <a class='button' href='reports/github_breakout_similarity.html'>See flagship demo</a>
      </div>
    </div>
    <div class='card'>
      <span class='pill'>{escape(LIVE_DEMO_HEADING)}</span>
      <h2>Fastest paths to value</h2>
      <ul>
        <li>Try the static playground first if you only want to inspect similarity demos.</li>
        <li>Run the local live demo when you want real computation on pasted arrays.</li>
        <li>Use the one-line quickstart when you already have Python ready.</li>
        <li>Write a compatibility constraints file if you are installing into a mixed scientific stack.</li>
        <li>Run the environment doctor when you are in a large scientific stack and want cleaner installation advice.</li>
      </ul>
    </div>
  </section>
  <section class='grid2'>
    <div class='card'>
      <h2>One-line quickstart</h2>
      <pre><code>{escape(QUICKSTART_INSTALL)}
{escape(QUICKSTART_ONE_LINER)}</code></pre>
    </div>
    <div class='card'>
      <h2>{escape(DOCTOR_HEADING)}</h2>
      <pre><code>echowave --guide doctor
# or
python -m echowave.cli --guide doctor
# legacy alias
python -m tsontology.cli --guide doctor</code></pre>
      <p class='small'>Use this when you suspect encoding issues, mixed scientific-stack packages, or resolver noise.</p>
    </div>
  </section>
  <section class='grid3'>
    {zero_cards}
  </section>
  <section class='grid2'>
    <div class='card'>
      <h2>Local live demo</h2>
      <pre><code>echowave-demo --open-browser
# legacy alias
tsontology-demo --open-browser
# or
python -m echowave.demo_server --open-browser</code></pre>
    </div>
    <div class='card'>
      <h2>Compatibility preset</h2>
      <pre><code>echowave --write-constraints constraints/mixed-scientific-stack.txt `
  --constraint-profile mixed-scientific-stack
pip install -c constraints/mixed-scientific-stack.txt echowave</code></pre>
    </div>
  </section>
  <section class='grid2'>
    <div class='card'>
      <h2>Export a GitHub Pages bundle</h2>
      <pre><code>echowave --export-pages docs
# then publish docs/ with GitHub Pages</code></pre>
    </div>
  </section>
</div>
</body>
</html>"""


__all__ = ["project_launchpad_html"]
