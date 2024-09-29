import json
import pandas as pd
# Read the first JSON file
with open("weather_data.json", "r") as file:
    data1 = json.load(file)

# Read the second JSON file
with open("transformed_eia_data_by_state.json", "r") as file:
    data2 = json.load(file)

# Convert JSON 1 to DataFrame
rows1 = []
for state, times in data1.items():
    for time, data in times.items():
        row = {"state": state, "time": time, **data}
        rows1.append(row)
df1 = pd.DataFrame(rows1)

# Convert JSON 2 to DataFrame
rows2 = []
for state, times in data2.items():
    for time, fuels in times.items():
        for fuel in fuels:
            row = {
                "state": state,
                "time": time,
                "fueltype": fuel["fueltype"],
                "value": fuel["value"],
            }
            rows2.append(row)
df2 = pd.DataFrame(rows2)

# Merging the two dataframes
merged_df = pd.merge(df1, df2, on=["state", "time"], how="inner")

# Display the merged dataframe
print(merged_df)
