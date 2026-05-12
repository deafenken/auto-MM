# Data recon checklist — what to extract in Stage 0

The output is `stage0_triage/data_recon.md`, read by every later stage. Keep it under 150 lines. Substance over decoration.

## Per CSV / Excel / Parquet

```python
import pandas as pd
df = pd.read_csv(path)   # or read_excel / read_parquet
{
  "path": str(path),
  "rows": len(df),
  "cols": len(df.columns),
  "dtypes": df.dtypes.value_counts().to_dict(),
  "missing_pct_top": (df.isna().mean() * 100).round(2).nlargest(5).to_dict(),
  "numeric_summary": df.describe().to_dict(),       # only for numeric columns
  "head": df.head(3).to_dict(orient="records"),
  "tail": df.tail(3).to_dict(orient="records"),
}
```

Write the result as a markdown subsection. Do not dump the raw dataframe — pick the most informative columns.

## Per image / video directory

```bash
find <dir> -type f | wc -l         # count
du -sh <dir>                       # total size
file <one_sample>                  # format
python3 -c "from PIL import Image; print(Image.open('<sample>').size)"  # dims
```

For 5 randomly-sampled files, record (path, dimensions, file size).

## Per text / JSON

- File count, total size.
- First record's top-level keys / fields.
- Total record count if streamable.
- Min/max/mean record length.

## Per time series (any format)

- Time column name and dtype.
- First / last timestamps (UTC if known; record source timezone if not).
- Sampling frequency (inferred from the median diff).
- Gap statistics: count and duration of gaps > 2× median diff.

## Anomalies section (mandatory)

Even if nothing is wrong, write `## Anomalies\n_None observed._`. If there are issues, list them with file + column + sample value + suspected interpretation:

```
## Anomalies
- `orders.csv` col `weight` has 14 negative values (sample: -1.5 kg row 432) — likely unit-conversion error.
- `routes.csv` col `start_time` has 3 entries where `end_time < start_time` — time-window inversion, suspect data entry bug.
- `customers.csv` has 31 customers; problem statement says 30 — discrepancy (recall integrity Rule 1: problem statement wins as main model; record both).
```

## Problem→data mapping section (mandatory)

A one-line summary per problem:

```
## Problem→data mapping
- Problem A → uses `routes.csv` (8,432 rows), `customers.csv` (31 rows). Sufficient.
- Problem B → references `weather.csv` but file is not in inputs/data/. Missing.
- Problem C → no data attachment; problem is analytical only.
```

Stage 1 reads this to decide what data each sub-question needs.

## Things to NOT do

- Don't paste raw CSVs in the markdown. Use head/tail samples only.
- Don't compute correlations or PCA at this stage. That's modeling, not recon.
- Don't fix anomalies — log them. Stage 1 / Stage 2 decide the fix.
- Don't pull external sources to enrich the recon. Stick to what's in `inputs/`.

## Resume behavior

If `data_recon.md` already exists, compare its declared file list against the current `inputs/data/` listing. If files were added → re-recon only the new ones, append to the section. If files were removed → flag inconsistency, escalate.
