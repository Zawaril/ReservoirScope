# ReservoirScope

ReservoirScope is an interactive data analytics dashboard developed with Python, Pandas, PySpark, Cassandra, MongoDB, GeoPandas, SciPy, scikit-learn, statsmodels, Matplotlib, and Streamlit.

The project was developed as part of the **IND320 – Data to Decision** course at the Norwegian University of Life Sciences (NMBU).

ReservoirScope combines Norwegian reservoir statistics, cross-border electricity transmission data, geographical sampling, historical weather data, anomaly detection, and time-series analysis in one interactive application.

## Features

- Retrieve Norwegian reservoir statistics directly from the NVE Magasinstatistikk API
- Explore reservoir data for the area types `EL`, `NO`, and `VASS`
- Select custom date ranges for reservoir `LineChartColumn()` tables
- Display reservoir measurements grouped by area number
- Plot all area numbers belonging to a selected NVE area type
- Compare multiple reservoir variables using normalised time-series plots
- Retrieve cross-border physical electricity-flow data from the ENTSO-E Transparency Platform
- Process ENTSO-E data using Apache Spark
- Store electricity-flow data in Cassandra
- Extract and prepare data from Cassandra using Spark
- Transfer curated electricity data to MongoDB Atlas
- Access MongoDB directly from the deployed Streamlit application
- Compare electricity imports and exports using yearly pie charts
- Select one or more months using Streamlit pills and explore electricity flow over time
- Analyse reservoir filling levels using STL decomposition
- Analyse reservoir filling-level frequency behaviour using a spectrogram
- Retrieve historical ERA5 weather data directly from Open-Meteo
- Use geographical samples for electricity bidding areas and NVE weather regions
- Detect precipitation outliers using DCT high-pass filtering and robust Statistical Process Control
- Detect temperature anomalies using Local Outlier Factor
- Navigate through a multi-page Streamlit interface
- Cache API data loading for improved application performance

## Project Structure

```text
ReservoirScope/
├── app.py
├── nve_api.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   ├── elspot_coordinates.json
│   ├── weather_region_coordinates.json
│   ├── no3_hourly_summary.parquet
│   └── shapefiles/
│       ├── elspotomraader.geojson
│       └── nve_regions.geojson
├── notebooks/
│   ├── ReservoirScope_CA1.ipynb
│   ├── ReservoirScope_CA2.ipynb
│   └── ReservoirScope_CA3.ipynb
└── pages/
    ├── 1_Data_table.py
    ├── 2_Data_plot.py
    ├── 3_Electricity_Transmission.py
    ├── 4_Seasonal_Analysis.py
    ├── 5_Weather_Anomalies.py
    └── 6_Project_Info.py
```

Local Streamlit secrets are stored separately in:

```text
.streamlit/secrets.toml
```

This file is excluded from GitHub through `.gitignore`.

Large raw monthly weather files are also excluded from GitHub.

## Technologies

- **Python**
- **Pandas**
- **PySpark**
- **Apache Spark**
- **Apache Cassandra**
- **MongoDB Atlas**
- **PyMongo**
- **GeoPandas**
- **SciPy**
- **scikit-learn**
- **statsmodels**
- **ENTSO-E API**
- **NVE Magasinstatistikk API**
- **Open-Meteo ERA5 API**
- **Matplotlib**
- **Streamlit**
- **Jupyter Notebook**
- **Docker**
- **Git**
- **GitHub**

## Data Sources

### NVE Magasinstatistikk API

Reservoir statistics are retrieved directly from the official NVE Magasinstatistikk API.

The data include observations for the Norwegian area classifications:

- `EL`
- `NO`
- `VASS`

The main reservoir measurements include:

- Reservoir fill level
- Storage capacity (TWh)
- Stored energy (TWh)
- Previous-week fill level
- Change in fill level

The earlier CSV-based workflow from Part 1 has been removed. Reservoir data are now retrieved directly from the NVE API.

### ENTSO-E Transparency Platform

Cross-border electricity transmission data are retrieved from the ENTSO-E Transparency Platform.

The current analysis focuses on the connection between:

- **NO2 – Norway**
- **Netherlands**

Both import and export directions are included.

The project uses approximately two years of cross-border physical-flow data.

ENTSO-E observations are reported at 15-minute intervals. For yearly energy calculations, physical-flow values in MW are multiplied by `0.25` hours to obtain MWh.

### Open-Meteo ERA5

Historical weather data are retrieved from the Open-Meteo Archive API using the ERA5 model.

