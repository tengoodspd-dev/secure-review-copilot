from __future__ import annotations
import json
import streamlit as st
import matplotlib.pyplot as plt
from src.analyser import run_analysis, Severity
from src.report import generate_markdown

SAMPLE_JSON = """{
  "system_name": "demo-app-server",
  "mfa_enabled": false,
  "default_credentials": false,
  "open_ports": [22, 80, 443, 3389],
  "public_endpoint": true,
  "tls_enabled": true,
  "tls_version": "1.2",
  "storage_encrypted": false,
  "audit_log_enabled": true,
  "os_version": "Ubuntu 20.04"
}"""

SEVERITY_COLORS = {
    Severity.CRITICAL: "\U0001f534",
    Severity.HIGH:     "\U0001f7e0",
    Severity.MEDIUM:   "\U0001f7e1",
    Severity.LOW:      "\U0001f535",
    Severity.INFO:     "\u26aa",
}


def main() -> None:
    """Streamlit application entry point for SecureReview Copilot."""
    st.set_page_config(page_title="SecureReview Copilot", page_icon="\U0001f512", layout="wide")
    st.title("\U0001f512 SecureReview Copilot")
    st.caption("Paste a system configuration JSON to analyse its security posture.")

    col_input, col_help = st.columns([3, 1])
    with col_input:
        raw_json = st.text_area("System Configuration (JSON)", value=SAMPLE_JSON, height=220)
    with col_help:
        st.markdown("**Tips**")
        st.markdown("- Paste your config JSON on the left")
        st.markdown("- Or upload a `.json` file below")
        uploaded = st.file_uploader("Upload JSON", type=["json"])
        if uploaded:
            raw_json = uploaded.read().decode("utf-8")

    analyse_btn = st.button("\U0001f50d Analyse", type="primary")

    if analyse_btn:
        try:
            config = json.loads(raw_json)
            if not isinstance(config, dict):
                st.error("JSON must be an object (dict), not a list or scalar.")
                return
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
            return

        findings = run_analysis(config)
        st.session_state["findings"] = findings
        st.session_state["config"] = config
        st.session_state.pop("checklist", None)

    if "findings" not in st.session_state:
        return

    findings = st.session_state["findings"]
    config = st.session_state["config"]
    system_name = config.get("system_name", "Unknown System")

    st.divider()

    counts = {s: sum(1 for f in findings if f.severity == s) for s in Severity}
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("\U0001f534 Critical", counts[Severity.CRITICAL])
    c2.metric("\U0001f7e0 High",     counts[Severity.HIGH])
    c3.metric("\U0001f7e1 Medium",   counts[Severity.MEDIUM])
    c4.metric("\U0001f535 Low",      counts[Severity.LOW])
    c5.metric("\u26aa Info",         counts[Severity.INFO])

    if findings:
        labels = [s.value for s in Severity if counts[s] > 0]
        values = [counts[s] for s in Severity if counts[s] > 0]
        colors = ["#d62728", "#ff7f0e", "#f0e442", "#1f77b4", "#aec7e8"][:len(labels)]
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
        ax.set_title(f"Findings — {system_name}")
        col_chart, _ = st.columns([1, 2])
        with col_chart:
            st.pyplot(fig)
        plt.close(fig)

    st.subheader("\U0001f4cb Findings")
    if not findings:
        st.success("\u2705 No security issues detected.")
    else:
        for severity in Severity:
            group = [f for f in findings if f.severity == severity]
            if not group:
                continue
            icon = SEVERITY_COLORS[severity]
            with st.expander(
                f"{icon} {severity.value} ({len(group)})",
                expanded=severity in (Severity.CRITICAL, Severity.HIGH),
            ):
                for finding in group:
                    st.markdown(f"**{finding.control_id} — {finding.title}**")
                    st.markdown(f"_{finding.description}_")
                    st.markdown(f"\U0001f4a1 **Remediation:** {finding.remediation}")
                    st.divider()

    st.subheader("\u2705 Remediation Checklist")
    checklist_items = [f for f in findings if f.severity in (Severity.CRITICAL, Severity.HIGH)]
    if not checklist_items:
        st.info("No critical or high-severity items to remediate.")
    else:
        if "checklist" not in st.session_state:
            st.session_state["checklist"] = {f.control_id: False for f in checklist_items}

        checked = 0
        for f in checklist_items:
            key = f"check_{f.control_id}"
            val = st.checkbox(
                f"{SEVERITY_COLORS[f.severity]} **[{f.severity.value}]** {f.control_id} — {f.title}",
                value=st.session_state["checklist"].get(f.control_id, False),
                key=key,
            )
            st.session_state["checklist"][f.control_id] = val
            if val:
                checked += 1

        progress = checked / len(checklist_items)
        st.progress(progress, text=f"Remediation progress: {checked}/{len(checklist_items)}")

    st.subheader("\U0001f4e5 Export Report")
    meta = {"system_name": system_name}
    md_content = generate_markdown(findings, meta)
    st.download_button(
        label="\u2b07\ufe0f Download Markdown Report",
        data=md_content.encode("utf-8"),
        file_name=f"security_report_{system_name}.md",
        mime="text/markdown",
    )


if __name__ == "__main__":
    main()
