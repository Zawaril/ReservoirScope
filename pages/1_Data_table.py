import streamlit as st
import pandas as pd
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to reservoirs.csv in the project root
DATA_PATH = BASE_DIR/"reservoirs.csv"

st.title("Reservoir Data")

@st.cache_data
def load_data():
    "Load the local reservoir CSV file."
    
    reservoirs_df = pd.read_csv(DATA_PATH)
    
    # renaming columns
    reservoirs_df = reservoirs_df.rename(
        columns = {
            "dato_Id": "date",
            "omrType": "area_type",
            "omrnr": "area_number",
            "iso_aar": "year",
            "iso_uke": "week",
            "fyllingsgrad": "fill_level",
            "kapasitet_TWh": "capacity_TWh",
            "fylling_TWh": "stored_energy_TWh",
            "neste_Publiseringsdato": "next_publication_date",
            "fyllingsgrad_forrige_uke": "previous_week_fill_level",
            "endring_fyllingsgrad": "change_in_fill_level",
            
        }
    )
    
    # changing date column dtype to datetime
    reservoirs_df["date"] = pd.to_datetime(reservoirs_df["date"])
    
    # Extract minimum date from "date" column
    first_date = reservoirs_df["date"].min()
    
    first_month = reservoirs_df[
        (reservoirs_df["date"].dt.year == first_date.year)
        & (reservoirs_df["date"].dt.month == first_date.month)
    ]
    
    # Extracting numeric columns
    numeric_columns = 
    [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "previous_week_fill_level",
    "change_in_fill_level",
    ]
    
    table_data = pd.DataFrame
    (
        {
            "Variable": numeric_columns,
            "First Month": [
                first_month[column].tolist()
                for column in numeric_columns
                ]
            }
        )
    st.dataframe(
        table_data,
        column_config={
            "First Month": st.column_config.LineChartColumn(
                "First Month"
            )
        },
        hide_index = True,
        use_container_width= True
    )
    
    
    return reservoirs_df

reservoirs_df = load_data()

st.write("The imported reservoir dataset (after preprocessing):")
st.dataframe(reservoirs_df.head())