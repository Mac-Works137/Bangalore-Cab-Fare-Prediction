import pandas as pd


TRIP_PAIRS_FILE = (
    "data/raw/trips/trip_pairs.csv"
)

ROUTES_FILE = (
    "data/processed/routes/routes.csv"
)


def main():

    print("Loading trip pairs...")
    trip_pairs = pd.read_csv(TRIP_PAIRS_FILE)

    print("Loading existing routes...")
    routes = pd.read_csv(ROUTES_FILE)

    print()

    print(
        f"Trip pairs       : {len(trip_pairs)}"
    )

    print(
        f"Existing routes  : {len(routes)}"
    )

    # ---------------------------------------------------------
    # Create route keys
    #
    # A route is uniquely identified by:
    #
    # pickup_osm_id -> drop_osm_id
    # ---------------------------------------------------------

    trip_pairs["route_key"] = (
        trip_pairs["pickup_osm_id"].astype(str)
        + " -> "
        + trip_pairs["drop_osm_id"].astype(str)
    )

    routes["route_key"] = (
        routes["pickup_osm_id"].astype(str)
        + " -> "
        + routes["drop_osm_id"].astype(str)
    )

    # ---------------------------------------------------------
    # Find existing routes that are still present in the
    # newly generated 25,000 trip pairs.
    # ---------------------------------------------------------

    existing_keys = set(
        routes["route_key"]
    )

    trip_keys = set(
        trip_pairs["route_key"]
    )

    matching_keys = existing_keys.intersection(
        trip_keys
    )

    print(
        f"\nExisting routes reused : "
        f"{len(matching_keys)}"
    )

    print(
        f"Existing routes no longer present : "
        f"{len(existing_keys - trip_keys)}"
    )

    print(
        f"New routes needing GraphHopper : "
        f"{len(trip_keys - existing_keys)}"
    )

    # ---------------------------------------------------------
    # Show a few matching routes
    # ---------------------------------------------------------

    if matching_keys:

        matching_routes = routes[
            routes["route_key"].isin(matching_keys)
        ]

        print(
            "\nExample matching routes:"
        )

        print(
            matching_routes[
                [
                    "pickup_name",
                    "drop_name",
                    "road_distance_km",
                    "travel_time_minutes",
                ]
            ].head(10).to_string(index=False)
        )

    # ---------------------------------------------------------
    # Check for duplicate route keys in either dataset
    # ---------------------------------------------------------

    trip_duplicates = (
        trip_pairs["route_key"]
        .duplicated()
        .sum()
    )

    route_duplicates = (
        routes["route_key"]
        .duplicated()
        .sum()
    )

    print()

    print(
        f"Duplicate keys in trip_pairs.csv : "
        f"{trip_duplicates}"
    )

    print(
        f"Duplicate keys in routes.csv      : "
        f"{route_duplicates}"
    )


if __name__ == "__main__":
    main()