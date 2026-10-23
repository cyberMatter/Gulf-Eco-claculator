# gulf-eco-calculator-api

Open-source REST API that estimates household carbon emissions and the carbon cost of desalinated water, using Qatar-specific factors (high AC loads, the local grid, desalination energy).

<!-- After deploying, add: **Live demo:** https://YOUR-SERVICE.onrender.com/docs -->

Interactive API docs are served at `/docs` when the app is running.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Or with Docker: `docker build -t gulf-eco . && docker run -p 8000:8000 gulf-eco`

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/carbon/electricity` | kWh and AC usage to kg CO2 |
| POST | `/api/v1/water/footprint` | litres of desalinated water to electricity, heat and kg CO2 |
| GET | `/api/v1/factors` | raw factors with sources and verification status |
| GET | `/health` | liveness check |

Examples:

```bash
curl -X POST localhost:8000/api/v1/carbon/electricity \
  -H "Content-Type: application/json" \
  -d '{"ac_kw": 2, "ac_hours_per_day": 10, "days": 30}'

curl -X POST localhost:8000/api/v1/water/footprint \
  -H "Content-Type: application/json" \
  -d '{"litres": 1000, "technology": "msf"}'
```

## Data and accuracy

All factors live in `app/core/emission_factors_qatar.json`, each with a source link, a `verified` flag (cited source) and a `qatar_specific` flag.

| Factor | Value | Source | Qatar-specific |
|---|---|---|---|
| Grid electricity | 0.4606 kgCO2/kWh | IEA 2025 (CO2 only) | Yes |
| Natural gas heat | 0.0561 kgCO2/MJ | IPCC 2006 default | No |
| SWRO | 4.1 kWh/m3 | Midpoint of 3.7-4.5, published review | No |
| MED | 2 kWh + 263 MJ per m3 | Same review | No |
| MSF | 4 kWh + 333 MJ per m3 | Same review | No |

Limitations:

- Desalination figures are global literature values, not Qatar measurements, and the API says so in every water response.
- Thermal plants (MED, MSF) are modelled with heat from natural gas combustion. Plants that use waste heat emit less.
- Grid emissions are CO2 only.

Qatar-specific values with citations are the most useful contribution.

## Deploy

A `render.yaml` blueprint is included: on Render choose New, then Blueprint, then select this repo.

## Alignment with Qatar National Vision 2030 & AYCMQA goals

- Supports the environmental development pillar of Qatar National Vision 2030 by making household energy and water impact measurable.
- Gives youth climate groups such as AYCMQA a documented, reusable calculation backend for footprint tools and awareness campaigns.
- Relevant to SDG 6 (clean water), SDG 7 (energy), SDG 12 (responsible consumption) and SDG 13 (climate action).

## Contributing

Issues and pull requests welcome. CI runs the test suite on every push and weekly.

## License

MIT. See `LICENSE`.
