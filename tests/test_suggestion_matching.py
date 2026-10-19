from collector.services.providers.uber_provider import (
    UberProvider,
)


def main():

    provider = UberProvider()

    provider.launch()

    graphql_responses = []


    def handle_response(response):

        if "m.uber.com/go/graphql" in response.url:

            try:
                body = response.text()

                graphql_responses.append({
                    "url": response.url,
                    "body": body,
                })

            except Exception:
                pass


    provider.page.on(
        "response",
        handle_response
    )

    try:

        provider._navigate_to_homepage()

        provider._click_pickup_button()

        provider._enter_pickup_location(
            "Brand Factory"
        )

        provider.page.wait_for_timeout(3000)

        print("\n========== PAGE HTML ==========")

        html = provider.page.locator(
            "li[data-testid='pudo-result']"
        ).all_inner_texts()

        for i, text in enumerate(html):

            print(
                f"\n--- RESULT {i} ---"
            )

            print(text)


        print(
            "\n========== GRAPHQL RESPONSES =========="
        )

        print(
            f"Total GraphQL responses: "
            f"{len(graphql_responses)}"
        )


        for i, item in enumerate(
            graphql_responses
        ):

            print(
                f"\n--- GRAPHQL RESPONSE {i} ---"
            )

            print(
                "\nURL:"
            )

            print(
                item["url"]
            )

            print(
                "\nBODY:"
            )

            print(
                item["body"][:10000]
            )


        print(
            "\n========================================"
        )

        print(
            "\n========== BRAND FACTORY IDS =========="
        )

        for item in graphql_responses:

            body = item["body"]

            if (
                "ChIJAf1JhVkRrjsRS8bBseGRfm0"
                in body
            ):
                print(
                    "Found BRAND FACTORY OUTLET ID"
                )

            if (
                "ChIJPYNuVvk_rjsRYk58kDktcRk"
                in body
            ):
                print(
                    "Found correct Brand Factory ID:"
                )

                print(
                    "ChIJPYNuVvk_rjsRYk58kDktcRk"
                )

            if (
                "ChIJbyfpBQA9rjsRHUpzHsdQmKg"
                in body
            ):
                print(
                    "Found Brand factory ID:"
                )

                print(
                    "ChIJbyfpBQA9rjsRHUpzHsdQmKg"
                )

        input(
            "\nPress Enter to close..."
        )

    finally:

        provider.close()


if __name__ == "__main__":
    main()