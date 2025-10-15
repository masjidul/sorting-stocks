
from typing import List, Tuple
import pandas as pd
from .load_data import load_stocks

def build_arrays(tsla_path: str, aapl_path: str) -> Tuple[pd.DataFrame, list, list, list]:
    """
    Returns combined df and lists for Close (float), Volume (int), Company (str).
    """
    df = load_stocks(tsla_path, aapl_path)
    close_prices = df["Close"].astype(float).tolist()
    volumes = df["Volume"].astype(int).tolist()
    companies = df["Company"].astype(str).tolist()
    return df, close_prices, volumes, companies

if __name__ == "__main__":
    df, closes, vols, comps = build_arrays("/mnt/data/TSLA.csv", "/mnt/data/aapl_us_2025.csv")
    print(len(df), len(closes), len(vols), len(comps))
