"""GitHub Pages-ready bundle helpers for EchoWave.

These helpers do not deploy anything by themselves. They generate a richer
static site bundle that can be published through GitHub Pages or any static
file host. The bundle now includes homepage, playground, flagship reports,
social cards, blog-style explainers, and a small manifest describing the demo
surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .copydeck import FLAGSHIP_DEMOS, PACKAGE_VERSION
from .datasets import starter_dataset
from .docs_site import project_docs_pages
from .homepage import project_homepage_html
from .launchpad import project_launchpad_html
from .playground import project_playground_html
from .profile import profile_dataset
from .similarity import compare_series, rolling_similarity
from .visuals import (
    axis_bar_svg,
    profile_html_report,
    profile_radar_svg,
    profile_social_card_svg,
    rolling_similarity_svg,
    series_overlay_svg,
    similarity_html_report,
    similarity_components_svg,
    similarity_social_card_svg,
)


def _blog_page(
    *,
    title: str,
    deck: str,
    report_href: str,
    social_href: str,
    notebook_hint: str,
    bullets: list[str],
    visuals: list[dict[str, str]],
    source_href: str,
) -> str:
    bullet_html = "".join(f"<li>{item}</li>" for item in bullets)
    visual_html = "".join(
        "<div class='visual-card'>"
        f"<div class='visual-label'>{item['label']}</div>"
        f"<div class='visual-frame'>{item['svg']}</div>"
        f"<p>{item['caption']}</p>"
        "</div>"
        for item in visuals
    )
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{title} - EchoWave demo story</title>
<style>
:root {{ --bg:#ffffff; --ink:#1F2937; --muted:#6B7280; --line:#E5E7EB; --panel:#ffffff; --panel-soft:#FAFAFA; --brand:#2F6BFF; --sun:#FFC83D; --shadow:0 1px 2px rgba(17,24,39,.04),0 14px 34px rgba(17,24,39,.08); --max:1024px; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); }}
.container {{ width:min(var(--max), calc(100vw - 28px)); margin:0 auto; padding:28px 0 42px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:22px 24px; box-shadow:var(--shadow); margin-bottom:18px; }}
.hero {{ display:grid; gap:16px; }}
.hero-grid {{ display:grid; grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr); gap:18px; align-items:start; }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--brand); font-size:.88rem; font-weight:700; margin-right:8px; }}
.pill.sun {{ background:#fff4c2; color:#a16207; }}
a {{ color:var(--brand); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
h1 {{ margin:0 0 10px; font-size:clamp(2rem,4vw,3rem); line-height:1.05; letter-spacing:-.04em; }} h2 {{ margin:0 0 10px; font-size:1.22rem; }} p.lead {{ color:var(--muted); font-size:1.05rem; }} ul {{ margin:0; padding-left:1.2rem; }}
.meta {{ display:grid; gap:12px; }}
.metric {{ border:1px solid var(--line); background:var(--panel-soft); border-radius:16px; padding:14px 16px; }}
.metric strong {{ display:block; font-size:.82rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-bottom:6px; }}
.metric span {{ font-size:1.6rem; font-weight:800; letter-spacing:-.03em; color:var(--ink); }}
.visual-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.visual-card {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow); }}
.visual-card p {{ color:var(--muted); margin:12px 0 0; }}
.visual-label {{ display:inline-flex; align-items:center; padding:6px 12px; border-radius:999px; background:#fff4c2; color:#a16207; font-size:.84rem; font-weight:800; margin-bottom:12px; }}
.visual-frame {{ border:1px solid var(--line); border-radius:16px; background:linear-gradient(180deg,#fffdfa 0%,#ffffff 100%); padding:10px; overflow:hidden; }}
.visual-frame svg {{ display:block; width:100%; height:auto; }}
.asset-list {{ display:grid; gap:10px; }}
.asset-list a {{ display:block; padding:12px 14px; border-radius:14px; border:1px solid var(--line); background:var(--panel-soft); font-weight:700; }}
@media (max-width: 860px) {{ .hero-grid, .visual-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class='container'>
  <div class='card hero'>
    <div><span class='pill sun'>flagship story</span><span class='pill'>EchoWave</span></div>
    <div class='hero-grid'>
      <div>
        <h1>{title}</h1>
        <p class='lead'>{deck}</p>
      </div>
      <div class='meta'>
        <div class='metric'><strong>Open assets</strong><span>Report + story + card</span></div>
        <div class='metric'><strong>Use case</strong><span>Explainable similarity demo</span></div>
      </div>
    </div>
  </div>
  <div class='card'>
    <h2>Why this demo travels</h2>
    <ul>{bullet_html}</ul>
  </div>
  <div class='visual-grid'>
    {visual_html}
  </div>
  <div class='card'>
    <h2>Open the assets</h2>
    <div class='asset-list'>
      <a href='../{report_href}'>Open the HTML report</a>
      <a href='../{social_href}'>Open the social card</a>
      <a href='{source_href}'>Open the Python source</a>
      <a href='#notebook'>{notebook_hint}</a>
    </div>
  </div>
  <div class='card' id='notebook'>
    <h2>Notebook hint</h2>
    <p>{notebook_hint}</p>
  </div>
</div>
</body>
</html>"""


