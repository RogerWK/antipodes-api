import pandas as pd
from typing import Tuple

def cumulative_geometric_mean(series: pd.Series) -> float:
    # Assume series contains daily returns in decimal form (e.g., 0.01 = 1%)
    return (series.add(1).prod()) ** (1 / len(series)) - 1 if len(series) > 0 else 0.0

def compute_returns_alpha(
    df: pd.DataFrame,
    date_col: str,
    fund_col: str,
    benchmark_col: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> Tuple[float, float, float]:
    sub = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
    if sub.empty:
        return 0.0, 0.0, 0.0

    fund_geom = cumulative_geometric_mean(sub[fund_col])
    bench_geom = cumulative_geometric_mean(sub[benchmark_col])
    alpha = fund_geom - bench_geom
    return fund_geom, bench_geom, alpha
