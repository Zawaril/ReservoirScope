import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="ReservoirScope",
    layout="wide"
)

# Main Page Title
st.title("ReservoirScope")

st.subheader("Interactive Reservoir Data Analytics Dashboard")

st.write(
    """
    ReservoirScope is a Streamlit-based data analytics application
    for exploring and visualising reservoir data.

    Use the sidebar to navigate between the different sections
    of the application.
    """
)

st.markdown("### IND320 - Data to Decision")
st.write("Compulsory Project Work - Part 1")