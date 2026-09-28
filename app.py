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

info_page = st.Page(
    "pages/3_Project_Info.py",
    title="Project Information"
)

# Configure sidebar navigation
navigation = st.navigation(
    [home_page, data_page, plot_page, info_page],
    position="sidebar"
)

# Run the selected page
navigation.run()