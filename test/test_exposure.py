import pandas as pd
from app.services.exposure import exposure_difference

def test_exposure_difference_basic():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2025-04-01","2025-04-01","2025-06-30","2025-06-30"]),
        "Weight": [0.10, 0.15, 0.12, 0.18],
        "Antipodes Region": ["North America","EM Asia","North America","EM Asia"],
        "Index": ["IdxA","IdxA","IdxA","IdxA"]
    })

    out = exposure_difference(
        df=df,
        date_col="Date",
        weight_col="Weight",
        group_by_col="Antipodes Region",
        start_date=pd.Timestamp("2025-04-01"),
        end_date=pd.Timestamp("2025-06-30"),
        index_filter_col="Index",
        index_filter_value="IdxA"
    )

    # EM Asia: 0.18 - 0.15 = 0.03
    # North America: 0.12 - 0.10 = 0.02
    assert set(out.columns) >= {"Antipodes Region","sum_weight_start","sum_weight_end","difference"}
    assert out.loc[out["Antipodes Region"]=="EM Asia","difference"].iloc[0] == 0.03
    assert out.loc[out["Antipodes Region"]=="North America","difference"].iloc[0] == 0.02
