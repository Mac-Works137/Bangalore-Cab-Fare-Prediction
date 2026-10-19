import json
import glob
from pathlib import Path

KEYWORDS = [
    "Uber",
    "Premier",
    "Go",
    "fare",
    "price",
    "vehicle",
    "product",
    "products",
]


def contains_keyword(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if contains_keyword(k):
                return True
            if contains_keyword(v):
                return True

    elif isinstance(obj, list):
        for item in obj:
            if contains_keyword(item):
                return True

    elif isinstance(obj, str):
        text = obj.lower()

        for keyword in KEYWORDS:
            if keyword.lower() in text:
                return True

    return False


def main():

    files = sorted(
        glob.glob("debug_graphql_*.json")
    )

    print(f"Found {len(files)} GraphQL files.\n")

    for filename in files:

        try:

            with open(
                filename,
                encoding="utf-8",
            ) as f:

                data = json.load(f)

            if contains_keyword(data):

                print(filename)

        except Exception as e:

            print(filename, e)


if __name__ == "__main__":
    main()