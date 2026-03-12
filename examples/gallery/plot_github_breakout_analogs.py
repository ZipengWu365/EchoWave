from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, rolling_similarity, starter_dataset


payload = starter_dataset("github_breakout_analogs")
target = payload["target"]
durable = payload["durable_breakout"]
short_hype = payload["short_hype"]

durable_report = compare_series(
    target,
    durable,
    left_name="OpenClaw-style candidate",
    right_name="durable breakout analog",
)
hype_report = compare_series(
    target,
    short_hype,
    left_name="OpenClaw-style candidate",
    right_name="short-hype analog",
)
windows = rolling_similarity(target, durable, window=20, step=5)

print(durable_report.to_summary_card_markdown())
print(
    {
        "durable_similarity": round(durable_report.similarity_score, 3),
        "hype_similarity": round(hype_report.similarity_score, 3),
        "rolling_windows": len(windows),
    }
)
