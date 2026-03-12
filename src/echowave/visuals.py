
"""Visual and HTML reporting helpers for EchoWave.

These helpers keep runtime dependencies light by emitting standalone SVG/HTML
artifacts. The goal is not publication-grade plotting; it is fast, shareable,
GitHub-friendly report generation that works in ordinary Python environments.
"""

from __future__ import annotations

import json
from html import escape
from math import cos, pi, sin
from typing import Any, Iterable, Mapping

import numpy as np

from .communication import summary_card_dict
from .schema import AXIS_DESCRIPTIONS

_AXIS_LABELS = {
    "sampling_irregularity": "Irregularity",
    "noise_contamination": "Noise",
    "predictability": "Predictability",
    "drift_nonstationarity": "Drift",
    "trendness": "Trend",
    "rhythmicity": "Rhythmicity",
    "complexity": "Complexity",
    "nonlinearity_chaoticity": "Nonlinearity",
    "eventness_burstiness": "Burstiness",
    "regime_switching": "Regimes",
    "coupling_networkedness": "Coupling",
    "heterogeneity": "Heterogeneity",
}


def _level(score: float) -> str:
    score = float(score)
    if score >= 0.75:
        return "very high"
    if score >= 0.55:
        return "high"
    if score >= 0.35:
        return "moderate"
    if score >= 0.15:
        return "low"
    return "very low"


def _nice_label(name: str) -> str:
    return _AXIS_LABELS.get(name, name.replace("_", " ").title())


def _svg_wrap(body: str, *, width: int, height: int, title: str | None = None) -> str:
    title_node = f"<title>{escape(title)}</title>" if title else ""
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
        f"viewBox='0 0 {width} {height}' role='img' aria-label='{escape(title or 'EchoWave visual')}'>"
        f"{title_node}{body}</svg>"
    )


def _polygon_points(values: Iterable[float], *, cx: float, cy: float, radius: float) -> str:
    vals = list(values)
    n = max(1, len(vals))
    pts = []
    for i, value in enumerate(vals):
        angle = -pi / 2 + 2 * pi * i / n
        r = radius * float(np.clip(value, 0.0, 1.0))
        x = cx + r * cos(angle)
        y = cy + r * sin(angle)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def profile_radar_svg(profile: Any, *, width: int = 420, height: int = 420) -> str:
    axes = list(profile.axes.keys())
    if not axes:
        return _svg_wrap("<text x='20' y='30'>No axes available.</text>", width=width, height=height, title="EchoWave axis radar")
    values = [float(profile.axes[a]) for a in axes]
    cx = width / 2
    cy = height / 2 + 8
    radius = min(width, height) * 0.31
    grid = []
    for level in (0.25, 0.5, 0.75, 1.0):
        pts = _polygon_points([level] * len(axes), cx=cx, cy=cy, radius=radius)
        grid.append(f"<polygon points='{pts}' fill='none' stroke='#d9e2ec' stroke-width='1'/>")
    spokes = []
    labels = []
    for i, axis in enumerate(axes):
        angle = -pi / 2 + 2 * pi * i / len(axes)
        x = cx + radius * cos(angle)
        y = cy + radius * sin(angle)
        spokes.append(f"<line x1='{cx:.1f}' y1='{cy:.1f}' x2='{x:.1f}' y2='{y:.1f}' stroke='#d9e2ec' stroke-width='1'/>")
        lx = cx + (radius + 20) * cos(angle)
        ly = cy + (radius + 20) * sin(angle)
        anchor = 'middle'
        if lx < cx - 18:
            anchor = 'end'
        elif lx > cx + 18:
            anchor = 'start'
        labels.append(
            f"<text x='{lx:.1f}' y='{ly:.1f}' font-size='11' fill='#334e68' text-anchor='{anchor}' dominant-baseline='middle'>{escape(_nice_label(axis))}</text>"
        )
    profile_pts = _polygon_points(values, cx=cx, cy=cy, radius=radius)
    body = (
        "<rect width='100%' height='100%' fill='white'/>"
        "<text x='18' y='24' font-size='16' font-weight='700' fill='#102a43'>Axis radar</text>"
        "<text x='18' y='42' font-size='11' fill='#486581'>Higher means the axis is more structurally dominant.</text>"
        + "".join(grid)
        + "".join(spokes)
        + f"<polygon points='{profile_pts}' fill='rgba(11,108,255,0.18)' stroke='#0b6cff' stroke-width='2'/>"
        + "".join(labels)
    )
    return _svg_wrap(body, width=width, height=height, title="EchoWave axis radar")