def project_demo_manifest(*, version: str = PACKAGE_VERSION) -> dict[str, Any]:
    return {
        "version": version,
        "product_surface": "explainable time-series similarity for humans and agents",
        "pages": {
            "homepage": "index.html",
            "start_here": "start-here.html",
            "playground": "playground.html",
            "reports": {
                "weekly_website_traffic": "reports/weekly_website_traffic_report.html",
                "irregular_patient_vitals": "reports/irregular_patient_vitals_report.html",
                "github_breakout": "reports/github_breakout_similarity.html",
                "btc_vs_gold": "reports/btc_vs_gold_similarity.html",
                "energy_load_heatwave": "reports/energy_load_heatwave_report.html",
            },
            "blog": {
                "github_breakout": "blog/github_breakout_analogs.html",
                "btc_vs_gold": "blog/btc_vs_gold_under_shocks.html",
                "heatwave_grid_load": "blog/heatwave_vs_grid_load.html",
            },
        },
        "flagship_demos": list(FLAGSHIP_DEMOS),
        "notes": [
            "The Pages bundle is static and similarity-showcase-oriented.",
            "Use tsontology-demo locally when you need real computation on pasted arrays; echowave-demo is the new primary command.",
        ],
        "public_demo_url_hint": "https://<your-github-username>.github.io/echowave/",
        "external_evidence_status": "seeking public showcase submissions and third-party case studies",
    }


