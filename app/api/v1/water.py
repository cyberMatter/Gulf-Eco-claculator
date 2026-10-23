from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.factors import desal_factor, grid_factor, heat_factor, technologies

router = APIRouter()


class WaterRequest(BaseModel):
    litres: float = Field(..., gt=0, description="Desalinated water used, in litres")
    technology: Optional[str] = Field(None, description="swro, med or msf (default: swro)")


class WaterResponse(BaseModel):
    cubic_metres: float
    technology: str
    electricity_kwh: float
    heat_mj: float
    kg_co2_electricity: float
    kg_co2_heat: float
    kg_co2: float
    warnings: List[str]


@router.post("/footprint", response_model=WaterResponse)
def footprint(req: WaterRequest) -> WaterResponse:
    try:
        name, d = desal_factor(req.technology)
    except KeyError:
        raise HTTPException(422, f"Unknown technology. Use one of: {technologies()}")
    g, h = grid_factor(), heat_factor()
    m3 = req.litres / 1000
    elec_kwh = m3 * d["electricity_kwh_per_m3"]
    heat_mj = m3 * d["heat_mj_per_m3"]
    co2_elec = elec_kwh * g["value"]
    co2_heat = heat_mj * h["natural_gas_kg_co2_per_mj"]

    warnings = []
    if not d["qatar_specific"]:
        warnings.append(f"Energy use for '{name}' is a global literature value, not a Qatar measurement.")
    if heat_mj > 0:
        warnings.append(
            "Heat is assumed to come from natural gas combustion. Plants that use waste heat emit less."
        )
    return WaterResponse(
        cubic_metres=round(m3, 4),
        technology=name,
        electricity_kwh=round(elec_kwh, 4),
        heat_mj=round(heat_mj, 4),
        kg_co2_electricity=round(co2_elec, 4),
        kg_co2_heat=round(co2_heat, 4),
        kg_co2=round(co2_elec + co2_heat, 4),
        warnings=warnings,
    )
