import streamlit as st


# Main Page Title
st.title("ReservoirScope")

st.subheader(
    "Interactive Reservoir and Electricity Data Analytics Dashboard"
)

st.write(
    """
    ReservoirScope is a Streamlit-based data analytics application
    for exploring Norwegian reservoir statistics and cross-border
    electricity transmission data.

    The application combines data from the NVE Magasinstatistikk API
    and the ENTSO-E Transparency Platform with Spark, Cassandra,
    MongoDB, and interactive Streamlit visualisations.

    Use the sidebar to navigate between the different sections
    of the application.
    """
)

st.markdown("**IND320 - Data to Decision**")
st.write("Compulsory Project Work")