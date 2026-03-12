"""Reproducible decision-impact benchmark for tsontology.

This benchmark is intentionally modest. It measures a product question rather
than a publication question: does a profile-guided baseline-family choice beat
an always-use-the-same-baseline policy often enough to matter?
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np

try:
    from tsontology import profile_series
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from tsontology import profile_series


@dataclass
class CaseResult:
    family: str
    routed_model: str
    fixed_model: str
    routed_mae: float
    fixed_mae: float
    improvement: float
    decision_changed: bool


def _seasonal(train: np.ndarray, horizon: int, period: int) -> np.ndarray:
    period = max(1, min(period, len(train)))
    tail = train[-period:]
    reps = int(np.ceil(horizon / period))
    return np.tile(tail, reps)[:horizon]


def _last(train: np.ndarray, horizon: int) -> np.ndarray:
    return np.repeat(train[-1], horizon)


def _moving_average(train: np.ndarray, horizon: int, window: int = 5) -> np.ndarray:
    window = max(1, min(window, len(train)))
    return np.repeat(float(np.mean(train[-window:])), horizon)


def _drift(train: np.ndarray, horizon: int) -> np.ndarray:
    x = np.arange(len(train), dtype=float)
    coef = np.polyfit(x, train, deg=1)
    future_x = np.arange(len(train), len(train) + horizon, dtype=float)
    return coef[0] * future_x + coef[1]


def _estimate_period(train: np.ndarray, candidates: tuple[int, ...] = (6, 7, 12, 24, 30)) -> int:
    best = candidates[0]
    best_score = -np.inf
    train = np.asarray(train, dtype=float)
    if len(train) < 8:
        return best
    centered = train - np.mean(train)
    for p in candidates:
        if p >= len(train):
            continue
        a = centered[:-p]
        b = centered[p:]
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        score = float(np.dot(a, b) / denom) if denom > 0 else -np.inf
        if score > best_score:
            best_score = score
            best = p
    return best


def _route(train: np.ndarray) -> str:
    profile = profile_series(train)
    axes = profile.axes
    if axes.get("sampling_irregularity", 0.0) > 0.45:
        return "moving_average"
    if axes.get("rhythmicity", 0.0) > 0.75 and axes.get("predictability", 0.0) > 0.35:
        return "seasonal_naive"
    if axes.get("eventness_burstiness", 0.0) > 0.30 or axes.get("noise_contamination", 0.0) > 0.60:
        return "moving_average"
    if axes.get("trendness", 0.0) > 0.28 and axes.get("predictability", 0.0) > 0.20:
        return "drift"
    return "last_value"


def _forecast(model: str, train: np.ndarray, horizon: int) -> np.ndarray:
    if model == "seasonal_naive":
        return _seasonal(train, horizon, _estimate_period(train))
    if model == "drift":
        return _drift(train, horizon)
    if model == "moving_average":
        return _moving_average(train, horizon)
    return _last(train, horizon)


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def _family_series(family: str, *, seed: int, n: int = 96, horizon: int = 12) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.arange(n + horizon)
    if family == "seasonal":
        y = 10 + 2.5 * np.sin(2 * np.pi * t / 12) + 0.4 * rng.normal(size=t.size)
    elif family == "trend":
        y = 4 + 0.18 * t + 0.6 * rng.normal(size=t.size)
    elif family == "trend_plus_seasonal":
        y = 6 + 0.09 * t + 1.7 * np.sin(2 * np.pi * t / 12 - 0.8) + 0.5 * rng.normal(size=t.size)
    elif family == "bursty":
        y = 8 + 0.4 * rng.normal(size=t.size)
        centers = rng.choice(np.arange(8, t.size - 8), size=4, replace=False)
        for c in centers:
            y += np.exp(-0.25 * np.abs(t - c)) * rng.uniform(2.0, 4.5)
    elif family == "flat_noisy":
        y = 7 + 0.8 * rng.normal(size=t.size)
    else:
        raise KeyError(family)
    return y[:-horizon], y[-horizon:]


def run_benchmark(*, seeds_per_family: int = 30) -> dict:
    families = ["seasonal", "trend", "trend_plus_seasonal", "bursty", "flat_noisy"]
    results: list[CaseResult] = []
    for family in families:
        for seed in range(seeds_per_family):
            train, test = _family_series(family, seed=seed)
            routed = _route(train)
            fixed = "last_value"
            routed_pred = _forecast(routed, train, len(test))
            fixed_pred = _forecast(fixed, train, len(test))
            routed_mae = _mae(test, routed_pred)
            fixed_mae = _mae(test, fixed_pred)
            results.append(CaseResult(
                family=family,
                routed_model=routed,
                fixed_model=fixed,
                routed_mae=routed_mae,
                fixed_mae=fixed_mae,
                improvement=fixed_mae - routed_mae,
                decision_changed=routed != fixed,
            ))
    improvements = np.array([r.improvement for r in results], dtype=float)
    changed = np.array([r.decision_changed for r in results], dtype=bool)
    wins = np.array([r.improvement > 0 for r in results], dtype=bool)
    family_summary = {}
    for family in families:
        fam = [r for r in results if r.family == family]
        family_summary[family] = {
            "n": len(fam),
            "decision_changed_rate": float(np.mean([r.decision_changed for r in fam])),
            "win_rate": float(np.mean([r.improvement > 0 for r in fam])),
            "mean_improvement": float(np.mean([r.improvement for r in fam])),
            "median_improvement": float(np.median([r.improvement for r in fam])),
            "most_common_routed_model": max({m: sum(r.routed_model == m for r in fam) for m in {r.routed_model for r in fam}}, key=lambda k: sum(r.routed_model == k for r in fam)),
        }
    return {
        "benchmark": "decision_impact_benchmark",
        "suite": "synthetic interpretable families",
        "seeds_per_family": seeds_per_family,
        "n_cases": len(results),
        "fixed_policy": "last_value",
        "summary": {
            "decision_changed_rate": float(np.mean(changed)),
            "win_rate_when_changed": float(np.mean(wins[changed])) if np.any(changed) else 0.0,
            "overall_win_rate": float(np.mean(wins)),
            "mean_improvement": float(np.mean(improvements)),
            "median_improvement": float(np.median(improvements)),
        },
        "family_summary": family_summary,
        "results": [asdict(r) for r in results],
        "note": "This is a product benchmark for decision impact, not a publication benchmark.",
    }


def main() -> None:
    payload = run_benchmark()
    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "decision_impact_benchmark.json"
    md_path = out_dir / "decision_impact_benchmark.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# tsontology decision-impact benchmark",
        "",
        payload["note"],
        "",
        f"- cases: {payload['n_cases']}",
        f"- decision changed rate: {payload['summary']['decision_changed_rate']:.3f}",
        f"- win rate when changed: {payload['summary']['win_rate_when_changed']:.3f}",
        f"- overall win rate: {payload['summary']['overall_win_rate']:.3f}",
        f"- mean improvement (fixed MAE - routed MAE): {payload['summary']['mean_improvement']:.4f}",
        "",
        "## By family",
        "",
        "| family | n | change rate | win rate | mean improvement | routed model |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for family, info in payload["family_summary"].items():
        lines.append(f"| {family} | {info['n']} | {info['decision_changed_rate']:.3f} | {info['win_rate']:.3f} | {info['mean_improvement']:.4f} | {info['most_common_routed_model']} |")
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
