from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.factors import grid_factor

router = APIRouter()


class ElectricityRequest(BaseModel):
    kwh: float = Field(0, ge=0, description="Other electricity use in kWh (non-AC)")
    ac_kw: float = Field(0, ge=0, description="Average AC power draw in kW")
    ac_hours_per_day: float = Field(0, ge=0, le=24)
    days: int = Field(1, ge=1, le=366)


class ElectricityResponse(BaseModel):
    total_kwh: float
    ac_kwh: float
    other_kwh: float
    kg_co2: float
    factor_kg_co2_per_kwh: float
    factor_source: str
    warnings: List[str]


@router.post("/electricity", response_model=ElectricityResponse)
def electricity(req: ElectricityRequest) -> ElectricityResponse:
    ac_kwh = req.ac_kw * req.ac_hours_per_day * req.days
    total = ac_kwh + req.kwh
    if total == 0:
        raise HTTPException(422, "Provide kwh, or ac_kw with ac_hours_per_day.")
    f = grid_factor()
    warnings = [] if f["verified"] else ["Grid factor is unverified."]
    return ElectricityResponse(
        total_kwh=round(total, 3),
        ac_kwh=round(ac_kwh, 3),
        other_kwh=round(req.kwh, 3),
        kg_co2=round(total * f["value"], 3),
        factor_kg_co2_per_kwh=f["value"],
        factor_source=f["source"],
        warnings=warnings,
    )
