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
    # SUPER simple rule-based suggestions based on schema text
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
        "This dataset appears to be tabular with columns inferred from the schema. "
        "Consider grouping by key categorical fields and examining trends over time or across regions. "
        "Use filters for high-cardinality columns and handle missing values as noted."
    )

    return AgentResponse(summary=summary, suggested_visuals=visuals)
