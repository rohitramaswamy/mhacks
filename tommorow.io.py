import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import json

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define the API URL and parameters
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 42.278046,
    "longitude": -83.73822,
    "start_date": "2024-09-01",
    "end_date": "2024-09-25",
    "hourly": ["temperature_2m", "cloud_cover", "wind_speed_100m"],
    "timezone": "America/New_York"
}

# Request data from the API
responses = openmeteo.weather_api(url, params=params)

# Process the first location (add a for-loop if needed for multiple locations)
response = responses[0]

# Extract and process hourly data
hourly = response.Hourly()
hourly_time = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=hourly.Interval()),
    inclusive="left"
).strftime('%Y-%m-%d %H:%M:%S').tolist()

hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
hourly_wind_speed_100m = hourly.Variables(2).ValuesAsNumpy()

# Create a dictionary with the time as key and other variables as values
hourly_data_dict = {
    time: {
        "temperature_2m": float(temp),# Convert to float for JSON compatibility
        "cloud_cover": float(cloud),# Convert to float for JSON compatibility
        "wind_speed_100m": float(wind)# Convert to float for JSON compatibility
    }
    for time, temp, cloud, wind in zip(hourly_time, hourly_temperature_2m, hourly_cloud_cover, hourly_wind_speed_100m)
}

# Convert the dictionary to a JSON object
hourly_json_dict = json.dumps(hourly_data_dict, indent=4)

# # Output the JSON data
# print(hourly_json_dict)

# Optionally, write the JSON data to a file
with open('weather_data.json', 'w') as json_file:
    json_file.write(hourly_json_dict)