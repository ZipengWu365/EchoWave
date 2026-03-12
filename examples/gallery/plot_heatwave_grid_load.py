from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, profile_dataset, starter_dataset


payload = starter_dataset("energy_load_heatwave")
values = payload["values"]
load_north = values[:, 0]
load_south = values[:, 1]

report = compare_series(
    load_north,
    load_south,
    left_name="north grid load",
    right_name="south grid load",
)
profile = profile_dataset(
    values,
    domain="energy",
    timestamps=payload["timestamps"],
    channel_names=payload["channels"],
)

print(report.to_summary_card_markdown())
print(profile.to_summary_card_markdown())
