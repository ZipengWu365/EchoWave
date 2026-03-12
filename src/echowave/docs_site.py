"""Docs-style pages for EchoWave.

These pages separate landing-page content from documentation content, closer
to a scikit-learn-style information architecture: a lightweight homepage and
dedicated tutorial / API / scenario pages with a persistent sidebar.
"""

from __future__ import annotations

from collections import defaultdict
from html import escape
from typing import Iterable

from .agent_tools import TOOL_SCHEMA_VERSION
from .copydeck import (
    AGENT_HEADING,
    AUTHOR_AFFILIATION,
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    BEGINNER_EXAMPLES,
    DISPLAY_NAME,
    ECOSYSTEM_HEADING,
    FLAGSHIP_DEMOS,
    HEADLINE,
    PACKAGE_VERSION,
    PROJECT_DOCUMENTATION_URL,
    PROJECT_REPOSITORY_URL,
    QUICKSTART_EXPECTED_LINES,
    QUICKSTART_INSTALL,
    QUICKSTART_ONE_LINER,
    TAGLINE,
    ZERO_INSTALL_OPTIONS,
)
from .datasets import list_starter_datasets
from .design_system import page_head
from .guide import API_ENTRIES, SCENARIOS
from .positioning import coverage_matrix, ecosystem_positioning

DOC_PAGES = (
    ("index", "Docs Home"),
    ("getting-started", "Getting Started"),
    ("tutorials", "Tutorials"),
    ("api", "API Reference"),
    ("scenarios", "Scenarios"),
    ("ecosystem", "Ecosystem"),
    ("agents", "Agent Tools"),
)


def _clean(text: str) -> str:
    return (
        str(text)
        .replace("tsontology", DISPLAY_NAME)
        .replace("TSontology", DISPLAY_NAME)
        .replace("¡Á", " x ")
        .replace("脳", " x ")
        .replace("鈥", "-")
        .replace("dataset-first structural profiling", "explainable structural similarity")
        .replace("Dataset-first structural profiling", "Dataset structure and similarity context")
    )


def _pill(label: str, tone: str = "") -> str:
    cls = "pill"
    if tone:
        cls += f" {tone}"
    return f"<span class='{cls}'>{escape(label)}</span>"


