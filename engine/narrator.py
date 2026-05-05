import os
import time
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MAX_EVIDENCE_CHARS = 1500
DISCLAIMER = (
    "\n\n---\n"
    "⚠ AI-Generated Report: This analysis was produced automatically from statistical findings. "
    "All conclusions should be verified by a qualified analyst before any business decisions are made."
)


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    return Groq(api_key=api_key)


def truncate_evidence(evidence_str, max_chars=MAX_EVIDENCE_CHARS):
    if len(evidence_str) <= max_chars:
        return evidence_str
    truncated = evidence_str[:max_chars]
    last_comma = truncated.rfind(",")
    if last_comma > max_chars * 0.8:
        truncated = truncated[:last_comma]
    return truncated + "\n[Evidence truncated to fit token limit — key findings preserved above]"


def validate_output(report, evidence):
    if not report or len(report.strip()) < 50:
        return False, "Report too short — likely incomplete generation"
    key_numbers = []
    try:
        if isinstance(evidence, dict):
            worst = evidence.get("worst_point", {})
            if worst:
                val = worst.get("value")
                if val is not None:
                    key_numbers.append(str(round(float(val), 1)))
                dev = worst.get("deviation_from_mean_pct")
                if dev is not None:
                    key_numbers.append(str(round(float(dev), 1)))
    except Exception:
        pass
    if not key_numbers:
        return True, None
    found = sum(1 for num in key_numbers if num in report)
    if found == 0 and len(key_numbers) >= 2:
        return False, "Report does not contain key statistical values — possible hallucination"
    return True, None


def build_fallback_report(col, evidence):
    try:
        severity = evidence.get("most_severe", "Unknown")
        total = evidence.get("total_anomalies", 0)
        trend = evidence.get("trend_direction", "unknown")
        worst = evidence.get("worst_point", {})
        value = worst.get("value", "N/A")
        deviation = worst.get("deviation_from_mean_pct", "N/A")
        time_val = worst.get("time", "unknown")
        top_dim = evidence.get("top_dimension_driver")
        top_metric = evidence.get("top_metric_driver")
        level_shift = evidence.get("level_shift")

        lines = [
            "SUMMARY",
            f"{col} shows {total} anomalies with {severity} severity. Trend direction: {trend}.",
            "",
            "ROOT CAUSE",
        ]

        if top_dim:
            lines.append(
                f"Primary dimension driver: {top_dim.get('column')} = {top_dim.get('category')} "
                f"({top_dim.get('contribution_pct')}% contribution, {top_dim.get('strength')} strength)."
            )
        elif top_metric:
            lines.append(
                f"Primary metric driver: {top_metric.get('column')} {top_metric.get('direction','changed')} "
                f"by {top_metric.get('mean_shift_pct', 'N/A')}% during anomaly period."
            )
        else:
            lines.append("No clear primary driver identified — further investigation required.")

        lines += [
            "",
            "KEY FINDINGS",
            f"- Worst point: value {value} at {time_val} ({deviation}% deviation from mean)",
            f"- Severity: {severity}",
            f"- Trend: {trend}",
        ]

        if level_shift:
            lines.append(
                f"- Level shift detected: {level_shift.get('shift_direction')} "
                f"{abs(level_shift.get('pct_change', 0))}% permanent change"
            )

        zero_count = evidence.get("zero_value_anomalies", 0)
        if zero_count:
            lines.append(f"- {zero_count} zero value(s) detected — possible data pipeline failure")

        lines += [
            "",
            "RECOMMENDATION",
            f"Investigate {col} focusing on the period around {time_val}. "
            f"{'Examine ' + str(top_dim.get('column','?')) + ' = ' + str(top_dim.get('category','?')) + ' segment specifically.' if top_dim else 'No specific segment identified — review full dataset for this period.'}"
        ]

        report = "\n".join(lines)
        report += DISCLAIMER
        return report
    except Exception as e:
        return f"Fallback report generation failed for {col}: {str(e)}{DISCLAIMER}"


