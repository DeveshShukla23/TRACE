import pandas as pd
import numpy as np
from scipy import stats


def calculate_contribution_percentage(df, anomaly_row_indices, target_col, dimension_col, category):
    if len(anomaly_row_indices) == 0:
        return 0.0
    try:
        anomaly_rows = df[df.index.isin(anomaly_row_indices)]
        normal_rows = df[~df.index.isin(anomaly_row_indices)]
        if len(normal_rows) == 0:
            return 0.0
        normal_mean = normal_rows[target_col].mean()
        total_loss = (normal_mean - anomaly_rows[target_col].mean()) * len(anomaly_rows)
        if total_loss == 0:
            return 0.0
        cat_anomaly_rows = anomaly_rows[anomaly_rows[dimension_col] == category]
        if len(cat_anomaly_rows) == 0:
            return 0.0
        cat_loss = (normal_mean - cat_anomaly_rows[target_col].mean()) * len(cat_anomaly_rows)
        contribution = (cat_loss / total_loss) * 100
        return round(float(np.clip(contribution, 0, 100)), 2)
    except Exception:
        return 0.0


def check_p_value_significance(series_a, series_b, threshold=0.05):
    try:
        clean_a = series_a.dropna()
        clean_b = series_b.dropna()
        common_idx = clean_a.index.intersection(clean_b.index)
        if len(common_idx) < 5:
            return False, 1.0
        corr, p_value = stats.pearsonr(clean_a[common_idx], clean_b[common_idx])
        return p_value < threshold, round(float(p_value), 6)
    except Exception:
        return False, 1.0


def detect_spurious_correlation(df, anomaly_row_indices, target_col, correlated_col, dimension_cols):
    if len(dimension_cols) == 0:
        return False, None
    try:
        anomaly_rows = df[df.index.isin(anomaly_row_indices)]
        if len(anomaly_rows) < 3:
            return False, None
        base_corr = anomaly_rows[target_col].corr(anomaly_rows[correlated_col])
        if pd.isna(base_corr):
            return False, None
        for dim_col in dimension_cols:
            if dim_col not in df.columns:
                continue
            top_category = (
                anomaly_rows[dim_col].value_counts().index[0]
                if len(anomaly_rows[dim_col].value_counts()) > 0
                else None
            )
            if top_category is None:
                continue
            subset = anomaly_rows[anomaly_rows[dim_col] != top_category]
            if len(subset) < 3:
                continue
            partial_corr = subset[target_col].corr(subset[correlated_col])
            if pd.isna(partial_corr):
                continue
            if abs(base_corr) >= 0.4 and abs(partial_corr) < 0.2:
                return True, dim_col
        return False, None
    except Exception:
        return False, None


def calculate_lagged_correlation(df, target_col, correlated_col, max_lag=5):
    best_lag = 0
    best_corr = 0.0
    best_p_value = 1.0
    try:
        for lag in range(1, max_lag + 1):
            shifted = df[correlated_col].shift(lag)
            valid_idx = df[target_col].notna() & shifted.notna()
            if valid_idx.sum() < 5:
                continue
            corr_val, p_val = stats.pearsonr(df[target_col][valid_idx], shifted[valid_idx])
            if abs(corr_val) > abs(best_corr) and p_val < 0.05:
                best_corr = corr_val
                best_lag = lag
                best_p_value = p_val
    except Exception:
        pass
    return best_lag, round(float(best_corr), 4), round(float(best_p_value), 6)


