"""Static homepage generator for EchoWave v0.16.0.

The homepage is docs-first, GitHub-friendly, and ready to be dropped into a
GitHub Pages bundle. It is intentionally closer to a scientific Python docs
landing page than to a marketing microsite, but it now carries stronger demo
and growth assets.
"""

from __future__ import annotations

from html import escape

from .copydeck import (
    AGENT_HEADING,
    AUTHOR_AFFILIATION,
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    BENCHMARK_HEADING,
    COVERAGE_HEADING,
    DISPLAY_NAME,
    ECOSYSTEM_HEADING,
    FLAGSHIP_DEMOS,
    HEADLINE,
    INSTALL_HEADING,
    LIVE_DEMO_HEADING,
    PACKAGE_VERSION,
    PAGES_HEADING,
    PRODUCT_PROMISE,
    PROJECT_DOCUMENTATION_URL,
    PROJECT_REPOSITORY_URL,
    QUICKSTART_EXPECTED_LINES,
    QUICKSTART_INSTALL,
    QUICKSTART_ONE_LINER,
    TAGLINE,
    TRUST_HEADING,
    HOMEPAGE_PILLS,
    ZERO_INSTALL_OPTIONS,
)
from .datasets import list_starter_datasets, starter_dataset
from .playground import project_playground_html
from .launchpad import project_launchpad_html
from .positioning import coverage_matrix, ecosystem_positioning
from .product import explain_similarity
from .profile import profile_dataset
from .similarity import compare_series, rolling_similarity
from .visuals import (
    axis_bar_svg,
    profile_radar_svg,
    profile_social_card_svg,
    rolling_similarity_svg,
    series_overlay_svg,
    similarity_components_svg,
    similarity_social_card_svg,
)


def _ecosystem_rows() -> str:
    payload = ecosystem_positioning(format="json")
    rows = []
    for entry in payload["entries"][:6]:
        strongest = ", ".join(entry["strongest_for"][:3])
        rows.append(
            f"<tr><td><strong>{escape(entry['name'])}</strong></td><td>{escape(entry['family'])}</td><td>{escape(strongest)}</td><td>{escape(entry['tsontology_relation'])}</td></tr>"
        )
    return "\n".join(rows)


def _coverage_rows() -> str:
    payload = coverage_matrix(format="json")
    rows = []
    for row in payload["rows"][:8]:
        companions = ", ".join(row["best_companions"]) if row["best_companions"] else "-"
        rows.append(
            f"<tr><td>{escape(row['capability'])}</td><td>{escape(row['tsontology_role'])}</td><td>{escape(companions)}</td><td>{escape(row['notes'])}</td></tr>"
        )
    return "\n".join(rows)


def _starter_rows() -> str:
    return "\n".join(
        f"<tr><td><strong>{escape(item['title'])}</strong><br><span class='muted'>{escape(item['name'])}</span></td><td>{escape(item['domain'])}</td><td>{escape(item['kind'])}</td><td>{escape(item['why'])}</td></tr>"
        for item in list_starter_datasets()
    )


def _flagship_cards() -> str:
    cards = []
    for item in FLAGSHIP_DEMOS:
        cards.append(
            f"<div class='card'><span class='pill alt'>flagship</span><h3>{escape(item['title'])}</h3><p>{escape(item['story'])}</p><p class='hook'>{escape(item['social_hook'])}</p></div>"
        )
    return "\n".join(cards)


