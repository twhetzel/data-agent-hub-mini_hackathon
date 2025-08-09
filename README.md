# Data Agent Hub — Mini (Freestyle + Streamlit)

This mini app:
1) Uploads a CSV
2) Infers schema
3) Calls a Freestyle-style agent endpoint
4) Builds **local dashboards** automatically (Altair)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run mock agent (local testing)
```bash
uvicorn backend.mock_agent:app --port 8000 --reload
```

### Run UI
```bash
streamlit run app.py
```

### Use a real agent
Set the endpoint:
```bash
export FREESTYLE_ENDPOINT="https://your-agent/agent"
```


## Agent-generated charts (Vega-Lite / Altair specs)
- The mock agent now returns `chart_specs` (Vega-Lite JSON). The UI renders them via `st.vega_lite_chart`.
- When you swap in a real Freestyle agent, have it return the same `chart_specs` structure.
