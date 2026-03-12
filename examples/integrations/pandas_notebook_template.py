import pandas as pd
from tsontology import profile_dataset

# Example long table with columns: subject, timestamp, channel, value
df = pd.read_csv('examples/data/irregular_patient_vitals.csv')
profile = profile_dataset(df, domain='clinical')
print(profile.to_summary_card_markdown())
print(profile.to_html_report())
