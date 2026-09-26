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
    return pd.read_csv(DATA_PATH)

reservoirs_df = load_data()

st.write("The imported reservoir dataset:")
st.dataframe(reservoirs_df.head())