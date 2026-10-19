import time
import traceback

from collector.route_reader import RouteReader
from collector.scheduler import CollectionScheduler
from collector.collectors.uber_collector import UberCollector
from collector.utils.logger import get_logger
from collector.services.fare_csv_writer import FareCSVWriter

from config.collection_schedule import (
    MAX_ROUTES_PER_SLOT,
    UBER_FARES_CSV,
    COLLECTION_DELAY_MS,
)


class CollectionRunner:

    def __init__(self):

        self.route_reader = RouteReader()

        self.scheduler = CollectionScheduler()

        self.collector = UberCollector()

        self.writer = FareCSVWriter(
            UBER_FARES_CSV
        )

        self.logger = get_logger()

    def run(self):

        # --------------------------------------------------
        # Load routes ready for fare collection.
        # --------------------------------------------------

        routes = (
            self.route_reader
            .load_routes_for_fare_collection()
        )

        # --------------------------------------------------
        # Limit the number of routes collected
        # during this execution.
        # --------------------------------------------------

        routes = routes[
            :MAX_ROUTES_PER_SLOT
        ]

        context = (
            self.scheduler
            .get_collection_context()
        )

        self.logger.info(
            f"\nLoaded {len(routes)} routes."
        )

        self.logger.info(
            f"Collection slot: "
            f"{context['time_slot']}"
        )

        self.logger.info(
            f"Day: "
            f"{context['day_of_week']}\n"
        )

        if not routes:

            self.logger.warning(
                "No routes available "
                "for fare collection."
            )

            return

        # --------------------------------------------------
        # Launch the browser once.
        # --------------------------------------------------

        self.collector.launch()

        successful_routes = 0
        failed_routes = 0

        try:

            total_routes = len(routes)

            for index, route in enumerate(
                routes,
                start=1,
            ):

                self.logger.info(
                    f"\n[{index}/{total_routes}] "
                    f"{route['pickup_name']} "
                    f"-> "
                    f"{route['drop_name']}"
                )

                try:

                    fares = (
                        self.collector
                        .collect_route(
                            route,
                            context,
                        )
                    )

                    # ------------------------------------------
                    # Save every fare returned by the provider.
                    # ------------------------------------------

                    for fare in fares:

                        self.writer.append(
                            fare
                        )

                    successful_routes += 1

                    self.logger.info(
                        f"✓ Collected "
                        f"{len(fares)} fares."
                    )

                except Exception:

                    failed_routes += 1

                    self.logger.exception(
                        "Failed route: "
                        f"{route['pickup_name']} "
                        f"-> "
                        f"{route['drop_name']}"
                    )

                # ----------------------------------------------
                # Wait before starting the next route.
                #
                # Do not wait after the final route.
                # ----------------------------------------------

                if index < total_routes:

                    time.sleep(
                        COLLECTION_DELAY_MS
                        / 1000
                    )

        finally:

            self.logger.info(
                "=" * 60
            )

            self.logger.info(
                "Collection Summary"
            )

            self.logger.info(
                "=" * 60
            )

            self.logger.info(
                f"Successful routes : "
                f"{successful_routes}"
            )

            self.logger.info(
                f"Failed routes     : "
                f"{failed_routes}"
            )

            self.logger.info(
                f"Total routes      : "
                f"{successful_routes + failed_routes}"
            )

            self.collector.close()