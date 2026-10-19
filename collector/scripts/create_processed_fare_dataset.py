"""
CREATE PROCESSED UBER FARE DATASET

Combines:
1. Raw Uber fare observations
2. Uber-validated route information

The resulting dataset is saved as:
data/processed/fares/uber_fares_processed.csv

One row represents one Uber ride option observed
for one route at one point in time.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

UBER_FARES_CSV = "data/raw/fares/uber_fares.csv"

ROUTES_CSV = (
    "data/processed/routes/routes.csv"
)

OUTPUT_CSV = (
    "data/processed/fares/uber_fares_processed.csv"
)


# ---------------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------------

FARE_COLUMNS = [
    "timestamp",
    "time_slot",
    "day_of_week",
    "provider",
    "pickup",
    "dropoff",
    "ride_name",
    "seats",
    "current_price",
    "original_price",
    "eta_minutes",
    "arrival_time",
    "promotion",
    "description",
]

ROUTE_COLUMNS = [
    "pickup_name",
    "drop_name",
    "pickup_category",
    "drop_category",
    "road_distance_km",
    "travel_time_minutes",
]


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_fare_data():
    """Load raw Uber fare observations."""

    if not Path(UBER_FARES_CSV).exists():
        raise FileNotFoundError(
            f"Fare data not found: {UBER_FARES_CSV}"
        )

    df = pd.read_csv(UBER_FARES_CSV)

    missing_columns = [
        column
        for column in FARE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing fare columns: {missing_columns}"
        )

    return df


def load_routes():
    """Load routed trip information."""

    if not Path(ROUTES_CSV).exists():
        raise FileNotFoundError(
            f"Routes data not found: {ROUTES_CSV}"
        )

    df = pd.read_csv(ROUTES_CSV)

    missing_columns = [
        column
        for column in ROUTE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing route columns: {missing_columns}"
        )

    return df


# ---------------------------------------------------------
# CREATE PROCESSED DATASET
# ---------------------------------------------------------

def create_processed_dataset(fares_df, routes_df):
    """
    Merge fare observations with validated route information.
    """

    # Keep only the route columns that we need.
    routes = routes_df[ROUTE_COLUMNS].copy()

    # The raw fare CSV contains the original requested
    # pickup/dropoff names.
    #
    # The validated routes contain the corresponding
    # pickup_name/drop_name values.
    #
    # Therefore we match:
    #
    # fare pickup  -> route pickup_name
    # fare dropoff -> route drop_name

    routes = routes.rename(
        columns={
            "pickup_name": "pickup",
            "drop_name": "dropoff",
        }
    )

    # Merge route information into fare observations.
    processed_df = fares_df.merge(
        routes,
        on=["pickup", "dropoff"],
        how="left",
        validate="many_to_one",
    )

    return processed_df


# ---------------------------------------------------------
# SELECT FINAL COLUMNS
# ---------------------------------------------------------

def select_processed_columns(df):
    """Select and order columns for the processed dataset."""

    processed_columns = [
        "timestamp",
        "time_slot",
        "day_of_week",
        "pickup",
        "dropoff",
        "pickup_category",
        "drop_category",
        "road_distance_km",
        "travel_time_minutes",
        "ride_name",
        "seats",
        "eta_minutes",
        "current_price",
    ]

    return df[processed_columns]


# ---------------------------------------------------------
# SAVE DATASET
# ---------------------------------------------------------

def save_processed_dataset(df):
    """Save the processed dataset."""

    output_path = Path(OUTPUT_CSV)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        index=False,
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("Creating processed Uber fare dataset")
    print("=" * 60)

    # Load raw fare observations
    fares_df = load_fare_data()

    print(f"\nRaw fare observations : {len(fares_df)}")

    # Load validated routes
    routes_df = load_routes()

    print(f"Validated routes      : {len(routes_df)}")

    # Merge both datasets
    processed_df = create_processed_dataset(
        fares_df,
        routes_df,
    )

    # Check whether any fare observations failed
    # to match a validated route.
    unmatched = processed_df[
        processed_df["road_distance_km"].isna()
    ]

    print(
        f"Unmatched fare rows   : {len(unmatched)}"
    )

    if len(unmatched) > 0:
        print(
            "\nWARNING: Some fare observations "
            "could not be matched to a validated route."
        )

    # Select final columns
    processed_df = select_processed_columns(
        processed_df
    )

    # Save
    save_processed_dataset(processed_df)

    print(
        f"\nProcessed rows        : {len(processed_df)}"
    )

    print(
        f"Output file           : {OUTPUT_CSV}"
    )

    print("\nProcessed columns:")
    for column in processed_df.columns:
        print(f"  - {column}")

    print("\n" + "=" * 60)
    print("Processed dataset created successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()