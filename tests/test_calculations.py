from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_electricity_ac_only():
    r = client.post("/api/v1/carbon/electricity", json={"ac_kw": 2, "ac_hours_per_day": 10, "days": 30})
    assert r.status_code == 200
    body = r.json()
    assert body["total_kwh"] == 600
    assert body["kg_co2"] == round(600 * 0.4606, 3)


def test_electricity_combined():
    r = client.post("/api/v1/carbon/electricity", json={"kwh": 100, "ac_kw": 1, "ac_hours_per_day": 5})
    assert r.json()["total_kwh"] == 105


def test_electricity_empty_rejected():
    assert client.post("/api/v1/carbon/electricity", json={}).status_code == 422


def test_negative_rejected():
    assert client.post("/api/v1/carbon/electricity", json={"kwh": -5}).status_code == 422


def test_water_swro_default():
    r = client.post("/api/v1/water/footprint", json={"litres": 1000})
    body = r.json()
    assert r.status_code == 200
    assert body["technology"] == "swro"
    assert body["electricity_kwh"] == 4.1
    assert body["heat_mj"] == 0
    assert body["kg_co2"] == round(4.1 * 0.4606, 4)
    assert any("not a Qatar measurement" in w for w in body["warnings"])


def test_water_msf_includes_heat():
    body = client.post("/api/v1/water/footprint", json={"litres": 1000, "technology": "msf"}).json()
    expected = 4.0 * 0.4606 + 333 * 0.0561
    assert abs(body["kg_co2"] - expected) < 1e-3
    assert any("natural gas" in w for w in body["warnings"])


def test_water_scales_linearly():
    a = client.post("/api/v1/water/footprint", json={"litres": 500, "technology": "med"}).json()
    b = client.post("/api/v1/water/footprint", json={"litres": 1000, "technology": "med"}).json()
    assert abs(b["kg_co2"] - 2 * a["kg_co2"]) < 1e-3


def test_factors_endpoint_has_sources():
    f = client.get("/api/v1/factors").json()
    assert f["grid_electricity"]["verified"] is True
    assert all(t["source_url"] for t in f["desalination"]["technologies"].values())


def test_water_unknown_technology():
    r = client.post("/api/v1/water/footprint", json={"litres": 10, "technology": "magic"})
    assert r.status_code == 422


def test_water_requires_positive():
    assert client.post("/api/v1/water/footprint", json={"litres": 0}).status_code == 422
