import pandas as pd
from fastapi import HTTPException
from app.settings import settings

_df_cache = None

def load_constituents_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        try:
            xl = pd.ExcelFile(settings.excel_path)
            df = xl.parse(settings.sheet_constituents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read Excel: {e}")

        # Normalize column names (strip, unify)
        df.columns = [c.strip() for c in df.columns]

        # Basic validations
        for required in [settings.date_column, settings.weight_column]:
            if required not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing column '{required}' in sheet {settings.sheet_constituents}")

        # Parse date
        df[settings.date_column] = pd.to_datetime(df[settings.date_column], errors="coerce")
        if df[settings.date_column].isna().any():
            raise HTTPException(status_code=400, detail="Invalid date values in Date column")

        # Ensure weight numeric
        df[settings.weight_column] = pd.to_numeric(df[settings.weight_column], errors="coerce")
        if df[settings.weight_column].isna().any():
            raise HTTPException(status_code=400, detail="Invalid numeric values in Weight column")

        _df_cache = df
    return _df_cache

