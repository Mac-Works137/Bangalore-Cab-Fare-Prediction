from collector.validators.uber_location_validator import (
    UberLocationValidator,
)


def main():

    validator = UberLocationValidator()

    try:

        validator.launch()

        locations = [
            "Manyata Tech Park",
            "Kempegowda International Airport Bengaluru",
            "Joint Advanced Technology Programme",
        ]

        for location in locations:

            print()

            print(location)

            valid, match = validator.validate(location)

            print("Valid :", valid)

            print("Match :", match)

    finally:

        validator.close()


if __name__ == "__main__":
    main()