def project_pages_bundle(*, version: str = PACKAGE_VERSION) -> dict[str, str]:
    assets_root = Path(__file__).resolve().parents[2] / "assets"
    title_card = (assets_root / "echowave_title_card.svg").read_text(encoding="utf-8") if (assets_root / "echowave_title_card.svg").exists() else ""
    mark_svg = (assets_root / "echowave_mark.svg").read_text(encoding="utf-8") if (assets_root / "echowave_mark.svg").exists() else ""
    affiliation_svg = (assets_root / "bham_affiliation_badge.svg").read_text(encoding="utf-8") if (assets_root / "bham_affiliation_badge.svg").exists() else ""
    weekly = starter_dataset("weekly_website_traffic")
    weekly_profile = profile_dataset(weekly["values"], domain="traffic", timestamps=weekly["timestamps"], channel_names=weekly["channels"])

    clinical = starter_dataset("irregular_patient_vitals")
    clinical_profile = profile_dataset(clinical["values"], domain="clinical")

    github_case = starter_dataset("github_breakout_analogs")
    github_report = compare_series(github_case["target"], github_case["durable_breakout"], left_name="OpenClaw-style candidate", right_name="durable breakout analog")
    github_roll = rolling_similarity(github_case["target"], github_case["durable_breakout"], window=20, step=5)

    markets = starter_dataset("btc_gold_oil_shocks")
    market_report = compare_series(markets["btc"], markets["gold"], left_name="BTC", right_name="Gold")
    market_roll = rolling_similarity(markets["btc"], markets["gold"], window=24, step=6)

    energy = starter_dataset("energy_load_heatwave")
    energy_profile = profile_dataset(energy["values"], domain="energy", timestamps=energy["timestamps"], channel_names=energy["channels"])

    manifest = json.dumps(project_demo_manifest(version=version), indent=2)

    return {
        "index.html": project_homepage_html(version=version),
        "start-here.html": project_launchpad_html(version=version),
        "playground.html": project_playground_html(version=version),
        "404.html": project_launchpad_html(version=version),
        ".nojekyll": "",
        "manifest/demo_manifest.json": manifest,
        "site.webmanifest": json.dumps({"name": "EchoWave", "short_name": "EchoWave", "start_url": "/", "display": "standalone"}, indent=2),
        "social/echowave_title_card.svg": title_card,
        "social/echowave_mark.svg": mark_svg,
        "social/bham_affiliation_badge.svg": affiliation_svg,
        "reports/weekly_website_traffic_report.html": profile_html_report(weekly_profile, title="Weekly website traffic"),
        "reports/irregular_patient_vitals_report.html": profile_html_report(clinical_profile, title="Irregular patient vitals", audience="clinical"),
        "reports/github_breakout_similarity.html": similarity_html_report(github_report, title="GitHub breakout analogs", left_series=github_case["target"], right_series=github_case["durable_breakout"], rolling_windows=github_roll),
        "reports/btc_vs_gold_similarity.html": similarity_html_report(market_report, title="BTC vs Gold under shocks", left_series=markets["btc"], right_series=markets["gold"], rolling_windows=market_roll),
        "reports/energy_load_heatwave_report.html": profile_html_report(energy_profile, title="Heatwave vs grid load", audience="operations"),
        "social/weekly_website_traffic_card.svg": profile_social_card_svg(weekly_profile, title="Website traffic report"),
        "social/irregular_patient_vitals_card.svg": profile_social_card_svg(clinical_profile, title="Irregular patient vitals"),
        "social/github_breakout_card.svg": similarity_social_card_svg(github_report, title="GitHub breakout analogs"),
        "social/btc_vs_gold_card.svg": similarity_social_card_svg(market_report, title="BTC vs Gold under shocks"),
        "social/energy_load_card.svg": profile_social_card_svg(energy_profile, title="Heatwave vs grid load"),
        "blog/github_breakout_analogs.html": _blog_page(
            title="GitHub breakout analogs",
            deck="A showcase story for asking whether a new repository looks like a durable breakout or only a short viral spike.",
            report_href="reports/github_breakout_similarity.html",
            social_href="social/github_breakout_card.svg",
            notebook_hint="See the matching notebook in examples/notebooks/04_github_breakout_analogs.ipynb.",
            bullets=[
                "The story is easy to explain to both engineers and non-specialists.",
                "The report gives a readable similarity verdict before you reach for lower-level DTW tooling.",
                "The same asset pack works on GitHub, LinkedIn, X, and a project homepage.",
            ],
            visuals=[
                {
                    "label": "Series overlay",
                    "svg": series_overlay_svg(github_case["target"], github_case["durable_breakout"], left_label="candidate", right_label="durable analog"),
                    "caption": "The durable analog stays shape-aligned beyond the opening spike, so the story is visible before you read the verdict.",
                },
                {
                    "label": "Component breakdown",
                    "svg": similarity_components_svg(github_report),
                    "caption": "The similarity is not just one score. EchoWave shows which structural dimensions make the analogy convincing.",
                },
                {
                    "label": "Rolling similarity",
                    "svg": rolling_similarity_svg(github_roll),
                    "caption": "Windowed similarity is what separates a durable breakout from a short viral burst.",
                },
            ],
            source_href="https://github.com/ZipengWu365/EchoWave/blob/main/examples/gallery/plot_github_breakout_analogs.py",
        ),
        "blog/btc_vs_gold_under_shocks.html": _blog_page(
            title="BTC vs gold under shocks",
            deck="A macro narrative that turns rolling similarity and regime-aware comparison into a shareable story.",
            report_href="reports/btc_vs_gold_similarity.html",
            social_href="social/btc_vs_gold_card.svg",
            notebook_hint="See the matching notebook in examples/notebooks/05_btc_gold_oil_shocks.ipynb.",
            bullets=[
                "The asset is understandable even if the reader is not a time-series specialist.",
                "The report shows where similarity is stable versus shock-dependent.",
                "The demo demonstrates how EchoWave can explain a comparison without claiming to replace market modelling libraries.",
            ],
            visuals=[
                {
                    "label": "Series overlay",
                    "svg": series_overlay_svg(markets["btc"], markets["gold"], left_label="BTC", right_label="Gold"),
                    "caption": "The normalized overlay makes the shared structural windows visible despite the scale mismatch.",
                },
                {
                    "label": "Component breakdown",
                    "svg": similarity_components_svg(market_report),
                    "caption": "The verdict stays interpretable because the component view shows whether the analogy is shape-, trend-, or shock-driven.",
                },
                {
                    "label": "Rolling similarity",
                    "svg": rolling_similarity_svg(market_roll),
                    "caption": "The rolling panel shows when the safe-haven analogy actually strengthens instead of pretending the relationship is constant.",
                },
            ],
            source_href="https://github.com/ZipengWu365/EchoWave/blob/main/examples/gallery/plot_btc_gold_under_shocks.py",
        ),
        "blog/heatwave_vs_grid_load.html": _blog_page(
            title="Heatwave vs grid load",
            deck="An operations-friendly report story about drift, rhythm, and regime switching under extreme weather.",
            report_href="reports/energy_load_heatwave_report.html",
            social_href="social/energy_load_card.svg",
            notebook_hint="See the matching notebook in examples/notebooks/06_energy_load_heatwave.ipynb.",
            bullets=[
                "This demo travels well because the narrative is operational, not purely methodological.",
                "The report makes structural instability legible before transfer or forecasting decisions begin.",
                "It is a good example of how EchoWave can turn a dataset handoff into an artifact someone else can act on.",
            ],
            visuals=[
                {
                    "label": "Regional loads",
                    "svg": series_overlay_svg(energy["values"][:, 0], energy["values"][:, 1], left_label="north", right_label="south"),
                    "caption": "The two regional load curves still share rhythm, but the heatwave response is clearly not identical.",
                },
                {
                    "label": "Dataset radar",
                    "svg": profile_radar_svg(energy_profile),
                    "caption": "The profile radar adds context around drift, complexity, and coupling before any model handoff begins.",
                },
                {
                    "label": "Top axes",
                    "svg": axis_bar_svg(energy_profile),
                    "caption": "The axis view turns the dataset profile into something an operations or reliability team can scan quickly.",
                },
            ],
            source_href="https://github.com/ZipengWu365/EchoWave/blob/main/examples/gallery/plot_heatwave_grid_load.py",
        ),
        **project_docs_pages(version=version),
    }


def write_pages_bundle(path: str | Path, *, version: str = PACKAGE_VERSION) -> Path:
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    for rel, content in project_pages_bundle(version=version).items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


__all__ = [
    "project_demo_manifest",
    "project_pages_bundle",
    "write_pages_bundle",
]
