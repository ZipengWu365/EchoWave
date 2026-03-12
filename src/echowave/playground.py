"""Static GitHub-Pages-friendly playground for EchoWave starter cases."""

from __future__ import annotations

import json
from html import escape

from .copydeck import HEADLINE, PACKAGE_NAME, PACKAGE_VERSION, PLAYGROUND_HEADING
from .datasets import starter_dataset
from .product import explain_dataset, explain_similarity
from .profile import profile_dataset
from .similarity import compare_series
from .visuals import (
    profile_html_report,
    profile_radar_svg,
    profile_social_card_svg,
    similarity_html_report,
    similarity_social_card_svg,
)


def _build_cases() -> dict[str, dict[str, str]]:
    weekly = starter_dataset("weekly_website_traffic")
    weekly_profile = profile_dataset(weekly["values"], domain="traffic", timestamps=weekly["timestamps"], channel_names=weekly["channels"])

    clinical = starter_dataset("irregular_patient_vitals")
    clinical_profile = profile_dataset(clinical["values"], domain="clinical")

    wearable = starter_dataset("wearable_recovery_cohort")
    wearable_profile = profile_dataset(wearable["values"], domain="wearable", timestamps=wearable["timestamps"], channel_names=wearable["channels"])

    energy = starter_dataset("energy_load_heatwave")
    energy_profile = profile_dataset(energy["values"], domain="energy", timestamps=energy["timestamps"], channel_names=energy["channels"])

    github_case = starter_dataset("github_breakout_analogs")
    github_similarity = compare_series(
        github_case["target"],
        github_case["durable_breakout"],
        left_name="OpenClaw-style candidate",
        right_name="durable breakout analog",
    )

    market_case = starter_dataset("btc_gold_oil_shocks")
    market_similarity = compare_series(
        market_case["btc"],
        market_case["gold"],
        left_name="BTC",
        right_name="Gold",
    )

    return {
        "weekly_website_traffic": {
            "title": "Weekly website traffic",
            "kind": "profile",
            "why": "Product-style rhythm, trend, and launch bursts.",
            "summary": explain_dataset(weekly["values"], domain="traffic"),
            "html": profile_html_report(weekly_profile, audience="general", title="Weekly website traffic"),
            "visual": profile_radar_svg(weekly_profile, width=320, height=320),
            "social": profile_social_card_svg(weekly_profile, title="Website traffic report"),
            "command": "python -c \"from echowave import starter_dataset, profile_dataset; case=starter_dataset('weekly_website_traffic'); print(profile_dataset(case['values'], domain='traffic').to_summary_card_markdown())\"",
        },
        "irregular_patient_vitals": {
            "title": "Irregular patient vitals",
            "kind": "profile",
            "why": "Show why timestamps and channel asynchrony matter.",
            "summary": explain_dataset(clinical["values"], domain="clinical"),
            "html": profile_html_report(clinical_profile, audience="clinical", title="Irregular patient vitals"),
            "visual": profile_radar_svg(clinical_profile, width=320, height=320),
            "social": profile_social_card_svg(clinical_profile, title="Irregular patient vitals"),
            "command": "python -c \"from echowave import starter_dataset, profile_dataset; case=starter_dataset('irregular_patient_vitals'); print(profile_dataset(case['values'], domain='clinical').to_summary_card_markdown())\"",
        },
        "wearable_recovery_cohort": {
            "title": "Wearable recovery cohort",
            "kind": "profile",
            "why": "Longitudinal cohort demo for adherence and heterogeneity.",
            "summary": explain_dataset(wearable["values"], domain="wearable"),
            "html": profile_html_report(wearable_profile, audience="general", title="Wearable recovery cohort"),
            "visual": profile_radar_svg(wearable_profile, width=320, height=320),
            "social": profile_social_card_svg(wearable_profile, title="Wearable recovery report"),
            "command": "python -c \"from echowave import starter_dataset, profile_dataset; case=starter_dataset('wearable_recovery_cohort'); print(profile_dataset(case['values'], domain='wearable').to_summary_card_markdown())\"",
        },
        "energy_load_heatwave": {
            "title": "Heatwave vs grid load",
            "kind": "profile",
            "why": "Grid-shift story with drift and rhythm.",
            "summary": explain_dataset(energy["values"], domain="energy"),
            "html": profile_html_report(energy_profile, audience="operations", title="Heatwave vs grid load"),
            "visual": profile_radar_svg(energy_profile, width=320, height=320),
            "social": profile_social_card_svg(energy_profile, title="Heatwave vs grid load"),
            "command": "python -c \"from echowave import starter_dataset, profile_dataset; case=starter_dataset('energy_load_heatwave'); print(profile_dataset(case['values'], domain='energy').to_summary_card_markdown())\"",
        },
        "openclaw_breakout_analogs": {
            "title": "OpenClaw-style GitHub breakout analogs",
            "kind": "similarity",
            "why": "Ask whether a new repo looks durable or just briefly viral.",
            "summary": explain_similarity(github_case["target"], github_case["durable_breakout"], left_name="OpenClaw-style candidate", right_name="durable breakout analog"),
            "html": similarity_html_report(github_similarity, left_series=github_case["target"], right_series=github_case["durable_breakout"], title="OpenClaw-style GitHub breakout analogs"),
            "visual": github_similarity.to_summary_card_markdown(),
            "social": similarity_social_card_svg(github_similarity, title="GitHub breakout analogs"),
            "command": "python -c \"from echowave import starter_dataset, explain_similarity; case=starter_dataset('github_breakout_analogs'); print(explain_similarity(case['target'], case['durable_breakout'], left_name='candidate', right_name='durable'))\"",
        },
        "btc_gold_oil_shocks": {
            "title": "BTC vs gold under shocks",
            "kind": "similarity",
            "why": "Macro-regime similarity story for a broad audience.",
            "summary": explain_similarity(market_case["btc"], market_case["gold"], left_name="BTC", right_name="Gold"),
            "html": similarity_html_report(market_similarity, left_series=market_case["btc"], right_series=market_case["gold"], title="BTC vs gold under shocks"),
            "visual": market_similarity.to_summary_card_markdown(),
            "social": similarity_social_card_svg(market_similarity, title="BTC vs Gold under shocks"),
            "command": "python -c \"from echowave import starter_dataset, explain_similarity; case=starter_dataset('btc_gold_oil_shocks'); print(explain_similarity(case['btc'], case['gold'], left_name='BTC', right_name='Gold'))\"",
        },
    }


