from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import compare_series, rolling_similarity, starter_dataset


payload = starter_dataset("btc_gold_oil_shocks")
btc = payload["btc"]
gold = payload["gold"]
oil = payload["oil"]

btc_gold = compare_series(btc, gold, left_name="BTC", right_name="Gold")
btc_oil = compare_series(btc, oil, left_name="BTC", right_name="Oil")
windows = rolling_similarity(btc, gold, window=24, step=6)

print(btc_gold.to_summary_card_markdown())
print(
    {
        "btc_gold_similarity": round(btc_gold.similarity_score, 3),
        "btc_oil_similarity": round(btc_oil.similarity_score, 3),
        "rolling_windows": len(windows),
    }
)
