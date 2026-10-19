from collector.services.providers.uber_provider import (
    UberProvider,
)


def main():

    provider = UberProvider()

    provider.launch()

    try:

        provider._navigate_to_homepage()

        # --------------------------------------------------
        # Pickup
        # --------------------------------------------------

        provider._click_pickup_button()

        pickup_match = (
            provider._select_pickup_by_coordinates(
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
            f"Requested : Brand Factory"
        )

        print(
            f"Selected  : {pickup_match['text']}"
        )

        print(
            f"ID        : {pickup_match['id']}"
        )

        print(
            f"Distance  : "
            f"{pickup_match['distance_km']:.3f} km"
        )

        print(
            "========================================"
        )

        provider._confirm_pickup()

        # --------------------------------------------------
        # Drop-off
        # --------------------------------------------------

        dropoff_match = (
            provider._select_dropoff_by_coordinates(
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
            f"Requested : NCS Elite"
        )

        print(
            f"Selected  : {dropoff_match['text']}"
        )

        print(
            f"ID        : {dropoff_match['id']}"
        )

        print(
            f"Distance  : "
            f"{dropoff_match['distance_km']:.3f} km"
        )

        print(
            "========================================"
        )

    finally:

        provider.close()


if __name__ == "__main__":
    main()