def project_playground_html(*, version: str = PACKAGE_VERSION) -> str:
    cases = _build_cases()
    first_key = next(iter(cases))
    first = cases[first_key]
    case_options = "\n".join(
        f"<option value='{escape(key)}'>{escape(value['title'])}</option>" for key, value in cases.items()
    )
    cases_json = json.dumps(cases)
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>EchoWave playground</title>
<style>
:root {{ --bg:#f4f7fb; --ink:#102a43; --muted:#486581; --line:#d9e2ec; --blue:#0b6cff; --shadow:0 1px 2px rgba(16,42,67,.05),0 12px 24px rgba(16,42,67,.08); }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:var(--bg); color:var(--ink); line-height:1.6; }}
.main {{ max-width:1280px; margin:0 auto; padding:28px 18px 36px; }} .hero {{ display:grid; grid-template-columns:1.05fr .95fr; gap:20px; align-items:start; }} .card {{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:20px 22px; box-shadow:var(--shadow); }} h1 {{ margin:0 0 6px; font-size:2rem; letter-spacing:-.03em; }} h2 {{ margin:0 0 8px; font-size:1.25rem; }} .lead {{ color:var(--muted); margin:8px 0 0; }} .grid {{ display:grid; grid-template-columns:.8fr 1.2fr; gap:20px; margin-top:20px; }} .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px; }} select {{ width:100%; padding:10px 12px; border:1px solid var(--line); border-radius:10px; font:inherit; }} pre {{ margin:0; padding:14px 16px; background:#f7fafc; border:1px solid var(--line); border-radius:12px; overflow:auto; font-size:.9rem; white-space:pre-wrap; word-break:break-word; }} iframe {{ width:100%; min-height:700px; border:1px solid var(--line); border-radius:14px; background:#fff; }} .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--blue); font-size:.88rem; font-weight:600; margin-right:8px; }} .muted {{ color:var(--muted); }} .toolbar {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }} .toolbar a {{ display:inline-flex; padding:8px 12px; border-radius:10px; border:1px solid var(--line); background:#fff; color:var(--ink); text-decoration:none; }}
@media (max-width: 960px) {{ .hero,.grid,.grid2 {{ grid-template-columns:1fr; }} iframe {{ min-height:520px; }} }}
</style>
</head>
<body>
<div class='main'>
  <section class='hero'>
    <div class='card'>
      <span class='pill'>Live demo / playground</span><span class='pill'>Version {escape(version)}</span>
      <h1>{escape(PLAYGROUND_HEADING)}</h1>
      <p class='lead'>{escape(HEADLINE)} This page is designed for GitHub Pages or local preview. It lets a visitor switch between starter cases and inspect the report surface without running Python first.</p>
      <div class='toolbar'>
        <a href='start-here.html'>Start here</a>
        <a href='index.html'>Back to homepage</a>
        <a href='#report-frame'>Jump to report</a>
      </div>
    </div>
    <div class='card'>
      <h2>Start with a case</h2>
      <select id='case-select'>{case_options}</select>
      <p id='case-why' class='lead'>{escape(first['why'])}</p>
      <div id='case-visual'>{first['visual']}</div>
    </div>
  </section>
  <section class='grid'>
    <div class='card'>
      <h2>Plain-language summary</h2>
      <pre id='summary'>{escape(first['summary'])}</pre>
      <h2 style='margin-top:16px'>Copyable command</h2>
      <pre id='command'>{escape(first['command'])}</pre>
    </div>
    <div class='card'>
      <h2>HTML report preview</h2>
      <iframe id='report-frame' srcdoc="{escape(first['html'])}"></iframe>
    </div>
  </section>
  <section class='grid2'>
    <div class='card'>
      <h2>Shareable card</h2>
      <div id='social-card'>{first['social']}</div>
    </div>
    <div class='card'>
      <h2>How to use this page</h2>
      <ul>
        <li>Open this file locally to preview the product surface without installing Python.</li>
        <li>Publish it through GitHub Pages to create a live demo URL for README and social posts.</li>
        <li>Use the case query string like <code>?case=btc_gold_oil_shocks</code> when sharing a specific scenario.</li>
      </ul>
    </div>
  </section>
</div>
<script>
const CASES = {cases_json};
const select = document.getElementById('case-select');
const whyEl = document.getElementById('case-why');
const visualEl = document.getElementById('case-visual');
const summaryEl = document.getElementById('summary');
const commandEl = document.getElementById('command');
const frame = document.getElementById('report-frame');
const social = document.getElementById('social-card');
function renderCase(key) {{
  const item = CASES[key];
  if (!item) return;
  whyEl.textContent = item.why;
  visualEl.innerHTML = item.visual;
  summaryEl.textContent = item.summary;
  commandEl.textContent = item.command;
  frame.srcdoc = item.html;
  social.innerHTML = item.social;
  const url = new URL(window.location.href);
  url.searchParams.set('case', key);
  window.history.replaceState({{}}, '', url.toString());
}}
select.addEventListener('change', (e) => renderCase(e.target.value));
const queryCase = new URL(window.location.href).searchParams.get('case');
if (queryCase && CASES[queryCase]) {{
  select.value = queryCase;
}}
renderCase(select.value);
</script>
</body>
</html>"""

