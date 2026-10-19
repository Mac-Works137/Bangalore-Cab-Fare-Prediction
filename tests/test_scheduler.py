from collector.scheduler import CollectionScheduler


def main():

    scheduler = CollectionScheduler()

    context = scheduler.get_collection_context()

    print()

    for key, value in context.items():

        print(f"{key:20}: {value}")


if __name__ == "__main__":
    main()