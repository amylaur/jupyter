"""Clean and tidy the yearly stray dog collection service CSVs.

Loads each year's raw CSV, standardises column names (they drift slightly
year to year), reshapes into a tidy long table, and writes both a long and
a wide version to data/processed/.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}

# Column layouts, in the order the values appear after the month column.
# 2020-2021 reports don't include the "patrolled areas" / "warden advised
# owners" columns that 2022+ reports added.
LAYOUT_6 = [
    "dogs_seized", "dogs_kennelled", "dogs_returned_by_warden",
    "dogs_retained_by_finder", "dogs_returned_by_kennel_provider",
    "dogs_euthanised",
]
LAYOUT_8 = [
    "dogs_seized", "dogs_kennelled", "dogs_returned_by_warden",
    "patrolled_no_dog_found", "warden_advised_owners",
    "dogs_retained_by_finder", "dogs_returned_by_kennel_provider",
    "dogs_euthanised",
]

FILES = {
    2016: ("2016_Stray_Dogs_v1.csv", LAYOUT_6),
    2017: ("2017-stray-dog-collection-service-v1.csv", LAYOUT_6),
    2018: ("2018-stray-dog-collection-service.csv", LAYOUT_6),
    2019: ("2019-stray-dog-collection-data-csv.csv", LAYOUT_6),
    2020: ("2020-stray-dog-collection-data-csv.csv", LAYOUT_6),
    2021: ("2021-stray-dog-information.csv", LAYOUT_6),
    2022: ("2022-Stray_dog_collection_service_(csv).csv", LAYOUT_8),
    2023: ("2023_Stray_dog_collection_service.csv", LAYOUT_8),
    2024: ("2024_Stray_dog_collection_service.csv", LAYOUT_8),
}


def load_year(year, filename, layout):
    # The 2016-2018 files use £ signs saved as cp1252/latin-1, not UTF-8.
    df = pd.read_csv(RAW_DIR / filename, header=None, dtype=str, encoding="cp1252")
    records = []
    for _, row in df.iterrows():
        month = str(row[0]).strip() if pd.notna(row[0]) else ""
        if month not in MONTH_NUM:
            continue  # skips header rows, blank rows, and the "Totals" row
        for col_offset, metric in enumerate(layout, start=1):
            raw = row[col_offset]
            records.append({
                "year": year,
                "month": month,
                "month_num": MONTH_NUM[month],
                "metric": metric,
                "value": pd.to_numeric(raw, errors="coerce"),
            })
    return pd.DataFrame.from_records(records)


def main():
    long_df = pd.concat(
        (load_year(year, filename, layout) for year, (filename, layout) in FILES.items()),
        ignore_index=True,
    ).sort_values(["year", "month_num", "metric"]).reset_index(drop=True)

    wide_df = long_df.pivot(
        index=["year", "month", "month_num"], columns="metric", values="value"
    ).reset_index().sort_values(["year", "month_num"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long_df.to_csv(OUT_DIR / "stray_dogs_tidy_long.csv", index=False)
    wide_df.to_csv(OUT_DIR / "stray_dogs_tidy_wide.csv", index=False)

    print(f"Wrote {len(long_df)} rows to {OUT_DIR / 'stray_dogs_tidy_long.csv'}")
    print(f"Wrote {len(wide_df)} rows to {OUT_DIR / 'stray_dogs_tidy_wide.csv'}")


if __name__ == "__main__":
    main()
