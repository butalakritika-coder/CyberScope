import streamlit as st
from collections import Counter
from src.data_loader import load_incidents
from src.search import search_incidents
from src.evidence import (
    get_finding_sources,
    analyze_evidence_quality,
    format_evidence_report,
    get_incident_techniques,
    compare_incident_techniques,
    format_technique_comparison,
)


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="CyberScope | Threat Intelligence",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #101722;
    color: #E6EDF5;
}

.block-container {
    padding-top: 4.5rem !important;
    padding-bottom: 2rem;
}

/* TOP HEADER */

[data-testid="stHeader"] {
    background-color: #101722 !important;
}

[data-testid="stToolbar"] {
    background-color: transparent !important;
}

[data-testid="stDecoration"] {
    background-color: #101722 !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #141E2B !important;
    border-right: 1px solid #293B50;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
section[data-testid="stSidebar"] label {
    color: #E2EAF3 !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #DCE6F1 !important;
    font-size: 14px !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #A5B4C5 !important;
}

/* BRANDING */

.brand {
    font-size: 27px;
    font-weight: 700;
    letter-spacing: -1px;
    color: #F1F5F9;
    margin-bottom: 3px;
}

.brand span {
    color: #63B3ED;
}

.subtitle {
    color: #A5B4C5;
    font-size: 11px;
    letter-spacing: 1.2px;
    margin-bottom: 35px;
}

/* MAIN HEADINGS */

.top-label {
    color: #63B3ED;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
}

.main-heading {
    font-size: 32px;
    font-weight: 700;
    color: #F1F5F9;
    margin-top: 10px;
    letter-spacing: -0.8px;
}

.description {
    color: #A5B4C5;
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 25px;
}

/* STATUS BADGE */

.status {
    display: inline-block;
    background-color: #17352F;
    color: #75DDBA;
    border: 1px solid #28604F;
    border-radius: 20px;
    padding: 7px 13px;
    font-size: 11px;
    font-weight: 600;
}

/* WORKSPACE CARDS */

.section-card {
    background-color: #192738;
    border: 1px solid #304258;
    border-radius: 12px;
    padding: 25px;
    min-height: 145px;
    margin-bottom: 15px;
    transition: border-color 0.2s ease;
}

.section-card:hover {
    border-color: #6395C2;
}

.card-title {
    color: #E6EDF5;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
}

.card-description {
    color: #B0BDCC;
    font-size: 13px;
    line-height: 1.8;
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background-color: #192738 !important;
    border: 1px solid #304258 !important;
    border-radius: 10px;
    padding: 18px;
}

div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetric"] p {
    color: #C5D4E3 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
    color: #F1F5F9 !important;
    opacity: 1 !important;
    font-size: 32px !important;
    font-weight: 700 !important;
}

/* INCIDENT DETAILS */

.detail-label {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 5px;
}

.detail-value {
    color: #F1F5F9;
    font-size: 15px;
    font-weight: 500;
    line-height: 1.7;
    margin-bottom: 16px;
}

.label-blue {
    color: #75B9F2;
}

.label-purple {
    color: #B8A5F5;
}

.label-teal {
    color: #72D6C2;
}

.label-cyan {
    color: #73C9DF;
}

.label-lavender {
    color: #C2B5F5;
}

.detail-section {
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: 600;
}

/* EVIDENCE STATUS BADGES */

.evidence-badge {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 5px;
}

.status-supported {
    background-color: #173B32;
    color: #75DDBA;
    border: 1px solid #28604F;
}

.status-unverified {
    background-color: #3A321E;
    color: #F0C66B;
    border: 1px solid #74602D;
}

.status-disputed {
    background-color: #40252B;
    color: #F28C9B;
    border: 1px solid #75404A;
}

.status-insufficient {
    background-color: #303746;
    color: #B9C2D0;
    border: 1px solid #4C586B;
}

/* EXPANDABLE CARDS */

div[data-testid="stExpander"] details {
    background-color: #192738 !important;
    border: 1px solid #304258 !important;
    border-radius: 10px;
}

div[data-testid="stExpander"] summary {
    background-color: #192738 !important;
    color: #E6EDF5 !important;
}

div[data-testid="stExpander"] summary p {
    color: #E6EDF5 !important;
    font-weight: 600;
}

div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background-color: #141E2B !important;
}

/* INPUT FIELDS */

.stTextInput input,
.stMultiSelect div[data-baseweb="select"] {
    background-color: #192738 !important;
    color: #E6EDF5 !important;
    border-color: #304258 !important;
}

.stTextInput label,
.stMultiSelect label {
    color: #DCE6F1 !important;
}

/* DIVIDERS */

hr {
    border-color: #293B50 !important;
}

/* BUTTONS */

.stButton button {
    background-color: #244D70;
    color: #FFFFFF;
    border: 1px solid #35658D;
    border-radius: 8px;
}

.stButton button:hover {
    background-color: #30658F;
    border-color: #63B3ED;
    color: #FFFFFF;
}

/* DOWNLOAD AND LINK BUTTONS */

[data-testid="stDownloadButton"] button,
[data-testid="stLinkButton"] a {
    background-color: #244D70 !important;
    color: #F1F5F9 !important;
    border: 1px solid #35658D !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
    text-decoration: none !important;
}

[data-testid="stDownloadButton"] button:hover,
[data-testid="stLinkButton"] a:hover {
    background-color: #30658F !important;
    border-color: #63B3ED !important;
    color: #FFFFFF !important;
}

[data-testid="stDownloadButton"] button p,
[data-testid="stLinkButton"] a p {
    color: #F1F5F9 !important;
    opacity: 1 !important;
}

/* EVIDENCE REPORT */

[data-testid="stCode"] {
    background-color: #141E2B !important;
    border: 1px solid #304258 !important;
    border-radius: 10px !important;
}

[data-testid="stCode"] pre {
    background-color: #141E2B !important;
    padding: 22px !important;
}

[data-testid="stCode"] code {
    color: #E6EDF5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    line-height: 2 !important;
    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
}

/* FOOTER */

.footer {
    color: #91A0B3;
    font-size: 12px;
    border-top: 1px solid #293B50;
    padding-top: 18px;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)


# ============================================
# HELPER FUNCTION: EVIDENCE STATUS
# ============================================

