"""Low-level similarity methods that complement EchoWave's report surface."""

from __future__ import annotations

from itertools import permutations
from typing import Any

import numpy as np

from .metrics import EPS


def _to_time_series(data: Any) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.ndim == 0:
        raise ValueError("A time series must contain at least one value.")
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    if arr.ndim == 2:
        if arr.shape[1] > arr.shape[0] and arr.shape[0] <= 16:
            return arr.T
        return arr
    raise ValueError("Time series inputs must be 1D or 2D.")


def _clean_series(values: np.ndarray, timestamps: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray | None]:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2:
        arr = _to_time_series(arr)
    mask = np.all(np.isfinite(arr), axis=1)
    clean = arr[mask]
    if timestamps is None:
        return clean, None
    ts = np.asarray(timestamps, dtype=float).reshape(-1)
    if ts.size != arr.shape[0]:
        raise ValueError("timestamps must match the time dimension of the input series.")
    return clean, ts[mask]


def _pair_series(
    left: Any,
    right: Any,
    *,
    left_timestamps: Any | None = None,
    right_timestamps: Any | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None]:
    left_arr, left_ts = _clean_series(_to_time_series(left), None if left_timestamps is None else np.asarray(left_timestamps, dtype=float))
    right_arr, right_ts = _clean_series(_to_time_series(right), None if right_timestamps is None else np.asarray(right_timestamps, dtype=float))
    if left_arr.shape[1] != right_arr.shape[1]:
        left_arr = np.nanmean(left_arr, axis=1, keepdims=True)
        right_arr = np.nanmean(right_arr, axis=1, keepdims=True)
    return left_arr, right_arr, left_ts, right_ts


