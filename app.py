import streamlit as st

# Configure the broser tab and page layout

st.set_page_config(
    
    page_title="IND320: Data to Decision"
    layout="wide"
)

# Main Page
st.title("IND320: Data to Decision")

st.write(
    """
    Welcome to my IND320 project.
    This application explores reservoir data and demonstrates
    data handling, visualisation, and interactive Streamlit features.
    
    """
    
)

st.header("Project Part 1")

st.write(
    """
    Use the navigation menu in the sidebar to explore:

    - Reservoir data
    - Interactive visualisations
    - Project information
    
    """
    
)