def display_evidence_status(status):

    status_styles = {
        "supported": ("status-supported", "SUPPORTED"),
        "unverified": ("status-unverified", "UNVERIFIED"),
        "disputed": ("status-disputed", "DISPUTED"),
        "insufficient_evidence": (
            "status-insufficient",
            "INSUFFICIENT EVIDENCE"
        )
    }

    css_class, label = status_styles.get(
        status,
        ("status-insufficient", "UNKNOWN")
    )

    st.markdown(
        f'<span class="evidence-badge {css_class}">{label}</span>',
        unsafe_allow_html=True
    )


# ============================================
# SIDEBAR NAVIGATION
# ============================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Cyber<span>Scope</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">THREAT INTELLIGENCE PLATFORM</div>',
        unsafe_allow_html=True
    )

    st.markdown("### WORKSPACE")

    page = st.radio(
    "Navigation",
        [
        "Overview",
        "Incident Explorer",
        "Finding Analysis",
        "Evidence Analysis",
        "Global Evidence Analytics",
        "Incident Trends & Insights",
        "MITRE ATT&CK Technique Explorer",
        "Incident Comparison",
        "Source & Reference Explorer"
    ],
    label_visibility="collapsed"
)

    st.divider()

    st.markdown("### PLATFORM")

    st.caption("Evidence-driven cyber threat research")
    st.caption("Version 1.0 | Development")


# ============================================
# MAIN HEADER
# ============================================

st.markdown(
    '<div class="top-label">CYBER THREAT INTELLIGENCE</div>',
    unsafe_allow_html=True
)


# ============================================
# OVERVIEW
# ============================================

