import pandas as pd

from collector.services.routing_service import (
    RoutingService,
)


TRIP_PAIRS_FILE = (
    "data/raw/trips/trip_pairs.csv"
)

ROUTES_FILE = (
    "data/processed/routes/routes.csv"
)


def main():

    trips = pd.read_csv(
        TRIP_PAIRS_FILE
    )

    routes = pd.read_csv(
        ROUTES_FILE
    )

    trip_keys = (
        trips[
            [
                "pickup_osm_id",
                "drop_osm_id",
            ]
        ]
        .astype(str)
        .apply(
            lambda row:
            f"{row['pickup_osm_id']} -> "
            f"{row['drop_osm_id']}",
            axis=1,
        )
    )

    route_keys = (
        routes[
            [
                "pickup_osm_id",
                "drop_osm_id",
            ]
        ]
        .astype(str)
        .apply(
            lambda row:
            f"{row['pickup_osm_id']} -> "
            f"{row['drop_osm_id']}",
            axis=1,
        )
    )

    existing_keys = set(
        route_keys
    )

    matching = trip_keys.isin(
        existing_keys
    )

    print(
        f"Total trip pairs       : "
        f"{len(trips)}"
    )

    print(
        f"Existing routes        : "
        f"{len(routes)}"
    )

    print(
        f"Already routed         : "
        f"{matching.sum()}"
    )

    print(
        f"Need GraphHopper       : "
        f"{(~matching).sum()}"
    )

    print()

    print(
        "RoutingService sees:"
    )

    service = RoutingService()

    detected_keys = (
        service._load_existing_route_keys(
            ROUTES_FILE
        )
    )

    print(
        f"Existing route keys    : "
        f"{len(detected_keys)}"
    )

    print()

    if len(detected_keys) == len(existing_keys):

        print(
            "✓ Existing route detection is correct."
        )

    else:

        print(
            "✗ Existing route detection mismatch."
        )


if __name__ == "__main__":
    main()