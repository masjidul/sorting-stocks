# app.py
from pathlib import Path
from collections import defaultdict, deque
import sys

import streamlit as st
import pandas as pd

# ---- Make project root and src/ importable (so load_data.py & sorts.py are found) ----
ROOT = Path(__file__).resolve().parents[1]     # .../UPDT-SORTING-STOCKS
SRC = ROOT / "src"
for p in (ROOT, SRC):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
# -------------------------------------------------------------------------------------

from load_data import load_stocks
from sorts import bubble_sort, merge_sort, quick_sort

ALGORITHMS = {
    "Bubble Sort (O(n^2))": bubble_sort,
    "Merge Sort (O(n log n))": merge_sort,
    "QuickSort (O(n log n) avg)": quick_sort,
}

def main():
    st.set_page_config(page_title="Stock Sorting Demo", layout="wide")
    st.title("Sorting Algorithms on Stock Data")

    # Folder + glob => drop in 20+ CSVs and you're done
    csv_dir = st.text_input("Folder containing CSV files", "data/")
    pattern = st.text_input("Filename pattern (glob)", "*.csv")

    paths = sorted(Path(csv_dir).glob(pattern))
    st.caption(f"Found {len(paths)} CSV file(s) matching {pattern!r} in {Path(csv_dir).resolve()}")
    if not paths:
        st.stop()

    # Load all files (supports multi-company rows)
    try:
        df = load_stocks(paths)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    # Guards for expected columns
    needed_any = {"Company", "Close", "Volume"}
    missing = [c for c in needed_any if c not in df.columns]
    if missing:
        st.error(
            "Missing required columns after loading: "
            + ", ".join(missing)
            + "\n\nColumns found: "
            + ", ".join(map(str, df.columns.tolist()))
        )
        st.stop()

    st.write(f"Loaded **{len(df):,}** rows from **{len(paths)}** file(s).")
    with st.expander("Preview first 20 rows"):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("What companies did we load?"):
        unique_count = int(df["Company"].astype(str).nunique())
        st.write(f"**{unique_count}** companies detected")
        st.dataframe(
            df["Company"]
            .astype(str)
            .value_counts()
            .rename_axis("Company")
            .reset_index(name="Rows")
            .head(200),
            use_container_width=True,
        )

    # Controls
    algo_name = st.selectbox("Choose algorithm", list(ALGORITHMS.keys()))
    attr = st.selectbox("Attribute", ["Close", "Volume", "Company"])
    order = st.selectbox("Order", ["Ascending", "Descending"])
    reverse = (order == "Descending")

    n_default = min(2000, len(df))
    n = st.slider("Input size (n)", 100, min(50000, len(df)), n_default, 100)

    # Dynamic company filter (populated from all files)
    all_companies = sorted(df["Company"].astype(str).unique().tolist())
    company_choice = st.selectbox("Company filter", ["All"] + all_companies)

    topk = st.slider("Show top K rows of the sorted result", 10, 200, 50, 10)

    # Filter & clamp to n rows
    df2 = df if company_choice == "All" else df[df["Company"] == company_choice].copy()
    if df2.empty:
        st.warning("No rows after filtering; adjust your filters.")
        st.stop()
    df2 = df2.head(min(n, len(df2)))

    # Build sort keys
    if attr == "Company":
        key_vals = df2[attr].astype(str).tolist()
    elif attr == "Volume":
        key_vals = df2[attr].astype(int).tolist()
    else:
        key_vals = df2[attr].astype(float).tolist()

    idxs = list(range(len(df2)))

    # Sort
    algo_fn = ALGORITHMS[algo_name]
    sorted_keys = algo_fn(key_vals, reverse=reverse)

    # Stable mapping keys -> original rows
    buckets = defaultdict(deque)
    for k, i in zip(key_vals, idxs):
        buckets[k].append(i)

    ordered_indices = []
    for k in sorted_keys:
        if buckets[k]:
            ordered_indices.append(buckets[k].popleft())

    df_sorted = df2.iloc[ordered_indices].head(topk)

    # Show
    st.subheader("Sorted preview")
    st.dataframe(df_sorted, use_container_width=True)

    st.caption(
        "Tip: Drop multi-company CSVs (Ticker/Symbol/Company) or many single-company CSVs into the folder. "
        "The dynamic Company filter will pick them up automatically."
    )

if __name__ == "__main__":
    main()
