import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

# Input: benchmark results created by benchmark.py
csv_path = BASE / "results" / "tables" / "sort_benchmarks.csv"

# Output: summary table with speedups
out_csv = BASE / "results" / "tables" / "summary_speedups.csv"

# Load benchmark data
df = pd.read_csv(csv_path)

# Compute median seconds per (attribute, algorithm, n)
med = df.groupby(
    ["attribute", "algo", "n"], 
    as_index=False
)["seconds"].median()

# Pivot for easier speedup calculations
piv = med.pivot_table(
    index=["attribute", "n"],
    columns="algo",
    values="seconds"
)

# Compute speedups (bubble / merge) and (bubble / quick) when available
for target in ["merge", "quick"]:
    if "bubble" in piv.columns and target in piv.columns:
        piv[f"{target}_speedup_vs_bubble"] = piv["bubble"] / piv[target]

# Clean + save
piv = piv.reset_index().sort_values(["attribute", "n"])
piv.to_csv(out_csv, index=False)

print(f"Saved: {out_csv}")
