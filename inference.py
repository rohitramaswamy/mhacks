import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim

# Load the saved model
model = load_model('my_model.h5')

# Example: Preparing new input data for inference
# Let's assume `X_new` is your new data for inference
# For demonstration, we are using some example data. Replace this with your actual data.
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
geolocator = Nominatim(user_agent="geoapiExercises")


city = input("Enter a city name: ")
location = geolocator.geocode(city)

lattitude = 0
longitude = 0

if location:
    lattitude = location.latitude
    longitude = location.longitude
else:
    exit(1, "Location not found")
    

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": lattitude,
	"longitude": longitude,
	"hourly": ["temperature_2m", "cloud_cover", "wind_speed_80m", "wind_speed_120m"],
	"timezone": "America/New_York",
	"past_days": 3,
	"forecast_days": 14
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
hourly_wind_speed_80m = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_120m = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["wind_speed_80m"] = hourly_wind_speed_80m
hourly_data["wind_speed_120m"] = hourly_wind_speed_120m
hourly_data["wind_speed_100m"] = ((hourly_data["wind_speed_80m"] + hourly_data["wind_speed_120m"]) / 2)
hourly_dataframe = pd.DataFrame(data = hourly_data)
hourly_dataframe.drop("wind_speed_120m", axis="columns",inplace=True)
hourly_dataframe.drop("wind_speed_80m", axis="columns",inplace=True)
hourly_dataframe.drop("date", axis="columns",inplace=True)
print(hourly_dataframe)

# X_new = pd.DataFrame({
#     'temperature_2m': [22.5, 18.3],  # Example values
#     'cloud_cover': [50.0, 80.0],
#     'wind_speed_100m': [12.0, 8.0]
# })

# Standardize the new input data using the same scaler used during training
scaler = StandardScaler()  # Ensure this is the same scaler as used during training
X_new_scaled = scaler.fit_transform(hourly_dataframe)  # In real use, you should use the scaler fitted on the training data

# Reshape the input data to match the LSTM input format: (samples, time_steps=1, features=3)
X_new_scaled = X_new_scaled[:, np.newaxis, :]  # Shape: (samples, time_steps=1, features=3)

# Make predictions using the loaded model
predictions = model.predict(X_new_scaled)

mean = np.mean(predictions)
var = np.var(predictions)
weight = mean/var
with open("output.txt", "w") as file:
    print(weight, file=file)