from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "historical_sales.csv"

products = {
    1: {"name": "Wireless Headphones", "base_demand": 18},
    2: {"name": "Bluetooth Speaker", "base_demand": 12},
    3: {"name": "Smart Watch", "base_demand": 9},
}

dates = pd.date_range(
    start="2024-01-01",
    end="2026-10-31",
    freq="D"
)

records = []

for product_id, product in products.items():
    for date in dates:
        weekend = int(date.dayofweek >= 5)
        seasonal = 1 + 0.15 * np.sin(
            2 * np.pi * date.dayofyear / 365.25
        )
        trend = 1 + 0.0002 * (
            date - dates[0]
        ).days

        expected_demand = (
            product["base_demand"]
            * seasonal
            * trend
            * (1.2 if weekend else 1.0)
        )

        units_sold = int(
            rng.poisson(max(expected_demand, 0))
        )

        records.append({
            "date": date,
            "product_id": product_id,
            "product_name": product["name"],
            "units_sold": units_sold,
            "is_weekend": weekend
        })

df = pd.DataFrame(records)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Dataset created: {OUTPUT_FILE}")
print(f"Total records: {len(df):,}")
print(df.head())