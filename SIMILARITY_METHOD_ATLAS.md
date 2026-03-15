# EchoWave similarity method atlas

This guide audits EchoWave's current raw-series similarity stack, extracts the method inventory from `ts_similarity_package`, and marks which methods fit EchoWave's product direction.

## Current EchoWave comparison layer

### shape_similarity

- family: EchoWave native component
- kind: similarity
- formula: `s_shape = GM(clip(r(x,y), 0, 1), clip(r(Delta x, Delta y), 0, 1))`
- note: Combines level correlation with first-difference correlation so the headline match does not ignore local dynamics.

### dtw_similarity

- family: EchoWave native component
- kind: similarity
- formula: `s_dtw = GM(exp(-DTW_w(x,y)/0.45), exp(-DTW_w(Delta x, Delta y)/0.35))`
- note: Turns constrained DTW distances into a similarity score and blends level-space and derivative-space warping.

### trend_similarity

- family: EchoWave native component
- kind: similarity
- formula: `s_trend = GM(clip(r(T(x), T(y)), 0, 1), clip(r(Delta T(x), Delta T(y)), 0, 1))`
- note: Smooths both series first, then compares both the trend level and the trend slope.

### derivative_similarity

- family: EchoWave native component
- kind: similarity
- formula: `s_diff = clip(r(Delta x, Delta y), 0, 1)`
- note: Focuses on whether local changes move together even when the levels differ.

### spectral_similarity

- family: EchoWave native component
- kind: similarity
- formula: `s_spec = GM(1 - JSD(P_x, P_y), clip(r(P_x - U, P_y - U), 0, 1))`
- note: Compares normalized spectra of differenced series, mixing JS overlap with structural similarity relative to a uniform spectrum U.

### pearson_r

- family: EchoWave reference metric
- kind: similarity
- formula: `r(x,y) = sum_t (x_t - x_bar)(y_t - y_bar) / sqrt(sum_t (x_t - x_bar)^2 sum_t (y_t - y_bar)^2)`
- note: Familiar linear correlation exposed directly in every raw-series similarity report.

### spearman_rho

- family: EchoWave reference metric
- kind: similarity
- formula: `rho(x,y) = corr(rank(x), rank(y))`
- note: Rank-order correlation used as a robustness check against nonlinear monotone relationships.

### kendall_tau

- family: EchoWave reference metric
- kind: similarity
- formula: `tau(x,y) = (C - D) / choose(n, 2)`
- note: Pairwise concordance measure that stays interpretable when rank ordering matters more than amplitude.

### best_lag_pearson_r

- family: EchoWave reference metric
- kind: similarity
- formula: `max_lag_r(x,y) = max_ell r(x_t, y_{t-ell})`
- note: Searches over a bounded lag window to show whether a shift-aware linear relationship is stronger than the aligned one.

### normalized_mutual_information

- family: EchoWave reference metric
- kind: similarity
- formula: `NMI(X,Y) = I(X;Y) / sqrt(H(X) H(Y))`
- note: Histogram-based nonlinear dependence score used as a familiar cross-check against linear metrics.

## Implemented and recommended additions from ts_similarity_package