The weather analysis uses:

- Hourly temperature at 2 metres
- Hourly precipitation

The Streamlit application can retrieve weather data using geographical selections corresponding to:

- `EL`
- `NO`
- `VASS`

API calls pool multiple latitude and longitude pairs in each request to reduce the total number of requests.

Retry and backoff logic are also used to handle API rate limits.

## Geographical Sampling

Part 3 introduces geographical sampling for weather-data retrieval.

NVE polygon data are used for Norwegian electricity bidding areas and broader NVE regions.

For the broader weather regions:

- `RS` + `RØ` → East
- `RV` → West
- `RM` + `RN` → North

The polygons are projected to a metric coordinate reference system before sampling.

Random points are generated inside the polygons and then converted back to WGS84 longitude and latitude for use with Open-Meteo.

The project generated 1,000 random sample locations for each electricity bidding area and 1,000 locations for each broader weather region.

The prepared coordinates are stored in JSON files so the Streamlit application can use them directly.

## Electricity Data Pipeline

The ENTSO-E workflow follows this pipeline:

```text
ENTSO-E API
     ↓
Pandas
     ↓
Apache Spark
     ↓
Cassandra
     ↓
Spark extraction and preparation
     ↓
MongoDB Atlas
     ↓
Streamlit
```

### Cassandra

Cassandra is used as the local database for storing ENTSO-E cross-border physical-flow data.

Spark is used to:

- Create the ENTSO-E DataFrame
- Insert data into Cassandra
- Read stored data back from Cassandra
- Extract relevant columns
- Perform SQL-based filtering and aggregation

### MongoDB Atlas

The curated Spark data are transferred to MongoDB Atlas.

The Streamlit application accesses MongoDB directly when displaying electricity transmission data.

MongoDB credentials are stored securely using Streamlit secrets and are not included in the GitHub repository.

## Weather Data Processing

The weather workflow follows this structure:

```text
NVE geographical polygons
        ↓
Random coordinate sampling
        ↓
WGS84 latitude / longitude
        ↓
Open-Meteo ERA5 API
        ↓
Hourly regional averages
        ↓
Precipitation SPC / Temperature LOF
        ↓
Streamlit
```

For the complete NO3 weather analysis for 2024, 1,000 sampled locations were used.

Because 2024 is a leap year, the complete dataset contains:

- 8,784 hourly timestamps
- 8,784,000 location-level hourly observations
- 8,784 aggregated hourly regional observations

## Precipitation Outlier Detection

Precipitation outliers are detected using a combination of Discrete Cosine Transform filtering and robust Statistical Process Control.

The analysis:

1. Calculates regional hourly average precipitation
2. Applies a Discrete Cosine Transform
3. Uses low-frequency coefficients to reconstruct the slower seasonal baseline
4. Uses the high-frequency component as seasonally adjusted variation
5. Calculates robust control limits using the median and median absolute deviation
6. Reconstructs upper and lower precipitation boundaries
7. Highlights observations outside the robust SPC limits

The Streamlit application allows the user to adjust:

- DCT frequency cutoff
- Number of standard deviations used for the control limits

## Temperature Anomaly Detection

Temperature anomalies are detected using Local Outlier Factor from scikit-learn.

LOF is a density-based anomaly-detection method that compares the local density of each observation with the density of nearby observations.

The default contamination value is:

```text
0.01
```

This represents an expected anomaly proportion of approximately 1%.

The contamination level can be changed interactively in Streamlit.

## Reservoir Time-Series Analysis

### STL Decomposition

Reservoir filling-level data are analysed using Seasonal-Trend decomposition with LOESS.

The decomposition separates the signal into:

- Trend
- Seasonal component
- Residual component

The analysis uses an annual period of approximately 52 weekly observations.

The Streamlit application allows the user to adjust:

- Seasonal smoother
- Trend smoother
- Robust fitting

### Spectrogram

Reservoir filling-level data are also analysed using a spectrogram.

The spectrogram shows how frequency behaviour changes over time.

The user can adjust:

- Window length
- Window overlap

This complements STL by showing the frequency structure of the reservoir signal through time.

## Jupyter Notebooks

The project notebooks document the analytical and data-engineering workflow.

The current notebooks are:

```text
notebooks/ReservoirScope_CA1.ipynb
notebooks/ReservoirScope_CA2.ipynb
notebooks/ReservoirScope_CA3.ipynb
```

The Part 3 notebook includes:

