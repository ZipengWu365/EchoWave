"""Static homepage generator for EchoWave v0.16.0.

The homepage is a bright, scientific, GitHub Pages-friendly landing page for
the EchoWave ecosystem. It favors clarity and trust over decoration while
keeping the product surface demo-forward.
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
    HOMEPAGE_PILLS,
    INSTALL_HEADING,
    LIVE_DEMO_HEADING,
    PACKAGE_STAGE,
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
    ZERO_INSTALL_OPTIONS,
)
from .datasets import list_starter_datasets, starter_dataset
from .design_system import page_head
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


def _normalize_public_copy(text: str) -> str:
    return (
        text.replace("tsontology", DISPLAY_NAME)
        .replace("TSontology", DISPLAY_NAME)
        .replace("dataset-first structural profiling", "explainable structural similarity")
        .replace("Dataset-first structural profiling", "Dataset structure and similarity context")
    )


def _ecosystem_rows() -> str:
    payload = ecosystem_positioning(format="json")
    rows = []
    for entry in payload["entries"][:6]:
        strongest = ", ".join(entry["strongest_for"][:3])
        rows.append(
            f"<tr><td><strong>{escape(entry['name'])}</strong></td><td>{escape(entry['family'])}</td><td>{escape(strongest)}</td><td>{escape(_normalize_public_copy(entry['tsontology_relation']))}</td></tr>"
        )
    return "\n".join(rows)


def _coverage_rows() -> str:
    payload = coverage_matrix(format="json")
    rows = []
    for row in payload["rows"][:8]:
        companions = ", ".join(row["best_companions"]) if row["best_companions"] else "-"
        rows.append(
            f"<tr><td>{escape(_normalize_public_copy(row['capability']))}</td><td>{escape(row['tsontology_role'])}</td><td>{escape(companions)}</td><td>{escape(_normalize_public_copy(row['notes']))}</td></tr>"
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
            "<div class='card feature-card sun'>"
            "<span class='pill sun'>Flagship demo</span>"
            f"<h3>{escape(item['title'])}</h3>"
            f"<p>{escape(item['story'])}</p>"
            f"<div class='note-box info'>{escape(item['social_hook'])}</div>"
            "</div>"
        )
    return "\n".join(cards)


def _zero_install_cards() -> str:
    return "\n".join(
        "<div class='card feature-card'>"
        f"<span class='pill blue'>{escape(item['title'])}</span>"
        f"<p>{escape(item['why'])}</p>"
        "</div>"
        for item in ZERO_INSTALL_OPTIONS
    )


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

    radar = profile_radar_svg(traffic_profile, width=420, height=380)
    bars = axis_bar_svg(traffic_profile, width=560, height=300)
    overlay = series_overlay_svg(
        github_case["target"],
        github_case["durable_breakout"],
        left_label="OpenClaw-style candidate",
        right_label="durable breakout analog",
        width=620,
        height=250,
    )
    comp = similarity_components_svg(github_report, width=620, height=250)
    roll_svg = rolling_similarity_svg(windows, width=620, height=250)
    summary_preview = escape(
        explain_similarity(
            github_case["target"],
            github_case["durable_breakout"],
            left_name="OpenClaw-style candidate",
            right_name="durable breakout analog",
        )
    )
    social_left = similarity_social_card_svg(github_report, title="GitHub breakout analogs")
    social_right = profile_social_card_svg(traffic_profile, title="Website traffic structure")
    starter_rows = _starter_rows()
    ecosystem_rows = _ecosystem_rows()
    coverage_rows = _coverage_rows()
    flagship_cards = _flagship_cards()
    zero_cards = _zero_install_cards()
    homepage_pills = "".join(f"<span class='pill'>{escape(item)}</span>" for item in HOMEPAGE_PILLS)
    quick_expected = escape("\n".join(QUICKSTART_EXPECTED_LINES))
    trust_logos = "".join(
        f"<span class='logo-chip'><span class='logo-dot'></span>{escape(item)}</span>"
        for item in (
            "MIT License",
            f"{PACKAGE_STAGE} release",
            "GitHub Pages",
            "Agent tools",
            AUTHOR_AFFILIATION,
        )
    )

    extra_css = """
    .hero-copy { display:grid; gap:16px; }
    .hero-visual { display:grid; gap:16px; }
    .hero-visual-grid { display:grid; grid-template-columns: 1fr 1fr; gap:14px; }
    .mini-kicker { color: var(--sun-700); font-size: 0.9rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
    .problem-grid { display:grid; grid-template-columns: 0.95fr 1.05fr; gap: 20px; }
    .cta-band { display:grid; gap:14px; padding: 22px 24px; border:1px solid rgba(255,200,61,0.46); border-radius: var(--radius-lg); background: linear-gradient(135deg, #fffdf4 0%, #ffffff 100%); box-shadow: var(--shadow-sm); }
    .eyebrow-line { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
    .section-stack { display:grid; gap:20px; }
    .report-stack { display:grid; gap:20px; }
    .brand-links { display:flex; flex-wrap:wrap; gap:12px; }
    .cta-row { display:flex; flex-wrap:wrap; gap:12px; margin-top: 4px; }
    .author-band { display:grid; gap:8px; }
    @media (max-width: 980px) {
      .problem-grid, .hero-visual-grid { grid-template-columns: 1fr; }
    }
    """

    return f"""<!doctype html>
<html lang='en'>
{page_head(f"{DISPLAY_NAME} - {TAGLINE}", extra_css=extra_css)}
<body>
<header class='topbar'>
  <div class='shell topbar-inner'>
    <div class='brand'>
      <span class='brand-mark'></span>
      <div class='brand-copy'>
        <strong>{DISPLAY_NAME}</strong>
        <span>{escape(TAGLINE)}</span>
      </div>
    </div>
    <nav class='nav'>
      <a href='#problem'>Problem</a>
      <a href='#features'>Features</a>
      <a href='#workflow'>Workflow</a>
      <a href='#quickstart'>{INSTALL_HEADING}</a>
      <a href='#demos'>Demos</a>
      <a href='#ecosystem'>{ECOSYSTEM_HEADING}</a>
      <a href='#cta'>Get started</a>
    </nav>
  </div>
</header>
<main class='shell'>
  <section class='hero'>
    <div class='hero-grid'>
      <div class='hero-copy'>
        <div class='eyebrow'>Bright scientific design system</div>
        <div class='hero-stage'>
          <div class='mini-kicker'>Version {escape(version)} · Compare-first release surface</div>
          <h1>{escape(HEADLINE)}</h1>
          <p class='subhead'>{escape(PRODUCT_PROMISE)} It is designed for the moment when one opaque distance score is not enough for a researcher, engineer, founder, or downstream agent.</p>
        </div>
        <div class='badge-row'>{homepage_pills}</div>
        <div class='button-row'>
          <a class='button primary' href='#quickstart'>Run the 60-second quickstart</a>
          <a class='button secondary' href='playground.html?case=openclaw_breakout_analogs'>Open static playground</a>
          <a class='button ghost' href='start-here.html'>Start here</a>
        </div>
        <div class='trust-strip'>{trust_logos}</div>
        <div class='hero-stat'>
          <div class='stat'><span class='muted'>Core promise</span><strong>Explainable similarity</strong><span class='muted'>for series and datasets</span></div>
          <div class='stat'><span class='muted'>Delivery surface</span><strong>HTML + JSON</strong><span class='muted'>for humans and agents</span></div>
          <div class='stat'><span class='muted'>Distribution</span><strong>Pages-ready</strong><span class='muted'>plus local demo</span></div>
        </div>
      </div>
      <div class='hero-visual'>
        <div class='card sun feature-card'>
          <div class='eyebrow-line'>
            <span class='pill sun'>Sunny research brand</span>
            <span class='pill blue'>{escape(AUTHOR_AFFILIATION)}</span>
          </div>
          <p><strong>EchoWave is a premium technical product surface on top of scientific time-series comparison.</strong> It stays white-background-first, readable, and trustworthy instead of leaning on dark hacker aesthetics.</p>
          <div class='hero-visual-grid'>
            <img class='brand-card' src='social/echowave_title_card.svg' alt='EchoWave title card'/>
            <img class='brand-card' src='social/bham_affiliation_badge.svg' alt='Zipeng Wu at The University of Birmingham'/>
          </div>
          <div class='author-meta'>
            <strong>{escape(AUTHOR_NAME)}</strong>
            <span>{escape(AUTHOR_AFFILIATION)}</span>
            <a href='mailto:{escape(AUTHOR_EMAIL)}'>{escape(AUTHOR_EMAIL)}</a>
            <div class='brand-links'>
              <a href='{escape(PROJECT_REPOSITORY_URL)}'>{escape(PROJECT_REPOSITORY_URL)}</a>
              <a href='{escape(PROJECT_DOCUMENTATION_URL)}'>{escape(PROJECT_DOCUMENTATION_URL)}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class='section' id='problem'>
    <div class='section-head'>
      <div class='eyebrow'>Problem statement</div>
      <h2>Raw distance scores are usually too weak for real collaboration</h2>
      <p class='lead'>The product reality is simple: teams need to know whether two curves are meaningfully alike, whether two datasets are structurally similar enough to share intuition, and why the package believes that. EchoWave turns that into a readable artifact instead of a naked metric.</p>
    </div>
    <div class='problem-grid'>
      <div class='card soft feature-card'>
        <span class='pill blue'>Why people get stuck</span>
        <ul class='panel-list'>
          <li>A single score does not explain whether similarity comes from shape, trend, rhythm, or observation regime.</li>
          <li>Dataset-level comparison gets lost when scale, cadence, or observation style differs.</li>
          <li>Teams need a handoff artifact for colleagues, notebooks, or AI agents, not just a scalar.</li>
        </ul>
      </div>
      <div class='card feature-card'>
        <span class='pill sun'>What EchoWave adds</span>
        <ul class='panel-list'>
          <li>Series-to-series comparison with interpretable component breakdowns.</li>
          <li>Dataset structure context that explains what makes a match convincing or fragile.</li>
          <li>Shareable HTML and stable JSON envelopes for downstream automation.</li>
        </ul>
      </div>
    </div>
  </section>

  <section class='section' id='features'>
    <div class='section-head'>
      <div class='eyebrow'>Key features</div>
      <h2>A small product surface with strong technical hierarchy</h2>
      <p class='lead'>This repo should scan like a premium scientific tool: one main task, a few strong surfaces, and zero clutter.</p>
    </div>
    <div class='grid-3'>
      <div class='card feature-card'>
        <span class='pill blue'>Compare series</span>
        <h3>Readable verdicts</h3>
        <p>Turn two curves into a similarity verdict with component-level evidence and recommended next actions.</p>
      </div>
      <div class='card feature-card sun'>
        <span class='pill sun'>Compare datasets</span>
        <h3>Structural context first</h3>
        <p>Profile cadence, burstiness, regimes, and heterogeneity before pretending two datasets are interchangeable.</p>
      </div>
      <div class='card feature-card'>
        <span class='pill blue'>Agent handoff</span>
        <h3>Stable outer wrapper</h3>
        <p>Use compare-first JSON envelopes in function calling, MCP wrappers, or lightweight research agents.</p>
      </div>
    </div>
  </section>

  <section class='section' id='workflow'>
    <div class='section-head'>
      <div class='eyebrow'>Architecture diagram</div>
      <h2>One ecosystem workflow across repos</h2>
      <p class='lead'>The design language and the product flow are aligned: ingest a signal, compare or profile, then hand off a clean artifact to the rest of the stack.</p>
    </div>
    <div class='diagram'>
      <div class='diagram-flow'>
        <div class='logo-chip'><span class='logo-dot'></span>Signals or datasets</div>
        <div class='diagram-arrow'>&rarr;</div>
        <div class='logo-chip'><span class='logo-dot'></span>EchoWave similarity layer</div>
        <div class='diagram-arrow'>&rarr;</div>
        <div class='logo-chip'><span class='logo-dot'></span>HTML, README, or agent JSON</div>
      </div>
      <div class='diagram-band'>
        <div class='diagram-card'>
          <h3>1. Observe</h3>
          <p>Input dense, irregular, multichannel, or event-style time series without forcing a fake one-size-fits-all workflow.</p>
        </div>
        <div class='diagram-card'>
          <h3>2. Explain similarity</h3>
          <p>Combine raw shape comparison with structural context so the verdict stays interpretable under real-world variation.</p>
        </div>
        <div class='diagram-card'>
          <h3>3. Ship the artifact</h3>
          <p>Export a shareable report, a social preview, or a compact machine-facing payload for the next step.</p>
        </div>
      </div>
    </div>
  </section>

  <section class='section' id='quickstart'>
    <div class='section-head'>
      <div class='eyebrow'>Quickstart</div>
      <h2>The first minute should produce a real result</h2>
      <p class='lead'>Clean onboarding matters more than clever prose. This repo now makes the first action obvious and the expected output visible.</p>
    </div>
    <div class='grid-2'>
      <div class='card feature-card'>
        <span class='pill sun'>{INSTALL_HEADING}</span>
        <pre><code>{escape(QUICKSTART_INSTALL)}
{escape(QUICKSTART_ONE_LINER)}</code></pre>
      </div>
      <div class='card feature-card'>
        <span class='pill blue'>Expected output</span>
        <pre><code>{quick_expected}</code></pre>
      </div>
    </div>
    <div class='grid-3' style='margin-top:20px'>
      {zero_cards}
    </div>
  </section>

  <section class='section' id='demos'>
    <div class='section-head'>
      <div class='eyebrow'>Demo and screenshots</div>
      <h2>Pages-ready visuals, not just notebook output</h2>
      <p class='lead'>The landing page should feel like a bright research-lab product: calm layout, clear hierarchy, and just enough visual proof to make the capability memorable.</p>
    </div>
    <div class='grid-2'>
      <div class='surface-frame pad'>{overlay}</div>
      <div class='card feature-card'>
        <span class='pill blue'>Plain-English verdict</span>
        <pre><code>{summary_preview}</code></pre>
      </div>
    </div>
    <div class='grid-2' style='margin-top:20px'>
      <div class='surface-frame pad'>{comp}</div>
      <div class='surface-frame pad'>{roll_svg}</div>
    </div>
    <div class='grid-2' style='margin-top:20px'>
      <div class='surface-frame pad'>{social_left}</div>
      <div class='surface-frame pad'>{social_right}</div>
    </div>
    <div class='grid-2' style='margin-top:20px'>
      <div class='surface-frame pad'>{radar}</div>
      <div class='surface-frame pad'>{bars}</div>
    </div>
    <div class='grid-2' style='margin-top:20px'>
      <div class='card feature-card'>
        <span class='pill sun'>{PAGES_HEADING}</span>
        <p><strong>{LIVE_DEMO_HEADING}:</strong> the repo ships both a static GitHub Pages showcase and a tiny live demo server. Use the static path for linkability and the local path for real computation.</p>
        <div class='button-row'>
          <a class='button primary' href='playground.html?case=openclaw_breakout_analogs'>Open the playground</a>
          <a class='button secondary' href='start-here.html'>Open start-here</a>
        </div>
      </div>
      <div class='surface-frame'>
        <iframe class='demo' src='playground.html?case=openclaw_breakout_analogs' title='EchoWave playground preview'></iframe>
      </div>
    </div>
  </section>

  <section class='section'>
    <div class='section-head'>
      <div class='eyebrow'>Flagship showcases</div>
      <h2>Demos built to travel across GitHub, social, and docs</h2>
      <p class='lead'>The strongest growth assets are not generic charts. They are memorable analog questions with a direct story.</p>
    </div>
    <div class='grid-3'>
      {flagship_cards}
    </div>
  </section>

  <section class='section' id='ecosystem'>
    <div class='section-head'>
      <div class='eyebrow'>Ecosystem</div>
      <h2>{ECOSYSTEM_HEADING}</h2>
      <p class='lead'>EchoWave is not trying to replace modelling stacks or the fastest DTW engines. It owns the explainable-comparison layer in front of them.</p>
    </div>
    <table>
      <thead><tr><th>Package</th><th>Family</th><th>Strongest fit</th><th>How EchoWave fits</th></tr></thead>
      <tbody>{ecosystem_rows}</tbody>
    </table>
  </section>

  <section class='section' id='coverage'>
    <div class='section-head'>
      <div class='eyebrow'>Coverage</div>
      <h2>{COVERAGE_HEADING}</h2>
      <p class='lead'>Be explicit about scope. Clarity builds trust faster than pretending the package does everything.</p>
    </div>
    <table>
      <thead><tr><th>Capability</th><th>Role</th><th>Companion packages</th><th>Notes</th></tr></thead>
      <tbody>{coverage_rows}</tbody>
    </table>
  </section>

  <section class='section' id='agents'>
    <div class='section-head'>
      <div class='eyebrow'>Agent-ready design</div>
      <h2>{AGENT_HEADING}</h2>
      <p class='lead'>The outside-facing tools stay intentionally small so an agent can choose the cheapest useful step and return a stable envelope.</p>
    </div>
    <div class='grid-2'>
      <div class='card feature-card'>
        <span class='pill blue'>Tooling surface</span>
        <pre><code>ts_profile({{data_ref, input_kind, timestamps_ref, domain, budget, audience}})
ts_compare({{left_ref, right_ref, left_timestamps_ref, right_timestamps_ref, mode, budget}})
ts_route({{task, available_inputs, has_reference}})</code></pre>
      </div>
      <div class='card feature-card'>
        <span class='pill sun'>Why this stays cheap</span>
        <ul class='panel-list'>
          <li>Compare first when you already have a candidate pair.</li>
          <li>Profile only when structural context is the missing piece.</li>
          <li>Return confidence, evidence, and next actions in one compact wrapper.</li>
        </ul>
      </div>
    </div>
  </section>

  <section class='section' id='benchmark'>
    <div class='section-head'>
      <div class='eyebrow'>Benchmark reality</div>
      <h2>{BENCHMARK_HEADING}</h2>
      <p class='lead'>This repo now looks like a product, but the benchmark story is still deliberately modest. The shipped evidence is decision-support evidence, not a publication-grade leaderboard.</p>
    </div>
    <div class='grid-2'>
      <div class='note-box info'>
        <strong>What exists</strong>
        <p>A reproducible decision-impact benchmark and a coherent product claim: readable similarity context can change downstream choices.</p>
      </div>
      <div class='note-box warn'>
        <strong>What is still missing</strong>
        <p>A full retrieval benchmark, stronger robustness studies, and broader public adoption proof.</p>
      </div>
    </div>
  </section>

  <section class='section'>
    <div class='section-head'>
      <div class='eyebrow'>Starter datasets</div>
      <h2>Cross-disciplinary entry points</h2>
      <p class='lead'>These bundled cases make it easier for medicine, engineering, economics, and product users to find their first relevant example fast.</p>
    </div>
    <table>
      <thead><tr><th>Dataset</th><th>Domain</th><th>Kind</th><th>Why it exists</th></tr></thead>
      <tbody>{starter_rows}</tbody>
    </table>
  </section>

  <section class='section' id='trust'>
    <div class='section-head'>
      <div class='eyebrow'>Trust layer</div>
      <h2>{TRUST_HEADING}</h2>
      <p class='lead'>Reliable open source products need more than code. They need docs, assets, demo entry points, schemas, and clean packaging surfaces.</p>
    </div>
    <div class='grid-3'>
      <div class='card feature-card'><span class='pill blue'>README + Pages</span><p>One bright, consistent brand surface across docs, demos, and GitHub.</p></div>
      <div class='card feature-card'><span class='pill sun'>Schemas</span><p>Stable function-calling and MCP descriptors for agents.</p></div>
      <div class='card feature-card'><span class='pill blue'>Starter assets</span><p>Notebooks, datasets, title cards, and social previews ready to publish.</p></div>
    </div>
  </section>

  <section class='section' id='cta'>
    <div class='cta-band'>
      <div class='section-head'>
        <div class='eyebrow'>Final call to action</div>
        <h2>Start with a flagship analog, then adapt the surface across your repo ecosystem</h2>
        <p class='lead'>This landing page, the GitHub README, the Pages bundle, and the design tokens now belong to the same bright scientific brand. That consistency is what makes multi-repo discoverability and trust compound over time.</p>
      </div>
      <div class='cta-row'>
        <a class='button primary' href='playground.html?case=openclaw_breakout_analogs'>Open the playground</a>
        <a class='button secondary' href='start-here.html'>Use the start-here flow</a>
        <a class='button ghost' href='{escape(PROJECT_REPOSITORY_URL)}'>View the repo</a>
      </div>
    </div>
  </section>
</main>
<footer class='shell footer'>
  <div class='footer-grid'>
    <div>
      <strong>{DISPLAY_NAME}</strong>
      <p class='lead'>Sunny, energetic, optimistic scientific software for explainable time-series similarity. Designed to feel like a modern research lab and a premium technical product at the same time.</p>
    </div>
    <div class='author-band'>
      <span>{escape(AUTHOR_NAME)} · {escape(AUTHOR_AFFILIATION)}</span>
      <a href='mailto:{escape(AUTHOR_EMAIL)}'>{escape(AUTHOR_EMAIL)}</a>
      <a href='{escape(PROJECT_DOCUMENTATION_URL)}'>{escape(PROJECT_DOCUMENTATION_URL)}</a>
    </div>
  </div>
</footer>
</body>
</html>"""


__all__ = ["project_homepage_html"]
