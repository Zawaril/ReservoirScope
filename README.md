# ReservoirScope

ReservoirScope is an interactive data analytics dashboard developed with Python, Pandas, PySpark, Cassandra, MongoDB, Matplotlib, and Streamlit.

The project was developed as part of the **IND320 – Data to Decision** course at the Norwegian University of Life Sciences (NMBU). It focuses on exploring Norwegian reservoir statistics and cross-border electricity transmission through API-based data collection, distributed data processing, database integration, and interactive visualisation.

## Features

- Retrieve Norwegian reservoir statistics directly from the NVE Magasinstatistikk API
- Explore reservoir data for the area types `EL`, `NO`, and `VASS`
- Display reservoir measurements using Streamlit `LineChartColumn()`
- Filter and visualise reservoir observations interactively
- Compare multiple reservoir variables through normalised time-series plots
- Retrieve cross-border physical electricity flow data from the ENTSO-E Transparency Platform
- Process ENTSO-E data using Apache Spark
- Store cross-border electricity data locally in Cassandra
- Extract curated data from Cassandra using Spark
- Transfer prepared data to MongoDB Atlas
- Access MongoDB directly from the deployed Streamlit application
- Compare electricity imports and exports using a yearly pie chart
- Select one or more months using Streamlit pills and explore electricity flow over time
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
├── notebooks/
│   ├── ReservoirScope_CA1.ipynb
│   └── ReservoirScope_CA2.ipynb
└── pages/
    ├── 1_Data_table.py
    ├── 2_Data_plot.py
    ├── 3_Electricity_Transmission.py
    └── 4_Project_Info.py
```

Local Streamlit secrets are stored separately in:

```text
.streamlit/secrets.toml
```

This file is excluded from GitHub through `.gitignore`.

## Technologies

- **Python**
- **Pandas**
- **PySpark**
- **Apache Spark**
- **Apache Cassandra**
- **MongoDB Atlas**
- **PyMongo**
- **ENTSO-E API**
- **NVE Magasinstatistikk API**
- **Matplotlib**
- **Streamlit**
- **Jupyter Notebook**
- **Docker**
- **Git**
- **GitHub**

## Data Sources

### NVE Magasinstatistikk API

Reservoir statistics are retrieved directly from the official NVE Magasinstatistikk API.

The data include observations for different Norwegian area classifications:

- `EL`
- `NO`
- `VASS`

The main reservoir measurements include:

- Reservoir fill level
- Storage capacity (TWh)
- Stored energy (TWh)
- Previous-week fill level
- Change in fill level

The earlier CSV-based workflow from Part 1 was replaced with a direct API connection.

### ENTSO-E Transparency Platform

Cross-border electricity transmission data are retrieved from the ENTSO-E Transparency Platform.

The current analysis focuses on the connection between:

- **NO2 – Norway**
- **Netherlands**

Both import and export directions are included.

The project uses approximately two years of cross-border physical flow data.

ENTSO-E observations are reported at 15-minute intervals. For yearly energy calculations, physical flow values in MW are multiplied by `0.25` hours to obtain MWh.

## Data Pipeline

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

Cassandra is used as the local database for storing ENTSO-E cross-border physical flow data.

Spark is used to:

- Create the ENTSO-E DataFrame
- Insert data into Cassandra
- Read the stored data back from Cassandra
- Extract relevant columns
- Perform SQL-based filtering and aggregation

### MongoDB Atlas

The curated Spark data are transferred to MongoDB Atlas.

The Streamlit application accesses the MongoDB database directly when displaying electricity transmission data.

MongoDB credentials are stored securely using Streamlit secrets and are not included in the GitHub repository.

## Jupyter Notebook

The project notebooks document the full analytical and data-engineering workflow.

The current notebooks are:

```text
notebooks/ReservoirScope_CA1.ipynb
notebooks/ReservoirScope_CA2.ipynb
```

The Part 2 notebook includes:

- NVE API data retrieval
- Reservoir data preprocessing
- Reservoir exploratory analysis
- Reservoir time-series visualisation
- ENTSO-E API retrieval
- Spark DataFrame creation
- Spark–Cassandra connection testing
- Cassandra data storage
- Spark extraction from Cassandra
- Spark SQL analysis
- Import/export pie chart
- Monthly cross-border electricity flow line plot
- MongoDB insertion
- Development log
- Description of AI usage
- Project links
- Final project conclusion

## Streamlit Application

ReservoirScope contains five application sections.

### 1. Home

Introduces ReservoirScope and provides navigation through the application.

### 2. Reservoir Data

Retrieves data directly from the NVE API.

Users can select an area type using `st.radio`:

- `EL`
- `NO`
- `VASS`

The page displays:

- The API dataset
- First-month observations
- Reservoir measurements grouped by area number
- Interactive Streamlit `LineChartColumn()` sparklines

### 3. Reservoir Visualisation

Provides interactive exploration of reservoir statistics.

Users can:

- Select an area type
- Select an associated area number
- Choose reservoir variables
- Filter observations by month range
- Display individual time-series plots
- Compare multiple normalised reservoir measurements

### 4. Electricity Transmission

Displays cross-border electricity transmission data stored in MongoDB Atlas.

The page uses `st.columns()` to divide the interface into two sections.

The left side contains:

- Connection selection using `st.radio`
- Year selection
- A yearly import/export pie chart

The right side contains:

- Month selection using `st.pills`
- A physical electricity flow line plot for the selected months

An `st.expander` below the charts documents the source and processing of the electricity data.

### 5. Project Information

Summarises:

- Project objectives
- Data sources
- Technologies
- Data pipeline
- Streamlit structure
- GitHub repository
- Live application

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

Development for Part 2 was completed on a separate GitHub branch and subsequently merged into `main`, following the IND320 project requirements.

## Current Development

ReservoirScope has evolved from a local CSV-based reservoir analysis into a multi-source data pipeline combining:

- Public APIs
- Spark processing
- Cassandra storage
- MongoDB Atlas
- Interactive Streamlit visualisation

Future project parts may extend the application with additional data sources, analytics, decision-support functionality, and improved visualisation.

## Author

**Jawaril Munshad Abedin**  
MSc Data Science  
Norwegian University of Life Sciences (NMBU)