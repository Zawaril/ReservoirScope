import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="ReservoirScope",
    layout="wide"
)

# Define the application pages
home_page = st.Page(
    "home.py",
    title="Home",
    default=True
)

data_page = st.Page(
    "pages/1_Data_table.py",
    title="Reservoir Data"
)

plot_page = st.Page(
    "pages/2_Data_plot.py",
    title="Reservoir Visualisation"
)

transmission_page = st.Page(
    "pages/3_Electricity_Transmission.py",
    title="Electricity Transmission"
)

seasonal_page = st.Page(
    "pages/4_Seasonal_Analysis.py",
    title="Seasonal Analysis"
)

weather_page = st.Page(
    "pages/5_Weather_Anomalies.py",
    title="Weather Outliers and Anomalies"
)

info_page = st.Page(
    "pages/6_Project_Info.py",
    title="Project Information"
)

# Configure sidebar navigation
navigation = st.navigation(
    [
        home_page,
        data_page,
        plot_page,
        transmission_page,
        seasonal_page,
        weather_page,
        info_page
    ],
    position="sidebar"
)

# Run the selected page
navigation.run()