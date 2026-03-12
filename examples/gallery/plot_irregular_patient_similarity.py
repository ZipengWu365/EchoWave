from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, profile_dataset, starter_dataset


payload = starter_dataset("irregular_patient_vitals")
cohort = payload["values"]
subjects = list(cohort.subjects)

left_subject = subjects[0]
right_subject = subjects[1]

left_hr = left_subject.values[0]
right_hr = right_subject.values[0]
left_times = left_subject.timestamps[0]
right_times = right_subject.timestamps[0]

report = compare_series(
    left_hr,
    right_hr,
    left_timestamps=left_times,
    right_timestamps=right_times,
    left_name="patient p1 heart rate",
    right_name="patient p2 heart rate",
)
profile = profile_dataset(cohort, domain="clinical")

print(report.to_summary_card_markdown())
print(profile.to_summary_card_markdown())
