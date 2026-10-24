
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

