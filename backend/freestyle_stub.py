from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import csv, io
import pandas as pd

# Local Freestyle-like stub with the same HTTP contract

app = FastAPI(title="Freestyle Local Stub")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    schema_description: str
    sample_rows: str

class AgentResponse(BaseModel):
    summary: str
    suggested_visuals: List[str]
    chart_specs: List[Dict[str, Any]]

def parse_rows(csv_text: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(csv_text))
    return df

def infer_types(df: pd.DataFrame):
    datetime_cols, numeric_cols, categorical_cols = [], [], []
    df2 = df.copy()
    for col in df2.columns:
        if df2[col].dtype == object:
            try:
                parsed = pd.to_datetime(df2[col], errors="raise", infer_datetime_format=True)
                df2[col] = parsed
            except Exception:
                pass
        if pd.api.types.is_datetime64_any_dtype(df2[col]):
            datetime_cols.append(col)
            continue
        ser = pd.to_numeric(df2[col], errors="coerce")
        non_na_ratio = ser.notna().mean()
        if non_na_ratio >= 0.6:
            df2[col] = ser
            numeric_cols.append(col)
        else:
            if col not in datetime_cols:
                categorical_cols.append(col)
    return df2, datetime_cols, numeric_cols, categorical_cols

def vega_bar(values, cat_col, num_col):
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": values},
        "mark": "bar",
        "encoding": {
            "x": {"field": cat_col, "type": "nominal", "title": cat_col},
            "y": {"field": num_col, "type": "quantitative", "title": num_col},
            "tooltip": [
                {"field": cat_col, "type": "nominal"},
                {"field": num_col, "type": "quantitative"}
            ]
        },
        "height": 300
    }

def vega_line(values, time_col, num_col):
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": values},
        "mark": "line",
        "encoding": {
            "x": {"field": time_col, "type": "temporal", "title": time_col},
            "y": {"field": num_col, "type": "quantitative", "title": num_col},
            "tooltip": [
                {"field": time_col, "type": "temporal"},
                {"field": num_col, "type": "quantitative"}
            ]
        },
        "height": 300
    }

def coerce_values_for_spec(df: pd.DataFrame):
    return df.to_dict(orient="records")

@app.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    try:
        df = parse_rows(req.sample_rows)
    except Exception:
        reader = csv.DictReader(io.StringIO(req.sample_rows))
        import pandas as pd
        df = pd.DataFrame(list(reader))

    df2, time_cols, num_cols, cat_cols = infer_types(df)

    visuals = []
    specs: List[Dict[str, Any]] = []
    values = coerce_values_for_spec(df2)

    if time_cols and num_cols:
        tcol, ncol = time_cols[0], num_cols[0]
        visuals.append("Line chart of numeric metric over time")
        specs.append(vega_line(values, tcol, ncol))

    if cat_cols and num_cols:
        ccol, ncol = cat_cols[0], num_cols[0]
        visuals.append("Bar chart of category vs numeric metric")
        specs.append(vega_bar(values, ccol, ncol))

    if not visuals:
        visuals = ["Histogram of a numeric column (not implemented in stub)", "Bar chart of counts by category"]

    rows, cols = df.shape
    summary = (
        f"Detected {cols} columns and {rows} rows. "
        f"Temporal: {time_cols or 'none'}, Numeric: {num_cols or 'none'}, Categorical: {cat_cols or 'none'}. "
        "Generated chart specs based on the detected column types."
    )

    return {"summary": summary, "suggested_visuals": visuals, "chart_specs": specs}
