from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class AgentRequest(BaseModel):
    schema_description: str
    sample_rows: str

class AgentResponse(BaseModel):
    summary: str
    suggested_visuals: List[str]

@app.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    schema = req.schema_description.lower()
    visuals = []
    if "date" in schema or "time" in schema:
        visuals.append("Line chart of value over time")
    if "location" in schema or "latitude" in schema or "longitude" in schema:
        visuals.append("Map of metric by location")
    if not visuals:
        visuals = ["Bar chart of a categorical column by a numeric metric",
                   "Histogram of a numeric column"]

    summary = (
        "This dataset appears to be tabular. Group by key categorical fields and examine trends over time. "
        "Use filters for high-cardinality columns and handle missing values."
    )

    return AgentResponse(summary=summary, suggested_visuals=visuals)
