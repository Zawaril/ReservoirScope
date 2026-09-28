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
    - Visualise national reservoir measurements over time
    - Compare multiple reservoir variables using Min-Max normalisation
    - Handle constant variables during normalisation
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
    The application uses the reservoirs.csv dataset provided for the
    IND320 project.

    The dataset contains reservoir observations from different geographical
    areas, including fill level, storage capacity, stored energy,
    previous-week fill level, and changes in fill level.

    The Reservoir Data page displays the imported dataset and first-month
    measurements from the available geographical areas.

    The Reservoir Visualisation page uses national reservoir observations
    to explore changes over time.
    """
)


st.header("Data Processing")

st.write(
    """
    The reservoir dataset is loaded using Pandas and cached using
    Streamlit to improve application performance.

    The original Norwegian column names are translated into English,
    and the observation dates are converted into datetime format.

    For the interactive visualisation, national reservoir observations
    are selected and organised chronologically.

    The selected measurements are grouped by observation date to
    obtain one value per date.

    When all measurement variables are displayed together,
    Min-Max normalisation is applied to make variables with
    different numerical scales easier to compare.

    Variables with constant values are assigned a normalised
    value of 0.5 for visualisation purposes.
    """
)


st.header("Application Structure")

st.markdown(
    """
    ReservoirScope currently contains four pages:

    1. **Home** – introduction to the project
    2. **Reservoir Data** – imported dataset and first-month data series
    3. **Reservoir Visualisation** – interactive time-series exploration
    4. **Project Information** – project overview and documentation
    """
)


st.header("Project Repository")

st.markdown(
    "[View ReservoirScope on GitHub](https://github.com/Zawaril/ReservoirScope)"
)

st.header("Live Application")

st.markdown(
    "[Open ReservoirScope](https://reservoirscope.streamlit.app/)"
)