import asyncio
import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, field_validator
from pydantic_extra_types.coordinate import Latitude, Longitude

load_dotenv()
KEY = os.environ["OPENWEATHER_KEY"]          # raises immediately if missing

class WeatherModel(BaseModel):
    city: str
    state: str
    country: str
    desc: str
    temp: float
    lat: Latitude
    long: Longitude
    visibility: int | None = None            # Vancouver-style optional field

    @field_validator("temp")
    @classmethod
    def validate_temp(cls, value: float) -> float:
        if value > 60.0:
            raise ValueError("Extreme hot weather")
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        return round(value, 1)


async def current(client: httpx.AsyncClient, city: str, state: str, country: str) -> WeatherModel:
    try:
        geo_resp = await client.get(
            "/geo/1.0/direct",
            params={"q": f"{city},{state},{country}", "limit": 1, "appid": KEY},
        )
        geo_resp.raise_for_status()
        geo = geo_resp.json()
        if not geo:
            raise ValueError(f"no geocode match for {city},{state},{country}")
        lat, lon = geo[0]["lat"], geo[0]["lon"]

        wx_resp = await client.get(
            "/data/2.5/weather",
            params={"lat": lat, "lon": lon, "units": "metric", "appid": KEY},
        )
        wx_resp.raise_for_status()
        d = wx_resp.json()

        return WeatherModel.model_validate({
            "city": d["name"],
            "state": state,
            "country": d["sys"]["country"],
            "desc": d["weather"][0]["description"],
            "temp": d["main"]["temp"],
            "lat": d["coord"]["lat"],
            "long": d["coord"]["lon"],
            "visibility": d.get("visibility"),
        })

    except httpx.HTTPStatusError as e:
        print(f"{city}: HTTP {e.response.status_code}: {e.response.text[:200]}")
        if e.response.status_code == 429:
            print(f"{city}: rate limited, Retry-After={e.response.headers.get('Retry-After', '?')}")
        raise
    except httpx.TimeoutException:
        print(f"{city}: request timed out")
        raise
    except ValidationError as e:
        print(f"{city}: validation failed: {e.errors()}")
        raise
