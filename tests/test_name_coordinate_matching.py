from collector.services.providers.uber_provider import (
    UberProvider,
)


def main():

    provider = UberProvider()

    provider.launch()

    try:

        # ==================================================
        # OPEN UBER
        # ==================================================

        provider._navigate_to_homepage()

        # ==================================================
        # PICKUP
        # ==================================================

        provider._click_pickup_button()

        provider._enter_pickup_location(
            "Brand Factory"
        )

        pickup_match = (
            provider._select_pickup_suggestion(
                "Brand Factory",
                12.8832635,
                77.5492301,
            )
        )

        print(
            "\n========================================"
        )

        print(
            "FINAL PICKUP"
        )

        print(
            "Requested : Brand Factory"
        )

        print(
            f"Selected  : "
            f"{pickup_match['text']}"
        )

        print(
            f"Distance  : "
            f"{pickup_match['distance_km']:.3f} km"
        )

        print(
            "========================================"
        )

        # ==================================================
        # CONFIRM PICKUP
        # ==================================================

        provider._confirm_pickup()

        print(
            f"\nURL after pickup: "
            f"{provider.page.url}"
        )

        # ==================================================
        # DROPOFF
        # ==================================================

        provider._enter_dropoff_location(
            "NCS Elite"
        )

        dropoff_match = (
            provider._select_dropoff_suggestion(
                "NCS Elite",
                13.06749,
                77.575442,
            )
        )

        print(
            "\n========================================"
        )

        print(
            "FINAL DROPOFF"
        )

        print(
            "Requested : NCS Elite"
        )

        print(
            f"Selected  : "
            f"{dropoff_match['text']}"
        )

        print(
            f"Distance  : "
            f"{dropoff_match['distance_km']:.3f} km"
        )

        print(
            "========================================"
        )

        # ==================================================
        # CONFIRM DROPOFF
        # ==================================================

        provider._confirm_dropoff()

        # ==================================================
        # COLLECT FARES
        # ==================================================

        print(
            "\n========================================"
        )

        print(
            "COLLECTING FARES"
        )

        print(
            "========================================"
        )

        fares = provider.collect_fares()

        print(
            "\n========================================"
        )

        print(
            "FARES COLLECTED"
        )

        print(
            "========================================"
        )

        for fare in fares:

            print(fare)

        print(
            f"\nTotal fares collected: "
            f"{len(fares)}"
        )

        print(
            "========================================"
        )

        provider.page.wait_for_timeout(
            5000
        )

    finally:

        provider.close()


if __name__ == "__main__":
    main()