import os, json, io, re
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml

# --- LLM client (OpenAI) ---
from openai import OpenAI

# Read env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # pick your model

# Paths
YAML_PATH = os.getenv("FREESTYLE_YAML", "freestyle/data_ui_agent.yaml")

# App
app = FastAPI(title="Local Freestyle Runner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Request / Response models (same as your UI expects)
class AgentRequest(BaseModel):
    schema_description: str
    sample_rows: str

class AgentResponse(BaseModel):
    summary: str
    suggested_visuals: List[str]
    chart_specs: List[Dict[str, Any]]

# --- Utilities ---
def load_agent_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_prompt(agent_cfg: Dict[str, Any], payload: AgentRequest) -> str:
    # Use your tuned YAML fields
    instructions = agent_cfg.get("instructions", "").strip()
    prompt_tmpl  = agent_cfg.get("prompt", "").strip()

    # Fill the simple jinja-style vars the YAML expects
    prompt = prompt_tmpl.replace("{{schema_description}}", payload.schema_description)
    prompt = prompt.replace("{{sample_rows}}", payload.sample_rows)

    # Wrap with a strict directive to return only JSON
    strict = (
        "Return ONLY a single JSON object with keys: "
        '"summary", "suggested_visuals", "chart_specs". '
        "Do not include markdown fences or extra text.\n"
    )
    return f"{instructions}\n\n{strict}\n{prompt}"

def extract_json(text: str) -> Dict[str, Any]:
    # Best effort: find the first { ... } block
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    raise ValueError("Could not parse JSON from model response")

# --- Level 0: deterministic fallback (no LLM) ---
def fallback_response(payload: AgentRequest) -> AgentResponse:
    # Minimal, safe default so you can debug end-to-end without an LLM
    # Produces a single bar chart if it sees 'Location' and 'DataValue'
    import csv
    reader = csv.DictReader(io.StringIO(payload.sample_rows))
    rows = list(reader)
    values = rows if rows else []
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {"values": values},
        "mark": "bar",
        "encoding": {
            "x": {"field": "Location", "type": "nominal", "title": "Location"},
            "y": {"field": "DataValue", "type": "quantitative", "title": "DataValue"},
            "tooltip": [
                {"field": "Location", "type": "nominal"},
                {"field": "DataValue", "type": "quantitative"}
            ]
        },
        "height": 300
    }
    return AgentResponse(
        summary="Fallback summary (no LLM).",
        suggested_visuals=["Bar chart of Location vs DataValue"],
        chart_specs=[spec] if values else []
    )

# --- Level 1: LLM-backed ---
def llm_response(agent_cfg: Dict[str, Any], payload: AgentRequest) -> AgentResponse:
    if not OPENAI_API_KEY:
        # No key? fall back deterministically
        return fallback_response(payload)

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = build_prompt(agent_cfg, payload)

    # System content: keep it minimal; YAML 'description' is a good fit
    system = agent_cfg.get("description", "You are a data visualization agent.")
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    text = completion.choices[0].message.content
    data = extract_json(text)

    # Validate minimal contract
    summary = data.get("summary", "")
    suggested = data.get("suggested_visuals", [])
    specs = data.get("chart_specs", [])
    if not isinstance(suggested, list): suggested = []
    if not isinstance(specs, list): specs = []

    return AgentResponse(summary=summary, suggested_visuals=suggested, chart_specs=specs)

# --- Routes ---
@app.get("/health")
def health():
    return {"ok": True, "yaml": YAML_PATH, "model": OPENAI_MODEL}

@app.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    agent_cfg = load_agent_yaml(YAML_PATH)

    # Toggle levels with an env var for easy debugging
    level = os.getenv("FREESTYLE_LEVEL", "1")  # "0" = fallback only, "1" = LLM
    if level == "0":
        return fallback_response(req)

    return llm_response(agent_cfg, req)
