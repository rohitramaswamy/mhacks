import requests
import json

# Define the API key and URL
API_KEY = 'mLJuZa8xlTL8uYh5KXDWHK7lYmsXVTcIC3AklQAz'
url = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
params = {
    "frequency": "local-hourly",
    "data[0]": "value",
    "facets[fueltype][]": ["SUN", "WND"],
    "facets[respondent][]": ["CAL", "FLA", "NY", "TEN", "TEX"],
    "start": "2024-09-24T00-04:00",
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
    
    # Print the JSON response
    print(json.dumps(data, indent=4))
    
    # Optionally, save the data to a JSON file
    with open('eia_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
else:
    print(f"Error: {response.status_code} - {response.text}")
