from collector.services.providers.uber_provider import UberProvider
from collector.services.fare_csv_writer import FareCSVWriter

def main():

    provider = UberProvider()

    try:

        provider.launch()

        provider._navigate_to_homepage()

        provider._click_pickup_button()

        provider._enter_pickup_location(
            "Manyata Tech Park"
        )

        provider._select_pickup_suggestion("Manyata Tech Park")

        provider._confirm_pickup()

        provider._enter_dropoff_location(
            "Electronic City"
        )

        provider._select_dropoff_suggestion("Electronic City")

        provider._confirm_dropoff()

        fares = provider.collect_fares()
        
        writer = FareCSVWriter(
            "uber_test.csv"
        )

        for fare in fares:
            writer.append(fare)

        print("\n\nCollected fares:\n")

        for fare in fares:
            print("=" * 60)

            for key, value in vars(fare).items():
                print(f"{key:15}: {value}")

            print()

        input(
            "\nPress Enter to close..."
        )

    finally:
        input(
            "\nPress Enter AFTER inspecting the page..."
        )
        provider.close()


if __name__ == "__main__":
    main()