def call_groq_with_retry(client, messages, max_tokens, max_retries=3):
    delay = 2
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.2,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = str(e)
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str:
                wait_time = delay * (2 ** attempt)
                time.sleep(wait_time)
            elif "401" in error_str or "invalid api key" in error_str:
                raise ValueError("Invalid Groq API key — check your .env file")
            else:
                time.sleep(delay)
    raise Exception(f"Groq API failed after {max_retries} attempts: {last_error}")


def build_anomaly_evidence(
    col,
    anomalies_df,
    trend_summary,
    correlation_summary,
    distribution_profiles,
    zero_value_anomalies,
    level_shift_anomalies,
    cross_column_anomalies
):
    evidence = {}
    col_anomalies = anomalies_df[anomalies_df["column"] == col]
    col_trend = trend_summary.get(col, {})
    col_correlation = correlation_summary.get(col, {})
    col_distribution = distribution_profiles.get(col, {})

    evidence["column"] = col
    evidence["total_anomalies"] = len(col_anomalies)
    evidence["severity_breakdown"] = {
        "critical": int(len(col_anomalies[col_anomalies["severity"] == "Critical"])),
        "high": int(len(col_anomalies[col_anomalies["severity"] == "High"])),
        "medium": int(len(col_anomalies[col_anomalies["severity"] == "Medium"]))
    }
    evidence["trend_direction"] = col_trend.get("trend_direction", "unknown")
    evidence["most_severe"] = col_trend.get("most_severe", "Unknown")
    evidence["highest_confidence"] = col_trend.get("highest_confidence", "Unknown")
    evidence["sustained_groups"] = col_trend.get("sustained_anomaly_groups", 0)
    evidence["distribution"] = {
        k: v for k, v in col_distribution.items()
        if k in ["mean", "median", "std", "min", "max", "is_skewed", "is_normal"]
    }

    worst = col_anomalies.sort_values("z_score", ascending=False).iloc[0] if len(col_anomalies) > 0 else None
    if worst is not None:
        evidence["worst_point"] = {
            "value": float(worst["value"]),
            "time": str(worst["time"]) if worst["time"] else "unknown",
            "deviation_from_mean_pct": float(worst["deviation_from_mean_pct"]),
            "z_score": float(worst["z_score"]),
            "severity": str(worst["severity"]),
            "confidence": str(worst["confidence"]),
            "methods_triggered": int(worst["methods_triggered"])
        }

    if col_correlation:
        top_dim = col_correlation.get("top_dimension_driver")
        top_metric = col_correlation.get("top_metric_driver")
        pareto = col_correlation.get("pareto_80_drivers", [])
        spurious_count = col_correlation.get("spurious_correlations_detected", 0)
        lagged = col_correlation.get("lagged_effect_drivers", [])
        multi_dim = col_correlation.get("multi_dimension_interactions", [])

        evidence["primary_cause_type"] = col_correlation.get("primary_cause_type")
        evidence["diagnosis_confidence"] = col_correlation.get("diagnosis_confidence")

        if top_dim:
            evidence["top_dimension_driver"] = {
                "column": top_dim.get("dimension_col"),
                "category": top_dim.get("category"),
                "contribution_pct": top_dim.get("contribution_pct"),
                "strength": top_dim.get("strength")
            }

        if top_metric and not top_metric.get("is_spurious"):
            evidence["top_metric_driver"] = {
                "column": top_metric.get("correlated_col"),
                "mean_shift_pct": top_metric.get("mean_shift_pct"),
                "direction": top_metric.get("direction"),
                "strength": top_metric.get("strength"),
                "has_lagged_effect": top_metric.get("has_lagged_effect"),
                "best_lag": top_metric.get("best_lag")
            }

        if pareto:
            evidence["pareto_80_drivers"] = [
                {
                    "dimension": d.get("dimension_col"),
                    "category": d.get("category"),
                    "contribution_pct": d.get("contribution_pct"),
                    "cumulative_pct": d.get("cumulative_contribution_pct")
                }
                for d in pareto[:2]
            ]

        if spurious_count > 0:
            evidence["spurious_correlations_detected"] = spurious_count

        if lagged:
            evidence["lagged_drivers"] = [
                {
                    "column": d.get("correlated_col"),
                    "lag": d.get("best_lag"),
                    "lag_correlation": d.get("lag_correlation")
                }
                for d in lagged[:1]
            ]

        if multi_dim:
            evidence["multi_dimension_interactions"] = [
                {
                    "combo": f"{d.get('dimension_a')}={d.get('category_a')} + {d.get('dimension_b')}={d.get('category_b')}",
                    "contribution_pct": d.get("contribution_pct")
                }
                for d in multi_dim[:1]
            ]

    col_zeros = [z for z in zero_value_anomalies if z.get("column") == col]
    if col_zeros:
        evidence["zero_value_anomalies"] = len(col_zeros)

    col_shifts = [s for s in level_shift_anomalies if s.get("column") == col]
    if col_shifts:
        shift = col_shifts[0]
        evidence["level_shift"] = {
            "direction": shift.get("shift_direction"),
            "pct_change": shift.get("pct_change"),
            "mean_before": shift.get("mean_before"),
            "mean_after": shift.get("mean_after"),
            "severity": shift.get("severity")
        }

    col_cross = [
        c for c in cross_column_anomalies
        if c.get("column_a") == col or c.get("column_b") == col
    ]
    if col_cross:
        evidence["cross_column_divergence"] = [
            {
                "paired_with": c.get("column_b") if c.get("column_a") == col else c.get("column_a"),
                "correlation_shift": c.get("correlation_shift"),
                "severity": c.get("severity")
            }
            for c in col_cross[:1]
        ]

    return evidence


