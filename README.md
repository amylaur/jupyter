# Stray Dog Collection Service — Rochdale (2016–2024)

Cleans and analyses Rochdale Borough Council's yearly stray dog collection
service reports, published as individually-formatted CSVs, into a single
tidy dataset for year-over-year analysis.

## Project layout

```
data/raw/            9 original yearly CSVs (2016-2024), as downloaded — untouched
data/processed/      Cleaned, tidy output (see below)
src/clean_data.py    Cleaning script: raw CSVs -> data/processed/
notebooks/analysis.ipynb   Analysis and charts, reading from data/processed/
outputs/figures/     PNG charts saved by the notebook
requirements.txt     pandas, matplotlib
```

## Data cleaning (`src/clean_data.py`)

Each year's CSV has its own quirks — multi-row headers, extra columns added
from 2022 onward, stray footnotes, `£` signs saved in cp1252 rather than
UTF-8 — so the script normalises them into one schema:

- **Column layout**: 2016–2021 report 6 metrics per month; 2022–2024 add two
  more (`patrolled_no_dog_found`, `warden_advised_owners`). Both layouts are
  mapped to the same canonical metric names.
- **Row filtering**: only rows whose first cell is a month name are kept —
  this automatically drops header rows, blank rows, "Totals"/"TOTALS" rows,
  and narrative footnotes (e.g. net-cost text) without needing to hardcode
  them.
- **Missing/non-numeric values**: cells like blanks, `"N/A"`, or
  `"7 (1 refused)"` are converted with `pd.to_numeric(errors="coerce")`,
  which turns anything that isn't a clean integer into `NaN`. This is a
  deliberate simplification — it doesn't try to recover the `7` from
  `"7 (1 refused)"` or distinguish *why* a cell is missing, it just leaves it
  as `NaN` rather than dropping the row or inventing a value.
- **Output**: written to `data/processed/` in two shapes —
  `stray_dogs_tidy_long.csv` (one row per year/month/metric/value — tidy
  format, easiest for grouping/plotting) and `stray_dogs_tidy_wide.csv` (one
  row per year/month, one column per metric).

Run it with:

```
py -m pip install -r requirements.txt
py src/clean_data.py
```

## Analysis (`notebooks/analysis.ipynb`)

Working from the tidy long/wide CSVs:

1. **Dogs seized per year** — the headline "how many strays came in" trend.
2. **Seasonality** — a year×month heatmap and an average-by-month line
   chart, to see which months are consistently busiest.

## Key findings so far

- See analysis.ipnb markdown.