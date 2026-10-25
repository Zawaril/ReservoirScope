import streamlit as st
import pandas as pd

from nve_api import load_nve_data


st.title("Reservoir Data")


# Load the prepared dataset directly from the NVE API.
reservoirs_df = load_nve_data()

# Sort the dataset by date.
reservoirs_df = reservoirs_df.sort_values("date")


st.subheader("Select Area Type")

selected_area_type = st.radio(
    "Area type",
    ["EL", "NO", "VASS"],
    horizontal=True
)


# Filter the dataset based on the selected area type.
filtered_df = reservoirs_df[
    reservoirs_df["area_type"] == selected_area_type
].copy()


# Find the available area numbers for the selected area type.
area_numbers = sorted(
    int(number)
    for number in filtered_df["area_number"]
    .dropna()
    .unique()
)


st.subheader("Imported Reservoir Dataset")

st.write(
    "The reservoir dataset retrieved directly from the NVE "
    "Magasinstatistikk API after basic preprocessing."
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# Find the earliest date in the filtered dataset.
first_date = filtered_df["date"].min()

# Filter observations belonging to the first calendar month.
first_month = filtered_df[
    (filtered_df["date"].dt.year == first_date.year)
    & (filtered_df["date"].dt.month == first_date.month)
].sort_values("date")


# Create a readable first-month label.
first_month_label = first_date.strftime("%Y-%m")


# Display all observations from the first month.
st.subheader(
    f"Data from {first_month_label}"
)

st.write(
    "The table below shows all observations recorded during "
    "the first month available for the selected area type."
)

st.dataframe(
    first_month,
    use_container_width=True,
    hide_index=True
)


# Continuous reservoir measurement columns.
plot_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "previous_week_fill_level",
    "change_in_fill_level",
]


# Clear display names for the table.
display_names = {
    "fill_level": "Filling level",
    "capacity_TWh": "Capacity (TWh)",
    "stored_energy_TWh": "Stored Energy (TWh)",
    "previous_week_fill_level": "Filling level previous week",
    "change_in_fill_level": "Change in filling level",
}


# Create one row for each area number.
table_rows = []

for area_number, group in first_month.groupby(
    "area_number"
):

    group = group.sort_values("date")

    row = {
        "Area number": int(area_number)
    }

    for column in plot_columns:

        row[
            display_names[column]
        ] = (
            group[column]
            .dropna()
            .tolist()
        )

    table_rows.append(row)


# Create the sparkline table.
table_data = pd.DataFrame(
    table_rows
)


st.subheader(
    "Reservoir Measurements During the First Month"
)

st.write(
    """
    Each row represents an area number associated with the
    selected area type. The sparklines show how the main
    reservoir measurements changed during the first available month.
    """
)


# Determine useful limits for the sparkline columns.
capacity_max = first_month[
    "capacity_TWh"
].max()

stored_energy_max = first_month[
    "stored_energy_TWh"
].max()

change_min = first_month[
    "change_in_fill_level"
].min()

change_max = first_month[
    "change_in_fill_level"
].max()


# Configure the line-chart columns.
column_config = {
    "Area number": st.column_config.NumberColumn(
        "Area number",
        width="small"
    ),

    "Filling level": st.column_config.LineChartColumn(
        "Filling level",
        y_min=0,
        y_max=1,
        color="#FF4B4B"
    ),

    "Capacity (TWh)": st.column_config.LineChartColumn(
        "Capacity (TWh)",
        y_min=0,
        y_max=max(
            float(capacity_max) * 1.1,
            1.0
        ),
        color="#FF4B4B"
    ),

    "Stored Energy (TWh)": st.column_config.LineChartColumn(
        "Stored Energy (TWh)",
        y_min=0,
        y_max=max(
            float(stored_energy_max) * 1.1,
            1.0
        ),
        color="#FF4B4B"
    ),

    "Filling level previous week":
        st.column_config.LineChartColumn(
            "Filling level previous week",
            y_min=0,
            y_max=1,
            color="#FF4B4B"
        ),

    "Change in filling level":
        st.column_config.LineChartColumn(
            "Change in filling level",
            y_min=float(change_min),
            y_max=float(change_max),
            color="#FF4B4B"
        ),
}


# Display the first-month measurements.
st.dataframe(
    table_data,
    column_config=column_config,
    hide_index=True,
    use_container_width=True
)