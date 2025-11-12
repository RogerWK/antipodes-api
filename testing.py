# Directory structure (you can copy to your GitHub repo)
# antipodes_api/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py
# │   └── data_processing.py
# ├── requirements.txt
# ├── Dockerfile
# └── .github/workflows/docker_build.yml

# ==================================
# app/data_processing.py
# ==================================
import pandas as pd
import numpy as np


def load_excel_data(filepath: str):
    returns_df = pd.read_excel(filepath, sheet_name="Returns")
    constituents_df = pd.read_excel(filepath, sheet_name="IndexConstituents")
    return returns_df, constituents_df


def geometric_cumulative_return(returns: pd.Series, na_strategy: str = "keep") -> float:
    if na_strategy == "zero":
        returns = returns.fillna(0)
    elif na_strategy == "drop":
        returns = returns.dropna()
    if returns.isna().any() or len(returns) == 0:
        return np.nan
    return np.prod(1 + returns) - 1


def cumulative_returns_and_alpha(df, as_of_date, fund_col, bench_col, date_col, windows, na_strategy="keep"):
    df[date_col] = pd.to_datetime(df[date_col])
    as_of_date = pd.to_datetime(as_of_date)
    output = []
    for w in windows:
        start_date = as_of_date - pd.Timedelta(days=w)
        period_df = df[(df[date_col] > start_date) & (df[date_col] <= as_of_date)]
        fund_return = geometric_cumulative_return(period_df[fund_col], na_strategy)
        bench_return = geometric_cumulative_return(period_df[bench_col], na_strategy)
        alpha = (fund_return - bench_return) if pd.notna(fund_return) and pd.notna(bench_return) else np.nan
        output.append({
            "window_days": w,
            "as_of": as_of_date.strftime("%Y-%m-%d"),
            "fund_cum_return": fund_return,
            "bench_cum_return": bench_return,
            "alpha": alpha
        })
    return output


def exposure_difference(df, left_date, right_date, group_by, date_col, weight_col, na_strategy="keep"):
    df[date_col] = pd.to_datetime(df[date_col])
    left_date = pd.to_datetime(left_date)
    right_date = pd.to_datetime(right_date)

    if na_strategy == "zero":
        df[weight_col] = df[weight_col].fillna(0)
    elif na_strategy == "drop":
        df = df.dropna(subset=[weight_col])

    left_df = df[df[date_col] == left_date]
    right_df = df[df[date_col] == right_date]

    left_sum = left_df.groupby(group_by, dropna=False)[weight_col].sum().reset_index().rename(columns={weight_col: "sum_weight_left"})
    right_sum = right_df.groupby(group_by, dropna=False)[weight_col].sum().reset_index().rename(columns={weight_col: "sum_weight_right"})

    merged = pd.merge(left_sum, right_sum, on=group_by, how="outer")
    merged["sum_weight_left"] = merged["sum_weight_left"].fillna(0)
    merged["sum_weight_right"] = merged["sum_weight_right"].fillna(0)
    merged["difference"] = merged["sum_weight_right"] - merged["sum_weight_left"]
    return merged.to_dict(orient="records")


# ==================================
# app/main.py
# ==================================
from fastapi import FastAPI, Query
from typing import List
import pandas as pd
from .data_processing import (
    load_excel_data,
    cumulative_returns_and_alpha,
    exposure_difference,
)

app = FastAPI(title="Antipodes Financial APIs")

FILE_PATH = "Returns_and_Constituent_Data.xlsx"
returns_df, constituents_df = load_excel_data(FILE_PATH)


@app.get("/returns")
def get_returns(
    as_of: str,
    windows: List[int] = Query(default=[30, 90, 180]),
    fund_col: str = "Fund",
    bench_col: str = "Benchmark",
    date_col: str = "Date",
    na_strategy: str = Query(default="keep", regex="^(keep|zero|drop)$"),
):
    result = cumulative_returns_and_alpha(
        returns_df, as_of, fund_col, bench_col, date_col, windows, na_strategy
    )
    return {"results": result}


@app.get("/exposure")
def get_exposure(
    left_date: str,
    right_date: str,
    group_by: str = "Antipodes Region",
    date_col: str = "Date",
    weight_col: str = "Weight",
    na_strategy: str = Query(default="keep", regex="^(keep|zero|drop)$"),
):
    result = exposure_difference(
        constituents_df, left_date, right_date, group_by, date_col, weight_col, na_strategy
    )
    return {"results": result}


# ==================================
# requirements.txt
# ==================================
# fastapi
# uvicorn
# pandas
# numpy
# openpyxl

# ==================================
# Dockerfile
# ==================================
# Use official lightweight Python image
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ==================================
# .github/workflows/docker_build.yml
# ==================================
name: Build Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        run: docker build -t antipodes-api .
