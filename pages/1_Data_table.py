import streamlit as st
import pandas as pd

from nve_api import load_nve_data


st.title("Reservoir Data")


# Load the prepared dataset directly from the NVE API.
reservoirs_df = load_nve_data()

# Sort the dataset by date.
reservoirs_df = reservoirs_df.sort_values(
    "date"
)


st.subheader("Select Area Type")

selected_area_type = st.radio(
    "Area type",
    [
        "EL",
        "NO",
        "VASS"
    ],
    horizontal=True
)


# Filter the dataset based on the selected area type.
filtered_df = reservoirs_df[
    reservoirs_df[
        "area_type"
    ] == selected_area_type
].copy()


# Find the available area numbers for the selected area type.
area_numbers = sorted(
    int(number)
    for number in (
        filtered_df[
            "area_number"
        ]
        .dropna()
        .unique()
    )
)


st.subheader(
    "Imported Reservoir Dataset"
)

st.write(
    "The reservoir dataset retrieved directly from the NVE "
    "Magasinstatistikk API after basic preprocessing."
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# Select a date range for the LineChartColumn table.
st.subheader(
    "Select Date Range"
)

min_date = (
    filtered_df[
        "date"
    ]
    .min()
    .date()
)

max_date = (
    filtered_df[
        "date"
    ]
    .max()
    .date()
)

selected_dates = st.date_input(
    "Date range",
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)


# Streamlit may temporarily return only one date
# while the user is selecting the range.
if (
    isinstance(
        selected_dates,
        tuple
    )
    and len(
        selected_dates
    ) == 2
):

    start_date, end_date = (
        selected_dates
    )

else:

    st.info(
        "Please select both a start date "
        "and an end date."
    )

    st.stop()


# Filter the dataset to the selected date range.
date_filtered_df = filtered_df[
    (
        filtered_df[
            "date"
        ].dt.date
        >= start_date
    )
    &
    (
        filtered_df[
            "date"
        ].dt.date
        <= end_date
    )
].copy()


st.subheader(
    f"Reservoir Measurements from "
    f"{start_date} to {end_date}"
)

st.write(
    """
    Each row represents an area number associated with the
    selected area type. The sparklines show how the main
    reservoir measurements changed during the selected
    date range.
    """
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
    "fill_level":
        "Filling level",

    "capacity_TWh":
        "Capacity (TWh)",

    "stored_energy_TWh":
        "Stored Energy (TWh)",

    "previous_week_fill_level":
        "Filling level previous week",

    "change_in_fill_level":
        "Change in filling level",
}


# Create one row for each area number.
table_rows = []

for area_number, group in (
    date_filtered_df
    .groupby(
        "area_number"
    )
):

    group = group.sort_values(
        "date"
    )

    row = {
        "Area number":
            int(
                area_number
            )
    }

    for column in plot_columns:

        row[
            display_names[
                column
            ]
        ] = (
            group[
                column
            ]
            .dropna()
            .tolist()
        )

    table_rows.append(
        row
    )


# Create the sparkline table.
table_data = pd.DataFrame(
    table_rows
)


# Check whether data exists for the selected period.
if table_data.empty:

    st.warning(
        "No reservoir observations were found "
        "for the selected date range."
    )

    st.stop()


# Determine useful limits for the sparkline columns.
capacity_max = (
    date_filtered_df[
        "capacity_TWh"
    ]
    .max()
)

stored_energy_max = (
    date_filtered_df[
        "stored_energy_TWh"
    ]
    .max()
)

change_min = (
    date_filtered_df[
        "change_in_fill_level"
    ]
    .min()
)

change_max = (
    date_filtered_df[
        "change_in_fill_level"
    ]
    .max()
)


# Protect against missing values.
capacity_max = (
    float(
        capacity_max
    )
    if pd.notna(
        capacity_max
    )
    else 1.0
)

stored_energy_max = (
    float(
        stored_energy_max
    )
    if pd.notna(
        stored_energy_max
    )
    else 1.0
)

change_min = (
    float(
        change_min
    )
    if pd.notna(
        change_min
    )
    else -1.0
)

change_max = (
    float(
        change_max
    )
    if pd.notna(
        change_max
    )
    else 1.0
)


# Avoid identical minimum and maximum values.
if change_min == change_max:

    change_min -= 0.1

    change_max += 0.1


# Configure the line-chart columns.
column_config = {
    "Area number":
        st.column_config.NumberColumn(
            "Area number",
            width="small"
        ),

    "Filling level":
        st.column_config.LineChartColumn(
            "Filling level",
            y_min=0,
            y_max=1,
            color="#FF4B4B"
        ),

    "Capacity (TWh)":
        st.column_config.LineChartColumn(
            "Capacity (TWh)",
            y_min=0,
            y_max=max(
                capacity_max
                * 1.1,
                1.0
            ),
            color="#FF4B4B"
        ),

    "Stored Energy (TWh)":
        st.column_config.LineChartColumn(
            "Stored Energy (TWh)",
            y_min=0,
            y_max=max(
                stored_energy_max
                * 1.1,
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
            y_min=change_min,
            y_max=change_max,
            color="#FF4B4B"
        ),
}


# Display the measurements for the selected date range.
st.dataframe(
    table_data,
    column_config=column_config,
    hide_index=True,
    use_container_width=True
)