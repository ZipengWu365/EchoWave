"""Reference atlas for time-series similarity methods and EchoWave fit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

GuideFormat = Literal["markdown", "dict"]


@dataclass(frozen=True, slots=True)
class EchoWaveNativeMethod:
    name: str
    family: str
    kind: str
    formula: str
    notes: str


@dataclass(frozen=True, slots=True)
class ExtractedMethod:
    name: str
    family: str
    kind: str
    metric: str
    formula: str
    notes: str
    echowave_status: str
    echowave_rationale: str


_FAMILY_ORDER = (
    "lock-step",
    "sliding",
    "elastic",
    "kernel",
    "feature-based",
    "model-based",
    "embedding-based",
)

_FAMILY_DESCRIPTIONS = {
    "lock-step": "Pointwise comparison on an already aligned timeline.",
    "sliding": "Shift-aware comparison under pure translation or lead-lag offsets.",
    "elastic": "Dynamic-programming alignments that allow local stretching or compression.",
    "kernel": "Similarity through kernel scores rather than direct distances.",
    "feature-based": "Compare derived features instead of raw waveforms.",
    "model-based": "Compare fitted dynamics or transition structure.",
    "embedding-based": "Encode first, then compare in a latent or compressed space.",
}

_DEFAULT_STATUS_BY_FAMILY = {
    "lock-step": (
        "Low-priority addition",
        "EchoWave already exposes familiar pointwise statistics, so adding more lock-step baselines is usually duplication rather than product leverage.",
    ),
    "sliding": (
        "High-fit addition",
        "Shift-aware comparisons fit EchoWave's compare-first story and are still easy to explain in reports.",
    ),
    "elastic": (
        "Possible addition",
        "Elastic methods are a strong thematic fit, but EchoWave should only add the variants that stay explainable for non-specialists.",
    ),
    "kernel": (
        "Low-priority addition",
        "Kernel scores can be useful downstream, but they are less legible than report-friendly distances or similarities.",
    ),
    "feature-based": (
        "Possible addition",
        "Feature-space methods can strengthen explainability when the representation itself is explicit and stable.",
    ),
    "model-based": (
        "Possible addition",
        "Model-based distances can be valuable for advanced users, but they depend on stronger modeling assumptions than EchoWave's current default surface.",
    ),
    "embedding-based": (
        "Low-priority addition",
        "Generic encoder adapters are flexible, but they are too open-ended for EchoWave's default public surface.",
    ),
}

_IMPLEMENTED_EXTRACTED_METHODS = {
    "max_ncc",
    "sbd",
    "acf_distance",
    "lcss_similarity",
    "lcss_distance",
    "edr",
    "erp",
    "twed",
}

_STATUS_OVERRIDES = {
    "pearson_similarity": (
        "Conceptually covered",
        "EchoWave already surfaces Pearson r directly as a familiar reference metric.",
    ),
    "pearson_distance": (
        "Conceptually covered",
        "EchoWave already exposes Pearson r, so the distance transform is trivial and does not need a separate public method.",
    ),
    "dtw": (
        "Conceptually covered",
        "EchoWave already reports a DTW-based similarity component.",
    ),
    "ddtw": (
        "Conceptually covered",
        "EchoWave's DTW similarity already mixes in derivative-space warping.",
    ),
    "spectral_cosine_similarity": (
        "Conceptually covered",
        "EchoWave already includes a spectral similarity component, although the current formula blends spectral JS overlap with structural correlation.",
    ),
    "max_ncc": (
        "High-fit addition",
        "Explicit shift-invariant similarity would strengthen EchoWave's story around phase offsets and lead-lag comparisons.",
    ),
    "sbd": (
        "High-fit addition",
        "SBD pairs naturally with EchoWave's shape language and gives a clean, reportable shift-aware distance.",
    ),
    "twed": (
        "High-fit addition",
        "EchoWave already cares about timestamps and irregular sampling; TWED is the cleanest timestamp-aware elastic addition.",
    ),
    "erp": (
        "High-fit addition",
        "ERP adds a metric elastic distance with explicit gap semantics that can still be explained clearly in a report.",
    ),
    "lcss_similarity": (
        "High-fit addition",
        "LCSS adds a robust partial-match view that is useful when noisy sections or missing peaks should not dominate the verdict.",
    ),
    "lcss_distance": (
        "High-fit addition",
        "The distance form of LCSS would complement the similarity form for retrieval and thresholding workflows.",
    ),
    "edr": (
        "High-fit addition",
        "EDR gives EchoWave a robust edit-style distance for noisy or threshold-based analog search.",
    ),
    "acf_distance": (
        "High-fit addition",
        "Autocorrelation-pattern distance would complement EchoWave's existing spectral view with a directly interpretable rhythm comparison.",
    ),
    "cdtw": (
        "Possible addition",
        "A constrained DTW variant could improve stability and speed without changing the overall mental model.",
    ),
    "wdtw": (
        "Possible addition",
        "Weighted DTW is useful when large phase shifts should be penalized more explicitly than in plain DTW.",
    ),
    "soft_dtw": (
        "Possible addition",
        "Soft-DTW matters if EchoWave wants differentiable training-time hooks, but it is less important for the current report-first product surface.",
    ),
    "soft_dtw_divergence": (
        "Possible addition",
        "The divergence form is cleaner than raw soft-DTW if EchoWave later adds learning-oriented or optimization-aware workflows.",
    ),
    "stats_distance": (
        "Possible addition",
        "A small explicit feature vector could help dataset-to-dataset summaries without turning EchoWave into a metric zoo.",
    ),
    "paa_distance": (
        "Possible addition",
        "PAA offers cheap coarse-shape comparison for previews, clustering, and fast approximate search.",
    ),
    "jensen_shannon": (
        "Possible addition",
        "Jensen-Shannon distance is already used inside EchoWave's spectral machinery and could be exposed for normalized-distribution views when needed.",
    ),
    "cosine_similarity": (
        "Possible addition",
        "Cosine similarity is familiar and cheap, but it overlaps with EchoWave's existing z-scored shape and correlation story.",
    ),
    "cosine_distance": (
        "Possible addition",
        "The cosine distance transform is simple, but it is only worth adding if EchoWave wants a clearer vector-baseline panel.",
    ),
    "ar_distance": (
        "Possible addition",
        "AR-parameter distance could fit EchoWave's structural language if framed as a lightweight generative summary rather than a forecasting engine.",
    ),
    "markov_distance": (
        "Possible addition",
        "Transition-matrix distance could be useful for discretized behavioral or event-state sequences, but it is more specialized than EchoWave's default story.",
    ),
}

_NATIVE_METHODS = (
    EchoWaveNativeMethod(
        name="shape_similarity",
        family="EchoWave native component",
        kind="similarity",
        formula="s_shape = GM(clip(r(x,y), 0, 1), clip(r(Delta x, Delta y), 0, 1))",
        notes="Combines level correlation with first-difference correlation so the headline match does not ignore local dynamics.",
    ),
    EchoWaveNativeMethod(
        name="dtw_similarity",
        family="EchoWave native component",
        kind="similarity",
        formula="s_dtw = GM(exp(-DTW_w(x,y)/0.45), exp(-DTW_w(Delta x, Delta y)/0.35))",
        notes="Turns constrained DTW distances into a similarity score and blends level-space and derivative-space warping.",
    ),
    EchoWaveNativeMethod(
        name="trend_similarity",
        family="EchoWave native component",
        kind="similarity",
        formula="s_trend = GM(clip(r(T(x), T(y)), 0, 1), clip(r(Delta T(x), Delta T(y)), 0, 1))",
        notes="Smooths both series first, then compares both the trend level and the trend slope.",
    ),
    EchoWaveNativeMethod(
        name="derivative_similarity",
        family="EchoWave native component",
        kind="similarity",
        formula="s_diff = clip(r(Delta x, Delta y), 0, 1)",
        notes="Focuses on whether local changes move together even when the levels differ.",
    ),
    EchoWaveNativeMethod(
        name="spectral_similarity",
        family="EchoWave native component",
        kind="similarity",
        formula="s_spec = GM(1 - JSD(P_x, P_y), clip(r(P_x - U, P_y - U), 0, 1))",
        notes="Compares normalized spectra of differenced series, mixing JS overlap with structural similarity relative to a uniform spectrum U.",
    ),
    EchoWaveNativeMethod(
        name="pearson_r",
        family="EchoWave reference metric",
        kind="similarity",
        formula="r(x,y) = sum_t (x_t - x_bar)(y_t - y_bar) / sqrt(sum_t (x_t - x_bar)^2 sum_t (y_t - y_bar)^2)",
        notes="Familiar linear correlation exposed directly in every raw-series similarity report.",
    ),
    EchoWaveNativeMethod(
        name="spearman_rho",
        family="EchoWave reference metric",
        kind="similarity",
        formula="rho(x,y) = corr(rank(x), rank(y))",
        notes="Rank-order correlation used as a robustness check against nonlinear monotone relationships.",
    ),
    EchoWaveNativeMethod(
        name="kendall_tau",
        family="EchoWave reference metric",
        kind="similarity",
        formula="tau(x,y) = (C - D) / choose(n, 2)",
        notes="Pairwise concordance measure that stays interpretable when rank ordering matters more than amplitude.",
    ),
    EchoWaveNativeMethod(
        name="best_lag_pearson_r",
        family="EchoWave reference metric",
        kind="similarity",
        formula="max_lag_r(x,y) = max_ell r(x_t, y_{t-ell})",
        notes="Searches over a bounded lag window to show whether a shift-aware linear relationship is stronger than the aligned one.",
    ),
    EchoWaveNativeMethod(
        name="normalized_mutual_information",
        family="EchoWave reference metric",
        kind="similarity",
        formula="NMI(X,Y) = I(X;Y) / sqrt(H(X) H(Y))",
        notes="Histogram-based nonlinear dependence score used as a familiar cross-check against linear metrics.",
    ),
)

_EXTRACTED_METHODS_RAW = (
    ("euclidean", "lock-step", "distance", "yes", r"$d(x,y)=\sqrt{\sum_t \|x_t-y_t\|_2^2}$", "Equal-length, pointwise aligned baseline."),
    ("squared_euclidean", "lock-step", "distance", "no", r"$d(x,y)=\sum_t \|x_t-y_t\|_2^2$", "Useful as a loss; not a strict metric."),
    ("manhattan", "lock-step", "distance", "yes", r"$d(x,y)=\sum_t \|x_t-y_t\|_1$", "More robust to outliers than Euclidean in some settings."),
    ("minkowski", "lock-step", "distance", "yes (p>=1)", r"$d_p(x,y)=(\sum_t \|x_t-y_t\|_p^p)^{1/p}$", "Generalizes Manhattan and Euclidean."),
    ("chebyshev", "lock-step", "distance", "yes", r"$d(x,y)=\max_t \|x_t-y_t\|_\infty$", "Focuses on the largest deviation."),
    ("canberra", "lock-step", "distance", "yes", r"$d(x,y)=\sum_t \frac{|x_t-y_t|}{|x_t|+|y_t|}$", "Sensitive near zero."),
    ("lorentzian", "lock-step", "distance", "not guaranteed", r"$d(x,y)=\sum_t \log(1+|x_t-y_t|)$", "Compresses large deviations logarithmically."),
    ("cosine_similarity", "lock-step", "similarity", "no", r"$s(x,y)=\frac{\langle x,y \rangle}{\|x\|_2\|y\|_2}$", "Measures directional similarity."),
    ("cosine_distance", "lock-step", "distance-like", "no", r"$d(x,y)=1-s_{cos}(x,y)$", "Monotone transform of cosine similarity."),
    ("pearson_similarity", "lock-step", "similarity", "no", r"$r(x,y)=\frac{\sum_t (x_t-\bar x)(y_t-\bar y)}{\sqrt{\sum_t (x_t-\bar x)^2}\sqrt{\sum_t (y_t-\bar y)^2}}$", "Captures linear correlation after centering."),
    ("pearson_distance", "lock-step", "distance-like", "no", r"$d(x,y)=1-r(x,y)$", "Distance-like transform of Pearson correlation."),
    ("jensen_shannon", "lock-step", "distance", "yes", r"$JSD(P,Q)=\sqrt{\tfrac{1}{2}KL(P\|M)+\tfrac{1}{2}KL(Q\|M)},\ M=\tfrac{P+Q}{2}$", "Requires nonnegative inputs interpreted as distributions."),
    ("max_ncc", "sliding", "similarity", "no", r"$s(x,y)=\max_\ell NCC(x,shift(y,\ell))$", "Shift-invariant similarity via cross-correlation."),
    ("sbd", "sliding", "distance-like", "no", r"$d(x,y)=1-\max_\ell NCC(x,shift(y,\ell))$", "Shape-based distance from k-Shape."),
    ("dtw", "elastic", "distance", "no", r"$DTW(x,y)=\sqrt{\min_{\pi} \sum_{(i,j)\in\pi} \|x_i-y_j\|_2^2}$", "Optimal nonlinear alignment."),
    ("cdtw", "elastic", "distance", "no", r"$cDTW=DTW$ with a Sakoe-Chiba window $|i-j|\le w$", "Constrains unrealistic warps."),
    ("wdtw", "elastic", "distance", "no", r"$WDTW(x,y)=\sqrt{\min_{\pi} \sum_{(i,j)\in\pi} w(|i-j|)\|x_i-y_j\|_2^2}$", "Penalizes large phase differences through a logistic weight."),
    ("ddtw", "elastic", "distance", "no", r"$DDTW(x,y)=DTW(\Delta x,\Delta y)$", "Applies DTW to derivative-transformed series for shape emphasis."),
    ("soft_dtw", "elastic", "soft distance / loss", "no", r"$SoftDTW_\gamma(x,y)=softmin_\gamma(\mathrm{all\ alignment\ costs})$", "Differentiable smoothing of DTW."),
    ("soft_dtw_divergence", "elastic", "divergence", "no", r"$D_\gamma(x,y)=SoftDTW(x,y)-\tfrac12 SoftDTW(x,x)-\tfrac12 SoftDTW(y,y)$", "Nonnegative divergence induced by soft-DTW."),
    ("lcss_similarity", "elastic", "similarity", "no", r"$LCSS(x,y)=\frac{1}{\min(n,m)}\max \#\{(i,j): \|x_i-y_j\|\le \epsilon\}$ under order constraints", "Robust to noise and outliers through thresholded matching."),
    ("lcss_distance", "elastic", "distance-like", "no", r"$d(x,y)=1-LCSS(x,y)$", "Distance-like transform of LCSS similarity."),
    ("edr", "elastic", "distance", "no", r"$EDR$ uses edit distance with substitution cost $0/1$ depending on $\|x_i-y_j\|\le\epsilon$", "Thresholded edit distance on real sequences."),
    ("swale_similarity", "elastic", "similarity", "no", r"$SWALE$ maximizes reward for matches and subtracts penalties for gaps.", "A reward-penalty view of threshold-based alignment."),
    ("erp", "elastic", "distance", "yes", r"$ERP$ uses edit distance with a real-valued gap $g$: diagonal $\|x_i-y_j\|$, gaps $\|x_i-g\|$ or $\|y_j-g\|$", "A metric elastic measure."),
    ("msm", "elastic", "distance", "yes", r"$MSM$ is the minimum cost of move, split, and merge operations.", "The current implementation is univariate."),
    ("twed", "elastic", "distance", "yes", r"$TWED$ combines edit operations, point distances, timestamps, stiffness $\nu$, and penalty $\lambda$.", "Suitable when timestamps carry meaning."),
    ("rbf_kernel", "kernel", "kernel similarity", "n/a", r"$K(x,y)=\exp(-\gamma \|x-y\|_2^2)$", "Kernelized similarity on equal-length vectors."),
    ("gak", "kernel", "kernel similarity", "n/a", r"$GAK(x,y)=\sum_{\pi\in A} \prod_{(i,j)\in\pi} k(x_i,y_j)$", "Sums over all alignments instead of only the best one."),
    ("lgak", "kernel", "kernel score", "n/a", r"$LGAK(x,y)=\log(GAK(x,y)+\epsilon)$", "Log-transformed global alignment kernel."),
    ("weighted_ncc_kernel", "kernel", "kernel similarity", "n/a", r"$K(x,y)=\sum_\ell w(\ell)NCC_\ell(x,y)$", "Practical shift-aware kernel adapter built on NCC."),
    ("stats_distance", "feature-based", "distance", "yes", r"$d(x,y)=\|\phi_{stats}(x)-\phi_{stats}(y)\|_2$", "Compares handcrafted statistical feature vectors."),
    ("acf_distance", "feature-based", "distance", "yes", r"$d(x,y)=\|ACF_L(x)-ACF_L(y)\|_2$", "Autocorrelation-pattern distance."),
    ("spectral_cosine_similarity", "feature-based", "similarity", "no", r"$s(x,y)=cos(|FFT(x)|,|FFT(y)|)$", "Frequency-domain similarity."),
    ("spectral_distance", "feature-based", "distance-like", "no", r"$d(x,y)=1-s_{spectral}(x,y)$", "Distance-like transform of spectral cosine similarity."),
    ("paa_distance", "feature-based", "distance", "yes", r"$d(x,y)=\|PAA_s(x)-PAA_s(y)\|_2$", "Piecewise aggregate approximation distance."),
    ("ar_distance", "model-based", "distance", "yes", r"$d(x,y)=\|[c_x,\phi_x]-[c_y,\phi_y]\|_2$ after AR(p) fitting", "Compares fitted autoregressive parameters."),
    ("markov_distance", "model-based", "distance", "yes", r"$d(x,y)=\|P_x-P_y\|_F$ after discretized Markov modeling", "Compares transition dynamics rather than raw points."),
    ("embedding_distance", "embedding-based", "distance", "depends on encoder + metric", r"$z_x=Enc(x),\; z_y=Enc(y),\; d(x,y)=dist(z_x,z_y)$", "Generic adapter for PAA/DFT/stats/random-projection/custom encoders."),
    ("embedding_similarity", "embedding-based", "similarity", "depends on encoder + metric", r"$s(x,y)=sim(Enc(x),Enc(y))$", "Generic similarity on latent or compressed representations."),
)


def _status_for(name: str, family: str) -> tuple[str, str]:
    if name in _IMPLEMENTED_EXTRACTED_METHODS:
        return (
            "Implemented in EchoWave",
            "This method is now available as a public low-level EchoWave similarity function.",
        )
    if name in _STATUS_OVERRIDES:
        return _STATUS_OVERRIDES[name]
    return _DEFAULT_STATUS_BY_FAMILY[family]


def native_similarity_methods() -> list[dict[str, str]]:
    return [asdict(row) for row in _NATIVE_METHODS]


def extracted_similarity_methods() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name, family, kind, metric, formula, notes in _EXTRACTED_METHODS_RAW:
        status, rationale = _status_for(name, family)
        rows.append(
            asdict(
                ExtractedMethod(
                    name=name,
                    family=family,
                    kind=kind,
                    metric=metric,
                    formula=formula,
                    notes=notes,
                    echowave_status=status,
                    echowave_rationale=rationale,
                )
            )
        )
    return rows


def similarity_method_atlas_dict() -> dict[str, object]:
    extracted = extracted_similarity_methods()
    native = native_similarity_methods()
    by_family = {
        family: [row for row in extracted if row["family"] == family]
        for family in _FAMILY_ORDER
    }
    status_order = {
        "Implemented in EchoWave": 0,
        "High-fit addition": 1,
        "Conceptually covered": 2,
        "Possible addition": 3,
        "Low-priority addition": 4,
    }
    recommended = sorted(
        [row for row in extracted if row["echowave_status"] in {"Implemented in EchoWave", "High-fit addition", "Possible addition"}],
        key=lambda row: (status_order[row["echowave_status"]], _FAMILY_ORDER.index(row["family"]), row["name"]),
    )
    counts_by_status: dict[str, int] = {}
    for row in extracted:
        counts_by_status[row["echowave_status"]] = counts_by_status.get(row["echowave_status"], 0) + 1
    return {
        "summary": {
            "native_method_count": len(native),
            "extracted_method_count": len(extracted),
            "family_count": len(_FAMILY_ORDER),
            "family_descriptions": dict(_FAMILY_DESCRIPTIONS),
            "counts_by_status": counts_by_status,
        },
        "native_methods": native,
        "recommended_additions": recommended,
        "families": [
            {
                "name": family,
                "description": _FAMILY_DESCRIPTIONS[family],
                "entries": by_family[family],
            }
            for family in _FAMILY_ORDER
        ],
    }


def _md_cell(text: str) -> str:
    return str(text).replace("|", r"\|")


def similarity_method_atlas_guide(*, format: GuideFormat = "markdown") -> str | dict:
    payload = similarity_method_atlas_dict()
    if format == "dict":
        return payload

    lines = [
        "# EchoWave similarity method atlas",
        "",
        "This guide audits EchoWave's current raw-series similarity stack, extracts the method inventory from `ts_similarity_package`, and marks which methods fit EchoWave's product direction.",
        "",
        "## Current EchoWave comparison layer",
        "",
    ]
    for entry in payload["native_methods"]:  # type: ignore[index]
        lines.extend(
            [
                f"### {entry['name']}",
                "",
                f"- family: {entry['family']}",
                f"- kind: {entry['kind']}",
                f"- formula: `{entry['formula']}`",
                f"- note: {entry['notes']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Implemented and recommended additions from ts_similarity_package",
            "",
            "| method | family | EchoWave fit | formula | why it matters |",
            "|---|---|---|---|---|",
        ]
    )
    for entry in payload["recommended_additions"]:  # type: ignore[index]
        lines.append(
            f"| {entry['name']} | {entry['family']} | {entry['echowave_status']} | `{_md_cell(entry['formula'])}` | {_md_cell(entry['echowave_rationale'])} |"
        )

    lines.extend(["", "## Full extracted atlas", ""])
    for family in payload["families"]:  # type: ignore[index]
        lines.extend(
            [
                f"### {family['name']}",
                "",
                family["description"],
                "",
                "| method | output | metric | EchoWave fit | formula | note |",
                "|---|---|---|---|---|---|",
            ]
        )
        for entry in family["entries"]:
            lines.append(
                f"| {entry['name']} | {entry['kind']} | {entry['metric']} | {entry['echowave_status']} | `{_md_cell(entry['formula'])}` | {_md_cell(entry['notes'])} |"
            )
        lines.append("")

    return "\n".join(lines)


__all__ = [
    "native_similarity_methods",
    "extracted_similarity_methods",
    "similarity_method_atlas_dict",
    "similarity_method_atlas_guide",
]
