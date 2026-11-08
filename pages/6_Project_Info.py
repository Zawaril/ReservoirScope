import streamlit as st


st.title("About ReservoirScope")

st.write(
    """
    ReservoirScope is an interactive data analytics application developed
    as part of the IND320 – Data to Decision course.

    The project explores Norwegian reservoir data, cross-border
    electricity transmission data, and historical weather data using
    Python, Pandas, Matplotlib, Streamlit, Spark, Cassandra, MongoDB,
    GeoPandas, SciPy, scikit-learn, statsmodels, and GitHub.
    """
)


st.header("Project Objective")

st.write(
    """
    The purpose of ReservoirScope is to make Norwegian reservoir,
    electricity transmission, and weather data easier to explore and
    understand through interactive visualisation and analysis.

    The application allows users to inspect reservoir observations,
    compare reservoir measurements, explore geographical areas,
    analyse cross-border electricity flows involving Norway, and
    investigate weather outliers and seasonal reservoir behaviour.
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
    - Retrieve historical ERA5 weather data directly from Open-Meteo
    - Analyse weather for EL, NO, and VASS geographical selections
    - Detect precipitation outliers using DCT and robust SPC limits
    - Detect temperature anomalies using Local Outlier Factor
    - Decompose reservoir filling levels using STL
    - Analyse reservoir frequency behaviour using spectrograms
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
    - **Open-Meteo API** – historical ERA5 weather data
    - **GeoPandas** – geographical polygon and coordinate processing
    - **SciPy** – DCT and spectrogram analysis
    - **scikit-learn** – Local Outlier Factor anomaly detection
    - **statsmodels** – STL decomposition
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
    Reservoir data is retrieved directly from the NVE
    Magasinstatistikk API.

    The NVE dataset contains reservoir observations from different
    geographical areas, including fill level, storage capacity,
    stored energy, previous-week fill level, and changes in fill level.

    The application supports the NVE area types EL, NO, and VASS and
    allows users to explore the area numbers associated with each type.

    Cross-border electricity transmission data is obtained from the
    ENTSO-E Transparency Platform. This data is used to analyse
    electricity flowing into and out of Norway.
    """
)

st.write(
    """
    Historical hourly temperature and precipitation data is retrieved
    from the Open-Meteo Historical Weather API using the ERA5 model.

    NVE geographical polygon data is used to define Norwegian
    electricity bidding areas and weather regions. Random locations
    sampled inside these polygons are used for the weather analysis.
    """
)


st.header("Data Processing")

st.write(
    """
    Reservoir data is retrieved from the NVE API and converted into a
    Pandas DataFrame.

    The original Norwegian column names are translated into English,
    and observation dates are converted into datetime format.

    Users can select geographical area types and associated area
    numbers before exploring the reservoir measurements.

    When all measurement variables are displayed together, Min-Max
    normalisation is applied to make variables with different numerical
    scales easier to compare.

    Variables with constant values are assigned a normalised value of
    0.5 for visualisation purposes.

    ENTSO-E electricity transmission data is stored in Cassandra using
    Spark. Relevant fields are extracted and processed using Spark
    before the curated data is transferred to MongoDB for use in the
    Streamlit application.
    """
)

st.write(
    """
    For weather analysis, geographical polygons are projected before
    random locations are sampled inside each area. The sampled
    coordinates are converted to latitude and longitude for use with
    the Open-Meteo API.

    Weather locations are pooled in batches when requesting ERA5
    temperature and precipitation data. The downloaded observations are
    averaged across the selected locations before statistical analysis.

    Precipitation is analysed using the Discrete Cosine Transform and
    robust Statistical Process Control boundaries. Temperature
    anomalies are detected using Local Outlier Factor.

    Reservoir filling-level data is further analysed using STL
    decomposition and spectrogram analysis.
    """
)


st.header("Application Structure")

st.markdown(
    """
    ReservoirScope contains pages for:

    1. **Home** – introduction to the project
    2. **Reservoir Data** – NVE API data and reservoir measurements
    3. **Reservoir Visualisation** – interactive reservoir time-series exploration
    4. **Electricity Transmission** – ENTSO-E and MongoDB analysis
    5. **Seasonal Analysis** – STL decomposition and spectrogram analysis
    6. **Weather Outliers and Anomalies** – precipitation SPC and temperature LOF analysis
    7. **Project Information** – project overview and documentation
    """
)


st.header("Part 3 – Weather and Time-Series Analysis")

st.write(
    """
    Part 3 extends ReservoirScope with historical ERA5 weather data
    from Open-Meteo and additional reservoir time-series analysis.

    The application now includes:

    - Randomly sampled weather locations for Norwegian electricity
      bidding areas and NVE weather regions.
    - Historical ERA5 temperature and precipitation data retrieved
      directly from the Open-Meteo API.
    - Precipitation outlier detection using a Discrete Cosine
      Transform and robust Statistical Process Control limits.
    - Temperature anomaly detection using Local Outlier Factor.
    - STL decomposition of reservoir filling levels.
    - Spectrogram analysis of reservoir filling-level data.
    """
)


st.subheader("Weather Region Mapping")

st.write(
    """
    The NVE weather regions are combined as required for
    Magasinstatistikk:

    - VASS 1: East (RS + RØ)
    - VASS 2: West (RV)
    - VASS 3: North (RM + RN)

    Electricity-area analysis uses NO1–NO5 directly.

    For national weather analysis, sampled locations from the broad
    East, West, and North weather regions are combined.
    """
)


st.header("Project Repository")

st.markdown(
    "[View ReservoirScope on GitHub]"
    "(https://github.com/Zawaril/ReservoirScope)"
)


st.header("Live Application")

st.markdown(
    "[Open ReservoirScope]"
    "(https://reservoirscope.streamlit.app/)"
)