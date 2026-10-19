import pandas as pd

from config.collection_schedule import (
    ROUTES_CSV,
    UBER_FARES_CSV,
)


class RouteReader:
    """
    Loads routes that are ready for fare collection.
    """

    REQUIRED_COLUMNS = [
        "pickup_osm_id",
        "pickup_name",
        "pickup_category",
        "pickup_latitude",
        "pickup_longitude",
        "drop_osm_id",
        "drop_name",
        "drop_category",
        "drop_latitude",
        "drop_longitude",
        "road_distance_km",
        "travel_time_minutes",
    ]

    def load_routes(self):
        """
        Loads the routed trips from routes.csv.

        Returns
        -------
        list[dict]
            One dictionary per route.
        """

        df = pd.read_csv(ROUTES_CSV)

        if df.empty:
            raise ValueError(
                "routes.csv is empty."
            )

        self._validate_columns(df)

        print(
            f"Loaded {len(df)} routed trips."
        )

        return df.to_dict(
            orient="records"
        )

    def load_routes_for_fare_collection(self):
        """
        Loads routes that have already been validated
        for Uber fare collection.

        Routes with fewer existing fare observations
        are prioritized so that the collection process
        gradually balances coverage across the validated
        route pool.

        Returns
        -------
        list[dict]
            Uber-validated routes ready for fare collection.
        """

        validated_routes_file = (
            "data/processed/routes/uber_validated_routes.csv"
        )

        df = pd.read_csv(
            validated_routes_file
        )

        if df.empty:
            raise ValueError(
                "uber_validated_routes.csv is empty."
            )

        self._validate_columns(df)

        print(
            f"Loaded {len(df)} Uber-validated routes "
            f"ready for fare collection."
        )

        # ---------------------------------------------------------
        # Load existing fare observations
        # ---------------------------------------------------------
        fares_df = pd.read_csv(UBER_FARES_CSV)

        if fares_df.empty:
            print(
                "No existing fare observations found. "
                "All validated routes have equal priority."
            )

            df = df.sample(
                frac=1
            ).reset_index(drop=True)

            return df.to_dict(
                orient="records"
            )

        # ---------------------------------------------------------
        # Count existing observations for each route
        # ---------------------------------------------------------
        route_counts = (
            fares_df.groupby(
                ["pickup", "dropoff"]
            )
            .size()
            .reset_index(
                name="fare_observation_count"
            )
        )

        # ---------------------------------------------------------
        # Match fare counts to validated routes
        # ---------------------------------------------------------
        df = df.merge(
            route_counts,
            left_on=[
                "pickup_name",
                "drop_name",
            ],
            right_on=[
                "pickup",
                "dropoff",
            ],
            how="left",
        )

        # Routes with no previous fare observations
        # get count 0.
        df["fare_observation_count"] = (
            df["fare_observation_count"]
            .fillna(0)
            .astype(int)
        )

        # ---------------------------------------------------------
        # Randomize first, then sort by observation count.
        #
        # Because pandas sorting is stable, routes with the
        # same observation count retain their randomized order.
        # ---------------------------------------------------------
        df = df.sample(
            frac=1
        ).reset_index(
            drop=True
        )

        df = df.sort_values(
            by="fare_observation_count",
            ascending=True,
            kind="stable",
        )

        # ---------------------------------------------------------
        # Remove helper columns
        # ---------------------------------------------------------
        df = df.drop(
            columns=[
                "pickup",
                "dropoff",
                "fare_observation_count",
            ]
        )

        df = df.reset_index(
            drop=True
        )

        return df.to_dict(
            orient="records"
        )

    def _validate_columns(
        self,
        df,
    ):
        """
        Ensures all required columns exist.
        """

        missing = []

        for column in self.REQUIRED_COLUMNS:

            if column not in df.columns:
                missing.append(column)

        if missing:

            raise ValueError(
                "Missing required columns:\n"
                + "\n".join(missing)
            )