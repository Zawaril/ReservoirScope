import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient


st.title("Electricity Transmission")


# Connect to MongoDB using Streamlit secrets.
client = MongoClient(
    st.secrets["MONGODB_URI"]
)

db = client["reservoirscope"]

collection = db["entsoe_flows"]


# Load ENTSO-E data from MongoDB.
records = list(
    collection.find(
        {},
        {"_id": 0}
    )
)

transmission_df = pd.DataFrame(records)


# Check whether data is available.
if transmission_df.empty:
    st.warning(
        "No electricity transmission data is currently available."
    )
    st.stop()


# Convert timestamp to datetime.
transmission_df["timestamp"] = pd.to_datetime(
    transmission_df["timestamp"]
)


# Create year and month variables from timestamp.
transmission_df["year"] = (
    transmission_df["timestamp"].dt.year
)

transmission_df["month"] = (
    transmission_df["timestamp"].dt.month
)


st.write(
    """
    This page explores cross-border electricity transmission
    between the Norwegian NO2 bidding zone and the Netherlands
    using ENTSO-E data stored in MongoDB.
    """
)


# Split the page into two columns.
left_column, right_column = st.columns(2)


with left_column:

    st.subheader("Yearly Electricity Flow")

    # Select connection.
    selected_connection = st.radio(
        "Select connection",
        ["NO2 ↔ Netherlands"]
    )


    # Find available years.
    year_options = sorted(
        transmission_df["year"]
        .dropna()
        .unique()
    )


    # Use 2025 as the default full calendar year when available.
    default_year_index = (
        year_options.index(2025)
        if 2025 in year_options
        else 0
    )


    selected_year = st.selectbox(
        "Select year",
        year_options,
        index=default_year_index
    )


    # Filter observations for the selected year.
    yearly_df = transmission_df[
        transmission_df["year"]
        == selected_year
    ].copy()


    # Calculate total energy by direction.
    # ENTSO-E observations are reported at 15-minute intervals,
    # therefore MW values are multiplied by 0.25 hours to obtain MWh.
    yearly_totals = (
        yearly_df
        .groupby("direction")["quantity_mw"]
        .sum()
        * 0.25
    )


    # Create pie chart.
    if not yearly_totals.empty:

        fig_pie, ax_pie = plt.subplots(
            figsize=(6, 6)
        )

        # Warm colors selected to match the Streamlit theme.
        pie_colors = [
            "#C96B7C",
            "#E6A06D"
        ]

        ax_pie.pie(
            yearly_totals.values,
            labels=yearly_totals.index,
            autopct="%1.1f%%",
            colors=pie_colors,
            startangle=90,
            wedgeprops={
                "edgecolor": "white",
                "linewidth": 2
            },
            textprops={
                "fontsize": 11
            }
        )

        ax_pie.set_title(
            f"Electricity Flow – "
            f"{selected_connection} "
            f"({selected_year})"
        )

        st.pyplot(fig_pie)

        plt.close(fig_pie)

    else:

        st.warning(
            "No data available for the selected year."
        )


with right_column:

    st.subheader("Monthly Electricity Flow")


    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }


    # Find available months for the selected year.
    available_month_numbers = sorted(
        yearly_df["month"]
        .dropna()
        .unique()
    )


    available_month_names = [
        month_names[month_number]
        for month_number in available_month_numbers
    ]


    selected_months = st.pills(
        "Select month",
        available_month_names,
        selection_mode="multi"
    )


    # Show the first available month by default.
    if not selected_months:

        selected_months = [
            available_month_names[0]
        ]


    selected_month_numbers = [
        month_number
        for month_number, month_name
        in month_names.items()
        if month_name in selected_months
    ]


    # Filter observations for selected months.
    monthly_df = yearly_df[
        yearly_df["month"].isin(
            selected_month_numbers
        )
    ].sort_values(
        "timestamp"
    )


    # Create line plot.
    if not monthly_df.empty:

        fig_line, ax_line = plt.subplots(
            figsize=(10, 6)
        )


        # Line colors matching the warm application theme.
        direction_colors = {
            "export": "#C96B7C",
            "import": "#E6A06D"
        }


        for direction in (
            monthly_df["direction"].unique()
        ):

            direction_df = monthly_df[
                monthly_df["direction"]
                == direction
            ]

            ax_line.plot(
                direction_df["timestamp"],
                direction_df["quantity_mw"],
                label=direction,
                color=direction_colors.get(
                    direction
                ),
                linewidth=2
            )


        ax_line.set_title(
            f"Electricity Flow – "
            f"{selected_connection}"
        )

        ax_line.set_xlabel(
            "Time"
        )

        ax_line.set_ylabel(
            "Physical Flow (MW)"
        )

        ax_line.legend()

        ax_line.grid(
            alpha=0.3
        )

        fig_line.autofmt_xdate()

        fig_line.tight_layout()

        st.pyplot(fig_line)

        plt.close(fig_line)

    else:

        st.warning(
            "No data available for the selected month."
        )


# Data-source documentation.
with st.expander("About the Data Source"):

    st.write(
        """
        Cross-border physical flow data is obtained from the
        ENTSO-E Transparency Platform.

        The analysis focuses on electricity exchanged between
        the Norwegian NO2 bidding zone and the Netherlands.

        Both import and export directions are included.

        The ENTSO-E data is processed using Spark and stored
        in Cassandra. The relevant data is then transferred
        to MongoDB for use in this Streamlit application.

        The yearly pie chart presents total energy in MWh.
        Because the observations are reported at 15-minute
        intervals, the MW values are multiplied by 0.25 hours.

        The monthly line plot displays physical electricity
        flow in MW over time.
        """
    )