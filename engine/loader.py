import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
import re
from datetime import datetime


def handle_missing_values(df):
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    object_cols = df.select_dtypes(include="object").columns
    for col in object_cols:
        df[col].fillna("Unknown", inplace=True)
    datetime_cols = df.select_dtypes(include="datetime").columns
    for col in datetime_cols:
        df[col].fillna(df[col].median(), inplace=True)
    return df


def handle_empty_columns_rows(df):
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(axis=0, how="all", inplace=True)
    return df


def handle_duplicates(df):
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        df = df.drop_duplicates()
    return df, int(duplicate_count)


def handle_whitespace(df):
    object_cols = df.select_dtypes(include="object").columns
    for col in object_cols:
        df[col] = df[col].str.strip()
        df[col] = df[col].str.replace(r"\s+", " ", regex=True)
    return df


def handle_currency_symbols(df):
    currency_log = {}
    object_cols = df.select_dtypes(include="object").columns
    for col in object_cols:
        sample = df[col].dropna().head(100)
        currency_pattern = r"^[\$€£¥₹₩,\s\-\+\(\)%\d\.]+$"
        match_ratio = sample.str.match(currency_pattern).mean()
        if match_ratio > 0.6:
            cleaned = (
                df[col]
                .str.replace(r"[\$€£¥₹₩]", "", regex=True)
                .str.replace(r",", "", regex=True)
                .str.replace(r"%", "", regex=True)
                .str.replace(r"\((\d+\.?\d*)\)", r"-\1", regex=True)
                .str.strip()
            )
            converted = pd.to_numeric(cleaned, errors="coerce")
            success_rate = converted.notna().mean()
            if success_rate > 0.7:
                original_sample = df[col].iloc[0] if len(df[col]) > 0 else ""
                df[col] = converted
                currency_log[col] = {
                    "original_sample": str(original_sample),
                    "action": "Stripped currency/unit symbols and converted to numeric"
                }
    return df, currency_log


def handle_mixed_data_types(df):
    mixed_log = {}
    object_cols = df.select_dtypes(include="object").columns
    for col in object_cols:
        converted = pd.to_numeric(df[col], errors="coerce")
        success_rate = converted.notna().sum() / df[col].notna().sum() if df[col].notna().sum() > 0 else 0
        if success_rate > 0.7:
            failed_mask = df[col].notna() & converted.isna()
            failed_values = df[col][failed_mask].unique().tolist()[:10]
            df[col] = converted
            mixed_log[col] = {
                "converted": True,
                "success_rate": round(success_rate * 100, 1),
                "failed_values": failed_values,
                "action": f"Converted to numeric — {round(success_rate * 100, 1)}% success"
            }
    return df, mixed_log


def handle_category_inconsistency(df):
    object_cols = df.select_dtypes(include="object").columns
    standardization_log = {}
    for col in object_cols:
        unique_values = df[col].dropna().unique().tolist()
        if len(unique_values) < 2 or len(unique_values) > 200:
            continue
        mapping = {}
        visited = set()
        for value in unique_values:
            if value in visited:
                continue
            matches = process.extract(
                value,
                unique_values,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=85
            )
            similar_values = [match[0] for match in matches]
            if len(similar_values) > 1:
                most_common = (
                    df[col][df[col].isin(similar_values)]
                    .value_counts()
                    .idxmax()
                )
                for v in similar_values:
                    visited.add(v)
                    if v != most_common:
                        mapping[v] = most_common
        if mapping:
            standardization_log[col] = mapping
            df[col] = df[col].map(lambda x: mapping.get(x, x))
    return df, standardization_log


