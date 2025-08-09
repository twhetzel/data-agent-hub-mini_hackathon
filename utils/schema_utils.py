def infer_schema(df):
    # Build a concise schema description
    lines = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        na_pct = float(df[col].isna().mean() * 100.0)
        # Simple sample values
        sample_vals = df[col].dropna().unique()[:3]
        sample_str = ", ".join(map(str, sample_vals))
        lines.append(f"{col} ({dtype}) - Missing: {na_pct:.1f}% - Samples: {sample_str}")
    schema_str = "\n".join(lines)
    sample_rows = df.head(10).to_csv(index=False)
    return schema_str, sample_rows
