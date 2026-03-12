from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, rolling_similarity, starter_dataset


payload = starter_dataset("weekly_website_traffic")
sessions = payload["values"][:, 0]
signups = payload["values"][:, 1]

report = compare_series(
    sessions,
    signups,
    left_name="sessions",
    right_name="signups",
)
windows = rolling_similarity(sessions, signups, window=21, step=7)

print(report.to_summary_card_markdown())
print({"rolling_windows": len(windows), "mean_similarity": round(report.similarity_score, 3)})