def handle_numeric_dates(df):
    converted_cols = []
    for col in df.select_dtypes(include="number").columns:
        col_values = df[col].dropna()
        if len(col_values) == 0:
            continue
        # Skip year-only columns
        if col_values.between(1900, 2100).mean() > 0.9 and col_values.nunique() <= 200:
            continue
        if col_values.between(19000101, 20991231).mean() > 0.8:
            try:
                df[col] = pd.to_datetime(df[col].astype(str), format="%Y%m%d")
                converted_cols.append({"column": col, "format": "YYYYMMDD"})
                continue
            except:
                pass
        if col_values.between(40000, 50000).mean() > 0.8:
            try:
                df[col] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df[col], unit="D")
                converted_cols.append({"column": col, "format": "Excel serial"})
                continue
            except:
                pass
        if col_values.between(1000000000, 9999999999).mean() > 0.8:
            try:
                df[col] = pd.to_datetime(df[col], unit="s")
                converted_cols.append({"column": col, "format": "Unix timestamp"})
                continue
            except:
                pass
    return df, converted_cols


def handle_data_entry_outliers(df):
    outlier_log = {}
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) < 10:
            continue
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        lower_fence = Q1 - (3.5 * IQR)
        upper_fence = Q3 + (3.5 * IQR)
        suspected_typos = df[(df[col] < lower_fence) | (df[col] > upper_fence)][col]
        if len(suspected_typos) > 0 and len(suspected_typos) / len(col_data) < 0.02:
            outlier_log[col] = {
                "count": len(suspected_typos),
                "values": suspected_typos.tolist()[:5],
                "lower_fence": round(lower_fence, 2),
                "upper_fence": round(upper_fence, 2),
                "action": "Flagged as suspected data entry errors"
            }
    return outlier_log


def handle_negative_values(df):
    negative_log = {}
    numeric_cols = df.select_dtypes(include="number").columns
    strictly_positive_keywords = [
        "price", "revenue", "sales", "cost", "amount", "quantity",
        "qty", "count", "age", "population", "units", "orders",
        "profit", "income", "salary", "stock", "inventory"
    ]
    for col in numeric_cols:
        col_lower = col.lower()
        is_strictly_positive = any(keyword in col_lower for keyword in strictly_positive_keywords)
        if is_strictly_positive:
            negative_mask = df[col] < 0
            negative_count = negative_mask.sum()
            if negative_count > 0:
                negative_log[col] = {
                    "count": int(negative_count),
                    "values": df[col][negative_mask].tolist()[:5],
                    "action": "Negative values found in a column that should be strictly positive"
                }
    return negative_log


def handle_future_dates(df):
    future_date_log = {}
    today = pd.Timestamp(datetime.today().date())
    datetime_cols = df.select_dtypes(include="datetime").columns
    for col in datetime_cols:
        future_mask = df[col] > today
        future_count = future_mask.sum()
        if future_count > 0:
            future_date_log[col] = {
                "count": int(future_count),
                "values": df[col][future_mask].dt.strftime("%Y-%m-%d").tolist()[:5],
                "action": "Future dates detected — may be data entry errors"
            }
    return future_date_log


