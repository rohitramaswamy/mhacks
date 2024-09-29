import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import json
import pytz

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define the API URL
url = "https://archive-api.open-meteo.com/v1/archive"

# List of latitudes, longitudes, timezones, and corresponding states
locations = [
    {"state": "NY", "latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
    {"state": "TEX", "latitude": 31.9686, "longitude": -99.9018, "timezone": "America/Chicago"},
    {"state": "TEN", "latitude": 35.5175, "longitude": -86.5804, "timezone": "America/Chicago"},
    {"state": "CAL", "latitude": 36.7783, "longitude": -119.4179, "timezone": "America/Los_Angeles"},
]

# Define start and end dates
start_date = "2024-08-29"
end_date = "2024-09-25"

# Initialize a dictionary to hold all locations' weather data
all_locations_data = {}

# Iterate through the list of locations
for location in locations:
    lat = location["latitude"]
    lon = location["longitude"]
    tz = location["timezone"]
    state = location["state"]

    # Define parameters for the current location
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "cloud_cover", "wind_speed_100m"],
        "timezone": tz
    }

    # Request data from the API
    responses = openmeteo.weather_api(url, params=params)

    # Process the first location response
    response = responses[0]
    
    # Extract and process hourly data
    hourly = response.Hourly()
    hourly_time_utc = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    # Localize and format times in the specified format
    timezone = pytz.timezone(tz)
    hourly_time = [time.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S %z') for time in hourly_time_utc]
    hourly_time = [time[:-2] + '-' + time[-2:] for time in hourly_time]  # Replace the last 2 digits with a hyphen

    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_100m = hourly.Variables(2).ValuesAsNumpy()

    # Create a nested dictionary with state as the first key and time as the second key
    if state not in all_locations_data:
        all_locations_data[state] = {}

    # Add the hourly data to the corresponding state
    for time, temp, cloud, wind in zip(hourly_time, hourly_temperature_2m, hourly_cloud_cover, hourly_wind_speed_100m):
        all_locations_data[state][time] = {
            "temperature_2m": float(temp),  # Convert to float for JSON compatibility
            "cloud_cover": float(cloud),     # Convert to float for JSON compatibility
            "wind_speed_100m": float(wind)   # Convert to float for JSON compatibility
        }

# Convert the entire dictionary to a JSON object
all_locations_json = json.dumps(all_locations_data, indent=4)

# Output the JSON data
# print(all_locations_json)

# Optionally, write the JSON data to a file
with open('weather_data.json', 'w') as json_file:
    json_file.write(all_locations_json)
