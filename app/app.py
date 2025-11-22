from pathlib import Path
from collections import defaultdict, deque
import sys

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ======================================================
#  PROJECT ROOT SETUP  (app/ is the current directory)
# ======================================================
ROOT = Path(__file__).resolve().parents[1]   # → SORTING-STOCKS
SRC = ROOT / "src"

for p in (ROOT, SRC):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from load_data import load_stocks
from sorts import bubble_sort, merge_sort, quick_sort


# ======================================================
#  AVAILABLE SORTING ALGORITHMS
# ======================================================
ALGORITHMS = {
    "Bubble Sort (O(n²))": bubble_sort,
    "Merge Sort (O(n log n))": merge_sort,
    "QuickSort (O(n log n) avg)": quick_sort,
}


# ======================================================
#  MAIN UI
# ======================================================
def main():
    st.set_page_config(page_title="Stock Sorting Demo", layout="wide")
    st.title("Sorting Algorithms on Stock Data")

    # --------------------------------------------------
    # Load ALL CSVs from ../data/
    # --------------------------------------------------
    csv_dir = ROOT / "data"
    paths = sorted(csv_dir.glob("*.csv"))

    st.caption(f"Found {len(paths)} CSV file(s) in {csv_dir.resolve()}")
    if not paths:
        st.error("❌ No CSV files found in /data folder.")
        st.stop()

    try:
        df = load_stocks(paths)
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        st.stop()

    required = {"Company", "Close", "Volume"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {', '.join(missing)}")
        st.stop()

    st.write(f"Loaded **{len(df):,}** rows from **{len(paths)}** files.")

    # --------------------------------------------------
    # Preview panels
    # --------------------------------------------------
    with st.expander("Preview first 20 rows"):
        st.dataframe(df.head(20), width="stretch")

    with st.expander("Companies detected"):
        st.write(f"Total companies: {df['Company'].nunique()}")
        st.dataframe(
            df["Company"].value_counts().rename_axis("Company").reset_index(name="Rows"),
            width="stretch"
        )

    # --------------------------------------------------
    # Sorting controls
    # --------------------------------------------------
    algo_name = st.selectbox("Choose algorithm", list(ALGORITHMS.keys()))
    attr = st.selectbox("Attribute", ["Close", "Volume", "Company"])
    order = st.selectbox("Order", ["Ascending", "Descending"])
    reverse = (order == "Descending")

    n_default = min(2000, len(df))
    n = st.slider("Input size (n)", 100, min(50000, len(df)), n_default, step=100)

    all_companies = sorted(df["Company"].astype(str).unique().tolist())
    company_choice = st.selectbox("Company filter", ["All"] + all_companies)

    topk = st.slider("Show top K rows", 10, 200, 50, step=10)

    # --------------------------------------------------
    # Apply user filtering
    # --------------------------------------------------
    df2 = df if company_choice == "All" else df[df["Company"] == company_choice]
    df2 = df2.head(min(n, len(df2)))

    # --------------------------------------------------
    # Build sort keys
    # --------------------------------------------------
    if attr == "Company":
        key_vals = df2[attr].astype(str).tolist()
    elif attr == "Volume":
        key_vals = df2[attr].astype(int).tolist()
    else:
        key_vals = df2[attr].astype(float).tolist()

    idxs = list(range(len(df2)))

    # --------------------------------------------------
    # Perform sorting
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Show sorted result
    # --------------------------------------------------
    st.subheader("Sorted preview")
    st.dataframe(df_sorted, width="stretch")

    st.markdown("---")
    st.caption("Loaded all CSVs from the /data folder. Multi-company data supported.")

    # --------------------------------------------------
    # Show performance visual comparison
    # --------------------------------------------------
    show_performance_visuals()


# ======================================================
#  RUNTIME PERFORMANCE VISUALIZER
# ======================================================
def show_performance_visuals():
    st.header("📊 Algorithm Runtime Comparison")

    bench_path = ROOT / "results" / "tables" / "sort_benchmarks.csv"
    if not bench_path.exists():
        st.warning(f"⚠ Benchmark file not found at: {bench_path}")
        return

    df = pd.read_csv(bench_path)
    med = df.groupby(["attribute", "algo", "n"])["seconds"].median().reset_index()
    attributes = med["attribute"].unique()

    # ---------- 2 charts per row  ----------
    cols = st.columns(2)

    # counter for alternating between col1 / col2
    col_index = 0

    for attr in attributes:
        sub = med[med["attribute"] == attr]

        # create figure
        fig, ax = plt.subplots(figsize=(4, 3))   # smaller, clean
        for algo in sub["algo"].unique():
            cur = sub[sub["algo"] == algo].sort_values("n")
            ax.plot(cur["n"], cur["seconds"], marker="o", label=algo)

        ax.set_title(f"{attr}", fontsize=12)
        ax.set_xlabel("n", fontsize=10)
        ax.set_ylabel("Time (s)", fontsize=10)
        ax.legend(fontsize=8)

        # put figure in column 1 or 2
        cols[col_index].pyplot(fig)
        col_index = (col_index + 1) % 2

    st.markdown("---")



# ======================================================
#  MAIN ENTRY
# ======================================================
if __name__ == "__main__":
    main()
