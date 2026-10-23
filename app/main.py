from fastapi import FastAPI

from app.api.v1 import carbon, water
from app.core.factors import load_factors

app = FastAPI(
    title="Gulf Eco Calculator API",
    description="Carbon and desalinated-water footprint calculations using Qatar-specific factors.",
    version="0.1.0",
)

app.include_router(carbon.router, prefix="/api/v1/carbon", tags=["carbon"])
app.include_router(water.router, prefix="/api/v1/water", tags=["water"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/v1/factors", tags=["data"])
def factors() -> dict:
    """Exposes the raw factors, including sources and verification status."""
    return load_factors()