def build_narrator_prompt(evidence_str):
    return f"""You are a senior data analyst writing a root cause analysis report.
You will be given structured statistical findings. Convert them into clear professional business English.

STRICT RULES:
- Only use information provided in the findings below
- Do not invent assume or add any information not present
- Use specific numbers from the findings
- Write in plain business English with no technical jargon
- Structure your response with these exact sections:
  1. SUMMARY (2-3 sentences — what happened and how severe)
  2. ROOT CAUSE (what drove this anomaly based on the evidence)
  3. KEY FINDINGS (bullet points — specific numbers only)
  4. RECOMMENDATION (what the analyst should investigate next)

STATISTICAL FINDINGS:
{evidence_str}

Write the report now. Be specific and concise."""


def narrate_column(
    col,
    anomalies_df,
    trend_summary,
    correlation_summary,
    distribution_profiles,
    zero_value_anomalies,
    level_shift_anomalies,
    cross_column_anomalies,
    client
):
    try:
        evidence = build_anomaly_evidence(
            col,
            anomalies_df,
            trend_summary,
            correlation_summary,
            distribution_profiles,
            zero_value_anomalies,
            level_shift_anomalies,
            cross_column_anomalies
        )

        evidence_str = truncate_evidence(str(evidence))
        prompt = build_narrator_prompt(evidence_str)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior data analyst. "
                    "Write precise grounded root cause analysis reports. "
                    "Never hallucinate. Never add information not in the findings. "
                    "Always cite specific numbers."
                )
            },
            {"role": "user", "content": prompt}
        ]

        report = call_groq_with_retry(client, messages, max_tokens=600)
        is_valid, validation_warning = validate_output(report, evidence)

        if not is_valid:
            report = build_fallback_report(col, evidence)
            return {
                "column": col,
                "report": report,
                "evidence": evidence,
                "status": "fallback",
                "fallback_reason": validation_warning
            }

        report += DISCLAIMER
        return {
            "column": col,
            "report": report,
            "evidence": evidence,
            "status": "success",
            "validation_warning": validation_warning
        }

    except Exception as e:
        fallback = build_fallback_report(col, {})
        return {
            "column": col,
            "report": fallback,
            "evidence": {},
            "status": "error",
            "error": str(e)
        }


