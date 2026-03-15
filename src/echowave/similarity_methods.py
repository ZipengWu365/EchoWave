"""Low-level similarity methods that complement EchoWave's report surface."""

from __future__ import annotations

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
    "acf_distance",
    "lcss_similarity",
    "lcss_distance",
    "edr_distance",
    "erp_distance",
    "twed_distance",
]