- Loading geographical polygon data
- Creating broader weather regions
- Random geographical sampling
- Coordinate conversion to WGS84
- Open-Meteo ERA5 data retrieval
- API pooling
- Retry and backoff handling
- NO3 2024 weather-data download
- Regional hourly aggregation
- DCT precipitation filtering
- Robust Statistical Process Control
- Local Outlier Factor temperature analysis
- STL decomposition
- Spectrogram analysis
- Development log
- Description of AI usage
- Project links

## Streamlit Application

ReservoirScope contains seven application sections.

### 1. Home

Introduces ReservoirScope and provides navigation through the application.

### 2. Reservoir Data

Retrieves reservoir data directly from the NVE API.

Users can select:

- `EL`
- `NO`
- `VASS`

The page includes:

- The imported API dataset
- Custom date-range selection
- Reservoir measurements grouped by area number
- Interactive Streamlit `LineChartColumn()` sparklines

### 3. Reservoir Visualisation

Provides interactive reservoir time-series analysis.

Users can:

- Select an NVE area type
- Select a reservoir variable
- Filter observations by month range
- Display all area numbers belonging to the selected area type
- Compare reservoir areas in the same plot
- Compare multiple normalised reservoir measurements

### 4. Electricity Transmission

Displays cross-border electricity transmission data stored in MongoDB Atlas.

The page uses `st.columns()` to divide the interface into two sections.

The left section contains:

- Connection selection using `st.radio`
- Year selection
- Yearly import/export pie chart

The right section contains:

- Month selection using `st.pills`
- Physical electricity-flow time series

An `st.expander` documents the source and processing pipeline.

### 5. Seasonal Analysis

Provides two analysis tabs:

- STL Decomposition
- Spectrogram

Users can select:

- Area type
- Area number
- STL seasonal smoother
- STL trend smoother
- Robust STL fitting
- Spectrogram window length
- Spectrogram overlap

### 6. Weather Outliers and Anomalies

Retrieves historical ERA5 weather data directly from Open-Meteo.

Users can select geographical areas using:

- `EL`
- `NO`
- `VASS`

The page contains two tabs:

- Precipitation SPC
- Temperature LOF

The precipitation tab provides:

- DCT high-pass filtering
- Robust SPC boundaries
- Adjustable DCT cutoff
- Adjustable standard-deviation multiplier
- Highlighted precipitation outliers

The temperature tab provides:

- Local Outlier Factor
- Adjustable contamination
- Highlighted temperature anomalies

### 7. Project Information

Summarises:

- Project objectives
- Data sources
- Technologies
- Data-processing workflows
- Streamlit application structure
- Part 3 geographical mappings
- GitHub repository
- Live application

## Part 2 Feedback Incorporated

Feedback from Part 2 was incorporated into the Part 3 version.

The following changes were made:

- Added a custom date-range selector for the reservoir `LineChartColumn` table
- Updated reservoir visualisation so all area numbers belonging to the selected NVE area type can be displayed
- Removed the old `reservoirs.csv` file from GitHub
- Reservoir data are now retrieved directly from the NVE API

## Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/Zawaril/ReservoirScope.git
cd ReservoirScope
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a local Streamlit secrets file:

```text
.streamlit/secrets.toml
```

Add the MongoDB connection string:

```toml
MONGODB_URI = "your-mongodb-connection-string"
```

Do not commit this file to GitHub.

Run the Streamlit application:

```bash
streamlit run app.py
```

## Live Application

ReservoirScope is publicly available through Streamlit Community Cloud.

**Streamlit:**  
https://reservoirscope.streamlit.app/

The same Streamlit application URL is maintained across the different parts of the IND320 project.

## Repository

**GitHub:**  
https://github.com/Zawaril/ReservoirScope

Development for Part 3 was completed on the separate:

```text
part3-development
```

branch.

The Part 3 branch contains the weather, anomaly-detection, geographical-sampling, STL, spectrogram, and feedback-related updates.

## Development History

ReservoirScope has evolved through the IND320 project from a local reservoir-analysis application into a multi-source analytical platform.

The current application combines:

- NVE reservoir data
- ENTSO-E electricity-flow data
- Spark processing
- Cassandra storage
- MongoDB Atlas
- NVE geographical polygon data
- Random geographical sampling
- Open-Meteo ERA5 historical weather data
- Robust Statistical Process Control
- Local Outlier Factor
- STL decomposition
- Spectrogram analysis
- Interactive Streamlit visualisation

## Author

**Jawaril Munshad Abedin**  
MSc Data Science  
Norwegian University of Life Sciences (NMBU)