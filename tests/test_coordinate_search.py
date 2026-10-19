from collector.services.providers.uber_provider import (
    UberProvider,
)


def main():

    provider = UberProvider()

    provider.launch()

    try:

        provider._navigate_to_homepage()

        provider._click_pickup_button()

        search_box = (
            provider.page
            .get_by_test_id("enhancer-container-pickup")
            .get_by_role("searchbox")
        )

        search_box.fill(
            "12.8832635, 77.5492301"
        )

        provider.page.wait_for_timeout(
            3000
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
                f"\n--- SUGGESTION {index} ---"
            )

            print(text)

    finally:

        provider.close()


if __name__ == "__main__":
    main()