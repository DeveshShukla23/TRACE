import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest


def is_constant_column(series):
    clean = series.dropna()
    return clean.nunique() <= 1


def is_sufficient_data(series, min_rows=3):
    return series.dropna().count() >= min_rows


def get_distribution_profile(series):
    clean = series.dropna()
    if len(clean) < 3:
        return {}
    try:
        skewness = float(clean.skew())
        kurtosis = float(clean.kurtosis())
    except:
        skewness = 0.0
        kurtosis = 0.0
    return {
        "count": int(len(clean)),
        "mean": round(float(clean.mean()), 4),
        "median": round(float(clean.median()), 4),
        "std": round(float(clean.std()), 4),
        "min": round(float(clean.min()), 4),
        "max": round(float(clean.max()), 4),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurtosis, 4),
        "is_skewed": abs(skewness) > 1.0,
        "is_normal": abs(skewness) <= 0.5 and abs(kurtosis) <= 1.0
    }


def calculate_zscore(series):
    clean = series.dropna()
    if not is_sufficient_data(series) or is_constant_column(series):
        return pd.Series([0.0] * len(series), index=series.index)
    z_scores = np.abs(stats.zscore(clean))
    result = pd.Series([np.nan] * len(series), index=series.index)
    result[clean.index] = z_scores
    return result


def calculate_modified_zscore(series):
    clean = series.dropna()
    if not is_sufficient_data(series) or is_constant_column(series):
        return pd.Series([0.0] * len(series), index=series.index)
    median = clean.median()
    mad = np.median(np.abs(clean - median))
    if mad == 0:
        mad = np.mean(np.abs(clean - median))
    if mad == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    modified_z = 0.6745 * np.abs(clean - median) / mad
    result = pd.Series([np.nan] * len(series), index=series.index)
    result[clean.index] = modified_z
    return result


def calculate_rolling_zscore(series, window=7):
    if not is_sufficient_data(series, min_rows=window + 1):
        return pd.Series([np.nan] * len(series), index=series.index)
    rolling_mean = series.rolling(window=window, min_periods=3).mean()
    rolling_std = series.rolling(window=window, min_periods=3).std()
    rolling_std = rolling_std.replace(0, np.nan)
    rolling_z = np.abs((series - rolling_mean) / rolling_std)
    return rolling_z


def calculate_iqr_bounds(series):
    clean = series.dropna()
    if not is_sufficient_data(series) or is_constant_column(series):
        return None, None, 1.5
    Q1 = clean.quantile(0.25)
    Q3 = clean.quantile(0.75)
    IQR = Q3 - Q1
    if IQR == 0:
        return None, None, 1.5
    mean_val = clean.mean()
    cv = (clean.std() / mean_val) if mean_val != 0 else 1
    if abs(cv) < 0.1:
        multiplier = 1.0
    elif abs(cv) < 0.3:
        multiplier = 1.5
    else:
        multiplier = 2.0
    lower = Q1 - (multiplier * IQR)
    upper = Q3 + (multiplier * IQR)
    return lower, upper, multiplier


def calculate_rate_of_change(series):
    if not is_sufficient_data(series):
        return pd.Series([np.nan] * len(series), index=series.index)
    roc = series.pct_change() * 100
    return roc


def calculate_roc_zscore(roc_series):
    clean = roc_series.dropna()
    if len(clean) < 3 or is_constant_column(clean):
        return pd.Series([np.nan] * len(roc_series), index=roc_series.index)
    z_scores = np.abs(stats.zscore(clean))
    result = pd.Series([np.nan] * len(roc_series), index=roc_series.index)
    result[clean.index] = z_scores
    return result