def handle_duplicate_columns(df):
    duplicate_col_log = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) < 2:
        return duplicate_col_log
    checked_pairs = set()
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col_a = numeric_cols[i]
            col_b = numeric_cols[j]
            pair = tuple(sorted([col_a, col_b]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)
            try:
                correlation = df[col_a].corr(df[col_b])
                if abs(correlation) >= 0.98:
                    duplicate_col_log.append({
                        "column_a": col_a,
                        "column_b": col_b,
                        "correlation": round(abs(correlation), 4),
                        "action": "Columns are 98%+ correlated — may be duplicates"
                    })
            except:
                continue
    return duplicate_col_log


def flag_suspicious_columns(df):
    warnings = []
    for col in df.columns:
        reason = None
        if df[col].dtype == object:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.95 and len(df) > 20:
                reason = "95% unique values — possibly an ID column or corrupted data"
        if pd.api.types.is_numeric_dtype(df[col]):
            missing_ratio = df[col].isna().sum() / len(df)
            if missing_ratio > 0.6:
                reason = f"{round(missing_ratio * 100)}% values missing — column data may be unreliable"
        if pd.api.types.is_numeric_dtype(df[col]):
            col_values = df[col].dropna()
            if len(col_values) > 0:
                if col_values.between(19000101, 20991231).mean() > 0.8:
                    reason = "Values look like YYYYMMDD format — possibly a date column stored as number"
                elif col_values.between(40000, 50000).mean() > 0.8:
                    reason = "Values look like Excel serial dates — possibly a date column stored as number"
                elif col_values.between(1000000000, 9999999999).mean() > 0.8:
                    reason = "Values look like Unix timestamps — possibly a date column stored as number"
        if reason:
            warnings.append({"column": col, "reason": reason})
    return warnings


def filter_flag_columns(df, metric_cols):
    flag_keywords = [
        "flag", "status", "code", "type", "indicator",
        "label", "tag", "class", "group", "rank", "level",
        "grade", "tier", "band", "bin", "bucket"
    ]
    filtered = []
    flag_cols = []
    for col in metric_cols:
        col_lower = col.lower()
        is_flag = any(keyword in col_lower for keyword in flag_keywords)
        if is_flag:
            flag_cols.append(col)
            continue
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
        unique_ratio = col_data.nunique() / len(col_data)
        try:
            max_val = col_data.max()
            min_val = col_data.min()
            value_range = max_val - min_val
            if unique_ratio < 0.01 and value_range <= 10:
                flag_cols.append(col)
                continue
        except:
            pass
        filtered.append(col)
    return filtered, flag_cols


def detect_columns(df):
    df, numeric_date_log = handle_numeric_dates(df)

    time_keywords = ["date", "week", "month", "year", "period", "time", "day", "quarter", "timestamp", "created", "updated"]
    time_col = None

    for col in df.columns:
        if any(keyword in col.lower() for keyword in time_keywords):
            if pd.api.types.is_numeric_dtype(df[col]):
                col_values = df[col].dropna()
                if len(col_values) > 0 and col_values.between(1900, 2100).mean() > 0.9:
                    time_col = col
                    break
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().mean() > 0.7:
                    df[col] = converted
                    time_col = col
                    break
            except:
                continue

    if time_col is None:
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                time_col = col
                break

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    dimension_cols = df.select_dtypes(include="object").columns.tolist()

    if time_col and time_col in numeric_cols:
        numeric_cols.remove(time_col)
    if time_col and time_col in dimension_cols:
        dimension_cols.remove(time_col)

    numeric_cols, flag_cols = filter_flag_columns(df, numeric_cols)

    return df, {
        "time_col": time_col,
        "metric_cols": numeric_cols,
        "dimension_cols": dimension_cols,
        "flag_cols": flag_cols
    }


def load_file(uploaded_file):
    file_name = uploaded_file.name

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Upload CSV or Excel only.")

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df = handle_empty_columns_rows(df)
    df = handle_whitespace(df)
    df, currency_log = handle_currency_symbols(df)
    df, mixed_log = handle_mixed_data_types(df)
    df, duplicate_count = handle_duplicates(df)
    df, standardization_log = handle_category_inconsistency(df)
    df = handle_missing_values(df)

    outlier_log = handle_data_entry_outliers(df)
    negative_log = handle_negative_values(df)
    future_date_log = handle_future_dates(df)
    duplicate_col_log = handle_duplicate_columns(df)
    suspicious_columns = flag_suspicious_columns(df)

    quality_report = {
        "duplicate_rows_removed": duplicate_count,
        "currency_columns_cleaned": currency_log,
        "mixed_type_columns_fixed": mixed_log,
        "categories_standardized": standardization_log,
        "suspected_data_entry_outliers": outlier_log,
        "negative_value_warnings": negative_log,
        "future_date_warnings": future_date_log,
        "duplicate_column_warnings": duplicate_col_log,
        "suspicious_column_warnings": suspicious_columns
    }

    return df, quality_report