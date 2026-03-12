"""Docs-style pages for EchoWave.

These pages separate landing-page content from documentation content, closer
to a scikit-learn-style information architecture: a lightweight homepage and
dedicated tutorial / API / scenario pages with a persistent sidebar.
"""

from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path
from typing import Any, Iterable

import numpy as np

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
from .datasets import list_starter_datasets, starter_dataset
from .design_system import page_head
from .guide import API_ENTRIES, SCENARIOS
from .positioning import coverage_matrix, ecosystem_positioning
from .profile import profile_dataset
from .similarity import compare_series, rolling_similarity
from .visuals import (
    axis_bar_svg,
    profile_radar_svg,
    rolling_similarity_svg,
    series_overlay_svg,
    similarity_components_svg,
)

DOC_PAGES = (
    ("index", "Docs Home"),
    ("getting-started", "Getting Started"),
    ("tutorials", "Tutorials"),
    ("api", "API Reference"),
    ("scenarios", "Scenarios"),
    ("ecosystem", "Ecosystem"),
    ("agents", "Agent Tools"),
)

_EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples" / "gallery"


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


def _doc_shell(
    *,
    page_key: str,
    title: str,
    lead: str,
    body: str,
    extra_css: str = "",
    sidebar_sections: Iterable[str] = (),
    hero_html: str | None = None,
) -> str:
    sidebar = []
    for key, label in DOC_PAGES:
        href = "index.html" if key == "index" else f"{key}.html"
        active = " active" if key == page_key else ""
        sidebar.append(f"<a class='doc-link{active}' href='{href}'>{escape(label)}</a>")
    base_css = """
    .docs-wrap { display:grid; grid-template-columns: 240px minmax(0, 1fr); gap: 18px; padding: 24px 0 36px; }
    .docs-sidebar { position: sticky; top: 88px; align-self: start; display:grid; gap:14px; min-width: 0; }
    .sidebar-card { background: var(--surface-strong); border:1px solid var(--border); border-radius: var(--radius-md); padding: 16px; box-shadow: var(--shadow-sm); overflow: hidden; }
    .sidebar-title { margin:0 0 10px; font-size: 0.86rem; color: var(--text-600); font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
    .doc-link { display:block; padding: 10px 12px; border-radius: 12px; color: var(--text-600); font-weight: 600; word-break: break-word; }
    .doc-link:hover { background: rgba(47,107,255,0.06); color: var(--text-900); }
    .doc-link.active { background: rgba(255, 244, 194, 0.78); color: var(--text-900); border:1px solid rgba(255,200,61,0.38); }
    .docs-main { display:grid; gap: 24px; min-width: 0; }
    .docs-hero { display:grid; gap: 12px; }
    .docs-hero h1 { font-size: clamp(2.1rem, 4vw, 3.3rem); line-height: 1.02; }
    .docs-card { background: var(--surface-strong); border:1px solid var(--border); border-radius: var(--radius-md); padding: 20px; box-shadow: var(--shadow-sm); display:grid; gap: 12px; min-width: 0; overflow: hidden; }
    .docs-grid-2, .docs-grid-3 { display:grid; gap: 20px; }
    .docs-grid-2 { grid-template-columns: 1fr 1fr; }
    .docs-grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .meta-line { display:flex; flex-wrap:wrap; gap: 10px; min-width: 0; }
    .meta-chip { display:inline-flex; align-items:center; gap:6px; padding: 6px 10px; border-radius: 999px; background: var(--surface); border:1px solid var(--border); color: var(--text-600); font-size: 0.84rem; font-weight: 700; min-width: 0; }
    .meta-chip strong { color: var(--text-900); }
    .entry-stack { display:grid; gap: 16px; }
    .entry { border-top: 1px solid var(--border); padding-top: 16px; }
    .entry:first-child { border-top: 0; padding-top: 0; }
    .entry h3 { font-size: 1.1rem; }
    .inline-code { display: inline-block; max-width: 100%; overflow-x: auto; vertical-align: bottom; white-space: nowrap; font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; background: #fffef8; border:1px solid var(--border); padding: 2px 6px; border-radius: 8px; }
    .small-table { width:100%; border-collapse:collapse; display:block; overflow-x:auto; }
    .small-table th, .small-table td { padding: 11px 12px; text-align:left; border-bottom:1px solid var(--border); vertical-align: top; }
    .small-table th { background: #fffdf6; color: var(--text-600); font-size: 0.9rem; }
    .small-table tr:last-child td { border-bottom: 0; }
    .toc-note { font-size: 0.92rem; color: var(--text-600); }
    .example-card { align-content: start; }
    .example-preview { border: 1px solid var(--border); border-radius: 16px; background: linear-gradient(180deg, #fffdfa 0%, #ffffff 100%); padding: 12px; overflow: hidden; }
    .example-preview svg { display: block; width: 100%; height: auto; }
    .example-link-row { display:flex; flex-wrap:wrap; gap:10px; margin-top: 4px; }
    .example-figure-grid { display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:20px; }
    .example-figure-wide { grid-column: 1 / -1; }
    .asset-list { display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .asset-link { display:grid; gap:4px; padding: 14px 16px; border-radius: 14px; border:1px solid var(--border); background: var(--surface); color: var(--text-900); }
    .asset-link:hover { border-color: rgba(47,107,255,0.18); background: rgba(47,107,255,0.04); color: var(--text-900); }
    .asset-link strong { font-size: 0.96rem; }
    .asset-link span { color: var(--text-600); font-size: 0.88rem; }
    .gallery-section { display:grid; gap: 14px; }
    .gallery-section h2 { font-size: 1.18rem; }
    .gallery-grid { display:grid; gap: 16px; }
    .gallery-card { display:grid; grid-template-columns: 220px minmax(0, 1fr); gap: 18px; align-items: start; padding: 16px 18px; border:1px solid var(--border); border-radius: 18px; background: var(--surface-strong); box-shadow: var(--shadow-sm); }
    .gallery-thumb { display:block; border: 1px solid var(--border); border-radius: 16px; padding: 10px; background: linear-gradient(180deg, #fffdfa 0%, #ffffff 100%); overflow: hidden; }
    .gallery-thumb svg { display:block; width: 100%; height: auto; }
    .gallery-body { display:grid; gap: 8px; min-width: 0; }
    .gallery-body h3 { font-size: 1.2rem; line-height: 1.25; }
    .gallery-body p { margin: 0; }
    .gallery-links { display:flex; flex-wrap:wrap; gap: 12px; font-weight: 700; }
    .gallery-links a { color: var(--blue-700); }
    .gallery-links a:hover { text-decoration: underline; }
    .gallery-kicker { font-size: 0.8rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-600); }
    .example-page-intro { display:grid; gap: 16px; }
    .example-breadcrumb { font-size: 0.9rem; color: var(--text-600); }
    .example-head { display:grid; gap: 10px; }
    .example-head h1 { font-size: clamp(1.8rem, 3vw, 2.55rem); line-height: 1.08; }
    .example-summary-grid { display:grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; }
    .example-teaser { display:grid; gap: 14px; }
    .example-score { font-size: 2.5rem; line-height: 0.95; font-weight: 800; letter-spacing: -0.05em; color: var(--text-900); }
    .example-score-label { font-size: 0.95rem; color: var(--text-600); font-weight: 700; }
    .component-list { display:grid; gap: 10px; }
    .component-row { display:grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; align-items: center; }
    .component-row span { color: var(--text-600); }
    .component-track { grid-column: 1 / -1; height: 8px; border-radius: 999px; background: #f3f4f6; overflow: hidden; }
    .component-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--sun-500), #f1b62a); }
    @media (max-width: 1180px) {
      .docs-grid-3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .example-figure-grid, .asset-list { grid-template-columns: 1fr; }
    }
    @media (max-width: 980px) {
      .docs-wrap { grid-template-columns: 1fr; }
      .docs-sidebar { position: static; }
      .docs-grid-2, .docs-grid-3 { grid-template-columns: 1fr; }
      .example-figure-grid { grid-template-columns: 1fr; }
      .gallery-card, .example-summary-grid { grid-template-columns: 1fr; }
    }
    """
    return f"""<!doctype html>
<html lang='en'>
{page_head(f"{DISPLAY_NAME} docs - {title}", extra_css=base_css + extra_css)}
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
    {"".join(sidebar_sections)}
  </aside>
  <section class='docs-main'>
    {hero_html or f"<div class='docs-hero'><div class='eyebrow'>Documentation</div><h1>{escape(title)}</h1><p class='subhead'>{escape(lead)}</p></div>"}
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


def _repo_blob_href(relpath: str) -> str:
    normalized = relpath.replace("\\", "/").lstrip("/")
    return f"{PROJECT_REPOSITORY_URL}/blob/main/{normalized}"


def _load_example_source(filename: str) -> str:
    path = _EXAMPLES_DIR / filename
    if not path.exists():
        return "# example source unavailable\n"
    return path.read_text(encoding="utf-8")


def _asset_link(label: str, href: str, caption: str) -> str:
    return (
        f"<a class='asset-link' href='{escape(href)}'>"
        f"<strong>{escape(label)}</strong>"
        f"<span>{escape(caption)}</span>"
        "</a>"
    )


def _example_sidebar(entries: list[dict[str, Any]], active_href: str) -> str:
    links = []
    for entry in entries:
        active = " active" if entry["href"] == active_href else ""
        links.append(f"<a class='doc-link{active}' href='{entry['href']}'>{escape(entry['title'])}</a>")
    return (
        "<div class='sidebar-card'>"
        "<div class='sidebar-title'>Example gallery</div>"
        + "".join(links)
        + "</div>"
    )


def _example_report_href(entry: dict[str, Any]) -> str:
    return next(
        (
            asset["href"]
            for asset in entry["assets"]
            if asset["label"] in {"Standalone report", "Related report", "Clinical report"}
        ),
        "",
    )


def _example_source_href(entry: dict[str, Any]) -> str:
    return _repo_blob_href(f"examples/gallery/{entry['code_filename']}")


def _component_rows(entry: dict[str, Any], *, limit: int = 4) -> str:
    report = entry["report"]
    rows = []
    for label, value in sorted(report.component_scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]:
        rows.append(
            "<div class='component-row'>"
            f"<span>{escape(label.replace('_', ' '))}</span>"
            f"<strong>{float(value):0.2f}</strong>"
            f"<div class='component-track'><div class='component-fill' style='width:{max(0.0, min(100.0, float(value) * 100.0)):0.1f}%'></div></div>"
            "</div>"
        )
    return "".join(rows)


def _render_example_page(entry: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    report_href = _example_report_href(entry)
    figures_html = "".join(
        "<div class='docs-card"
        + (" example-figure-wide" if figure.get("wide") else "")
        + "'>"
        + _pill(figure["label"], figure.get("tone", "blue"))
        + f"<div class='example-preview'>{figure['svg']}</div>"
        + f"<p class='muted'>{escape(figure['caption'])}</p>"
        + "</div>"
        for figure in entry["figures"]
    )
    assets_html = "".join(
        _asset_link(asset["label"], asset["href"], asset["caption"])
        for asset in entry["assets"]
    )
    highlights = "".join(f"<li>{escape(item)}</li>" for item in entry["highlights"])
    hero_html = f"""
    <div class='example-page-intro'>
      <div class='example-breadcrumb'><a href='tutorials.html'>Examples</a> / {escape(entry['category'])}</div>
      <div class='example-head'>
        <div class='eyebrow'>{escape(entry['category'])}</div>
        <h1>{escape(entry['title'])}</h1>
        <p class='subhead'>{escape(entry['lead'])}</p>
      </div>
    </div>
    """
    body = f"""
    <div class='example-summary-grid'>
      <div class='docs-card example-teaser'>
        <div class='example-preview'>{entry['preview_svg']}</div>
        <div class='meta-line'>
          <span class='meta-chip'><strong>Mode</strong> {escape(entry['mode'])}</span>
          <span class='meta-chip'><strong>Headline</strong> {escape(entry['score_text'])}</span>
        </div>
        <p>{escape(entry['deck'])}</p>
        <div class='gallery-links'>
          <a href='{entry['href']}'>Permalink</a>
          {f"<a href='{report_href}'>Open report</a>" if report_href else ""}
          <a href='{_example_source_href(entry)}'>Source</a>
        </div>
        <ul class='panel-list'>{highlights}</ul>
      </div>
      <div class='docs-card'>
        {_pill('Similarity verdict', 'sun')}
        <div class='example-score'>{entry['report'].similarity_score:.2f}</div>
        <div class='example-score-label'>{escape(entry['report'].qualitative_label.title())} similarity overall</div>
        <p>{escape(entry['report'].interpretation)}</p>
        <div class='component-list'>{_component_rows(entry)}</div>
      </div>
    </div>
    <div class='example-figure-grid'>
      {figures_html}
    </div>
    <div class='docs-grid-2'>
      <div class='docs-card'>
        {_pill('Python source', 'blue')}
        <pre><code>{escape(entry['code'])}</code></pre>
      </div>
      <div class='docs-card'>
        {_pill('Open assets', 'sun')}
        <div class='asset-list'>{assets_html}</div>
      </div>
    </div>
    """
    return _doc_shell(
        page_key="tutorials",
        title=entry["title"],
        lead=entry["lead"],
        body=body,
        sidebar_sections=(_example_sidebar(entries, entry["href"]),),
        hero_html=hero_html,
    )


def _tutorial_examples() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    t = np.linspace(0, 8 * np.pi, 128)
    candidate = np.sin(t) + 0.08 * np.cos(t / 2.0)
    reference = np.sin(t + 0.22) + 0.05 * np.cos(t / 2.0)
    quick_report = compare_series(candidate, reference, left_name="candidate curve", right_name="reference analog")
    quick_roll = rolling_similarity(candidate, reference, window=24, step=6)
    entries.append(
        {
            "href": "example-two-curves-similarity.html",
            "slug": "two_curves",
            "title": "Two curves, one similarity verdict",
            "lead": "A compact first example: a phase-shifted analog, one similarity verdict, and a rolling view of where the match stays stable.",
            "deck": "This is the shortest path from raw arrays to an interpretable similarity result. The two curves are not identical, but the structural match is strong enough that EchoWave explains the agreement instead of dumping one number.",
            "category": "Beginner example",
            "tone": "sun",
            "mode": "compare_series",
            "score_text": f"{quick_report.similarity_score:.2f} overall similarity",
            "summary": quick_report.to_summary_card_markdown(),
            "report": quick_report,
            "code_filename": "plot_two_curves_similarity.py",
            "code": _load_example_source("plot_two_curves_similarity.py"),
            "highlights": [
                f"Overall similarity lands at {quick_report.similarity_score:.2f} ({quick_report.qualitative_label}).",
                "Shape, DTW, and trend agreement stay high even with a mild phase shift.",
                "Rolling similarity remains stable, so the match is structural rather than a single-window accident.",
            ],
            "figures": [
                {
                    "label": "Series overlay",
                    "tone": "blue",
                    "svg": series_overlay_svg(candidate, reference, left_label="candidate", right_label="reference"),
                    "caption": "EchoWave rescales the two curves so the shared shape is legible before you inspect components.",
                },
                {
                    "label": "Component breakdown",
                    "tone": "sun",
                    "svg": similarity_components_svg(quick_report),
                    "caption": "The component panel shows why the verdict is high instead of hiding the reasoning behind one score.",
                },
                {
                    "label": "Rolling similarity",
                    "tone": "blue",
                    "svg": rolling_similarity_svg(quick_roll),
                    "caption": "Windowed similarity confirms that the analog remains strong across the sequence.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_two_curves_similarity.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/10_two_curves_similarity_verdict.ipynb"),
                    "caption": "The matching notebook version.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/sine_vs_noise.csv"),
                    "caption": "A related low-similarity contrast case for the same workflow.",
                },
            ],
            "preview_svg": series_overlay_svg(candidate, reference, width=520, height=200, left_label="candidate", right_label="reference"),
        }
    )

    traffic = starter_dataset("weekly_website_traffic")
    sessions = traffic["values"][:, 0]
    signups = traffic["values"][:, 1]
    traffic_report = compare_series(sessions, signups, left_name="sessions", right_name="signups")
    traffic_roll = rolling_similarity(sessions, signups, window=21, step=7)
    entries.append(
        {
            "href": "example-weekly-traffic-signals.html",
            "slug": "weekly_traffic",
            "title": "Weekly traffic signals move together, but not identically",
            "lead": "A product-style example showing two metrics with shared weekly cadence, but enough lag and funnel drift that the match stays only moderate.",
            "deck": "Sessions and signups are related, but they are not a scaled copy of one another. Conversion lag, saturation after launch bursts, and weekday bias all reduce the similarity score to something closer to a realistic product relationship.",
            "category": "Beginner example",
            "tone": "blue",
            "mode": "compare_series",
            "score_text": f"{traffic_report.similarity_score:.2f} overall similarity",
            "summary": traffic_report.to_summary_card_markdown(),
            "report": traffic_report,
            "code_filename": "plot_weekly_traffic_similarity.py",
            "code": _load_example_source("plot_weekly_traffic_similarity.py"),
            "highlights": [
                f"The overall similarity is {traffic_report.similarity_score:.2f}, so the metrics are related but clearly not interchangeable.",
                "Launch-week divergence and conversion lag lower the pointwise agreement instead of disappearing into one average score.",
                "This is closer to a realistic funnel relationship than a synthetic scaled-copy demo.",
            ],
            "figures": [
                {
                    "label": "Sessions vs signups",
                    "tone": "blue",
                    "svg": series_overlay_svg(sessions, signups, left_label="sessions", right_label="signups"),
                    "caption": "The shape match is visible at a glance, but the burst response is not perfectly aligned.",
                },
                {
                    "label": "Component breakdown",
                    "tone": "sun",
                    "svg": similarity_components_svg(traffic_report),
                    "caption": "EchoWave explains which parts of the relationship are strong and which are only moderate.",
                },
                {
                    "label": "Rolling similarity",
                    "tone": "blue",
                    "svg": rolling_similarity_svg(traffic_roll),
                    "caption": "Windowed similarity shows where the funnel stays coupled and where campaign bursts change the relationship.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_weekly_traffic_similarity.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/02_weekly_website_traffic.ipynb"),
                    "caption": "The longer notebook walkthrough.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/weekly_website_traffic.csv"),
                    "caption": "The raw traffic demo data used here.",
                },
                {
                    "label": "Related report",
                    "href": "../reports/weekly_website_traffic_report.html",
                    "caption": "The dataset-level report for the same traffic data.",
                },
            ],
            "preview_svg": series_overlay_svg(sessions, signups, width=520, height=200, left_label="sessions", right_label="signups"),
        }
    )

    clinical = starter_dataset("irregular_patient_vitals")
    cohort = clinical["values"]
    subjects = list(cohort.subjects)
    left_subject = subjects[0]
    right_subject = subjects[1]
    left_hr = left_subject.values[0]
    right_hr = right_subject.values[0]
    left_times = left_subject.timestamps[0]
    right_times = right_subject.timestamps[0]
    clinical_report = compare_series(
        left_hr,
        right_hr,
        left_timestamps=left_times,
        right_timestamps=right_times,
        left_name="patient p1 heart rate",
        right_name="patient p2 heart rate",
    )
    clinical_profile = profile_dataset(cohort, domain="clinical")
    entries.append(
        {
            "href": "example-irregular-patient-similarity.html",
            "slug": "irregular_patients",
            "title": "Irregular patient trajectories still deserve a similarity verdict",
            "lead": "A clinical example that uses explicit timestamps so irregular sampling changes the verdict instead of being ignored.",
            "deck": "Clinical monitoring is rarely dense and tidy. This page compares two heart-rate trajectories with explicit timestamps, then uses a cohort profile to show why irregularity has to stay part of the story.",
            "category": "Cross-disciplinary example",
            "tone": "sun",
            "mode": "compare_series + profile_dataset",
            "score_text": f"{clinical_report.similarity_score:.2f} overall similarity",
            "summary": clinical_report.to_summary_card_markdown(),
            "report": clinical_report,
            "code_filename": "plot_irregular_patient_similarity.py",
            "code": _load_example_source("plot_irregular_patient_similarity.py"),
            "highlights": [
                f"Even with irregular timestamps, EchoWave still resolves a {clinical_report.qualitative_label} similarity judgment.",
                "The comparison respects timing instead of forcing naive equal-interval alignment.",
                "The cohort profile adds structural context so a clinician or collaborator can see why this dataset is hard.",
            ],
            "figures": [
                {
                    "label": "Heart-rate overlay",
                    "tone": "blue",
                    "svg": series_overlay_svg(left_hr, right_hr, left_label="patient p1", right_label="patient p2"),
                    "caption": "The raw shapes look similar, but the timestamps are not evenly spaced, so EchoWave resamples them before comparison.",
                },
                {
                    "label": "Similarity components",
                    "tone": "sun",
                    "svg": similarity_components_svg(clinical_report),
                    "caption": "The component view keeps the similarity verdict interpretable even in irregular monitoring data.",
                },
                {
                    "label": "Clinical cohort axes",
                    "tone": "blue",
                    "svg": axis_bar_svg(clinical_profile),
                    "caption": "The cohort profile shows that irregularity and heterogeneity are part of the background, not a preprocessing afterthought.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_irregular_patient_similarity.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/03_irregular_patient_vitals.ipynb"),
                    "caption": "The notebook walkthrough for the clinical cohort.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/irregular_patient_vitals.csv"),
                    "caption": "The raw irregular monitoring table.",
                },
                {
                    "label": "Clinical report",
                    "href": "../reports/irregular_patient_vitals_report.html",
                    "caption": "The dataset-level report for this cohort.",
                },
            ],
            "preview_svg": similarity_components_svg(clinical_report, width=520, height=220),
        }
    )

    github_case = starter_dataset("github_breakout_analogs")
    target = github_case["target"]
    durable = github_case["durable_breakout"]
    short_hype = github_case["short_hype"]
    github_report = compare_series(target, durable, left_name="OpenClaw-style candidate", right_name="durable breakout analog")
    github_hype = compare_series(target, short_hype, left_name="OpenClaw-style candidate", right_name="short-hype analog")
    github_roll = rolling_similarity(target, durable, window=20, step=5)
    entries.append(
        {
            "href": "example-github-breakout-analogs.html",
            "slug": "github_breakout",
            "title": "GitHub breakout analogs",
            "lead": "A flagship demo for asking whether a new repository resembles a durable breakout or only a short-lived spike.",
            "deck": "This example is built to travel. It compares a target repository curve against two analog families and shows why the durable analog is the more convincing match.",
            "category": "Flagship demo",
            "tone": "blue",
            "mode": "compare_series + rolling_similarity",
            "score_text": f"{github_report.similarity_score:.2f} durable analog score",
            "summary": github_report.to_summary_card_markdown(),
            "report": github_report,
            "code_filename": "plot_github_breakout_analogs.py",
            "code": _load_example_source("plot_github_breakout_analogs.py"),
            "highlights": [
                f"The durable-breakout analog scores {github_report.similarity_score:.2f}, versus {github_hype.similarity_score:.2f} for the short-hype analog.",
                "Rolling similarity is what makes the story credible: the match remains strong after the initial spike.",
                "This is the clearest product-style demo in the package because anyone can read the narrative.",
            ],
            "figures": [
                {
                    "label": "Target vs durable analog",
                    "tone": "blue",
                    "svg": series_overlay_svg(target, durable, left_label="candidate", right_label="durable analog"),
                    "caption": "The target and durable analog stay shape-aligned beyond the launch spike.",
                },
                {
                    "label": "Component breakdown",
                    "tone": "sun",
                    "svg": similarity_components_svg(github_report),
                    "caption": "The similarity verdict is backed by multiple components instead of a single point metric.",
                },
                {
                    "label": "Rolling similarity",
                    "tone": "blue",
                    "svg": rolling_similarity_svg(github_roll),
                    "caption": "Windowed similarity is what separates a durable analog from a short-lived hype curve.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_github_breakout_analogs.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/04_github_breakout_analogs.ipynb"),
                    "caption": "The full notebook walkthrough.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/github_breakout_analogs.csv"),
                    "caption": "The starter stars-over-time data.",
                },
                {
                    "label": "Standalone report",
                    "href": "../reports/github_breakout_similarity.html",
                    "caption": "Open the full HTML similarity report.",
                },
                {
                    "label": "Story page",
                    "href": "../blog/github_breakout_analogs.html",
                    "caption": "The blog-style explainer for this demo.",
                },
                {
                    "label": "Social card",
                    "href": "../social/github_breakout_card.svg",
                    "caption": "The shareable card for the same result.",
                },
            ],
            "preview_svg": similarity_components_svg(github_report, width=520, height=220),
        }
    )

    markets = starter_dataset("btc_gold_oil_shocks")
    btc = markets["btc"]
    gold = markets["gold"]
    oil = markets["oil"]
    btc_gold = compare_series(btc, gold, left_name="BTC", right_name="Gold")
    btc_oil = compare_series(btc, oil, left_name="BTC", right_name="Oil")
    btc_roll = rolling_similarity(btc, gold, window=24, step=6)
    entries.append(
        {
            "href": "example-btc-gold-under-shocks.html",
            "slug": "btc_gold",
            "title": "BTC vs gold under shocks",
            "lead": "A macro demo showing how rolling similarity turns a market narrative into something inspectable and reproducible.",
            "deck": "This page compares BTC to gold and oil, then uses a rolling view to show whether the similarity is stable or only shock-dependent. It is exactly the kind of cross-disciplinary story that makes the package more than a pure method artifact.",
            "category": "Flagship demo",
            "tone": "sun",
            "mode": "compare_series + rolling_similarity",
            "score_text": f"{btc_gold.similarity_score:.2f} BTC-vs-gold score",
            "summary": btc_gold.to_summary_card_markdown(),
            "report": btc_gold,
            "code_filename": "plot_btc_gold_under_shocks.py",
            "code": _load_example_source("plot_btc_gold_under_shocks.py"),
            "highlights": [
                f"BTC-vs-gold scores {btc_gold.similarity_score:.2f}, while BTC-vs-oil scores {btc_oil.similarity_score:.2f}.",
                "The rolling curve shows when the analogy strengthens instead of pretending the market relationship is constant.",
                "This is a strong external-facing demo because the story is intuitive even for non-specialists.",
            ],
            "figures": [
                {
                    "label": "BTC vs gold",
                    "tone": "blue",
                    "svg": series_overlay_svg(btc, gold, left_label="BTC", right_label="Gold"),
                    "caption": "The raw paths diverge in scale, but EchoWave still compares the shared structure after normalization.",
                },
                {
                    "label": "Component breakdown",
                    "tone": "sun",
                    "svg": similarity_components_svg(btc_gold),
                    "caption": "The component view reveals whether the relationship is shape-, trend-, or rhythm-driven.",
                },
                {
                    "label": "Rolling similarity",
                    "tone": "blue",
                    "svg": rolling_similarity_svg(btc_roll),
                    "caption": "Windowed similarity shows whether the safe-haven analogy holds steadily or only during shocks.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_btc_gold_under_shocks.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/05_btc_gold_oil_shocks.ipynb"),
                    "caption": "The full notebook walkthrough.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/btc_gold_oil_shocks.csv"),
                    "caption": "The starter markets dataset.",
                },
                {
                    "label": "Standalone report",
                    "href": "../reports/btc_vs_gold_similarity.html",
                    "caption": "Open the full HTML similarity report.",
                },
                {
                    "label": "Story page",
                    "href": "../blog/btc_vs_gold_under_shocks.html",
                    "caption": "The blog-style explainer for this demo.",
                },
                {
                    "label": "Social card",
                    "href": "../social/btc_vs_gold_card.svg",
                    "caption": "The shareable card for the same result.",
                },
            ],
            "preview_svg": similarity_components_svg(btc_gold, width=520, height=220),
        }
    )

    energy = starter_dataset("energy_load_heatwave")
    load_north = energy["values"][:, 0]
    load_south = energy["values"][:, 1]
    energy_report = compare_series(load_north, load_south, left_name="north grid load", right_name="south grid load")
    energy_profile = profile_dataset(energy["values"], domain="energy", timestamps=energy["timestamps"], channel_names=energy["channels"])
    entries.append(
        {
            "href": "example-heatwave-grid-load.html",
            "slug": "heatwave_grid_load",
            "title": "Heatwave vs grid load",
            "lead": "An operations-oriented example showing how two regional load curves stay similar while the broader dataset drifts under heat stress.",
            "deck": "This example compares north and south load trajectories, then uses a multivariate profile to show why heatwave conditions change the structural context around the comparison.",
            "category": "Flagship demo",
            "tone": "blue",
            "mode": "compare_series + profile_dataset",
            "score_text": f"{energy_report.similarity_score:.2f} north-vs-south score",
            "summary": energy_report.to_summary_card_markdown(),
            "report": energy_report,
            "code_filename": "plot_heatwave_grid_load.py",
            "code": _load_example_source("plot_heatwave_grid_load.py"),
            "highlights": [
                f"Regional loads still score {energy_report.similarity_score:.2f} overall, so they remain comparable even under stress.",
                "The supporting dataset profile shows that temperature and regime drift change how that comparison should be interpreted.",
                "This is a good example of EchoWave working as an operations handoff artifact instead of only a research toy.",
            ],
            "figures": [
                {
                    "label": "North vs south load",
                    "tone": "blue",
                    "svg": series_overlay_svg(load_north, load_south, left_label="north", right_label="south"),
                    "caption": "Regional load curves share rhythm, but their response to heat stress is not identical.",
                },
                {
                    "label": "Similarity components",
                    "tone": "sun",
                    "svg": similarity_components_svg(energy_report),
                    "caption": "The component breakdown shows where the two load curves still agree and where stress changes the picture.",
                },
                {
                    "label": "Dataset structure",
                    "tone": "blue",
                    "svg": profile_radar_svg(energy_profile),
                    "caption": "The full dataset profile reveals the broader structural context behind the series comparison.",
                    "wide": True,
                },
            ],
            "assets": [
                {
                    "label": "Python source",
                    "href": _repo_blob_href("examples/gallery/plot_heatwave_grid_load.py"),
                    "caption": "The exact script used for this example.",
                },
                {
                    "label": "Notebook",
                    "href": _repo_blob_href("examples/notebooks/06_energy_load_heatwave.ipynb"),
                    "caption": "The full notebook walkthrough.",
                },
                {
                    "label": "Starter CSV",
                    "href": _repo_blob_href("examples/data/energy_load_heatwave.csv"),
                    "caption": "The starter energy dataset.",
                },
                {
                    "label": "Standalone report",
                    "href": "../reports/energy_load_heatwave_report.html",
                    "caption": "Open the full HTML report.",
                },
                {
                    "label": "Story page",
                    "href": "../blog/heatwave_vs_grid_load.html",
                    "caption": "The blog-style explainer for this demo.",
                },
                {
                    "label": "Social card",
                    "href": "../social/energy_load_card.svg",
                    "caption": "The shareable card for the same result.",
                },
            ],
            "preview_svg": axis_bar_svg(energy_profile, width=520, height=220),
        }
    )

    for entry in entries:
        entry["page_html"] = _render_example_page(entry, entries)
    return entries


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
    examples = _tutorial_examples()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in examples:
        grouped[entry["category"]].append(entry)

    group_order = [
        ("Beginner example", "Short, low-friction walkthroughs that make the package legible in a few minutes."),
        ("Cross-disciplinary example", "Examples where timestamps, cohorts, or domain structure matter enough to change the similarity story."),
        ("Flagship demo", "Examples built to travel in talks, README sections, social posts, and benchmark discussions."),
    ]
    sections = []
    for category, blurb in group_order:
        group_entries = grouped.get(category, [])
        if not group_entries:
            continue
        cards = []
        for entry in group_entries:
            report_href = _example_report_href(entry)
            cards.append(
                "<article class='gallery-card'>"
                f"<a class='gallery-thumb' href='{entry['href']}'>{entry['preview_svg']}</a>"
                "<div class='gallery-body'>"
                f"<div class='gallery-kicker'>{escape(category)}</div>"
                f"<h3><a href='{entry['href']}'>{escape(entry['title'])}</a></h3>"
                f"<p>{escape(entry['lead'])}</p>"
                f"<div class='meta-line'><span class='meta-chip'><strong>Mode</strong> {escape(entry['mode'])}</span><span class='meta-chip'><strong>Verdict</strong> {escape(entry['score_text'])}</span></div>"
                "<div class='gallery-links'>"
                f"<a href='{entry['href']}'>Open example</a>"
                + (f"<a href='{report_href}'>Open report</a>" if report_href else "")
                + f"<a href='{_example_source_href(entry)}'>View source</a>"
                + "</div>"
                "</div>"
                "</article>"
            )
        sections.append(
            "<section class='gallery-section'>"
            f"<div><h2>{escape(category)}s</h2><p class='muted'>{escape(blurb)}</p></div>"
            f"<div class='gallery-grid'>{''.join(cards)}</div>"
            "</section>"
        )
    rows = "\n".join(
        f"<tr><td><strong>{escape(item['title'])}</strong><br><span class='muted'>{escape(item['name'])}</span></td><td>{escape(item['domain'])}</td><td>{escape(item['kind'])}</td><td>{escape(item['why'])}</td></tr>"
        for item in list_starter_datasets()
    )
    hero_html = """
    <div class='example-page-intro'>
      <div class='example-head'>
        <div class='eyebrow'>Examples gallery</div>
        <h1>Tutorials and runnable examples</h1>
        <p class='subhead'>A scikit-learn-style example index: compact summaries first, then dedicated pages with figures, source code, and downloadable assets.</p>
      </div>
    </div>
    """
    body = f"""
    <div class='docs-card'>
      {_pill('Tutorial map', 'sun')}
      <p>This page is now a real example gallery, not a placeholder card deck. Every entry below links to a dedicated page generated from an actual EchoWave run, with visual outputs, runnable source code, and links to reports, notebooks, or social assets where they exist.</p>
    </div>
    {"".join(sections)}
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
        sidebar_sections=(_example_sidebar(examples, ""),),
        hero_html=hero_html,
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
    examples = _tutorial_examples()
    pages = {
        "guide/index.html": project_docs_home_html(version=version),
        "guide/getting-started.html": project_getting_started_html(version=version),
        "guide/tutorials.html": project_tutorials_html(version=version),
        "guide/api.html": project_api_reference_html(version=version),
        "guide/scenarios.html": project_scenarios_html(version=version),
        "guide/ecosystem.html": project_ecosystem_html(version=version),
        "guide/agents.html": project_agents_html(version=version),
    }
    for entry in examples:
        pages[f"guide/{entry['href']}"] = entry["page_html"]
    return pages


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
