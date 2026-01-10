from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

try:
    import akshare as ak
except ImportError as e:
    raise ImportError(f"Missing dependency: {e}. Please install akshare.")


# =========================
# Types / Config
# =========================

IntervalType = Union[str, int, None]


@dataclass(frozen=True)
class StockQuery:
    stock_code: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    interval: str    # normalized string (e.g. "30d")


# =========================
# Helpers
# =========================

def _normalize_stock_symbol(stock_code: str) -> str:
    """
    Accept: "600519", "600519.SH", "600519.SZ" -> "600519"
    """
    if stock_code is None:
        return ""
    return str(stock_code).strip().split(".")[0].strip()


def _parse_interval_to_days(interval: IntervalType, default_days: int = 365) -> int:
    """
    interval:
      - int: treated as days
      - str: "365d", "6m", "1y", "30" (days), case-insensitive
    """
    if interval is None:
        return default_days

    try:
        if isinstance(interval, int):
            return max(1, interval)

        s = str(interval).strip().lower()
        if not s:
            return default_days

        if s.isdigit():
            return max(1, int(s))

        unit = s[-1]
        value = s[:-1]
        if not value.isdigit():
            return default_days

        n = int(value)
        if unit == "d":
            return max(1, n)
        if unit == "m":
            return max(1, n * 30)
        if unit == "y":
            return max(1, n * 365)

        return default_days
    except Exception:
        return default_days


def _calc_date_range(interval: IntervalType) -> Tuple[str, str, str]:
    """
    Return (start_date, end_date, normalized_interval_str)
    """
    days = _parse_interval_to_days(interval)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"), f"{days}d"


def _sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert NaN/Inf (numpy or python) to None so strict JSON won't fail.
    """
    # numpy scalar -> python scalar
    if isinstance(obj, (np.floating, np.integer)):
        obj = obj.item()

    if isinstance(obj, float):
        if not math.isfinite(obj) or math.isnan(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]

    return obj


# =========================
# Core: Fetch
# =========================

def fetch_china_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch daily A-share data via AkShare.

    Returns standardized OHLCV dataframe indexed by Date:
      columns: Open, High, Low, Close, Volume
    """
    symbol = _normalize_stock_symbol(stock_code)
    if not symbol:
        return pd.DataFrame()

    start_date_clean = start_date.replace("-", "")
    end_date_clean = end_date.replace("-", "")

    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date_clean,
            end_date=end_date_clean,
            adjust="qfq",
        )
    except Exception as e:
        # Never throw to API layer
        print(f"[AkShare Error] symbol={symbol} start={start_date} end={end_date} err={e}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        "日期": "Date",
        "开盘": "Open",
        "最高": "High",
        "最低": "Low",
        "收盘": "Close",
        "成交量": "Volume",
    }

    existing = [c for c in rename_map.keys() if c in df.columns]
    if not existing:
        print(f"[Column Error] AkShare returned columns={list(df.columns)}")
        return pd.DataFrame()

    df = df[existing].rename(columns=rename_map)

    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        print(f"[Column Error] missing required cols, got={list(df.columns)}")
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).set_index("Date").sort_index()

    # Ensure numeric types
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])  # Close is essential
    return df


# =========================
# Core: Features
# =========================

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators:
      - MA_10, MA_50
      - Daily_Return
      - Volatility_20d
      - RSI (14)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    # Moving Averages
    out["MA_10"] = out["Close"].rolling(window=10, min_periods=1).mean()
    out["MA_50"] = out["Close"].rolling(window=50, min_periods=1).mean()

    # Daily returns & volatility
    out["Daily_Return"] = out["Close"].pct_change()
    out["Volatility_20d"] = out["Daily_Return"].rolling(window=20, min_periods=1).std()

    # RSI (14-day), simple rolling mean
    delta = out["Close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()

    # avoid division by zero -> NaN (handled later)
    avg_loss = avg_loss.replace(0, np.nan)

    rs = avg_gain / avg_loss
    out["RSI"] = 100 - (100 / (1 + rs))

    # Round float columns for readability
    float_cols = out.select_dtypes(include=["float64", "float32"]).columns
    out[float_cols] = out[float_cols].round(4)  # 4位更稳，前端可再格式化

    return out


# =========================
# Public API Function
# =========================

def get_stock_data_with_features(stock_code: str, interval: IntervalType = "365d") -> Dict[str, Any]:
    """
    Returns:
      {
        success: bool,
        message: str,
        meta: { stock_code, symbol, start_date, end_date, interval, rows },
        data: [ {Date: "...", Open:..., ...}, ...]
      }
    """
    start_date, end_date, interval_norm = _calc_date_range(interval)
    symbol = _normalize_stock_symbol(stock_code)

    if not symbol:
        return {
            "success": False,
            "message": "Error: stock_code cannot be empty.",
            "meta": {"stock_code": stock_code, "symbol": "", "start_date": start_date, "end_date": end_date, "interval": interval_norm, "rows": 0},
            "data": [],
        }

    df = fetch_china_stock_data(symbol, start_date, end_date)
    if df.empty:
        return {
            "success": False,
            "message": f"No data found for stock {symbol}.",
            "meta": {"stock_code": stock_code, "symbol": symbol, "start_date": start_date, "end_date": end_date, "interval": interval_norm, "rows": 0},
            "data": [],
        }

    df = feature_engineering(df)

    # Build records
    records: List[Dict[str, Any]] = df.reset_index().to_dict(orient="records")

    # ✅ Critical: make strict-JSON safe
    records = _sanitize_for_json(records)

    return {
        "success": True,
        "message": f"Successfully retrieved stock data for {symbol}",
        "meta": {"stock_code": stock_code, "symbol": symbol, "start_date": start_date, "end_date": end_date, "interval": interval_norm, "rows": len(records)},
        "data": records,
    }
