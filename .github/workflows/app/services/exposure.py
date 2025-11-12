import pandas as pd

def exposure_sum_grouped(df, date_col, weight_col, group_by_col, asof_date, index_col=None, index_val=None):
    sub = df[df[date_col] == asof_date]
    if index_col and index_val:
        sub = sub[sub[index_col] == index_val]
    grouped = sub.groupby(group_by_col)[weight_col].sum().reset_index()
    grouped.rename(columns={weight_col: "sum_weight"}, inplace=True)
    return grouped

def exposure_difference(df, date_col, weight_col, group_by_col, start_date, end_date, index_col=None, index_val=None):
    s = exposure_sum_grouped(df, date_col, weight_col, group_by_col, start_date, index_col, index_val)
    e = exposure_sum_grouped(df, date_col, weight_col, group_by_col, end_date, index_col, index_val)

    merged = pd.merge(s, e, on=group_by_col, how="outer", suffixes=("_start", "_end")).fillna(0)
    merged["difference"] = merged["sum_weight_end"] - merged["sum_weight_start"]
    return merged
