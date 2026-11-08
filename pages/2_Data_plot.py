import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from nve_api import load_nve_data


st.title("Reservoir Visualisation")


# Load the prepared dataset directly from the NVE API.
reservoirs_df = load_nve_data()

# Sort the dataset by date.
reservoirs_df = reservoirs_df.sort_values(
    "date"
)


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
    [
        "EL",
        "NO",
        "VASS"
    ],
    horizontal=True
)


# Filter observations belonging to the selected area type.
area_type_df = reservoirs_df[
    reservoirs_df[
        "area_type"
    ] == selected_area_type
].copy()


# Find all area numbers associated with the selected area type.
area_numbers = sorted(
    int(number)
    for number in (
        area_type_df[
            "area_number"
        ]
        .dropna()
        .unique()
    )
)


# Display the available area numbers.
st.write(
    "Available area numbers:",
    area_numbers
)


# Create the variable selector.
options = [
    "All Columns"
] + measurement_columns

selected_column = st.selectbox(
    "Select a reservoir variable",
    options
)


st.caption(
    "The NVE HentOffentligData endpoint returns the complete public "
    "dataset and does not provide start and end date parameters. "
    "ReservoirScope therefore downloads and caches the API dataset, "
    "while the month-range slider controls the interval used for "
    "analysis and visualisation."
)


# Create month options using the full selected area type.
month_options = sorted(
    area_type_df[
        "date"
    ]
    .dt.to_period(
        "M"
    )
    .astype(str)
    .unique()
)


# Select a range of months.
selected_months = st.select_slider(
    "Select month range",
    options=month_options,
    value=(
        month_options[0],
        month_options[0]
    )
)


start_month, end_month = (
    selected_months
)


# Convert dates to YYYY-MM and filter the selected range.
month_series = (
    area_type_df[
        "date"
    ]
    .dt.to_period(
        "M"
    )
    .astype(str)
)

filtered_df = area_type_df[
    (
        month_series
        >= start_month
    )
    &
    (
        month_series
        <= end_month
    )
].copy()


# Check that observations exist.
if filtered_df.empty:

    st.warning(
        "No reservoir data available for the selected month range."
    )

    st.stop()


st.write(
    f"Showing all area numbers for "
    f"**{selected_area_type}**: "
    f"{', '.join(map(str, area_numbers))}"
)


# Create the figure.
fig, ax = plt.subplots(
    figsize=(12, 6)
)


if selected_column == "All Columns":

    # Calculate mean values for each date and variable
    # across all area numbers.
    date_mean = (
        filtered_df
        .groupby(
            "date"
        )[
            measurement_columns
        ]
        .mean()
        .sort_index()
    )

    # Normalize the measurements to the range 0–1.
    column_min = (
        date_mean.min()
    )

    column_range = (
        date_mean.max()
        - column_min
    )

    normalized_data = (
        (
            date_mean
            - column_min
        )
        / column_range.replace(
            0,
            float("nan")
        )
    )

    # Assign 0.5 to variables with constant values.
    constant_columns = (
        column_range[
            column_range == 0
        ]
        .index
    )

    normalized_data[
        constant_columns
    ] = 0.5


    # Plot the normalized measurement variables.
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
            normalized_data[
                column
            ],
            label=column.replace(
                "_",
                " "
            ).title(),
            linestyle=line_styles[
                column
            ],
            marker=markers[
                column
            ],
            markersize=5,
            linewidth=(
                3
                if column
                == "fill_level"
                else 2
            ),
            alpha=0.8,
            zorder=(
                5
                if column
                == "fill_level"
                else 2
            )
        )


    ax.set_title(
        f"Normalized Reservoir Measurements "
        f"({selected_area_type} – All Area Numbers)"
    )

    ax.set_ylabel(
        "Normalized Value (0–1)"
    )

    ax.legend()


else:

    # Plot the selected measurement separately
    # for every area number.
    for area_number in area_numbers:

        area_df = filtered_df[
            filtered_df[
                "area_number"
            ] == area_number
        ].copy()

        area_series = (
            area_df
            .groupby(
                "date"
            )[
                selected_column
            ]
            .mean()
            .sort_index()
        )

        if area_series.empty:
            continue

        ax.plot(
            area_series.index,
            area_series.values,
            label=(
                f"Area {area_number}"
            ),
            marker="o",
            markersize=4,
            linewidth=2
        )


    ax.set_title(
        f"{selected_column.replace('_', ' ').title()} "
        f"({selected_area_type} – All Area Numbers)"
    )

    ax.set_ylabel(
        selected_column.replace(
            "_",
            " "
        ).title()
    )

    ax.legend(
        title="Area number"
    )


# Common formatting.
ax.set_xlabel(
    "Date"
)

ax.grid(
    alpha=0.3
)

fig.autofmt_xdate()

fig.tight_layout()


# Display the Matplotlib figure.
st.pyplot(
    fig
)

plt.close(
    fig
)