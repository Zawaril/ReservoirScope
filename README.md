# ReservoirScope

ReservoirScope is an interactive reservoir data analytics dashboard built with Python, Pandas, Matplotlib, and Streamlit.

The project was developed as part of the **IND320 – Data to Decision** course and focuses on exploring Norwegian reservoir data through preprocessing, exploratory analysis, interactive filtering, and time-series visualisation.

## Features

- Load and preprocess reservoir data from CSV
- Rename Norwegian variables to descriptive English labels
- Explore the dataset in an interactive table
- Display first-month data series with Streamlit line-chart columns
- Select individual reservoir variables using a drop-down menu
- Filter observations by month range
- Compare reservoir measurements over time
- Normalise variables for multi-series comparison
- Cache data loading for improved application performance
- Navigate through a multi-page Streamlit interface

## Project Structure

```text
ReservoirScope/
├── app.py
├── reservoirs.csv
├── ReservoirScope.ipynb
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── 1_Data_Table.py
│   ├── 2_Data_Plot.py
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

## Data Analysis

The Jupyter Notebook documents the analytical workflow used to prepare the data for the application.

The workflow includes:

- dataset inspection
- missing-value and duplicate checks
- column renaming
- datetime conversion
- descriptive statistics
- exploratory data analysis
- individual time-series visualisations
- aggregated reservoir measurements
- normalised multi-variable comparison
- monthly summaries

## Streamlit Application

ReservoirScope contains four application pages:

1. **Home**  
   Introduction to the ReservoirScope project.

2. **Reservoir Data**  
   Displays the imported dataset and first-month reservoir data series.

3. **Reservoir Visualisation**  
   Provides interactive variable selection, month-range filtering, and time-series plots.

4. **Project Information**  
   Summarises the project objectives, features, technologies, and structure.

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

**Streamlit:** *Add deployment URL*

## Repository

**GitHub:** https://github.com/Zawaril/ReservoirScope

## Future Development

ReservoirScope is designed to evolve throughout the IND320 project.

Future development may include:

- database integration
- replacing local CSV storage with MongoDB
- additional interactive analytics
- expanded data visualisation
- improved application architecture
- additional decision-support functionality

## Author

**Jawaril Munshad Abedin**  
MSc Data Science  
Norwegian University of Life Sciences (NMBU)