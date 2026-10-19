from collector.services.providers.uber_provider import UberProvider
from config.uber_location_search import (
    LOCATION_SEARCH_ALIASES,
)

class UberLocationValidator:

    def __init__(self):

        self.provider = UberProvider()

    def launch(self):
        self.provider.launch()
        self.provider._navigate_to_homepage()

    def close(self):
        self.provider.close()

    def validate(
        self,
        location_name,
    ):
        """
        Tries the original location name followed by
        configured Uber search aliases.

        Returns:
            (is_valid, matched_text, search_used)
        """

        search_terms = [
            location_name
        ]

        search_terms.extend(
            LOCATION_SEARCH_ALIASES.get(
                location_name,
                []
            )
        )

        for search_term in search_terms:

            try:

                self.provider._navigate_to_homepage()

                self.provider._click_pickup_button()

                self.provider._enter_pickup_location(
                    search_term
                )

                matched = (
                    self.provider._select_pickup_suggestion(
                        search_term
                    )
                )

                return True, matched, search_term

            except Exception:

                continue

        return False, "", ""