import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
csv_path = BASE / "results" / "tables" / "sort_benchmarks.csv"
out_csv  = BASE / "results" / "tables" / "summary_speedups.csv"

df = pd.read_csv(csv_path)

# median time per (algo, attribute, n)
med = df.groupby(["attribute","algo","n"], as_index=False)["seconds"].median()

# pivot for easy ratios
piv = med.pivot_table(index=["attribute","n"], columns="algo", values="seconds")

# compute speedups vs bubble (where available)
for target in ["merge","quick"]:
    if "bubble" in piv.columns and target in piv.columns:
        piv[f"{target}_speedup_vs_bubble"] = piv["bubble"] / piv[target]

piv = piv.reset_index().sort_values(["attribute","n"])
piv.to_csv(out_csv, index=False)
print(f"Saved: {out_csv}")
