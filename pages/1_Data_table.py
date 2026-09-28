import streamlit as st
import pandas as pd
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to reservoirs.csv in the project root
DATA_PATH = BASE_DIR / "reservoirs.csv"

st.title("Reservoir Data")


@st.cache_data
def load_data():
    """Load and prepare the local reservoir CSV file."""

    reservoirs_df = pd.read_csv(DATA_PATH)

    # Rename original Norwegian column names to clear English names.
    reservoirs_df = reservoirs_df.rename(
        columns={
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

    # Convert date columns to datetime.
    reservoirs_df["date"] = pd.to_datetime(
        reservoirs_df["date"]
    )

    reservoirs_df["next_publication_date"] = pd.to_datetime(
        reservoirs_df["next_publication_date"]
    )

    # Sort the dataset by date.
    reservoirs_df = reservoirs_df.sort_values("date")

    return reservoirs_df


# Load the prepared dataset.
reservoirs_df = load_data()


st.subheader("Imported Reservoir Dataset")

st.write(
    "The imported reservoir dataset after basic preprocessing."
)

st.dataframe(
    reservoirs_df,
    use_container_width=True,
    hide_index=True
)


# Find the earliest date in the dataset.
first_date = reservoirs_df["date"].min()

# Filter observations belonging to the first calendar month.
first_month = reservoirs_df[
    (reservoirs_df["date"].dt.year == first_date.year)
    & (reservoirs_df["date"].dt.month == first_date.month)
].sort_values("date")


# Display all observations from the first month.
st.subheader("Data from the First Month")

st.write(
    "The table below shows all observations recorded during "
    "the first month available in the dataset."
)

st.dataframe(
    first_month,
    use_container_width=True,
    hide_index=True
)


# Continuous reservoir measurement columns.
numeric_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "previous_week_fill_level",
    "change_in_fill_level",
]


# Create one row for each measurement variable.
# The second column stores the values observed during the first month.
table_data = pd.DataFrame(
    {
        "Variable": numeric_columns,
        "First Month": [
            first_month[column].tolist()
            for column in numeric_columns
        ],
    }
)


st.subheader("Reservoir Measurements During the First Month")

st.write(
    """
    The table below shows the reservoir measurement variables.
    Each sparkline represents the values observed during the
    first month available in the dataset.
    """
)



# Display the first-month measurements using line charts.
st.dataframe(
    table_data,
    column_config={
        "Variable": st.column_config.TextColumn(
            "Variable",
            width="medium"
        ),

        "First Month": st.column_config.LineChartColumn(
            "First Month",
            width="large",
            color="#C46A42"
        )
    },
    hide_index=True,
    use_container_width=True
)