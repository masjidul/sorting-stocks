# app/app.py
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# --- Make 'src' importable when running this script directly ---
ROOT = Path(__file__).resolve().parents[1]  # project root: .../SORTING-STOCKS
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.load_data import load_stocks
from src.sorts import bubble_sort, merge_sort, quick_sort

ALGORITHMS = {
    "Bubble Sort (O(n^2))": bubble_sort,
    "Merge Sort (O(n log n))": merge_sort,
    "QuickSort (O(n log n) avg)": quick_sort,
}

def main():
    st.set_page_config(page_title="Stock Sorting Demo", layout="wide")
    st.title("Sorting Algorithms on Stock Data")

    # Use project-relative defaults so it works out of the box
    tsla_path = st.text_input("Path to TSLA.csv", "data/TSLA.csv")
    aapl_path = st.text_input("Path to AAPL.csv", "data/aapl_us_2025.csv")

    df = load_stocks(tsla_path, aapl_path)
    st.write(f"Loaded {len(df):,} rows.")
    st.dataframe(df.head(20))

    algo_name = st.selectbox("Choose algorithm", list(ALGORITHMS.keys()))
    attr = st.selectbox("Attribute", ["Close", "Volume", "Company"])
    order = st.selectbox("Order", ["Ascending", "Descending"])
    reverse = (order == "Descending")

    n = st.slider(
        "Input size (n)",
        min_value=100,
        max_value=min(50000, len(df)),
        value=min(2000, len(df)),
        step=100,
    )
    show_company = st.selectbox("Company filter", ["Both", "Apple", "Tesla"])
    topk = st.slider("Show top K rows", min_value=10, max_value=200, value=50, step=10)

    df2 = df if show_company == "Both" else df[df["Company"] == show_company].copy()

    # Build key list for sorting
    if attr == "Company":
        key_vals = df2[attr].astype(str).tolist()
    elif attr == "Volume":
        key_vals = df2[attr].astype(int).tolist()
    else:
        key_vals = df2[attr].astype(float).tolist()

    idxs = list(range(len(df2)))

    # Sort keys using chosen algorithm
    algo_fn = ALGORITHMS[algo_name]
    sorted_keys = algo_fn(key_vals, reverse=reverse)

    # Map keys back to original rows, preserving order for duplicates
    from collections import defaultdict, deque
    buckets = defaultdict(deque)
    for k, i in zip(key_vals, idxs):
        buckets[k].append(i)

    ordered_indices = []
    for k in sorted_keys:
        if buckets[k]:
            ordered_indices.append(buckets[k].popleft())

    df_sorted = df2.iloc[ordered_indices].head(topk)

    st.subheader("Sorted preview")
    st.dataframe(df_sorted)

if __name__ == "__main__":
    main()
