from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, rolling_similarity


t = np.linspace(0, 8 * np.pi, 128)
candidate = np.sin(t) + 0.08 * np.cos(t / 2.0)
reference = np.sin(t + 0.22) + 0.05 * np.cos(t / 2.0)

report = compare_series(
    candidate,
    reference,
    left_name="candidate curve",
    right_name="reference analog",
)
windows = rolling_similarity(candidate, reference, window=24, step=6)

print(report.to_summary_card_markdown())
print({"rolling_windows": len(windows), "mean_similarity": round(report.similarity_score, 3)})
