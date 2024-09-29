import requests
import json
from datetime import datetime

# Define the API key and URL
API_KEY = 'mLJuZa8xlTL8uYh5KXDWHK7lYmsXVTcIC3AklQAz'
url = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
params = {
    "frequency": "local-hourly",
    "data[0]": "value",
    "facets[fueltype][]": ["SUN", "WND"],
    "facets[respondent][]": ["CAL", "FLA", "NY", "TEN", "TEX"],
    "start": "2024-09-01T00-04:00",
    "end": "2024-09-25T00-04:00",
    "sort[0][column]": "period",
    "sort[0][direction]": "desc",
    "offset": 0,
    "length": 5000,
    "api_key": API_KEY
}

# Make the API request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    
    # Initialize a new dictionary to store the transformed data
    transformed_data = {}

    # Loop through the data and format it
    for entry in data['response']['data']:
        # Use the period as the outer key
        period = entry['period'].replace("T", " ") + ":00"  # Add seconds
        
        # Check if the fuel type is SUN or WND
        if entry['fueltype'] in ["SUN", "WND"]:
            # Initialize nested dictionary for the period if not already done
            if period not in transformed_data:
                transformed_data[period] = {}

            # Add fuel data organized by respondent (state)
            transformed_data[period][entry['respondent']] = {
                "fueltype": entry['fueltype'],
                "value": float(entry['value'])  # Convert value to float
            }

    # Print the transformed data
    # print(json.dumps(transformed_data, indent=4))

    # Optionally, save the transformed data to a JSON file
    with open('transformed_eia_data_by_state.json', 'w') as json_file:
        json.dump(transformed_data, json_file, indent=4)
else:
    print(f"Error: {response.status_code} - {response.text}")
