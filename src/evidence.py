
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
    """Summarize source coverage and identify evidence gaps."""

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
        evidence_level = "No Evidence Linked"
        needs_review = True

    elif source_count == 1:
        assessment = "Limited source coverage: only one source linked"
        evidence_level = "Limited"
        needs_review = True

    elif publisher_count == 1:
        assessment = (
            "Multiple sources linked, but only one publisher represented"
        )
        evidence_level = "Limited Publisher Diversity"
        needs_review = True

    else:
        assessment = "Multiple sources and publishers represented"
        evidence_level = "Multiple Publishers"
        needs_review = False

    return {
        "source_count": source_count,
        "publisher_count": publisher_count,
        "assessment": assessment,
        "evidence_level": evidence_level,
        "needs_review": needs_review,
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
        f"Evidence Level: {quality['evidence_level']}",
        f"Assessment: {quality['assessment']}",
        f"Further Review Needed: {'Yes' if quality['needs_review'] else 'No'}",
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


def get_incident_techniques(incidents, incident_id):
    """Retrieve MITRE ATT&CK techniques for a specific incident."""

    for incident in incidents:
        if incident.get("incident_id") == incident_id:
            return incident.get("techniques", [])

    return None


def compare_incident_techniques(incidents, incident_id_1, incident_id_2):
    """Compare MITRE ATT&CK techniques between two incidents."""

    techniques_1 = get_incident_techniques(incidents, incident_id_1)
    techniques_2 = get_incident_techniques(incidents, incident_id_2)

    if techniques_1 is None or techniques_2 is None:
        return None

    ids_1 = {technique["technique_id"] for technique in techniques_1}
    ids_2 = {technique["technique_id"] for technique in techniques_2}

    return {
        "common_techniques": ids_1 & ids_2,
        "unique_to_first": ids_1 - ids_2,
        "unique_to_second": ids_2 - ids_1
    }


def format_technique_comparison(incidents, incident_id_1, incident_id_2):
    """Format a readable comparison report for two incidents."""

    result = compare_incident_techniques(
        incidents, incident_id_1, incident_id_2
    )

    if result is None:
        return "One or both incidents not found."

    def get_technique_details(incident_id, technique_ids):
        techniques = get_incident_techniques(incidents, incident_id)

        return [
            f"{technique['technique_id']} - {technique['name']}"
            for technique in techniques
            if technique["technique_id"] in technique_ids
        ]

    lines = [
        "CYBERSCOPE INCIDENT TECHNIQUE COMPARISON",
        "",
        "Common Techniques:",
    ]

    common = get_technique_details(
        incident_id_1, result["common_techniques"]
    )

    lines.extend(common if common else ["None"])

    lines.extend(["", "Unique to First Incident:"])

    unique_first = get_technique_details(
        incident_id_1, result["unique_to_first"]
    )

    lines.extend(unique_first if unique_first else ["None"])

    lines.extend(["", "Unique to Second Incident:"])

    unique_second = get_technique_details(
        incident_id_2, result["unique_to_second"]
    )

    lines.extend(unique_second if unique_second else ["None"])

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