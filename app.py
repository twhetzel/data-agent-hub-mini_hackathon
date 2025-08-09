import os
import streamlit as st
import pandas as pd
import requests
import altair as alt

from utils.schema_utils import infer_schema
from utils.viz_utils import default_dashboard, detect_columns, chart_line_over_time, chart_bar_top_categories, chart_histogram

st.set_page_config(page_title="Data Agent Hub — Mini", page_icon="🧠", layout="wide")
st.title("🧠 Data Agent Hub — Mini")

# --- Agent endpoint switcher (sidebar) ---
import os
DEFAULTS = {
    "Mock Agent (8000)": "http://localhost:8000/agent",
    "Freestyle Stub (8001)": "http://localhost:8001/agent",
    "Local Freestyle Runner (8002)": "http://localhost:8002/agent",
    "Hosted Freestyle (3000)": "http://localhost:3000/agent",
    "Custom…": "",
}

with st.sidebar:
    st.header("Agent Backend")
    choice = st.selectbox("Target", list(DEFAULTS.keys()), index=2)
    if choice == "Custom…":
        endpoint = st.text_input("Endpoint URL", os.getenv("FREESTYLE_ENDPOINT", "http://localhost:8002/agent"))
    else:
        endpoint = DEFAULTS[choice]
    st.caption(f"Using: {endpoint}")



# endpoint = os.getenv("FREESTYLE_ENDPOINT", "http://localhost:8000/agent")
st.caption(f"Agent endpoint: {endpoint}")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Sample Data")
    st.dataframe(df.head(), use_container_width=True)

    schema_str, sample_str = infer_schema(df)

    with st.expander("🔎 Inferred Schema", expanded=False):
        st.text(schema_str)

    with st.spinner("Calling agent..."):
        try:
            response = requests.post(endpoint, json={
                "schema_description": schema_str,
                "sample_rows": sample_str
            }, timeout=60)
            response.raise_for_status()
            output = response.json()
        except Exception as e:
            st.error(f"Agent call failed: {e}")
            output = {"summary": "", "suggested_visuals": []}

    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("🧾 Agent Summary")
        st.write(output.get("summary", ""))

    with col2:
        st.subheader("🧭 Suggested Visualizations")
    st.subheader("🗺️ Agent-Generated Charts")
    specs = output.get("chart_specs", [])
    if isinstance(specs, list) and specs:
        for i, spec in enumerate(specs, 1):
            st.caption(f"Chart {i}")
            st.vega_lite_chart(spec, use_container_width=True)
    else:
        st.info("No chart specs returned by the agent (yet).")

        viz = output.get("suggested_visuals", [])
        if isinstance(viz, list):
            for v in viz:
                st.markdown(f"- {v}")
        else:
            st.write(viz)

    st.markdown("---")
    st.header("📊 Auto Dashboard (Local)")

    charts, col_info = default_dashboard(df)
    if charts:
        for ch in charts:
            st.altair_chart(ch, use_container_width=True)
    else:
        st.info("Couldn't infer chart candidates. Try a dataset with numeric/date columns.")

    with st.expander("🔧 Build a Custom Chart"):
        df2, nums, cats, times = detect_columns(df.copy())
        chart_type = st.selectbox("Chart type", ["Line over time", "Bar by category", "Histogram"])
        if chart_type == "Line over time":
            if times and nums:
                tcol = st.selectbox("Time column", times, index=0)
                vcol = st.selectbox("Value column", nums, index=0)
                st.altair_chart(chart_line_over_time(df2, tcol, vcol), use_container_width=True)
            else:
                st.warning("No datetime and numeric columns detected.")
        elif chart_type == "Bar by category":
            if cats and nums:
                ccol = st.selectbox("Category column", cats, index=0)
                vcol = st.selectbox("Value column", nums, index=0)
                agg = st.selectbox("Aggregation", ["mean", "sum"], index=0)
                st.altair_chart(chart_bar_top_categories(df2, ccol, vcol, top_n=10, agg=agg), use_container_width=True)
            else:
                st.warning("Need at least one categorical and one numeric column.")
        else:
            if nums:
                vcol = st.selectbox("Value column", nums, index=0)
                bins = st.slider("Bins", 5, 60, 30)
                st.altair_chart(chart_histogram(df2, vcol, bins=bins), use_container_width=True)
            else:
                st.warning("Need at least one numeric column.")
else:
    st.info("Upload a CSV to begin.")