| method | family | EchoWave fit | formula | why it matters |
|---|---|---|---|---|
| max_ncc | sliding | Implemented in EchoWave | `$s(x,y)=\max_\ell NCC(x,shift(y,\ell))$` | This method is now available as a public low-level EchoWave similarity function. |
| sbd | sliding | Implemented in EchoWave | `$d(x,y)=1-\max_\ell NCC(x,shift(y,\ell))$` | This method is now available as a public low-level EchoWave similarity function. |
| edr | elastic | Implemented in EchoWave | `$EDR$ uses edit distance with substitution cost $0/1$ depending on $\\|x_i-y_j\\|\le\epsilon$` | This method is now available as a public low-level EchoWave similarity function. |
| erp | elastic | Implemented in EchoWave | `$ERP$ uses edit distance with a real-valued gap $g$: diagonal $\\|x_i-y_j\\|$, gaps $\\|x_i-g\\|$ or $\\|y_j-g\\|$` | This method is now available as a public low-level EchoWave similarity function. |
| lcss_distance | elastic | Implemented in EchoWave | `$d(x,y)=1-LCSS(x,y)$` | This method is now available as a public low-level EchoWave similarity function. |
| lcss_similarity | elastic | Implemented in EchoWave | `$LCSS(x,y)=\frac{1}{\min(n,m)}\max \#\{(i,j): \\|x_i-y_j\\|\le \epsilon\}$ under order constraints` | This method is now available as a public low-level EchoWave similarity function. |
| twed | elastic | Implemented in EchoWave | `$TWED$ combines edit operations, point distances, timestamps, stiffness $\nu$, and penalty $\lambda$.` | This method is now available as a public low-level EchoWave similarity function. |
| acf_distance | feature-based | Implemented in EchoWave | `$d(x,y)=\\|ACF_L(x)-ACF_L(y)\\|_2$` | This method is now available as a public low-level EchoWave similarity function. |
| cosine_distance | lock-step | Possible addition | `$d(x,y)=1-s_{cos}(x,y)$` | The cosine distance transform is simple, but it is only worth adding if EchoWave wants a clearer vector-baseline panel. |
| cosine_similarity | lock-step | Possible addition | `$s(x,y)=\frac{\langle x,y \rangle}{\\|x\\|_2\\|y\\|_2}$` | Cosine similarity is familiar and cheap, but it overlaps with EchoWave's existing z-scored shape and correlation story. |
| jensen_shannon | lock-step | Possible addition | `$JSD(P,Q)=\sqrt{\tfrac{1}{2}KL(P\\|M)+\tfrac{1}{2}KL(Q\\|M)},\ M=\tfrac{P+Q}{2}$` | Jensen-Shannon distance is already used inside EchoWave's spectral machinery and could be exposed for normalized-distribution views when needed. |
| cdtw | elastic | Possible addition | `$cDTW=DTW$ with a Sakoe-Chiba window $\|i-j\|\le w$` | A constrained DTW variant could improve stability and speed without changing the overall mental model. |
| msm | elastic | Possible addition | `$MSM$ is the minimum cost of move, split, and merge operations.` | Elastic methods are a strong thematic fit, but EchoWave should only add the variants that stay explainable for non-specialists. |
| soft_dtw | elastic | Possible addition | `$SoftDTW_\gamma(x,y)=softmin_\gamma(\mathrm{all\ alignment\ costs})$` | Soft-DTW matters if EchoWave wants differentiable training-time hooks, but it is less important for the current report-first product surface. |
| soft_dtw_divergence | elastic | Possible addition | `$D_\gamma(x,y)=SoftDTW(x,y)-\tfrac12 SoftDTW(x,x)-\tfrac12 SoftDTW(y,y)$` | The divergence form is cleaner than raw soft-DTW if EchoWave later adds learning-oriented or optimization-aware workflows. |
| swale_similarity | elastic | Possible addition | `$SWALE$ maximizes reward for matches and subtracts penalties for gaps.` | Elastic methods are a strong thematic fit, but EchoWave should only add the variants that stay explainable for non-specialists. |
| wdtw | elastic | Possible addition | `$WDTW(x,y)=\sqrt{\min_{\pi} \sum_{(i,j)\in\pi} w(\|i-j\|)\\|x_i-y_j\\|_2^2}$` | Weighted DTW is useful when large phase shifts should be penalized more explicitly than in plain DTW. |
| paa_distance | feature-based | Possible addition | `$d(x,y)=\\|PAA_s(x)-PAA_s(y)\\|_2$` | PAA offers cheap coarse-shape comparison for previews, clustering, and fast approximate search. |
| spectral_distance | feature-based | Possible addition | `$d(x,y)=1-s_{spectral}(x,y)$` | Feature-space methods can strengthen explainability when the representation itself is explicit and stable. |
| stats_distance | feature-based | Possible addition | `$d(x,y)=\\|\phi_{stats}(x)-\phi_{stats}(y)\\|_2$` | A small explicit feature vector could help dataset-to-dataset summaries without turning EchoWave into a metric zoo. |
| ar_distance | model-based | Possible addition | `$d(x,y)=\\|[c_x,\phi_x]-[c_y,\phi_y]\\|_2$ after AR(p) fitting` | AR-parameter distance could fit EchoWave's structural language if framed as a lightweight generative summary rather than a forecasting engine. |
| markov_distance | model-based | Possible addition | `$d(x,y)=\\|P_x-P_y\\|_F$ after discretized Markov modeling` | Transition-matrix distance could be useful for discretized behavioral or event-state sequences, but it is more specialized than EchoWave's default story. |

## Full extracted atlas

### lock-step