def axis_bar_svg(profile: Any, *, width: int = 560, height: int = 300, top_n: int = 6) -> str:
    items = sorted(((k, float(v)) for k, v in profile.axes.items()), key=lambda kv: kv[1], reverse=True)[:top_n]
    if not items:
        return _svg_wrap("<text x='20' y='30'>No axes available.</text>", width=width, height=height, title="EchoWave top axes")
    left = 170
    right = width - 20
    top = 48
    step = max(30, (height - top - 20) / len(items))
    bar_w = right - left
    rows = []
    for idx, (axis, score) in enumerate(items):
        y = top + idx * step
        filled = bar_w * float(np.clip(score, 0.0, 1.0))
        rows.append(f"<text x='16' y='{y + 14:.1f}' font-size='12' fill='#102a43'>{escape(_nice_label(axis))}</text>")
        rows.append(f"<rect x='{left}' y='{y:.1f}' width='{bar_w:.1f}' height='16' rx='8' fill='#edf2f7'/>")
        rows.append(f"<rect x='{left}' y='{y:.1f}' width='{filled:.1f}' height='16' rx='8' fill='#0b6cff'/>")
        rows.append(f"<text x='{right - 2:.1f}' y='{y + 13:.1f}' font-size='11' fill='#334e68' text-anchor='end'>{score:.2f}</text>")
    body = (
        "<rect width='100%' height='100%' fill='white'/>"
        "<text x='16' y='24' font-size='16' font-weight='700' fill='#102a43'>Top structure axes</text>"
        "<text x='16' y='40' font-size='11' fill='#486581'>The axes most likely to shape modelling and communication choices.</text>"
        + "".join(rows)
    )
    return _svg_wrap(body, width=width, height=height, title="EchoWave top axes")


def similarity_components_svg(report: Any, *, width: int = 560, height: int = 280) -> str:
    items = sorted(((k, float(v)) for k, v in report.component_scores.items()), key=lambda kv: kv[1], reverse=True)
    if not items:
        return _svg_wrap("<text x='20' y='30'>No components available.</text>", width=width, height=height, title="EchoWave similarity components")
    left = 160
    right = width - 20
    top = 48
    step = max(28, (height - top - 18) / len(items))
    bar_w = right - left
    rows = []
    for idx, (name, score) in enumerate(items):
        y = top + idx * step
        filled = bar_w * float(np.clip(score, 0.0, 1.0))
        rows.append(f"<text x='16' y='{y + 14:.1f}' font-size='12' fill='#102a43'>{escape(name.replace('_', ' '))}</text>")
        rows.append(f"<rect x='{left}' y='{y:.1f}' width='{bar_w:.1f}' height='16' rx='8' fill='#edf2f7'/>")
        rows.append(f"<rect x='{left}' y='{y:.1f}' width='{filled:.1f}' height='16' rx='8' fill='#dd6b20'/>")
        rows.append(f"<text x='{right - 2:.1f}' y='{y + 13:.1f}' font-size='11' fill='#334e68' text-anchor='end'>{score:.2f}</text>")
    body = (
        "<rect width='100%' height='100%' fill='white'/>"
        "<text x='16' y='24' font-size='16' font-weight='700' fill='#102a43'>Similarity components</text>"
        f"<text x='16' y='40' font-size='11' fill='#486581'>Overall similarity {report.similarity_score:.2f} ({escape(report.qualitative_label)}).</text>"
        + "".join(rows)
    )
    return _svg_wrap(body, width=width, height=height, title="EchoWave similarity components")


