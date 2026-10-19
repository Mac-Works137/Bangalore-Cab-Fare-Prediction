import random
import re

import pandas as pd

from collector.route_reader import RouteReader
from collector.collectors.uber_collector import UberCollector


MAX_ROUTES_PER_RUN = 100

VALIDATED_ROUTES_FILE = (
    "data/processed/routes/uber_validated_routes.csv"
)

REJECTED_ROUTES_FILE = (
    "data/processed/routes/uber_rejected_routes.csv"
)

MAX_LOCATION_DISTANCE_KM = 0.1

## MIN_NAME_SIMILARITY = 0.5

def route_key(route):
    return (
        route["pickup_osm_id"],
        route["drop_osm_id"],
    )


def load_already_validated_routes():
    try:
        df = pd.read_csv(VALIDATED_ROUTES_FILE)

        if df.empty:
            return set()

        return set(
            zip(
                df["pickup_osm_id"],
                df["drop_osm_id"],
            )
        )

    except FileNotFoundError:
        return set()


def append_dataframe(dataframe, filepath):
    if dataframe.empty:
        return

    try:
        existing = pd.read_csv(filepath)

        if existing.empty:
            dataframe.to_csv(
                filepath,
                mode="w",
                header=True,
                index=False,
            )
        else:
            dataframe.to_csv(
                filepath,
                mode="a",
                header=False,
                index=False,
            )

    except FileNotFoundError:
        dataframe.to_csv(
            filepath,
            mode="w",
            header=True,
            index=False,
        )

def normalize_name(name):
    """
    Normalize a location name for comparison.

    Removes punctuation, converts to lowercase,
    expands a few common abbreviations, and removes
    generic location words.
    """

    if name is None:
        return ""

    text = str(name).lower()

    # Replace punctuation with spaces.
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    words = text.split()

    # Normalize common abbreviations.
    abbreviation_map = {
        "rd": "road",
        "st": "street",
        "blr": "bengaluru",
        "bangalore": "bengaluru",
    }

    words = [
        abbreviation_map.get(word, word)
        for word in words
    ]

    ignored_words = {
        "the",
        "at",
        "near",
        "road",
        "street",
        "main",
        "gate",
        "entry",
        "entrance",
        "metro",
        "station",
        "bengaluru",
        "india",
    }

    words = [
        word
        for word in words
        if word not in ignored_words
    ]

    return " ".join(words)

def get_match_text(match):
    """
    Get the text available from an Uber location match.

    Currently the validator primarily uses the Uber
    suggestion text. If additional textual fields are
    available, include them as well.
    """

    parts = []

    if match.get("text"):
        parts.append(str(match["text"]))

    if match.get("address"):
        parts.append(str(match["address"]))

    if match.get("secondary_text"):
        parts.append(str(match["secondary_text"]))

    return " ".join(parts)

def calculate_name_similarity(
    requested_name,
    matched_name,
):
    """
    Calculate name similarity using token overlap.

    Returns a value between 0 and 1.

    The score is based on the fraction of meaningful
    requested-name tokens that also appear in the
    Uber-matched name.
    """

    requested = normalize_name(requested_name)
    matched = normalize_name(matched_name)

    if not requested or not matched:
        return 0.0

    requested_tokens = set(requested.split())
    matched_tokens = set(matched.split())

    if not requested_tokens or not matched_tokens:
        return 0.0

    common_tokens = (
        requested_tokens.intersection(matched_tokens)
    )

    if not common_tokens:
        return 0.0

    return (
        len(common_tokens)
        / len(requested_tokens)
    )

def validate_match(
    match,
    requested_name,
    location_type,
):
    """
    Validate an Uber location match using both:

    1. Geographic distance
    2. Name similarity

    A match is accepted only when both conditions
    are satisfied.
    """

    if match is None:
        return False, "Uber returned no usable location."

    matched_name = get_match_text(match)
    distance_km = match["distance_km"]

    name_similarity = calculate_name_similarity(
        requested_name,
        matched_name,
    )

    if distance_km > MAX_LOCATION_DISTANCE_KM:
        return (
            False,
            (
                f"{location_type} distance too large: "
                f"{distance_km:.3f} km"
            ),
        )

    return True, ""