def _z_normalize(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    mean = np.mean(arr, axis=0, keepdims=True)
    std = np.std(arr, axis=0, keepdims=True)
    std = np.where(std <= EPS, 1.0, std)
    return (arr - mean) / std


def _local_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def _to_univariate_series(data: Any) -> np.ndarray:
    arr, _ = _clean_series(_to_time_series(data))
    if arr.shape[1] != 1:
        raise ValueError("This method currently supports univariate series only.")
    return arr[:, 0]


def _autocorrelation_vector(x: np.ndarray, max_lag: int) -> np.ndarray:
    series = np.asarray(x, dtype=float).reshape(-1)
    series = series[np.isfinite(series)]
    if series.size < 2 or max_lag <= 0:
        return np.zeros(max_lag, dtype=float)
    centered = series - float(np.mean(series))
    variance = float(np.var(centered))
    if variance <= EPS:
        return np.zeros(max_lag, dtype=float)
    out = np.zeros(max_lag, dtype=float)
    for lag in range(1, max_lag + 1):
        if lag >= series.size:
            break
        out[lag - 1] = float(np.dot(centered[:-lag], centered[lag:]) / ((series.size - lag) * variance))
    return out


def ncc_sequence(x: Any, y: Any, *, normalize: bool = True) -> tuple[np.ndarray, np.ndarray]:
    left, right, _, _ = _pair_series(x, y)
    xs = _z_normalize(left) if normalize else left
    ys = _z_normalize(right) if normalize else right
    corr = None
    for dim in range(xs.shape[1]):
        current = np.correlate(xs[:, dim], ys[:, dim], mode="full")
        corr = current if corr is None else corr + current
    assert corr is not None
    corr = corr / max(xs.shape[1], 1)
    denom = float(np.linalg.norm(xs) * np.linalg.norm(ys))
    if denom <= EPS:
        ncc = np.zeros_like(corr, dtype=float)
    else:
        ncc = corr / denom
    lags = np.arange(-(len(ys) - 1), len(xs), dtype=int)
    return ncc.astype(float), lags


def max_ncc(x: Any, y: Any, *, normalize: bool = True) -> float:
    values, _ = ncc_sequence(x, y, normalize=normalize)
    if values.size == 0:
        return float("nan")
    return float(np.max(values))


def best_shift(x: Any, y: Any, *, normalize: bool = True) -> int:
    values, lags = ncc_sequence(x, y, normalize=normalize)
    if values.size == 0:
        return 0
    return int(lags[int(np.argmax(values))])


def sbd(x: Any, y: Any, *, normalize: bool = True) -> float:
    value = max_ncc(x, y, normalize=normalize)
    if not np.isfinite(value):
        return float("nan")
    return float(1.0 - value)


def independent_max_ncc(x: Any, y: Any, *, normalize: bool = True) -> float:
    left, right, _, _ = _pair_series(x, y)
    if left.shape[1] == 0:
        return float("nan")
    values = [
        max_ncc(left[:, dim], right[:, dim], normalize=normalize)
        for dim in range(left.shape[1])
    ]
    finite = [value for value in values if np.isfinite(value)]
    if not finite:
        return float("nan")
    return float(np.mean(finite))


def independent_sbd(x: Any, y: Any, *, normalize: bool = True) -> float:
    value = independent_max_ncc(x, y, normalize=normalize)
    if not np.isfinite(value):
        return float("nan")
    return float(1.0 - value)


def acf_distance(x: Any, y: Any, *, max_lag: int = 10) -> float:
    left, right, _, _ = _pair_series(x, y)
    if max_lag <= 0:
        raise ValueError("max_lag must be positive.")
    distances = []
    for dim in range(left.shape[1]):
        ax = _autocorrelation_vector(left[:, dim], max_lag=max_lag)
        ay = _autocorrelation_vector(right[:, dim], max_lag=max_lag)
        distances.append(float(np.linalg.norm(ax - ay)))
    if not distances:
        return float("nan")
    return float(np.mean(distances))


def _periodogram_embedding(x: np.ndarray, *, n_coeffs: int = 32, normalize: bool = True) -> np.ndarray:
    parts = []
    for dim in range(x.shape[1]):
        power = np.abs(np.fft.rfft(x[:, dim])) ** 2
        if normalize and float(np.sum(power)) > EPS:
            power = power / float(np.sum(power))
        keep = min(n_coeffs, len(power))
        parts.append(power[:keep])
        if keep < n_coeffs:
            parts.append(np.zeros(n_coeffs - keep, dtype=float))
    return np.concatenate(parts).astype(float)


def periodogram_distance(x: Any, y: Any, *, n_coeffs: int = 32) -> float:
    left, right, _, _ = _pair_series(x, y)
    if len(left) == 0 or len(right) == 0:
        return float("nan")
    ex = _periodogram_embedding(left, n_coeffs=n_coeffs, normalize=True)
    ey = _periodogram_embedding(right, n_coeffs=n_coeffs, normalize=True)
    return float(np.linalg.norm(ex - ey))


def _trend_feature_vector(x: np.ndarray) -> np.ndarray:
    t = np.arange(len(x), dtype=float)
    feats = []
    for dim in range(x.shape[1]):
        values = x[:, dim]
        if len(values) < 2:
            feats.extend([float(values[0]) if len(values) else 0.0, 0.0, 0.0])
            continue
        slope, intercept = np.polyfit(t, values, 1)
        pred = slope * t + intercept
        feats.extend([float(intercept), float(slope), float(np.std(values - pred))])
    return np.asarray(feats, dtype=float)


def trend_distance(x: Any, y: Any) -> float:
    left, right, _, _ = _pair_series(x, y)
    if len(left) == 0 or len(right) == 0:
        return float("nan")
    return float(np.linalg.norm(_trend_feature_vector(left) - _trend_feature_vector(right)))


def _ordinal_pattern_distribution(x: Any, *, order: int = 3, delay: int = 1) -> np.ndarray:
    values = _to_univariate_series(x)
    if order < 2 or delay < 1:
        raise ValueError("order must be >= 2 and delay must be >= 1.")
    n_vectors = len(values) - (order - 1) * delay
    patterns = list(permutations(range(order)))
    index = {pattern: idx for idx, pattern in enumerate(patterns)}
    counts = np.zeros(len(patterns), dtype=float)
    if n_vectors <= 0:
        return counts
    for idx in range(n_vectors):
        window = values[idx : idx + order * delay : delay]
        pattern = tuple(np.argsort(window, kind="mergesort"))
        counts[index[pattern]] += 1.0
    if float(np.sum(counts)) > EPS:
        counts = counts / float(np.sum(counts))
    return counts


def _jensen_shannon_distance(p: np.ndarray, q: np.ndarray) -> float:
    if p.shape != q.shape:
        raise ValueError("Jensen-Shannon distance requires equal-length vectors.")
    if np.any(p < 0) or np.any(q < 0):
        raise ValueError("Jensen-Shannon distance requires nonnegative inputs.")
    px = p / float(np.sum(p) if float(np.sum(p)) > EPS else 1.0)
    py = q / float(np.sum(q) if float(np.sum(q)) > EPS else 1.0)
    m = 0.5 * (px + py)
    def _kl(a: np.ndarray, b: np.ndarray) -> float:
        mask = a > EPS
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))
    js_div = 0.5 * _kl(px, m) + 0.5 * _kl(py, m)
    return float(np.sqrt(max(js_div, 0.0)))


