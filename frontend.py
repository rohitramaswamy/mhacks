import streamlit as st
import folium as fl
from streamlit_folium import st_folium
from inference import return_weight, get_lat_lon  # Import the custom function
import pandas as pd
from kserver import KServerLoadBalancer
import random  # Streamlit title

st.title("Load Balancer")

# Initialize session state for locations if not already done
if "locations" not in st.session_state:
    st.session_state.locations = []  # Initialize locations in session memory
if "city_weights" not in st.session_state:
    st.session_state.city_weights = []  # Initialize city weights in session memory
if "cities" not in st.session_state:
    st.session_state.cities = []  # To track the list of cities entered
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False  # Track if the button has been clicked

# Create two columns for layout
col1, col2 = st.columns([2, 1])  # Adjust the ratio for column widths

# Right column (City input and weight calculation)
with col2:
    # Add a text input to enter city names and store them in a list
    st.subheader("Enter cities:")
    city_list = st.text_input(
        "Enter city names separated by commas (e.g., New York, Los Angeles, Chicago)"
    )

    # Add a button to submit the entered city list
    if st.button("Submit"):
        # When the button is clicked, set flag and perform calculations
        st.session_state.button_clicked = True

        # Split city input by commas and strip whitespace
        cities = [city.strip() for city in city_list.split(",")]

        # Only update if there is new input
        if cities and cities != st.session_state.cities:
            # Store the entered cities
            st.session_state.cities = cities

            # Use the return_weight function to get weights for each city
            st.session_state.city_weights = [
                return_weight(city) for city in st.session_state.cities
            ]

            # Get the lat/lon for each city using the get_lat_lon function
            st.session_state.locations = [
                get_lat_lon(city) for city in st.session_state.cities
            ]

    # Show the results only if the button has been clicked at least once
    if st.session_state.button_clicked:
        data = {
            "City": st.session_state.cities,
            "Weight": st.session_state.city_weights,
        }
        df = pd.DataFrame(data)

        # Display the DataFrame
        st.dataframe(df)

# Left column (Map)
with col1:
    # Use the stored locations from session state
    locations = st.session_state.locations

    # Create a folium map centered on the first city if any cities are entered
    if locations:
        m = fl.Map(location=locations[0], zoom_start=4)
    else:
        # Default map center if no cities are entered
        m = fl.Map(location=[40.7128, -74.0060], zoom_start=4)

    # Add markers for the entered cities
    for loc in locations:
        fl.Marker(loc, popup=f"Location: {loc[0]}, {loc[1]}").add_to(m)

    # Connect each pin to every other pin (Complete Graph)
    for i in range(len(locations)):
        for j in range(i + 1, len(locations)):
            # Draw a line between every pair of locations
            fl.PolyLine(
                [locations[i], locations[j]], color="blue", weight=2.5, opacity=1
            ).add_to(m)

    # Display the folium map with markers and lines connecting them
    st_folium(m, height=350, width=700)


st.write("Server Load Balance Simulator")
if st.session_state.city_weights:
    load_balancer = KServerLoadBalancer(
        len(st.session_state.city_weights), st.session_state.city_weights
    )

    nums = st.number_input("Simulate n tasks", step=1)
    random_numbers = [random.randint(1, 20) for i in range(int(nums))]

    # Distribute tasks across servers
    if random_numbers:
        load_balancer.serve_tasks(random_numbers)

    st.write("\nFinal loads on each server:")
    for i, load in enumerate(load_balancer.server_loads):
        st.write(f"{st.session_state.cities[i]} Server: {load} load units")
