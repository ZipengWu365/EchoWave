from __future__ import annotations

import importlib

import numpy as np

from tsontology import (
    acf_distance,
    best_shift,
    edr_distance,
    erp_distance,
    independent_max_ncc,
    independent_sbd,
    lcss_distance,
    lcss_similarity,
    linear_trend_model_distance,
    max_ncc,
    ncc_sequence,
    ordinal_pattern_js_distance,
    periodogram_distance,
    sbd,
    trend_distance,
    twed_distance,
)


def _base_series() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = np.sin(np.linspace(0.0, 4.0 * np.pi, 64))
    shifted = np.roll(x, 5)
    noisy = x + 0.05 * np.sin(np.linspace(0.0, 16.0 * np.pi, 64))
    different = np.cos(np.linspace(0.0, 4.0 * np.pi, 64))
    return x, shifted, noisy, different


def test_shift_aware_similarity_methods_behave_monotonically() -> None:
    x, shifted, _, different = _base_series()

    values, lags = ncc_sequence(x, shifted)

    assert values.shape == lags.shape
    assert values.size == 127
    assert max_ncc(x, shifted) > 0.95
    assert best_shift(x, shifted) == -5
    assert sbd(x, shifted) < sbd(x, different)


def test_acf_distance_prefers_matching_rhythm() -> None:
    x, _, noisy, _ = _base_series()
    faster = np.sin(np.linspace(0.0, 8.0 * np.pi, 64))

    assert acf_distance(x, noisy, max_lag=12) < acf_distance(x, faster, max_lag=12)


def test_independent_shift_aware_methods_handle_multichannel_inputs() -> None:
    x, shifted, _, different = _base_series()
    multi_x = np.column_stack([x, np.roll(x, 2)])
    multi_shifted = np.column_stack([shifted, np.roll(shifted, 2)])
    multi_different = np.column_stack([different, np.roll(different, 2)])

    assert independent_max_ncc(multi_x, multi_shifted) > independent_max_ncc(multi_x, multi_different)
    assert independent_sbd(multi_x, multi_shifted) < independent_sbd(multi_x, multi_different)


def test_elastic_and_partial_match_methods_rank_similar_series_lower() -> None:
    x, _, noisy, different = _base_series()

    assert lcss_similarity(x, noisy, epsilon=0.15) > lcss_similarity(x, different, epsilon=0.15)
    assert lcss_distance(x, noisy, epsilon=0.15) < lcss_distance(x, different, epsilon=0.15)
    assert edr_distance(x, noisy, epsilon=0.15) < edr_distance(x, different, epsilon=0.15)
    assert erp_distance(x, noisy) < erp_distance(x, different)
    assert twed_distance(x, noisy) < twed_distance(x, different)


def test_periodogram_and_trend_distances_prefer_structurally_closer_series() -> None:
    x, _, noisy, different = _base_series()
    faster = np.sin(np.linspace(0.0, 8.0 * np.pi, 64))
    drifted = 0.8 * x + np.linspace(0.0, 0.8, x.size)

    assert periodogram_distance(x, noisy) < periodogram_distance(x, faster)
    assert trend_distance(x, noisy) < trend_distance(x, drifted)


def test_symbolic_and_trend_model_distances_run_as_public_apis() -> None:
    x, _, _, different = _base_series()
    x_step = np.concatenate([np.zeros(32), np.ones(32)])
    y_step = np.concatenate([np.zeros(28), np.ones(36)])
    x_trend = np.linspace(0.0, 1.0, 64)
    y_trend = np.linspace(0.1, 1.1, 64)
    z_trend = np.sin(np.linspace(0.0, 4.0 * np.pi, 64))

    assert ordinal_pattern_js_distance(x_step, y_step) < ordinal_pattern_js_distance(x_step, different)
    assert linear_trend_model_distance(x_trend, y_trend) < linear_trend_model_distance(x_trend, z_trend)


def test_tsontology_compat_shim_exposes_new_similarity_modules() -> None:
    atlas_module = importlib.import_module("tsontology.similarity_method_atlas")
    methods_module = importlib.import_module("tsontology.similarity_methods")

    assert hasattr(atlas_module, "similarity_method_atlas_dict")
    assert hasattr(methods_module, "twed_distance")
