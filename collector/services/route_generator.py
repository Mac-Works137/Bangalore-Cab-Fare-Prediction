import pandas as pd

from math import radians, sin, cos, sqrt, atan2

from config.trip_patterns import (
    MIN_TRIP_DISTANCE_KM,
    MAX_TRIP_DISTANCE_KM,
    TRIP_PATTERNS,
)


class RouteGenerator:

    def __init__(self):

        self.locations_df = None

    # ---------------------------------------------------------

    def load_locations(self, csv_path):

        self.locations_df = pd.read_csv(csv_path)

        if self.locations_df.empty:
            raise ValueError("locations.csv is empty.")

        # ------------------------------------------
        # Remove locations without names
        # ------------------------------------------

        self.locations_df["name"] = (
            self.locations_df["name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        before = len(self.locations_df)

        self.locations_df = self.locations_df[
            self.locations_df["name"] != ""
        ].copy()

        self.locations_df = self.locations_df[
            self.locations_df["name"].str.lower() != "nan"
        ]

        removed = before - len(self.locations_df)

        print(f"Removed {removed} unnamed locations.")

        print(
            f"Loaded {len(self.locations_df)} locations."
        )


    # ---------------------------------------------------------

    def _calculate_distance(
        self,
        pickup,
        drop,
    ):

        EARTH_RADIUS_KM = 6371.0

        lat1 = radians(pickup["latitude"])
        lon1 = radians(pickup["longitude"])

        lat2 = radians(drop["latitude"])
        lon2 = radians(drop["longitude"])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return EARTH_RADIUS_KM * c

    # ---------------------------------------------------------

    def _calculate_trip_weight(
        self,
        pickup_category,
        drop_category,
    ):

        return (
            TRIP_PATTERNS
            .get(pickup_category, {})
            .get(drop_category, 0)
        )

    # ---------------------------------------------------------

    def generate_routes(self):

        routes = []

        locations = self.locations_df.to_dict(
            orient="records"
        )

        total = len(locations)

        print(
            f"\nGenerating routes from {total} locations...\n"
        )

        for pickup in locations:

            for drop in locations:

                #
                # same place
                #

                if pickup["osm_id"] == drop["osm_id"]:
                    continue

                #
                # distance
                #

                distance = self._calculate_distance(
                    pickup,
                    drop,
                )

                if (
                    distance < MIN_TRIP_DISTANCE_KM
                    or
                    distance > MAX_TRIP_DISTANCE_KM
                ):
                    continue

                #
                # weight
                #

                weight = self._calculate_trip_weight(
                    pickup["category_key"],
                    drop["category_key"],
                )

                #
                # impossible transition
                #

                if weight == 0:
                    weight=0.01

                routes.append(
                    {
                        "pickup_osm_id":
                            pickup["osm_id"],

                        "pickup_name":
                            pickup["name"],

                        "pickup_category":
                            pickup["category_key"],

                        "pickup_latitude":
                            pickup["latitude"],

                        "pickup_longitude":
                            pickup["longitude"],

                        "drop_osm_id":
                            drop["osm_id"],

                        "drop_name":
                            drop["name"],

                        "drop_category":
                            drop["category_key"],

                        "drop_latitude":
                            drop["latitude"],

                        "drop_longitude":
                            drop["longitude"],

                        "distance_km":
                            round(distance, 3),

                        "trip_weight":
                            weight,
                    }
                )

        routes_df = pd.DataFrame(routes)

        print(
            f"Generated {len(routes_df)} unique routes."
        )

        return routes_df