def project_homepage_html(*, version: str = PACKAGE_VERSION) -> str:
    traffic = starter_dataset("weekly_website_traffic")
    traffic_profile = profile_dataset(
        traffic["values"],
        domain="traffic",
        timestamps=traffic["timestamps"],
        channel_names=traffic["channels"],
    )
    github_case = starter_dataset("github_breakout_analogs")
    github_report = compare_series(
        github_case["target"],
        github_case["durable_breakout"],
        left_name="OpenClaw-style candidate",
        right_name="durable breakout analog",
    )
    windows = rolling_similarity(github_case["target"], github_case["durable_breakout"], window=20, step=5)

    radar = profile_radar_svg(traffic_profile, width=380, height=360)
    bars = axis_bar_svg(traffic_profile, width=560, height=300)
    overlay = series_overlay_svg(
        github_case["target"],
        github_case["durable_breakout"],
        left_label="OpenClaw-style candidate",
        right_label="durable breakout analog",
        width=560,
        height=220,
    )
    comp = similarity_components_svg(github_report, width=560, height=220)
    roll_svg = rolling_similarity_svg(windows, width=560, height=220)
    summary_preview = escape(explain_similarity(github_case["target"], github_case["durable_breakout"], left_name="OpenClaw-style candidate", right_name="durable breakout analog"))
    social_left = similarity_social_card_svg(github_report, title="GitHub breakout analogs")
    social_right = profile_social_card_svg(traffic_profile, title="Website traffic structure")
    starter_rows = _starter_rows()
    ecosystem_rows = _ecosystem_rows()
    coverage_rows = _coverage_rows()
    flagship_cards = _flagship_cards()
    homepage_pills = "".join(f"<span class='pill'>{escape(item)}</span>" for item in HOMEPAGE_PILLS)
    quick_expected = escape("\n".join(QUICKSTART_EXPECTED_LINES))
    playground = project_playground_html(version=version)
    zero_cards = "".join(
        f"<div class='card'><span class='pill'>{escape(item['title'])}</span><p>{escape(item['why'])}</p></div>" for item in ZERO_INSTALL_OPTIONS
    )

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{DISPLAY_NAME} - {TAGLINE.lower()}</title>
<style>
:root {{ --bg:#f4f8fc; --ink:#102a43; --muted:#486581; --line:#d9e2ec; --soft:#f7fafc; --blue:#0b6cff; --orange:#dd6b20; --card:#ffffff; --shadow:0 1px 2px rgba(16,42,67,.05),0 12px 24px rgba(16,42,67,.08); --max:1180px; --academic:#a51c30; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); line-height:1.6; }} a {{ color:var(--blue); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
.topbar {{ position:sticky; top:0; z-index:20; backdrop-filter:saturate(180%) blur(10px); background:rgba(248,251,255,.92); border-bottom:1px solid var(--line); }}
.container {{ width:min(var(--max), calc(100vw - 32px)); margin:0 auto; }} .topbar-inner {{ min-height:64px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
.brand {{ display:flex; align-items:center; gap:12px; }} .brand-mark {{ width:18px; height:18px; border-radius:5px; background:linear-gradient(135deg,var(--blue),#9cc9ff); }} .brand strong {{ font-size:1.18rem; letter-spacing:-.02em; }} .brand span {{ color:var(--muted); }} .nav {{ display:flex; flex-wrap:wrap; gap:16px; font-size:.94rem; }}
.hero {{ padding:42px 0 20px; }} .hero-grid {{ display:grid; grid-template-columns:1.08fr .92fr; gap:24px; align-items:start; }} .card {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:20px 22px; box-shadow:var(--shadow); }} .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }} .grid3 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:20px; }} section.block {{ padding:12px 0 18px; }}
.kicker {{ display:inline-block; font-size:.88rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--blue); margin-bottom:8px; }} h1 {{ margin:0; font-size:clamp(2.4rem,5vw,4rem); line-height:1.03; letter-spacing:-.045em; }} h2 {{ margin:0 0 8px; font-size:1.75rem; letter-spacing:-.02em; }} h3 {{ margin:0 0 8px; font-size:1.2rem; letter-spacing:-.02em; }} .subhead {{ margin:12px 0 0; font-size:1.16rem; color:var(--muted); max-width:48rem; }} .badge-row {{ display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 0; }}
.buttons {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:22px; }} .button {{ display:inline-flex; align-items:center; gap:8px; padding:10px 14px; border-radius:10px; font-weight:600; border:1px solid var(--line); color:var(--ink); background:#fff; box-shadow:var(--shadow); }} .button.primary {{ background:var(--blue); color:#fff; border-color:var(--blue); }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--blue); font-size:.88rem; font-weight:600; margin-right:8px; }} .pill.alt {{ background:#fff4e8; color:var(--orange); }} .pill.academic {{ background:#fce8ec; color:var(--academic); }} .hook {{ color:var(--muted); font-style:italic; }} .muted {{ color:var(--muted); }} .lead {{ margin:0 0 16px; color:var(--muted); max-width:72rem; }}
pre {{ margin:0; padding:14px 16px; background:#f6f8fa; border:1px solid var(--line); border-radius:12px; overflow:auto; font-size:.92rem; white-space:pre-wrap; word-break:break-word; }} table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden; box-shadow:var(--shadow); }} th,td {{ text-align:left; vertical-align:top; padding:12px 14px; border-bottom:1px solid var(--line); }} th {{ background:#f7fafc; font-size:.95rem; }} tr:last-child td {{ border-bottom:none; }} iframe.demo {{ width:100%; min-height:420px; border:1px solid var(--line); border-radius:14px; background:#fff; box-shadow:var(--shadow); }} img.hero-art {{ width:100%; border:1px solid var(--line); border-radius:14px; margin-top:16px; box-shadow:var(--shadow); background:#fff; }} img.affiliation-art {{ width:100%; max-width:460px; border:1px solid var(--line); border-radius:14px; margin-top:16px; box-shadow:var(--shadow); background:#fff; }} .author-meta {{ display:grid; gap:6px; margin-top:14px; }} .footer {{ padding:28px 0 48px; color:var(--muted); }}
@media (max-width: 980px) {{ .hero-grid,.grid2,.grid3 {{ grid-template-columns:1fr; }} .topbar-inner {{ padding:12px 0; align-items:flex-start; }} }}
</style>
</head>
<body>
<header class='topbar'><div class='container topbar-inner'><div class='brand'><span class='brand-mark'></span><div><strong>{DISPLAY_NAME}</strong><span> {escape(TAGLINE)}</span></div></div><nav class='nav'><a href='start-here.html'>Start here</a><a href='#install'>{INSTALL_HEADING}</a><a href='#live-demo'>{PAGES_HEADING}</a><a href='#demos'>Flagship demos</a><a href='#ecosystem'>{ECOSYSTEM_HEADING}</a><a href='#agents'>{AGENT_HEADING}</a><a href='#benchmark'>{BENCHMARK_HEADING}</a><a href='#trust'>{TRUST_HEADING}</a></nav></div></header>
<main class='container'>
<!-- EchoWave was formerly published as tsontology. -->
<section class='hero'>
<div class='hero-grid'>
<div>
<span class='kicker'>Version {escape(version)} - compare-first product surface</span>
<h1>{escape(HEADLINE)}</h1>
<p class='subhead'>{escape(PRODUCT_PROMISE)} Use it when you need an explainable verdict, not just an opaque distance score.</p>
<div class='badge-row'>{homepage_pills}</div>
<div class='buttons'>
<a class='button primary' href='#install'>Run the quickstart</a>
<a class='button' href='start-here.html'>Start here</a><a class='button' href='playground.html'>Open static playground</a><a class='button' href='#live-demo'>See live demo options</a>
<a class='button' href='reports/github_breakout_similarity.html'>See flagship demo</a>
</div>
</div>
<div class='card'>
<span class='pill'>What this solves</span><span class='pill academic'>Built with academic grounding</span>
<p><strong>Many time-series comparisons fail because one score is not enough.</strong> Teams still need to know whether two curves really match, whether two datasets are structurally alike, and what part of the similarity is doing the work.</p>
<ul>
<li>Compare two curves with a readable verdict and component breakdown</li>
<li>Compare two datasets when scale or observation style differs</li>
<li>Search for analogs instead of eyeballing historical cases</li>
<li>Ship the result as agent JSON and shareable HTML</li>
</ul>
<img class='hero-art' src='social/echowave_title_card.svg' alt='EchoWave title card'/>
<img class='affiliation-art' src='social/bham_affiliation_badge.svg' alt='Zipeng Wu, The University of Birmingham'/>
<div class='author-meta'>
<strong>{escape(AUTHOR_NAME)}</strong>
<span>{escape(AUTHOR_AFFILIATION)}</span>
<a href='mailto:{escape(AUTHOR_EMAIL)}'>{escape(AUTHOR_EMAIL)}</a>
<a href='{escape(PROJECT_REPOSITORY_URL)}'>{escape(PROJECT_REPOSITORY_URL)}</a>
<a href='{escape(PROJECT_DOCUMENTATION_URL)}'>{escape(PROJECT_DOCUMENTATION_URL)}</a>
</div>
</div>
</div>
</section>
<section class='block' id='install'>
<h2>{INSTALL_HEADING}</h2>
<p class='lead'>The first minute should be copy-pasteable and should produce a real output.</p>
<div class='grid2'>
<div class='card'><pre><code>{escape(QUICKSTART_INSTALL)}
{escape(QUICKSTART_ONE_LINER)}</code></pre></div>
<div class='card'><h3>Expected output starts like this</h3><pre><code>{quick_expected}</code></pre></div>
</div>
</section>
<section class='block' id='live-demo'>
<h2>{PAGES_HEADING}</h2><p class='lead'><strong>{LIVE_DEMO_HEADING}:</strong> for real computation without a backend, run the bundled local server.</p>
<p class='lead'>This version ships both a static GitHub Pages showcase and a tiny local live demo server. Use Pages when you want a shareable similarity demo, and use the local demo when you want real computation on pasted arrays or starter cases.</p>
<div class='grid3'>
<div class='card'><span class='pill'>Start here</span><p>Use <code>start-here.html</code> as the single launch page for quickstart, local demo, environment doctor, and Pages export.</p></div>
{zero_cards}
</div>
<div class='grid2' style='margin-top:20px'>
<div class='card'><h3>Playground preview</h3><iframe class='demo' srcdoc="{escape(playground)}"></iframe></div>
<div class='card'><h3>Zero-install paths</h3><ul><li>Open <code>docs/index.html</code> or <code>playground.html</code> locally.</li><li>Publish the included <code>docs/</code> bundle with GitHub Pages.</li><li>Use the Colab starter notebook or the documented <code>uvx</code> pattern for lightweight trials.</li><li>Export a compatibility preset before installing into a crowded scientific stack.</li></ul></div>
</div>
</section>
<section class='block'>
<h2>What explainable similarity looks like</h2>
<p class='lead'>The goal is not just one score. It is a verdict a researcher, product manager, clinician, or agent can act on.</p>
<div class='grid2'>
<div class='card'>{overlay}</div>
<div class='card'><h3>Plain-English similarity preview</h3><pre><code>{summary_preview}</code></pre></div>
</div>
<div class='grid2' style='margin-top:20px'>
<div class='card'>{comp}</div>
<div class='card'><h3>Brandable similarity card</h3>{social_left}</div>
</div>
<div class='grid2' style='margin-top:20px'>
<div class='card'>{roll_svg}</div>
<div class='card'><h3>When raw shape is not enough</h3>{radar}</div>
</div>
</section>
<section class='block' id='demos'>
<h2>Flagship demos built to travel</h2>
<p class='lead'>The strongest social hooks in this repo are GitHub breakout analogs, BTC vs gold under shocks, and heatwave vs grid load. Each flagship demo now has a notebook, HTML report, social card, GIF, and short blog draft.</p>
<div class='grid3'>{flagship_cards}</div>
<div class='grid2' style='margin-top:20px'>
<div class='card'>{bars}</div>
<div class='card'><h3>Dataset context card</h3>{social_right}</div>
</div>
</section>
<section class='block' id='benchmark'>
<h2>{BENCHMARK_HEADING}</h2>
<p class='lead'>The benchmark story is still modest. The bundled reproducible suite is a decision-impact benchmark, not yet a full similarity robustness or retrieval benchmark.</p>
<div class='grid2'>
<div class='card'><h3>What exists today</h3><ul><li>A reproducible decision-impact benchmark.</li><li>A realistic product claim: structural reports can change downstream choices.</li><li>A clear place to attach future similarity retrieval benchmarks.</li></ul></div>
<div class='card'><h3>What is still missing</h3><ul><li>Not a publication benchmark.</li><li>Not a leaderboard.</li><li>Not yet proof that EchoWave is the best general-purpose similarity engine.</li></ul></div>
</div>
</section>
<section class='block' id='ecosystem'>
<!-- Where tsontology fits in the ecosystem -->
<h2>{ECOSYSTEM_HEADING}</h2>
<p class='lead'>EchoWave is not trying to replace your modelling toolkit or your DTW engine. It sits in the explainable-comparison layer: compare clearly, explain clearly, and only then reach for the rest of the stack.</p>
<table><thead><tr><th>Package</th><th>Family</th><th>Strongest fit</th><th>How EchoWave fits</th></tr></thead><tbody>{ecosystem_rows}</tbody></table>
</section>
<section class='block' id='coverage'>
<h2>{COVERAGE_HEADING}</h2>
<p class='lead'>Primary means EchoWave is a first-class solution. Complementary means it helps but another package usually does the heavy lifting. Out of scope means hand the job to another package family.</p>
<table><thead><tr><th>Capability</th><th>Role</th><th>Companion packages</th><th>Notes</th></tr></thead><tbody>{coverage_rows}</tbody></table>
</section>
<section class='block' id='agents'>
<h2>{AGENT_HEADING}</h2>
<p class='lead'>The outer product surface is now compare-first: <code>ts_compare</code> when you already have a pair, <code>ts_profile</code> when you need structure context first, and <code>ts_route</code> when another agent needs the smallest useful next step.</p>
<div class='grid2'>
<div class='card'><h3>Why this saves tokens</h3><ul><li>Start with the cheapest informative move.</li><li>Stop early when the signal is already clear.</li><li>Return a stable success/error envelope with confidence, evidence, and next actions.</li></ul></div>
<div class='card'><h3>Caller contract in one line</h3><pre><code>ts_profile({{data_ref, input_kind, timestamps_ref, domain, budget, audience}})
ts_compare({{left_ref, right_ref, left_timestamps_ref, right_timestamps_ref, mode, budget}})
ts_route({{task, available_inputs, has_reference}})</code></pre></div>
</div>
</section>
<section class='block'>
<h2>Starter datasets</h2>
<p class='lead'>Bundled starter datasets make the repo easier to try, easier to teach, and easier to demo across disciplines.</p>
<table><thead><tr><th>Dataset</th><th>Domain</th><th>Kind</th><th>Why it exists</th></tr></thead><tbody>{starter_rows}</tbody></table>
</section>
<section class='block' id='trust'>
<h2>{TRUST_HEADING}</h2>
<p class='lead'>A GitHub-ready project needs more than code: docs, visuals, demos, schemas, and repo basics.</p>
<div class='grid3'>
<div class='card'><strong>README + homepage</strong><p class='muted'>Clear first-minute value.</p></div>
<div class='card'><strong>Pages-ready demo bundle</strong><p class='muted'>Publish the product layer as static files.</p></div>
<div class='card'><strong>Stable agent schemas</strong><p class='muted'>Function-calling and MCP-friendly contracts.</p></div>
<div class='card'><strong>Notebooks + starter datasets</strong><p class='muted'>Clone-and-run examples across disciplines.</p></div>
<div class='card'><strong>Decision-impact benchmark</strong><p class='muted'>A modest but reproducible product benchmark.</p></div>
<div class='card'><strong>Social cards + GIFs</strong><p class='muted'>Growth assets instead of pure documentation.</p></div>
</div>
</section>
</main>
<footer class='container footer'>Compare-first, product-oriented, and GitHub Pages-ready. Next step: push the docs bundle to a live demo URL and operate the flagship analog cases as a steady showcase stream.</footer>
</body>
</html>"""
