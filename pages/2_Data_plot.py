import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from nve_api import load_nve_data


st.title("Reservoir Visualisation")


# Load the prepared dataset directly from the NVE API.
reservoirs_df = load_nve_data()

# Sort the dataset by date.
reservoirs_df = reservoirs_df.sort_values("date")


# Reservoir measurement variables suitable for time-series plotting.
measurement_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "previous_week_fill_level",
    "change_in_fill_level",
]


# Select geographical area type.
st.subheader("Select Area")

selected_area_type = st.radio(
    "Area type",
    ["EL", "NO", "VASS"],
    horizontal=True
)


# Filter observations belonging to the selected area type.
area_type_df = reservoirs_df[
    reservoirs_df["area_type"] == selected_area_type
].copy()


# Find the area numbers associated with the selected area type.
area_numbers = sorted(
    area_type_df["area_number"]
    .dropna()
    .unique()
)


# Select one of the available area numbers.
selected_area_number = st.selectbox(
    "Select area number",
    area_numbers
)


# Filter observations belonging to the selected area number.
area_df = area_type_df[
    area_type_df["area_number"] == selected_area_number
].copy()


# Create the required drop-down menu.
options = ["All Columns"] + measurement_columns

selected_column = st.selectbox(
    "Select a reservoir variable",
    options
)


# Create month options in YYYY-MM format.
month_options = sorted(
    area_df["date"]
    .dt.to_period("M")
    .astype(str)
    .unique()
)


# Select a range of months.
# By default, both ends are set to the first available month.
selected_months = st.select_slider(
    "Select month range",
    options=month_options,
    value=(month_options[0], month_options[0])
)


start_month, end_month = selected_months


# Convert the date column temporarily to YYYY-MM strings
# and filter observations within the selected month range.
month_series = (
    area_df["date"]
    .dt.to_period("M")
    .astype(str)
)

filtered_df = area_df[
    (month_series >= start_month)
    & (month_series <= end_month)
].copy()


# Calculate the mean for each date to obtain
# one time-series value per measurement.
date_mean = (
    filtered_df
    .groupby("date")[measurement_columns]
    .mean()
    .sort_index()
)


# Check whether the selected range contains observations.
if date_mean.empty:
    st.warning(
        "No reservoir data available for the selected month range."
    )
    st.stop()


# Display information about the selected geographical area.
st.write(
    f"Showing **{selected_area_type}** area type, "
    f"area number **{selected_area_number}**."
)


# Create the figure.
fig, ax = plt.subplots(figsize=(12, 6))


if selected_column == "All Columns":

    # Normalize the measurements to the range 0–1.
    column_min = date_mean.min()
    column_range = date_mean.max() - column_min

    normalized_data = (
        (date_mean - column_min)
        / column_range.replace(0, float("nan"))
    )

    # Assign 0.5 to variables with constant values.
    constant_columns = column_range[
        column_range == 0
    ].index

    normalized_data[constant_columns] = 0.5

    # Use different line styles and markers to distinguish overlapping lines.
    plot_order = [
        "capacity_TWh",
        "stored_energy_TWh",
        "previous_week_fill_level",
        "change_in_fill_level",
        "fill_level",
    ]

    line_styles = {
        "capacity_TWh": "--",
        "stored_energy_TWh": "-.",
        "previous_week_fill_level": ":",
        "change_in_fill_level": "-",
        "fill_level": "-",
    }

    markers = {
        "capacity_TWh": "s",
        "stored_energy_TWh": "^",
        "previous_week_fill_level": "D",
        "change_in_fill_level": "x",
        "fill_level": "o",
    }

    for column in plot_order:
        ax.plot(
            normalized_data.index,
            normalized_data[column],
            label=column.replace("_", " ").title(),
            linestyle=line_styles[column],
            marker=markers[column],
            markersize=5,
            linewidth=3 if column == "fill_level" else 2,
            alpha=0.8,
            zorder=5 if column == "fill_level" else 2
        )

    ax.set_title(
        f"Normalized Reservoir Measurements "
        f"({selected_area_type} {selected_area_number})"
    )

    ax.set_ylabel("Normalized Value (0–1)")
    ax.legend()

else:

    # Plot the selected variable using its original values.
    ax.plot(
        date_mean.index,
        date_mean[selected_column],
        label=selected_column.replace("_", " ").title(),
        marker="o",
        markersize=5,
        linewidth=2
    )

    ax.set_title(
        f"{selected_column.replace('_', ' ').title()} "
        f"({selected_area_type} {selected_area_number})"
    )

    ax.set_ylabel(
        selected_column.replace("_", " ").title()
    )

    ax.legend()


# Common formatting for both plot types.
ax.set_xlabel("Date")
ax.grid(alpha=0.3)

fig.autofmt_xdate()
fig.tight_layout()

# Display the Matplotlib figure in Streamlit.
st.pyplot(fig)

# Close the figure after displaying it.
plt.close(fig)