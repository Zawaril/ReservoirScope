import streamlit as st

st.title("About ReservoirScope")

st.write(
    """
    ReservoirScope is an interactive data analytics application developed
    as part of the IND320 – Data to Decision course.

    The project explores Norwegian reservoir data using Python, Pandas,
    Matplotlib, Streamlit, and GitHub.
    """
)

st.header("Project Objective")

st.write(
    """
    The purpose of ReservoirScope is to make reservoir data easier to
    explore and understand through interactive visualisation and filtering.

    The application allows users to inspect the dataset, compare reservoir
    measurements, and explore changes over time.
    """
)

st.header("Features")

st.markdown(
    """
    - Import and preprocess reservoir data from CSV
    - Rename Norwegian variables to descriptive English labels
    - Explore reservoir measurements in tabular form
    - Display first-month data series using Streamlit line-chart columns
    - Select individual reservoir variables using a drop-down menu
    - Filter observations by month range
    - Compare multiple reservoir variables using normalised visualisation
    - Cache data loading for improved application performance
    """
)

st.header("Technologies Used")

st.markdown(
    """
    - **Python** – application development
    - **Pandas** – data loading and preprocessing
    - **Matplotlib** – data visualisation
    - **Streamlit** – interactive web application
    - **Jupyter Notebook** – analysis and project documentation
    - **GitHub** – version control and source-code hosting
    """
)

st.header("Dataset")

st.write(
    """
    The application uses the `reservoirs.csv` dataset provided for the
    IND320 project.

    The dataset contains time-based reservoir measurements, including
    fill level, storage capacity, stored energy, previous-week fill level,
    and changes in fill level.
    """
)

st.header("Application Structure")

st.markdown(
    """
    ReservoirScope currently contains four pages:

    1. **Home** – introduction to the project
    2. **Reservoir Data** – dataset preview and first-month data series
    3. **Reservoir Visualisation** – interactive time-series exploration
    4. **Project Information** – project overview and documentation
    """
)

st.header("Project Repository")

st.markdown(
    "[View ReservoirScope on GitHub](https://github.com/Zawaril/ReservoirScope)"
)