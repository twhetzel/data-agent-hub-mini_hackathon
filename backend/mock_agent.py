from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import csv
import io

app = FastAPI()

class AgentRequest(BaseModel):
    schema_description: str
    sample_rows: str

class AgentResponse(BaseModel):
    summary: str
    suggested_visuals: List[str]
    chart_specs: List[Dict[str, Any]]

def parse_sample_rows(csv_text: str):
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        return rows
    except csv.Exception:
        return []

def coerce_numeric(value: str):
    try:
        if value is None:
            return None
        v = float(value)
        return v
    except Exception:
        return value

def detect_columns(rows: List[dict]):
    if not rows:
        return [], [], []
    columns = list(rows[0].keys())
    # detect numeric by trying to parse first non-empty value in each column
    numeric_cols = []
    categorical_cols = []
    time_cols = []
    for col in columns:
        val = None
        for r in rows:
            if r.get(col) not in (None, ""):
                val = r[col]
                break
        if val is None:
            categorical_cols.append(col)
            continue
        lower = col.lower()
        if "date" in lower or "time" in lower:
            time_cols.append(col)
            continue
        try:
            float(val)
            numeric_cols.append(col)
        except Exception:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols, time_cols

def make_bar_spec(rows: List[dict], cat_col: str, num_col: str):
    # inline data
    # coerce numeric
    values = []
    for r in rows:
        new_r = dict(r)
        new_r[num_col] = coerce_numeric(r.get(num_col))
        values.append(new_r)
    spec = {
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
    return spec

def make_line_spec(rows: List[dict], time_col: str, num_col: str):
    values = []
    for r in rows:
        new_r = dict(r)
        new_r[num_col] = coerce_numeric(r.get(num_col))
        values.append(new_r)
    spec = {
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
    return spec

@app.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    rows = parse_sample_rows(req.sample_rows)
    numeric_cols, categorical_cols, time_cols = detect_columns(rows)

    visuals_text = []
    specs = []

    # Prefer time series if available
    if time_cols and numeric_cols:
        visuals_text.append("Line chart of numeric metric over time")
        specs.append(make_line_spec(rows, time_cols[0], numeric_cols[0]))

    # Add a bar chart if we can
    if categorical_cols and numeric_cols:
        visuals_text.append("Bar chart of category vs numeric metric")
        specs.append(make_bar_spec(rows, categorical_cols[0], numeric_cols[0]))

    # Default suggestions if we couldn't detect much
    if not visuals_text:
        visuals_text = ["Histogram of a numeric column", "Bar chart of counts by category"]

    summary = (
        "Generated chart specs based on the detected column types. "
        "If you include a date/time column and at least one numeric column, you'll get a time series. "
        "Otherwise a category vs numeric bar chart is suggested."
    )

    return AgentResponse(summary=summary, suggested_visuals=visuals_text, chart_specs=specs)
