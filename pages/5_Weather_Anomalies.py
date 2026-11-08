import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import requests
import time

from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor


# Load sampled electricity-area coordinates.
with open(
    "data/elspot_coordinates.json",
    "r",
    encoding="utf-8"
) as file:
    elspot_coordinates = json.load(file)


# Load sampled broad weather-region coordinates.
with open(
    "data/weather_region_coordinates.json",
    "r",
    encoding="utf-8"
) as file:
    weather_region_coordinates = json.load(file)


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


st.title(
    "Weather Outliers and Anomalies"
)

st.write(
    "Analyse precipitation outliers and temperature anomalies "
    "for ERA5 weather data downloaded from Open-Meteo."
)


# Match the area types used by Magasinstatistikk.
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

    # Use a balanced subset from East, West and North
    # to keep the national weather download practical.
    selected_coordinates = []

    for coordinates in (
        weather_region_coordinates.values()
    ):
        selected_coordinates.extend(
            coordinates[:100]
        )


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


download_weather = st.button(
    "Download weather data"
)


if not download_weather:

    st.info(
        "Choose a region and date interval, then click "
        "'Download weather data' to run the analysis."
    )

    st.stop()


with st.spinner(
    f"Downloading ERA5 weather data for {region_identifier}..."
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
            f"Weather data could not be downloaded: {error}"
        )

        st.stop()


weather_df["time"] = pd.to_datetime(
    weather_df["time"]
)


st.success(
    f"Weather data loaded for {region_identifier}: "
    f"{len(weather_df)} hourly observations."
)


# Create the two required analysis tabs.
spc_tab, lof_tab = st.tabs(
    [
        "Precipitation SPC",
        "Temperature LOF"
    ]
)


with spc_tab:

    st.subheader(
        "Precipitation Outlier Detection"
    )

    frequency_cutoff = st.slider(
        "DCT frequency cutoff",
        min_value=5,
        max_value=200,
        value=50,
        step=5
    )

    n_std = st.slider(
        "Number of standard deviations",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )

    hourly_avg = (
        weather_df
        .groupby(
            "time",
            as_index=False
        )[
            "precipitation"
        ]
        .mean()
        .sort_values(
            "time"
        )
    )

    values = hourly_avg[
        "precipitation"
    ].to_numpy()


    # Apply the Discrete Cosine Transform.
    coefficients = dct(
        values,
        norm="ortho"
    )


    # Low-frequency component represents the seasonal baseline.
    low_pass_coefficients = np.zeros_like(
        coefficients
    )

    low_pass_coefficients[
        :frequency_cutoff
    ] = coefficients[
        :frequency_cutoff
    ]

    seasonal_baseline = idct(
        low_pass_coefficients,
        norm="ortho"
    )


    # High-pass component gives seasonally adjusted variation.
    high_pass_coefficients = (
        coefficients.copy()
    )

    high_pass_coefficients[
        :frequency_cutoff
    ] = 0

    satv = idct(
        high_pass_coefficients,
        norm="ortho"
    )


    # Robust SPC limits based on median and MAD.
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


    # Convert SATV limits back to precipitation-scale curves.
    lower_boundary = (
        seasonal_baseline
        + lower_limit
    )

    upper_boundary = (
        seasonal_baseline
        + upper_limit
    )


    # Detect observations outside the SPC boundaries.
    outlier_mask = (
        (satv < lower_limit)
        |
        (satv > upper_limit)
    )

    outliers = hourly_avg.loc[
        outlier_mask
    ].copy()


    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        hourly_avg["time"],
        hourly_avg[
            "precipitation"
        ],
        label="Average precipitation"
    )

    ax.plot(
        hourly_avg["time"],
        upper_boundary,
        linestyle="--",
        label="Upper SPC boundary"
    )

    ax.plot(
        hourly_avg["time"],
        lower_boundary,
        linestyle="--",
        label="Lower SPC boundary"
    )

    ax.scatter(
        outliers["time"],
        outliers[
            "precipitation"
        ],
        label="Outliers",
        zorder=3
    )

    ax.set_title(
        f"Average {region_identifier} "
        "Precipitation with SPC Outliers"
    )

    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Average Precipitation (mm)"
    )

    ax.grid(
        True
    )

    ax.legend()

    st.pyplot(
        fig
    )

    plt.close(
        fig
    )


    col1, col2 = st.columns(
        2
    )

    with col1:

        st.metric(
            "Detected outliers",
            int(
                outlier_mask.sum()
            )
        )

    with col2:

        st.metric(
            "Outlier percentage",
            f"{outlier_mask.mean() * 100:.2f}%"
        )


with lof_tab:

    st.subheader(
        "Temperature Anomaly Detection"
    )

    contamination = st.slider(
        "Expected anomaly proportion",
        min_value=0.001,
        max_value=0.05,
        value=0.01,
        step=0.001
    )

    temperature_avg = (
        weather_df
        .groupby(
            "time",
            as_index=False
        )[
            "temperature_2m"
        ]
        .mean()
        .sort_values(
            "time"
        )
    )

    values = temperature_avg[
        [
            "temperature_2m"
        ]
    ].to_numpy()


    lof = LocalOutlierFactor(
        contamination=contamination
    )

    labels = lof.fit_predict(
        values
    )

    anomaly_mask = (
        labels == -1
    )

    anomalies = temperature_avg.loc[
        anomaly_mask
    ].copy()


    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        temperature_avg[
            "time"
        ],
        temperature_avg[
            "temperature_2m"
        ],
        label="Average temperature"
    )

    ax.scatter(
        anomalies[
            "time"
        ],
        anomalies[
            "temperature_2m"
        ],
        label="Anomalies",
        zorder=3
    )

    ax.set_title(
        f"Average {region_identifier} "
        "Temperature with LOF Anomalies"
    )

    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Average Temperature (°C)"
    )

    ax.grid(
        True
    )

    ax.legend()

    st.pyplot(
        fig
    )

    plt.close(
        fig
    )


    col1, col2 = st.columns(
        2
    )

    with col1:

        st.metric(
            "Detected anomalies",
            int(
                anomaly_mask.sum()
            )
        )

    with col2:

        st.metric(
            "Anomaly percentage",
            f"{anomaly_mask.mean() * 100:.2f}%"
        )