def _doc_shell(*, page_key: str, title: str, lead: str, body: str) -> str:
    sidebar = []
    for key, label in DOC_PAGES:
        href = "index.html" if key == "index" else f"{key}.html"
        active = " active" if key == page_key else ""
        sidebar.append(f"<a class='doc-link{active}' href='{href}'>{escape(label)}</a>")
    extra_css = """
    .docs-wrap { display:grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; padding: 28px 0 40px; }
    .docs-sidebar { position: sticky; top: 94px; align-self: start; display:grid; gap:18px; }
    .sidebar-card { background: var(--surface-strong); border:1px solid var(--border); border-radius: var(--radius-md); padding: 18px; box-shadow: var(--shadow-sm); }
    .sidebar-title { margin:0 0 10px; font-size: 0.86rem; color: var(--text-600); font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
    .doc-link { display:block; padding: 10px 12px; border-radius: 12px; color: var(--text-600); font-weight: 600; }
    .doc-link:hover { background: rgba(47,107,255,0.06); color: var(--text-900); }
    .doc-link.active { background: rgba(255, 244, 194, 0.78); color: var(--text-900); border:1px solid rgba(255,200,61,0.38); }
    .docs-main { display:grid; gap: 24px; min-width: 0; }
    .docs-hero { display:grid; gap: 12px; }
    .docs-hero h1 { font-size: clamp(2.1rem, 4vw, 3.3rem); line-height: 1.02; }
    .docs-card { background: var(--surface-strong); border:1px solid var(--border); border-radius: var(--radius-md); padding: 22px 24px; box-shadow: var(--shadow-sm); display:grid; gap: 12px; }
    .docs-grid-2, .docs-grid-3 { display:grid; gap: 20px; }
    .docs-grid-2 { grid-template-columns: 1fr 1fr; }
    .docs-grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .meta-line { display:flex; flex-wrap:wrap; gap: 10px; }
    .meta-chip { display:inline-flex; align-items:center; gap:6px; padding: 6px 10px; border-radius: 999px; background: var(--surface); border:1px solid var(--border); color: var(--text-600); font-size: 0.84rem; font-weight: 700; }
    .meta-chip strong { color: var(--text-900); }
    .entry-stack { display:grid; gap: 16px; }
    .entry { border-top: 1px solid var(--border); padding-top: 16px; }
    .entry:first-child { border-top: 0; padding-top: 0; }
    .entry h3 { font-size: 1.1rem; }
    .inline-code { font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; background: #fffef8; border:1px solid var(--border); padding: 2px 6px; border-radius: 8px; }
    .small-table { width:100%; border-collapse:collapse; }
    .small-table th, .small-table td { padding: 11px 12px; text-align:left; border-bottom:1px solid var(--border); vertical-align: top; }
    .small-table th { background: #fffdf6; color: var(--text-600); font-size: 0.9rem; }
    .small-table tr:last-child td { border-bottom: 0; }
    .toc-note { font-size: 0.92rem; color: var(--text-600); }
    @media (max-width: 980px) {
      .docs-wrap { grid-template-columns: 1fr; }
      .docs-sidebar { position: static; }
      .docs-grid-2, .docs-grid-3 { grid-template-columns: 1fr; }
    }
    """
    return f"""<!doctype html>
<html lang='en'>
{page_head(f"{DISPLAY_NAME} docs - {title}", extra_css=extra_css)}
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
      <a href='../index.html'>Home</a>
      <a href='index.html'>Docs</a>
      <a href='tutorials.html'>Tutorials</a>
      <a href='api.html'>API</a>
      <a href='../playground.html'>Playground</a>
      <a href='{escape(PROJECT_REPOSITORY_URL)}'>GitHub</a>
    </nav>
  </div>
</header>
<main class='shell docs-wrap'>
  <aside class='docs-sidebar'>
    <div class='sidebar-card'>
      <div class='sidebar-title'>Documentation</div>
      {"".join(sidebar)}
    </div>
    <div class='sidebar-card'>
      <div class='sidebar-title'>Quick links</div>
      <a class='doc-link' href='../playground.html'>Static playground</a>
      <a class='doc-link' href='../start-here.html'>Start here</a>
      <a class='doc-link' href='../reports/github_breakout_similarity.html'>Flagship report</a>
    </div>
    <div class='sidebar-card'>
      <div class='sidebar-title'>Maintainer</div>
      <div class='toc-note'><strong>{escape(AUTHOR_NAME)}</strong><br>{escape(AUTHOR_AFFILIATION)}<br><a href='mailto:{escape(AUTHOR_EMAIL)}'>{escape(AUTHOR_EMAIL)}</a></div>
    </div>
  </aside>
  <section class='docs-main'>
    <div class='docs-hero'>
      <div class='eyebrow'>Documentation</div>
      <h1>{escape(title)}</h1>
      <p class='subhead'>{escape(lead)}</p>
    </div>
    {body}
  </section>
</main>
</body>
</html>"""


def _overview_cards() -> str:
    cards = [
        ("Getting Started", "Install, zero-install paths, and the first 60 seconds.", "getting-started.html", "sun"),
        ("Tutorials", "Beginner examples, flagship demos, and starter datasets.", "tutorials.html", "blue"),
        ("API Reference", "The public compare/profile surface and result objects.", "api.html", "sun"),
        ("Scenarios", "Where EchoWave fits across medicine, engineering, product, and research.", "scenarios.html", "blue"),
        ("Ecosystem", "How EchoWave complements sktime, tsfresh, DTAIDistance, and others.", "ecosystem.html", "sun"),
        ("Agent Tools", "Compact routing, stable schemas, and compare-first wrappers.", "agents.html", "blue"),
    ]
    return "".join(
        "<div class='docs-card'>"
        f"{_pill(label, tone)}"
        f"<h3>{escape(label)}</h3>"
        f"<p>{escape(text)}</p>"
        f"<a class='button ghost' href='{href}'>Open page</a>"
        "</div>"
        for label, text, href, tone in cards
    )