def ordinal_pattern_js_distance(x: Any, y: Any, *, order: int = 3, delay: int = 1) -> float:
    px = _ordinal_pattern_distribution(x, order=order, delay=delay)
    py = _ordinal_pattern_distribution(y, order=order, delay=delay)
    return _jensen_shannon_distance(px, py)


def _linear_trend_parameters(x: np.ndarray) -> np.ndarray:
    t = np.arange(len(x), dtype=float)
    if len(x) < 2:
        return np.array([float(x[0]) if len(x) else 0.0, 0.0, 0.0], dtype=float)
    slope, intercept = np.polyfit(t, x, 1)
    pred = slope * t + intercept
    resid = np.std(x - pred)
    return np.array([float(intercept), float(slope), float(resid)], dtype=float)


def linear_trend_model_distance(x: Any, y: Any) -> float:
    left = _to_univariate_series(x)
    right = _to_univariate_series(y)
    return float(np.linalg.norm(_linear_trend_parameters(left) - _linear_trend_parameters(right)))


def _window_bounds(i: int, m: int, window: int | None) -> tuple[int, int]:
    if window is None:
        return 1, m + 1
    return max(1, i - window), min(m, i + window) + 1


def _match(a: np.ndarray, b: np.ndarray, epsilon: float) -> bool:
    return _local_l2(a, b) <= epsilon


def lcss_similarity(x: Any, y: Any, *, epsilon: float = 1.0, window: int | None = None) -> float:
    left, right, _, _ = _pair_series(x, y)
    n, m = len(left), len(right)
    if n == 0 or m == 0:
        return float("nan")
    if window is not None:
        window = max(window, abs(n - m))
    D = np.zeros((n + 1, m + 1), dtype=float)
    for i in range(1, n + 1):
        j_start, j_end = _window_bounds(i, m, window)
        for j in range(j_start, j_end):
            if _match(left[i - 1], right[j - 1], epsilon):
                D[i, j] = D[i - 1, j - 1] + 1.0
            else:
                D[i, j] = max(D[i - 1, j], D[i, j - 1])
    return float(D[n, m] / max(1, min(n, m)))


def lcss_distance(x: Any, y: Any, *, epsilon: float = 1.0, window: int | None = None) -> float:
    similarity = lcss_similarity(x, y, epsilon=epsilon, window=window)
    if not np.isfinite(similarity):
        return float("nan")
    return float(1.0 - similarity)


def edr_distance(x: Any, y: Any, *, epsilon: float = 1.0, normalized: bool = True) -> float:
    left, right, _, _ = _pair_series(x, y)
    n, m = len(left), len(right)
    if n == 0 or m == 0:
        return float("nan")
    D = np.zeros((n + 1, m + 1), dtype=float)
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = 0.0 if _match(left[i - 1], right[j - 1], epsilon) else 1.0
            D[i, j] = min(D[i - 1, j] + 1.0, D[i, j - 1] + 1.0, D[i - 1, j - 1] + sub)
    value = float(D[n, m])
    if normalized:
        value /= max(1, max(n, m))
    return value


