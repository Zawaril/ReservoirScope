
# ReservoirScope

ReservoirScope is an interactive reservoir data analytics dashboard built with Python, Pandas, Matplotlib, and Streamlit.

The project was developed as part of the **IND320 – Data to Decision** course and focuses on exploring Norwegian reservoir data through preprocessing, exploratory analysis, interactive filtering, and time-series visualisation.

## Features

- Load and preprocess reservoir data from CSV
- Rename Norwegian variables to descriptive English labels
- Explore the dataset in an interactive table
- Display first-month data series with Streamlit line-chart columns
- Select individual reservoir measurements using a drop-down menu
- Filter observations by month range
- Visualise national reservoir measurements over time
- Normalise variables for multi-series comparison
- Handle constant variables during normalisation
- Cache data loading for improved application performance
- Navigate through a multi-page Streamlit interface

## Project Structure

```text
ReservoirScope/
├── app.py
├── home.py
├── reservoirs.csv
├── ReservoirScope.ipynb
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── 1_Data_table.py
│   ├── 2_Data_plot.py
│   └── 3_Project_Info.py
└── README.md
```

## Technologies

- **Python**
- **Pandas**
- **Matplotlib**
- **Streamlit**
- **Jupyter Notebook**
- **Git**
- **GitHub**

## Dataset

The project uses the `reservoirs.csv` dataset provided for the IND320 course.

The dataset contains Norwegian reservoir observations from 1995 to 2026, including measurements from different geographical areas.

The main measurements include:

- Reservoir fill level
- Storage capacity (TWh)
- Stored energy (TWh)
- Previous-week fill level
- Change in fill level

The interactive time-series visualisation uses national reservoir observations.

## Data Analysis

The Jupyter Notebook documents the analytical workflow used to prepare and explore the dataset.

The workflow includes:

- Dataset inspection
- Missing-value and duplicate checks
- Column renaming
- Datetime conversion
- Descriptive statistics
- Exploratory data analysis
- Individual time-series visualisations
- Aggregated reservoir measurements
- Normalised multi-variable comparison
- Monthly summaries

Min-Max normalisation is used to compare measurements with different numerical scales. Constant variables are handled separately to avoid division by zero.

## Streamlit Application

ReservoirScope contains four application pages:

1. **Home:** Introduces ReservoirScope and provides navigation.

2. **Reservoir Data:** Displays the imported dataset and first-month reservoir data series using Streamlit's `LineChartColumn()`.

3. **Reservoir Visualisation:** Provides interactive variable selection, month-range filtering, and time-series visualisation of national reservoir measurements.

4. **Project Information:** Summarises the project objectives, features, technologies, dataset, and data processing.

The application uses `st.cache_data` to improve data-loading performance.

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

Run the Streamlit application:

```bash
streamlit run app.py
```

## Live Application

The deployed Streamlit application will be available here:

**Streamlit:** https://reservoirscope.streamlit.app/

## Repository

**GitHub:** https://github.com/Zawaril/ReservoirScope

## Future Development

ReservoirScope is designed to evolve throughout the IND320 project.

Future development may include:

- Database integration
- Replacing local CSV storage with MongoDB
- Additional interactive analytics
- Expanded data visualisation
- Improved application architecture
- Additional decision-support functionality

## Author

**Jawaril Munshad Abedin**  
MSc Data Science  
Norwegian University of Life Sciences (NMBU)