def main():

    route_reader = RouteReader()

    routes = route_reader.load_routes()

    if not routes:
        print(
            "\nNo routed trips are available "
            "for Uber validation."
        )
        return

    total_available_routes = len(routes)

    already_validated = (
        load_already_validated_routes()
    )

    routes = [
        route
        for route in routes
        if route_key(route)
        not in already_validated
    ]

    if not routes:
        print(
            "\nAll available routes have already "
            "been validated."
        )
        return

    batch_size = min(
        MAX_ROUTES_PER_RUN,
        len(routes),
    )

    routes = random.sample(
        routes,
        batch_size,
    )

    print("=" * 60)
    print("Uber Route Validation")
    print("=" * 60)

    print(
        f"Routes available      : "
        f"{total_available_routes}"
    )

    print(
        f"Already validated     : "
        f"{len(already_validated)}"
    )

    print(
        f"Routes selected       : "
        f"{len(routes)}"
    )

    print("=" * 60)

    collector = UberCollector()

    validated_routes = []
    rejected_routes = []

    try:

        collector.launch()

        total = len(routes)

        for index, route in enumerate(
            routes,
            start=1,
        ):

            pickup_name = route["pickup_name"]
            dropoff_name = route["drop_name"]

            print("\n")
            print("-" * 60)

            print(
                f"[{index}/{total}] "
                f"{pickup_name} -> "
                f"{dropoff_name}"
            )

            print("-" * 60)

            try:

                provider = collector.provider

                provider.current_pickup = pickup_name
                provider.current_dropoff = dropoff_name

                # -------------------------------------------------
                # PICKUP VALIDATION
                # -------------------------------------------------

                provider._navigate_to_homepage()

                provider._click_pickup_button()

                pickup_match = (
                    provider._select_pickup_by_coordinates(
                        route["pickup_latitude"],
                        route["pickup_longitude"],
                    )
                )

                pickup_similarity = (
                    calculate_name_similarity(
                        pickup_name,
                        get_match_text(pickup_match),
                    )
                )

                pickup_valid, pickup_reason = (
                    validate_match(
                        pickup_match,
                        pickup_name,
                        "Pickup",
                    )
                )

                print("\nPickup result:")

                print(
                    f"  Requested : "
                    f"{pickup_name}"
                )

                print(
                    f"  Uber      : "
                    f"{pickup_match['text']}"
                )

                print(
                    f"  Distance  : "
                    f"{pickup_match['distance_km']:.3f} km"
                )

                print(
                    f"  Similarity: "
                    f"{pickup_similarity:.2f}"
                )

                if not pickup_valid:
                    raise ValueError(
                        pickup_reason
                    )

                print(
                    "  ✓ Pickup accepted"
                )

                provider._confirm_pickup()

                # -------------------------------------------------
                # DROP-OFF VALIDATION
                # -------------------------------------------------

                dropoff_match = (
                    provider._select_dropoff_by_coordinates(
                        route["drop_latitude"],
                        route["drop_longitude"],
                    )
                )

                dropoff_similarity = (
                    calculate_name_similarity(
                        dropoff_name,
                        get_match_text(dropoff_match),
                    )
                )

                dropoff_valid, dropoff_reason = (
                    validate_match(
                        dropoff_match,
                        dropoff_name,
                        "Drop-off",
                    )
                )

                print("\nDrop-off result:")

                print(
                    f"  Requested : "
                    f"{dropoff_name}"
                )

                print(
                    f"  Uber      : "
                    f"{dropoff_match['text']}"
                )

                print(
                    f"  Distance  : "
                    f"{dropoff_match['distance_km']:.3f} km"
                )

                print(
                    f"  Similarity: "
                    f"{dropoff_similarity:.2f}"
                )

                if not dropoff_valid:
                    raise ValueError(
                        dropoff_reason
                    )

                print(
                    "  ✓ Drop-off accepted"
                )

                # -------------------------------------------------
                # ROUTE VALID
                # -------------------------------------------------

                validated_row = route.copy()

                validated_row[
                    "uber_pickup"
                ] = pickup_match["text"]

                validated_row[
                    "uber_pickup_distance_km"
                ] = pickup_match[
                    "distance_km"
                ]

                validated_row[
                    "uber_pickup_id"
                ] = pickup_match["id"]

                validated_row[
                    "uber_pickup_name_similarity"
                ] = pickup_similarity

                validated_row[
                    "uber_dropoff"
                ] = dropoff_match["text"]

                validated_row[
                    "uber_dropoff_distance_km"
                ] = dropoff_match[
                    "distance_km"
                ]

                validated_row[
                    "uber_dropoff_id"
                ] = dropoff_match["id"]

                validated_row[
                    "uber_dropoff_name_similarity"
                ] = dropoff_similarity

                validated_row[
                    "validation_status"
                ] = "valid"

                validated_row[
                    "validation_reason"
                ] = ""

                validated_routes.append(
                    validated_row
                )

                print(
                    "\n✓ ROUTE VALID"
                )

            except Exception as e:

                rejected_row = route.copy()

                rejected_row[
                    "validation_status"
                ] = "rejected"

                rejected_row[
                    "validation_reason"
                ] = str(e)

                rejected_routes.append(
                    rejected_row
                )

                print(
                    "\n✗ ROUTE REJECTED"
                )

                print(
                    f"  Reason: {e}"
                )

    finally:

        collector.close()

    # -------------------------------------------------------------
    # SAVE RESULTS
    # -------------------------------------------------------------

    validated_df = pd.DataFrame(
        validated_routes
    )

    rejected_df = pd.DataFrame(
        rejected_routes
    )

    append_dataframe(
        validated_df,
        VALIDATED_ROUTES_FILE,
    )

    append_dataframe(
        rejected_df,
        REJECTED_ROUTES_FILE,
    )

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------

    print("\n")

    print("=" * 60)
    print("Uber Route Validation Summary")
    print("=" * 60)

    print(
        f"Routes tested       : "
        f"{len(routes)}"
    )

    print(
        f"Valid routes        : "
        f"{len(validated_df)}"
    )

    print(
        f"Rejected routes     : "
        f"{len(rejected_df)}"
    )

    print("=" * 60)

    print(
        "\nValidated routes saved to:"
        f"\n{VALIDATED_ROUTES_FILE}"
    )

    print(
        "\nRejected routes saved to:"
        f"\n{REJECTED_ROUTES_FILE}"
    )


if __name__ == "__main__":
    main()