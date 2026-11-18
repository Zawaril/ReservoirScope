import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from nve_api import load_nve_data


st.title("Weather & Reservoir Correlation")

st.write(
    "Explore how weekly weather variables relate to reservoir filling "
    "using selectable lag and rolling-window settings."
)



# Shared map selection
selected_area_type = st.session_state.get(
    "selected_area_type",
    "EL"
)

selected_area = st.session_state.get(
    "selected_area",
    "NO3"
)

st.info(
    f"Shared map selection: "
    f"{selected_area_type} {selected_area}"
)



# Load data
@st.cache_data
def load_weather_summary():
    weather_df = pd.read_parquet(
        "data/no3_hourly_summary.parquet"
    )

    weather_df["time"] = pd.to_datetime(
        weather_df["time"]
    )

    weekly_weather = (
        weather_df
        .set_index("time")
        .resample("W-SUN")
        .agg({
            "temperature_2m": "mean",
            "precipitation": "sum"
        })
        .rename(columns={
            "temperature_2m": "temperature_mean",
            "precipitation": "precipitation_sum"
        })
    )

    return weekly_weather


reservoir_df = load_nve_data()
weekly_weather = load_weather_summary()



# Area selector
area_type_options = [
    "EL",
    "NO",
    "VASS"
]

default_area_type = (
    selected_area_type
    if selected_area_type in area_type_options
    else "EL"
)

area_type = st.selectbox(
    "Area type",
    area_type_options,
    index=area_type_options.index(
        default_area_type
    )
)


if area_type == "EL":

    area_options = [
        "NO1",
        "NO2",
        "NO3",
        "NO4",
        "NO5"
    ]

elif area_type == "NO":

    area_options = [
        "1"
    ]

else:

    area_options = [
        "1",
        "2",
        "3"
    ]


if (
    area_type == selected_area_type
    and selected_area in area_options
):
    default_index = area_options.index(
        selected_area
    )
else:
    default_index = 0


area_number = st.selectbox(
    "Area",
    area_options,
    index=default_index
)



# Convert selected area to NVE number
if area_type == "EL":

    selected_number = int(
        area_number.replace(
            "NO",
            ""
        )
    )

else:

    selected_number = int(
        area_number
    )



# Reservoir series
reservoir_series = (
    reservoir_df[
        (
            reservoir_df["area_type"]
            == area_type
        )
        & (
            reservoir_df["area_number"]
            == selected_number
        )
    ]
    .sort_values(
        "date"
    )
    .set_index(
        "date"
    )["fill_level"]
    .dropna()
)


if reservoir_series.empty:

    st.error(
        "No reservoir data is available "
        "for the selected area."
    )

    st.stop()



# Combine reservoir and weather data
correlation_data = (
    reservoir_series
    .rename(
        "fill_level"
    )
    .to_frame()
    .join(
        weekly_weather,
        how="inner"
    )
)


if correlation_data.empty:

    st.error(
        "No overlapping reservoir and weather "
        "observations were found."
    )

    st.stop()


# Weather property selector
weather_property = st.selectbox(
    "Weather property",
    [
        "Temperature",
        "Precipitation"
    ]
)


if weather_property == "Temperature":

    weather_column = "temperature_mean"

    default_lag = 4

else:

    weather_column = "precipitation_sum"

    default_lag = 0



# Correlation controls
lag = st.slider(
    "Lag (weeks)",
    min_value=0,
    max_value=12,
    value=default_lag,
    step=1,
    help=(
        "Positive lag means the weather variable "
        "is shifted earlier relative to reservoir filling."
    )
)


window = st.slider(
    "Rolling window (weeks)",
    min_value=4,
    max_value=52,
    value=24,
    step=4
)



# Sliding window correlation
def sliding_window_correlation(
    data,
    weather_column,
    reservoir_column="fill_level",
    lag=0,
    window=24
):
    """
    Calculate rolling correlation between reservoir filling
    and a selected weather variable.
    """

    df = data[
        [
            reservoir_column,
            weather_column
        ]
    ].dropna().copy()

    df["weather_lagged"] = (
        df[weather_column]
        .shift(lag)
    )

    df["correlation"] = (
        df[reservoir_column]
        .rolling(
            window=window
        )
        .corr(
            df["weather_lagged"]
        )
    )

    return df


correlation_result = (
    sliding_window_correlation(
        data=correlation_data,
        weather_column=weather_column,
        lag=lag,
        window=window
    )
)


plot_data = (
    correlation_result
    .dropna(
        subset=[
            "correlation"
        ]
    )
)



# Summary metrics
if plot_data.empty:

    st.warning(
        "There are not enough observations for "
        "the selected lag and window settings."
    )

    st.stop()


col1, col2, col3 = st.columns(
    3
)

col1.metric(
    "Mean correlation",
    f"{plot_data['correlation'].mean():.2f}"
)

col2.metric(
    "Minimum correlation",
    f"{plot_data['correlation'].min():.2f}"
)

col3.metric(
    "Maximum correlation",
    f"{plot_data['correlation'].max():.2f}"
)



# Plotly correlation chart
fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=plot_data.index,
        y=plot_data["correlation"],
        mode="lines",
        name="Rolling correlation",
        hovertemplate=(
            "%{x|%d %b %Y}"
            "<br>Correlation: %{y:.3f}"
            "<extra></extra>"
        )
    )
)


fig.add_hline(
    y=0,
    line_dash="dash"
)


fig.update_layout(
    title=(
        f"{weather_property} vs Reservoir Filling "
        f"– {area_type} {area_number}"
    ),
    xaxis_title="Date",
    yaxis_title="Correlation",
    hovermode="x unified",
    height=600
)


fig.update_yaxes(
    range=[
        -1,
        1
    ]
)


st.plotly_chart(
    fig,
    use_container_width=True
)



# Interpretation
mean_corr = (
    plot_data["correlation"]
    .mean()
)

mean_abs_corr = (
    plot_data["correlation"]
    .abs()
    .mean()
)


st.caption(
    f"Mean correlation: {mean_corr:.3f} "
    f"• Mean absolute correlation: "
    f"{mean_abs_corr:.3f} "
    f"• Lag: {lag} weeks "
    f"• Window: {window} weeks"
)