from collector.services.providers.uber_provider import (
    UberProvider,
)


def main():

    provider = UberProvider()

    provider.launch()

    try:

        provider._navigate_to_homepage()

        provider._click_pickup_button()

        provider._enter_pickup_location(
            "Brand Factory"
        )

        suggestions = provider.page.locator(
            "li[data-testid='pudo-result']"
        )

        count = suggestions.count()

        print(
            f"\nFound {count} suggestions"
        )

        for i in range(count):

            text = suggestions.nth(i).inner_text().strip()

            print(
                f"\n--- SUGGESTION {i} ---"
            )

            print(text)

        # --------------------------------------------------
        # We only want the actual location suggestions.
        # For Brand Factory these are expected to be 0, 1, 2.
        # --------------------------------------------------

        for index in range(min(3, count)):

            print(
                "\n"
                + "=" * 60
            )

            print(
                f"TESTING SUGGESTION {index}"
            )

            print(
                "=" * 60
            )

            # Re-open pickup search before each test.
            if index > 0:

                provider._navigate_to_homepage()

                provider._click_pickup_button()

                provider._enter_pickup_location(
                    "Brand Factory"
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

            provider.page.on(
                "response",
                handle_response
            )

            # --------------------------------------------------
            # Click this specific suggestion.
            # --------------------------------------------------

            suggestion = provider.page.locator(
                "li[data-testid='pudo-result']"
            ).nth(index)

            print(
                "\nClicking:"
            )

            print(
                suggestion.inner_text().strip()
            )

            suggestion.click()

            provider.page.wait_for_timeout(
                3000
            )

            # --------------------------------------------------
            # Print resolve-location responses.
            # --------------------------------------------------

            print(
                f"\nFound {len(responses)} "
                f"pudoResolveLocation responses"
            )

            for response_index, body in enumerate(
                responses
            ):

                print(
                    f"\n--- RESOLVE RESPONSE "
                    f"{response_index} ---"
                )

                print(body)

            provider.page.remove_listener(
                "response",
                handle_response
            )

    finally:

        provider.close()


if __name__ == "__main__":
    main()