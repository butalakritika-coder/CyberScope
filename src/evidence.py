
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
                    "incident": incident,
                    "finding": finding,
                    "sources": sources,
                }

        return None

    return None

def analyze_evidence_quality(result):
    """Summarize the source coverage for a finding."""

    if result is None:
        return None

    sources = result.get("sources", [])

    publishers = {
        source.get("publisher", "").strip().casefold()
        for source in sources
        if source.get("publisher", "").strip()
    }

    source_count = len(sources)
    publisher_count = len(publishers)

    if source_count == 0:
        assessment = "No linked sources available"
    elif source_count == 1:
        assessment = "Limited source coverage: only one source linked"
    elif publisher_count == 1:
        assessment = "Multiple sources linked, but only one publisher represented"
    else:
        assessment = "Multiple sources and publishers represented"

    return {
        "source_count": source_count,
        "publisher_count": publisher_count,
        "assessment": assessment,
    }
def format_evidence_report(result):
    """Format a finding and its sources into a readable report."""

    if result is None:
        return "Finding or incident not found."

    incident = result.get("incident", {})
    finding = result["finding"]
    sources = result["sources"]
    quality = analyze_evidence_quality(result)

    lines = [
        "=" * 50,
        "          CYBERSCOPE EVIDENCE REPORT",
        "=" * 50,
        "",
        f"Incident: {incident.get('name', 'Not available')}",
        f"Incident ID: {incident.get('incident_id', 'Not available')}",
        f"Finding ID: {finding['finding_id']}",
        "",
        "Finding:",
        finding["claim"],
        "",
        f"Evidence Status: {finding['evidence_status'].replace('_', ' ').title()}",
        "",
        "Evidence Quality Analysis:",
        f"Linked Sources: {quality['source_count']}",
        f"Distinct Publishers: {quality['publisher_count']}",
        f"Assessment: {quality['assessment']}",
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

    lines.append("=" * 50)

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
