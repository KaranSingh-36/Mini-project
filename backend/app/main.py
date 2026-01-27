import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
API_BASE = "https://api.openweathermap.org/data/2.5"

app = FastAPI(title="Weather AQI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


async def _call_openweather(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="OPENWEATHER_API_KEY is missing")

    params_with_key = {"appid": API_KEY, **params}
    url = f"{API_BASE}/{path}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params_with_key)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Upstream error: {exc}") from exc

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()


@app.get("/aqi")
async def get_aqi(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
) -> Dict[str, Any]:
    payload = await _call_openweather("air_pollution", {"lat": lat, "lon": lon})
    first_entry = payload.get("list", [{}])[0]
    return {
        "aqi": first_entry.get("main", {}).get("aqi"),
        "components": first_entry.get("components", {}),
        "timestamp": first_entry.get("dt"),
    }


@app.get("/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    units: str = Query("metric", description="Units: metric/imperial/standard"),
) -> Dict[str, Any]:
    payload = await _call_openweather(
        "weather",
        {
            "lat": lat,
            "lon": lon,
            "units": units,
        },
    )
    main = payload.get("main", {})
    wind = payload.get("wind", {})
    weather = (payload.get("weather") or [{}])[0]
    return {
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind_speed": wind.get("speed"),
        "condition": weather.get("description"),
        "city": payload.get("name"),
        "country": (payload.get("sys") or {}).get("country"),
    }


# TODO: add diet-related routes under /diet when ready.
