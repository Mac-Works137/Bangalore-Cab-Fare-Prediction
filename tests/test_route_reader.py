from collector.route_reader import RouteReader


def main():

    reader = RouteReader()

    routes = reader.load_routes()

    print()

    print(f"Loaded {len(routes)} routes")

    print()

    print("First route:")

    print()

    for key, value in routes[0].items():

        print(f"{key:25}: {value}")


if __name__ == "__main__":
    main()