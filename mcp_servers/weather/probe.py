from dotenv import load_dotenv
from pydantic import BaseModel
import os
from pydantic import BaseModel, ValidationError
from pydantic.functional_validators import field_validator
from pydantic_extra_types.coordinate import Latitude, Longitude, Coordinate
import httpx
import asyncio


load_dotenv()

openweatherapi = os.getenv('OPENWEATHER_KEY')

class WeatherModel(BaseModel):
    city: str
    state: str
    country: str
    desc: str
    temp: float
    @field_validator('temp')
    @classmethod
    def validate_temp(cls, value: float) -> float:
        if value > 60.0:
            raise ValueError("Extreme hot weather")

        if value < -273.15:
            raise ValueError("Temperature below Absolute zero")
        return round(value, 1)
    lat: Latitude
    long: Longitude

# test_json_data = '''{
#     "city":"calgary",
#     "state":"AB",
#     "country":"CA",
#     "desc":"calgary city",
#     "temp":-1.4,
#     "lat": 40.0,
#     "long": -87.9
# }
# '''

# user_input = WeatherModel.model_validate_json(test_json_data)
# print(user_input.model_dump_json(indent=2))
# print(user_input.city)



# # Need to pull from this url
# # http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
## https://api.openweathermap.org/data/4.0/onecall/current?lat={lat}&lon={lon}&appid={API key}


# gcode_direct_query = f"direct?q={user_input.city},{user_input.state},{user_input.country}&limit=5&appid={openweatherapi}"
# full_url_geocoding = base_weather_url+geo_endpoint+direct_query
# print(full_url_geocoding)

# response = httpx.get(full_url_geocoding)
# print(response.status_code)
# print(response.content)
# print(response.json())
# lat = response.json()[0].get('lat')
# long = response.json()[0].get('lon')

# print(f"lat = {lat}, long = {long}")
# current_temp_query = f"/onecall/current?lat={lat}&{long}"

# # full_current_weather = base_weather_url+data_endpoint+current_temp_query
# full_current_weather = f'https://api.openweathermap.org/data/2.5/weather?lat=51.0456064&lon=-114.057541&units=metric&appid={openweatherapi}'

# current_weather_response = httpx.get(full_current_weather)
# print(current_weather_response.status_code)
# print(current_weather_response.content)
# print(current_weather_response.json())




async def fetch_gcodes(urls:list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

async def current(urls:list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

def extract_lat_long(results: list[dict]) -> list[dict]:
    latlong_list = []
    for result in results:
        lat = result[0].get('lat')
        long = result[0].get('lon')
        lat_long_dict = {"lat":lat, "long":long}
        latlong_list.append(lat_long_dict)
        print(f"lat = {lat}, long = {long}")
    return latlong_list

async def main():
    base_weather_url = "http://api.openweathermap.org/"
    geo_endpoint = "geo/1.0/"
    # data_endpoint = "data/2.5/weather"

    city_list = [{
        "city":"calgary",
        "state":"AB",
        "country":"CA"
    },
    {     "city":"Vancouver",
    "state":"BC",
    "country":"CA"  },
    {
        "city":"regina",
        "state":"SK",
        "country":"CA"
    }
    ]

    urls = []
    for city in city_list:
        gcode_direct_query = base_weather_url+geo_endpoint+f"direct?q={city.get('city')},{city.get('state')},{city.get('country')}&limit=5&appid={openweatherapi}"
        print(gcode_direct_query)
        urls.append(gcode_direct_query)

    print(urls)

    results = await fetch_gcodes(urls)
    print(results)

    list_latlong = extract_lat_long(results)
    weather_urls = []
    for latlong in list_latlong:
        print(latlong)
        weather_direct_query = f"https://api.openweathermap.org/data/2.5/weather?lat={latlong.get('lat')}&lon={latlong.get('long')}&units=metric&appid={openweatherapi}"
        print(weather_direct_query)
        weather_urls.append(weather_direct_query)

    current_weather = await current(weather_urls)
    print(current_weather)


asyncio.run(main())
