from pydantic import BaseModel
from typing import List, Optional

class ReturnsResponse(BaseModel):
    start_date: str
    end_date: str
    fund_geom: float
    benchmark_geom: float
    alpha: float

class ExposureDiffItem(BaseModel):
    group: str
    sum_weight_start: float
    sum_weight_end: float
    difference: float

class ExposureDiffResponse(BaseModel):
    group_by: str
    start_date: str
    end_date: str
    index: Optional[str] = None
    results: List[ExposureDiffItem]
