import streamlit as st
import matplotlib.pyplot as plt

from scipy.signal import spectrogram
from statsmodels.tsa.seasonal import STL

from nve_api import load_nve_data


st.title("Seasonal and Frequency Analysis")

st.write(
    "Explore seasonal patterns and frequency behaviour in "
    "Norwegian reservoir filling levels."
)


# Load reservoir data directly from the NVE API.
reservoir_df = load_nve_data()


# Select geographical area type.
area_type = st.radio(
    "Select area type",
    ["EL", "NO", "VASS"],
    horizontal=True
)


area_df = reservoir_df[
    reservoir_df["area_type"] == area_type
].copy()


# Identify the area numbers belonging to the selected area type.
area_numbers = sorted(
    area_df["area_number"]
    .dropna()
    .unique()
)


area_number = st.selectbox(
    "Select area number",
    area_numbers
)


# Select and prepare the reservoir filling-level series.
selected_df = (
    area_df[
        area_df["area_number"] == area_number
    ][
        [
            "date",
            "fill_level"
        ]
    ]
    .dropna()
    .sort_values("date")
)


st.caption(
    f"Selected area: {area_type} {area_number} "
    f"• {len(selected_df)} observations"
)


# Create the two required analysis tabs.
stl_tab, spectrogram_tab = st.tabs(
    [
        "STL Decomposition",
        "Spectrogram"
    ]
)


with stl_tab:

    st.subheader("STL Decomposition")

    st.write(
        "STL separates reservoir filling level into trend, "
        "seasonal, and residual components."
    )

    seasonal = st.slider(
        "Seasonal smoother",
        min_value=7,
        max_value=105,
        value=53,
        step=2
    )

    trend = st.slider(
        "Trend smoother",
        min_value=53,
        max_value=209,
        value=105,
        step=2
    )

    robust = st.checkbox(
        "Use robust STL fitting",
        value=True
    )

    series = (
        selected_df
        .set_index("date")["fill_level"]
        .sort_index()
    )

    try:

        stl = STL(
            series,
            period=52,
            seasonal=seasonal,
            trend=trend,
            robust=robust
        )

        result = stl.fit()

        fig = result.plot()

        fig.set_size_inches(
            12,
            8
        )

        fig.suptitle(
            f"STL Decomposition – "
            f"{area_type} {area_number}",
            y=1.02
        )

        st.pyplot(fig)

        plt.close(fig)

    except ValueError as error:

        st.error(
            f"STL analysis could not be completed: {error}"
        )


with spectrogram_tab:

    st.subheader("Spectrogram")

    st.write(
        "The spectrogram shows how the frequency structure "
        "of reservoir filling levels changes over time."
    )

    window_length = st.slider(
        "Window length",
        min_value=26,
        max_value=208,
        value=104,
        step=13
    )

    max_overlap = max(
        0,
        window_length - 1
    )

    window_overlap = st.slider(
        "Window overlap",
        min_value=0,
        max_value=max_overlap,
        value=min(
            52,
            max_overlap
        ),
        step=1
    )

    values = (
        selected_df["fill_level"]
        .to_numpy()
    )

    frequencies, times, power = spectrogram(
        values,
        fs=1,
        nperseg=window_length,
        noverlap=window_overlap
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    mesh = ax.pcolormesh(
        times,
        frequencies,
        power,
        shading="auto"
    )

    ax.set_title(
        f"Reservoir Filling Spectrogram – "
        f"{area_type} {area_number}"
    )

    ax.set_xlabel(
        "Time index (weeks)"
    )

    ax.set_ylabel(
        "Frequency (cycles per week)"
    )

    fig.colorbar(
        mesh,
        ax=ax,
        label="Power"
    )

    st.pyplot(fig)

    plt.close(fig)