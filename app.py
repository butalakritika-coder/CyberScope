import streamlit as st

from src.data_loader import load_incidents
from src.search import search_incidents
from src.evidence import (
    get_finding_sources,
    analyze_evidence_quality,
    format_evidence_report,
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
            "Evidence Analysis"
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

elif page == "Incident Explorer":

    st.markdown(
        '<div class="main-heading">Incident Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Search, investigate and explore documented cybersecurity incidents.
    </div>
    """, unsafe_allow_html=True)

    try:
        incidents = load_incidents()
    except ValueError as error:
        st.error(f"Unable to load incident data: {error}")
        st.stop()

    st.markdown("### Search Intelligence Database")

    query = st.text_input(
        "Search incidents",
        placeholder="Try WannaCry, ransomware, malware..."
    )

    selected_fields = st.multiselect(
        "Search within",
        options=["name", "category", "summary", "techniques"],
        default=["name", "category", "summary", "techniques"]
    )

    if not selected_fields:
        results = []
        st.warning("Please select at least one search field.")

    elif query.strip():
        results = search_incidents(
            incidents,
            query,
            fields=selected_fields
        )

    else:
        results = incidents

    st.divider()

    st.markdown("### Search Results")
    st.caption(f"{len(results)} incident(s) found")

    if not results:

        st.info("No matching incidents found. Try another keyword.")

    else:

        for incident in results:

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

elif page == "Evidence Analysis":

    st.markdown(
        '<div class="main-heading">Evidence Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="description">
        Evaluate source coverage, publisher diversity, and evidence gaps.
    </div>
    """, unsafe_allow_html=True)

    st.info("Evidence analysis workspace is under development.")