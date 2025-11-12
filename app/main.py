from fastapi import FastAPI, Query, HTTPException
import pandas as pd

from app.settings import settings
from app.services.returns import compute_returns_alpha
from app.services.exposure import exposure_difference
from app.models import ReturnsResponse, ExposureDiffResponse, ExposureDiffItem

app = FastAPI(title="Antipodes API", version="1.0.0")

# Load Excel once
xl = pd.ExcelFile(settings.excel_path)
returns_df = xl.parse(settings.sheet_returns)
returns_df[settings.date_col_returns] = pd.to_datetime(returns_df[settings.date_col_returns])

constituents_df = xl.parse(settings.sheet_constituents)
constituents_df[settings.date_col_constituents] = pd.to_datetime(constituents_df[settings.date_col_constituents])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/returns", response_model=ReturnsResponse)
def get_returns(
    start_date: str = Query(...),
    end_date: str = Query(...),
):
    try:
        sd = pd.to_datetime(start_date)
        ed = pd.to_datetime(end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format")

    fund_geom, bench_geom, alpha = compute_returns_alpha(
        returns_df,
        settings.date_col_returns,
        settings.fund_col,
        settings.benchmark_col,
        sd,
        ed,
    )

    return ReturnsResponse(
        start_date=start_date,
        end_date=end_date,
        fund_geom=fund_geom,
        benchmark_geom=bench_geom,
        alpha=alpha,
    )

@app.get("/exposure-diff", response_model=ExposureDiffResponse)
def get_exposure_diff(
    start_date: str = Query(...),
    end_date: str = Query(...),
    group_by: str = Query("Antipodes Region"),
    index: str | None = Query(None),
):
    if group_by not in constituents_df.columns:
        raise HTTPException(status_code=400, detail=f"Group-by column '{group_by}' not found")

    try:
        sd = pd.to_datetime(start_date)
        ed = pd.to_datetime(end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format")

    out = exposure_difference(
        constituents_df,
        settings.date_col_constituents,
        settings.weight_col,
        group_by,
        sd,
        ed,
        settings.index_col if index else None,
        index,
    )

    results = [
        ExposureDiffItem(
            group=str(row[group_by]),
            sum_weight_start=float(row["sum_weight_start"]),
            sum_weight_end=float(row["sum_weight_end"]),
            difference=float(row["difference"]),
        )
        for _, row in out.iterrows()
    ]

    return ExposureDiffResponse(
        group_by=group_by,
        start_date=start_date,
        end_date=end_date,
        index=index,
        results=results,
    )
