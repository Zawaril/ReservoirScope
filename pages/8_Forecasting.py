import streamlit as st
import plotly.graph_objects as go

import pandas as pd
import requests
from io import StringIO

from nve_api import load_nve_data
from forecasting import (
    train_forecast_model,
    forecast_future
)


st.title("Reservoir Forecasting")

st.write(
    "Forecast reservoir filling using the selected region "
    "and configurable model parameters."
)



# Read shared map settings
selected_area_type = st.session_state.get(
    "selected_area_type",
    "EL"
)

selected_area = st.session_state.get(
    "selected_area",
    "NO3"
)

map_start_date = st.session_state.get(
    "map_start_date"
)

map_end_date = st.session_state.get(
    "map_end_date"
)


st.info(
    f"Shared map selection: "
    f"{selected_area_type} {selected_area}"
)


if (
    map_start_date is not None
    and map_end_date is not None
):

    st.info(
        f"Shared map timeframe: "
        f"{map_start_date} to {map_end_date}"
    )



# Helper: Norges Bank currency data
@st.cache_data(show_spinner=False)
def load_currency_data(
    start_date,
    end_date
):
    """
    Download EUR/NOK and USD/NOK exchange rates
    from Norges Bank and aggregate to weekly values.
    """

    currencies = [
        "EUR",
        "USD"
    ]

    all_rates = []


    for currency in currencies:

        url = (
            "https://data.norges-bank.no/api/data/"
            f"EXR/B.{currency}.NOK.SP"
        )

        params = {
            "format": "csv",
            "startPeriod": start_date,
            "endPeriod": end_date,
            "locale": "en"
        }


        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()


        currency_df = pd.read_csv(
            StringIO(
                response.text
            ),
            sep=";"
        )


        currency_df[
            "currency"
        ] = currency


        all_rates.append(
            currency_df
        )


    currency_df = pd.concat(
        all_rates,
        ignore_index=True
    )


    currency_df[
        "TIME_PERIOD"
    ] = pd.to_datetime(
        currency_df[
            "TIME_PERIOD"
        ]
    )


    currency_df[
        "OBS_VALUE"
    ] = pd.to_numeric(
        currency_df[
            "OBS_VALUE"
        ],
        errors="coerce"
    )


    daily_currency = (
        currency_df[
            [
                "TIME_PERIOD",
                "currency",
                "OBS_VALUE"
            ]
        ]
        .pivot(
            index="TIME_PERIOD",
            columns="currency",
            values="OBS_VALUE"
        )
        .sort_index()
    )


    weekly_currency = (
        daily_currency
        .resample(
            "W-SUN"
        )
        .mean()
        .rename(
            columns={
                "EUR": "eur_nok",
                "USD": "usd_nok"
            }
        )
    )


    return weekly_currency



# Helper: available historical weather
@st.cache_data
def load_weather_data():
    """
    Load the existing NO3 weather summary and
    aggregate it to weekly resolution.
    """

    weather_df = pd.read_parquet(
        "data/no3_hourly_summary.parquet"
    )


    weather_df[
        "time"
    ] = pd.to_datetime(
        weather_df[
            "time"
        ]
    )


    weekly_weather = (
        weather_df
        .set_index(
            "time"
        )
        .resample(
            "W-SUN"
        )
        .agg(
            {
                "temperature_2m": "mean",
                "precipitation": "sum"
            }
        )
        .rename(
            columns={
                "temperature_2m":
                    "temperature_mean",

                "precipitation":
                    "precipitation_sum"
            }
        )
    )


    return weekly_weather



# Area controls
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



# Forecast controls
st.subheader(
    "Model settings"
)


history_weeks = st.slider(
    "Training history (weeks)",
    min_value=104,
    max_value=520,
    value=260,
    step=52
)


lags = st.slider(
    "Lag features",
    min_value=1,
    max_value=20,
    value=8
)


horizon = st.slider(
    "Forecast horizon (weeks)",
    min_value=4,
    max_value=26,
    value=12
)


