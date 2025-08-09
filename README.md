# Data Agent Hub — Mini (Freestyle + Streamlit)

This is a minimal, hackathon-ready prototype that:
1) Uploads a CSV in Streamlit
2) Infers a schema (dtype + missing % + samples)
3) Sends schema + sample rows to a **Freestyle agent**
4) Displays the agent's summary and suggested visualizations

## Quick Start

### 1) Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) (Option A) Run a mock agent locally (no Freestyle required)
```bash
uvicorn backend.mock_agent:app --port 8000 --reload
```
This exposes `POST http://localhost:8000/agent` with a simple rule-based response.

### 2) (Option B) Use a real Freestyle agent
- Make sure your Freestyle runtime exposes an HTTP endpoint receiving JSON:
  ```json
  {
    "schema_description": "...",
    "sample_rows": "..."
  }
  ```
  and returning JSON:
  ```json
  {
    "summary": "...",
    "suggested_visuals": ["...", "..."]
  }
  ```
- Update `FREESTYLE_ENDPOINT` in your environment (defaults to `http://localhost:8000/agent`).

### 3) Run the app
```bash
streamlit run app.py
```

Upload the sample CSV in `data/chronic_disease.csv` or your own file.

## Files
- `app.py` — Streamlit UI
- `utils/schema_utils.py` — schema inference helper
- `freestyle/data_ui_agent.yaml` — Freestyle agent definition (example)
- `backend/mock_agent.py` — a simple FastAPI mock to simulate the agent
- `data/chronic_disease.csv` — tiny sample dataset
- `requirements.txt` — deps

## Notes
- For the hackathon, point the app at your **Freestyle** (or Same.new-hosted) agent.
- The mock agent is just for local testing.