def project_docs_home_html(*, version: str = PACKAGE_VERSION) -> str:
    expected = escape("\n".join(QUICKSTART_EXPECTED_LINES))
    body = f"""
    <div class='docs-grid-2'>
      <div class='docs-card'>
        {_pill('Docs home', 'sun')}
        <p><strong>EchoWave separates its landing page from its documentation.</strong> The homepage is now a product entry point, while the docs area is organized like a proper technical manual with a persistent left sidebar.</p>
        <div class='meta-line'>
          <span class='meta-chip'><strong>Version</strong> {escape(version)}</span>
          <span class='meta-chip'><strong>Audience</strong> researchers, engineers, technical founders</span>
        </div>
      </div>
      <div class='docs-card'>
        {_pill('60-second quickstart', 'blue')}
        <pre><code>{escape(QUICKSTART_INSTALL)}
{escape(QUICKSTART_ONE_LINER)}</code></pre>
      </div>
    </div>
    <div class='docs-grid-3'>
      {_overview_cards()}
    </div>
    <div class='docs-card'>
      {_pill('Expected output', 'sun')}
      <pre><code>{expected}</code></pre>
    </div>
    """
    return _doc_shell(
        page_key="index",
        title="Documentation Home",
        lead="A docs-first entry point inspired by scikit-learn: separate pages, strong left navigation, and clear boundaries between tutorials, API reference, and ecosystem guidance.",
        body=body,
    )


def project_getting_started_html(*, version: str = PACKAGE_VERSION) -> str:
    expected = escape("\n".join(QUICKSTART_EXPECTED_LINES))
    zero_cards = "".join(
        "<div class='docs-card'>"
        f"{_pill(item['title'], 'blue')}"
        f"<p>{escape(item['why'])}</p>"
        "</div>"
        for item in ZERO_INSTALL_OPTIONS
    )
    body = f"""
    <div class='docs-card'>
      {_pill('Install', 'sun')}
      <pre><code>{escape(QUICKSTART_INSTALL)}
{escape(QUICKSTART_ONE_LINER)}</code></pre>
      <p>EchoWave keeps the install surface light, but mixed scientific Python stacks can still produce resolver noise. Use a clean environment when possible, and use the compatibility / doctor flow when you cannot.</p>
    </div>
    <div class='docs-grid-2'>
      <div class='docs-card'>
        {_pill('Expected output', 'blue')}
        <pre><code>{expected}</code></pre>
      </div>
      <div class='docs-card'>
        {_pill('First minute', 'sun')}
        <ul class='panel-list'>
          <li>Use the homepage when you want a product-level overview.</li>
          <li>Use the static playground when you want a zero-install demo.</li>
          <li>Use <span class='inline-code'>start-here.html</span> when you want the local demo, doctor, and Pages export in one place.</li>
        </ul>
      </div>
    </div>
    <div class='docs-grid-2'>
      {zero_cards}
    </div>
    <div class='docs-card'>
      {_pill('Install notes', 'blue')}
      <ul class='panel-list'>
        <li>Core install is intentionally small: numpy and scipy.</li>
        <li>Older aeon / sktime / numba-heavy stacks may still surface resolver warnings.</li>
        <li>If you only need proof of value first, use the static Pages bundle or local demo instead of installing into a crowded environment immediately.</li>
      </ul>
    </div>
    """
    return _doc_shell(
        page_key="getting-started",
        title="Getting Started",
        lead="The job of this page is simple: make the first successful EchoWave interaction obvious, fast, and realistic.",
        body=body,
    )


def project_tutorials_html(*, version: str = PACKAGE_VERSION) -> str:
    beginner_cards = "".join(
        "<div class='docs-card'>"
        f"{_pill(example['title'], 'sun')}"
        f"<p>{escape(example['why'])}</p>"
        "</div>"
        for example in BEGINNER_EXAMPLES
    )
    flagship_cards = "".join(
        "<div class='docs-card'>"
        f"{_pill(demo['title'], 'blue')}"
        f"<p>{escape(demo['story'])}</p>"
        f"<div class='note-box info'>{escape(demo['social_hook'])}</div>"
        "</div>"
        for demo in FLAGSHIP_DEMOS
    )
    rows = "\n".join(
        f"<tr><td><strong>{escape(item['title'])}</strong><br><span class='muted'>{escape(item['name'])}</span></td><td>{escape(item['domain'])}</td><td>{escape(item['kind'])}</td><td>{escape(item['why'])}</td></tr>"
        for item in list_starter_datasets()
    )
    body = f"""
    <div class='docs-card'>
      {_pill('Tutorial map', 'sun')}
      <p>This page is where users should browse examples. It is intentionally separate from the homepage so the landing page stays short and the tutorials stay discoverable.</p>
    </div>
    <div class='docs-grid-3'>
      {beginner_cards}
    </div>
    <div class='docs-card'>
      {_pill('Flagship demos', 'blue')}
      <div class='docs-grid-3'>
        {flagship_cards}
      </div>
    </div>
    <div class='docs-card'>
      {_pill('Starter datasets', 'sun')}
      <table class='small-table'>
        <thead><tr><th>Dataset</th><th>Domain</th><th>Kind</th><th>Why it exists</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """
    return _doc_shell(
        page_key="tutorials",
        title="Tutorials and Examples",
        lead="Begin with tiny scenarios, then move to flagship demos built for GitHub, talks, social posts, and notebooks.",
        body=body,
    )


