import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor


st.title("Weather Outliers and Anomalies")

st.write(
    "Analyse precipitation outliers and temperature anomalies "
    "for ERA5 weather data downloaded from Open-Meteo."
)

# Load the prepared hourly NO3 weather summary.
weather_file = Path(
    "data/no3_hourly_summary.parquet"
)

if not weather_file.exists():
    st.warning(
        "The prepared NO3 weather summary file was not found."
    )
    st.stop()

weather_df = pd.read_parquet(
    weather_file
)

weather_df["time"] = pd.to_datetime(
    weather_df["time"]
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
        )["precipitation"]
        .mean()
        .sort_values("time")
    )

    values = hourly_avg[
        "precipitation"
    ].to_numpy()

    coefficients = dct(
        values,
        norm="ortho"
    )

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
        - n_std * robust_std
    )

    upper_limit = (
        centre
        + n_std * robust_std
    )

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
        hourly_avg["precipitation"],
        label="Average precipitation"
    )

    ax.scatter(
        outliers["time"],
        outliers["precipitation"],
        label="Outliers",
        zorder=3
    )

    ax.set_title(
        "Average NO3 Precipitation with SPC Outliers"
    )

    ax.set_xlabel("Time")
    ax.set_ylabel(
        "Average Precipitation (mm)"
    )

    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

    plt.close(fig)

    st.metric(
        "Detected outliers",
        int(
            outlier_mask.sum()
        )
    )

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
        )["temperature_2m"]
        .mean()
        .sort_values("time")
    )

    values = temperature_avg[
        ["temperature_2m"]
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
        temperature_avg["time"],
        temperature_avg[
            "temperature_2m"
        ],
        label="Average temperature"
    )

    ax.scatter(
        anomalies["time"],
        anomalies[
            "temperature_2m"
        ],
        label="Anomalies",
        zorder=3
    )

    ax.set_title(
        "Average NO3 Temperature with LOF Anomalies"
    )

    ax.set_xlabel("Time")
    ax.set_ylabel(
        "Average Temperature (°C)"
    )

    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

    plt.close(fig)

    st.metric(
        "Detected anomalies",
        int(
            anomaly_mask.sum()
        )
    )

    st.metric(
        "Anomaly percentage",
        f"{anomaly_mask.mean() * 100:.2f}%"
    )