import os
import time

import pandas as pd
import requests

from collector.utils.rate_limiter import RateLimiter

from config.routing import (
    BASE_URL,
    ROUTING_PROFILE,
    API_KEY,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    REQUEST_DELAY,
    MINUTE_LIMIT_SLEEP,
    MAX_MINUTE_LIMIT_RETRIES,
    PROGRESS_INTERVAL,
    ROAD_DISTANCE_DECIMALS,
    DURATION_DECIMALS,
    SAVE_BATCH_SIZE,
    REQUESTS_PER_SECOND,
)


class RoutingService:

    def __init__(self):

        self.trips_df = None

        self.successful_routes = 0

        self.failed_routes = 0

        self.successfully_routed_indices = []

        self.rate_limiter = RateLimiter(
            REQUESTS_PER_SECOND
        )

    def load_trips(self, csv_path):
        """
        Loads trips from a CSV file.
        """

        self.trips_df = pd.read_csv(
            csv_path
        )

        if self.trips_df.empty:
            raise ValueError(
                "Trip file is empty."
            )

    def set_trips(self, trips_df):
        """
        Sets the trips to be enriched.
        """

        self.trips_df = trips_df.copy()

    def _build_route_key(self, trip):
        """
        Creates a unique key for a directed route.

        pickup -> drop

        Direction matters.
        """

        return (
            f"{trip['pickup_osm_id']}"
            f" -> "
            f"{trip['drop_osm_id']}"
        )

    def _load_existing_route_keys(
        self,
        output_path,
    ):
        """
        Loads route keys that already exist in the
        output CSV.

        These routes will not be sent to GraphHopper again.
        """

        if not os.path.exists(output_path):

            return set()

        try:

            existing_routes = pd.read_csv(
                output_path
            )

        except pd.errors.EmptyDataError:

            return set()

        if existing_routes.empty:

            return set()

        required_columns = {
            "pickup_osm_id",
            "drop_osm_id",
        }

        if not required_columns.issubset(
            existing_routes.columns
        ):

            raise ValueError(
                "Existing routes file is missing "
                "pickup_osm_id or drop_osm_id."
            )

        existing_keys = (
            existing_routes[
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

        return set(
            existing_keys
        )

    def _build_request(self, trip):
        """
        Builds the query parameters required by
        the GraphHopper Route API.
        """

        pickup_point = (
            f"{trip['pickup_latitude']},"
            f"{trip['pickup_longitude']}"
        )

        drop_point = (
            f"{trip['drop_latitude']},"
            f"{trip['drop_longitude']}"
        )

        params = {
            "point": [
                pickup_point,
                drop_point,
            ],
            "profile": ROUTING_PROFILE,
            "instructions": "false",
            "calc_points": "false",
            "key": API_KEY,
        }

        return params

    def _call_api(self, params):
        """
        Sends a routing request to GraphHopper
        and returns the JSON response.
        """

        network_retry = 0

        minute_limit_retries = 0

        while True:

            try:

                self.rate_limiter.wait_if_needed()

                response = requests.get(
                    url=BASE_URL,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                return response.json()

            except requests.exceptions.HTTPError:

                if response.status_code == 429:

                    minute_limit_retries += 1

                    if (
                        minute_limit_retries
                        > MAX_MINUTE_LIMIT_RETRIES
                    ):

                        raise Exception(
                            "Exceeded maximum "
                            "minute-limit retries."
                        )

                    print(
                        f"\nMinute rate limit reached "
                        f"({minute_limit_retries}/"
                        f"{MAX_MINUTE_LIMIT_RETRIES})"
                    )

                    print(
                        f"Waiting "
                        f"{MINUTE_LIMIT_SLEEP} seconds..."
                    )

                    time.sleep(
                        MINUTE_LIMIT_SLEEP
                    )

                    continue

                raise

            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ):

                network_retry += 1

                if network_retry > MAX_RETRIES:

                    raise

                print(
                    f"Network error. Retrying "
                    f"({network_retry}/"
                    f"{MAX_RETRIES})..."
                )

                time.sleep(
                    REQUEST_DELAY
                )

    def _parse_response(self, response):
        """
        Extracts routing information from a
        GraphHopper API response.
        """

        paths = response.get(
            "paths"
        )

        if not paths:

            raise ValueError(
                "No route found in "
                "GraphHopper response."
            )

        route = paths[0]

        return {
            "road_distance": route["distance"],
            "travel_time": route["time"],
        }

    def _enrich_single_trip(self, trip):
        """
        Enriches a single trip with routing information.
        """

        enriched_trip = trip.copy()

        try:

            params = self._build_request(
                trip
            )

            response = self._call_api(
                params
            )

            routing_data = self._parse_response(
                response
            )

            enriched_trip["road_distance"] = (
                routing_data["road_distance"]
            )

            enriched_trip["travel_time"] = (
                routing_data["travel_time"]
            )

            self.successful_routes += 1

            self.successfully_routed_indices.append(
                trip.name
            )

        except Exception as e:

            print(
                f"Failed to enrich trip "
                f"'{trip['pickup_name']}' -> "
                f"'{trip['drop_name']}': {e}"
            )

            self.failed_routes += 1

            return None

        return enriched_trip

    def _save_batch(
        self,
        batch,
        output_path,
    ):
        """
        Saves a batch of enriched trips by appending
        them to the output CSV.
        """

        if not batch:

            return

        batch_df = pd.DataFrame(
            batch
        )

        # -------------------------------------------------
        # Convert meters -> kilometers
        # -------------------------------------------------

        batch_df["road_distance_km"] = (
            batch_df["road_distance"] / 1000
        ).round(
            ROAD_DISTANCE_DECIMALS
        )

        # -------------------------------------------------
        # Convert milliseconds -> minutes
        # -------------------------------------------------

        batch_df["travel_time_minutes"] = (
            batch_df["travel_time"]
            / (1000 * 60)
        ).round(
            DURATION_DECIMALS
        )

        # -------------------------------------------------
        # Remove raw GraphHopper columns
        # -------------------------------------------------

        batch_df.drop(
            columns=[
                "road_distance",
                "travel_time",
            ],
            inplace=True,
        )

        output_directory = os.path.dirname(
            output_path
        )

        if output_directory:

            os.makedirs(
                output_directory,
                exist_ok=True,
            )

        file_exists = os.path.exists(
            output_path
        )

        batch_df.to_csv(
            output_path,
            mode="a" if file_exists else "w",
            header=not file_exists,
            index=False,
        )

    def enrich_routes(
        self,
        output_path,
    ):
        """
        Enriches trips using GraphHopper.

        Routes that already exist in output_path
        are skipped and considered successfully routed.

        This makes the process resumable and prevents
        duplicate GraphHopper requests.
        """

        if self.trips_df is None:

            raise ValueError(
                "Trips have not been loaded."
            )

        self.successful_routes = 0

        self.failed_routes = 0

        self.successfully_routed_indices = []

        enriched_trips = []

        # -------------------------------------------------
        # Load routes that already exist
        # -------------------------------------------------

        existing_route_keys = (
            self._load_existing_route_keys(
                output_path
            )
        )

        print(
            f"\nExisting routes found: "
            f"{len(existing_route_keys)}"
        )

        total_trips = len(
            self.trips_df
        )

        skipped_existing = 0

        processed = 0

        # -------------------------------------------------
        # Process trips
        # -------------------------------------------------

        for _, trip in self.trips_df.iterrows():

            processed += 1

            route_key = self._build_route_key(
                trip
            )

            # -------------------------------------------------
            # Route already exists
            # -------------------------------------------------

            if route_key in existing_route_keys:

                skipped_existing += 1

                # The route already has GraphHopper
                # data, so tell TripSampler that this
                # trip is routed.

                self.successfully_routed_indices.append(
                    trip.name
                )

                continue

            # -------------------------------------------------
            # Route does not exist -> call GraphHopper
            # -------------------------------------------------

            enriched_trip = (
                self._enrich_single_trip(
                    trip
                )
            )

            if enriched_trip is not None:

                enriched_trips.append(
                    enriched_trip
                )

                # Add the route immediately to our
                # in-memory set.
                #
                # This protects us against accidental
                # duplicate processing within this run.

                existing_route_keys.add(
                    route_key
                )

            # -------------------------------------------------
            # Save batch
            # -------------------------------------------------

            if (
                len(enriched_trips)
                == SAVE_BATCH_SIZE
            ):

                self._save_batch(
                    enriched_trips,
                    output_path,
                )

                enriched_trips.clear()

            # -------------------------------------------------
            # Progress
            # -------------------------------------------------

            if (
                processed % PROGRESS_INTERVAL == 0
                or processed == total_trips
            ):

                print(
                    f"Processed "
                    f"{processed}/{total_trips} trips"
                )

        # -------------------------------------------------
        # Save remaining routes
        # -------------------------------------------------

        if enriched_trips:

            self._save_batch(
                enriched_trips,
                output_path,
            )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        print(
            f"\nNew routes successfully processed: "
            f"{self.successful_routes}"
        )

        print(
            f"Existing routes reused: "
            f"{skipped_existing}"
        )

        print(
            f"Failed: "
            f"{self.failed_routes}"
        )

        print(
            f"\nRoutes saved to: "
            f"{output_path}"
        )

        return (
            self.successfully_routed_indices
        )