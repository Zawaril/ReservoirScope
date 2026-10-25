import streamlit as st

st.title("About ReservoirScope")

st.write(
    """
    ReservoirScope is an interactive data analytics application developed
    as part of the IND320 – Data to Decision course.

    The project explores Norwegian reservoir data and cross-border
    electricity transmission data using Python, Pandas, Matplotlib,
    Streamlit, Spark, Cassandra, MongoDB, and GitHub.
    """
)


st.header("Project Objective")

st.write(
    """
    The purpose of ReservoirScope is to make Norwegian reservoir and
    electricity transmission data easier to explore and understand through
    interactive visualisation and filtering.

    The application allows users to inspect reservoir observations,
    compare reservoir measurements, explore geographical areas, and
    analyse cross-border electricity flows involving Norway.
    """
)


st.header("Features")

st.markdown(
    """
    - Retrieve reservoir data directly from the NVE Magasinstatistikk API
    - Rename Norwegian variables to descriptive English labels
    - Explore reservoir measurements in tabular form
    - Select geographical area types using EL, NO, and VASS
    - Explore the area numbers associated with each area type
    - Display first-month data series using Streamlit line-chart columns
    - Select individual reservoir variables using a drop-down menu
    - Filter reservoir observations by month range
    - Compare multiple reservoir variables using Min-Max normalisation
    - Handle constant variables during normalisation
    - Retrieve cross-border electricity transmission data from ENTSO-E
    - Store electricity transmission data in Cassandra using Spark
    - Process relevant transmission data using Spark
    - Store prepared data in MongoDB
    - Use MongoDB data in the Streamlit application
    - Cache API data loading for improved application performance
    """
)


st.header("Technologies Used")

st.markdown(
    """
    - **Python** – application development
    - **Pandas** – data processing and preprocessing
    - **Matplotlib** – data visualisation
    - **Streamlit** – interactive web application
    - **NVE API** – Norwegian reservoir statistics
    - **ENTSO-E API** – European cross-border electricity transmission data
    - **Apache Spark** – distributed data processing
    - **Apache Cassandra** – local storage of transmission data
    - **MongoDB Atlas** – remote curated-data storage
    - **Jupyter Notebook** – analysis and project documentation
    - **GitHub** – version control and source-code hosting
    """
)


st.header("Data Sources")

st.write(
    """
    Reservoir data is retrieved directly from the NVE Magasinstatistikk API.

    The NVE dataset contains reservoir observations from different
    geographical areas, including fill level, storage capacity, stored
    energy, previous-week fill level, and changes in fill level.

    The application supports the NVE area types EL, NO, and VASS and
    allows users to explore the area numbers associated with each type.

    Cross-border electricity transmission data is obtained from the
    ENTSO-E Transparency Platform. This data is used to analyse
    electricity flowing into and out of Norway.
    """
)


st.header("Data Processing")

st.write(
    """
    Reservoir data is retrieved from the NVE API and converted into a
    Pandas DataFrame.

    The original Norwegian column names are translated into English,
    and observation dates are converted into datetime format.

    Users can select geographical area types and associated area numbers
    before exploring the reservoir measurements.

    When all measurement variables are displayed together, Min-Max
    normalisation is applied to make variables with different numerical
    scales easier to compare.

    Variables with constant values are assigned a normalised value of
    0.5 for visualisation purposes.

    ENTSO-E electricity transmission data is stored in Cassandra using
    Spark. Relevant fields are extracted and processed using Spark before
    the curated data is transferred to MongoDB for use in the Streamlit
    application.
    """
)


st.header("Application Structure")

st.markdown(
    """
    ReservoirScope contains pages for:

    1. **Home** – introduction to the project
    2. **Reservoir Data** – NVE API data and first-month measurement series
    3. **Reservoir Visualisation** – interactive reservoir time-series exploration
    4. **Electricity Transmission** – ENTSO-E and MongoDB analysis
    5. **Project Information** – project overview and documentation
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