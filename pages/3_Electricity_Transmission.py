import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient


st.title("Electricity Transmission")



# Connect to MongoDB
client = MongoClient(
    st.secrets["MONGODB_URI"]
)

db = client["reservoirscope"]
collection = db["entsoe_flows"]



# Load ENTSO-E data from MongoDB
records = list(
    collection.find(
        {},
        {"_id": 0}
    )
)

transmission_df = pd.DataFrame(records)



# Check whether data is available
if transmission_df.empty:
    st.warning(
        "No electricity transmission data is currently available."
    )
    st.stop()



# Prepare data
transmission_df["timestamp"] = pd.to_datetime(
    transmission_df["timestamp"]
)

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



# Page layout
left_column, right_column = st.columns(2)


with left_column:

    st.subheader("Yearly Electricity Flow")

    selected_connection = st.radio(
        "Select connection",
        ["NO2 ↔ Netherlands"]
    )

    year_options = sorted(
        transmission_df["year"]
        .dropna()
        .unique()
    )

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

    yearly_df = transmission_df[
        transmission_df["year"] == selected_year
    ].copy()

    # ENTSO-E observations are in 15-minute intervals.
    # Convert MW to MWh by multiplying by 0.25 hours.
    yearly_totals = (
        yearly_df
        .groupby("direction", as_index=False)["quantity_mw"]
        .sum()
    )

    yearly_totals["total_mwh"] = (
        yearly_totals["quantity_mw"] * 0.25
    )

    if not yearly_totals.empty:

        fig_pie = px.pie(
            yearly_totals,
            names="direction",
            values="total_mwh",
            title=(
                f"Electricity Flow – "
                f"{selected_connection} "
                f"({selected_year})"
            ),
            color="direction",
            color_discrete_map={
                "export": "#C96B7C",
                "import": "#E6A06D"
            }
        )

        fig_pie.update_traces(
            textinfo="percent+label",
            marker=dict(
                line=dict(
                    color="white",
                    width=2
                )
            ),
            hovertemplate=(
                "Direction: %{label}"
                "<br>Total energy: %{value:,.0f} MWh"
                "<br>Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig_pie.update_layout(
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

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

    monthly_df = yearly_df[
        yearly_df["month"].isin(
            selected_month_numbers
        )
    ].sort_values("timestamp")

    if not monthly_df.empty:

        fig_line = px.line(
            monthly_df,
            x="timestamp",
            y="quantity_mw",
            color="direction",
            title=(
                f"Electricity Flow – "
                f"{selected_connection}"
            ),
            color_discrete_map={
                "export": "#C96B7C",
                "import": "#E6A06D"
            }
        )

        fig_line.update_traces(
            mode="lines",
            line=dict(width=2),
            hovertemplate=(
                "Time: %{x|%d %b %Y %H:%M}"
                "<br>Flow: %{y:.2f} MW"
                "<br>Direction: %{fullData.name}"
                "<extra></extra>"
            )
        )

        fig_line.update_layout(
            xaxis_title="Time",
            yaxis_title="Physical Flow (MW)",
            hovermode="x unified",
            height=500,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            fig_line,
            use_container_width=True
        )

    else:

        st.warning(
            "No data available for the selected month."
        )



# Data-source documentation
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