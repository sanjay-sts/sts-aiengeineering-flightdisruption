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



async def current(client :httpx.AsyncClient, city: str, state: str, country: str) -> WeatherModel | None:
    print("current called")
    try:
        params = {"q": f"{city},{state},{country}", "limit": 1, "appid": openweatherapi}
        print(params)
        gecode = await client.get("geo/1.0/direct?q=", params=params)
        print(gecode.raise_for_status())
        print(gecode.status_code)
        print(gecode.json())
        lat = gecode.json()[0].get('lat')
        long = gecode.json()[0].get('lon')
        print(lat, long)
        print("calling current weather")
        city_weather = await client.get("data/2.5/weather?", params={"lat":lat, "lon":long, "units":"metric", "appid":openweatherapi})
        print(city_weather)
        print(city_weather.status_code)
        print(city_weather.json())
        wx_city = city_weather.json().get('name')
        wx_country = city_weather.json().get('sys').get('country')
        wx_description = city_weather.json().get('weather')[0].get('description')
        wx_temp = city_weather.json().get('main').get('temp')
        wx_lat= city_weather.json().get('coord').get('lat')
        wx_long = city_weather.json().get('coord').get('lon')
        wx_visibility = city_weather.json().get('visibility')
        print(wx_city,state, wx_country, wx_description, wx_temp, wx_lat, wx_long, wx_visibility)
        weather_data = {
            "city" : wx_city,
            "state" : state,
            "country" : wx_country,
            "desc": wx_description,
            "temp": wx_temp,
            "lat": wx_lat,
            "long": wx_long,
            "visibility": wx_visibility
        }
        return WeatherModel.model_validate(weather_data)
    except httpx.HTTPStatusError as e:
        # 4xx or 5xx response
        print(f"HTTP error {e.response.status_code}: {e.response.text[:200]}")

        if e.response.status_code == 401:
            print("Authentication required")
        elif e.response.status_code == 403:
            print("Access forbidden")
        elif e.response.status_code == 404:
            print("Resource not found")
        elif e.response.status_code == 429:
            retry_after = e.response.headers.get("Retry-After", "unknown")
            print(f"Rate limited. Retry after: {retry_after}")
        elif e.response.status_code >= 500:
            print("Server error - try again later")

        return None
    except httpx.TimeoutException:
        print(f"Request timed out")
        return None




async def main():
    base_weather_url = "https://api.openweathermap.org/"
    geo_endpoint = "geo/1.0/"
    data_endpoint = "data/2.5/weather"

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

    async with httpx.AsyncClient(base_url=base_weather_url, timeout=10) as client:
        tasks = []
        try:
            for item in city_list:
                city = item.get('city')
                state = item.get('state')
                country = item.get('country')
                print(city, state, country)
                task = current(client, city, state, country)
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print("results called")
            print(results)
        except:
            print("error parsing")




asyncio.run(main())


# def extract_lat_long(results: list[dict]) -> list[dict]:
#     latlong_list = []
#     for result in results:
#         lat = result[0].get('lat')
#         long = result[0].get('lon')
#         lat_long_dict = {"lat":lat, "long":long}
#         latlong_list.append(lat_long_dict)
#         print(f"lat = {lat}, long = {long}")
#     return latlong_list
#
#
# # test_json_data = '''{
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



# async def extract_weather(city_list):
#     try:
#         urls = []
#         for city in city_list:
#             gcode_direct_query = base_weather_url+geo_endpoint+f"direct?q={city.get('city')},{city.get('state')},{city.get('country')}&limit=5&appid={openweatherapi}"
#             print(gcode_direct_query)
#             urls.append(gcode_direct_query)
#             print(urls)
#         async with httpx.AsyncClient(timeout=10) as client:

#     except:
#         pass



# async def fetch_gcodes(urls:list[str]) -> list[dict] | None:
#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             tasks = [client.get(url) for url in urls]
#             responses = await asyncio.gather(*tasks)
#             for r in responses: r.raise_for_status()
#             return [r.json() for r in responses]
#     except httpx.HTTPStatusError as e:
#             print(f"HTTP error {e.response.status_code}: {e.response.text[:200]}")
