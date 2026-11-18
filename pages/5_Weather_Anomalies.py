import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import time

import plotly.graph_objects as go

from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor



# Load sampled coordinates
with open(
    "data/elspot_coordinates.json",
    "r",
    encoding="utf-8"
) as file:
    elspot_coordinates = json.load(file)


with open(
    "data/weather_region_coordinates.json",
    "r",
    encoding="utf-8"
) as file:
    weather_region_coordinates = json.load(file)



# Download weather data
@st.cache_data(show_spinner=False)
def download_weather_summary(
    coordinates,
    start_date,
    end_date,
    batch_size=100,
    max_retries=6
):
    """
    Download ERA5 weather data from Open-Meteo and return
    hourly averages across all selected locations.

    Locations are pooled into batches to reduce the number
    of API requests.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    batch_summaries = []

    for start in range(
        0,
        len(coordinates),
        batch_size
    ):

        batch = coordinates[
            start:start + batch_size
        ]

        longitudes = [
            coordinate[0]
            for coordinate in batch
        ]

        latitudes = [
            coordinate[1]
            for coordinate in batch
        ]

        params = {
            "latitude": ",".join(
                map(str, latitudes)
            ),
            "longitude": ",".join(
                map(str, longitudes)
            ),
            "start_date": start_date,
            "end_date": end_date,
            "hourly": [
                "temperature_2m",
                "precipitation"
            ],
            "models": "era5",
            "timezone": "UTC"
        }

        # Retry if the API rate limit is reached.
        for attempt in range(
            max_retries
        ):

            response = requests.get(
                url,
                params=params,
                timeout=120
            )

            if response.status_code == 429:

                wait_seconds = (
                    5 * (attempt + 1)
                )

                time.sleep(
                    wait_seconds
                )

                continue

            response.raise_for_status()

            break

        else:

            raise RuntimeError(
                "Open-Meteo rate limit persisted "
                "after retries."
            )

        result = response.json()

        if isinstance(
            result,
            dict
        ):
            result = [result]

        batch_frames = []

        for location_result in result:

            hourly = location_result[
                "hourly"
            ]

            location_df = pd.DataFrame(
                {
                    "time": pd.to_datetime(
                        hourly["time"]
                    ),
                    "temperature_2m":
                        hourly["temperature_2m"],
                    "precipitation":
                        hourly["precipitation"]
                }
            )

            batch_frames.append(
                location_df
            )

        batch_df = pd.concat(
            batch_frames,
            ignore_index=True
        )

        # Average all locations in this API batch.
        batch_summary = (
            batch_df
            .groupby(
                "time",
                as_index=False
            )
            .agg(
                temperature_2m=(
                    "temperature_2m",
                    "mean"
                ),
                precipitation=(
                    "precipitation",
                    "mean"
                ),
                location_count=(
                    "precipitation",
                    "count"
                )
            )
        )

        batch_summaries.append(
            batch_summary
        )

    combined = pd.concat(
        batch_summaries,
        ignore_index=True
    )

    # Weighted combination of batch averages.
    combined[
        "temperature_sum"
    ] = (
        combined[
            "temperature_2m"
        ]
        * combined[
            "location_count"
        ]
    )

    combined[
        "precipitation_sum"
    ] = (
        combined[
            "precipitation"
        ]
        * combined[
            "location_count"
        ]
    )

    weather_summary = (
        combined
        .groupby(
            "time",
            as_index=False
        )
        .agg(
            temperature_sum=(
                "temperature_sum",
                "sum"
            ),
            precipitation_sum=(
                "precipitation_sum",
                "sum"
            ),
            location_count=(
                "location_count",
                "sum"
            )
        )
    )

    weather_summary[
        "temperature_2m"
    ] = (
        weather_summary[
            "temperature_sum"
        ]
        / weather_summary[
            "location_count"
        ]
    )

    weather_summary[
        "precipitation"
    ] = (
        weather_summary[
            "precipitation_sum"
        ]
        / weather_summary[
            "location_count"
        ]
    )

    return weather_summary[
        [
            "time",
            "temperature_2m",
            "precipitation"
        ]
    ]



# Page title
st.title(
    "Weather Outliers and Anomalies"
)

st.write(
    "Analyse temperature and precipitation using "
    "DCT-based SATV/SPC and Local Outlier Factor."
)



# Area selection
area_type = st.radio(
    "Select area type",
    [
        "EL",
        "NO",
        "VASS"
    ],
    horizontal=True
)


if area_type == "EL":

    area_number = st.selectbox(
        "Select electricity area",
        [
            "NO1",
            "NO2",
            "NO3",
            "NO4",
            "NO5"
        ]
    )

    region_identifier = (
        area_number
    )

    selected_coordinates = (
        elspot_coordinates[
            area_number
        ]
    )


elif area_type == "VASS":

    vass_number = st.selectbox(
        "Select VASS region",
        [
            1,
            2,
            3
        ]
    )

    vass_weather_map = {
        1: "East",
        2: "West",
        3: "North"
    }

    region_identifier = (
        vass_weather_map[
            vass_number
        ]
    )

    selected_coordinates = (
        weather_region_coordinates[
            region_identifier
        ]
    )


else:

    region_identifier = "Norway"

    # Balanced national subset from
    # East, West and North.
    selected_coordinates = []

    for coordinates in (
        weather_region_coordinates.values()
    ):

        selected_coordinates.extend(
            coordinates[:100]
        )



# Date selection
start_date = st.date_input(
    "Start date",
    value=pd.to_datetime(
        "2024-01-01"
    )
)

end_date = st.date_input(
    "End date",
    value=pd.to_datetime(
        "2024-01-07"
    )
)


if start_date > end_date:

    st.error(
        "Start date must be before or equal to end date."
    )

    st.stop()



# Download button
download_weather = st.button(
    "Download weather data",
    type="primary"
)


if not download_weather:

    st.info(
        "Choose a region and date interval, then click "
        "'Download weather data' to run the analysis."
    )

    st.stop()


with st.spinner(
    f"Downloading ERA5 weather data for "
    f"{region_identifier}..."
):

    try:

        weather_df = download_weather_summary(
            coordinates=selected_coordinates,
            start_date=start_date.strftime(
                "%Y-%m-%d"
            ),
            end_date=end_date.strftime(
                "%Y-%m-%d"
            ),
            batch_size=100
        )

    except Exception as error:

        st.error(
            f"Weather data could not be downloaded: "
            f"{error}"
        )

        st.stop()


weather_df["time"] = pd.to_datetime(
    weather_df["time"]
)


st.success(
    f"Weather data loaded for {region_identifier}: "
    f"{len(weather_df)} hourly observations."
)



# Weather property selector
st.subheader(
    "Analysis settings"
)

weather_property = st.selectbox(
    "Weather property",
    [
        "Temperature",
        "Precipitation"
    ],
    index=0,
    help=(
        "Select which meteorological variable should "
        "be analysed with SATV/SPC and LOF."
    )
)


if weather_property == "Temperature":

    analysis_column = (
        "temperature_2m"
    )

    y_label = (
        "Temperature (°C)"
    )

else:

    analysis_column = (
        "precipitation"
    )

    y_label = (
        "Precipitation (mm)"
    )


# Hourly regional average for selected property.
hourly_avg = (
    weather_df
    .groupby(
        "time",
        as_index=False
    )[
        analysis_column
    ]
    .mean()
    .sort_values(
        "time"
    )
)



# Analysis tabs
spc_tab, lof_tab = st.tabs(
    [
        "SATV / SPC",
        "LOF"
    ]
)



# SATV / SPC

with spc_tab:

    st.subheader(
        f"{weather_property} – SATV and Robust SPC"
    )

    st.write(
        "DCT filtering separates the lower-frequency "
        "baseline from short-term variation. Robust "
        "control limits are calculated from the SATV "
        "component using the median and MAD."
    )

    frequency_cutoff = st.slider(
        "DCT frequency cutoff",
        min_value=5,
        max_value=200,
        value=50,
        step=5
    )

    n_std = st.slider(
        "Number of robust standard deviations",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )


    values = hourly_avg[
        analysis_column
    ].to_numpy()


   
    # DCT
    coefficients = dct(
        values,
        norm="ortho"
    )


    # Low-frequency component.
    low_pass_coefficients = (
        np.zeros_like(
            coefficients
        )
    )

    cutoff = min(
        frequency_cutoff,
        len(coefficients)
    )

    low_pass_coefficients[
        :cutoff
    ] = coefficients[
        :cutoff
    ]


    seasonal_baseline = idct(
        low_pass_coefficients,
        norm="ortho"
    )


  
    # SATV
    high_pass_coefficients = (
        coefficients.copy()
    )

    high_pass_coefficients[
        :cutoff
    ] = 0


    satv = idct(
        high_pass_coefficients,
        norm="ortho"
    )


   
    # Robust SPC limits
    centre = np.median(
        satv
    )

    mad = np.median(
        np.abs(
            satv - centre
        )
    )

    robust_std = (
        1.4826 * mad
    )


    lower_limit = (
        centre
        - n_std
        * robust_std
    )

    upper_limit = (
        centre
        + n_std
        * robust_std
    )


    # Convert residual limits back to
    # original weather-property scale.
    lower_boundary = (
        seasonal_baseline
        + lower_limit
    )

    upper_boundary = (
        seasonal_baseline
        + upper_limit
    )


    
    # Detect flagged observations
    outlier_mask = (
        (satv < lower_limit)
        |
        (satv > upper_limit)
    )


    outliers = hourly_avg.loc[
        outlier_mask
    ].copy()


  
    # Plotly SATV / SPC plot
    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=hourly_avg["time"],
            y=hourly_avg[
                analysis_column
            ],
            mode="lines",
            name=weather_property,
            hovertemplate=(
                "%{x|%d %b %Y %H:%M}"
                "<br>Value: %{y:.2f}"
                "<extra></extra>"
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=hourly_avg["time"],
            y=upper_boundary,
            mode="lines",
            name="Upper SPC boundary",
            line=dict(
                dash="dash"
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=hourly_avg["time"],
            y=lower_boundary,
            mode="lines",
            name="Lower SPC boundary",
            line=dict(
                dash="dash"
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=outliers["time"],
            y=outliers[
                analysis_column
            ],
            mode="markers",
            name="Flagged observations",
            marker=dict(
                size=8
            ),
            hovertemplate=(
                "%{x|%d %b %Y %H:%M}"
                "<br>Flagged value: %{y:.2f}"
                "<extra></extra>"
            )
        )
    )


    fig.update_layout(
        title=(
            f"Average {region_identifier} "
            f"{weather_property} with Robust SPC Limits"
        ),
        xaxis_title="Time",
        yaxis_title=y_label,
        hovermode="x unified",
        height=600
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    
    # SPC metrics
    col1, col2, col3 = st.columns(
        3
    )


    col1.metric(
        "Flagged observations",
        int(
            outlier_mask.sum()
        )
    )


    col2.metric(
        "Flagged percentage",
        f"{outlier_mask.mean() * 100:.2f}%"
    )


    col3.metric(
        "Robust scale",
        f"{robust_std:.3f}"
    )



# LOF
with lof_tab:

    st.subheader(
        f"{weather_property} – Local Outlier Factor"
    )

    st.write(
        "Local Outlier Factor compares each observation "
        "with nearby observations in feature space to "
        "identify unusual values."
    )


    contamination = st.slider(
        "Expected anomaly proportion",
        min_value=0.001,
        max_value=0.05,
        value=0.01,
        step=0.001
    )


    lof_values = (
        hourly_avg[
            [
                analysis_column
            ]
        ]
        .to_numpy()
    )


   
    # LOF model
    lof = LocalOutlierFactor(
        contamination=contamination
    )


    labels = lof.fit_predict(
        lof_values
    )


    anomaly_mask = (
        labels == -1
    )


    anomalies = hourly_avg.loc[
        anomaly_mask
    ].copy()


  
    # Plotly LOF plot

    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=hourly_avg["time"],
            y=hourly_avg[
                analysis_column
            ],
            mode="lines",
            name=weather_property,
            hovertemplate=(
                "%{x|%d %b %Y %H:%M}"
                "<br>Value: %{y:.2f}"
                "<extra></extra>"
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=anomalies["time"],
            y=anomalies[
                analysis_column
            ],
            mode="markers",
            name="LOF anomalies",
            marker=dict(
                size=9
            ),
            hovertemplate=(
                "%{x|%d %b %Y %H:%M}"
                "<br>Anomaly: %{y:.2f}"
                "<extra></extra>"
            )
        )
    )


    fig.update_layout(
        title=(
            f"Average {region_identifier} "
            f"{weather_property} with LOF Anomalies"
        ),
        xaxis_title="Time",
        yaxis_title=y_label,
        hovermode="x unified",
        height=600
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # LOF metrics
    col1, col2 = st.columns(
        2
    )


    col1.metric(
        "Detected anomalies",
        int(
            anomaly_mask.sum()
        )
    )


    col2.metric(
        "Anomaly percentage",
        f"{anomaly_mask.mean() * 100:.2f}%"
    )