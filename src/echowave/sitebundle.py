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
from .homepage import project_homepage_html
from .launchpad import project_launchpad_html
from .playground import project_playground_html
from .profile import profile_dataset
from .similarity import compare_series, rolling_similarity
from .visuals import (
    profile_html_report,
    profile_social_card_svg,
    similarity_html_report,
    similarity_social_card_svg,
)


def _blog_page(*, title: str, deck: str, report_href: str, social_href: str, notebook_hint: str, bullets: list[str]) -> str:
    bullet_html = "".join(f"<li>{item}</li>" for item in bullets)
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{title} - EchoWave demo story</title>
<style>
:root {{ --bg:#f4f8fc; --ink:#102a43; --muted:#486581; --line:#d9e2ec; --panel:#ffffff; --brand:#0b6cff; --shadow:0 1px 2px rgba(16,42,67,.05),0 12px 24px rgba(16,42,67,.08); --max:980px; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); }}
.container {{ width:min(var(--max), calc(100vw - 28px)); margin:0 auto; padding:28px 0 42px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:22px 24px; box-shadow:var(--shadow); margin-bottom:18px; }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--brand); font-size:.88rem; font-weight:700; margin-right:8px; }}
a {{ color:var(--brand); text-decoration:none; }} a:hover {{ text-decoration:underline; }}
h1 {{ margin:0 0 10px; font-size:clamp(2rem,4vw,3rem); line-height:1.05; letter-spacing:-.04em; }} h2 {{ margin:0 0 10px; font-size:1.22rem; }} p.lead {{ color:var(--muted); font-size:1.05rem; }} ul {{ margin:0; padding-left:1.2rem; }}
</style>
</head>
<body>
<div class='container'>
  <div class='card'>
    <span class='pill'>flagship story</span><span class='pill'>EchoWave</span>
    <h1>{title}</h1>
    <p class='lead'>{deck}</p>
  </div>
  <div class='card'>
    <h2>Why this demo travels</h2>
    <ul>{bullet_html}</ul>
  </div>
  <div class='card'>
    <h2>Open the assets</h2>
    <ul>
      <li><a href='../{report_href}'>Open the HTML report</a></li>
      <li><a href='../{social_href}'>Open the social card</a></li>
      <li>{notebook_hint}</li>
    </ul>
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
        ),
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
