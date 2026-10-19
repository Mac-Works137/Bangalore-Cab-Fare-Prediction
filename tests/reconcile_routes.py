import pandas as pd


TRIP_PAIRS_FILE = (
    "data/raw/trips/trip_pairs.csv"
)

ROUTES_FILE = (
    "data/processed/routes/routes.csv"
)


def main():

    print("Loading trip pairs...")
    trip_pairs = pd.read_csv(
        TRIP_PAIRS_FILE
    )

    print("Loading existing routes...")
    routes = pd.read_csv(
        ROUTES_FILE
    )

    # ---------------------------------------------------------
    # Ensure is_routed exists
    # ---------------------------------------------------------

    if "is_routed" not in trip_pairs.columns:

        trip_pairs["is_routed"] = False

    # ---------------------------------------------------------
    # Build unique route keys
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
    # Routes that already have GraphHopper data
    # ---------------------------------------------------------

    existing_route_keys = set(
        routes["route_key"]
    )

    already_routed = (
        trip_pairs["route_key"]
        .isin(existing_route_keys)
    )

    # ---------------------------------------------------------
    # Update is_routed
    # ---------------------------------------------------------

    trip_pairs.loc[
        already_routed,
        "is_routed"
    ] = True

    # ---------------------------------------------------------
    # Remove temporary route key
    # ---------------------------------------------------------

    trip_pairs.drop(
        columns=["route_key"],
        inplace=True,
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    trip_pairs.to_csv(
        TRIP_PAIRS_FILE,
        index=False,
    )

    print()
    print("=" * 60)

    print(
        f"Total trip pairs : "
        f"{len(trip_pairs)}"
    )

    print(
        f"Already routed   : "
        f"{already_routed.sum()}"
    )

    print(
        f"Still unrouted   : "
        f"{(~already_routed).sum()}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()