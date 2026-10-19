import time
from collector.collectors.fare_collector import FareCollector
from collector.services.providers.uber_provider import (
    UberProvider,
    UberSuggestionResolutionError,
    UberTransientError,
)


MAX_LOCATION_DISTANCE_KM = 0.1

RETRYABLE_ERRORS = (
    UberSuggestionResolutionError,
    UberTransientError,
)

MAX_ROUTE_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2

class UberCollector(FareCollector):
    """
    Wrapper around UberProvider.

    Responsible for collecting fares for one route.
    """

    def __init__(self):

        super().__init__()

        self.provider_name = "Uber"

        self.provider = UberProvider()

    def launch(self):

        self.provider.launch()

    def _validate_location_match(
        self,
        match,
        requested_location,
        location_type,
    ):
        """
        Validates that the location selected by Uber
        is sufficiently close to the requested coordinates.

        Raises
        ------
        ValueError
            If Uber selected a location farther than the
            allowed distance from the requested coordinates.
        """

        if match is None:

            raise ValueError(
                f"Uber could not find a valid "
                f"{location_type} location for "
                f"'{requested_location}'."
            )

        distance_km = match["distance_km"]

        if distance_km > MAX_LOCATION_DISTANCE_KM:

            raise ValueError(
                f"Uber {location_type} location mismatch: "
                f"requested '{requested_location}', "
                f"selected '{match['text']}', "
                f"distance = {distance_km:.3f} km, "
                f"maximum allowed = "
                f"{MAX_LOCATION_DISTANCE_KM:.3f} km."
            )

    def _collect_route_once(
        self,
        route,
        context,
    ):

        self.provider.current_pickup = (
            route["pickup_name"]
        )

        self.provider.current_dropoff = (
            route["drop_name"]
        )

        self.provider.search_timestamp = (
            context["search_timestamp"]
        )

        self.provider.time_slot = (
            context["time_slot"]
        )

        self.provider.day_of_week = (
            context["day_of_week"]
        )

        self.provider._navigate_to_homepage()

        self.provider._click_pickup_button()

        self.provider._enter_pickup_location(
            route["pickup_name"]
        )

        pickup_match = (
            self.provider._select_pickup_by_coordinates(
                route["pickup_latitude"],
                route["pickup_longitude"],
            )
        )

        print(
            f"Requested pickup : "
            f"{route['pickup_name']}"
        )

        print(
            f"Uber pickup      : "
            f"{pickup_match['text']}"
        )

        print(
            f"Pickup distance  : "
            f"{pickup_match['distance_km']:.3f} km"
        )

        self._validate_location_match(
            pickup_match,
            route["pickup_name"],
            "pickup",
        )

        self.provider._confirm_pickup()

        self.provider._enter_dropoff_location(
            route["drop_name"]
        )

        dropoff_match = (
            self.provider._select_dropoff_by_coordinates(
                route["drop_latitude"],
                route["drop_longitude"],
            )
        )

        print(
            f"Requested dropoff: "
            f"{route['drop_name']}"
        )

        print(
            f"Uber dropoff     : "
            f"{dropoff_match['text']}"
        )

        print(
            f"Dropoff distance : "
            f"{dropoff_match['distance_km']:.3f} km"
        )

        self._validate_location_match(
            dropoff_match,
            route["drop_name"],
            "dropoff",
        )

        self.provider._confirm_dropoff()

        return self.provider.collect_fares()

    def collect_route(
        self,
        route,
        context,
    ):
        for attempt in range(1, MAX_ROUTE_ATTEMPTS + 1):

            try:

                return self._collect_route_once(
                    route,
                    context,
                )

            except RETRYABLE_ERRORS as exc:

                if attempt == MAX_ROUTE_ATTEMPTS:
                    print(
                        f"Route failed after "
                        f"{MAX_ROUTE_ATTEMPTS} attempts: "
                        f"{route['pickup_name']} -> "
                        f"{route['drop_name']}"
                    )
                    raise

                print(
                    f"Retryable Uber error on attempt "
                    f"{attempt}/{MAX_ROUTE_ATTEMPTS}: "
                    f"{exc}"
                )

                print(
                    f"Retrying route "
                    f"{route['pickup_name']} -> "
                    f"{route['drop_name']}..."
                )

                time.sleep(
                    RETRY_DELAY_SECONDS
                )

    def close(self):

        self.provider.close()