def project_api_reference_html(*, version: str = PACKAGE_VERSION) -> str:
    grouped = defaultdict(list)
    for entry in API_ENTRIES:
        grouped[_clean(entry.category)].append(entry)
    sections = []
    for category, entries in grouped.items():
        entry_html = []
        for entry in entries:
            accepted = "".join(f"<li>{escape(_clean(item))}</li>" for item in entry.accepted_inputs)
            outputs = "".join(f"<li>{escape(_clean(item))}</li>" for item in entry.outputs_to_inspect)
            envs = ", ".join(_clean(item) for item in entry.recommended_environments)
            entry_html.append(
                "<div class='entry'>"
                f"<h3><span class='inline-code'>{escape(entry.name)}</span></h3>"
                f"<p><strong>Signature:</strong> <span class='inline-code'>{escape(_clean(entry.signature))}</span></p>"
                f"<p><strong>Purpose:</strong> {escape(_clean(entry.purpose))}</p>"
                f"<p><strong>Why this exists:</strong> {escape(_clean(entry.why_exists))}</p>"
                f"<p><strong>When to use it:</strong> {escape(_clean(entry.when_to_use))}</p>"
                f"<p><strong>Returns:</strong> {escape(_clean(entry.returns))}</p>"
                f"<p><strong>Recommended environments:</strong> {escape(envs)}</p>"
                "<div class='docs-grid-2'>"
                f"<div><strong>Accepted inputs</strong><ul class='panel-list'>{accepted}</ul></div>"
                f"<div><strong>Inspect these outputs</strong><ul class='panel-list'>{outputs}</ul></div>"
                "</div>"
                "</div>"
            )
        sections.append(
            "<div class='docs-card'>"
            f"{_pill(category, 'blue')}"
            f"<div class='entry-stack'>{''.join(entry_html)}</div>"
            "</div>"
        )
    body = "".join(sections)
    return _doc_shell(
        page_key="api",
        title="API Reference",
        lead="The public API surface is intentionally small and role-based: compare, profile, summarize, and hand off.",
        body=body,
    )


def project_scenarios_html(*, version: str = PACKAGE_VERSION) -> str:
    cards = []
    for scenario in SCENARIOS:
        environments = ", ".join(_clean(item) for item in scenario.environments)
        domains = ", ".join(_clean(item) for item in scenario.domains)
        inputs = "".join(f"<li>{escape(_clean(item))}</li>" for item in scenario.typical_inputs)
        actions = "".join(f"<li>{escape(_clean(item))}</li>" for item in scenario.what_you_can_do)
        caveats = "".join(f"<li>{escape(_clean(item))}</li>" for item in scenario.caveats)
        cards.append(
            "<div class='docs-card'>"
            f"{_pill(scenario.title, 'sun')}"
            f"<div class='meta-line'><span class='meta-chip'><strong>Domains</strong> {escape(domains)}</span><span class='meta-chip'><strong>Environments</strong> {escape(environments)}</span></div>"
            f"<p><strong>Data shape:</strong> {escape(_clean(scenario.data_shape))}</p>"
            f"<p><strong>Where EchoWave helps:</strong> {escape(_clean(scenario.tsontology_role))}</p>"
            "<div class='docs-grid-2'>"
            f"<div><strong>Typical inputs</strong><ul class='panel-list'>{inputs}</ul></div>"
            f"<div><strong>What you can do</strong><ul class='panel-list'>{actions}</ul></div>"
            "</div>"
            f"<div><strong>Caveats</strong><ul class='panel-list'>{caveats}</ul></div>"
            "</div>"
        )
    body = "".join(cards)
    return _doc_shell(
        page_key="scenarios",
        title="Scenarios",
        lead="Use this page the way scikit-learn users use problem-oriented documentation: find your domain, then jump into the right entrypoint.",
        body=body,
    )


