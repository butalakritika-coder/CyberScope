
def get_finding_sources(incidents, incident_id, finding_id):
    """Retrieve a finding and its linked source records."""

    for incident in incidents:
        if incident.get("incident_id") != incident_id:
            continue

        for finding in incident.get("findings", []):
            if finding.get("finding_id") == finding_id:
                source_ids = finding.get("source_ids", [])

                sources = [
                    source
                    for source in incident.get("sources", [])
                    if source.get("source_id") in source_ids
                ]

                return {
                    "finding": finding,
                    "sources": sources,
                }

        return None

    return None


def format_evidence_report(result):
    """Format a finding and its sources into a readable report."""

    if result is None:
        return "Finding or incident not found."

    finding = result["finding"]
    sources = result["sources"]

    lines = [
        "=" * 45,
        "          CYBERSCOPE EVIDENCE",
        "=" * 45,
        "",
        f"Finding ID: {finding['finding_id']}",
        "",
        "Finding:",
        finding["claim"],
        "",
        f"Evidence Status: {finding['evidence_status'].replace('_', ' ').title()}",
        "",
        "Associated Sources:",
    ]

    if not sources:
        lines.append("No associated sources found.")
    else:
        for index, source in enumerate(sources, start=1):
            lines.append(f"{index}. {source['title']}")
            lines.append(f"   Publisher: {source['publisher']}")
            lines.append(f"   URL: {source.get('url') or 'Not available'}")
            lines.append("")

    lines.append("=" * 45)

    return "\n".join(lines)

def main():
    """Run an interactive evidence lookup."""
    from src.data_loader import load_incidents

    try:
        incidents = load_incidents()
    except ValueError as error:
        print(f"ERROR: {error}")
        return

    print("\n=== CyberScope Evidence Lookup ===")
    incident_id = input("Enter incident ID: ").strip()
    finding_id = input("Enter finding ID: ").strip()

    result = get_finding_sources(
        incidents, incident_id, finding_id
    )

    print()
    print(format_evidence_report(result))


if __name__ == "__main__":
    main()
