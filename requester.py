import datetime
import os

import requests

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
zipcode = 'L1' # Only first part is required
country_code = 'GB'

def calculate_direction(degrees: int) -> str:
    # Ensure degrees are within 0-360
    degrees %= 360
    
    # Define the 8 directions
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    # Calculate index
    # Adding 22.5 offsets the degree so that N covers 337.5 to 22.5
    idx = int((degrees + 22.5) / 45) % 8
    
    return directions[idx]


class WeatherData:
    def __init__(self, context):
        self.name = context.get('name')
        self.humidity = context.get('humidity')
        self.temp = context.get('temp')
        self.temp_max = context.get('temp_max')
        self.temp_min = context.get('temp_min')
        self.is_cold = context.get('is_cold')
        self.weather_type = context.get('weather_type')
        self.weather_desc = context.get('weather_desc')
        self.weather_id = context.get('weather_id')
        self.wind_speed = context.get('wind_speed')
        self.wind_degrees = context.get('wind_degrees')
        self.sunrise  = context.get('sunrise')
        self.sunset = context.get('sunset')
        self.is_day = context.get('is_day')
        self.wind_direction = calculate_direction(self.wind_degrees)

    def __repr__(self):
        return f'It is {self.temp}C! There is a {self.wind_speed}mph {self.wind_directon} wind'


def _safe_extract(target_dict: dict | None, key):
    return target_dict.get(key) if target_dict else None


def get_coords(zipcode: str, country_code: str) -> dict:
    """
    Get lat/lon coordinates from api.
    
    Returns keys zip, name, lat, lon, country.
    """
    base_url = f'http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},{country_code}&appid={api_key}'
    r = requests.get(base_url)
    response = r.json()
    return response


def get_weather(lat: float, lon: float) -> dict:
    """Call weather API and receive response"""
    base_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    r = requests.get(base_url)
    response = r.json()
    return response


def parse_weather(weather_data: dict) -> WeatherData:
    weather = weather_data.get('weather')

    if isinstance(weather, list):
        weather = weather[0]
    elif isinstance(weather, dict):
        pass
    else:
        raise ValueError(f'unknown type for weather detail: {type(weather)}')

    main_data = weather_data.get('main')
    wind_data = weather_data.get('wind')
    sys_data = weather_data.get('sys')

    # times are in unix, need to be translated
    sunrise = _safe_extract(sys_data, 'sunrise')
    sunset = _safe_extract(sys_data, 'sunset')

    if sunrise:
        sunrise_dt = datetime.datetime.fromtimestamp(int(sunrise))
        sunrise_t = sunrise_dt.time().strftime('%H:%M') # For sunrise/sunset clocks

    if sunset:
        sunset_dt = datetime.datetime.fromtimestamp(int(sunset))
        sunset_t = sunset_dt.time().strftime('%H:%M')
    else:
        sunrise_dt = None
        sunset_dt = None
        sunrise_t = None
        sunset_t = None

    # Take sunrise & sunset data
    current_ts = datetime.datetime.now()
    is_day = True if current_ts > sunrise_dt else False or current_ts < sunset_dt

    temp = _safe_extract(main_data, 'temp_min')

    # How hot/cold
    is_cold = True if temp < 8 else False

    w = WeatherData(context={
        'humidity': _safe_extract(main_data, 'humidity'),
        'sunrise': sunrise_t,
        'sunset': sunset_t,
        'is_day': is_day,
        'temp_min': _safe_extract(main_data, 'temp_min'),
        'temp_max': _safe_extract(main_data, 'temp_max'),
        'temp': temp,
        'is_cold': is_cold,
        'weather_type': _safe_extract(weather, 'main'),
        'weather_desc': _safe_extract(weather, 'description'),
        'weather_id': _safe_extract(weather, 'id'),
        'wind_speed': _safe_extract(wind_data, 'speed'),
        'wind_degrees': _safe_extract(wind_data, 'deg'),
        'name': _safe_extract(weather_data, 'name')
        }    
    )
    return w


def request_weather() -> WeatherData:
    geo_data = get_coords(zipcode=zipcode, country_code=country_code)
    lat = geo_data.get('lat')
    lon = geo_data.get('lon')

    weather_data = get_weather(lat=lat, lon=lon)

    output = parse_weather(weather_data)
    return output

if __name__ == '__main__':
    data = request_weather()
    print(data)