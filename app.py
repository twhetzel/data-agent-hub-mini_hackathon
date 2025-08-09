import os
import streamlit as st
import pandas as pd
import requests

from utils.schema_utils import infer_schema

st.set_page_config(page_title="Data Agent Hub — Mini", page_icon="🧠")
st.title("🧠 Data Agent Hub — Mini")

endpoint = os.getenv("FREESTYLE_ENDPOINT", "http://localhost:8000/agent")
st.caption(f"Agent endpoint: {endpoint}")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Sample Data")
    st.dataframe(df.head())

    schema_str, sample_str = infer_schema(df)

    with st.expander("🔎 Inferred Schema", expanded=True):
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
            st.stop()

    st.subheader("🧾 Agent Summary")
    st.write(output.get("summary", ""))

    st.subheader("📊 Suggested Visualizations")
    viz = output.get("suggested_visuals", [])
    if isinstance(viz, list):
        for v in viz:
            st.markdown(f"- {v}")
    else:
        st.write(viz)

else:
    st.info("Upload a CSV to begin.")