if page == "Overview":

    st.markdown(
        '<div class="main-heading">Security Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Explore cyber incidents, investigate findings, and evaluate
        the evidence behind security intelligence.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<span class="status">● SYSTEM INTERFACE ACTIVE</span>',
        unsafe_allow_html=True
    )

    st.write("")
    st.markdown("### Intelligence Workspace")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="section-card">
            <div class="card-title">⌕ Incident Explorer</div>
            <div class="card-description">
                Search and explore documented cyber incidents
                using keywords and incident information.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card">
            <div class="card-title">◈ Evidence Analysis</div>
            <div class="card-description">
                Examine supporting sources, publisher diversity,
                evidence coverage, and potential gaps.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="section-card">
            <div class="card-title">◎ Finding Analysis</div>
            <div class="card-description">
                Investigate incident findings and examine
                their associated techniques and sources.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card">
            <div class="card-title">▤ Intelligence Reports</div>
            <div class="card-description">
                Generate structured, readable evidence reports
                for cybersecurity research and analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        CyberScope © 2026 | Evidence-Driven Cyber Threat Research
    </div>
    """, unsafe_allow_html=True)


# ============================================
# INCIDENT EXPLORER
# ============================================

# ============================================
# INCIDENT EXPLORER
# ============================================

elif page == "Incident Explorer":

    st.markdown(
        '<div class="main-heading">Incident Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Search, filter and investigate documented cybersecurity incidents
        using incident categories, evidence status and MITRE ATT&CK techniques.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    # -------------------------------------------------
    # PREPARE FILTER OPTIONS
    # -------------------------------------------------

    categories = sorted({
        incident.get("category", "Unknown")
        for incident in incidents
    })

    evidence_statuses = sorted({
        finding.get("evidence_status", "unknown")
        for incident in incidents
        for finding in incident.get("findings", [])
    })

    technique_options = sorted({
        f"{technique.get('technique_id', 'Unknown')} - "
        f"{technique.get('name', 'Unknown')}"
        for incident in incidents
        for technique in incident.get("techniques", [])
    })

    # -------------------------------------------------
    # CLEAR FILTERS
    # -------------------------------------------------

    if st.button("Clear Filters", use_container_width=True):

        st.session_state["incident_query"] = ""
        st.session_state["incident_fields"] = [
            "name", "category", "summary", "techniques"
        ]
        st.session_state["incident_categories"] = []
        st.session_state["incident_statuses"] = []
        st.session_state["incident_techniques"] = []

        st.rerun()

    # -------------------------------------------------
    # KEYWORD SEARCH
    # -------------------------------------------------

    st.markdown("### Search Intelligence Database")

    query = st.text_input(
        "Search incidents",
        placeholder="Try WannaCry, ransomware, malware...",
        key="incident_query"
    )

    selected_fields = st.multiselect(
        "Search within",
        options=["name", "category", "summary", "techniques"],
        default=["name", "category", "summary", "techniques"],
        key="incident_fields"
    )

    st.divider()

    # -------------------------------------------------
    # ADVANCED FILTERS
    # -------------------------------------------------

    st.markdown("### Advanced Filters")

    col1, col2 = st.columns(2)

    with col1:

        selected_categories = st.multiselect(
            "Filter by Category",
            options=categories,
            key="incident_categories",
            placeholder="Select incident categories"
        )

        selected_statuses = st.multiselect(
            "Filter by Evidence Status",
            options=evidence_statuses,
            key="incident_statuses",
            placeholder="Select evidence statuses"
        )

    with col2:

        selected_techniques = st.multiselect(
            "Filter by MITRE ATT&CK Technique",
            options=technique_options,
            key="incident_techniques",
            placeholder="Select techniques"
        )

    # -------------------------------------------------
    # APPLY FILTERS
    # -------------------------------------------------

    if not selected_fields:

        filtered_incidents = []
        st.warning("Please select at least one search field.")

    else:

        # First apply keyword search
        if query.strip():

            filtered_incidents = search_incidents(
                incidents,
                query,
                fields=selected_fields
            )

        else:

            filtered_incidents = incidents.copy()

        # Apply category filter
        if selected_categories:

            filtered_incidents = [
                incident
                for incident in filtered_incidents
                if incident.get("category") in selected_categories
            ]

        # Apply evidence status filter
        if selected_statuses:

            filtered_incidents = [
                incident
                for incident in filtered_incidents
                if any(
                    finding.get("evidence_status", "unknown")
                    in selected_statuses
                    for finding in incident.get("findings", [])
                )
            ]

        # Apply MITRE technique filter
        if selected_techniques:

            selected_technique_ids = {
                technique.split(" - ", 1)[0]
                for technique in selected_techniques
            }

            filtered_incidents = [
                incident
                for incident in filtered_incidents
                if any(
                    technique.get("technique_id")
                    in selected_technique_ids
                    for technique in incident.get("techniques", [])
                )
            ]

    # -------------------------------------------------
    # SEARCH RESULTS
    # -------------------------------------------------

    st.divider()

    st.markdown("### Search Results")

    st.caption(
        f"{len(filtered_incidents)} of {len(incidents)} "
        f"incident(s) found"
    )

    if not filtered_incidents:

        st.info(
            "No matching incidents found. Try changing or clearing "
            "your search and filters."
        )

    else:

        for incident in filtered_incidents:

            incident_id = incident.get("incident_id", "Unknown")
            name = incident.get("name", "Unnamed Incident")
            category = incident.get("category", "Unknown")
            summary = incident.get("summary", "")

            with st.expander(f"{name} | {incident_id}"):

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        '<div class="detail-label label-blue">'
                        'INCIDENT ID</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f'<div class="detail-value">{incident_id}</div>',
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        '<div class="detail-label label-purple">'
                        'CATEGORY</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f'<div class="detail-value">{category}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    '<div class="detail-label label-teal">'
                    'INCIDENT SUMMARY</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="detail-value">{summary}</div>',
                    unsafe_allow_html=True
                )

                st.divider()

                findings = incident.get("findings", [])
                techniques = incident.get("techniques", [])
                sources = incident.get("sources", [])

                col1, col2, col3 = st.columns(3)

                col1.metric("Findings", len(findings))
                col2.metric("Techniques", len(techniques))
                col3.metric("Sources", len(sources))

                # Associated techniques
                st.markdown(
                    '<div class="detail-section label-lavender">'
                    'ASSOCIATED TECHNIQUES</div>',
                    unsafe_allow_html=True
                )

                if techniques:

                    for technique in techniques:

                        technique_id = technique.get(
                            "technique_id", "N/A"
                        )

                        technique_name = technique.get(
                            "name", "Unknown"
                        )

                        st.markdown(
                            f'<div class="detail-value">'
                            f'<span style="color:#B8A5F5;">'
                            f'{technique_id}</span> '
                            f'— {technique_name}</div>',
                            unsafe_allow_html=True
                        )

                else:

                    st.caption("No techniques recorded.")

                # Incident findings
                st.markdown(
                    '<div class="detail-section label-blue">'
                    'INCIDENT FINDINGS</div>',
                    unsafe_allow_html=True
                )

                if findings:

                    for finding in findings:

                        claim = finding.get(
                            "claim", "No claim available"
                        )

                        evidence_status = finding.get(
                            "evidence_status", "unknown"
                        )

                        st.markdown(
                            f'<div class="detail-value">{claim}</div>',
                            unsafe_allow_html=True
                        )

                        display_evidence_status(evidence_status)
                        st.write("")

                else:

                    st.caption("No findings recorded.")

                # Supporting sources
                st.markdown(
                    '<div class="detail-section label-cyan">'
                    'SUPPORTING SOURCES</div>',
                    unsafe_allow_html=True
                )

                if sources:

                    for source in sources:

                        source_title = source.get(
                            "title", "Untitled source"
                        )

                        publisher = source.get(
                            "publisher", "Unknown publisher"
                        )

                        source_type = source.get(
                            "source_type", "Unknown"
                        )

                        st.markdown(
                            f'<div class="detail-value">'
                            f'{source_title}<br>'
                            f'<span style="color:#73C9DF;">'
                            f'{publisher}</span> '
                            f'<span style="color:#91A0B3;">'
                            f'· {source_type}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                else:

                    st.caption("No sources recorded.")
# ============================================
# FINDING ANALYSIS
# ============================================

elif page == "Finding Analysis":

    st.markdown(
        '<div class="main-heading">Finding Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Investigate individual incident findings, review their linked sources,
        and assess how well each finding is supported by available evidence.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    # Build incident choices.

    incident_options = {
        f"{incident.get('name', 'Unnamed Incident')} "
        f"({incident.get('incident_id', 'Unknown ID')})": incident
        for incident in incidents
        if isinstance(incident, dict)
    }

    if not incident_options:

        st.warning("No incidents are available for analysis.")

    else:

        st.markdown("### Select an Incident")

        selected_incident_label = st.selectbox(
            "Incident",
            options=list(incident_options.keys()),
            key="finding_analysis_incident"
        )

        selected_incident = incident_options[selected_incident_label]

        incident_id = selected_incident.get("incident_id", "")
        findings = selected_incident.get("findings", [])

        if not findings:

            st.info("No findings are recorded for this incident.")

        else:

            finding_options = {}

            for finding in findings:

                if not isinstance(finding, dict):
                    continue

                finding_id = finding.get("finding_id")

                if not isinstance(finding_id, str) or not finding_id:
                    continue

                claim = finding.get("claim", "No claim available")

                short_claim = (
                    claim if len(claim) <= 85 else claim[:82] + "..."
                )

                option_label = f"{short_claim} | {finding_id}"
                finding_options[option_label] = finding_id

            if not finding_options:

                st.warning("No valid findings with finding IDs were found.")

            else:

                st.markdown("### Select a Finding")

                selected_finding_label = st.selectbox(
                    "Finding",
                    options=list(finding_options.keys()),
                    key=f"finding_choice_{incident_id}"
                )

                finding_id = finding_options[selected_finding_label]

                result = get_finding_sources(
                    incidents,
                    incident_id,
                    finding_id
                )

                if result is None:

                    st.error("The selected finding could not be retrieved.")

                else:

                    finding = result["finding"]
                    quality = analyze_evidence_quality(result)
                    sources = result.get("sources", [])

                    st.divider()
                    st.markdown("### Finding Details")

                    detail_col1, detail_col2 = st.columns(2)

                    with detail_col1:

                        st.markdown(
                            '<div class="detail-label label-blue">'
                            'INCIDENT ID</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="detail-value">{incident_id}</div>',
                            unsafe_allow_html=True
                        )

                    with detail_col2:

                        st.markdown(
                            '<div class="detail-label label-purple">'
                            'FINDING ID</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="detail-value">{finding_id}</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(
                        '<div class="detail-label label-teal">'
                        'FINDING CLAIM</div>',
                        unsafe_allow_html=True
                    )

                    st.write(finding.get("claim", "No claim available"))

                    st.markdown(
                        '<div class="detail-label label-lavender">'
                        'EVIDENCE STATUS</div>',
                        unsafe_allow_html=True
                    )

                    display_evidence_status(
                        finding.get("evidence_status", "unknown")
                    )

                    st.divider()
                    st.markdown("### Evidence Quality")

                    metric_col1, metric_col2, metric_col3 = st.columns(3)

                    metric_col1.metric(
                        "Linked Sources",
                        quality["source_count"]
                    )

                    metric_col2.metric(
                        "Distinct Publishers",
                        quality["publisher_count"]
                    )

                    metric_col3.metric(
                        "Further Review",
                        "Required" if quality["needs_review"] else "Not flagged"
                    )

                    st.markdown(
                        '<div class="detail-label label-cyan">'
                        'EVIDENCE ASSESSMENT</div>',
                        unsafe_allow_html=True
                    )

                    st.write(quality["assessment"])

                    st.caption(
                        f"Evidence level: {quality['evidence_level']}"
                    )

                    st.divider()
                    st.markdown("### Linked Evidence Sources")

                    if not sources:

                        st.warning(
                            "No sources are linked to this finding. "
                            "Further evidence is needed before relying on it."
                        )

                    else:

                        for index, source in enumerate(sources, start=1):

                            with st.container(border=True):

                                st.markdown(
                                    f"**{index}. {source.get('title', 'Untitled source')}**"
                                )

                                st.markdown(
                                    f'<span style="color:#73C9DF;">'
                                    f'{source.get("publisher", "Unknown publisher")}'
                                    f'</span> '
                                    f'<span style="color:#91A0B3;">'
                                    f'· {source.get("source_type", "Unknown source type")}'
                                    f'</span>',
                                    unsafe_allow_html=True
                                )

                                source_url = source.get("url")

                                if (
                                    isinstance(source_url, str)
                                    and source_url.startswith(
                                        ("https://", "http://")
                                    )
                                ):

                                    st.link_button(
                                        "Open source",
                                        source_url,
                                        key=f"finding_source_{finding_id}_{index}"
                                    )

                                else:

                                    st.caption("Source URL not available.")

                    # ========================================
                    # FORMATTED EVIDENCE REPORT
                    # ========================================

                    st.divider()
                    st.markdown("### Evidence Report")

                    report = format_evidence_report(result)

                    # Remove decorative separator lines,
                    # while preserving blank lines and spacing.

                    report_lines = []

                    for line in report.splitlines():

                        stripped_line = line.strip()

                        if stripped_line and set(stripped_line) == {"="}:
                            continue

                        report_lines.append(line)

                    clean_report = "\n".join(report_lines).strip()

                    with st.expander(
                        "View formatted evidence report",
                        expanded=True
                    ):

                        st.code(
                            clean_report,
                            language=None,
                            wrap_lines=True
                        )

                    st.download_button(
                        label="Download Evidence Report",
                        data=clean_report,
                        file_name=f"{finding_id}_evidence_report.txt",
                        mime="text/plain",
                        key=f"download_report_{finding_id}"
                    )


# ============================================
# EVIDENCE ANALYSIS
# ============================================

# ============================================
# EVIDENCE ANALYSIS
# ============================================

elif page == "Evidence Analysis":

    st.markdown(
        '<div class="main-heading">Evidence Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Evaluate source coverage, publisher diversity, and evidence gaps
        across documented cybersecurity incidents.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    if not incidents:

        st.warning("No incident records are available.")

    else:

        st.markdown("### Select an Incident")

        incident_options = {
            f"{incident.get('name', 'Unnamed Incident')} "
            f"({incident.get('incident_id', 'Unknown')})": incident
            for incident in incidents
        }

        selected_label = st.selectbox(
            "Choose an incident",
            options=list(incident_options.keys()),
            key="evidence_analysis_incident"
        )

        selected_incident = incident_options[selected_label]

        findings = selected_incident.get("findings", [])
        incident_id = selected_incident.get("incident_id")

        st.divider()

        if not findings:

            st.info("No findings are recorded for this incident.")

        else:

            analysis_results = []

            for finding in findings:

                result = get_finding_sources(
                    incidents,
                    incident_id,
                    finding.get("finding_id")
                )

                if result is None:
                    continue

                quality = analyze_evidence_quality(result)

                analysis_results.append({
                    "finding": finding,
                    "result": result,
                    "quality": quality
                })

            total_findings = len(analysis_results)

            supported = sum(
                1 for item in analysis_results
                if item["finding"].get("evidence_status") == "supported"
            )

            unverified = sum(
                1 for item in analysis_results
                if item["finding"].get("evidence_status") == "unverified"
            )

            disputed = sum(
                1 for item in analysis_results
                if item["finding"].get("evidence_status") == "disputed"
            )

            review_required = sum(
                1 for item in analysis_results
                if item["quality"]["needs_review"]
            )

            st.markdown("### Evidence Overview")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Findings", total_findings)
            col2.metric("Supported", supported)
            col3.metric("Unverified", unverified)
            col4.metric("Review Required", review_required)

            st.divider()

            st.markdown("### Evidence Status Distribution")

            status_data = {
                "Supported": supported,
                "Unverified": unverified,
                "Disputed": disputed,
                "Insufficient Evidence": sum(
                    1 for item in analysis_results
                    if item["finding"].get("evidence_status")
                    == "insufficient_evidence"
                )
            }

            st.bar_chart(status_data)

            st.divider()

            st.markdown("### Finding-wise Evidence Coverage")

            table_data = []

            for item in analysis_results:

                finding = item["finding"]
                quality = item["quality"]

                table_data.append({
                    "Finding ID": finding.get("finding_id"),
                    "Evidence Status": finding.get(
                        "evidence_status", "unknown"
                    ).replace("_", " ").title(),
                    "Linked Sources": quality["source_count"],
                    "Distinct Publishers": quality["publisher_count"],
                    "Evidence Level": quality["evidence_level"],
                    "Review Required": (
                        "Yes" if quality["needs_review"] else "No"
                    )
                })

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.markdown("### Publisher Diversity")

            for item in analysis_results:

                finding = item["finding"]
                quality = item["quality"]

                with st.expander(
                    f"{finding.get('finding_id')} — "
                    f"{quality['publisher_count']} publisher(s)"
                ):

                    st.write(finding.get("claim", "No claim available"))

                    st.write(
                        f"**Assessment:** {quality['assessment']}"
                    )

                    publishers = sorted({
                        source.get("publisher", "Unknown")
                        for source in item["result"].get("sources", [])
                    })

                    if publishers:

                        st.write("**Associated publishers:**")

                        for publisher in publishers:
                            st.write(f"- {publisher}")

                    else:

                        st.warning("No publishers are linked to this finding.")

            st.divider()

            st.markdown("### Findings Requiring Further Review")

            flagged_findings = [
                item for item in analysis_results
                if item["quality"]["needs_review"]
            ]

            if flagged_findings:

                st.warning(
                    f"{len(flagged_findings)} finding(s) "
                    "require additional evidence review."
                )

                for item in flagged_findings:

                    finding = item["finding"]
                    quality = item["quality"]

                    with st.expander(
                        f"{finding.get('finding_id')} — Review Required"
                    ):

                        st.write(finding.get("claim", "No claim available"))

                        st.write(
                            f"**Evidence Status:** "
                            f"{finding.get('evidence_status', 'unknown')}"
                        )

                        st.write(
                            f"**Linked Sources:** "
                            f"{quality['source_count']}"
                        )

                        st.write(
                            f"**Assessment:** {quality['assessment']}"
                        )

            else:

                st.success(
                    "No findings have been flagged for further review "
                    "by the current evidence quality checks."
                )
    
# ============================================
# INCIDENT COMPARISON
# ============================================
    # =========================================================
    # GLOBAL EVIDENCE ANALYTICS
    # =========================================================

elif page == "Global Evidence Analytics":

        st.title("Global Evidence Analytics")

        st.markdown(
            "A platform-wide overview of evidence coverage, "
            "source diversity, and findings that may require review."
        )

        # Load all incidents
        incidents = load_incidents()

        # -----------------------------------------------------
        # COLLECT GLOBAL EVIDENCE DATA
        # -----------------------------------------------------

        total_incidents = len(incidents)

        total_findings = 0
        supported_findings = 0
        unverified_findings = 0
        disputed_findings = 0
        insufficient_findings = 0

        all_source_ids = set()
        all_publishers = set()

        review_findings = []
        incident_review_counts = []

        status_counts = {
            "Supported": 0,
            "Unverified": 0,
            "Disputed": 0,
            "Insufficient Evidence": 0
        }

        # Process every incident
        for incident in incidents:

            incident_findings = incident.get("findings", [])
            incident_sources = incident.get("sources", [])

            source_lookup = {
                source.get("source_id"): source
                for source in incident_sources
            }

            incident_review_count = 0

            for finding in incident_findings:

                total_findings += 1

                status = finding.get(
                    "evidence_status",
                    "unverified"
                )

                status = status.lower()

                source_ids = finding.get("source_ids", [])

                # Count evidence status
                if status == "supported":
                    supported_findings += 1
                    status_counts["Supported"] += 1

                elif status == "unverified":
                    unverified_findings += 1
                    status_counts["Unverified"] += 1

                elif status == "disputed":
                    disputed_findings += 1
                    status_counts["Disputed"] += 1

                elif status == "insufficient_evidence":
                    insufficient_findings += 1
                    status_counts["Insufficient Evidence"] += 1

                # Collect linked sources and publishers
                linked_publishers = set()

                for source_id in source_ids:

                    source = source_lookup.get(source_id)

                    if source:

                        all_source_ids.add(source_id)

                        publisher = source.get("publisher")

                        if publisher:
                            all_publishers.add(publisher)
                            linked_publishers.add(publisher)

                # Identify findings that need review
                needs_review = (
                    status in [
                        "unverified",
                        "disputed",
                        "insufficient_evidence"
                    ]
                    or len(source_ids) == 0
                )

                if needs_review:

                    incident_review_count += 1

                    review_findings.append({
                        "Incident": incident.get("name", "Unknown"),
                        "Finding ID": finding.get("finding_id", "N/A"),
                        "Claim": finding.get("claim", "N/A"),
                        "Evidence Status": status.replace(
                            "_", " "
                        ).title(),
                        "Linked Sources": len(source_ids),
                        "Distinct Publishers": len(linked_publishers)
                    })

            incident_review_counts.append({
                "Incident": incident.get("name", "Unknown"),
                "Findings Requiring Review": incident_review_count
            })

        # -----------------------------------------------------
        # GLOBAL METRICS
        # -----------------------------------------------------

        st.subheader("Platform-wide Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Incidents", total_incidents)
        col2.metric("Total Findings", total_findings)
        col3.metric("Linked Sources", len(all_source_ids))
        col4.metric("Unique Publishers", len(all_publishers))

        st.divider()

        # -----------------------------------------------------
        # EVIDENCE STATUS DISTRIBUTION
        # -----------------------------------------------------

        st.subheader("Evidence Status Distribution")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Supported", supported_findings)
        col2.metric("Unverified", unverified_findings)
        col3.metric("Disputed", disputed_findings)
        col4.metric("Insufficient Evidence", insufficient_findings)

        st.markdown("#### Findings by Evidence Status")

        st.bar_chart(status_counts)

        st.caption(
            "This chart represents the evidence status labels "
            "assigned to findings in the dataset."
        )

        st.divider()

        # -----------------------------------------------------
        # EVIDENCE GAPS
        # -----------------------------------------------------

        st.subheader("Evidence Gaps Across Incidents")

        st.markdown(
            "The following findings are flagged for review because "
            "they are unverified, disputed, have insufficient evidence, "
            "or have no linked sources."
        )

        if review_findings:

            st.metric(
                "Total Findings Requiring Review",
                len(review_findings)
            )

            st.dataframe(
                review_findings,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success("No findings currently require review.")

        st.divider()

        # -----------------------------------------------------
        # INCIDENT-WISE REVIEW SUMMARY
        # -----------------------------------------------------

        st.subheader("Incidents Requiring the Most Review")

        incident_review_counts.sort(
            key=lambda item: item["Findings Requiring Review"],
            reverse=True
        )

        st.dataframe(
            incident_review_counts,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # -----------------------------------------------------
        # PUBLISHER DIVERSITY
        # -----------------------------------------------------

        st.subheader("Source Publisher Overview")

        st.metric(
            "Total Unique Publishers",
            len(all_publishers)
        )

        if all_publishers:

            st.markdown("#### Publishers in the Dataset")

            for publisher in sorted(all_publishers):
                st.write(f"• {publisher}")

        else:

            st.info("No publishers found in the current dataset.")

        # -----------------------------------------------------
        # IMPORTANT NOTE
        # -----------------------------------------------------

        st.info(
            "Note: These analytics describe evidence coverage and "
            "dataset status labels. A higher source count or publisher "
            "count does not automatically establish that a finding "
            "is accurate. Findings should still be reviewed against "
            "their original sources."
        )
# =========================================================
# INCIDENT TRENDS & INSIGHTS
# =========================================================

elif page == "Incident Trends & Insights":

    st.markdown(
        '<div class="main-heading">Incident Trends & Insights</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Explore patterns across documented cyber incidents,
        examine frequently recorded attack techniques,
        and identify interesting trends in the dataset.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    if not incidents:

        st.warning("No incident records are available.")

    else:

        # -------------------------------------------------
        # COLLECT DATA
        # -------------------------------------------------

        category_counts = Counter()
        technique_counts = Counter()
        technique_incidents = {}

        findings_per_incident = []

        for incident in incidents:

            incident_name = incident.get("name", "Unknown")
            category = incident.get("category", "Unknown")

            findings = incident.get("findings", [])
            techniques = incident.get("techniques", [])

            # Count incident categories
            category_counts[category] += 1

            # Count findings per incident
            findings_per_incident.append({
                "Incident": incident_name,
                "Number of Findings": len(findings)
            })

            # Count MITRE techniques
            for technique in techniques:

                technique_id = technique.get(
                    "technique_id", "Unknown"
                )

                technique_name = technique.get(
                    "name", "Unknown"
                )

                technique_label = (
                    f"{technique_id} - {technique_name}"
                )

                technique_counts[technique_label] += 1

                if technique_label not in technique_incidents:
                    technique_incidents[technique_label] = set()

                technique_incidents[technique_label].add(
                    incident_name
                )

        # -------------------------------------------------
        # OVERVIEW METRICS
        # -------------------------------------------------

        total_incidents = len(incidents)

        total_findings = sum(
            len(incident.get("findings", []))
            for incident in incidents
        )

        total_techniques = sum(
            len(incident.get("techniques", []))
            for incident in incidents
        )

        unique_techniques = len(technique_counts)

        st.subheader("Dataset Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Incidents", total_incidents)
        col2.metric("Total Findings", total_findings)
        col3.metric("Technique Records", total_techniques)
        col4.metric("Unique Techniques", unique_techniques)

        st.divider()

        # -------------------------------------------------
        # INCIDENT CATEGORY DISTRIBUTION
        # -------------------------------------------------

        st.subheader("Incident Category Distribution")

        st.caption(
            "Distribution of documented incidents according "
            "to their recorded categories."
        )

        if category_counts:

            st.bar_chart(dict(category_counts))

        else:

            st.info("No incident categories are available.")

        st.divider()

        # -------------------------------------------------
        # FINDINGS PER INCIDENT
        # -------------------------------------------------

        st.subheader("Findings Across Incidents")

        st.caption(
            "Compare the number of recorded findings "
            "associated with each incident."
        )

        st.bar_chart(
            {
                item["Incident"]: item["Number of Findings"]
                for item in findings_per_incident
            }
        )

        st.dataframe(
            findings_per_incident,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # -------------------------------------------------
        # MITRE ATT&CK TECHNIQUE FREQUENCY
        # -------------------------------------------------

        st.subheader("MITRE ATT&CK Technique Frequency")

        st.caption(
            "Techniques are counted according to their recorded "
            "occurrences in the incident dataset."
        )

        if technique_counts:

            sorted_techniques = dict(
                sorted(
                    technique_counts.items(),
                    key=lambda item: item[1],
                    reverse=True
                )
            )

            st.bar_chart(sorted_techniques)

            technique_table = []

            for technique, count in sorted_techniques.items():

                technique_table.append({
                    "Technique": technique,
                    "Occurrences": count,
                    "Incidents Associated": len(
                        technique_incidents[technique]
                    )
                })

            st.dataframe(
                technique_table,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No MITRE ATT&CK techniques are recorded.")

        st.divider()

        # -------------------------------------------------
        # TECHNIQUE OVERLAP
        # -------------------------------------------------

        st.subheader("Techniques Shared Across Incidents")

        shared_techniques = {
            technique: names
            for technique, names in technique_incidents.items()
            if len(names) > 1
        }

        if shared_techniques:

            for technique, names in shared_techniques.items():

                with st.expander(technique):

                    st.write(
                        "**Recorded in the following incidents:**"
                    )

                    for name in sorted(names):
                        st.write(f"- {name}")

        else:

            st.info(
                "No techniques are currently shared across "
                "multiple incidents."
            )

        st.divider()

        # -------------------------------------------------
        # AUTOMATIC DATASET INSIGHTS
        # -------------------------------------------------

        st.subheader("Key Dataset Insights")

        # Most common category
        if category_counts:

            most_common_category = category_counts.most_common(1)[0]

            st.write(
                f"**1. Most represented incident category:** "
                f"{most_common_category[0]} "
                f"({most_common_category[1]} incident(s))."
            )

        # Incident with most findings
        if findings_per_incident:

            highest_findings = max(
                findings_per_incident,
                key=lambda item: item["Number of Findings"]
            )

            st.write(
                f"**2. Incident with the most findings:** "
                f"{highest_findings['Incident']} "
                f"({highest_findings['Number of Findings']} findings)."
            )

        # Most frequent technique
        if technique_counts:

            most_common_technique = technique_counts.most_common(1)[0]

            st.write(
                f"**3. Most frequently recorded technique:** "
                f"{most_common_technique[0]} "
                f"({most_common_technique[1]} occurrence(s))."
            )

        # Shared techniques
        st.write(
            f"**4. Techniques shared across incidents:** "
            f"{len(shared_techniques)}."
        )

        st.divider()

        st.info(
            "Note: These insights are generated from the records "
            "currently present in the CyberScope dataset. "
            "Technique frequency represents recorded mappings, "
            "not the prevalence of techniques across all real-world "
            "cyberattacks."
        )
# =========================================================
# MITRE ATT&CK TECHNIQUE EXPLORER
# =========================================================

elif page == "MITRE ATT&CK Technique Explorer":

    st.markdown(
        '<div class="main-heading">MITRE ATT&CK Technique Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Explore recorded MITRE ATT&CK techniques, identify associated
        incidents, and examine their supporting source references.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    # -----------------------------------------------------
    # COLLECT TECHNIQUES AND THEIR ASSOCIATED DATA
    # -----------------------------------------------------

    technique_library = {}

    for incident in incidents:

        incident_name = incident.get("name", "Unknown")
        incident_id = incident.get("incident_id", "Unknown")

        sources = incident.get("sources", [])

        source_lookup = {
            source.get("source_id"): source
            for source in sources
        }

        for technique in incident.get("techniques", []):

            technique_id = technique.get("technique_id", "Unknown")
            technique_name = technique.get("name", "Unknown")

            if technique_id not in technique_library:

                technique_library[technique_id] = {
                    "name": technique_name,
                    "incidents": [],
                    "sources": {}
                }

            entry = technique_library[technique_id]

            if incident_id not in [
                item["incident_id"] for item in entry["incidents"]
            ]:

                entry["incidents"].append({
                    "incident_id": incident_id,
                    "incident_name": incident_name
                })

            for source_id in technique.get("source_ids", []):

                source = source_lookup.get(source_id)

                if source:
                    entry["sources"][source_id] = source

    # -----------------------------------------------------
    # TECHNIQUE OVERVIEW
    # -----------------------------------------------------

    total_techniques = len(technique_library)

    total_associations = sum(
        len(item["incidents"])
        for item in technique_library.values()
    )

    total_sources = len({
        source_id
        for item in technique_library.values()
        for source_id in item["sources"]
    })

    st.subheader("Technique Library Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Unique Techniques", total_techniques)
    col2.metric("Incident Associations", total_associations)
    col3.metric("Linked Sources", total_sources)

    st.divider()

    # -----------------------------------------------------
    # SEARCH TECHNIQUES
    # -----------------------------------------------------

    st.subheader("Search Techniques")

    search_query = st.text_input(
        "Search by technique ID or name",
        placeholder="Try T1210 or Exploitation of Remote Services..."
    )

    filtered_techniques = {}

    for technique_id, details in technique_library.items():

        searchable_text = (
            technique_id + " " + details["name"]
        ).lower()

        if search_query.lower().strip() in searchable_text:

            filtered_techniques[technique_id] = details

    st.caption(
        f"{len(filtered_techniques)} technique(s) found"
    )

    st.divider()

    # -----------------------------------------------------
    # TECHNIQUE LIBRARY
    # -----------------------------------------------------

    st.subheader("Recorded MITRE ATT&CK Techniques")

    if not filtered_techniques:

        st.info("No matching techniques found.")

    else:

        for technique_id, details in sorted(
            filtered_techniques.items()
        ):

            with st.expander(
                f"{technique_id} — {details['name']}"
            ):

                # Technique details
                st.markdown("#### Technique Details")

                col1, col2 = st.columns(2)

                col1.metric("Technique ID", technique_id)

                col2.metric(
                    "Associated Incidents",
                    len(details["incidents"])
                )

                st.write(
                    f"**Technique Name:** {details['name']}"
                )

                st.divider()

                # Associated incidents
                st.markdown("#### Associated Incidents")

                if details["incidents"]:

                    for incident in details["incidents"]:

                        st.write(
                            f"• {incident['incident_name']} "
                            f"({incident['incident_id']})"
                        )

                else:

                    st.caption("No associated incidents found.")

                st.divider()

                # Supporting sources
                st.markdown("#### Supporting Source References")

                if details["sources"]:

                    for index, source in enumerate(
                        details["sources"].values(),
                        start=1
                    ):

                        st.markdown(
                            f"**{index}. {source.get('title', 'Untitled source')}**"
                        )

                        st.caption(
                            f"{source.get('publisher', 'Unknown publisher')} "
                            f"· {source.get('source_type', 'Unknown type')}"
                        )

                        source_url = source.get("url", "")

                        if source_url.startswith(("https://", "http://")):

                            st.link_button(
                                "Open Source",
                                source_url,
                                key=f"technique_source_{technique_id}_{index}"
                            )

                else:

                    st.info(
                        "No supporting source references are linked "
                        "to this technique."
                    )

                st.divider()

                st.caption(
                    "Technique associations are based on the "
                    "MITRE ATT&CK mappings recorded in CyberScope."
                )
elif page == "Incident Comparison":

    st.markdown(
        '<div class="main-heading">Incident Comparison</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Compare cybersecurity incidents based on their MITRE ATT&CK
        techniques and identify shared and unique attack techniques.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    # Select incidents that have recorded techniques.
    incident_options = {
        f"{incident.get('name', 'Unnamed Incident')} "
        f"({incident.get('incident_id', 'Unknown')})":
        incident.get("incident_id")
        for incident in incidents
        if incident.get("techniques")
    }

    if len(incident_options) < 2:
        st.info(
            "At least two incidents with recorded MITRE ATT&CK "
            "techniques are needed for comparison."
        )

    else:
        st.markdown("### Select Incidents")

        col1, col2 = st.columns(2)

        labels = list(incident_options.keys())

        with col1:
            first_incident = st.selectbox(
                "First Incident",
                labels,
                key="comparison_first"
            )

        with col2:
            second_options = [
                label for label in labels
                if label != first_incident
            ]

            second_incident = st.selectbox(
                "Second Incident",
                second_options,
                key="comparison_second"
            )

        st.write("")

        if st.button("Compare Incidents", use_container_width=True):

            first_id = incident_options[first_incident]
            second_id = incident_options[second_incident]

            result = compare_incident_techniques(
                incidents,
                first_id,
                second_id
            )

            if result is None:
                st.error("Unable to compare the selected incidents.")

            else:
                st.divider()

                st.markdown("### Comparison Results")

                common = result["common_techniques"]
                unique_first = result["unique_to_first"]
                unique_second = result["unique_to_second"]

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric("Common Techniques", len(common))
                metric2.metric("Unique to First", len(unique_first))
                metric3.metric("Unique to Second", len(unique_second))

                report = format_technique_comparison(
                    incidents,
                    first_id,
                    second_id
                )

                st.markdown("### Detailed Comparison")

                st.code(report, language=None)

                st.download_button(
                    "Download Comparison Report",
                    data=report,
                    file_name="incident_comparison_report.txt",
                    mime="text/plain"
                )
# ============================================
# SOURCE & REFERENCE EXPLORER
# ============================================

elif page == "Source & Reference Explorer":

    st.markdown(
        '<div class="main-heading">Source & Reference Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Explore the evidence library, search research sources,
        examine publisher information, and trace references
        back to their associated incidents and findings.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    # -------------------------------------------------
    # BUILD SOURCE LIBRARY
    # -------------------------------------------------

    source_library = []

    for incident in incidents:

        incident_id = incident.get("incident_id", "Unknown")
        incident_name = incident.get("name", "Unknown")

        findings = incident.get("findings", [])
        techniques = incident.get("techniques", [])

        for source in incident.get("sources", []):

            source_id = source.get("source_id", "Unknown")

            # Find findings linked to this source.
            linked_findings = [
                finding
                for finding in findings
                if source_id in finding.get("source_ids", [])
            ]

            # Find techniques linked to this source.
            linked_techniques = [
                technique
                for technique in techniques
                if source_id in technique.get("source_ids", [])
            ]

            source_library.append({
                "source_id": source_id,
                "title": source.get("title", "Untitled source"),
                "publisher": source.get("publisher", "Unknown publisher"),
                "source_type": source.get("source_type", "Unknown"),
                "url": source.get("url", ""),
                "date": source.get(
                    "date",
                    source.get("publication_date", "Not available")
                ),
                "incident_id": incident_id,
                "incident_name": incident_name,
                "findings": linked_findings,
                "techniques": linked_techniques
            })

    # -------------------------------------------------
    # SOURCE LIBRARY OVERVIEW
    # -------------------------------------------------

    st.subheader("Source Library Overview")

    total_sources = len(source_library)

    unique_publishers = len({
        source["publisher"]
        for source in source_library
    })

    unique_source_types = len({
        source["source_type"]
        for source in source_library
    })

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Sources", total_sources)
    col2.metric("Unique Publishers", unique_publishers)
    col3.metric("Source Types", unique_source_types)

    st.divider()

    # -------------------------------------------------
    # SEARCH AND FILTER SOURCES
    # -------------------------------------------------

    st.subheader("Search Evidence Sources")

    search_query = st.text_input(
        "Search sources",
        placeholder="Try Microsoft, CERT-In, WannaCry...",
        key="source_search_query"
    )

    source_types = sorted({
        source["source_type"]
        for source in source_library
    })

    selected_source_types = st.multiselect(
        "Filter by Source Type",
        options=source_types,
        key="source_type_filter",
        placeholder="Select source types"
    )

    # -------------------------------------------------
    # APPLY SEARCH AND FILTERS
    # -------------------------------------------------

    filtered_sources = []

    for source in source_library:

        searchable_text = " ".join([
            source["title"],
            source["publisher"],
            source["source_type"],
            source["source_id"],
            source["incident_name"]
        ]).lower()

        matches_search = (
            search_query.strip().lower() in searchable_text
        )

        matches_type = (
            not selected_source_types
            or source["source_type"] in selected_source_types
        )

        if matches_search and matches_type:
            filtered_sources.append(source)

    st.caption(
        f"{len(filtered_sources)} of {total_sources} source(s) found"
    )

    st.divider()

    # -------------------------------------------------
    # DISPLAY SOURCE LIBRARY
    # -------------------------------------------------

    st.subheader("Evidence Source Library")

    if not filtered_sources:

        st.info(
            "No matching sources found. "
            "Try changing your search or filters."
        )

    else:

        for index, source in enumerate(filtered_sources, start=1):

            with st.expander(
                f"{source['title']} | {source['source_id']}"
            ):

                st.markdown("#### Source Details")

                col1, col2 = st.columns(2)

                with col1:

                    st.write("**Source ID**")
                    st.write(source["source_id"])

                    st.write("**Publisher**")
                    st.write(source["publisher"])

                with col2:

                    st.write("**Source Type**")
                    st.write(source["source_type"])

                    st.write("**Publication Date**")
                    st.write(source["date"])

                st.divider()

                # Source URL
                st.markdown("#### Original Reference")

                source_url = source["url"]

                if (
                    isinstance(source_url, str)
                    and source_url.startswith(("https://", "http://"))
                ):

                    st.link_button(
                        "Open Original Source",
                        source_url,
                        key=f"source_library_link_{index}"
                    )

                else:

                    st.caption("Source URL is not available.")

                st.divider()

                # Associated incident
                st.markdown("#### Associated Incident")

                st.write(source["incident_name"])

                st.caption(
                    f"Incident ID: {source['incident_id']}"
                )

                st.divider()

                # Linked findings
                st.markdown("#### Linked Findings")

                if source["findings"]:

                    for finding in source["findings"]:

                        st.markdown(
                            f"**{finding.get('finding_id', 'Unknown')}**"
                        )

                        st.write(
                            finding.get("claim", "No claim available")
                        )

                        st.caption(
                            "Evidence Status: "
                            + finding.get(
                                "evidence_status", "unknown"
                            ).replace("_", " ").title()
                        )

                else:

                    st.caption(
                        "No findings are directly linked to this source."
                    )

                st.divider()

                # Linked MITRE techniques
                st.markdown("#### Linked MITRE ATT&CK Techniques")

                if source["techniques"]:

                    for technique in source["techniques"]:

                        st.write(
                            f"• {technique.get('technique_id', 'Unknown')} "
                            f"— {technique.get('name', 'Unknown')}"
                        )

                else:

                    st.caption(
                        "No MITRE ATT&CK techniques are linked to this source."
                    )

    st.divider()

    st.info(
        "Note: Source references show how evidence is connected "
        "to the incidents, findings, and techniques recorded "
        "in the current CyberScope dataset. A listed source "
        "does not automatically establish the accuracy of a claim."
    )