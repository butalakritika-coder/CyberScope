
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "incidents.json"


def load_incidents(file_path=DEFAULT_DATA_FILE):
    """Load incident records from a JSON file."""
    file_path = Path(file_path)

    try:
        with file_path.open("r", encoding="utf-8") as file:
            incidents = json.load(file)
    except FileNotFoundError as error:
        raise ValueError(f"Data file not found: {file_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {file_path}, line {error.lineno}: {error.msg}"
        ) from error

    if not isinstance(incidents, list):
        raise ValueError("The JSON root must be a list of incidents.")

    return incidents


def validate_incidents(incidents):
    """Validate incident records and their finding-source relationships."""
    errors = []

    if not isinstance(incidents, list):
        return ["The incident data must be a list."]

    incident_ids = set()
    finding_ids = set()

    for incident_index, incident in enumerate(incidents):
        location = f"Incident at index {incident_index}"

        if not isinstance(incident, dict):
            errors.append(f"{location} must be an object.")
            continue

        # Check required incident fields.
        required_fields = (
            "incident_id",
            "name",
            "category",
            "summary",
            "findings",
            "techniques",
            "sources",
        )

        for field in required_fields:
            if field not in incident:
                errors.append(f"{location} is missing '{field}'.")

        incident_id = incident.get("incident_id")

        if not isinstance(incident_id, str) or not incident_id.strip():
            errors.append(f"{location} has an invalid incident_id.")
        elif incident_id in incident_ids:
            errors.append(f"Duplicate incident_id: {incident_id}")
        else:
            incident_ids.add(incident_id)

        for field in ("name", "category", "summary"):
            if field in incident:
                value = incident[field]
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"{location} has an invalid '{field}'."
                    )

        findings = incident.get("findings")
        sources = incident.get("sources")
        techniques = incident.get("techniques")

        if not isinstance(findings, list):
            errors.append(f"{location}: 'findings' must be a list.")
            findings = []

        if not isinstance(sources, list):
            errors.append(f"{location}: 'sources' must be a list.")
            sources = []

        if not isinstance(techniques, list):
            errors.append(f"{location}: 'techniques' must be a list.")
            techniques = []

        # Validate source records and collect their IDs.
        source_ids = set()

        for source_index, source in enumerate(sources):
            source_location = (
                f"{location}, source at index {source_index}"
            )

            if not isinstance(source, dict):
                errors.append(f"{source_location} must be an object.")
                continue

            source_id = source.get("source_id")

            if not isinstance(source_id, str) or not source_id.strip():
                errors.append(f"{source_location} has an invalid source_id.")
            elif source_id in source_ids:
                errors.append(f"{location} has duplicate source_id: {source_id}")
            else:
                source_ids.add(source_id)

            for field in ("title", "publisher", "source_type"):
                value = source.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"{source_location} has an invalid '{field}'."
                    )

        # Validate findings and their source references.
        for finding_index, finding in enumerate(findings):
            finding_location = (
                f"{location}, finding at index {finding_index}"
            )

            if not isinstance(finding, dict):
                errors.append(f"{finding_location} must be an object.")
                continue

            finding_id = finding.get("finding_id")

            if not isinstance(finding_id, str) or not finding_id.strip():
                errors.append(
                    f"{finding_location} has an invalid finding_id."
                )
            elif finding_id in finding_ids:
                errors.append(f"Duplicate finding_id: {finding_id}")
            else:
                finding_ids.add(finding_id)

            claim = finding.get("claim")
            if not isinstance(claim, str) or not claim.strip():
                errors.append(f"{finding_location} has an invalid claim.")

            evidence_status = finding.get("evidence_status")
            allowed_statuses = {
                "unverified",
                "supported",
                "disputed",
                "insufficient_evidence",
            }

            if evidence_status not in allowed_statuses:
                errors.append(
                    f"{finding_location} has an invalid evidence_status."
                )

            referenced_sources = finding.get("source_ids")

            if not isinstance(referenced_sources, list):
                errors.append(
                    f"{finding_location}: 'source_ids' must be a list."
                )
                continue

            for source_id in referenced_sources:
                if source_id not in source_ids:
                    errors.append(
                        f"{finding_location} references unknown source: "
                        f"{source_id}"
                    )

        # Technique mapping is intentionally basic at this stage.
        for technique_index, technique in enumerate(techniques):
            if not isinstance(technique, dict):
                errors.append(
                    f"{location}, technique at index {technique_index} "
                    "must be an object."
                )
                continue

            technique_id = technique.get("technique_id")
            if not isinstance(technique_id, str) or not technique_id.strip():
                errors.append(
                    f"{location}, technique at index {technique_index} "
                    "has an invalid technique_id."
                )

    return errors


def main():
    """Load the dataset, validate it, and display a summary."""
    try:
        incidents = load_incidents()
    except ValueError as error:
        print(f"ERROR: {error}")
        return

    errors = validate_incidents(incidents)

    if errors:
        print("CyberScope data validation failed:")
        for error in errors:
            print(f"- {error}")
        return

    finding_count = sum(
        len(incident["findings"])
        for incident in incidents
    )

    print("CyberScope data validation successful!")
    print(f"Incidents loaded: {len(incidents)}")
    print(f"Findings loaded: {finding_count}")


if __name__ == "__main__":
    main()