def build_executive_summary(all_reports, volume_anomalies, level_shift_anomalies, cross_column_anomalies, client):
    try:
        critical_cols = [
            r["column"] for r in all_reports
            if r["status"] in ("success", "fallback") and
            r.get("evidence", {}).get("most_severe") == "Critical"
        ]

        high_cols = [
            r["column"] for r in all_reports
            if r["status"] in ("success", "fallback") and
            r.get("evidence", {}).get("most_severe") == "High"
        ]

        total_anomalous_cols = len([r for r in all_reports if r["status"] in ("success", "fallback")])

        summary_evidence = {
            "total_anomalous_columns": total_anomalous_cols,
            "critical_columns": critical_cols,
            "high_severity_columns": high_cols,
            "volume_anomalies_detected": len(volume_anomalies),
            "level_shifts_detected": len(level_shift_anomalies),
            "cross_column_divergences": len(cross_column_anomalies),
            "level_shift_details": [
                {
                    "column": s.get("column"),
                    "direction": s.get("shift_direction"),
                    "pct_change": s.get("pct_change")
                }
                for s in level_shift_anomalies[:2]
            ],
            "volume_anomaly_details": [
                {
                    "period": v.get("period"),
                    "direction": v.get("direction"),
                    "row_count": v.get("row_count"),
                    "expected": v.get("expected_average")
                }
                for v in volume_anomalies[:2]
            ]
        }

        evidence_str = truncate_evidence(str(summary_evidence), max_chars=1000)

        exec_prompt = f"""You are a senior data analyst writing an executive summary.

STRICT RULES:
- Only use the information provided below
- Be direct and concise — maximum 4 sentences
- Lead with the most critical finding
- End with one clear recommended action

FINDINGS:
{evidence_str}

Write the executive summary now."""

        messages = [
            {
                "role": "system",
                "content": "You are a senior data analyst. Write concise executive summaries. Never hallucinate. Only use provided findings."
            },
            {"role": "user", "content": exec_prompt}
        ]

        summary = call_groq_with_retry(client, messages, max_tokens=250)
        summary += DISCLAIMER
        return summary

    except Exception as e:
        critical = [r["column"] for r in all_reports if r.get("evidence", {}).get("most_severe") == "Critical"]
        fallback_summary = (
            f"Analysis complete. {len(all_reports)} column(s) contain anomalies. "
            f"Critical issues found in: {', '.join(critical) if critical else 'none'}. "
            f"Level shifts: {len(level_shift_anomalies)}. Volume anomalies: {len(volume_anomalies)}. "
            f"Review individual column reports for details."
        )
        fallback_summary += DISCLAIMER
        return fallback_summary


def generate_full_report(
    df,
    anomalies_df,
    trend_summary,
    correlation_summary,
    distribution_profiles,
    zero_value_anomalies,
    volume_anomalies,
    level_shift_anomalies,
    cross_column_anomalies
):
    if anomalies_df.empty:
        return {
            "executive_summary": "No anomalies detected in the uploaded dataset. All metrics appear within normal statistical boundaries.",
            "column_reports": [],
            "status": "clean"
        }

    try:
        client = get_groq_client()
    except ValueError as e:
        return {
            "executive_summary": str(e),
            "column_reports": [],
            "status": "error"
        }

    all_affected = anomalies_df[
        anomalies_df["suppressed"] == False
    ]["column"].unique().tolist()

    col_scores = {}
    for col in all_affected:
        col_data = anomalies_df[anomalies_df["column"] == col]
        score = (
            len(col_data[col_data["severity"] == "Critical"]) * 3 +
            len(col_data[col_data["severity"] == "High"]) * 2 +
            len(col_data[col_data["severity"] == "Medium"])
        )
        col_scores[col] = score

    affected_columns = sorted(col_scores, key=col_scores.get, reverse=True)[:5]

    column_reports = []

    for i, col in enumerate(affected_columns):
        report = narrate_column(
            col=col,
            anomalies_df=anomalies_df,
            trend_summary=trend_summary,
            correlation_summary=correlation_summary,
            distribution_profiles=distribution_profiles,
            zero_value_anomalies=zero_value_anomalies,
            level_shift_anomalies=level_shift_anomalies,
            cross_column_anomalies=cross_column_anomalies,
            client=client
        )
        column_reports.append(report)

        if i < len(affected_columns) - 1:
            time.sleep(2)

    executive_summary = build_executive_summary(
        all_reports=column_reports,
        volume_anomalies=volume_anomalies,
        level_shift_anomalies=level_shift_anomalies,
        cross_column_anomalies=cross_column_anomalies,
        client=client
    )

    return {
        "executive_summary": executive_summary,
        "column_reports": column_reports,
        "status": "complete"
    }