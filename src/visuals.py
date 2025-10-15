
import pandas as pd
import matplotlib.pyplot as plt

def plot_curves(csv_path: str, out_dir: str):
    df = pd.read_csv(csv_path)
    # Compute median seconds per algo/attribute/n
    med = df.groupby(["attribute","algo","n"])["seconds"].median().reset_index()

    for attr in med["attribute"].unique():
        sub = med[med["attribute"] == attr]
        plt.figure()
        for algo in sub["algo"].unique():
            cur = sub[sub["algo"] == algo].sort_values("n")
            plt.plot(cur["n"], cur["seconds"], marker="o", label=algo)
        plt.xlabel("Input size (n)")
        plt.ylabel("Median time (s)")
        plt.title(f"Sorting performance on {attr}")
        plt.legend()
        plt.tight_layout()
        out_path = f"{out_dir}/perf_{attr.lower()}.png"
        plt.savefig(out_path, dpi=150)
        plt.close()

if __name__ == "__main__":
    from pathlib import Path

    BASE = Path(__file__).resolve().parents[1]  # project root
    csv_path = BASE / "results" / "tables" / "sort_benchmarks.csv"
    out_dir = BASE / "results" / "figures"

    plot_curves(str(csv_path), str(out_dir))
    print(f"Saved figures to: {out_dir}")