Pointwise comparison on an already aligned timeline.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| euclidean | distance | yes | Low-priority addition | `$d(x,y)=\sqrt{\sum_t \\|x_t-y_t\\|_2^2}$` | Equal-length, pointwise aligned baseline. |
| squared_euclidean | distance | no | Low-priority addition | `$d(x,y)=\sum_t \\|x_t-y_t\\|_2^2$` | Useful as a loss; not a strict metric. |
| manhattan | distance | yes | Low-priority addition | `$d(x,y)=\sum_t \\|x_t-y_t\\|_1$` | More robust to outliers than Euclidean in some settings. |
| minkowski | distance | yes (p>=1) | Low-priority addition | `$d_p(x,y)=(\sum_t \\|x_t-y_t\\|_p^p)^{1/p}$` | Generalizes Manhattan and Euclidean. |
| chebyshev | distance | yes | Low-priority addition | `$d(x,y)=\max_t \\|x_t-y_t\\|_\infty$` | Focuses on the largest deviation. |
| canberra | distance | yes | Low-priority addition | `$d(x,y)=\sum_t \frac{\|x_t-y_t\|}{\|x_t\|+\|y_t\|}$` | Sensitive near zero. |
| lorentzian | distance | not guaranteed | Low-priority addition | `$d(x,y)=\sum_t \log(1+\|x_t-y_t\|)$` | Compresses large deviations logarithmically. |
| cosine_similarity | similarity | no | Possible addition | `$s(x,y)=\frac{\langle x,y \rangle}{\\|x\\|_2\\|y\\|_2}$` | Measures directional similarity. |
| cosine_distance | distance-like | no | Possible addition | `$d(x,y)=1-s_{cos}(x,y)$` | Monotone transform of cosine similarity. |
| pearson_similarity | similarity | no | Conceptually covered | `$r(x,y)=\frac{\sum_t (x_t-\bar x)(y_t-\bar y)}{\sqrt{\sum_t (x_t-\bar x)^2}\sqrt{\sum_t (y_t-\bar y)^2}}$` | Captures linear correlation after centering. |
| pearson_distance | distance-like | no | Conceptually covered | `$d(x,y)=1-r(x,y)$` | Distance-like transform of Pearson correlation. |
| jensen_shannon | distance | yes | Possible addition | `$JSD(P,Q)=\sqrt{\tfrac{1}{2}KL(P\\|M)+\tfrac{1}{2}KL(Q\\|M)},\ M=\tfrac{P+Q}{2}$` | Requires nonnegative inputs interpreted as distributions. |

### sliding

Shift-aware comparison under pure translation or lead-lag offsets.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| max_ncc | similarity | no | Implemented in EchoWave | `$s(x,y)=\max_\ell NCC(x,shift(y,\ell))$` | Shift-invariant similarity via cross-correlation. |
| sbd | distance-like | no | Implemented in EchoWave | `$d(x,y)=1-\max_\ell NCC(x,shift(y,\ell))$` | Shape-based distance from k-Shape. |

### elastic

Dynamic-programming alignments that allow local stretching or compression.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| dtw | distance | no | Conceptually covered | `$DTW(x,y)=\sqrt{\min_{\pi} \sum_{(i,j)\in\pi} \\|x_i-y_j\\|_2^2}$` | Optimal nonlinear alignment. |
| cdtw | distance | no | Possible addition | `$cDTW=DTW$ with a Sakoe-Chiba window $\|i-j\|\le w$` | Constrains unrealistic warps. |
| wdtw | distance | no | Possible addition | `$WDTW(x,y)=\sqrt{\min_{\pi} \sum_{(i,j)\in\pi} w(\|i-j\|)\\|x_i-y_j\\|_2^2}$` | Penalizes large phase differences through a logistic weight. |
| ddtw | distance | no | Conceptually covered | `$DDTW(x,y)=DTW(\Delta x,\Delta y)$` | Applies DTW to derivative-transformed series for shape emphasis. |
| soft_dtw | soft distance / loss | no | Possible addition | `$SoftDTW_\gamma(x,y)=softmin_\gamma(\mathrm{all\ alignment\ costs})$` | Differentiable smoothing of DTW. |
| soft_dtw_divergence | divergence | no | Possible addition | `$D_\gamma(x,y)=SoftDTW(x,y)-\tfrac12 SoftDTW(x,x)-\tfrac12 SoftDTW(y,y)$` | Nonnegative divergence induced by soft-DTW. |
| lcss_similarity | similarity | no | Implemented in EchoWave | `$LCSS(x,y)=\frac{1}{\min(n,m)}\max \#\{(i,j): \\|x_i-y_j\\|\le \epsilon\}$ under order constraints` | Robust to noise and outliers through thresholded matching. |
| lcss_distance | distance-like | no | Implemented in EchoWave | `$d(x,y)=1-LCSS(x,y)$` | Distance-like transform of LCSS similarity. |
| edr | distance | no | Implemented in EchoWave | `$EDR$ uses edit distance with substitution cost $0/1$ depending on $\\|x_i-y_j\\|\le\epsilon$` | Thresholded edit distance on real sequences. |
| swale_similarity | similarity | no | Possible addition | `$SWALE$ maximizes reward for matches and subtracts penalties for gaps.` | A reward-penalty view of threshold-based alignment. |
| erp | distance | yes | Implemented in EchoWave | `$ERP$ uses edit distance with a real-valued gap $g$: diagonal $\\|x_i-y_j\\|$, gaps $\\|x_i-g\\|$ or $\\|y_j-g\\|$` | A metric elastic measure. |
| msm | distance | yes | Possible addition | `$MSM$ is the minimum cost of move, split, and merge operations.` | The current implementation is univariate. |
| twed | distance | yes | Implemented in EchoWave | `$TWED$ combines edit operations, point distances, timestamps, stiffness $\nu$, and penalty $\lambda$.` | Suitable when timestamps carry meaning. |