def series_overlay_svg(left: Any, right: Any | None = None, *, width: int = 720, height: int = 240, left_label: str = "left", right_label: str = "right") -> str:
    l = np.asarray(left, dtype=float).reshape(-1)
    r = None if right is None else np.asarray(right, dtype=float).reshape(-1)
    if l.size == 0:
        return _svg_wrap("<text x='20' y='30'>No series available.</text>", width=width, height=height, title="EchoWave series preview")
    if r is not None and r.size > 0:
        n = min(len(l), len(r))
        l = l[:n]
        r = r[:n]
    data = l if r is None else np.concatenate([l, r])
    finite = data[np.isfinite(data)]
    if finite.size == 0:
        finite = np.array([0.0, 1.0])
    ymin = float(np.min(finite))
    ymax = float(np.max(finite))
    if ymax - ymin < 1e-9:
        ymax = ymin + 1.0
    def _path(values: np.ndarray) -> str:
        xs = np.linspace(40, width - 20, len(values))
        ys = height - 28 - ((values - ymin) / (ymax - ymin)) * (height - 52)
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
        return pts
    body = ["<rect width='100%' height='100%' fill='white'/>", "<text x='16' y='24' font-size='16' font-weight='700' fill='#102a43'>Series preview</text>"]
    body.append("<line x1='40' y1='24' x2='40' y2='212' stroke='#d9e2ec'/><line x1='40' y1='212' x2='700' y2='212' stroke='#d9e2ec'/>")
    body.append(f"<polyline points='{_path(l)}' fill='none' stroke='#0b6cff' stroke-width='2.5'/>")
    body.append(f"<text x='46' y='42' font-size='11' fill='#0b6cff'>{escape(left_label)}</text>")
    if r is not None:
        body.append(f"<polyline points='{_path(r)}' fill='none' stroke='#dd6b20' stroke-width='2.5' stroke-dasharray='5 4'/>")
        body.append(f"<text x='120' y='42' font-size='11' fill='#dd6b20'>{escape(right_label)}</text>")
    return _svg_wrap("".join(body), width=width, height=height, title="EchoWave series preview")


def rolling_similarity_svg(windows: Iterable[Mapping[str, Any]], *, width: int = 720, height: int = 240) -> str:
    items = list(windows)
    scores = [float(item.get("similarity_score", np.nan)) for item in items]
    scores = [s for s in scores if np.isfinite(s)]
    if not scores:
        return _svg_wrap("<text x='20' y='30'>No rolling similarity windows available.</text>", width=width, height=height, title="Rolling similarity")
    arr = np.asarray(scores, dtype=float)
    xs = np.linspace(40, width - 20, len(arr))
    ys = height - 28 - arr * (height - 52)
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    body = (
        "<rect width='100%' height='100%' fill='white'/>"
        "<text x='16' y='24' font-size='16' font-weight='700' fill='#102a43'>Rolling similarity</text>"
        "<line x1='40' y1='24' x2='40' y2='212' stroke='#d9e2ec'/><line x1='40' y1='212' x2='700' y2='212' stroke='#d9e2ec'/>"
        "<line x1='40' y1='118' x2='700' y2='118' stroke='#eef2f6' stroke-dasharray='4 4'/>"
        f"<polyline points='{pts}' fill='none' stroke='#177245' stroke-width='2.5'/>"
        f"<text x='46' y='42' font-size='11' fill='#177245'>mean={float(np.mean(arr)):.2f}, min={float(np.min(arr)):.2f}, max={float(np.max(arr)):.2f}</text>"
    )
    return _svg_wrap(body, width=width, height=height, title="Rolling similarity")


