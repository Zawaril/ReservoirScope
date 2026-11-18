import streamlit as st
import plotly.graph_objects as go

from scipy.signal import spectrogram
from statsmodels.tsa.seasonal import STL

from nve_api import load_nve_data


st.title("Seasonal and Frequency Analysis")

st.write(
    "Explore seasonal patterns and frequency behaviour in "
    "Norwegian reservoir filling levels."
)



# Load reservoir data
reservoir_df = load_nve_data()



# Area selection
area_type = st.radio(
    "Select area type",
    ["EL", "NO", "VASS"],
    horizontal=True
)


area_df = reservoir_df[
    reservoir_df["area_type"] == area_type
].copy()


area_numbers = sorted(
    area_df["area_number"]
    .dropna()
    .unique()
)


area_number = st.selectbox(
    "Select area number",
    area_numbers
)


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



# Analysis tabs
stl_tab, spectrogram_tab = st.tabs(
    [
        "STL Decomposition",
        "Spectrogram"
    ]
)



# STL TAB
with stl_tab:

    st.subheader(
        "STL Decomposition"
    )

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


    st.caption(
        "Smaller values allow the seasonal pattern to vary more over time; "
        "larger values produce a smoother and more stable seasonal component."
    )


    trend = st.slider(
        "Trend smoother",
        min_value=53,
        max_value=209,
        value=105,
        step=2
    )


    st.caption(
        "Smaller values make the trend more responsive to short-term changes; "
        "larger values produce a smoother long-term trend."
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


       
        # Interactive Plotly STL figure
        stl_fig = go.Figure()


        stl_fig.add_trace(
            go.Scatter(
                x=series.index,
                y=result.observed,
                mode="lines",
                name="Observed",
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Observed: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


        stl_fig.add_trace(
            go.Scatter(
                x=series.index,
                y=result.trend,
                mode="lines",
                name="Trend",
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Trend: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


        stl_fig.add_trace(
            go.Scatter(
                x=series.index,
                y=result.seasonal,
                mode="lines",
                name="Seasonal",
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Seasonal: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


        stl_fig.add_trace(
            go.Scatter(
                x=series.index,
                y=result.resid,
                mode="lines",
                name="Residual",
                hovertemplate=(
                    "%{x|%d %b %Y}"
                    "<br>Residual: %{y:.3f}"
                    "<extra></extra>"
                )
            )
        )


        stl_fig.update_layout(
            title=(
                f"STL Decomposition – "
                f"{area_type} {area_number}"
            ),
            xaxis_title="Date",
            yaxis_title="Component value",
            hovermode="x unified",
            height=650
        )


        stl_fig.update_xaxes(
            rangeslider_visible=True
        )


        st.plotly_chart(
            stl_fig,
            use_container_width=True
        )


    except ValueError as error:

        st.error(
            f"STL analysis could not be completed: {error}"
        )



# SPECTROGRAM TAB
with spectrogram_tab:

    st.subheader(
        "Spectrogram"
    )

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


   
    # Interactive Plotly heatmap
    spectrogram_fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=power,
            colorbar=dict(
                title="Power"
            ),
            hovertemplate=(
                "Time index: %{x:.1f} weeks"
                "<br>Frequency: %{y:.4f} cycles/week"
                "<br>Power: %{z:.6f}"
                "<extra></extra>"
            )
        )
    )


    spectrogram_fig.update_layout(
        title=(
            "Reservoir Filling Spectrogram – "
            f"{area_type} {area_number}"
        ),
        xaxis_title="Time index (weeks)",
        yaxis_title="Frequency (cycles per week)",
        height=650
    )


    st.plotly_chart(
        spectrogram_fig,
        use_container_width=True
    )