### kernel

Similarity through kernel scores rather than direct distances.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| rbf_kernel | kernel similarity | n/a | Low-priority addition | `$K(x,y)=\exp(-\gamma \\|x-y\\|_2^2)$` | Kernelized similarity on equal-length vectors. |
| gak | kernel similarity | n/a | Low-priority addition | `$GAK(x,y)=\sum_{\pi\in A} \prod_{(i,j)\in\pi} k(x_i,y_j)$` | Sums over all alignments instead of only the best one. |
| lgak | kernel score | n/a | Low-priority addition | `$LGAK(x,y)=\log(GAK(x,y)+\epsilon)$` | Log-transformed global alignment kernel. |
| weighted_ncc_kernel | kernel similarity | n/a | Low-priority addition | `$K(x,y)=\sum_\ell w(\ell)NCC_\ell(x,y)$` | Practical shift-aware kernel adapter built on NCC. |

### feature-based

Compare derived features instead of raw waveforms.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| stats_distance | distance | yes | Possible addition | `$d(x,y)=\\|\phi_{stats}(x)-\phi_{stats}(y)\\|_2$` | Compares handcrafted statistical feature vectors. |
| acf_distance | distance | yes | Implemented in EchoWave | `$d(x,y)=\\|ACF_L(x)-ACF_L(y)\\|_2$` | Autocorrelation-pattern distance. |
| spectral_cosine_similarity | similarity | no | Conceptually covered | `$s(x,y)=cos(\|FFT(x)\|,\|FFT(y)\|)$` | Frequency-domain similarity. |
| spectral_distance | distance-like | no | Possible addition | `$d(x,y)=1-s_{spectral}(x,y)$` | Distance-like transform of spectral cosine similarity. |
| paa_distance | distance | yes | Possible addition | `$d(x,y)=\\|PAA_s(x)-PAA_s(y)\\|_2$` | Piecewise aggregate approximation distance. |

### model-based

Compare fitted dynamics or transition structure.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| ar_distance | distance | yes | Possible addition | `$d(x,y)=\\|[c_x,\phi_x]-[c_y,\phi_y]\\|_2$ after AR(p) fitting` | Compares fitted autoregressive parameters. |
| markov_distance | distance | yes | Possible addition | `$d(x,y)=\\|P_x-P_y\\|_F$ after discretized Markov modeling` | Compares transition dynamics rather than raw points. |

### embedding-based

Encode first, then compare in a latent or compressed space.

| method | output | metric | EchoWave fit | formula | note |
|---|---|---|---|---|---|
| embedding_distance | distance | depends on encoder + metric | Low-priority addition | `$z_x=Enc(x),\; z_y=Enc(y),\; d(x,y)=dist(z_x,z_y)$` | Generic adapter for PAA/DFT/stats/random-projection/custom encoders. |
| embedding_similarity | similarity | depends on encoder + metric | Low-priority addition | `$s(x,y)=sim(Enc(x),Enc(y))$` | Generic similarity on latent or compressed representations. |