def detect_multi_dimension_interactions(df, anomaly_row_indices, target_col, dimension_cols):
    if len(dimension_cols) < 2 or len(anomaly_row_indices) == 0:
        return []
    interactions = []
    anomaly_rows = df[df.index.isin(anomaly_row_indices)]
    normal_rows = df[~df.index.isin(anomaly_row_indices)]
    if len(normal_rows) == 0:
        return []
    try:
        normal_mean = normal_rows[target_col].mean()
        for i in range(len(dimension_cols)):
            for j in range(i + 1, len(dimension_cols)):
                dim_a = dimension_cols[i]
                dim_b = dimension_cols[j]
                if dim_a not in df.columns or dim_b not in df.columns:
                    continue
                combo_groups = anomaly_rows.groupby([dim_a, dim_b])[target_col].agg(["mean", "count"])
                combo_groups = combo_groups[combo_groups["count"] >= 2]
                if len(combo_groups) == 0:
                    continue
                for (cat_a, cat_b), row in combo_groups.iterrows():
                    combo_mean = row["mean"]
                    combo_count = row["count"]
                    total_loss = (normal_mean - combo_mean) * combo_count
                    overall_total_loss = (normal_mean - anomaly_rows[target_col].mean()) * len(anomaly_rows)
                    if overall_total_loss == 0:
                        continue
                    contribution = (total_loss / overall_total_loss) * 100
                    if contribution >= 20:
                        interactions.append({
                            "dimension_a": dim_a,
                            "category_a": str(cat_a),
                            "dimension_b": dim_b,
                            "category_b": str(cat_b),
                            "combo_mean": round(float(combo_mean), 4),
                            "normal_mean": round(float(normal_mean), 4),
                            "count": int(combo_count),
                            "contribution_pct": round(float(np.clip(contribution, 0, 100)), 2),
                            "description": (
                                f"{dim_a}={cat_a} combined with {dim_b}={cat_b} "
                                f"accounts for {round(contribution, 1)}% of the total anomaly impact"
                            )
                        })
        interactions.sort(key=lambda x: x["contribution_pct"], reverse=True)
        return interactions[:5]
    except Exception:
        return []


def build_pareto_ranking(drivers):
    if not drivers:
        return []
    sorted_drivers = sorted(drivers, key=lambda x: x.get("contribution_pct", 0), reverse=True)
    cumulative = 0.0
    for driver in sorted_drivers:
        cumulative += driver.get("contribution_pct", 0)
        driver["cumulative_contribution_pct"] = round(min(cumulative, 100.0), 2)
        driver["pareto_critical"] = cumulative <= 80
    return sorted_drivers


def correlate_metric_to_dimensions(df, anomaly_row_indices, target_col, dimension_cols):
    if not dimension_cols or len(anomaly_row_indices) == 0:
        return []
    results = []
    anomaly_rows = df[df.index.isin(anomaly_row_indices)]
    normal_rows = df[~df.index.isin(anomaly_row_indices)]
    if len(normal_rows) == 0 or len(anomaly_rows) == 0:
        return []
    for dim_col in dimension_cols:
        if dim_col not in df.columns:
            continue
        anomaly_dist = anomaly_rows[dim_col].value_counts(normalize=True)
        normal_dist = normal_rows[dim_col].value_counts(normalize=True)
        for category in anomaly_dist.index:
            anomaly_share = anomaly_dist.get(category, 0)
            normal_share = normal_dist.get(category, 0)
            share_diff = anomaly_share - normal_share
            if abs(share_diff) < 0.15:
                continue
            contribution_pct = calculate_contribution_percentage(
                df, anomaly_row_indices, target_col, dim_col, category
            )
            results.append({
                "metric_col": target_col,
                "dimension_col": dim_col,
                "category": str(category),
                "anomaly_share": round(float(anomaly_share), 4),
                "normal_share": round(float(normal_share), 4),
                "share_difference": round(float(share_diff), 4),
                "contribution_pct": contribution_pct,
                "direction": "overrepresented" if share_diff > 0 else "underrepresented",
                "strength": "Strong" if abs(share_diff) >= 0.3 else "Moderate"
            })
    results.sort(key=lambda x: x["contribution_pct"], reverse=True)
    results = build_pareto_ranking(results)
    return results


