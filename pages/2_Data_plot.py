import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from nve_api import load_nve_data


st.title("Reservoir Visualisation")



# Load reservoir data
reservoirs_df = load_nve_data()

reservoirs_df = reservoirs_df.sort_values(
    "date"
)



# Variables available for plotting
measurement_columns = [
    "fill_level",
    "capacity_TWh",
    "stored_energy_TWh",
    "previous_week_fill_level",
    "change_in_fill_level",
]

# Area selection
st.subheader(
    "Select Area"
)


selected_area_type = st.radio(
    "Area type",
    [
        "EL",
        "NO",
        "VASS"
    ],
    horizontal=True
)


area_type_df = reservoirs_df[
    reservoirs_df[
        "area_type"
    ] == selected_area_type
].copy()


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


st.write(
    "Available area numbers:",
    area_numbers
)



# Variable selection
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



# Month range
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



# Validate selected period
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



# Plotly figure
fig = go.Figure()



# Plot all variables
if selected_column == "All Columns":

    # Mean value for each date across all area numbers.
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


  
    # Normalize variables to 0–1
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


    constant_columns = (
        column_range[
            column_range == 0
        ]
        .index
    )


    normalized_data[
        constant_columns
    ] = 0.5


    plot_order = [
        "capacity_TWh",
        "stored_energy_TWh",
        "previous_week_fill_level",
        "change_in_fill_level",
        "fill_level",
    ]


   
    # Add interactive Plotly traces
    for column in plot_order:

        fig.add_trace(
            go.Scatter(
                x=normalized_data.index,
                y=normalized_data[
                    column
                ],
                mode="lines+markers",
                name=column.replace(
                    "_",
                    " "
                ).title(),
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Normalized value: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


    fig.update_layout(
        title=(
            "Normalized Reservoir Measurements "
            f"({selected_area_type} – All Area Numbers)"
        ),
        xaxis_title="Date",
        yaxis_title="Normalized Value (0–1)",
        hovermode="x unified",
        height=650
    )


    fig.update_yaxes(
        range=[
            0,
            1
        ]
    )



# Plot one selected variable
else:

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


        fig.add_trace(
            go.Scatter(
                x=area_series.index,
                y=area_series.values,
                mode="lines+markers",
                name=(
                    f"Area {area_number}"
                ),
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Value: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


    fig.update_layout(
        title=(
            f"{selected_column.replace('_', ' ').title()} "
            f"({selected_area_type} – All Area Numbers)"
        ),
        xaxis_title="Date",
        yaxis_title=(
            selected_column
            .replace(
                "_",
                " "
            )
            .title()
        ),
        hovermode="x unified",
        height=650
    )



# Common Plotly formatting
fig.update_layout(
    legend_title_text="Series",
    margin={
        "l": 30,
        "r": 30,
        "t": 70,
        "b": 30
    }
)


fig.update_xaxes(
    rangeslider_visible=True
)



# Display Plotly chart
st.plotly_chart(
    fig,
    use_container_width=True
)