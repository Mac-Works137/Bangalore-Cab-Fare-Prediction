import glob
import json


def find_operation_name(obj):
    """
    Recursively search for an operationName field.
    """

    if isinstance(obj, dict):

        if "operationName" in obj:
            return obj["operationName"]

        if "operation_name" in obj:
            return obj["operation_name"]

        for value in obj.values():
            result = find_operation_name(value)
            if result is not None:
                return result

    elif isinstance(obj, list):

        for item in obj:
            result = find_operation_name(item)
            if result is not None:
                return result

    return None


def main():

    files = sorted(glob.glob("debug_graphql_*.json"))

    for filename in files:

        try:
            with open(filename, encoding="utf-8") as f:
                data = json.load(f)

            operation = find_operation_name(data)

            print(f"{filename:<30} {operation}")

        except Exception as e:
            print(filename, e)


if __name__ == "__main__":
    main()