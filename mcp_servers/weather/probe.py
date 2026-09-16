from dotenv import load_dotenv
from pydantic import BaseModel
import os
from pydantic import BaseModel, ValidationError
from pydantic.functional_validators import field_validator
from pydantic_extra_types.coordinate import Latitude, Longitude, Coordinate



load_dotenv()

openweatherapi = os.getenv('OPENWEATHER_KEY')

class WeatherModel(BaseModel):
    city: str
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

test_json_data = '''{
    "city":"calgary",
    "desc":"calgary city",
    "temp":67.4,
    "lat": 40.0,
    "long": -87.9
}
'''

user_input = WeatherModel.model_validate_json(test_json_data)
print(user_input.model_dump_json(indent=2))
