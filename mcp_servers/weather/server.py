import asyncio

from pydantic import BaseModel, field_validator
from pydantic_extra_types.coordinate import Latitude, Longitude

from libs.http_base import ApiToolServer

KEY_NAME = "OPENWEATHER_KEY"
BASE_URL = "https://api.openweathermap.org"
GEO_CODE_PATH = "/geo/1.0/direct"
WEATHER_PATH = "/data/2.5/weather"


class WeatherModel(BaseModel):
    city: str
    state: str
    country: str
    desc: str
    temp: float
    lat: Latitude
    long: Longitude
    visibility: int | None = None

    @field_validator("temp")
    @classmethod
    def validate_temp(cls, value: float) -> float:
        if value > 60.0:
            raise ValueError("Extreme hot weather")
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        return round(value, 1)


class WeatherServer(ApiToolServer):
    def __init__(self):
        super().__init__("weather-mcp", KEY_NAME)

    @property
    def base_url(self) -> str:
        return BASE_URL

    async def current_weather(self, city: str, state: str, country: str) -> WeatherModel:
        geo = await self.get(GEO_CODE_PATH, q=f"{city},{state},{country}", limit=1)
        if not geo:
            raise ValueError(f"no geocode match for {city},{state},{country}")
        lat, lon = geo[0]["lat"], geo[0]["lon"]

        d = await self.get(WEATHER_PATH, lat=lat, lon=lon, units="metric")
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


async def main():
    city_list = [
        {"city": "Calgary", "state": "AB", "country": "CA"},
        {"city": "Vancouver", "state": "BC", "country": "CA"},
        {"city": "Regina", "state": "SK", "country": "CA"},
        {"city": "Xyzabc", "state": "AB", "country": "CA"},   # deliberate failure
    ]

    async with WeatherServer() as ws:
        print(ws)
        tasks = [ws.current_weather(**item) for item in city_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for item, result in zip(city_list, results):
        if isinstance(result, Exception):
            print(f"{item['city']}: FAILED ({type(result).__name__}: {result})")
        else:
            print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
