import streamlit as st

st.set_page_config(
    page_title="ReservoirScope",
    page_icon="💧",
    layout="wide"
)

st.title("💧 ReservoirScope")
st.subheader("Interactive Reservoir Data Analytics Dashboard")

st.write(
    """
    ReservoirScope is a Streamlit-based data analytics application
    for exploring and visualising reservoir data.

    Use the sidebar to navigate between the different sections
    of the application.
    """
)