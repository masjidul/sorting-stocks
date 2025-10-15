
import os
import pandas as pd

def _read_csv_safe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path)

def load_stocks(tsla_path: str, aapl_path: str) -> pd.DataFrame:
    """
    Loads Tesla and Apple CSVs, normalizes columns, adds 'Company', and returns a combined DataFrame.
    Expected columns: Date, Open, High, Low, Close, Volume (+ optional Adj Close)
    """
    tsla = _read_csv_safe(tsla_path)
    aapl = _read_csv_safe(aapl_path)

    # Normalize Tesla
    if "Company" not in tsla.columns:
        tsla["Company"] = "Tesla"
    # Normalize Apple
    if "Company" not in aapl.columns:
        aapl["Company"] = "Apple"

    # Standardize column names (title case)
    def standardize(df: pd.DataFrame) -> pd.DataFrame:
        cols = {c: c.strip().title() for c in df.columns}
        df = df.rename(columns=cols)
        # Keep only the columns we need if present
        keep = [c for c in ["Date","Open","High","Low","Close","Volume","Company"] if c in df.columns]
        df = df[keep].copy()

        # Types
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        for num in ["Open","High","Low","Close","Volume"]:
            if num in df.columns:
                df[num] = pd.to_numeric(df[num], errors="coerce")
        return df

    tsla = standardize(tsla)
    aapl = standardize(aapl)

    # Combine
    combined = pd.concat([aapl, tsla], ignore_index=True)
    combined = combined.dropna(subset=["Date","Close","Volume"])
    combined = combined.sort_values("Date").reset_index(drop=True)
    return combined

if __name__ == "__main__":
    # Default paths for quick manual run
    df = load_stocks(tsla_path="/mnt/data/TSLA.csv",
                     aapl_path="/mnt/data/aapl_us_2025.csv")
    print(df.head())
    print(df.tail())
    print(df.dtypes)
