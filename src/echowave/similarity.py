"""Time-series similarity utilities for raw-shape and structure-aware comparisons."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
from scipy.signal import savgol_filter

from .metrics import EPS, _js_divergence, _normalized_spectrum
from .profile import DatasetProfile, SeriesProfile, profile_dataset


def _level(score: float) -> str:
    score = float(score)
    if score >= 0.85:
        return "very high"
    if score >= 0.68:
        return "high"
    if score >= 0.48:
        return "moderate"
    if score >= 0.28:
        return "low"
    return "very low"


@dataclass(slots=True)
class SimilarityReport:
    left_name: str
    right_name: str
    mode: str
    similarity_score: float
    qualitative_label: str
    component_scores: dict[str, float]
    interpretation: str
    notes: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "left_name": self.left_name,
            "right_name": self.right_name,
            "mode": self.mode,
            "similarity_score": float(self.similarity_score),
            "qualitative_label": self.qualitative_label,
            "component_scores": dict(self.component_scores),
            "interpretation": self.interpretation,
            "notes": list(self.notes),
            "suggestions": list(self.suggestions),
            "metadata": dict(self.metadata),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        lines = [
            "# tsontology similarity report",
            "",
            f"**left:** {self.left_name}  ",
            f"**right:** {self.right_name}  ",
            f"**mode:** {self.mode}  ",
            f"**overall similarity:** {self.similarity_score:0.3f} ({self.qualitative_label})",
            "",
            "## Interpretation",
            "",
            self.interpretation,
            "",
            "## Component scores",
            "",
            "| component | score | level |",
            "|---|---:|---|",
        ]
        for key, value in self.component_scores.items():
            lines.append(f"| {key} | {float(value):0.3f} | {_level(float(value))} |")
        if self.suggestions:
            lines.extend(["", "## Suggested next moves", ""])
            for item in self.suggestions:
                lines.append(f"- {item}")
        if self.notes:
            lines.extend(["", "## Notes", ""])
            for note in self.notes:
                lines.append(f"- {note}")
        if self.metadata:
            lines.extend(["", "## Metadata", "", "| field | value |", "|---|---|" ])
            for key, value in self.metadata.items():
                lines.append(f"| {key} | {value} |")
        return "\n".join(lines)

    def to_summary_card_markdown(self) -> str:
        lines = [
            "# tsontology similarity summary",
            "",
            f"**Compared:** {self.left_name} vs {self.right_name}",
            "",
            "## Headline",
            "",
            f"These two inputs show **{self.qualitative_label}** similarity overall (score {self.similarity_score:0.3f}).",
            "",
            self.interpretation,
            "",
            "## Most important similarity dimensions",
            "",
            "| plain-language label | score |",
            "|---|---:|",
        ]
        for key, value in sorted(self.component_scores.items(), key=lambda kv: kv[1], reverse=True)[:4]:
            label = key.replace("_", " ")
            lines.append(f"| {label} | {float(value):0.3f} |")
        if self.suggestions:
            lines.extend(["", "## Recommended next actions", ""])
            for item in self.suggestions[:5]:
                lines.append(f"- {item}")
        return "\n".join(lines)

    def to_narrative_report(self) -> str:
        lines = [
            "# tsontology similarity narrative",
            "",
            "## What was compared",
            "",
            f"This report compares **{self.left_name}** with **{self.right_name}** using the **{self.mode}** similarity mode.",
            "",
            "## What the package thinks is going on",
            "",
            self.interpretation,
            "",
            "## Why this matters",
            "",
        ]
        top = sorted(self.component_scores.items(), key=lambda kv: kv[1], reverse=True)
        if top:
            best = top[0][0].replace("_", " ")
            lines.append(f"The strongest agreement appears in **{best}**, which means these two trajectories share an important part of their structure even if they are not identical point by point.")
            lines.append("")
        lines.extend(["## What to do next", ""])
        for item in self.suggestions[:6] or [
            "Inspect the raw trajectories and the aligned windows together.",
            "Check whether similarity is stable over time instead of relying on one aggregate number.",
        ]:
            lines.append(f"- {item}")
        if self.notes:
            lines.extend(["", "## Guardrails", ""])
            for note in self.notes:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def to_html_report(self, *, title: str | None = None) -> str:
        from .visuals import similarity_html_report

        return similarity_html_report(self, title=title)

    def to_agent_context_dict(self, *, budget: str = "lean") -> dict[str, Any]:
        from .agent import agent_context

        return agent_context(self, budget=budget, format="dict")  # type: ignore[return-value]

    def to_agent_context_json(self, *, budget: str = "lean", indent: int = 2) -> str:
        import json as _json
        return _json.dumps(self.to_agent_context_dict(budget=budget), indent=indent)

    def to_agent_context_markdown(self, *, budget: str = "lean") -> str:
        from .agent import agent_context

        return agent_context(self, budget=budget, format="markdown")  # type: ignore[return-value]


def _as_matrix(data: Any) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    if arr.ndim == 2:
        return arr
    if arr.ndim >= 3:
        # reduce higher dimensions conservatively; keep time first if likely dataset-shaped
        flat = arr.reshape(arr.shape[0], -1)
        return flat
    raise ValueError("Unsupported input dimensionality for similarity comparison.")


def _normalize_channel_layout(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=float)
    if arr.ndim != 2:
        return _as_matrix(arr)
    # Prefer time x channels layout. If channels appear to exceed time, transpose.
    if arr.shape[1] > arr.shape[0] and arr.shape[0] <= 16:
        arr = arr.T
    return arr


def _valid_timestamps(timestamps: Any, expected_length: int) -> np.ndarray | None:
    if timestamps is None:
        return None
    ts = np.asarray(timestamps, dtype=float).reshape(-1)
    if ts.size != expected_length:
        return None
    mask = np.isfinite(ts)
    if int(mask.sum()) < 3:
        return None
    return ts


def _interpolate_series(values: np.ndarray, timestamps: np.ndarray | None, n_points: int) -> np.ndarray:
    values = np.asarray(values, dtype=float).reshape(-1)
    mask = np.isfinite(values)
    values = values[mask]
    if values.size < 3:
        return np.full(n_points, np.nan)
    if timestamps is None:
        x = np.linspace(0.0, 1.0, values.size)
    else:
        ts = np.asarray(timestamps, dtype=float).reshape(-1)
        ts = ts[mask]
        if ts.size < 3:
            x = np.linspace(0.0, 1.0, values.size)
        else:
            order = np.argsort(ts, kind="mergesort")
            ts = ts[order]
            values = values[order]
            ts = ts - float(np.min(ts))
            span = float(np.max(ts))
            if span <= EPS:
                x = np.linspace(0.0, 1.0, values.size)
            else:
                x = ts / span
    x = np.clip(x, 0.0, 1.0)
    x_new = np.linspace(0.0, 1.0, n_points)
    if np.unique(x).size < 3:
        return np.interp(x_new, np.linspace(0.0, 1.0, values.size), values)
    return np.interp(x_new, x, values)


def _zscore(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    mu = float(np.nanmean(x))
    sigma = float(np.nanstd(x))
    if sigma <= EPS:
        return np.zeros_like(x)
    return (x - mu) / sigma


def _safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3:
        return float("nan")
    x2 = x[mask]
    y2 = y[mask]
    sx = float(np.std(x2))
    sy = float(np.std(y2))
    if sx <= EPS or sy <= EPS:
        return 0.0
    return float(np.corrcoef(x2, y2)[0, 1])


def _corr_to_similarity(corr: float) -> float:
    if not np.isfinite(corr):
        return float("nan")
    return float(np.clip((corr + 1.0) / 2.0, 0.0, 1.0))


def _smooth_trend(x: np.ndarray) -> np.ndarray:
    n = len(x)
    if n < 9:
        return x
    window = int(max(7, min(n - (1 - n % 2), (n // 6) * 2 + 1)))
    if window % 2 == 0:
        window += 1
    window = min(window, n if n % 2 == 1 else n - 1)
    if window < 5:
        return x
    return savgol_filter(x, window_length=window, polyorder=min(3, window - 2), mode="interp")


def _dtw_distance(x: np.ndarray, y: np.ndarray, window: int | None = None) -> float:
    x = np.asarray(x, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    n = x.size
    m = y.size
    if n == 0 or m == 0:
        return float("nan")
    if window is None:
        window = max(abs(n - m), max(5, min(n, m) // 8))
    window = max(window, abs(n - m))
    cost = np.full((n + 1, m + 1), np.inf, dtype=float)
    cost[0, 0] = 0.0
    for i in range(1, n + 1):
        j_start = max(1, i - window)
        j_stop = min(m + 1, i + window + 1)
        for j in range(j_start, j_stop):
            dist = abs(x[i - 1] - y[j - 1])
            cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
    final = float(cost[n, m])
    if not np.isfinite(final):
        return float("nan")
    return final / (n + m)


def _distance_to_similarity(distance: float, scale: float = 1.0) -> float:
    if not np.isfinite(distance):
        return float("nan")
    return float(np.exp(-max(0.0, distance) / max(scale, EPS)))


def _resampled_multichannel(data: Any, timestamps: Any | None = None, n_points: int = 256) -> np.ndarray:
    arr = _normalize_channel_layout(_as_matrix(data))
    ts = _valid_timestamps(timestamps, arr.shape[0])
    channels = []
    for idx in range(arr.shape[1]):
        channel = _interpolate_series(arr[:, idx], ts, n_points)
        channels.append(_zscore(channel))
    return np.column_stack(channels)


def _pair_multichannel(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray, str]:
    if left.shape[1] == right.shape[1]:
        return left, right, "paired_channels"
    left_agg = np.nanmean(left, axis=1, keepdims=True)
    right_agg = np.nanmean(right, axis=1, keepdims=True)
    return left_agg, right_agg, "aggregate_channels"


def _mean_channel(values: np.ndarray) -> np.ndarray:
    if values.ndim == 1:
        return values
    return np.nanmean(values, axis=1)


def _series_interpretation(overall: float, components: Mapping[str, float], left_name: str, right_name: str) -> str:
    ranked = sorted(components.items(), key=lambda kv: kv[1], reverse=True)
    strong = [name.replace("_", " ") for name, value in ranked if value >= 0.65][:2]
    weak = [name.replace("_", " ") for name, value in ranked if value <= 0.4][:2]
    if overall >= 0.75:
        sentence = f"{left_name} and {right_name} are strongly similar overall."
    elif overall >= 0.55:
        sentence = f"{left_name} and {right_name} share a noticeable amount of structure, but the match is not one-to-one."
    elif overall >= 0.35:
        sentence = f"{left_name} and {right_name} have some overlapping structure, but the relationship is mixed."
    else:
        sentence = f"{left_name} and {right_name} do not look very similar overall."
    if strong:
        sentence += " The best agreement appears in " + " and ".join(strong) + "."
    if weak:
        sentence += " The weakest agreement appears in " + " and ".join(weak) + ", so timing or regime differences probably matter."
    return sentence


def _profile_from_input(obj: Any, *, name: str | None = None) -> tuple[DatasetProfile | SeriesProfile, str]:
    if isinstance(obj, (DatasetProfile, SeriesProfile)):
        return obj, name or getattr(obj.metadata, "name", None) or obj.metadata.get("name", obj.kind)
    profile = profile_dataset(obj)
    return profile, name or "dataset"


def compare_series(
    left: Any,
    right: Any,
    *,
    left_timestamps: Any | None = None,
    right_timestamps: Any | None = None,
    left_name: str = "left",
    right_name: str = "right",
    n_points: int = 256,
) -> SimilarityReport:
    """Compare two raw time-series inputs and return a shape-aware similarity report.

    The comparison mixes pointwise agreement, dynamic-time-warping, trend similarity,
    derivative similarity, and spectral similarity. Inputs may be univariate or
    multichannel. When channel counts differ, the function falls back to aggregate
    trajectories instead of forcing an arbitrary channel pairing.
    """

    left_rs = _resampled_multichannel(left, timestamps=left_timestamps, n_points=n_points)
    right_rs = _resampled_multichannel(right, timestamps=right_timestamps, n_points=n_points)
    left_cmp, right_cmp, channel_mode = _pair_multichannel(left_rs, right_rs)

    correlations = []
    dtw_scores = []
    trend_scores = []
    derivative_scores = []
    spectral_scores = []
    for idx in range(left_cmp.shape[1]):
        xl = left_cmp[:, idx]
        xr = right_cmp[:, idx]
        corr = _corr_to_similarity(_safe_corr(xl, xr))
        correlations.append(corr)

        dtw = _distance_to_similarity(_dtw_distance(xl, xr), scale=0.8)
        dtw_scores.append(dtw)

        trend_l = _smooth_trend(xl)
        trend_r = _smooth_trend(xr)
        trend_scores.append(_corr_to_similarity(_safe_corr(trend_l, trend_r)))

        dxl = np.diff(xl)
        dxr = np.diff(xr)
        derivative_scores.append(_corr_to_similarity(_safe_corr(dxl, dxr)))

        _, pl = _normalized_spectrum(xl)
        _, pr = _normalized_spectrum(xr)
        m = min(pl.size, pr.size)
        if m >= 4:
            spectral_scores.append(float(np.clip(1.0 - _js_divergence(pl[:m], pr[:m]), 0.0, 1.0)))
        else:
            spectral_scores.append(float("nan"))

    components = {
        "shape_similarity": float(np.nanmean(correlations)),
        "dtw_similarity": float(np.nanmean(dtw_scores)),
        "trend_similarity": float(np.nanmean(trend_scores)),
        "derivative_similarity": float(np.nanmean(derivative_scores)),
        "spectral_similarity": float(np.nanmean(spectral_scores)),
    }

    weights = {
        "shape_similarity": 0.27,
        "dtw_similarity": 0.23,
        "trend_similarity": 0.20,
        "derivative_similarity": 0.15,
        "spectral_similarity": 0.15,
    }
    valid = [(key, value) for key, value in components.items() if np.isfinite(value)]
    if valid:
        weight_sum = sum(weights[key] for key, _ in valid)
        overall = float(sum(weights[key] * value for key, value in valid) / max(weight_sum, EPS))
    else:
        overall = 0.0

    notes: list[str] = []
    if channel_mode == "aggregate_channels":
        notes.append("Channel counts did not match, so the comparison used aggregate trajectories rather than one-to-one channel pairing.")
    if components["trend_similarity"] - components["shape_similarity"] >= 0.2:
        notes.append("Broad trend agreement is stronger than point-by-point alignment, which often means the stories match better than the exact timing.")
    if components["spectral_similarity"] - components["shape_similarity"] >= 0.2:
        notes.append("Rhythms or periodic structure match more closely than exact levels, so cycle-aware comparisons may be more informative than raw overlays.")
    if components["dtw_similarity"] - components["shape_similarity"] >= 0.15:
        notes.append("Dynamic-time-warping similarity is stronger than direct shape correlation, suggesting similar patterns with shifted timing.")

    suggestions = [
        "Plot both series after z-score normalization to show the shared shape without scale differences.",
        "Run rolling or windowed similarity if you expect the relationship to change over time.",
        "Use structural-profile similarity when scales, frequencies, or observation modes differ too much for raw-shape comparison.",
    ]
    if components["spectral_similarity"] >= 0.65:
        suggestions.append("Inspect spectral or seasonality-aware models because the two series share rhythm strongly.")
    if components["dtw_similarity"] >= 0.65 and components["shape_similarity"] < 0.55:
        suggestions.append("Try lag-aware alignment or event-based anchoring because the main mismatch may be timing rather than mechanism.")

    return SimilarityReport(
        left_name=left_name,
        right_name=right_name,
        mode="raw_series",
        similarity_score=overall,
        qualitative_label=_level(overall),
        component_scores=components,
        interpretation=_series_interpretation(overall, components, left_name, right_name),
        notes=notes,
        suggestions=suggestions,
        metadata={
            "channel_mode": channel_mode,
            "resample_points": int(n_points),
            "left_channels": int(left_rs.shape[1]),
            "right_channels": int(right_rs.shape[1]),
        },
    )


def compare_profiles(
    left: Any,
    right: Any,
    *,
    left_name: str = "left profile",
    right_name: str = "right profile",
) -> SimilarityReport:
    """Compare two tsontology profiles or raw inputs at the ontology-axis level."""

    left_profile, left_resolved_name = _profile_from_input(left, name=left_name)
    right_profile, right_resolved_name = _profile_from_input(right, name=right_name)

    left_axes = {k: float(v) for k, v in left_profile.axes.items()}
    right_axes = {k: float(v) for k, v in right_profile.axes.items()}
    keys = sorted(set(left_axes) | set(right_axes))
    axis_similarity = {key: float(np.clip(1.0 - abs(left_axes.get(key, 0.0) - right_axes.get(key, 0.0)), 0.0, 1.0)) for key in keys}

    groups = {
        "observation_similarity": ["sampling_irregularity", "noise_contamination"],
        "dynamic_similarity": [
            "predictability",
            "drift_nonstationarity",
            "trendness",
            "rhythmicity",
            "complexity",
            "nonlinearity_chaoticity",
            "eventness_burstiness",
            "regime_switching",
        ],
        "multivariate_similarity": ["coupling_networkedness", "heterogeneity"],
    }
    components = {
        name: float(np.nanmean([axis_similarity[k] for k in members if k in axis_similarity]))
        for name, members in groups.items()
    }
    components["overall_axis_similarity"] = float(np.nanmean(list(axis_similarity.values())))
    overall = components["overall_axis_similarity"]

    ranked_diffs = sorted(((key, abs(left_axes.get(key, 0.0) - right_axes.get(key, 0.0))) for key in keys), key=lambda kv: kv[1], reverse=True)
    most_different = [key.replace("_", " ") for key, diff in ranked_diffs[:2] if diff >= 0.2]
    strongest = [name.replace("_", " ") for name, score in sorted(components.items(), key=lambda kv: kv[1], reverse=True)[:2]]
    interpretation = f"{left_resolved_name} and {right_resolved_name} are {_level(overall)}ly similar at the structural-profile level."
    if strongest:
        interpretation += " The strongest agreement is in " + " and ".join(strongest) + "."
    if most_different:
        interpretation += " The biggest differences appear in " + " and ".join(most_different) + "."

    suggestions = [
        "Use profile similarity when you want to compare datasets collected on different scales but with comparable structure.",
        "Inspect the axis-level differences to explain why two datasets need different validation or model choices.",
        "Attach both dataset cards and the similarity report when presenting cross-domain analogies to non-method collaborators.",
    ]
    notes = [
        "Profile similarity compares ontology structure rather than raw point-by-point alignment.",
    ]
    return SimilarityReport(
        left_name=left_resolved_name,
        right_name=right_resolved_name,
        mode="profile",
        similarity_score=float(overall),
        qualitative_label=_level(float(overall)),
        component_scores=components,
        interpretation=interpretation,
        notes=notes,
        suggestions=suggestions,
        metadata={
            "left_domain": left_profile.metadata.get("domain", "generic"),
            "right_domain": right_profile.metadata.get("domain", "generic"),
            "left_observation_mode": left_profile.metadata.get("observation_mode", "dense"),
            "right_observation_mode": right_profile.metadata.get("observation_mode", "dense"),
            "axis_similarity": axis_similarity,
        },
    )


def rolling_similarity(
    left: Any,
    right: Any,
    *,
    window: int,
    step: int = 1,
    left_timestamps: Any | None = None,
    right_timestamps: Any | None = None,
    n_points: int = 128,
) -> list[dict[str, float]]:
    """Compute raw-series similarity over aligned rolling windows.

    This is designed for quick exploratory work such as 'when did BTC and gold start
    moving more alike?' or 'which launch week looks most like the current one?'.
    """

    left_arr = _normalize_channel_layout(_as_matrix(left))
    right_arr = _normalize_channel_layout(_as_matrix(right))
    min_len = min(left_arr.shape[0], right_arr.shape[0])
    if min_len < window or window < 4:
        return []
    out: list[dict[str, float]] = []
    for start in range(0, min_len - window + 1, step):
        stop = start + window
        lt = None if left_timestamps is None else np.asarray(left_timestamps)[start:stop]
        rt = None if right_timestamps is None else np.asarray(right_timestamps)[start:stop]
        report = compare_series(
            left_arr[start:stop],
            right_arr[start:stop],
            left_timestamps=lt,
            right_timestamps=rt,
            left_name="left_window",
            right_name="right_window",
            n_points=n_points,
        )
        out.append({
            "start": float(start),
            "stop": float(stop),
            "similarity_score": float(report.similarity_score),
            "shape_similarity": float(report.component_scores.get("shape_similarity", float("nan"))),
            "trend_similarity": float(report.component_scores.get("trend_similarity", float("nan"))),
            "spectral_similarity": float(report.component_scores.get("spectral_similarity", float("nan"))),
        })
    return out
