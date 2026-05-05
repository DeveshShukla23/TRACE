import pandas as pd
import numpy as np


# ── NUMBER FORMATTING ──────────────────────────────────────────────────────────

def format_number(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        return f"{value:.2f}"
    except Exception:
        return "N/A"


def format_percentage(value, show_sign=True):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    try:
        value = float(value)
        if show_sign:
            return f"{value:+.2f}%"
        return f"{value:.2f}%"
    except Exception:
        return "N/A"


def format_delta(current, baseline):
    if current is None or baseline is None:
        return "N/A", "normal"
    try:
        current = float(current)
        baseline = float(baseline)
        if baseline == 0:
            return "N/A", "normal"
        delta_pct = ((current - baseline) / abs(baseline)) * 100
        formatted = f"{delta_pct:+.2f}%"
        direction = "inverse" if delta_pct < 0 else "normal"
        return formatted, direction
    except Exception:
        return "N/A", "normal"


def safe_divide(numerator, denominator, default=0.0):
    try:
        if denominator == 0:
            return default
        return float(numerator) / float(denominator)
    except Exception:
        return default


def truncate_text(text, max_length=300):
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


# ── SEVERITY SYSTEM ────────────────────────────────────────────────────────────

def get_severity_color(severity):
    colors = {
        "Critical": "#FF0000",
        "High":     "#FF6600",
        "Medium":   "#FFD700",
        "Normal":   "#00CC44"
    }
    return colors.get(severity, "#FFFFFF")


def get_severity_badge_html(severity):
    styles = {
        "Critical": (
            "color:#FF0000; font-family:'JetBrains Mono',monospace; "
            "font-size:12px; font-weight:700; letter-spacing:2px; "
            "animation:pulse-red 1.2s infinite; "
            "text-shadow:0 0 8px #FF000088;"
        ),
        "High": (
            "color:#FF6600; font-family:'JetBrains Mono',monospace; "
            "font-size:12px; font-weight:700; letter-spacing:2px;"
        ),
        "Medium": (
            "color:#FFD700; font-family:'JetBrains Mono',monospace; "
            "font-size:12px; font-weight:700; letter-spacing:2px;"
        ),
        "Normal": (
            "color:#00CC44; font-family:'JetBrains Mono',monospace; "
            "font-size:12px; font-weight:700; letter-spacing:2px;"
        )
    }
    style = styles.get(severity, "color:#FFFFFF;")
    return f'<span style="{style}">{severity.upper()}</span>'


def get_severity_card_class(severity):
    classes = {
        "Critical": "trace-card-critical",
        "High":     "trace-card-high",
        "Medium":   "trace-card-medium",
        "Normal":   "trace-card"
    }
    return classes.get(severity, "trace-card")


def severity_to_priority(severity):
    order = {"Critical": 0, "High": 1, "Medium": 2, "Normal": 3}
    return order.get(severity, 99)


# ── CONFIDENCE SYSTEM ──────────────────────────────────────────────────────────

def get_confidence_badge_html(confidence):
    configs = {
        "Very High": (
            "[ VERIFIED ]",
            "color:#00CC44; font-family:'JetBrains Mono',monospace; "
            "font-size:10px; font-weight:700; letter-spacing:1.5px; "
            "border:1px solid #00CC44; padding:1px 6px; border-radius:2px;"
        ),
        "High": (
            "[ CONFIRMED ]",
            "color:#66CC00; font-family:'JetBrains Mono',monospace; "
            "font-size:10px; font-weight:700; letter-spacing:1.5px; "
            "border:1px solid #66CC00; padding:1px 6px; border-radius:2px;"
        ),
        "Moderate": (
            "[ PROBABLE ]",
            "color:#FFD700; font-family:'JetBrains Mono',monospace; "
            "font-size:10px; font-weight:700; letter-spacing:1.5px; "
            "border:1px solid #FFD700; padding:1px 6px; border-radius:2px;"
        ),
        "Low": (
            "[ UNCERTAIN ]",
            "color:#FF6600; font-family:'JetBrains Mono',monospace; "
            "font-size:10px; font-weight:700; letter-spacing:1.5px; "
            "border:1px solid #FF6600; padding:1px 6px; border-radius:2px;"
        )
    }
    label, style = configs.get(confidence, ("[ UNKNOWN ]", "color:#FFFFFF;"))
    return f'<span style="{style}">{label}</span>'


# ── QUALITY REPORT SUMMARY ─────────────────────────────────────────────────────

def summarize_quality_report(quality_report):
    summary = []

    dup = quality_report.get("duplicate_rows_removed", 0)
    if dup > 0:
        summary.append(f"REMOVED — {dup} duplicate row(s)")

    currency = quality_report.get("currency_columns_cleaned", {})
    if currency:
        summary.append(f"CLEANED — Currency symbols in: {', '.join(currency.keys())}")

    mixed = quality_report.get("mixed_type_columns_fixed", {})
    if mixed:
        summary.append(f"FIXED — Mixed data types in: {', '.join(mixed.keys())}")

    dates = quality_report.get("numeric_dates_converted", [])
    if dates:
        cols = [d.get("column") for d in dates]
        summary.append(f"CONVERTED — Numeric dates in: {', '.join(cols)}")

    standardized = quality_report.get("categories_standardized", {})
    if standardized:
        total = sum(len(v) for v in standardized.values())
        summary.append(f"STANDARDIZED — {total} category inconsistencies across {len(standardized)} column(s)")

    outliers = quality_report.get("suspected_data_entry_outliers", {})
    if outliers:
        summary.append(f"FLAGGED — Suspected data entry errors in: {', '.join(outliers.keys())}")

    negatives = quality_report.get("negative_value_warnings", {})
    if negatives:
        summary.append(f"WARNING — Negative values in: {', '.join(negatives.keys())}")

    future_dates = quality_report.get("future_date_warnings", {})
    if future_dates:
        summary.append(f"WARNING — Future dates in: {', '.join(future_dates.keys())}")

    dup_cols = quality_report.get("duplicate_column_warnings", [])
    if dup_cols:
        pairs = [f"{d['column_a']} / {d['column_b']}" for d in dup_cols]
        summary.append(f"REVIEW — Possibly duplicate columns: {', '.join(pairs)}")

    suspicious = quality_report.get("suspicious_column_warnings", [])
    if suspicious:
        cols = [s["column"] for s in suspicious]
        summary.append(f"REVIEW — Suspicious columns: {', '.join(cols)}")

    return summary


# ── ANOMALY SUMMARY ────────────────────────────────────────────────────────────

def summarize_anomaly_counts(anomalies_df):
    if anomalies_df.empty:
        return {"Critical": 0, "High": 0, "Medium": 0, "Total": 0}
    active = anomalies_df[anomalies_df["suppressed"] == False]
    counts = active["severity"].value_counts().to_dict()
    return {
        "Critical": counts.get("Critical", 0),
        "High":     counts.get("High", 0),
        "Medium":   counts.get("Medium", 0),
        "Total":    len(active)
    }


def get_most_affected_column(trend_summary):
    if not trend_summary:
        return None, None
    most_affected = max(
        trend_summary.items(),
        key=lambda x: (
            x[1].get("critical_count", 0) * 3 +
            x[1].get("high_count", 0) * 2 +
            x[1].get("medium_count", 0)
        )
    )
    return most_affected[0], most_affected[1]


def group_anomalies_by_severity(anomalies_df):
    if anomalies_df.empty:
        return {"Critical": [], "High": [], "Medium": []}
    active = anomalies_df[anomalies_df["suppressed"] == False]
    grouped = {}
    for severity in ["Critical", "High", "Medium"]:
        subset = active[active["severity"] == severity]
        grouped[severity] = subset.to_dict("records") if not subset.empty else []
    return grouped


def group_anomalies_by_dimension(anomalies_df, df, dimension_cols):
    if anomalies_df.empty or not dimension_cols:
        return {}
    active = anomalies_df[anomalies_df["suppressed"] == False]
    if active.empty:
        return {}
    result = {}
    for dim_col in dimension_cols:
        if dim_col not in df.columns:
            continue
        anomaly_indices = active["row_index"].tolist()
        valid_indices = [i for i in anomaly_indices if i in df.index]
        if not valid_indices:
            continue
        dim_values = df.loc[valid_indices, dim_col]
        counts = dim_values.value_counts().to_dict()
        if counts:
            result[dim_col] = counts
    return result


# ── TIMELINE BUILDER ───────────────────────────────────────────────────────────

def build_anomaly_timeline(anomalies_df, time_col):
    if anomalies_df.empty or not time_col:
        return pd.DataFrame()
    active = anomalies_df[
        (anomalies_df["suppressed"] == False) &
        (anomalies_df["time"].notna())
    ].copy()
    if active.empty:
        return pd.DataFrame()
    active["time_parsed"] = pd.to_datetime(active["time"], errors="coerce")
    active = active.dropna(subset=["time_parsed"])
    if active.empty:
        return pd.DataFrame()
    timeline = (
        active.groupby(["time_parsed", "severity"])
        .size()
        .reset_index(name="count")
        .sort_values("time_parsed")
    )
    return timeline


# ── CHART ANNOTATION BUILDER ───────────────────────────────────────────────────

def build_chart_annotations(anomalies_df, col, time_col):
    annotations = []
    if anomalies_df.empty or not time_col:
        return annotations
    col_anomalies = anomalies_df[
        (anomalies_df["column"] == col) &
        (anomalies_df["suppressed"] == False) &
        (anomalies_df["severity"].isin(["Critical", "High"]))
    ]
    for _, row in col_anomalies.iterrows():
        if not row["time"]:
            continue
        severity = row["severity"]
        color = get_severity_color(severity)
        deviation = row.get("deviation_from_mean_pct", 0)
        direction = "above" if deviation > 0 else "below"
        annotations.append({
            "x": row["time"],
            "y": row["value"],
            "text": f"{severity}: {abs(round(deviation, 1))}% {direction} mean",
            "color": color,
            "severity": severity
        })
    return annotations


# ── REPORT STATUS SUMMARY ──────────────────────────────────────────────────────

def summarize_report_status(column_reports):
    if not column_reports:
        return {"success": 0, "fallback": 0, "error": 0, "total": 0}
    counts = {"success": 0, "fallback": 0, "error": 0, "total": len(column_reports)}
    for r in column_reports:
        status = r.get("status", "error")
        if status in counts:
            counts[status] += 1
    return counts


def get_overall_health_status(anomaly_counts):
    critical = anomaly_counts.get("Critical", 0)
    high = anomaly_counts.get("High", 0)
    medium = anomaly_counts.get("Medium", 0)
    total = anomaly_counts.get("Total", 0)
    if total == 0:
        return "CLEAN", "#00CC44"
    if critical > 0:
        return "CRITICAL", "#FF0000"
    if high > 0:
        return "ELEVATED", "#FF6600"
    if medium > 0:
        return "MODERATE", "#FFD700"
    return "CLEAN", "#00CC44"