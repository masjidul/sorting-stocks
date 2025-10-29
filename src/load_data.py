# load_data.py
import os
from pathlib import Path
from typing import Iterable, Union, List
import pandas as pd

# ---------------- helpers ----------------

def _read_csv_safe(path: str) -> pd.DataFrame:
    """Safely read a CSV and return a DataFrame."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    # Let pandas infer delimiter/encoding
    return pd.read_csv(path)

def _strip_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace around headers (keep original casing)."""
    if not len(df.columns):
        return df
    trimmed = {c: c.strip() for c in df.columns}
    return df.rename(columns=trimmed)

def _lower_map(df: pd.DataFrame) -> dict:
    """Map lowercased header -> actual header name."""
    return {c.lower(): c for c in df.columns}

def _standardize_company(df: pd.DataFrame, path: Union[str, Path]) -> pd.DataFrame:
    """
    Ensure a canonical 'Company' column (UPPERCASE values).
    Works for multi-company CSVs (Ticker/Symbol/Name/Security) or infers from filename.
    """
    df = _strip_headers(df)
    lower_to_actual = _lower_map(df)

    for alias in ["company", "ticker", "symbol", "ticker_symbol", "ticker symbol", "security", "name"]:
        if alias in lower_to_actual:
            src = lower_to_actual[alias]
            df["Company"] = df[src].astype(str).str.strip().str.upper()
            return df

    # Fallback for single-company files: infer from filename
    token = Path(path).stem.split("_")[0].split("-")[0]
    df["Company"] = token.strip().upper()
    return df

def _standardize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map common column-name variants to canonical OHLCV,
    keep only those + Company, and coerce types (without
    destroying the 'Company' column casing).
    """
    df = _strip_headers(df)
    lower_to_actual = _lower_map(df)

    # Helper to rename if an alias exists and canonical missing
    def ensure_col(alias_lc: str, canonical: str):
        nonlocal df, lower_to_actual
        if alias_lc in lower_to_actual and canonical not in df.columns:
            src = lower_to_actual[alias_lc]
            df = df.rename(columns={src: canonical})
            lower_to_actual = _lower_map(df)

    # Date aliases
    for a in ["date", "timestamp", "time"]:
        ensure_col(a, "Date")

    # Open aliases
    for a in ["open", "open price", "opening price", "open*"]:
        ensure_col(a, "Open")

    # High aliases
    for a in ["high", "high price", "high*"]:
        ensure_col(a, "High")

    # Low aliases
    for a in ["low", "low price", "low*"]:
        ensure_col(a, "Low")

    # Close aliases
    for a in ["close", "adj close", "adjusted close", "close/last", "last", "close price", "closing price", "close*","price"]:
        ensure_col(a, "Close")

    # Volume aliases
    for a in ["volume", "total volume", "volume*", "shares traded", "vol"]:
        ensure_col(a, "Volume")

    # If user provided 'company' in lowercase, lift to 'Company'
    if "company" in lower_to_actual and "Company" not in df.columns:
        df = df.rename(columns={lower_to_actual["company"]: "Company"})
        lower_to_actual = _lower_map(df)

    # Keep only canonical columns that exist
    keep = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume", "Company"] if c in df.columns]
    df = df[keep].copy()

    # Types
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for num in ["Open", "High", "Low", "Close", "Volume"]:
        if num in df.columns:
            df[num] = pd.to_numeric(df[num], errors="coerce")

    return df

# ---------------- public API ----------------

def load_stocks(paths: Iterable[Union[str, Path]]) -> pd.DataFrame:
    """
    Load one or many CSVs (multi-company supported).
    Detects company per row from Company/Ticker/Symbol/Security/Name
    or infers from filename if missing. Normalizes OHLCV.
    """
    paths = list(paths)
    if not paths:
        raise ValueError("No CSV paths provided to load_stocks(...)")

    frames: List[pd.DataFrame] = []
    for p in paths:
        raw = _read_csv_safe(str(p))
        raw = _standardize_company(raw, p)   # create 'Company'
        std = _standardize_ohlcv(raw)        # normalize OHLCV
        frames.append(std)

    combined = pd.concat(frames, ignore_index=True)

    # Drop invalid rows using available required cols (be tolerant)
    subset = [c for c in ["Date", "Close", "Volume"] if c in combined.columns]
    if subset:
        combined = combined.dropna(subset=subset)

    if "Date" in combined.columns:
        combined = combined.sort_values("Date")

    return combined.reset_index(drop=True)

if __name__ == "__main__":
    folder = Path("data")
    csvs = sorted(folder.glob("*.csv"))
    df = load_stocks(csvs)
    companies = df["Company"].nunique() if "Company" in df.columns else 0
    print(f"Loaded {len(df)} rows across {companies} companies.")
    if "Company" in df.columns:
        print(df["Company"].value_counts().head(20))
    else:
        print("WARNING: 'Company' column not present. Columns:", df.columns.tolist())