st.caption(
    "Annual week-of-year seasonality is included "
    "in the forecasting model."
)



# Optional exogenous variables
st.subheader(
    "Optional exogenous variables"
)


st.caption(
    "The seasonal lag-only model remains the default. "
    "Optional variables can be added for scenario analysis."
)


use_temperature = st.checkbox(
    "Temperature"
)

use_precipitation = st.checkbox(
    "Precipitation"
)

use_eur = st.checkbox(
    "EUR/NOK"
)

use_usd = st.checkbox(
    "USD/NOK"
)



# Future scenario assumptions
future_temperature = None
future_precipitation = None
future_eur = None
future_usd = None


if (
    use_temperature
    or use_precipitation
):

    if not (
        area_type == "EL"
        and area_number == "NO3"
    ):

        st.warning(
            "Historical weather data currently available "
            "for forecasting is the NO3 weather dataset. "
            "Weather exogenous forecasting should therefore "
            "currently be interpreted as an NO3 scenario."
        )


if use_temperature:

    future_temperature = st.number_input(
        "Future average temperature (°C)",
        value=5.0,
        step=0.5,
        help=(
            "Assumed average temperature used "
            "throughout the forecast horizon."
        )
    )


if use_precipitation:

    future_precipitation = st.number_input(
        "Future weekly precipitation (mm)",
        value=20.0,
        step=1.0,
        min_value=0.0,
        help=(
            "Assumed weekly precipitation used "
            "throughout the forecast horizon."
        )
    )


if use_eur:

    future_eur = st.number_input(
        "Future EUR/NOK",
        value=11.50,
        step=0.10
    )


if use_usd:

    future_usd = st.number_input(
        "Future USD/NOK",
        value=10.50,
        step=0.10
    )


# Load reservoir data
reservoir_df = load_nve_data()


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


series = (
    reservoir_df[
        (
            reservoir_df[
                "area_type"
            ]
            == area_type
        )
        & (
            reservoir_df[
                "area_number"
            ]
            == selected_number
        )
    ]
    .sort_values(
        "date"
    )
    .set_index(
        "date"
    )[
        "fill_level"
    ]
    .dropna()
)



# Check available data
if series.empty:

    st.error(
        "No reservoir data is available "
        "for the selected area."
    )

    st.stop()


st.caption(
    f"Available observations: {len(series)} "
    f"• {series.index.min().date()} to "
    f"{series.index.max().date()}"
)



# Build historical exogenous dataset
exogenous_data = None


if (
    use_temperature
    or use_precipitation
    or use_eur
    or use_usd
):

    exogenous_data = pd.DataFrame(
        index=series.index
    )


    
    # Weather
    if (
        use_temperature
        or use_precipitation
    ):

        weather_data = (
            load_weather_data()
        )


        if use_temperature:

            exogenous_data[
                "temperature_mean"
            ] = weather_data[
                "temperature_mean"
            ]


        if use_precipitation:

            exogenous_data[
                "precipitation_sum"
            ] = weather_data[
                "precipitation_sum"
            ]


    
    # Currency
    if (
        use_eur
        or use_usd
    ):

        currency_start = (
            series.index.min()
            .strftime(
                "%Y-%m-%d"
            )
        )

        currency_end = (
            series.index.max()
            .strftime(
                "%Y-%m-%d"
            )
        )


        try:

            currency_data = (
                load_currency_data(
                    currency_start,
                    currency_end
                )
            )


            if use_eur:

                exogenous_data[
                    "eur_nok"
                ] = currency_data[
                    "eur_nok"
                ]


            if use_usd:

                exogenous_data[
                    "usd_nok"
                ] = currency_data[
                    "usd_nok"
                ]


        except Exception as error:

            st.error(
                "Norges Bank exchange-rate data "
                f"could not be loaded: {error}"
            )

            st.stop()



