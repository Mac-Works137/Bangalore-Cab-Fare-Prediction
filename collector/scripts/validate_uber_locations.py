import pandas as pd

from collector.validators.uber_location_validator import (
    UberLocationValidator,
)


INPUT_FILE = (
    "data/raw/locations/locations.csv"
)

VALIDATED_FILE = (
    "data/raw/locations/validated_locations.csv"
)

REJECTED_FILE = (
    "data/raw/locations/rejected_locations.csv"
)


def main():

    locations = pd.read_csv(INPUT_FILE)

    validator = UberLocationValidator()

    validated = []
    rejected = []

    try:

        validator.launch()

        total = len(locations)

        print(
            f"\nValidating {total} locations...\n"
        )

        for index, (_, row) in enumerate(
            locations.iterrows(),
            start=1,
        ):

            name = row["name"]

            print(
                f"[{index}/{total}] {name}"
            )

            # -------------------------------------------------
            # Check for missing location name
            # -------------------------------------------------

            if pd.isna(name) or not str(name).strip():

                new_row = row.copy()

                new_row["uber_match"] = ""

                new_row["reason"] = (
                    "Missing location name"
                )

                rejected.append(new_row)

                print(
                    "   ✗ INVALID "
                    "(missing location name)"
                )

                print()

                continue

            # Convert to a clean string before
            # passing it to Playwright.

            name = str(name).strip()

            # -------------------------------------------------
            # Validate location
            # -------------------------------------------------

            try:

                is_valid, matched, search_used = (
                    validator.validate(name)
                )

                new_row = row.copy()

                new_row["uber_match"] = (
                    matched if matched else ""
                )

                new_row["uber_search_used"] = (
                    search_used if search_used else ""
                )

                if is_valid:

                    validated.append(new_row)

                    print("   ✓ VALID")

                else:

                    new_row["reason"] = (
                        "Not directly searchable on Uber"
                    )

                    rejected.append(new_row)

                    print("   ✗ INVALID")

            except Exception as e:

                # -------------------------------------------------
                # Do not allow one bad location to stop the
                # entire validation process.
                # -------------------------------------------------

                new_row = row.copy()

                new_row["uber_match"] = ""

                new_row["uber_search_used"] = ""

                new_row["reason"] = (
                    f"Validation error: {str(e)}"
                )

                rejected.append(new_row)

                print(
                    f"   ✗ ERROR: {e}"
                )

            print()

        # -----------------------------------------------------
        # Save results
        # -----------------------------------------------------

        validated_df = pd.DataFrame(
            validated
        )

        rejected_df = pd.DataFrame(
            rejected
        )

        validated_df.to_csv(
            VALIDATED_FILE,
            index=False,
        )

        rejected_df.to_csv(
            REJECTED_FILE,
            index=False,
        )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        print("=" * 60)

        print(
            f"Total locations : {total}"
        )

        print(
            f"Validated       : {len(validated_df)}"
        )

        print(
            f"Rejected        : {len(rejected_df)}"
        )

        print("=" * 60)

        print(
            f"\nValidated locations saved to:"
            f"\n{VALIDATED_FILE}"
        )

        print(
            f"\nRejected locations saved to:"
            f"\n{REJECTED_FILE}"
        )

    finally:

        validator.close()


if __name__ == "__main__":
    main()