import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

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

# Pivot the DataFrame
pivot_df = merged_df.pivot_table(
    index=["state", "time", "temperature_2m", "cloud_cover", "wind_speed_100m"],
    columns="fueltype",
    values="value",
    fill_value=0  # Replace NaN with 0 or any other value you prefer
).reset_index()

# Optional: Rename columns if necessary
pivot_df.columns.name = None  # Remove the name for the columns index
pivot_df.rename(columns={'SUN': 'sun_value', 'WND': 'wind_value'}, inplace=True)

# Display the transformed DataFrame
pivot_df['sun_value'] = pivot_df['sun_value'].where(pivot_df['sun_value'] >= 0, 0)
pivot_df['wind_value'] = pivot_df['wind_value'].where(pivot_df['wind_value'] >= 0, 0)

pivot_df['sum_value'] = pivot_df['sun_value'] + pivot_df['wind_value']



# Optionally, save the transformed DataFrame to a JSON file
# pivot_df.to_json("transformed_pivot_data.json", orient="records", lines=True)

# Assuming pivot_df is your DataFrame with the relevant columns
X = pivot_df[['temperature_2m', 'cloud_cover', 'wind_speed_100m']]
pivot_df['sum_value'] = (pivot_df['sum_value'] - pivot_df['sum_value'].min()) / (pivot_df['sum_value'].max() - pivot_df['sum_value'].min())
y = pivot_df[['sum_value']]


print(pivot_df)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Standardize the feature data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Reshape the data for LSTM (samples, time steps, features)
# Here, we are using 1 time step, hence we add a new axis
X_train_scaled = X_train_scaled[:, np.newaxis, :]  # Shape: (samples, time_steps=1, features=3)
X_test_scaled = X_test_scaled[:, np.newaxis, :]    # Shape: (samples, time_steps=1, features=3)

# Build the LSTM model
model = keras.Sequential([
    layers.LSTM(64, activation='relu', input_shape=(X_train_scaled.shape[1], X_train_scaled.shape[2])),
    layers.Dense(32, activation='relu'),
    layers.Dense(1)  # Output layer with 2 neurons for sun_value and wind_value
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mse'])

# Train the model
history = model.fit(X_train_scaled, y_train, epochs=100, batch_size=32, validation_split=0.2)

# Evaluate the model
test_loss, test_mae = model.evaluate(X_test_scaled, y_test)
print(f'Test MAE: {test_mae:.2f}')

# Make predictions
predictions = model.predict(X_test_scaled)

# Create a DataFrame for the predictions
# predicted_df = pd.DataFrame(predictions, columns=['predicted_sun_value', 'predicted_wind_value'])
predicted_df = pd.DataFrame(predictions, columns=['predicted_sum_value'])

print(predicted_df)