from pydantic import BaseSettings

class Settings(BaseSettings):
    excel_path: str = "app/data/Returns_and_Constituent_Data.xlsx"
    sheet_returns: str = "Returns"
    sheet_constituents: str = "IndexConstituents"

    # Column names (adjust to match your Excel headers)
    date_col_returns: str = "ReturnDate"
    fund_col: str = "FundReturn"
    benchmark_col: str = "BenchmarkReturn"

    date_col_constituents: str = "Date"
    weight_col: str = "Weight"
    index_col: str = "Index"
    region_col: str = "Antipodes Region"

    class Config:
        env_file = ".env"

settings = Settings()
