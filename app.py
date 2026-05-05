import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from engine.loader import load_file, detect_columns
from engine.detector import detect_anomalies
from engine.correlator import build_correlation_summary
from engine.narrator import generate_full_report
from utils.helpers import (
    format_number, format_percentage, format_delta,
    get_severity_color, get_severity_badge_html, get_severity_card_class,
    get_confidence_badge_html, summarize_quality_report,
    summarize_anomaly_counts, get_most_affected_column,
    group_anomalies_by_severity, build_anomaly_timeline,
    build_chart_annotations, get_overall_health_status,
    summarize_report_status
)
from utils.theme import inject_theme


st.set_page_config(
    page_title="TRACE — AI Root Cause Analyzer",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_theme()


def render_plotly_dark(fig):
    fig.update_layout(
        paper_bgcolor="#0A0A0A",
        plot_bgcolor="#0A0A0A",
        font=dict(family="JetBrains Mono", color="#E8E8E8", size=11),
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(
            gridcolor="#1E1E1E",
            linecolor="#1E1E1E",
            tickcolor="#444444",
            tickfont=dict(color="#666666", size=10)
        ),
        yaxis=dict(
            gridcolor="#1E1E1E",
            linecolor="#1E1E1E",
            tickcolor="#444444",
            tickfont=dict(color="#666666", size=10)
        ),
        legend=dict(
            bgcolor="#111111",
            bordercolor="#1E1E1E",
            borderwidth=1,
            font=dict(color="#E8E8E8", size=10)
        )
    )
    return fig


def render_header():
    st.markdown("""
        <div style="padding: 2rem 0 1.5rem 0; border-bottom: 1px solid #1E1E1E; margin-bottom: 2rem;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:4px; color:#444444; margin-bottom:8px;">
                DIAGNOSTIC INTELLIGENCE SYSTEM
            </div>
            <div style="display:flex; align-items:baseline; gap:16px;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:36px; font-weight:700; color:#E8E8E8; letter-spacing:-1px;">
                    TRACE
                </span>
                <span style="font-family:'Inter',sans-serif; font-size:14px; color:#444444; font-weight:400;">
                    Trend Recognition and Automated Cause Explanation
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_upload_section():
    st.markdown('<div class="trace-section-title">01 — DATA INPUT</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Upload your business data",
        type=["csv", "xlsx", "xls"],
        help="Supports CSV and Excel files. Any business domain — sales, HR, logistics, finance."
    )
    return uploaded_file


def render_quality_report(quality_report):
    summary = summarize_quality_report(quality_report)
    if not summary:
        st.markdown("""
            <div class="trace-card" style="border-color:#00CC44;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#00CC44; letter-spacing:1px;">
                    DATA QUALITY — NO ISSUES DETECTED
                </span>
            </div>
        """, unsafe_allow_html=True)
        return
    with st.expander("DATA QUALITY REPORT — CLICK TO EXPAND", expanded=False):
        for item in summary:
            parts = item.split(" — ", 1)
            label = parts[0] if len(parts) > 1 else "NOTE"
            content = parts[1] if len(parts) > 1 else item
            label_color = (
                "#FF0000" if label in ("WARNING",) else
                "#FF6600" if label in ("FLAGGED", "REVIEW") else
                "#00CC44" if label in ("REMOVED", "FIXED", "CLEANED", "CONVERTED", "STANDARDIZED") else
                "#E8E8E8"
            )
            st.markdown(f"""
                <div style="padding:6px 0; border-bottom:1px solid #1E1E1E;">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:10px;
                        font-weight:700; color:{label_color}; letter-spacing:1.5px;">
                        {label}
                    </span>
                    <span style="font-family:'Inter',sans-serif; font-size:13px; color:#888888; margin-left:12px;">
                        {content}
                    </span>
                </div>
            """, unsafe_allow_html=True)


def render_kpi_cards(anomaly_counts, most_affected_col, most_affected_info, df_shape):
    health_label, health_color = get_overall_health_status(anomaly_counts)
    st.markdown('<div class="trace-section-title">02 — SYSTEM STATUS</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="trace-card">
                <div class="trace-label">System Health</div>
                <div class="trace-value" style="color:{health_color}; font-size:20px;
                    {'animation:pulse-red 1.2s infinite; text-shadow:0 0 8px #FF000088;' if health_label == 'CRITICAL' else ''}">
                    {health_label}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        count = anomaly_counts.get("Critical", 0)
        st.markdown(f"""
            <div class="trace-card" style="{'border-color:#FF0000; background:#110000;' if count > 0 else ''}">
                <div class="trace-label">Critical</div>
                <div class="trace-value" style="color:{'#FF0000' if count > 0 else '#444444'};
                    {'animation:pulse-red 1.2s infinite;' if count > 0 else ''}">
                    {count}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        count = anomaly_counts.get("High", 0)
        st.markdown(f"""
            <div class="trace-card" style="{'border-color:#FF6600;' if count > 0 else ''}">
                <div class="trace-label">High</div>
                <div class="trace-value" style="color:{'#FF6600' if count > 0 else '#444444'};">
                    {count}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        count = anomaly_counts.get("Medium", 0)
        st.markdown(f"""
            <div class="trace-card" style="{'border-color:#FFD700;' if count > 0 else ''}">
                <div class="trace-label">Medium</div>
                <div class="trace-value" style="color:{'#FFD700' if count > 0 else '#444444'};">
                    {count}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class="trace-card">
                <div class="trace-label">Rows Analyzed</div>
                <div class="trace-value">{format_number(df_shape[0])}</div>
                <div class="trace-subvalue">{df_shape[1]} columns</div>
            </div>
        """, unsafe_allow_html=True)

    if most_affected_col:
        critical = most_affected_info.get("critical_count", 0)
        high = most_affected_info.get("high_count", 0)
        direction = most_affected_info.get("trend_direction", "unknown")
        st.markdown(f"""
            <div class="trace-card" style="margin-top:0.5rem; border-color:#333333;">
                <span class="trace-label">Most Affected Column — </span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:13px;
                    font-weight:700; color:#E8E8E8; letter-spacing:1px;">
                    {most_affected_col.upper()}
                </span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:11px;
                    color:#666666; margin-left:16px;">
                    {critical} critical · {high} high · trend {direction}
                </span>
            </div>
        """, unsafe_allow_html=True)


def render_anomaly_chart(df, col, anomalies_df, column_info, level_shift_anomalies):
    time_col = column_info.get("time_col")
    if col not in df.columns:
        return
    fig = go.Figure()
    if time_col and time_col in df.columns:
        x_values = df[time_col].astype(str)
    else:
        x_values = list(range(len(df)))
    fig.add_trace(go.Scatter(
        x=x_values,
        y=df[col],
        mode="lines",
        name=col.replace("_", " ").title(),
        line=dict(color="#333333", width=1.5),
        hovertemplate="%{y:.2f}<extra></extra>"
    ))
    col_anomalies = anomalies_df[
        (anomalies_df["column"] == col) &
        (anomalies_df["suppressed"] == False)
    ]
    for severity, color in [("Critical", "#FF0000"), ("High", "#FF6600"), ("Medium", "#FFD700")]:
        sev_data = col_anomalies[col_anomalies["severity"] == severity]
        if sev_data.empty:
            continue
        if time_col and time_col in df.columns:
            x_pts = [str(df.loc[i, time_col]) if i in df.index else "" for i in sev_data["row_index"]]
        else:
            x_pts = sev_data["row_index"].tolist()
        fig.add_trace(go.Scatter(
            x=x_pts,
            y=sev_data["value"].tolist(),
            mode="markers",
            name=severity,
            marker=dict(
                color=color,
                size=10 if severity == "Critical" else 8,
                symbol="circle",
                line=dict(color=color, width=2)
            ),
            hovertemplate=f"<b>{severity}</b><br>Value: %{{y:.2f}}<extra></extra>"
        ))
    col_shifts = [s for s in level_shift_anomalies if s.get("column") == col]
    if col_shifts:
        shift = col_shifts[0]
        split_idx = shift.get("split_index")
        if split_idx is not None and split_idx in df.index:
            x_shift = str(df.loc[split_idx, time_col]) if time_col and time_col in df.columns else split_idx
            fig.add_vline(
                x=x_shift,
                line_dash="dash",
                line_color="#C0C0C0",
                line_width=1,
                annotation_text="LEVEL SHIFT",
                annotation_font=dict(color="#C0C0C0", size=9, family="JetBrains Mono"),
                annotation_position="top right"
            )
    fig.update_layout(
        title=dict(
            text=col.replace("_", " ").upper(),
            font=dict(family="JetBrains Mono", size=12, color="#666666"),
            x=0
        ),
        height=280,
        showlegend=True
    )
    fig = render_plotly_dark(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_correlation_heatmap(df, metric_cols):
    if len(metric_cols) < 2:
        return
    valid_cols = [c for c in metric_cols if c in df.columns]
    if len(valid_cols) < 2:
        return
    corr = df[valid_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=[c.replace("_", " ").upper() for c in corr.columns],
        y=[c.replace("_", " ").upper() for c in corr.index],
        colorscale=[
            [0.0, "#FF0000"],
            [0.5, "#0A0A0A"],
            [1.0, "#00CC44"]
        ],
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=10, family="JetBrains Mono"),
        hovertemplate="%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(
            text="METRIC CORRELATION MATRIX",
            font=dict(family="JetBrains Mono", size=12, color="#666666"),
            x=0
        ),
        height=350
    )
    fig = render_plotly_dark(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_timeline_chart(anomalies_df, column_info):
    time_col = column_info.get("time_col")
    if not time_col:
        return
    timeline = build_anomaly_timeline(anomalies_df, time_col)
    if timeline.empty:
        return
    fig = go.Figure()
    for severity, color in [("Critical", "#FF0000"), ("High", "#FF6600"), ("Medium", "#FFD700")]:
        sev_data = timeline[timeline["severity"] == severity]
        if sev_data.empty:
            continue
        fig.add_trace(go.Bar(
            x=sev_data["time_parsed"].astype(str),
            y=sev_data["count"],
            name=severity,
            marker_color=color,
            hovertemplate=f"<b>{severity}</b><br>Count: %{{y}}<extra></extra>"
        ))
    fig.update_layout(
        title=dict(
            text="ANOMALY TIMELINE",
            font=dict(family="JetBrains Mono", size=12, color="#666666"),
            x=0
        ),
        barmode="stack",
        height=250
    )
    fig = render_plotly_dark(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_column_report(report, anomalies_df, df, column_info, level_shift_anomalies):
    col = report.get("column")
    evidence = report.get("evidence", {})
    status = report.get("status", "error")
    severity = evidence.get("most_severe", "Normal")
    confidence = evidence.get("highest_confidence", "Low")
    card_class = get_severity_card_class(severity)
    severity_html = get_severity_badge_html(severity)
    confidence_html = get_confidence_badge_html(confidence)
    total = evidence.get("total_anomalies", 0)
    trend = evidence.get("trend_direction", "unknown")
    with st.expander(f"  {col.replace('_', ' ').upper()}  —  {total} anomalies  —  trend: {trend}", expanded=severity == "Critical"):
        st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:16px;
                        font-weight:700; color:#E8E8E8; letter-spacing:1px;">
                        {col.replace('_', ' ').upper()}
                    </span>
                    <div style="display:flex; gap:12px; align-items:center;">
                        {severity_html}
                        {confidence_html}
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1rem;">
                    <div>
                        <div class="trace-label">Total Anomalies</div>
                        <div class="trace-value" style="font-size:20px;">{total}</div>
                    </div>
                    <div>
                        <div class="trace-label">Critical</div>
                        <div class="trace-value" style="font-size:20px; color:#FF0000;">
                            {evidence.get('severity_breakdown', {}).get('critical', 0)}
                        </div>
                    </div>
                    <div>
                        <div class="trace-label">Trend</div>
                        <div class="trace-value" style="font-size:16px; color:#C0C0C0;">{trend.upper()}</div>
                    </div>
                    <div>
                        <div class="trace-label">Sustained Groups</div>
                        <div class="trace-value" style="font-size:20px;">{evidence.get('sustained_groups', 0)}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        render_anomaly_chart(df, col, anomalies_df, column_info, level_shift_anomalies)
        st.markdown('<div class="trace-section-title" style="margin-top:1rem;">ROOT CAUSE REPORT</div>', unsafe_allow_html=True)
        report_text = report.get("report", "No report generated.")
        if status == "fallback":
            st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:10px;
                        color:#FF6600; letter-spacing:1px; border:1px solid #FF6600;
                        padding:1px 6px; border-radius:2px;">
                        FALLBACK REPORT — LLM UNAVAILABLE
                    </span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown(f'<div class="trace-report-box">{report_text}</div>', unsafe_allow_html=True)
        top_dim = evidence.get("top_dimension_driver")
        top_metric = evidence.get("top_metric_driver")
        if top_dim or top_metric:
            st.markdown('<div class="trace-section-title" style="margin-top:1rem;">DRIVER EVIDENCE</div>', unsafe_allow_html=True)
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                if top_dim:
                    st.markdown(f"""
                        <div class="trace-card">
                            <div class="trace-label">Primary Dimension Driver</div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:14px;
                                font-weight:700; color:#E8E8E8; margin-top:4px;">
                                {str(top_dim.get('column','?')).upper()} = {top_dim.get('category','?')}
                            </div>
                            <div class="trace-subvalue">
                                {top_dim.get('contribution_pct', 0)}% contribution · {top_dim.get('strength','?')} signal
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            with dcol2:
                if top_metric:
                    lag_note = f" · {top_metric.get('best_lag')} row lag detected" if top_metric.get("has_lagged_effect") else ""
                    st.markdown(f"""
                        <div class="trace-card">
                            <div class="trace-label">Primary Metric Driver</div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:14px;
                                font-weight:700; color:#E8E8E8; margin-top:4px;">
                                {str(top_metric.get('column','?')).upper()}
                            </div>
                            <div class="trace-subvalue">
                                {top_metric.get('direction','?')} {abs(top_metric.get('mean_shift_pct', 0))}% during anomaly period{lag_note}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)


def render_special_anomalies(volume_anomalies, level_shift_anomalies, cross_column_anomalies):
    has_any = volume_anomalies or level_shift_anomalies or cross_column_anomalies
    if not has_any:
        return
    st.markdown('<div class="trace-section-title">04 — STRUCTURAL ANOMALIES</div>', unsafe_allow_html=True)
    if level_shift_anomalies:
        for shift in level_shift_anomalies:
            severity = shift.get("severity", "High")
            card_class = get_severity_card_class(severity)
            severity_html = get_severity_badge_html(severity)
            st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span class="trace-label">LEVEL SHIFT — {shift.get('column','?').upper()}</span>
                        {severity_html}
                    </div>
                    <div style="font-family:'Inter',sans-serif; font-size:13px; color:#CCCCCC;">
                        {shift.get('description','')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    if volume_anomalies:
        for vol in volume_anomalies:
            severity = vol.get("severity", "High")
            card_class = get_severity_card_class(severity)
            severity_html = get_severity_badge_html(severity)
            st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span class="trace-label">VOLUME ANOMALY — {vol.get('period','?')}</span>
                        {severity_html}
                    </div>
                    <div style="font-family:'Inter',sans-serif; font-size:13px; color:#CCCCCC;">
                        {vol.get('description','')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    if cross_column_anomalies:
        for cross in cross_column_anomalies[:3]:
            st.markdown(f"""
                <div class="trace-card-high">
                    <div style="margin-bottom:6px;">
                        <span class="trace-label">CROSS-COLUMN DIVERGENCE — </span>
                        <span style="font-family:'JetBrains Mono',monospace; font-size:11px;
                            color:#FF6600; font-weight:700;">
                            {cross.get('column_a','?').upper()} ↔ {cross.get('column_b','?').upper()}
                        </span>
                    </div>
                    <div style="font-family:'Inter',sans-serif; font-size:13px; color:#CCCCCC;">
                        {cross.get('description','')}
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_sidebar(df, column_info, quality_report, anomaly_counts):
    with st.sidebar:
        st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
                letter-spacing:3px; color:#444444; padding:1rem 0 0.5rem 0;">
                TRACE SYSTEM
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:18px;
                font-weight:700; color:#E8E8E8; margin-bottom:1.5rem;">
                DIAGNOSTIC PANEL
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="trace-label" style="margin-bottom:8px;">DATASET INFO</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#888888; line-height:2;">
                ROWS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {df.shape[0]}<br>
                COLUMNS &nbsp; {df.shape[1]}<br>
                METRICS &nbsp;&nbsp; {len(column_info.get('metric_cols',[]))}<br>
                DIMENSIONS {len(column_info.get('dimension_cols',[]))}<br>
                TIME COL &nbsp; {column_info.get('time_col','NONE') or 'NONE'}
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="trace-label" style="margin-bottom:8px;">ANOMALY SUMMARY</div>', unsafe_allow_html=True)
        for label, color in [("Critical","#FF0000"),("High","#FF6600"),("Medium","#FFD700")]:
            count = anomaly_counts.get(label, 0)
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0;
                    border-bottom:1px solid #1E1E1E;">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#666666;">
                        {label.upper()}
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:11px;
                        font-weight:700; color:{color};">
                        {count}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace; font-size:9px;
                letter-spacing:1px; color:#333333; margin-top:1rem; line-height:2;">
                TRACE v1.0<br>
                AI ROOT CAUSE ANALYZER<br>
                POWERED BY LLAMA 3.3 70B<br>
                © 2026 DEVESH SHUKLA
            </div>
        """, unsafe_allow_html=True)


def main():
    render_header()
    uploaded_file = render_upload_section()

    if uploaded_file is None:
        st.markdown("""
            <div class="trace-card" style="margin-top:2rem; text-align:center; padding:3rem;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
                    letter-spacing:3px; color:#333333; margin-bottom:1rem;">
                    AWAITING DATA INPUT
                </div>
                <div style="font-family:'Inter',sans-serif; font-size:14px; color:#444444;">
                    Upload a CSV or Excel file to begin root cause analysis.<br>
                    Supports any business domain — sales, HR, logistics, finance, operations.
                </div>
            </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("PROCESSING DATA..."):
        try:
            df, quality_report = load_file(uploaded_file)
            df, column_info = detect_columns(df)
        except Exception as e:
            st.error(f"Failed to load file: {str(e)}")
            return

    st.markdown("<hr>", unsafe_allow_html=True)
    render_quality_report(quality_report)
    st.markdown("<hr>", unsafe_allow_html=True)

    metric_cols = column_info.get("metric_cols", [])
    if not metric_cols:
        st.markdown("""
            <div class="trace-card" style="border-color:#FFD700;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:12px;
                    color:#FFD700; letter-spacing:1px;">
                    WARNING — No numeric metric columns detected. TRACE requires at least one numeric column.
                </span>
            </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("RUNNING ANOMALY DETECTION..."):
        try:
            (
                anomalies_df,
                trend_summary,
                cross_column_anomalies,
                distribution_profiles,
                zero_value_anomalies,
                volume_anomalies,
                level_shift_anomalies
            ) = detect_anomalies(df, column_info)
        except Exception as e:
            st.error(f"Anomaly detection failed: {str(e)}")
            return

    with st.spinner("RUNNING CORRELATION ANALYSIS..."):
        try:
            correlation_summary = build_correlation_summary(df, anomalies_df, column_info)
        except Exception as e:
            correlation_summary = {}

    with st.spinner("GENERATING AI ROOT CAUSE REPORTS..."):
        try:
            full_report = generate_full_report(
                df=df,
                anomalies_df=anomalies_df,
                trend_summary=trend_summary,
                correlation_summary=correlation_summary,
                distribution_profiles=distribution_profiles,
                zero_value_anomalies=zero_value_anomalies,
                volume_anomalies=volume_anomalies,
                level_shift_anomalies=level_shift_anomalies,
                cross_column_anomalies=cross_column_anomalies
            )
        except Exception as e:
            full_report = {
                "executive_summary": f"Report generation failed: {str(e)}",
                "column_reports": [],
                "status": "error"
            }

    anomaly_counts = summarize_anomaly_counts(anomalies_df)
    most_affected_col, most_affected_info = get_most_affected_column(trend_summary)

    render_sidebar(df, column_info, quality_report, anomaly_counts)
    render_kpi_cards(anomaly_counts, most_affected_col, most_affected_info, df.shape)
    st.markdown("<hr>", unsafe_allow_html=True)

    if full_report.get("status") != "clean":
        st.markdown('<div class="trace-section-title">03 — EXECUTIVE SUMMARY</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="trace-report-box" style="border-color:#333333; margin-bottom:1.5rem;">
                {full_report.get('executive_summary','')}
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    render_timeline_chart(anomalies_df, column_info)

    if len(metric_cols) >= 2:
        render_correlation_heatmap(df, metric_cols)

    render_special_anomalies(volume_anomalies, level_shift_anomalies, cross_column_anomalies)
    st.markdown("<hr>", unsafe_allow_html=True)

    column_reports = full_report.get("column_reports", [])
    if column_reports:
        st.markdown('<div class="trace-section-title">05 — COLUMN ANALYSIS</div>', unsafe_allow_html=True)
        column_reports_sorted = sorted(
            column_reports,
            key=lambda r: (
                r.get("evidence", {}).get("severity_breakdown", {}).get("critical", 0) * -3 +
                r.get("evidence", {}).get("severity_breakdown", {}).get("high", 0) * -2
            )
        )
        for report in column_reports_sorted:
            render_column_report(
                report=report,
                anomalies_df=anomalies_df,
                df=df,
                column_info=column_info,
                level_shift_anomalies=level_shift_anomalies
            )
    elif full_report.get("status") == "clean":
        st.markdown("""
            <div class="trace-card" style="border-color:#00CC44; text-align:center; padding:2rem;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:14px;
                    color:#00CC44; letter-spacing:2px; font-weight:700;">
                    ALL CLEAR — NO ANOMALIES DETECTED
                </div>
                <div style="font-family:'Inter',sans-serif; font-size:13px;
                    color:#444444; margin-top:8px;">
                    All metrics are within normal statistical boundaries.
                </div>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()