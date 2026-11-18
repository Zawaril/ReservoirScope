import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="ReservoirScope",
    layout="wide"
)

# Define pages
home_page = st.Page(
    "home.py",
    title="Home",
    default=True
)

map_page = st.Page(
    "pages/2_Interactive_Map.py",
    title="Interactive Map"
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
    title="Weather Analysis"
)

correlation_page = st.Page(
    "pages/7_Correlation.py",
    title="Weather & Reservoir Correlation"
)

forecast_page = st.Page(
    "pages/8_Forecasting.py",
    title="Reservoir Forecasting"
)

info_page = st.Page(
    "pages/6_Project_Info.py",
    title="Project Information"
)

# Group pages logically
navigation = st.navigation(
    {
        "Overview": [
            home_page,
            map_page,
            data_page
        ],

        "Exploration": [
            plot_page,
            transmission_page,
            seasonal_page
        ],

        "Data Quality & Relationships": [
            weather_page,
            correlation_page
        ],

        "Prediction": [
            forecast_page
        ],

        "Project": [
            info_page
        ]
    },
    position="sidebar"
)

navigation.run()