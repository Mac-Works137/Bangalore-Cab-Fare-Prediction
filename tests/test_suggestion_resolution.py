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

        for index in range(count):

            text = suggestions.nth(
                index
            ).inner_text().strip()

            print(
                f"\n[{index}] {text}"
            )

        print(
            "\n======================================"
        )

        print(
            "Resolving FIRST suggestion only"
        )

        print(
            "======================================"
        )

        result = provider._get_suggestion_coordinates(
            0
        )

        print(
            "\nResult:"
        )

        print(result)

    finally:

        provider.close()


if __name__ == "__main__":
    main()