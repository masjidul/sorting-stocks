
import time
import statistics as stats
import csv
from typing import List, Tuple
import pandas as pd

from .preprocess import build_arrays
from .sorts import bubble_sort, merge_sort, quick_sort

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

def run_benchmarks(tsla_path: str, aapl_path: str,
                   sizes: List[int], out_csv: str, repeats: int = 5):
    df, closes, vols, comps = build_arrays(tsla_path, aapl_path)

    # Attributes to test
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
                # Cap bubble on very large N to avoid huge runtimes
                if algo_name == "bubble" and n > 10000:
                    continue
                t = median_time(algo_fn, subset, repeats=repeats, reverse=False)
                rows.append({
                    "algo": algo_name,
                    "attribute": attr_name,
                    "n": n,
                    "repeats": repeats,
                    "seconds": t
                })
                print(f"{algo_name:6s} | {attr_name:7s} | n={n:6d} | {t:.6f}s")

    # Save to CSV
    fieldnames = ["algo","attribute","n","repeats","seconds"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

# --- at bottom of src/benchmark.py ---
if __name__ == "__main__":
    from pathlib import Path

    BASE = Path(__file__).resolve().parents[1]  # project root
    tsla = BASE / "data" / "TSLA.csv"
    aapl = BASE / "data" / "aapl_us_2025.csv"
    out_csv = BASE / "results" / "tables" / "sort_benchmarks.csv"

    sizes = [1000, 2500, 5000, 10000, 20000, 50000]
    run_benchmarks(str(tsla), str(aapl), sizes, str(out_csv), repeats=5)
    print(f"\nSaved results to: {out_csv}")

