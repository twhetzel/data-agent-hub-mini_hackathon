import pandas as pd
import altair as alt

def detect_columns(df: pd.DataFrame):
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    datetime_cols = []
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            datetime_cols.append(c)
    for c in df.columns:
        if c not in datetime_cols and df[c].dtype == object:
            try:
                parsed = pd.to_datetime(df[c], errors="raise", infer_datetime_format=True)
                na_ratio = parsed.isna().mean()
                if na_ratio < 0.2:
                    df[c] = parsed
                    datetime_cols.append(c)
            except Exception:
                pass
    cat_cols = [c for c in df.columns if c not in numeric_cols and c not in datetime_cols]
    return df, numeric_cols, cat_cols, datetime_cols

def chart_line_over_time(df, time_col, value_col):
    agg = df.groupby(time_col, as_index=False)[value_col].mean()
    return alt.Chart(agg).mark_line().encode(
        x=alt.X(time_col, title=time_col),
        y=alt.Y(value_col, title=f"Mean {value_col}")
    ).properties(height=300)

def chart_bar_top_categories(df, category_col, value_col, top_n=10, agg="mean"):
    if agg == "mean":
        agg_df = df.groupby(category_col, as_index=False)[value_col].mean()
    else:
        agg_df = df.groupby(category_col, as_index=False)[value_col].sum()
    agg_df = agg_df.sort_values(value_col, ascending=False).head(top_n)
    return alt.Chart(agg_df).mark_bar().encode(
        x=alt.X(value_col, title=f"{agg.title()} {value_col}"),
        y=alt.Y(category_col, sort='-x', title=category_col)
    ).properties(height=300)

def chart_histogram(df, value_col, bins=30):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{value_col}:Q", bin=alt.Bin(maxbins=bins), title=value_col),
        y=alt.Y('count()', title='Count')
    ).properties(height=300)

def default_dashboard(df):
    df, nums, cats, times = detect_columns(df.copy())
    charts = []
    if times and nums:
        charts.append(chart_line_over_time(df, times[0], nums[0]))
    if cats and nums:
        charts.append(chart_bar_top_categories(df, cats[0], nums[0], top_n=10))
    if nums:
        charts.append(chart_histogram(df, nums[0]))
    return charts, {"numeric": nums, "categorical": cats, "datetime": times}
