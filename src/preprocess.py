from typing import Tuple, Iterable, Union
from pathlib import Path
import pandas as pd

try:
    from .load_data import load_stocks
except ImportError:
    from load_data import load_stocks


def build_arrays(paths: Iterable[Union[str, Path]]) -> Tuple[pd.DataFrame, list, list, list]:
    """
    Build arrays for sorting/benchmarks from one or many CSV paths.
    """
    df = load_stocks(paths)

    closes = df["Close"].astype(float).tolist()
    volumes = df["Volume"].astype(int).tolist()
    companies = df["Company"].astype(str).tolist()

    return df, closes, volumes, companies


if __name__ == "__main__":
    data_dir = Path("data")
    paths = sorted(data_dir.glob("*.csv"))

    df, closes, volumes, companies = build_arrays(paths)

    print("Total rows:", len(df))
    print("Close values:", len(closes))
    print("Volume values:", len(volumes))
    print("Company labels:", len(companies))