def run_isolation_forest(df, metric_cols):
    valid_cols = [
        col for col in metric_cols
        if col in df.columns
        and is_sufficient_data(df[col])
        and not is_constant_column(df[col])
    ]
    if len(valid_cols) == 0:
        return pd.Series([False] * len(df), index=df.index), pd.Series([0.0] * len(df), index=df.index)
    subset = df[valid_cols].copy()
    subset = subset.fillna(subset.median())
    contamination = min(0.05, max(0.01, 10 / len(subset)))
    try:
        iso = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            max_samples="auto"
        )
        predictions = iso.fit_predict(subset)
        scores = iso.decision_function(subset)
        is_anomaly = pd.Series(predictions == -1, index=df.index)
        anomaly_scores = pd.Series(np.abs(scores), index=df.index)
        return is_anomaly, anomaly_scores
    except Exception:
        return pd.Series([False] * len(df), index=df.index), pd.Series([0.0] * len(df), index=df.index)


def detect_cross_column_anomalies(df, metric_cols):
    valid_cols = [
        col for col in metric_cols
        if col in df.columns
        and is_sufficient_data(df[col])
        and not is_constant_column(df[col])
        and len(df[col].dropna()) >= 5
    ]
    if len(valid_cols) < 2:
        return []
    cross_anomalies = []
    subset = df[valid_cols].fillna(df[valid_cols].median())
    corr_matrix = subset.corr()
    for i in range(len(valid_cols)):
        for j in range(i + 1, len(valid_cols)):
            col_a = valid_cols[i]
            col_b = valid_cols[j]
            baseline_corr = corr_matrix.loc[col_a, col_b]
            if abs(baseline_corr) < 0.6:
                continue
            window = min(10, len(df) // 3)
            if window < 3:
                continue
            for start in range(len(df) - window + 1):
                window_slice = subset.iloc[start:start + window]
                if len(window_slice) < 3:
                    continue
                try:
                    window_corr = window_slice[col_a].corr(window_slice[col_b])
                except:
                    continue
                if pd.isna(window_corr):
                    continue
                corr_shift = abs(baseline_corr - window_corr)
                if corr_shift > 0.5:
                    cross_anomalies.append({
                        "column_a": col_a,
                        "column_b": col_b,
                        "baseline_correlation": round(float(baseline_corr), 4),
                        "window_correlation": round(float(window_corr), 4),
                        "correlation_shift": round(float(corr_shift), 4),
                        "window_start_index": start,
                        "window_end_index": start + window - 1,
                        "severity": "High" if corr_shift > 0.7 else "Medium",
                        "description": (
                            f"{col_a} and {col_b} normally move together "
                            f"(correlation {round(baseline_corr, 2)}) but diverged sharply "
                            f"(correlation dropped to {round(window_corr, 2)}) "
                            f"between rows {start} and {start + window - 1}"
                        )
                    })
    return cross_anomalies


def detect_zero_value_anomalies(df, metric_cols):
    zero_anomalies = []
    for col in metric_cols:
        if col not in df.columns:
            continue
        if not is_sufficient_data(df[col]):
            continue
        clean = df[col].dropna()
        total = len(clean)
        zero_mask = clean == 0
        zero_count = zero_mask.sum()
        if zero_count == 0:
            continue
        zero_ratio = zero_count / total
        non_zero = clean[clean != 0]
        if len(non_zero) < 3:
            continue
        expected_zero_rate = zero_ratio
        if expected_zero_rate > 0.4:
            continue
        for idx in clean[zero_mask].index:
            position = list(clean.index).index(idx)
            window_start = max(0, position - 5)
            window_end = min(len(clean), position + 5)
            local_window = clean.iloc[window_start:window_end]
            local_non_zero = local_window[local_window != 0]
            if len(local_non_zero) == 0:
                continue
            local_mean = local_non_zero.mean()
            severity = "Critical" if local_mean > non_zero.mean() * 0.5 else "High"
            zero_anomalies.append({
                "column": col,
                "row_index": idx,
                "value": 0.0,
                "local_mean": round(float(local_mean), 4),
                "column_mean": round(float(non_zero.mean()), 4),
                "zero_ratio_in_column": round(float(zero_ratio), 4),
                "severity": severity,
                "description": (
                    f"Zero value detected in {col} at row {idx}. "
                    f"Local average around this point is {round(local_mean, 2)}. "
                    f"Possible data pipeline failure, system outage, or missing transaction."
                )
            })
    return zero_anomalies


def detect_volume_anomalies(df, time_col):
    if time_col is None or time_col not in df.columns:
        return []
    try:
        time_series = pd.to_datetime(df[time_col], errors="coerce")
        if time_series.isna().mean() > 0.5:
            return []
        df_temp = df.copy()
        df_temp["_parsed_time"] = time_series
        df_temp = df_temp.dropna(subset=["_parsed_time"])
        time_range = df_temp["_parsed_time"].max() - df_temp["_parsed_time"].min()
        total_days = time_range.days
        if total_days <= 1:
            return []
        if total_days <= 31:
            freq = "D"
            period_label = "day"
        elif total_days <= 365:
            freq = "W"
            period_label = "week"
        else:
            freq = "ME"
            period_label = "month"
        volume_by_period = df_temp.groupby(
            pd.Grouper(key="_parsed_time", freq=freq)
        ).size()
        volume_by_period = volume_by_period[volume_by_period > 0]
        if len(volume_by_period) < 3:
            return []
        volume_mean = volume_by_period.mean()
        volume_std = volume_by_period.std()
        if volume_std == 0:
            return []
        volume_anomalies = []
        for period, count in volume_by_period.items():
            z = abs((count - volume_mean) / volume_std)
            if z >= 2:
                severity = "Critical" if z >= 3 else "High"
                direction = "low" if count < volume_mean else "high"
                volume_anomalies.append({
                    "period": str(period.date()) if hasattr(period, "date") else str(period),
                    "period_label": period_label,
                    "row_count": int(count),
                    "expected_average": round(float(volume_mean), 1),
                    "z_score": round(float(z), 4),
                    "direction": direction,
                    "severity": severity,
                    "description": (
                        f"Abnormal data volume detected for {period_label} of {str(period)[:10]}. "
                        f"Row count: {int(count)} vs expected average of {round(volume_mean, 1)}. "
                        f"{'Unusually low volume may indicate missing or incomplete data.' if direction == 'low' else 'Unusually high volume may indicate duplicate records or data feed issues.'}"
                    )
                })
        return volume_anomalies
    except Exception:
        return []


def detect_level_shifts(df, metric_cols):
    level_shift_results = []
    min_rows_required = 20
    for col in metric_cols:
        if col not in df.columns:
            continue
        clean = df[col].dropna()
        if len(clean) < min_rows_required:
            continue
        if is_constant_column(df[col]):
            continue
        values = clean.values
        n = len(values)
        min_segment = max(5, n // 5)
        best_shift = None
        best_score = 0
        for split in range(min_segment, n - min_segment):
            before = values[:split]
            after = values[split:]
            mean_before = np.mean(before)
            mean_after = np.mean(after)
            std_before = np.std(before)
            std_after = np.std(after)
            pooled_std = np.sqrt(
                ((len(before) - 1) * std_before ** 2 + (len(after) - 1) * std_after ** 2)
                / (len(before) + len(after) - 2)
            )
            if pooled_std == 0:
                continue
            shift_magnitude = abs(mean_after - mean_before) / pooled_std
            if shift_magnitude > best_score:
                best_score = shift_magnitude
                best_shift = {
                    "split_index": int(clean.index[split]),
                    "split_position": split,
                    "mean_before": round(float(mean_before), 4),
                    "mean_after": round(float(mean_after), 4),
                    "shift_magnitude": round(float(shift_magnitude), 4),
                    "shift_direction": "downward" if mean_after < mean_before else "upward",
                    "pct_change": round(((mean_after - mean_before) / mean_before) * 100, 2) if mean_before != 0 else 0.0
                }
        if best_shift and best_shift["shift_magnitude"] >= 2.0:
            severity = "Critical" if best_shift["shift_magnitude"] >= 3.5 else "High" if best_shift["shift_magnitude"] >= 2.5 else "Medium"
            level_shift_results.append({
                "column": col,
                "severity": severity,
                "split_index": best_shift["split_index"],
                "mean_before": best_shift["mean_before"],
                "mean_after": best_shift["mean_after"],
                "shift_magnitude": best_shift["shift_magnitude"],
                "shift_direction": best_shift["shift_direction"],
                "pct_change": best_shift["pct_change"],
                "description": (
                    f"Permanent level shift detected in {col}. "
                    f"Baseline changed {best_shift['shift_direction']} by {abs(best_shift['pct_change'])}% "
                    f"at row {best_shift['split_index']}. "
                    f"Mean before: {best_shift['mean_before']}, Mean after: {best_shift['mean_after']}. "
                    f"This is a sustained structural change, not a temporary spike."
                )
            })
    return level_shift_results


def suppress_false_positives(anomalies):
    if not anomalies:
        return anomalies
    filtered = []
    for a in anomalies:
        methods = a.get("methods_triggered", 0)
        confidence = a.get("confidence", "Low")
        severity = a.get("severity", "Normal")
        if confidence == "Low" and severity == "Medium" and methods == 1:
            a["suppressed"] = True
            a["suppression_reason"] = "Single method detection with low confidence — likely noise"
        else:
            a["suppressed"] = False
        filtered.append(a)
    return filtered


def get_severity(z_score, modified_z, rolling_z=None, roc_z=None):
    scores = [z_score, modified_z]
    if rolling_z is not None and not np.isnan(rolling_z):
        scores.append(rolling_z)
    if roc_z is not None and not np.isnan(roc_z):
        scores.append(roc_z)
    max_z = max(scores)
    if max_z >= 4:
        return "Critical"
    elif max_z >= 3:
        return "High"
    elif max_z >= 2:
        return "Medium"
    else:
        return "Normal"


def get_confidence(z_flagged, modified_z_flagged, iqr_flagged, rolling_z_flagged, roc_flagged, iso_flagged):
    methods_triggered = sum([z_flagged, modified_z_flagged, iqr_flagged, rolling_z_flagged, roc_flagged, iso_flagged])
    if methods_triggered >= 5:
        return "Very High"
    elif methods_triggered >= 4:
        return "High"
    elif methods_triggered >= 2:
        return "Moderate"
    else:
        return "Low"


def detect_consecutive_anomalies(anomalies_df):
    if anomalies_df.empty:
        return anomalies_df
    anomalies_df = anomalies_df.copy()
    anomalies_df["is_sustained"] = False
    anomalies_df["sustained_length"] = 1
    columns = anomalies_df["column"].unique()
    for col in columns:
        col_mask = anomalies_df["column"] == col
        col_indices = anomalies_df[col_mask].index.tolist()
        if len(col_indices) < 2:
            continue
        col_rows = anomalies_df.loc[col_indices, "row_index"].tolist()
        group = [col_indices[0]]
        groups = []
        for i in range(1, len(col_indices)):
            current_row = col_rows[i]
            previous_row = col_rows[i - 1]
            if current_row - previous_row <= 2:
                group.append(col_indices[i])
            else:
                groups.append(group)
                group = [col_indices[i]]
        groups.append(group)
        for g in groups:
            if len(g) >= 3:
                anomalies_df.loc[g, "is_sustained"] = True
                anomalies_df.loc[g, "sustained_length"] = len(g)
    return anomalies_df


def detect_trend_direction(series, anomaly_indices):
    if len(anomaly_indices) < 2:
        return "single_point"
    values_at_anomalies = series[anomaly_indices].dropna()
    if len(values_at_anomalies) < 2:
        return "single_point"
    slope = np.polyfit(range(len(values_at_anomalies)), values_at_anomalies.values, 1)[0]
    if slope < -0.01 * values_at_anomalies.mean():
        return "declining"
    elif slope > 0.01 * values_at_anomalies.mean():
        return "rising"
    else:
        return "volatile"


def detect_anomalies(df, column_info):
    metric_cols = column_info.get("metric_cols", [])
    time_col = column_info.get("time_col", None)
    anomalies = []

    distribution_profiles = {}
    for col in metric_cols:
        if col in df.columns:
            distribution_profiles[col] = get_distribution_profile(df[col])

    iso_anomaly_flags, iso_anomaly_scores = run_isolation_forest(df, metric_cols)
    cross_column_anomalies = detect_cross_column_anomalies(df, metric_cols)
    zero_value_anomalies = detect_zero_value_anomalies(df, metric_cols)
    volume_anomalies = detect_volume_anomalies(df, time_col)
    level_shift_anomalies = detect_level_shifts(df, metric_cols)

    for col in metric_cols:
        if col not in df.columns:
            continue
        if is_constant_column(df[col]):
            continue
        if not is_sufficient_data(df[col]):
            continue

        z_scores = calculate_zscore(df[col])
        modified_z_scores = calculate_modified_zscore(df[col])
        rolling_z_scores = calculate_rolling_zscore(df[col], window=7)
        roc_series = calculate_rate_of_change(df[col])
        roc_z_scores = calculate_roc_zscore(roc_series)
        lower_bound, upper_bound, iqr_multiplier = calculate_iqr_bounds(df[col])

        profile = distribution_profiles.get(col, {})
        col_mean = profile.get("mean", float(df[col].mean()))
        col_median = profile.get("median", float(df[col].median()))
        col_std = profile.get("std", float(df[col].std()))

        for idx, row in df.iterrows():
            value = row[col]
            if pd.isna(value):
                continue

            z = float(z_scores[idx]) if not pd.isna(z_scores[idx]) else 0.0
            mz = float(modified_z_scores[idx]) if not pd.isna(modified_z_scores[idx]) else 0.0
            rz = float(rolling_z_scores[idx]) if not pd.isna(rolling_z_scores[idx]) else 0.0
            roc = float(roc_series[idx]) if not pd.isna(roc_series[idx]) else 0.0
            roc_z = float(roc_z_scores[idx]) if not pd.isna(roc_z_scores[idx]) else 0.0
            iso_flag = bool(iso_anomaly_flags[idx]) if idx in iso_anomaly_flags.index else False
            iso_score = float(iso_anomaly_scores[idx]) if idx in iso_anomaly_scores.index else 0.0

            z_flagged = z >= 2
            modified_z_flagged = mz >= 2
            rolling_z_flagged = rz >= 2
            roc_flagged = roc_z >= 2
            iqr_flagged = False
            if lower_bound is not None and upper_bound is not None:
                iqr_flagged = value < lower_bound or value > upper_bound

            if not (z_flagged or modified_z_flagged or iqr_flagged or rolling_z_flagged or roc_flagged or iso_flag):
                continue

            severity = get_severity(z, mz, rz, roc_z)
            confidence = get_confidence(z_flagged, modified_z_flagged, iqr_flagged, rolling_z_flagged, roc_flagged, iso_flag)

            time_value = None
            if time_col and time_col in df.columns:
                time_value = str(row[time_col])

            deviation_from_mean = round(((value - col_mean) / col_mean) * 100, 2) if col_mean != 0 else 0.0
            deviation_from_median = round(((value - col_median) / col_median) * 100, 2) if col_median != 0 else 0.0
            direction = "above_normal" if value > col_mean else "below_normal"

            anomalies.append({
                "column": col,
                "row_index": idx,
                "time": time_value,
                "value": round(float(value), 4),
                "column_mean": round(float(col_mean), 4),
                "column_median": round(float(col_median), 4),
                "column_std": round(float(col_std), 4),
                "distribution_skewed": profile.get("is_skewed", False),
                "distribution_normal": profile.get("is_normal", False),
                "deviation_from_mean_pct": deviation_from_mean,
                "deviation_from_median_pct": deviation_from_median,
                "direction": direction,
                "z_score": round(z, 4),
                "modified_z_score": round(mz, 4),
                "rolling_z_score": round(rz, 4),
                "rate_of_change_pct": round(roc, 4),
                "roc_z_score": round(roc_z, 4),
                "isolation_forest_flagged": iso_flag,
                "isolation_forest_score": round(iso_score, 4),
                "iqr_flagged": iqr_flagged,
                "iqr_multiplier_used": iqr_multiplier,
                "lower_bound": round(float(lower_bound), 4) if lower_bound is not None else None,
                "upper_bound": round(float(upper_bound), 4) if upper_bound is not None else None,
                "severity": severity,
                "confidence": confidence,
                "methods_triggered": sum([z_flagged, modified_z_flagged, iqr_flagged, rolling_z_flagged, roc_flagged, iso_flag]),
                "z_flagged": z_flagged,
                "modified_z_flagged": modified_z_flagged,
                "rolling_z_flagged": rolling_z_flagged,
                "roc_flagged": roc_flagged,
                "iqr_flagged": iqr_flagged,
                "suppressed": False,
                "suppression_reason": None,
                "is_sustained": False,
                "sustained_length": 1
            })

    anomalies = suppress_false_positives(anomalies)
    anomalies_df = pd.DataFrame(anomalies)

    if anomalies_df.empty:
        return anomalies_df, {}, cross_column_anomalies, distribution_profiles, zero_value_anomalies, volume_anomalies, level_shift_anomalies

    anomalies_df = detect_consecutive_anomalies(anomalies_df)

    for idx, row in anomalies_df.iterrows():
        if row["is_sustained"]:
            if row["severity"] == "Medium":
                anomalies_df.at[idx, "severity"] = "High"
            elif row["severity"] == "High":
                anomalies_df.at[idx, "severity"] = "Critical"

    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Normal": 3}
    confidence_order = {"Very High": 0, "High": 1, "Moderate": 2, "Low": 3}

    anomalies_df["severity_rank"] = anomalies_df["severity"].map(severity_order)
    anomalies_df["confidence_rank"] = anomalies_df["confidence"].map(confidence_order)
    anomalies_df = anomalies_df.sort_values(
        ["severity_rank", "confidence_rank", "methods_triggered"],
        ascending=[True, True, False]
    ).drop(columns=["severity_rank", "confidence_rank"])
    anomalies_df = anomalies_df.reset_index(drop=True)

    trend_summary = {}
    for col in anomalies_df["column"].unique():
        col_anomaly_rows = anomalies_df[anomalies_df["column"] == col]["row_index"].tolist()
        if col in df.columns:
            direction = detect_trend_direction(df[col], col_anomaly_rows)
            trend_summary[col] = {
                "total_anomalies": len(col_anomaly_rows),
                "critical_count": int(len(anomalies_df[(anomalies_df["column"] == col) & (anomalies_df["severity"] == "Critical")])),
                "high_count": int(len(anomalies_df[(anomalies_df["column"] == col) & (anomalies_df["severity"] == "High")])),
                "medium_count": int(len(anomalies_df[(anomalies_df["column"] == col) & (anomalies_df["severity"] == "Medium")])),
                "sustained_anomaly_groups": int(len(anomalies_df[(anomalies_df["column"] == col) & (anomalies_df["is_sustained"] == True)])),
                "suppressed_count": int(len(anomalies_df[(anomalies_df["column"] == col) & (anomalies_df["suppressed"] == True)])),
                "trend_direction": direction,
                "most_severe": anomalies_df[anomalies_df["column"] == col]["severity"].iloc[0],
                "highest_confidence": anomalies_df[anomalies_df["column"] == col]["confidence"].iloc[0],
                "distribution_profile": distribution_profiles.get(col, {})
            }

    return (
        anomalies_df,
        trend_summary,
        cross_column_anomalies,
        distribution_profiles,
        zero_value_anomalies,
        volume_anomalies,
        level_shift_anomalies
    )