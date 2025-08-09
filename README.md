# Data Agent Hub Mini App

## Overview
Data Agent Hub is a Streamlit + FastAPI demo that takes a dataset, extracts schema information, and uses an AI agent to summarize the dataset and suggest or generate visualizations.

## Running the App

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start your chosen backend agent in one terminal tab:
```bash
# Mock Agent
uvicorn backend.mock_agent:app --port 8000 --reload

# OR

# Freestyle Stub
uvicorn backend.freestyle_stub:app --port 8001 --reload
```

4. Start the Streamlit UI in another tab:
```bash
streamlit run app.py
```

## 🔄 Switching Agent Backends On the Fly

The app includes a **sidebar Agent Backend switcher**, letting you change which backend is used without restarting.

### Available Options
- **Mock Agent (8000)**  
  Runs `backend/mock_agent.py` — returns hard-coded example outputs.  
  Start it with:  
  ```bash
  uvicorn backend.mock_agent:app --port 8000 --reload
  ```

- **Freestyle Stub (8001)**  
  Runs `backend/freestyle_stub.py` — local FastAPI stub that parses CSVs and returns dynamic chart specs.  
  Start it with:  
  ```bash
  uvicorn backend.freestyle_stub:app --port 8001 --reload
  ```

- **Custom…**  
  Enter the URL of a hosted Freestyle agent endpoint.

### Running Multiple Backends at Once
1. Open **two terminal tabs**:
   - **Tab 1** → Mock Agent  
     ```bash
     source .venv/bin/activate
     uvicorn backend.mock_agent:app --port 8000 --reload
     ```
   - **Tab 2** → Freestyle Stub  
     ```bash
     source .venv/bin/activate
     uvicorn backend.freestyle_stub:app --port 8001 --reload
     ```

2. Open **a third tab** for the Streamlit UI:
   ```bash
   source .venv/bin/activate
   streamlit run app.py
   ```

3. In the **Streamlit sidebar**:
   - Use the **Agent Backend** dropdown to pick your backend.
   - The app will re-run automatically to use the new backend.

> 💡 Tip: Keep both agents running so you can switch instantly if one is being updated or tested.
