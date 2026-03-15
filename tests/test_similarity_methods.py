from __future__ import annotations

import importlib

import numpy as np

from tsontology import (
    acf_distance,
    best_shift,
    edr_distance,
    erp_distance,
    lcss_distance,
    lcss_similarity,
    max_ncc,
    ncc_sequence,
    sbd,
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


def test_elastic_and_partial_match_methods_rank_similar_series_lower() -> None:
    x, _, noisy, different = _base_series()

    assert lcss_similarity(x, noisy, epsilon=0.15) > lcss_similarity(x, different, epsilon=0.15)
    assert lcss_distance(x, noisy, epsilon=0.15) < lcss_distance(x, different, epsilon=0.15)
    assert edr_distance(x, noisy, epsilon=0.15) < edr_distance(x, different, epsilon=0.15)
    assert erp_distance(x, noisy) < erp_distance(x, different)
    assert twed_distance(x, noisy) < twed_distance(x, different)


def test_tsontology_compat_shim_exposes_new_similarity_modules() -> None:
    atlas_module = importlib.import_module("tsontology.similarity_method_atlas")
    methods_module = importlib.import_module("tsontology.similarity_methods")

    assert hasattr(atlas_module, "similarity_method_atlas_dict")
    assert hasattr(methods_module, "twed_distance")
