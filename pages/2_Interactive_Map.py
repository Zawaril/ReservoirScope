import streamlit as st
import geopandas as gpd
import plotly.express as px

import pandas as pd
import json
import requests
import time


st.title("Interactive Map")

st.write(
    "Explore Norwegian electricity and water regions "
    "using interactive GeoJSON overlays."
)


# Load coordinate data
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





# Load GeoJSON
@st.cache_data
def load_geojson(path):
    """
    Load a GeoJSON file and convert it to WGS84
    for use with Plotly maps.
    """

    gdf = gpd.read_file(path)

    if gdf.crs is not None:
        gdf = gdf.to_crs(4326)

    return gdf


# Download aggregated regional weather
@st.cache_data(show_spinner=False)
def download_region_weather_value(
    coordinates,
    start_date,
    end_date,
    weather_property,
    batch_size=100,
    max_retries=6
):
    """
    Download ERA5 weather data for a region and return
    one aggregated weather value for the selected period.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    all_values = []

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

        for location_result in result:

            hourly = location_result[
                "hourly"
            ]

            if weather_property == "Temperature":

                values = hourly[
                    "temperature_2m"
                ]

            else:

                values = hourly[
                    "precipitation"
                ]

            all_values.extend(
                value
                for value in values
                if value is not None
            )


    if not all_values:
        return None


    return float(
        pd.Series(
            all_values
        ).mean()
    )



# Area type selector
area_type = st.radio(
    "Select area type",
    [
        "Electricity areas",
        "Water regions"
    ],
    horizontal=True
)



# Colour selector
color_mode = st.selectbox(
    "Colour areas by",
    [
        "Area category",
        "Weather property"
    ]
)


weather_property = None
start_date = None
end_date = None


if color_mode == "Weather property":

    weather_property = st.selectbox(
        "Weather property",
        [
            "Temperature",
            "Precipitation"
        ],
        index=0
    )


    
    # Weather time period
    date_col1, date_col2 = st.columns(
        2
    )


    with date_col1:

        start_date = st.date_input(
            "Weather start date",
            value=pd.to_datetime(
                "2024-01-01"
            )
        )


    with date_col2:

        end_date = st.date_input(
            "Weather end date",
            value=pd.to_datetime(
                "2024-01-07"
            )
        )
    st.session_state["map_start_date"] = start_date
    st.session_state["map_end_date"] = end_date


    if start_date > end_date:

        st.error(
            "Start date must be before or equal "
            "to end date."
        )

        st.stop()



# Load selected geographical layer
if area_type == "Electricity areas":

    gdf = load_geojson(
        "data/shapefiles/elspotomraader.geojson"
    )

    id_column = "ElSpotOmr"
    label_column = "ElSpotOmr"


else:

    gdf = load_geojson(
        "data/shapefiles/nve_regions.geojson"
    )

    id_column = "REGION"
    label_column = "REGIONNAVN"



# Prepare colour values
if color_mode == "Area category":

    color_column = id_column


else:

    weather_values = {}


    if st.button(
        "Load weather values",
        type="primary"
    ):

        with st.spinner(
            "Downloading and aggregating ERA5 "
            "weather data for the map..."
        ):

            try:

                
                # Electricity regions
                if area_type == "Electricity areas":

                    for region in gdf[
                        id_column
                    ]:

                        coordinates = (
                            elspot_coordinates[
                                region
                            ]
                        )

                        weather_values[
                            region
                        ] = (
                            download_region_weather_value(
                                coordinates=coordinates,
                                start_date=start_date.strftime(
                                    "%Y-%m-%d"
                                ),
                                end_date=end_date.strftime(
                                    "%Y-%m-%d"
                                ),
                                weather_property=weather_property
                            )
                        )


                
                # Water regions
                else:

                    region_map = {
                        "RV": "West",
                        "RM": "North",
                        "RN": "North",
                        "RØ": "East",
                        "RS": "East"
                    }


                    for region in gdf[
                        id_column
                    ]:

                        broad_region = (
                            region_map[
                                region
                            ]
                        )

                        coordinates = (
                            weather_region_coordinates[
                                broad_region
                            ]
                        )

                        weather_values[
                            region
                        ] = (
                            download_region_weather_value(
                                coordinates=coordinates,
                                start_date=start_date.strftime(
                                    "%Y-%m-%d"
                                ),
                                end_date=end_date.strftime(
                                    "%Y-%m-%d"
                                ),
                                weather_property=weather_property
                            )
                        )


                # Store the values and settings so they
                # survive Streamlit reruns.
                st.session_state[
                    "map_weather_values"
                ] = weather_values

                st.session_state[
                    "map_weather_area_type"
                ] = area_type

                st.session_state[
                    "map_weather_property"
                ] = weather_property

                st.session_state[
                    "map_weather_start_date"
                ] = str(
                    start_date
                )

                st.session_state[
                    "map_weather_end_date"
                ] = str(
                    end_date
                )


            except Exception as error:

                st.error(
                    "Weather values could not be "
                    f"downloaded: {error}"
                )

                st.stop()


        st.success(
            "Weather values loaded successfully."
        )


    
    # Use stored weather values only if they correspond
    # to the current map settings.
    settings_match = (
        "map_weather_values"
        in st.session_state
        and st.session_state.get(
            "map_weather_area_type"
        ) == area_type
        and st.session_state.get(
            "map_weather_property"
        ) == weather_property
        and st.session_state.get(
            "map_weather_start_date"
        ) == str(start_date)
        and st.session_state.get(
            "map_weather_end_date"
        ) == str(end_date)
    )


    if settings_match:

        gdf[
            "weather_value"
        ] = (
            gdf[
                id_column
            ]
            .map(
                st.session_state[
                    "map_weather_values"
                ]
            )
        )

    else:

        # Map stays visible before the weather
        # download is run.
        gdf[
            "weather_value"
        ] = None


    color_column = (
        "weather_value"
    )



# Convert GeoDataFrame to GeoJSON
geojson = (
    gdf.__geo_interface__
)



# Interactive choropleth
if color_mode == "Area category":

    fig = px.choropleth_map(
        gdf,
        geojson=geojson,
        locations=id_column,
        featureidkey=(
            f"properties.{id_column}"
        ),
        color=color_column,
        hover_name=label_column,
        center={
            "lat": 64.5,
            "lon": 11.0
        },
        zoom=3.4,
        opacity=0.55,
        map_style="carto-positron"
    )


else:

    if weather_property == "Temperature":

        color_label = (
            "Mean temperature (°C)"
        )

    else:

        color_label = (
            "Mean precipitation (mm/hour)"
        )


    fig = px.choropleth_map(
        gdf,
        geojson=geojson,
        locations=id_column,
        featureidkey=(
            f"properties.{id_column}"
        ),
        color="weather_value",
        hover_name=label_column,
        hover_data={
            "weather_value": ":.2f"
        },
        labels={
            "weather_value":
                color_label
        },
        center={
            "lat": 64.5,
            "lon": 11.0
        },
        zoom=3.4,
        opacity=0.60,
        map_style="carto-positron",
        color_continuous_scale="Viridis"
    )


# Highlight currently selected area
current_selected_area = st.session_state.get(
    "selected_area"
)

current_selected_type = st.session_state.get(
    "selected_area_type"
)

expected_type = (
    "EL"
    if area_type == "Electricity areas"
    else "VASS"
)

if (
    current_selected_area is not None
    and current_selected_type == expected_type
    and current_selected_area in gdf[id_column].values
):

    selected_gdf = gdf[
        gdf[id_column] == current_selected_area
    ]

    selected_geojson = (
        selected_gdf.__geo_interface__
    )

    highlight = px.choropleth_map(
        selected_gdf,
        geojson=selected_geojson,
        locations=id_column,
        featureidkey=f"properties.{id_column}",
        color_discrete_sequence=[
            "rgba(0,0,0,0)"
        ],
        center={
            "lat": 64.5,
            "lon": 11.0
        },
        zoom=3.4
    )

    for trace in highlight.data:

        trace.update(
            showscale=False,
            marker_line_width=5,
            marker_line_color="black",
            marker_opacity=0
        )

        fig.add_trace(trace)
        
        

# Map title
if color_mode == "Area category":

    map_title = (
        f"{area_type} – Area Categories"
    )


else:

    map_title = (
        f"{area_type} – "
        f"{weather_property}"
    )


fig.update_layout(
    title=map_title,
    margin={
        "r": 0,
        "t": 45,
        "l": 0,
        "b": 0
    },
    height=700
)



# Show map and capture selection

event = st.plotly_chart(
    fig,
    use_container_width=True,
    on_select="rerun",
    selection_mode="points",
    key="region_map"
)

# Extract selected region
selected_area = None


if (
    event
    and event.selection
    and event.selection.points
):

    point = (
        event.selection.points[
            0
        ]
    )

    selected_area = point.get(
        "location"
    )


# Save selection in session state
if selected_area is not None:

    if area_type == "Electricity areas":

        st.session_state[
            "selected_area_type"
        ] = "EL"


    else:

        st.session_state[
            "selected_area_type"
        ] = "VASS"


    st.session_state[
        "selected_area"
    ] = selected_area


    st.success(
        f"Selected area: "
        f"{selected_area}"
    )

# Persistent shared selection
if "selected_area" in st.session_state:

    st.info(
        "Current shared selection: "
        f"{st.session_state.get('selected_area_type')} "
        f"{st.session_state.get('selected_area')}"
    )



# Current map settings
with st.expander(
    "Current map settings"
):

    st.write(
        {
            "Area type":
                area_type,

            "Colour mode":
                color_mode,

            "Weather property":
                weather_property,

            "Weather start date":
                start_date,

            "Weather end date":
                end_date
        }
    )