# Current configuration
with st.expander(
    "Current forecast configuration"
):

    st.write(
        {
            "Area type":
                area_type,

            "Area":
                area_number,

            "History weeks":
                history_weeks,

            "Lags":
                lags,

            "Forecast horizon":
                horizon,

            "Seasonality":
                True,

            "Temperature":
                use_temperature,

            "Precipitation":
                use_precipitation,

            "EUR/NOK":
                use_eur,

            "USD/NOK":
                use_usd,

            "Future temperature":
                future_temperature,

            "Future precipitation":
                future_precipitation,

            "Future EUR/NOK":
                future_eur,

            "Future USD/NOK":
                future_usd,

            "Shared map start date":
                map_start_date,

            "Shared map end date":
                map_end_date
        }
    )



# Generate forecast
if st.button(
    "Generate forecast",
    type="primary"
):

    if history_weeks <= lags:

        st.error(
            "Training history must be longer "
            "than the number of lag features."
        )

        st.stop()


    with st.spinner(
        "Training River model and generating forecast..."
    ):

        model, history = (
            train_forecast_model(
                series=series,
                history_weeks=history_weeks,
                lags=lags,
                exogenous_data=exogenous_data,
                use_temperature=use_temperature,
                use_precipitation=use_precipitation,
                use_eur=use_eur,
                use_usd=use_usd
            )
        )


        forecast = forecast_future(
            model=model,
            history=history,
            lags=lags,
            horizon=horizon,
            future_temperature=(
                future_temperature
                if use_temperature
                else None
            ),
            future_precipitation=(
                future_precipitation
                if use_precipitation
                else None
            ),
            future_eur=(
                future_eur
                if use_eur
                else None
            ),
            future_usd=(
                future_usd
                if use_usd
                else None
            )
        )


  
    # Forecast summary
    st.subheader(
        "Forecast result"
    )


    col1, col2, col3 = st.columns(
        3
    )


    col1.metric(
        "Latest filling level",
        f"{history.iloc[-1]:.1%}"
    )


    col2.metric(
        "End-of-horizon forecast",
        f"{forecast.iloc[-1]:.1%}"
    )


    forecast_change = (
        forecast.iloc[-1]
        - history.iloc[-1]
    )


    col3.metric(
        "Forecast change",
        f"{forecast_change:+.1%}"
    )


    
    # Forecast overview
    st.subheader(
        "Forecast overview"
    )


    history_plot = history.tail(
        52
    )


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=history_plot.index,
            y=history_plot.values,
            mode="lines",
            name="Historical",
            hovertemplate=(
                "%{x|%d %b %Y}"
                "<br>Filling: %{y:.1%}"
                "<extra></extra>"
            )
        )
    )


    forecast_x = (
        [history_plot.index[-1]]
        + list(
            forecast.index
        )
    )


    forecast_y = (
        [history_plot.iloc[-1]]
        + list(
            forecast.values
        )
    )


    fig.add_trace(
        go.Scatter(
            x=forecast_x,
            y=forecast_y,
            mode="lines+markers",
            name="Forecast",
            hovertemplate=(
                "%{x|%d %b %Y}"
                "<br>Forecast: %{y:.1%}"
                "<extra></extra>"
            )
        )
    )


    fig.add_vline(
        x=history.index.max(),
        line_dash="dash"
    )


    fig.update_layout(
        title=(
            "Reservoir Filling Forecast – "
            f"{area_type} {area_number}"
        ),
        xaxis_title="Date",
        yaxis_title="Filling level",
        hovermode="x unified",
        height=600
    )


    fig.update_yaxes(
        range=[
            0,
            1
        ],
        tickformat=".0%"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    
    # Animated forecast
    st.subheader(
        "Animated forecast"
    )


    animation_dates = list(
        forecast.index
    )

    animation_values = list(
        forecast.values
    )


    animated_fig = go.Figure()


    animated_fig.add_trace(
        go.Scatter(
            x=history_plot.index,
            y=history_plot.values,
            mode="lines",
            name="Historical"
        )
    )


    animated_fig.add_trace(
        go.Scatter(
            x=[
                history_plot.index[-1]
            ],
            y=[
                history_plot.iloc[-1]
            ],
            mode="lines+markers",
            name="Forecast"
        )
    )


    frames = []


    for i in range(
        len(animation_dates)
    ):

        frame_x = (
            [history_plot.index[-1]]
            + animation_dates[
                :i + 1
            ]
        )

        frame_y = (
            [history_plot.iloc[-1]]
            + animation_values[
                :i + 1
            ]
        )


        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=history_plot.index,
                        y=history_plot.values,
                        mode="lines"
                    ),

                    go.Scatter(
                        x=frame_x,
                        y=frame_y,
                        mode="lines+markers"
                    )
                ],
                name=str(i)
            )
        )


    animated_fig.frames = frames


    slider_steps = []


    for i, forecast_date in enumerate(
        animation_dates
    ):

        slider_steps.append(
            {
                "label":
                    forecast_date.strftime(
                        "%d %b"
                    ),

                "method":
                    "animate",

                "args": [
                    [str(i)],
                    {
                        "mode":
                            "immediate",

                        "frame": {
                            "duration":
                                300,

                            "redraw":
                                True
                        },

                        "transition": {
                            "duration":
                                100
                        }
                    }
                ]
            }
        )


    animated_fig.update_layout(
        title=(
            "Dynamic Reservoir Filling Forecast – "
            f"{area_type} {area_number}"
        ),

        xaxis_title=
            "Date",

        yaxis_title=
            "Filling level",

        height=
            600,

        hovermode=
            "x unified",

        updatemenus=[
            {
                "type":
                    "buttons",

                "direction":
                    "left",

                "showactive":
                    False,

                "x":
                    0,

                "y":
                    1.12,

                "buttons": [
                    {
                        "label":
                            "▶ Play",

                        "method":
                            "animate",

                        "args": [
                            None,
                            {
                                "frame": {
                                    "duration":
                                        500,

                                    "redraw":
                                        True
                                },

                                "transition": {
                                    "duration":
                                        100
                                },

                                "fromcurrent":
                                    True,

                                "mode":
                                    "immediate"
                            }
                        ]
                    },

                    {
                        "label":
                            "⏸ Pause",

                        "method":
                            "animate",

                        "args": [
                            [None],
                            {
                                "frame": {
                                    "duration":
                                        0,

                                    "redraw":
                                        False
                                },

                                "transition": {
                                    "duration":
                                        0
                                },

                                "mode":
                                    "immediate"
                            }
                        ]
                    }
                ]
            }
        ],

        sliders=[
            {
                "active":
                    0,

                "currentvalue": {
                    "prefix":
                        "Forecast date: "
                },

                "pad": {
                    "t":
                        40
                },

                "steps":
                    slider_steps
            }
        ]
    )


    animated_fig.add_vline(
        x=history.index.max(),
        line_dash="dash"
    )


    animated_fig.update_yaxes(
        range=[
            0,
            1
        ],
        tickformat=".0%"
    )


    st.plotly_chart(
        animated_fig,
        use_container_width=True
    )


    
    # Forecast table
    st.subheader(
        "Forecast values"
    )


    forecast_table = (
        forecast
        .rename(
            "Forecast filling level"
        )
        .to_frame()
    )


    forecast_table[
        "Forecast filling (%)"
    ] = (
        forecast_table[
            "Forecast filling level"
        ]
        * 100
    ).round(
        2
    )


    st.dataframe(
        forecast_table[
            [
                "Forecast filling (%)"
            ]
        ],
        use_container_width=True
    )


   
    # Model description
    selected_features = [
        "reservoir lags",
        "annual seasonality"
    ]


    if use_temperature:
        selected_features.append(
            "temperature"
        )

    if use_precipitation:
        selected_features.append(
            "precipitation"
        )

    if use_eur:
        selected_features.append(
            "EUR/NOK"
        )

    if use_usd:
        selected_features.append(
            "USD/NOK"
        )


    st.caption(
        "Model inputs: "
        + ", ".join(
            selected_features
        )
        + "."
    )