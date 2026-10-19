import streamlit as st
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Load the trained model
MODEL_PATH = "models/final_fare_prediction_model.joblib"

model = joblib.load(MODEL_PATH)

# Load validated Uber routes
ROUTES_PATH = "data/processed/routes/uber_validated_routes.csv"

routes_df = pd.read_csv(ROUTES_PATH)

st.title("Bangalore Cab Fare Prediction")

st.write(
    "Enter your trip details below to predict the estimated Uber fare."
)

st.subheader("Trip Details")

pickup_locations = sorted(routes_df["pickup_name"].unique())

pickup = st.selectbox(
    "Pickup Location",
    pickup_locations
)

# Only show destinations that exist for the selected pickup
available_dropoffs = sorted(
    routes_df.loc[
        routes_df["pickup_name"] == pickup,
        "drop_name"
    ].unique()
)

dropoff = st.selectbox(
    "Dropoff Location",
    available_dropoffs
)

# Find the selected route
selected_route = routes_df[
    (routes_df["pickup_name"] == pickup) &
    (routes_df["drop_name"] == dropoff)
].iloc[0]

# Get route information
pickup_category = selected_route["pickup_category"]
drop_category = selected_route["drop_category"]
road_distance_km = selected_route["road_distance_km"]
travel_time_minutes = selected_route["travel_time_minutes"]

# Display route information
st.subheader("Route Information")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Road Distance",
        f"{road_distance_km:.2f} km"
    )

with col2:
    st.metric(
        "Travel Time",
        f"{travel_time_minutes:.2f} min"
    )

# Automatically detect current time and day
current_time = datetime.now(
    ZoneInfo("Asia/Kolkata")
)

hour = current_time.hour
day_of_week = current_time.strftime("%A")

if hour < 5:
    time_slot = "00:00"
elif hour < 11:
    time_slot = "09:00"
elif hour < 14:
    time_slot = "12:00"
elif hour < 17:
    time_slot = "15:00"
elif hour < 20:
    time_slot = "18:00"
else:
    time_slot = "21:00"

st.caption(
    f"Current time: {current_time.strftime('%H:%M')} • "
    f"{day_of_week}"
)

# Available Uber ride types
ride_types = [
    "Auto",
    "Auto Priority",
    "Bike",
    "Bike Saver",
    "Black",
    "Black Rentals",
    "Electric",
    "Go Intercity",
    "Go Non AC",
    "Go Priority",
    "Go Rentals",
    "Hatchback",
    "Innova",
    "Premier",
    "Premier AC",
    "Premier Rentals",
    "Premier XL",
    "Uber Go AC",
    "Uber Pet",
    "UberXL",
    "XL",
    "XL Plus Rentals",
    "XL Rentals",
]

# Create one input row for each ride type
prediction_data = pd.DataFrame({
    "road_distance_km": [road_distance_km] * len(ride_types),
    "travel_time_minutes": [travel_time_minutes] * len(ride_types),
    "ride_name": ride_types,
    "pickup_category": [pickup_category] * len(ride_types),
    "drop_category": [drop_category] * len(ride_types),
    "time_slot": [time_slot] * len(ride_types),
    "day_of_week": [day_of_week] * len(ride_types),
    "pickup": [pickup] * len(ride_types),
    "dropoff": [dropoff] * len(ride_types)
})

print(prediction_data)

if st.button("Predict Fares"):

    # Predict fares for all ride types
    predicted_log_fares = model.predict(prediction_data)

    # Convert predictions from log scale back to actual fare
    predicted_fares = np.expm1(predicted_log_fares)

    # Add predictions to the DataFrame
    prediction_data["predicted_fare"] = predicted_fares

    st.subheader("Estimated Fares")

    # Prediction summary
    lowest_fare = prediction_data.loc[
        prediction_data["predicted_fare"].idxmin()
    ]

    highest_fare = prediction_data.loc[
        prediction_data["predicted_fare"].idxmax()
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Lowest Estimated Fare",
            f"₹{lowest_fare['predicted_fare']:,.2f}"
        )

    with col2:
        st.metric(
            "Highest Estimated Fare",
            f"₹{highest_fare['predicted_fare']:,.2f}"
        )

    with col3:
        st.metric(
            "Ride Types",
            len(prediction_data)
        )

    results = prediction_data[
        ["ride_name", "predicted_fare"]
    ].copy()

    # Sort by predicted fare
    results = results.sort_values(
        "predicted_fare"
    ).reset_index(drop=True)

    # Format fare as currency
    results["predicted_fare"] = results["predicted_fare"].apply(
        lambda x: f"₹{x:,.2f}"
    )

    # Rename columns for display
    results = results.rename(
        columns={
            "ride_name": "Ride Type",
            "predicted_fare": "Estimated Fare"
        }
    )

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )