from models.fare_estimate import FareEstimate



import re

import math

from config.fare import UBER_URL

from config.browser import (
    PROFILE_DIR,
    VIEWPORT,
    GEOLOCATION,
    LOCALE,
    TIMEZONE,
    PERMISSIONS,
)

from playwright.sync_api import (sync_playwright,TimeoutError as PlaywrightTimeoutError,)

from collector.services.providers.base_provider import BaseProvider

class UberLocationNotFoundError(RuntimeError):
    """Uber could not find or resolve the requested location."""
    pass


class UberSuggestionResolutionError(RuntimeError):
    """Uber showed suggestions but none could be resolved."""
    pass


class UberTransientError(RuntimeError):
    """A potentially temporary Uber/Playwright failure occurred."""
    pass

class UberProvider(BaseProvider):
    """
    Collects fare estimates from Uber.
    """

    def __init__(self):

        self.playwright = None

        self.browser = None

        # self.context = None

        self.page = None

        self.current_pickup = None
        self.current_dropoff = None

        self.current_pickup_match = None
        self.current_dropoff_match = None

        self.current_pickup_latitude = None
        self.current_pickup_longitude = None

        # These are supplied by UberCollector
        self.search_timestamp = None
        self.time_slot = None
        self.day_of_week = None

    @property
    def provider_name(self):
        return "Uber"

    def launch(self):
        """
        Launches Playwright using a persistent browser profile.
        """

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport=VIEWPORT,
            geolocation=GEOLOCATION,
            permissions=PERMISSIONS,
            locale=LOCALE,
            timezone_id=TIMEZONE,
        )

        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = self.browser.new_page()

    def _navigate_to_homepage(self):
        """
        Opens the Uber mobile website.
        """

        self.page.goto(
            UBER_URL,
            wait_until="domcontentloaded",
        )

        print(
            "Opened Uber homepage."
        )

    def _click_pickup_button(self):
        """
        Opens the pickup search page.
        """

        pickup_button = self.page.get_by_test_id(
            "pudo-button-pickup"
        )

        pickup_button.click()

        print(
            "Opened pickup search."
        )

    def _enter_pickup_location(
        self,
        pickup_location,
    ):
        """
        Enters the pickup and drop locations.
        """

        pickup_box = (
                self.page
                .get_by_test_id("enhancer-container-pickup")
                .get_by_role("searchbox")
        )

        pickup_box.fill(pickup_location)
        self.current_pickup = pickup_location
        self.page.wait_for_timeout(1000)

        print(f"Entered pickup: {pickup_location}")

    def _enter_coordinate_location(
        self,
        latitude,
        longitude,
        location_type,
    ):
        """
        Searches Uber using the exact coordinates of the
        intended location.

        This avoids ambiguity when multiple Uber suggestions
        have the same or similar names.
        """

        search_text = (
            f"{latitude}, {longitude}"
        )

        if location_type == "pickup":

            search_box = (
                self.page
                .get_by_test_id(
                    "enhancer-container-pickup"
                )
                .get_by_role("searchbox")
            )

        elif location_type == "dropoff":

            candidates = [

                self.page.locator(
                    'input[placeholder="Dropoff location"]'
                ),

                self.page.locator(
                    'input[placeholder="Drop-off location"]'
                ),

                self.page.get_by_role(
                    "searchbox"
                ).nth(1),
            ]

            search_box = None

            for locator in candidates:

                try:

                    locator.wait_for(
                        state="visible",
                        timeout=1500,
                    )

                    search_box = locator

                    break

                except Exception:

                    pass

            if search_box is None:

                raise RuntimeError(
                    "Unable to locate the drop-off "
                    "search box."
                )

        else:

            raise ValueError(
                f"Unknown location type: "
                f"{location_type}"
            )

        search_box.fill(
            search_text
        )

        self.page.wait_for_timeout(
            1500
        )

        print(
            f"Entered coordinates: {search_text}"
        )

    def _candidate_search_terms(
        self,
        location_name,
    ):
        """
        Generates search terms from most specific to least specific.

        The original location name is always tried first.
        """

        location_name = str(
            location_name
        ).strip()

        if not location_name:
            return []

        words = location_name.split()

        candidates = [
            location_name
        ]

        while len(words) > 1:

            words = words[:-1]

            candidate = " ".join(words)

            if len(candidate) >= 10:
                candidates.append(candidate)

        return candidates

    def _distance_km(
        self,
        latitude1,
        longitude1,
        latitude2,
        longitude2,
    ):
        """
        Calculates the approximate distance between two
        latitude/longitude points using the Haversine formula.
        """

        try:

            latitude1 = float(latitude1)
            longitude1 = float(longitude1)
            latitude2 = float(latitude2)
            longitude2 = float(longitude2)

        except (TypeError, ValueError):

            return None

        earth_radius_km = 6371.0

        lat1 = math.radians(latitude1)
        lat2 = math.radians(latitude2)

        delta_lat = math.radians(
            latitude2 - latitude1
        )

        delta_lon = math.radians(
            longitude2 - longitude1
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            +
            math.cos(lat1)
            *
            math.cos(lat2)
            *
            math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return earth_radius_km * c

    def _get_suggestion_coordinates(
        self,
        suggestion_index,
    ):
        """
        Clicks one Uber suggestion and captures the coordinates
        returned by pudoResolveLocation.

        Returns:
            {
                "text": str,
                "latitude": float,
                "longitude": float,
                "id": str,
            }

            or None if the coordinates could not be resolved.
        """

        suggestions = self.page.locator(
            "li[data-testid='pudo-result']"
        )

        suggestion = suggestions.nth(
            suggestion_index
        )

        suggestion_text = (
            suggestion
            .inner_text()
            .strip()
        )

        responses = []

        def handle_response(response):

            if "m.uber.com/go/graphql" not in response.url:
                return

            try:

                body = response.text()

                if "pudoResolveLocation" in body:

                    responses.append(body)

            except Exception:

                pass

        self.page.on(
            "response",
            handle_response,
        )

        try:

            suggestion.click()

            self.page.wait_for_timeout(
                1500
            )

        finally:

            self.page.remove_listener(
                "response",
                handle_response,
            )

        if not responses:
            return None

        import json

        try:

            data = json.loads(
                responses[-1]
            )

            location = (
                data
                .get("data", {})
                .get("pudoResolveLocation")
            )

            if not location:
                return None

            coordinate = location.get(
                "coordinate"
            )

            if not coordinate:
                return None

            return {
                "text": suggestion_text,

                "latitude": coordinate.get(
                    "latitude"
                ),

                "longitude": coordinate.get(
                    "longitude"
                ),

                "id": location.get(
                    "id"
                ),
            }

        except Exception:

            return None

    def _select_coordinate_suggestion(
        self,
        latitude,
        longitude,
        location_type,
    ):
        """
        Searches Uber using coordinates and selects the
        geographically closest valid suggestion.

        A suggestion is accepted only when its resolved
        coordinates are within 0.1 km of the requested
        coordinates.
        """

        suggestions = self.page.locator(
            "li[data-testid='pudo-result']"
        )

        try:
            suggestions.first.wait_for(
                state="visible",
                timeout=5000,
            )
        except PlaywrightTimeoutError:
            raise UberLocationNotFoundError(
                "No Uber coordinate suggestions found."
            )

        suggestion_texts = []

        count = suggestions.count()

        print(
            f"\nFound {count} Uber coordinate suggestions"
        )

        for index in range(count):
            try:
                text = (
                    suggestions
                    .nth(index)
                    .inner_text()
                    .strip()
                )
            except Exception:
                continue

            lower_text = text.lower()

            if (
                "set location on map" in lower_text
                or "see more results" in lower_text
                or "saved places" in lower_text
            ):
                continue

            suggestion_texts.append(text)

        print(
            f"\nActual coordinate suggestions: "
            f"{len(suggestion_texts)}"
        )

        if not suggestion_texts:
            raise UberSuggestionResolutionError(
                "Uber returned no usable coordinate suggestions."
            )

        candidates = []

        for candidate_number, suggestion_text in enumerate(
            suggestion_texts
        ):
            print(
                f"\n--- Testing coordinate suggestion "
                f"{candidate_number + 1}/{len(suggestion_texts)} ---"
            )

            print(suggestion_text)

            # ------------------------------------------------------
            # Find the candidate in the CURRENT suggestion list.
            # ------------------------------------------------------

            suggestions = self.page.locator(
                "li[data-testid='pudo-result']"
            )

            matching_suggestion = None

            current_count = suggestions.count()

            for index in range(current_count):
                try:
                    current_text = (
                        suggestions
                        .nth(index)
                        .inner_text()
                        .strip()
                    )
                except Exception:
                    continue

                if current_text == suggestion_text:
                    matching_suggestion = (
                        suggestions.nth(index)
                    )
                    break

            if matching_suggestion is None:
                print(
                    f"Suggestion disappeared: "
                    f"{suggestion_text}"
                )

                # Rebuild the correct search state.
                self._navigate_to_homepage()

                if location_type == "pickup":
                    self._click_pickup_button()

                elif location_type == "dropoff":
                    self._click_pickup_button()

                    self._enter_pickup_location(
                        self.current_pickup
                    )

                    self._select_suggestion(
                        self.current_pickup,
                        self.current_pickup_latitude,
                        self.current_pickup_longitude,
                        "pickup",
                    )

                    self._confirm_pickup()

                else:
                    raise ValueError(
                        f"Unknown location type: "
                        f"{location_type}"
                    )

                self._enter_coordinate_location(
                    latitude,
                    longitude,
                    location_type,
                )

                continue

            # ------------------------------------------------------
            # Capture pudoResolveLocation.
            # ------------------------------------------------------

            responses = []

            def handle_response(response):
                if "m.uber.com/go/graphql" not in response.url:
                    return

                try:
                    body = response.text()

                    if "pudoResolveLocation" in body:
                        responses.append(body)

                except Exception:
                    pass

            self.page.on(
                "response",
                handle_response,
            )

            try:
                matching_suggestion.click()

                self.page.wait_for_timeout(
                    1500
                )

            finally:
                self.page.remove_listener(
                    "response",
                    handle_response,
                )

            # ------------------------------------------------------
            # Could not resolve this suggestion.
            # ------------------------------------------------------

            if not responses:
                print(
                    f"Could not resolve suggestion: "
                    f"{suggestion_text}"
                )

                self._navigate_to_homepage()

                if location_type == "pickup":
                    self._click_pickup_button()

                elif location_type == "dropoff":
                    self._click_pickup_button()

                    self._enter_pickup_location(
                        self.current_pickup
                    )

                    self._select_suggestion(
                        self.current_pickup,
                        self.current_pickup_latitude,
                        self.current_pickup_longitude,
                        "pickup",
                    )

                    self._confirm_pickup()

                else:
                    raise ValueError(
                        f"Unknown location type: "
                        f"{location_type}"
                    )

                self._enter_coordinate_location(
                    latitude,
                    longitude,
                    location_type,
                )

                continue

            # ------------------------------------------------------
            # Parse pudoResolveLocation response.
            # ------------------------------------------------------

            import json

            try:
                data = json.loads(
                    responses[-1]
                )

                location = (
                    data
                    .get("data", {})
                    .get("pudoResolveLocation")
                )

                if not location:
                    raise ValueError(
                        "pudoResolveLocation missing"
                    )

                coordinate = location.get(
                    "coordinate"
                )

                if not coordinate:
                    raise ValueError(
                        "coordinate missing"
                    )

                result = {
                    "text": suggestion_text,
                    "latitude": coordinate.get(
                        "latitude"
                    ),
                    "longitude": coordinate.get(
                        "longitude"
                    ),
                    "id": location.get(
                        "id"
                    ),
                }

            except Exception as e:
                print(
                    f"Could not parse suggestion "
                    f"{suggestion_text}: {e}"
                )

                self._navigate_to_homepage()

                if location_type == "pickup":
                    self._click_pickup_button()

                elif location_type == "dropoff":
                    self._click_pickup_button()

                    self._enter_pickup_location(
                        self.current_pickup
                    )

                    self._select_suggestion(
                        self.current_pickup,
                        self.current_pickup_latitude,
                        self.current_pickup_longitude,
                        "pickup",
                    )

                    self._confirm_pickup()

                else:
                    raise ValueError(
                        f"Unknown location type: "
                        f"{location_type}"
                    )

                self._enter_coordinate_location(
                    latitude,
                    longitude,
                    location_type,
                )

                continue

            # ------------------------------------------------------
            # Calculate geographic distance.
            # ------------------------------------------------------

            distance = self._distance_km(
                latitude,
                longitude,
                result["latitude"],
                result["longitude"],
            )

            if distance is None:
                print(
                    f"Could not calculate distance "
                    f"for {suggestion_text}."
                )

                self._navigate_to_homepage()

                if location_type == "pickup":
                    self._click_pickup_button()

                elif location_type == "dropoff":
                    self._click_pickup_button()

                    self._enter_pickup_location(
                        self.current_pickup
                    )

                    self._select_suggestion(
                        self.current_pickup,
                        self.current_pickup_latitude,
                        self.current_pickup_longitude,
                        "pickup",
                    )

                    self._confirm_pickup()

                else:
                    raise ValueError(
                        f"Unknown location type: "
                        f"{location_type}"
                    )

                self._enter_coordinate_location(
                    latitude,
                    longitude,
                    location_type,
                )

                continue

            result["distance_km"] = distance

            candidates.append(result)

            print(
                f"\nResolved:"
                f"\n  Name: {result['text']}"
                f"\n  ID: {result['id']}"
                f"\n  Coordinates: "
                f"{result['latitude']}, "
                f"{result['longitude']}"
                f"\n  Distance: "
                f"{distance:.3f} km"
            )

            # ------------------------------------------------------
            # Valid coordinate match.
            # ------------------------------------------------------

            if distance <= 0.1:
                print(
                    "\nCoordinate match is within "
                    "the 0.1 km threshold."
                )

                print(
                    "\n=================================================="
                )

                print(
                    "SELECTED COORDINATE LOCATION"
                )

                print(
                    f"Name        : {result['text']}"
                )

                print(
                    f"ID          : {result['id']}"
                )

                print(
                    f"Coordinates : "
                    f"{result['latitude']}, "
                    f"{result['longitude']}"
                )

                print(
                    f"Distance    : "
                    f"{distance:.3f} km"
                )

                print(
                    "=================================================="
                )

                return result

            print(
                f"\nCandidate rejected because it is "
                f"{distance:.3f} km away."
            )

            # ------------------------------------------------------
            # Rebuild the correct search state before testing
            # the next candidate.
            # ------------------------------------------------------

            self._navigate_to_homepage()

            if location_type == "pickup":
                self._click_pickup_button()

            elif location_type == "dropoff":
                self._click_pickup_button()

                self._enter_pickup_location(
                    self.current_pickup
                )

                self._select_suggestion(
                    self.current_pickup,
                    self.current_pickup_latitude,
                    self.current_pickup_longitude,
                    "pickup",
                )

                self._confirm_pickup()

            else:
                raise ValueError(
                    f"Unknown location type: "
                    f"{location_type}"
                )

            self._enter_coordinate_location(
                latitude,
                longitude,
                location_type,
            )

        # ----------------------------------------------------------
        # No candidate was within 0.1 km.
        # ----------------------------------------------------------

        if not candidates:
            raise UberSuggestionResolutionError(
                "Unable to resolve any Uber location "
                f"for coordinates {latitude}, {longitude}."
            )

        best = min(
            candidates,
            key=lambda candidate:
            candidate["distance_km"],
        )

        print(
            "\n=================================================="
        )

        print(
            "CLOSEST COORDINATE LOCATION"
        )

        print(
            f"Name        : {best['text']}"
        )

        print(
            f"ID          : {best['id']}"
        )

        print(
            f"Coordinates : "
            f"{best['latitude']}, "
            f"{best['longitude']}"
        )

        print(
            f"Distance    : "
            f"{best['distance_km']:.3f} km"
        )

        print(
            "=================================================="
        )

        raise UberSuggestionResolutionError(
            "Uber returned no location within "
            f"0.1 km of coordinates "
            f"{latitude}, {longitude}."
        )
    
    def _select_pickup_by_coordinates(
        self,
        latitude,
        longitude,
    ):
        """
        Searches for and selects the pickup using coordinates.
        """

        self._enter_coordinate_location(
            latitude,
            longitude,
            "pickup",
        )

        result = (
            self._select_coordinate_suggestion(
                latitude,
                longitude,
                "pickup",
            )
        )

        self.current_pickup_match = result

        return result


    def _select_dropoff_by_coordinates(
        self,
        latitude,
        longitude,
    ):
        """
        Searches for and selects the drop-off using coordinates.
        """

        self._enter_coordinate_location(
            latitude,
            longitude,
            "dropoff",
        )

        result = (
            self._select_coordinate_suggestion(
                latitude,
                longitude,
                "dropoff",
            )
        )

        self.current_dropoff_match = result

        return result

    def _restore_location_search(
        self,
        location_name,
        location_type,
    ):
        """
        Restores the appropriate Uber search screen after
        resolving one suggestion.

        For pickup:
            Homepage -> pickup search

        For drop-off:
            Homepage -> pickup search -> restore pickup
            -> drop-off search
        """

        self._navigate_to_homepage()

        # --------------------------------------------------
        # PICKUP SEARCH
        # --------------------------------------------------

        if location_type == "pickup":

            self._click_pickup_button()

            self._enter_pickup_location(
                location_name
            )

        # --------------------------------------------------
        # DROP-OFF SEARCH
        #
        # We must reconstruct the entire trip because
        # navigating to the homepage loses the selected pickup.
        # --------------------------------------------------

        elif location_type == "dropoff":

            if (
                self.current_pickup is None
                or
                self.current_pickup_latitude is None
                or
                self.current_pickup_longitude is None
            ):

                raise RuntimeError(
                    "Cannot restore drop-off search because "
                    "the original pickup information is missing."
                )

            # Restore pickup search.
            self._click_pickup_button()

            self._enter_pickup_location(
                self.current_pickup
            )

            # Re-select the original pickup using its
            # coordinates.
            self._select_pickup_suggestion(
                self.current_pickup,
                self.current_pickup_latitude,
                self.current_pickup_longitude,
            )

            # Confirm pickup / move to drop-off page.
            self._confirm_pickup()

            # Enter the drop-off again.
            self._enter_dropoff_location(
                location_name
            )

        else:

            raise ValueError(
                f"Unknown location type: "
                f"{location_type}"
            )

        self.page.wait_for_timeout(
            1000
        )

    def _select_suggestion(
        self,
        location_name,
        latitude,
        longitude,
        location_type,
    ):
        """
        Searches Uber by location name and selects the best
        geographically valid suggestion.

        Suggestions are ranked by name similarity first.
        Candidates are then resolved one at a time.

        If a candidate cannot be resolved or is geographically
        invalid, the same search is performed again before
        testing the next candidate.

        This avoids relying on browser history to restore the
        suggestion list.
        """

        def get_suggestion_texts():
            """
            Reads the currently visible Uber location suggestions.
            """

            suggestions = self.page.locator(
                "li[data-testid='pudo-result']"
            )

            try:
                suggestions.first.wait_for(
                    state="visible",
                    timeout=5000,
                )
            except PlaywrightTimeoutError:
                raise UberLocationNotFoundError(
                    f"No Uber suggestions found "
                    f"for '{location_name}'."
                )

            suggestion_texts = []
            count = suggestions.count()

            print(
                f"\nFound {count} Uber suggestions"
            )

            for index in range(count):
                try:
                    text = (
                        suggestions
                        .nth(index)
                        .inner_text()
                        .strip()
                    )
                except Exception:
                    continue

                lower_text = text.lower()

                if (
                    "set location on map" in lower_text
                    or "see more results" in lower_text
                    or "saved places" in lower_text
                ):
                    continue

                suggestion_texts.append(text)

            print(
                f"\nActual location suggestions: "
                f"{len(suggestion_texts)}"
            )

            if not suggestion_texts:
                raise UberSuggestionResolutionError(
                    f"Uber returned no usable suggestions "
                    f"for '{location_name}'."
                )

            return suggestion_texts

        def restore_search():
            """
            Recreates the same location search after a candidate
            has been rejected or could not be resolved.

            For pickup, the pickup search is opened again.

            For drop-off, the current drop-off search is reused
            whenever possible. If Uber has navigated away from the
            drop-off page, the method falls back to rebuilding the
            pickup/drop-off state.
            """

            if location_type == "pickup":

                self._navigate_to_homepage()
                self._click_pickup_button()
                self._enter_pickup_location(
                    location_name
                )

                return

            if location_type != "dropoff":
                raise ValueError(
                    f"Unknown location type: "
                    f"{location_type}"
                )

            # --------------------------------------------------
            # Try to return to the existing drop-off page first.
            # --------------------------------------------------

            if "/go/drop" in self.page.url:

                self._enter_dropoff_location(
                    location_name
                )

                return

            # --------------------------------------------------
            # If Uber navigated away from the drop-off page,
            # rebuild the trip.
            #
            # This is only a fallback. Under normal operation,
            # go_back() should return us to /go/drop.
            # --------------------------------------------------

            self._navigate_to_homepage()
            self._click_pickup_button()

            self._enter_pickup_location(
                self.current_pickup
            )

            pickup_match = self._select_suggestion(
                self.current_pickup,
                self.current_pickup_latitude,
                self.current_pickup_longitude,
                "pickup",
            )

            self.current_pickup_match = pickup_match

            self._confirm_pickup()

            self._enter_dropoff_location(
                location_name
            )

        # ------------------------------------------------------
        # Initial search
        # ------------------------------------------------------

        suggestion_texts = get_suggestion_texts()

        requested_name = (
            str(location_name)
            .strip()
            .lower()
        )

        requested_words = set(
            re.findall(
                r"[a-z0-9]+",
                requested_name,
            )
        )

        # ------------------------------------------------------
        # Rank suggestions by name similarity.
        # ------------------------------------------------------

        ranked_suggestions = []

        for suggestion_text in suggestion_texts:

            suggestion_name = (
                suggestion_text
                .splitlines()[0]
                .strip()
                .lower()
            )

            suggestion_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    suggestion_name,
                )
            )

            common_words = (
                requested_words
                &
                suggestion_words
            )

            if requested_words:
                name_match_ratio = (
                    len(common_words)
                    /
                    len(requested_words)
                )
            else:
                name_match_ratio = 0.0

            ranked_suggestions.append(
                {
                    "text": suggestion_text,
                    "name_match_ratio": name_match_ratio,
                }
            )

        name_matched = [
            candidate
            for candidate in ranked_suggestions
            if candidate["name_match_ratio"] > 0
        ]

        if name_matched:

            candidates_to_test = name_matched

            candidates_to_test.sort(
                key=lambda candidate:
                -candidate["name_match_ratio"]
            )

            print("\nRanked name matches:")

        else:

            candidates_to_test = ranked_suggestions

            print(
                "\nNo meaningful name match found."
            )

            print(
                "Falling back to geographic validation "
                "of all returned suggestions."
            )

        for index, candidate in enumerate(
            candidates_to_test,
            start=1,
        ):
            print(
                f"{index}. "
                f"{candidate['text'].splitlines()[0]} "
                f"(name match: "
                f"{candidate['name_match_ratio']:.2f})"
            )

        # ------------------------------------------------------
        # Resolve candidates one at a time.
        # ------------------------------------------------------

        for candidate_number, candidate in enumerate(
            candidates_to_test
        ):

            suggestion_text = candidate["text"]

            print(
                f"\n--- Testing ranked suggestion "
                f"{candidate_number} ---"
            )

            print(suggestion_text)

            # --------------------------------------------------
            # Find the candidate in the CURRENT suggestion list.
            # --------------------------------------------------

            suggestions = self.page.locator(
                "li[data-testid='pudo-result']"
            )

            matching_suggestion = None

            current_count = suggestions.count()

            for index in range(current_count):

                try:
                    current_text = (
                        suggestions
                        .nth(index)
                        .inner_text()
                        .strip()
                    )
                except Exception:
                    continue

                if current_text == suggestion_text:

                    matching_suggestion = (
                        suggestions.nth(index)
                    )

                    break

            # --------------------------------------------------
            # Candidate disappeared.
            # --------------------------------------------------

            if matching_suggestion is None:

                print(
                    f"Suggestion disappeared: "
                    f"{suggestion_text}"
                )

                if (
                    candidate_number
                    <
                    len(candidates_to_test) - 1
                ):
                    restore_search()

                continue

            # --------------------------------------------------
            # Capture pudoResolveLocation.
            # --------------------------------------------------

            responses = []

            def handle_response(response):

                if "m.uber.com/go/graphql" not in response.url:
                    return

                try:

                    body = response.text()

                    if "pudoResolveLocation" in body:
                        responses.append(body)

                except Exception:
                    pass

            self.page.on(
                "response",
                handle_response,
            )

            try:

                matching_suggestion.click()

                self.page.wait_for_timeout(
                    1500
                )

            finally:

                self.page.remove_listener(
                    "response",
                    handle_response,
                )

            # --------------------------------------------------
            # Candidate could not be resolved.
            # --------------------------------------------------

            if not responses:

                print(
                    f"Could not resolve suggestion: "
                    f"{suggestion_text}"
                )

                if (
                    candidate_number
                    <
                    len(candidates_to_test) - 1
                ):

                    try:
                        self.page.go_back(
                            wait_until="domcontentloaded"
                        )

                        self.page.wait_for_timeout(
                            1000
                        )

                    except Exception:
                        pass

                    restore_search()

                continue

            # --------------------------------------------------
            # Parse pudoResolveLocation.
            # --------------------------------------------------

            import json

            try:

                data = json.loads(
                    responses[-1]
                )

                location = (
                    data
                    .get("data", {})
                    .get("pudoResolveLocation")
                )

                if not location:
                    raise ValueError(
                        "pudoResolveLocation missing"
                    )

                coordinate = location.get(
                    "coordinate"
                )

                if not coordinate:
                    raise ValueError(
                        "coordinate missing"
                    )

                result = {
                    "text": suggestion_text,
                    "latitude": coordinate.get(
                        "latitude"
                    ),
                    "longitude": coordinate.get(
                        "longitude"
                    ),
                    "id": location.get(
                        "id"
                    ),
                }

            except Exception as e:

                print(
                    f"Could not parse suggestion "
                    f"{suggestion_text}: {e}"
                )

                if (
                    candidate_number
                    <
                    len(candidates_to_test) - 1
                ):

                    try:
                        self.page.go_back(
                            wait_until="domcontentloaded"
                        )

                        self.page.wait_for_timeout(
                            1000
                        )

                    except Exception:
                        pass

                    restore_search()

                continue

            # --------------------------------------------------
            # Calculate geographic distance.
            # --------------------------------------------------

            distance = self._distance_km(
                latitude,
                longitude,
                result["latitude"],
                result["longitude"],
            )

            if distance is None:

                print(
                    f"Could not calculate distance "
                    f"for {suggestion_text}."
                )

                if (
                    candidate_number
                    <
                    len(candidates_to_test) - 1
                ):

                    try:
                        self.page.go_back(
                            wait_until="domcontentloaded"
                        )

                        self.page.wait_for_timeout(
                            1000
                        )

                    except Exception:
                        pass

                    restore_search()

                continue

            result["distance_km"] = distance

            result["name_match_ratio"] = (
                candidate["name_match_ratio"]
            )

            print(
                f"\nCandidate:"
                f"\n  Name: {result['text']}"
                f"\n  ID: {result['id']}"
                f"\n  Coordinates: "
                f"{result['latitude']}, "
                f"{result['longitude']}"
                f"\n  Distance: "
                f"{distance:.3f} km"
                f"\n  Name match: "
                f"{candidate['name_match_ratio']:.2f}"
            )

            # --------------------------------------------------
            # Valid geographic match.
            # --------------------------------------------------

            if distance <= 0.1:

                print(
                    "\n=================================================="
                )

                print(
                    "SELECTED LOCATION"
                )

                print(
                    f"Name        : {result['text']}"
                )

                print(
                    f"ID          : {result['id']}"
                )

                print(
                    f"Coordinates : "
                    f"{result['latitude']}, "
                    f"{result['longitude']}"
                )

                print(
                    f"Distance    : "
                    f"{result['distance_km']:.3f} km"
                )

                print(
                    f"Name match  : "
                    f"{result['name_match_ratio']:.2f}"
                )

                print(
                    "=================================================="
                )

                return result

            # --------------------------------------------------
            # Candidate is geographically invalid.
            # --------------------------------------------------

            print(
                f"\nCandidate rejected because it is "
                f"{distance:.3f} km away."
            )

            # --------------------------------------------------
            # Do not restore after the final candidate.
            # --------------------------------------------------

            if (
                candidate_number
                <
                len(candidates_to_test) - 1
            ):

                try:

                    self.page.go_back(
                        wait_until="domcontentloaded"
                    )

                    self.page.wait_for_timeout(
                        1000
                    )

                except Exception as e:

                    print(
                        f"Could not return to search page: "
                        f"{e}"
                    )

                # Re-run the search so Uber recreates
                # the suggestion DOM.
                restore_search()

        raise ValueError(
            f"Uber returned no location within "
            f"0.1 km of '{location_name}'."
        )

    def _select_pickup_suggestion(
        self,
        pickup_location,
        latitude,
        longitude,
    ):
        """
        Selects the Uber pickup suggestion closest to the
        intended coordinates and remembers the coordinates
        so that the pickup can be reconstructed if necessary.
        """

        match = self._select_suggestion(
            pickup_location,
            latitude,
            longitude,
            "pickup",
        )

        self.current_pickup_match = match

        self.current_pickup_latitude = latitude
        self.current_pickup_longitude = longitude

        return match

    def _confirm_pickup(self):
        """
        Confirms the pickup only if Uber asks for it.
        Some sessions skip this page and go directly
        to the drop-off page.
        """

        print(f"Current URL: {self.page.url}")

        # Already on the drop-off page
        if "/go/drop" in self.page.url:
            print("Pickup already confirmed.")
            return

        confirm_button = self.page.locator(
            'button[aria-label="Confirm pick-up"]'
        )

        try:
            confirm_button.wait_for(
                state="visible",
                timeout=5000
            )

            confirm_button.click()

            self.page.wait_for_url("**/go/drop**")

            print("Confirmed pickup.")

        except PlaywrightTimeoutError:
            print("Pickup confirmation page was skipped.")

    def _enter_dropoff_location(
        self,
        dropoff_location,
    ):
        """
        Enters the drop-off location.
        """

        candidates = [

            self.page.locator(
                'input[placeholder="Dropoff location"]'
            ),

            self.page.locator(
                'input[placeholder="Drop-off location"]'
            ),

            self.page.get_by_role(
                "searchbox"
            ).nth(1),

        ]

        drop_box = None

        for locator in candidates:

            try:

                locator.wait_for(
                    state="visible",
                    timeout=1500,
                )

                drop_box = locator

                break

            except Exception:

                pass

        if drop_box is None:
            raise RuntimeError(
                "Unable to locate the drop-off input box."
            )

        drop_box.fill(
            dropoff_location
        )

        self.current_dropoff = dropoff_location

        self.page.wait_for_timeout(1000)

        print(
            f"Entered drop-off: {dropoff_location}"
        )

    def _select_dropoff_suggestion(
        self,
        dropoff_location,
        latitude,
        longitude,
    ):
        match = self._select_suggestion(
            dropoff_location,
            latitude,
            longitude,
            "dropoff",
        )

        self.current_dropoff_match = match

        return match

    def _confirm_dropoff(self):
        """
        Confirms the drop-off only if Uber asks for it.
        Some sessions go directly to product selection.
        """

        print(f"Current URL: {self.page.url}")

        # Already on the ride-selection page
        if "/go/product-selection" in self.page.url:
            print("Drop-off already confirmed.")
            self.page.wait_for_timeout(2000)
            self._print_current_trip()
            return

        confirm_button = self.page.get_by_role(
            "button",
            name="Confirm drop-off"
        )

        try:
            confirm_button.wait_for(
                state="visible",
                timeout=5000
            )

            confirm_button.click()

            self.page.wait_for_url("**/product-selection**")

            print("Confirmed drop-off.")
            
            self.page.wait_for_timeout(2000)

            self._print_current_trip()

        except PlaywrightTimeoutError:
            print("Drop-off confirmation page was skipped.")

    def _print_current_trip(self):
        """
        Prints the currently selected pickup and drop-off.
        """

        print("\n========== CURRENT TRIP ==========")

        if self.current_pickup_match:
            print(
                f"From: "
                f"{self.current_pickup_match['text']}"
            )
        else:
            print(
                f"From: {self.current_pickup}"
            )

        if self.current_dropoff_match:
            print(
                f"To: "
                f"{self.current_dropoff_match['text']}"
            )
        else:
            print(
                f"To: {self.current_dropoff}"
            )

        print("=================================\n")

    def _print_browser_location(self):
        """
        Prints the browser's current geolocation.
        """

        location = self.page.evaluate(
            """
            () => new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    pos => resolve({
                        latitude: pos.coords.latitude,
                        longitude: pos.coords.longitude
                    }),
                    err => reject(err)
                );
            })
            """
        )

        print(location)

    def _wait_for_homepage(self):
        """
        Waits until the Uber homepage is ready for interaction
        """
        pass

    def _parse_price(
        self,
        price,
    ):
        """
        Converts an Uber price into a float.

        Examples:
            ₹1,234.56      -> 1234.56
            ₹325.00/hour   -> 325.00

        Returns None if the value cannot be parsed.
        """

        if price is None:
            return None

        match = re.search(
            r"₹\s*([\d,]+(?:\.\d+)?)",
            price,
        )

        if not match:
            return None

        try:

            return float(
                match.group(1).replace(",", "")
            )

        except ValueError:

            return None

    def _parse_eta(
        self,
        eta,
    ):
        """
        Converts:
            7 mins away
        into
            7
        """

        if eta is None:
            return None

        match = re.search(
            r"\d+",
            eta,
        )

        if match:
            return int(match.group())

        return None


    def _split_description(
        self,
        description,
    ):
        """
        Separates promotions from ride descriptions.
        """

        if not description:
            return None, None

        promotions = {
            "Good deal",
            "Cheaper",
            "Fastest",
            "Recommended",
            "Popular",
            "Best price",
            "Best value",
            "Faster",
        }

        if description in promotions:
            return description, None

        return None, description

    """
    def _debug_ride_cards(self):

        print(
            "\n========================================"
        )

        print(
            "DEBUGGING RIDE CARD DOM"
        )

        print(
            "========================================"
        )

        elements = self.page.locator(
            "text=/₹/"
        )

        count = elements.count()

        print(
            f"\nElements containing ₹: {count}"
        )

        for i in range(
            min(count, 20)
        ):

            element = elements.nth(i)

            try:

                print(
                    f"\n--- ELEMENT {i} ---"
                )

                print(
                    f"Tag: "
                    f"{element.evaluate('(el) => el.tagName')}"
                )

                print(
                    f"Test ID: "
                    f"{element.get_attribute('data-testid')}"
                )

                print(
                    f"Class: "
                    f"{element.get_attribute('class')}"
                )

                print(
                    f"Text:\n"
                    f"{element.inner_text()[:500]}"
                )

            except Exception as e:

                print(
                    f"Could not inspect element {i}: {e}"
                )

        print(
            "\n========================================"
        )
    """
        
    def collect_fares(self):
        """
        Parses all visible Uber ride cards.
        """

        print("\nWaiting for ride cards...")

        self.page.wait_for_timeout(5000)

        # self._debug_ride_cards()

        cards = self.page.locator(
            'li[data-testid="product_selector.list_item"]'
        )

        count = cards.count()

        print(f"\nFound {count} ride cards\n")

        fares = []

        for i in range(count):

            card = cards.nth(i)

            if not card.is_visible():
                continue

            text = card.inner_text().strip()

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            #
            # Ride name + seats
            #

            first = lines[0]

            match = re.match(r"(.+?)(\d+)$", first)

            if match:
                ride_name = match.group(1).strip()
                seats = int(match.group(2))
            else:
                ride_name = first
                seats = None

            #
            # Prices
            #

            prices = []

            for line in lines:

                # Ignore rental hourly rates such as:
                # ₹325.00/hour
                if (
                    line.startswith("₹")
                    and "/hour" not in line
                ):
                    prices.append(line)

            current_price = (
                self._parse_price(prices[0])
                if prices
                else None
            )

            original_price = (
                self._parse_price(prices[1])
                if len(prices) > 1
                else None
            )      
            #
            # ETA
            #

            eta = None
            arrival = None

            for line in lines:

                if (
                    "min away" in line
                    or
                    "mins away" in line
                ):

                    parts = line.split("•")

                    eta = parts[0].strip()

                    if len(parts) > 1:
                        arrival = parts[1].strip()

                    break

            #
            # Description / Promotion
            #

            description = None
            promotion = None

            eta_minutes = self._parse_eta(
                eta
            )

            for line in reversed(lines):

                if (
                    not line.startswith("₹")
                    and "/hour" not in line
                    and "min away" not in line
                    and "mins away" not in line
                    and line != first
                    and line != "Unavailable"
                ):

                    promotion, description = (
                        self._split_description(line)
                    )

                    break

            fare = FareEstimate(

                provider=self.provider_name,

                pickup=self.current_pickup,

                dropoff=self.current_dropoff,

                ride_name=ride_name,

                seats=seats,

                current_price=current_price,

                original_price=original_price,

                eta_minutes=eta_minutes,

                arrival_time=arrival,

                promotion=promotion,

                description=description,

                timestamp=self.search_timestamp,

                time_slot=self.time_slot,

                day_of_week=self.day_of_week,
            )

            fares.append(fare)

        return fares

    def close(self):
        """
        Closes all Playwright resources.
        """

        """
        if self.page is not None:
            self.page.close()

        if self.context is not None:
            self.context.close()
        """

        if self.browser is not None:
            self.browser.close()

            if self.playwright is not None:
                self.playwright.stop()