def project_ecosystem_html(*, version: str = PACKAGE_VERSION) -> str:
    eco = ecosystem_positioning(format="json")
    eco_rows = "\n".join(
        f"<tr><td><strong>{escape(entry['name'])}</strong></td><td>{escape(_clean(entry['family']))}</td><td>{escape(', '.join(entry['strongest_for'][:3]))}</td><td>{escape(_clean(entry['tsontology_relation']))}</td></tr>"
        for entry in eco["entries"]
    )
    cov = coverage_matrix(format="json")
    cov_rows = "\n".join(
        f"<tr><td>{escape(_clean(row['capability']))}</td><td>{escape(_clean(row['tsontology_role']))}</td><td>{escape(', '.join(row['best_companions']) if row['best_companions'] else '-')}</td><td>{escape(_clean(row['notes']))}</td></tr>"
        for row in cov["rows"]
    )
    body = f"""
    <div class='docs-card'>
      {_pill(ECOSYSTEM_HEADING, 'sun')}
      <table class='small-table'>
        <thead><tr><th>Package</th><th>Family</th><th>Strongest fit</th><th>How EchoWave fits</th></tr></thead>
        <tbody>{eco_rows}</tbody>
      </table>
    </div>
    <div class='docs-card'>
      {_pill('Capability coverage', 'blue')}
      <table class='small-table'>
        <thead><tr><th>Capability</th><th>Role</th><th>Companion packages</th><th>Notes</th></tr></thead>
        <tbody>{cov_rows}</tbody>
      </table>
    </div>
    """
    return _doc_shell(
        page_key="ecosystem",
        title="Ecosystem and Scope",
        lead="This page exists to keep the package honest. EchoWave should be easy to place next to sktime, tsfresh, DTAIDistance, STUMPY, and other neighboring tools.",
        body=body,
    )


def project_agents_html(*, version: str = PACKAGE_VERSION) -> str:
    body = f"""
    <div class='docs-card'>
      {_pill(AGENT_HEADING, 'sun')}
      <p><strong>EchoWave is agent-friendly because the outer surface is small and stable.</strong> The point is not to be a full orchestration platform. The point is to make the domain task cheap to route and easy to consume.</p>
      <pre><code>ts_profile({{data_ref, input_kind, timestamps_ref, domain, budget, audience}})
ts_compare({{left_ref, right_ref, left_timestamps_ref, right_timestamps_ref, mode, budget}})
ts_route({{task, available_inputs, has_reference}})</code></pre>
      <div class='meta-line'>
        <span class='meta-chip'><strong>Schema version</strong> {escape(TOOL_SCHEMA_VERSION)}</span>
        <span class='meta-chip'><strong>Surface</strong> compare-first</span>
      </div>
    </div>
    <div class='docs-grid-2'>
      <div class='docs-card'>
        {_pill('Stable envelope', 'blue')}
        <ul class='panel-list'>
          <li>schema_version</li>
          <li>tool</li>
          <li>ok</li>
          <li>confidence</li>
          <li>limitations</li>
          <li>evidence</li>
          <li>recommended_next_step</li>
          <li>next_actions</li>
        </ul>
      </div>
      <div class='docs-card'>
        {_pill('Why this matters', 'sun')}
        <ul class='panel-list'>
          <li>Agents do not need to scrape notebook prose.</li>
          <li>Routers can choose compare vs profile without guessing the whole package surface.</li>
          <li>Downstream apps can cache on compact, stable payloads.</li>
        </ul>
      </div>
    </div>
    """
    return _doc_shell(
        page_key="agents",
        title="Agent Tools",
        lead="A dedicated page for the function-calling and routing surface. This keeps agent material out of the homepage while still making it easy to discover.",
        body=body,
    )


def project_docs_pages(*, version: str = PACKAGE_VERSION) -> dict[str, str]:
    return {
        "guide/index.html": project_docs_home_html(version=version),
        "guide/getting-started.html": project_getting_started_html(version=version),
        "guide/tutorials.html": project_tutorials_html(version=version),
        "guide/api.html": project_api_reference_html(version=version),
        "guide/scenarios.html": project_scenarios_html(version=version),
        "guide/ecosystem.html": project_ecosystem_html(version=version),
        "guide/agents.html": project_agents_html(version=version),
    }


__all__ = [
    "project_docs_home_html",
    "project_getting_started_html",
    "project_tutorials_html",
    "project_api_reference_html",
    "project_scenarios_html",
    "project_ecosystem_html",
    "project_agents_html",
    "project_docs_pages",
]