def correlate_metric_to_metrics(df, anomaly_row_indices, target_col, metric_cols, dimension_cols):
    if len(anomaly_row_indices) == 0:
        return []
    results = []
    normal_row_indices = df.index[~df.index.isin(anomaly_row_indices)].tolist()
    if len(normal_row_indices) < 3:
        return []
    for col in metric_cols:
        if col == target_col or col not in df.columns:
            continue
        try:
            full_corr = df[target_col].corr(df[col])
        except Exception:
            continue
        if pd.isna(full_corr):
            continue
        is_significant, p_value = check_p_value_significance(df[target_col], df[col])
        if not is_significant:
            continue
        anomaly_vals_col = df.loc[anomaly_row_indices, col].dropna()
        normal_vals_col = df.loc[normal_row_indices, col].dropna()
        if len(anomaly_vals_col) == 0 or len(normal_vals_col) == 0:
            continue
        anomaly_mean = anomaly_vals_col.mean()
        normal_mean = normal_vals_col.mean()
        mean_shift = ((anomaly_mean - normal_mean) / normal_mean * 100) if normal_mean != 0 else 0
        if abs(mean_shift) < 10 or abs(full_corr) < 0.4:
            continue
        is_spurious, confounding_dim = detect_spurious_correlation(
            df, anomaly_row_indices, target_col, col, dimension_cols
        )
        best_lag, lag_corr, lag_p_value = calculate_lagged_correlation(df, target_col, col)
        results.append({
            "target_col": target_col,
            "correlated_col": col,
            "full_correlation": round(float(full_corr), 4),
            "p_value": p_value,
            "is_statistically_significant": True,
            "normal_mean": round(float(normal_mean), 4),
            "anomaly_mean": round(float(anomaly_mean), 4),
            "mean_shift_pct": round(float(mean_shift), 2),
            "direction": "rose" if mean_shift > 0 else "fell",
            "strength": "Strong" if abs(full_corr) >= 0.7 else "Moderate",
            "is_spurious": is_spurious,
            "confounding_dimension": confounding_dim,
            "spurious_warning": (
                f"Correlation may be confounded by {confounding_dim} — not a direct cause"
                if is_spurious else None
            ),
            "best_lag": best_lag,
            "lag_correlation": lag_corr,
            "lag_p_value": lag_p_value,
            "has_lagged_effect": best_lag > 0 and abs(lag_corr) > abs(full_corr)
        })
    results.sort(key=lambda x: (not x["is_spurious"], abs(x["mean_shift_pct"])), reverse=True)
    return results


def build_correlation_summary(df, anomalies_df, column_info):
    if anomalies_df.empty:
        return {}
    metric_cols = column_info.get("metric_cols", [])
    dimension_cols = column_info.get("dimension_cols", [])
    correlation_summary = {}
    affected_columns = anomalies_df[
        anomalies_df["suppressed"] == False
    ]["column"].unique()
    for col in affected_columns:
        col_anomaly_indices = anomalies_df[
            (anomalies_df["column"] == col) &
            (anomalies_df["suppressed"] == False)
        ]["row_index"].tolist()
        if len(col_anomaly_indices) == 0:
            continue
        dimension_drivers = correlate_metric_to_dimensions(
            df, col_anomaly_indices, col, dimension_cols
        )
        metric_drivers = correlate_metric_to_metrics(
            df, col_anomaly_indices, col, metric_cols, dimension_cols
        )
        multi_dim_interactions = detect_multi_dimension_interactions(
            df, col_anomaly_indices, col, dimension_cols
        )
        top_dimension_driver = dimension_drivers[0] if dimension_drivers else None
        top_metric_driver = next(
            (d for d in metric_drivers if not d.get("is_spurious", False)), None
        )
        primary_cause = None
        if top_dimension_driver and top_metric_driver:
            if top_dimension_driver.get("strength") == "Strong":
                primary_cause = "dimension"
            elif top_metric_driver.get("strength") == "Strong":
                primary_cause = "metric"
            else:
                primary_cause = "dimension"
        elif top_dimension_driver:
            primary_cause = "dimension"
        elif top_metric_driver:
            primary_cause = "metric"
        pareto_80_drivers = [
            d for d in dimension_drivers if d.get("pareto_critical", False)
        ]
        spurious_count = len([d for d in metric_drivers if d.get("is_spurious", False)])
        lagged_drivers = [d for d in metric_drivers if d.get("has_lagged_effect", False)]
        correlation_summary[col] = {
            "anomaly_count": len(col_anomaly_indices),
            "dimension_drivers": dimension_drivers[:5],
            "metric_drivers": metric_drivers[:5],
            "multi_dimension_interactions": multi_dim_interactions,
            "top_dimension_driver": top_dimension_driver,
            "top_metric_driver": top_metric_driver,
            "primary_cause_type": primary_cause,
            "pareto_80_drivers": pareto_80_drivers,
            "spurious_correlations_detected": spurious_count,
            "lagged_effect_drivers": lagged_drivers,
            "diagnosis_confidence": (
                "High" if primary_cause and (
                    (top_dimension_driver and top_dimension_driver.get("strength") == "Strong") or
                    (top_metric_driver and top_metric_driver.get("strength") == "Strong")
                ) else "Moderate" if primary_cause else "Low"
            )
        }
    return correlation_summary