def _brand_shell(*, title: str, body: str, accent: str = "#0b6cff") -> str:
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{escape(title)}</title>
<style>
:root {{ --ink:#102a43; --muted:#486581; --line:#d9e2ec; --panel:#ffffff; --soft:#f7fafc; --brand:{accent}; --orange:#dd6b20; --green:#177245; --bg:#f3f7fb; --shadow:0 1px 2px rgba(16,42,67,.05),0 12px 24px rgba(16,42,67,.08); }}
* {{ box-sizing:border-box; }} body {{ margin:0; padding:0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; color:var(--ink); background:var(--bg); line-height:1.55; }}
a {{ color:var(--brand); text-decoration:none; }}
.header {{ background:linear-gradient(180deg,#0f2740,#17344d); color:#fff; border-bottom:1px solid rgba(255,255,255,.08); }}
.header-inner {{ max-width:1180px; margin:0 auto; padding:16px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
.brand {{ display:flex; align-items:center; gap:12px; font-weight:700; letter-spacing:-.02em; }}
.brand-mark {{ width:22px; height:22px; border-radius:6px; background:linear-gradient(135deg,var(--brand),#8bc4ff); box-shadow:inset 0 0 0 1px rgba(255,255,255,.18); }}
.brand small {{ display:block; font-weight:500; color:#cfe2ff; }}
.container {{ max-width:1180px; margin:0 auto; padding:28px 24px 36px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:20px 22px; box-shadow:var(--shadow); }}
.hero {{ display:grid; grid-template-columns:1.1fr .9fr; gap:20px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:20px; }}
.facts {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:16px; }}
.fact {{ background:var(--soft); border:1px solid var(--line); border-radius:12px; padding:12px; }}
.fact strong {{ display:block; font-size:1.2rem; }}
.pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef5ff; color:var(--brand); font-size:.88rem; font-weight:600; margin-right:8px; }}
.pill.alt {{ background:#fff4e8; color:#dd6b20; }}
.muted {{ color:var(--muted); }}
.score {{ font-size:2.6rem; line-height:1; font-weight:800; letter-spacing:-.04em; }}
h1,h2,h3 {{ margin:0 0 10px; }} h1 {{ font-size:2.2rem; letter-spacing:-.03em; }} h2 {{ font-size:1.25rem; }}
p.lead {{ color:var(--muted); font-size:1.05rem; margin:8px 0 0; }}
table {{ width:100%; border-collapse:collapse; }} th,td {{ text-align:left; padding:10px 8px; border-bottom:1px solid var(--line); vertical-align:top; }} th {{ font-size:.92rem; color:var(--muted); }} ul {{ margin:0; padding-left:1.1rem; }} pre {{ background:#f7fafc; border:1px solid var(--line); border-radius:12px; padding:14px; overflow:auto; font-size:.88rem; white-space:pre-wrap; word-break:break-word; }}
.signature {{ margin-top:18px; padding-top:14px; border-top:1px dashed var(--line); color:var(--muted); font-size:.92rem; }}
@media (max-width: 920px) {{ .hero,.grid,.facts {{ grid-template-columns:1fr; }} body {{ padding:0; }} .container {{ padding:18px; }} }}
</style>
</head>
<body>
<header class='header'><div class='header-inner'><div class='brand'><span class='brand-mark'></span><div><div>EchoWave</div><small>explainable time-series similarity for humans and agents</small></div></div><div><span class='pill'>explainable similarity</span></div></div></header>
<div class='container'>{body}</div>
</body>
</html>"""


def profile_html_report(profile: Any, *, title: str | None = None, audience: str = "general") -> str:
    card = summary_card_dict(profile, audience=audience)
    reliability = card["dataset_facts"]["reliability"]
    radar = profile_radar_svg(profile)
    bars = axis_bar_svg(profile)
    top_rows = "".join(
        f"<tr><td>{escape(item['plain_label'])}</td><td>{item['score']:.2f}</td><td>{escape(item['level'])}</td><td>{escape(item['meaning'])}</td></tr>"
        for item in card["top_structure_axes"]
    )
    takeaways = "".join(f"<li>{escape(item)}</li>" for item in card["main_takeaways"])
    watchouts = "".join(f"<li>{escape(item)}</li>" for item in card["main_watchouts"])
    actions = "".join(f"<li>{escape(item)}</li>" for item in card["recommended_next_actions"])
    compact = escape(profile.to_agent_context_json(budget="lean"))
    archetypes = ", ".join(card["archetypes"][:4]) if card["archetypes"] else "No strong archetype label dominates yet."
    subtitle = title or f"EchoWave profile - {card['domain']}"
    body = f"""
  <section class='hero'>
    <div class='card'>
      <span class='pill'>EchoWave</span><span class='pill'>{escape(str(card['domain']))}</span><span class='pill'>{escape(str(card['observation_mode']))}</span>
      <h1>{escape(card['executive_summary'])}</h1>
      <p class='lead'>Generate plain-English structural context you can compare, share, and hand off.</p>
      <div class='facts'>
        <div class='fact'><span class='muted'>Reliability</span><strong>{reliability['score']:.2f}</strong><span class='muted'>{escape(reliability['level'])}</span></div>
        <div class='fact'><span class='muted'>Subjects / units</span><strong>{card['dataset_facts']['n_subjects']}</strong><span class='muted'>cohort size</span></div>
        <div class='fact'><span class='muted'>Median channels</span><strong>{card['dataset_facts']['n_channels_median']}</strong><span class='muted'>per unit</span></div>
        <div class='fact'><span class='muted'>Median length</span><strong>{card['dataset_facts']['length_median']}</strong><span class='muted'>samples</span></div>
      </div>
      <h2 style='margin-top:22px'>What this looks like structurally</h2>
      <p>{escape(archetypes)}</p>
      <h2 style='margin-top:22px'>Recommended next actions</h2>
      <ul>{actions}</ul>
      <div class='signature'>Generated by EchoWave for an audience of <strong>{escape(audience)}</strong>. Use this as a structural context and dataset-comparison artifact, not as a modelling guarantee.</div>
    </div>
    <div class='card'>{radar}</div>
  </section>
  <section class='grid'>
    <div class='card'>{bars}</div>
    <div class='card'>
      <h2>Top structure axes</h2>
      <table><thead><tr><th>Axis</th><th>Score</th><th>Level</th><th>What it means</th></tr></thead><tbody>{top_rows}</tbody></table>
    </div>
  </section>
  <section class='grid'>
    <div class='card'><h2>Main takeaways</h2><ul>{takeaways}</ul></div>
    <div class='card'><h2>Main watchouts</h2><ul>{watchouts}</ul></div>
  </section>
  <section class='grid'>
    <div class='card'><h2>Why the score is trustworthy</h2><p><strong>Overall reliability:</strong> {reliability['score']:.2f} ({escape(reliability['level'])})</p><p class='muted'>A higher reliability score means more proxy coverage and stronger data support for the reported structure.</p></div>
    <div class='card'><h2>Compact agent context</h2><pre>{compact}</pre></div>
  </section>
"""
    return _brand_shell(title=subtitle, body=body, accent="#0b6cff")



def similarity_html_report(report: Any, *, title: str | None = None, left_series: Any | None = None, right_series: Any | None = None, rolling_windows: Iterable[Mapping[str, Any]] | None = None) -> str:
    bars = similarity_components_svg(report)
    overlay = series_overlay_svg(left_series, right_series, left_label=report.left_name, right_label=report.right_name) if left_series is not None and right_series is not None else ""
    rolling = rolling_similarity_svg(rolling_windows) if rolling_windows else ""
    suggestions = "".join(f"<li>{escape(item)}</li>" for item in report.suggestions)
    notes = "".join(f"<li>{escape(item)}</li>" for item in report.notes)
    compact = escape(report.to_agent_context_json(budget="lean"))
    title_text = title or f"EchoWave similarity report - {report.left_name} vs {report.right_name}"
    overlay_card = f"<div class='card'>{overlay}</div>" if overlay else ""
    rolling_card = f"<div class='card'>{rolling}</div>" if rolling else ""
    body = f"""
  <section class='hero'>
    <div class='card'>
      <span class='pill alt'>similarity</span><span class='pill'>{escape(report.mode)}</span>
      <h1>{escape(report.interpretation)}</h1>
      <p class='muted'>Overall similarity score.</p>
      <div class='score'>{report.similarity_score:.2f}</div>
      <p class='muted'>{escape(report.left_name)} vs {escape(report.right_name)} - {escape(report.qualitative_label)}</p>
      <h2 style='margin-top:18px'>Recommended next actions</h2>
      <ul>{suggestions}</ul>
      <div class='signature'>Use this as an interpretable comparison summary. If you need alignment paths or distance matrices, pair the result with a lower-level similarity library.</div>
    </div>
    <div class='card'>{bars}</div>
  </section>
  <section class='grid'>
    {overlay_card}
    {rolling_card}
    <div class='card'><h2>Notes and guardrails</h2><ul>{notes or '<li>No major notes.</li>'}</ul></div>
    <div class='card'><h2>Compact agent context</h2><pre>{compact}</pre></div>
  </section>
"""
    return _brand_shell(title=title_text, body=body, accent="#dd6b20")


def _social_card_shell(*, title: str, subtitle: str, bullets: list[str], accent: str, width: int = 1200, height: int = 630) -> str:
    bullets_svg = "".join(
        f"<text x='70' y='{225 + 58*i}' font-size='30' fill='#17324d'>&#8226; {escape(item)}</text>" for i, item in enumerate(bullets[:4])
    )
    return _svg_wrap(
        f"<defs><linearGradient id='bg' x1='0' x2='1' y1='0' y2='1'><stop offset='0%' stop-color='#f7fbff'/><stop offset='100%' stop-color='#eaf2ff'/></linearGradient></defs>"
        f"<rect width='100%' height='100%' fill='url(#bg)'/>"
        f"<rect x='40' y='38' width='{width-80}' height='{height-76}' rx='32' fill='white' stroke='#d9e2ec'/>"
        f"<rect x='40' y='38' width='14' height='{height-76}' rx='7' fill='{accent}'/>"
        f"<text x='84' y='108' font-size='34' font-weight='700' fill='#102a43'>EchoWave</text>"
        f"<text x='84' y='152' font-size='54' font-weight='800' fill='#102a43'>{escape(title)}</text>"
        f"<text x='84' y='192' font-size='28' fill='#486581'>{escape(subtitle)}</text>"
        f"{bullets_svg}"
        f"<text x='84' y='{height-74}' font-size='24' fill='#486581'>explainable time-series similarity for humans and agents</text>",
        width=width,
        height=height,
        title=f"EchoWave social card - {title}",
    )


def profile_social_card_svg(profile: Any, *, title: str | None = None) -> str:
    card = summary_card_dict(profile, audience="general")
    bullets = [item["plain_label"] for item in card["top_structure_axes"][:3]]
    return _social_card_shell(
        title=title or "Plain-English structural report",
        subtitle=f"{card['domain']} | reliability {card['dataset_facts']['reliability']['score']:.2f}",
        bullets=[f"Top axis: {b}" for b in bullets] + ["Structural context for better matching"],
        accent="#0b6cff",
    )


def similarity_social_card_svg(report: Any, *, title: str | None = None) -> str:
    bullets = [f"Similarity {report.similarity_score:.2f}", f"Label: {report.qualitative_label}"]
    bullets.extend(f"{name.replace('_', ' ')} {score:.2f}" for name, score in list(report.component_scores.items())[:2])
    return _social_card_shell(
        title=title or "Similarity verdict",
        subtitle=f"{report.left_name} vs {report.right_name}",
        bullets=bullets,
        accent="#dd6b20",
    )

