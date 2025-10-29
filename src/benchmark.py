# benchmark.py
import time
import statistics as stats
import csv
from typing import List, Iterable, Union
from pathlib import Path
import pandas as pd

try:
    from .preprocess import build_arrays
    from .sorts import bubble_sort, merge_sort, quick_sort
except ImportError:
    from preprocess import build_arrays
    from sorts import bubble_sort, merge_sort, quick_sort

ALGORITHMS = {
    "bubble": bubble_sort,
    "merge": merge_sort,
    "quick": quick_sort,
}

def _time_once(func, data, reverse=False):
    start = time.perf_counter()
    _ = func(data, reverse=reverse)
    return time.perf_counter() - start

def median_time(func, data, repeats=5, reverse=False):
    times = [_time_once(func, data, reverse=reverse) for _ in range(repeats)]
    return stats.median(times)

def run_benchmarks(paths: Iterable[Union[str, Path]],
                   sizes: List[int], out_csv: str, repeats: int = 5):
    df, closes, vols, comps = build_arrays(paths)

    datasets = [
        ("Close", closes, False),
        ("Volume", vols, False),
        ("Company", comps, False),
    ]

    rows = []
    for attr_name, data, reverse in datasets:
        for n in sizes:
            subset = data[:n]
            for algo_name, algo_fn in ALGORITHMS.items():
                # Skip Bubble on huge N to keep runtime reasonable
                if algo_name == "bubble" and n > 10000:
                    continue
                t = median_time(algo_fn, subset, repeats=repeats, reverse=reverse)
                rows.append({
                    "algo": algo_name,
                    "attribute": attr_name,
                    "n": n,
                    "repeats": repeats,
                    "seconds": t
                })
                print(f"{algo_name:6s} | {attr_name:7s} | n={n:6d} | {t:.6f}s")

    # Save results
    fieldnames = ["algo", "attribute", "n", "repeats", "seconds"]
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nSaved results to: {out_csv}")

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parents[1]     # project root
    data_dir = BASE / "data"
    csvs = sorted(data_dir.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSVs found in {data_dir}")

    out_csv = BASE / "results" / "tables" / "sort_benchmarks.csv"
    sizes = [1000, 2500, 5000, 10000, 20000, 50000]

    print(f"Running benchmarks on {len(csvs)} CSV file(s)...\n")
    run_benchmarks(csvs, sizes, str(out_csv), repeats=5)