def erp_distance(x: Any, y: Any, *, gap_value: float | np.ndarray = 0.0) -> float:
    left, right, _, _ = _pair_series(x, y)
    n, m = len(left), len(right)
    if n == 0 or m == 0:
        return float("nan")
    gap = np.asarray(gap_value, dtype=float)
    if gap.ndim == 0:
        gap = np.full(left.shape[1], float(gap))
    if gap.shape != (left.shape[1],):
        raise ValueError(f"gap_value must broadcast to shape {(left.shape[1],)}.")
    D = np.full((n + 1, m + 1), np.inf, dtype=float)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        D[i, 0] = D[i - 1, 0] + _local_l2(left[i - 1], gap)
    for j in range(1, m + 1):
        D[0, j] = D[0, j - 1] + _local_l2(right[j - 1], gap)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(
                D[i - 1, j - 1] + _local_l2(left[i - 1], right[j - 1]),
                D[i - 1, j] + _local_l2(left[i - 1], gap),
                D[i, j - 1] + _local_l2(right[j - 1], gap),
            )
    return float(D[n, m])


def twed_distance(
    x: Any,
    y: Any,
    *,
    lambda_: float = 1.0,
    nu: float = 0.001,
    t_x: Any | None = None,
    t_y: Any | None = None,
) -> float:
    left, right, left_ts, right_ts = _pair_series(x, y, left_timestamps=t_x, right_timestamps=t_y)
    n, m = len(left), len(right)
    if n == 0 or m == 0:
        return float("nan")
    tx = np.arange(1, n + 1, dtype=float) if left_ts is None else np.asarray(left_ts, dtype=float).reshape(-1)
    ty = np.arange(1, m + 1, dtype=float) if right_ts is None else np.asarray(right_ts, dtype=float).reshape(-1)
    if tx.size != n or ty.size != m:
        raise ValueError("Timestamp arrays must match the cleaned series lengths.")
    zero = np.zeros(left.shape[1], dtype=float)
    D = np.full((n + 1, m + 1), np.inf, dtype=float)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        xi = left[i - 1]
        xim1 = left[i - 2] if i > 1 else zero
        ti = tx[i - 1]
        tim1 = tx[i - 2] if i > 1 else 0.0
        D[i, 0] = D[i - 1, 0] + _local_l2(xi, xim1) + nu * abs(ti - tim1) + lambda_
    for j in range(1, m + 1):
        yj = right[j - 1]
        yjm1 = right[j - 2] if j > 1 else zero
        tj = ty[j - 1]
        tjm1 = ty[j - 2] if j > 1 else 0.0
        D[0, j] = D[0, j - 1] + _local_l2(yj, yjm1) + nu * abs(tj - tjm1) + lambda_
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            xi = left[i - 1]
            yj = right[j - 1]
            xim1 = left[i - 2] if i > 1 else zero
            yjm1 = right[j - 2] if j > 1 else zero
            ti = tx[i - 1]
            tj = ty[j - 1]
            tim1 = tx[i - 2] if i > 1 else 0.0
            tjm1 = ty[j - 2] if j > 1 else 0.0
            delete_x = D[i - 1, j] + _local_l2(xi, xim1) + nu * abs(ti - tim1) + lambda_
            delete_y = D[i, j - 1] + _local_l2(yj, yjm1) + nu * abs(tj - tjm1) + lambda_
            match = (
                D[i - 1, j - 1]
                + _local_l2(xi, yj)
                + _local_l2(xim1, yjm1)
                + nu * (abs(ti - tj) + abs(tim1 - tjm1))
            )
            D[i, j] = min(delete_x, delete_y, match)
    return float(D[n, m])


__all__ = [
    "ncc_sequence",
    "max_ncc",
    "best_shift",
    "sbd",
    "independent_max_ncc",
    "independent_sbd",
    "acf_distance",
    "periodogram_distance",
    "trend_distance",
    "ordinal_pattern_js_distance",
    "linear_trend_model_distance",
    "lcss_similarity",
    "lcss_distance",
    "edr_distance",
    "erp_distance",
    "twed_distance",
]
