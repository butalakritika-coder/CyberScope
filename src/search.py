
def search_incidents(incidents, query, fields=None):
    """Search incidents using a case-insensitive keyword."""

    if not isinstance(query, str) or not query.strip():
        return []

    query = query.strip().casefold()

    if fields is None:
        searchable_fields = ["name", "category", "summary", "techniques"]
    else:
        searchable_fields = fields

    allowed_fields = {"name", "category", "summary", "techniques"}

    if not isinstance(searchable_fields, (list, tuple)):
        raise ValueError("Fields must be provided as a list or tuple.")

    if any(field not in allowed_fields for field in searchable_fields):
        raise ValueError("Unsupported search field provided.")

    results = []

    for incident in incidents:
        if not isinstance(incident, dict):
            continue

        for field in searchable_fields:
            value = incident.get(field, "")

            if field == "techniques":
                if isinstance(value, list):
                    searchable_text = " ".join(
                        f"{technique.get('technique_id', '')} "
                        f"{technique.get('name', '')}"
                        for technique in value
                        if isinstance(technique, dict)
                    )
                else:
                    searchable_text = ""
            else:
                searchable_text = value if isinstance(value, str) else ""

            if query in searchable_text.casefold():
                results.append(incident)
                break

    return results


def main():
    """Run an interactive incident search."""
    from src.data_loader import load_incidents

    try:
        incidents = load_incidents()
    except ValueError as error:
        print(f"ERROR: {error}")
        return

    query = input("Search CyberScope incidents: ").strip()
    results = search_incidents(incidents, query)

    if not results:
        print("No matching incidents found.")
        return

    print(f"\nFound {len(results)} matching incident(s):\n")

    for incident in results:
        print(f"ID: {incident.get('incident_id', 'Unknown')}")
        print(f"Name: {incident.get('name', 'Unknown')}")
        print(f"Category: {incident.get('category', 'Unknown')}")
        print(f"Summary: {incident.get('summary', '')}")
        print("-" * 40)


if __name__ == "__main__":
    main()
