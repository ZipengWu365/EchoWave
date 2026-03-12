# tsontology decision-impact benchmark

This is a product benchmark for decision impact, not a publication benchmark.

- cases: 150
- decision changed rate: 0.913
- win rate when changed: 0.869
- overall win rate: 0.793
- mean improvement (fixed MAE - routed MAE): 0.7715

## By family

| family | n | change rate | win rate | mean improvement | routed model |
|---|---:|---:|---:|---:|---|
| seasonal | 30 | 1.000 | 1.000 | 1.4280 | seasonal_naive |
| trend | 30 | 1.000 | 1.000 | 0.9786 | drift |
| trend_plus_seasonal | 30 | 1.000 | 1.000 | 1.2969 | seasonal_naive |
| bursty | 30 | 1.000 | 0.567 | -0.0007 | moving_average |
| flat_noisy | 30 | 0.567 | 0.400 | 0.1547 | moving_average |