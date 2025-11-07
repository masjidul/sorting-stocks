from pathlib import Path
from collections import defaultdict, deque
import sys

import streamlit as st
import pandas as pd

# ---- Make project root and src/ importable ----
ROOT = Path(__file__).resolve().parents[1]     # .../SORTING-STOCKS
SRC = ROOT / "src"
for p in (ROOT, SRC):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
# ------------------------------------------------

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

    # ✅ Load ALL CSVs from /data/
    csv_dir = ROOT / "data"
    paths = sorted(csv_dir.glob("*.csv"))

    st.caption(f"Found {len(paths)} CSV file(s) in {csv_dir.resolve()}")
    if not paths:
        st.error("No CSV files found in /data folder.")
        st.stop()

    # ✅ Load all CSVs
    try:
        df = load_stocks(paths)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    # ✅ Required columns
    needed_any = {"Company", "Close", "Volume"}
    missing = [c for c in needed_any if c not in df.columns]
    if missing:
        st.error(
            "Missing required columns: "
            + ", ".join(missing)
            + "\n\nColumns present: "
            + ", ".join(df.columns)
        )
        st.stop()

    st.write(f"Loaded **{len(df):,}** rows from **{len(paths)}** CSV file(s).")

    with st.expander("Preview first 20 rows"):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("Companies detected"):
        st.write(f"{df['Company'].nunique()} unique companies")
        st.dataframe(
            df["Company"]
            .value_counts()
            .rename_axis("Company")
            .reset_index(name="Rows"),
            use_container_width=True
        )

    # Controls for sorting
    algo_name = st.selectbox("Choose algorithm", list(ALGORITHMS.keys()))
    attr = st.selectbox("Attribute", ["Close", "Volume", "Company"])
    order = st.selectbox("Order", ["Ascending", "Descending"])
    reverse = (order == "Descending")

    n_default = min(2000, len(df))
    n = st.slider("Input size (n)", 100, min(50000, len(df)), n_default, 100)

    # Company filter
    all_companies = sorted(df["Company"].astype(str).unique().tolist())
    company_choice = st.selectbox("Company filter", ["All"] + all_companies)

    topk = st.slider("Show top K rows", 10, 200, 50, 10)

    # Apply filters
    df2 = df if company_choice == "All" else df[df["Company"] == company_choice]
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

    buckets = defaultdict(deque)
    for k, i in zip(key_vals, idxs):
        buckets[k].append(i)

    ordered_indices = []
    for k in sorted_keys:
        if buckets[k]:
            ordered_indices.append(buckets[k].popleft())

    df_sorted = df2.iloc[ordered_indices].head(topk)

    # Show sorted output
    st.subheader("Sorted preview")
    st.dataframe(df_sorted, use_container_width=True)

    st.caption("Loaded all CSVs from the /data folder. Multi-company data supported.")


if __name__ == "__main__":
    main()
