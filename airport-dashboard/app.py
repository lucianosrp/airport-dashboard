import pandas as pd
import pydeck as pdk
import streamlit as st


@st.cache_data
def get_airports():
    return pd.read_csv("https://davidmegginson.github.io/ourairports-data/airports.csv")


@st.cache_data
def get_runways():
    return pd.read_csv("https://davidmegginson.github.io/ourairports-data/runways.csv")


runways = get_runways()
airports = get_airports()

st.title("Airport Network")

airport_type = st.multiselect("Airport Type", airports.type.unique())

rwy_length = st.slider(
    "Runway Length:",
    runways.length_ft.min(),
    runways.length_ft.max(),
    runways.length_ft.mean(),
    format="%d ft",
)

elevation = st.slider(
    "Elevation",
    airports.elevation_ft.min(),
    airports.elevation_ft.max(),
    airports.elevation_ft.mean(),
    format="%d ft",
)

selected_airports = airports.loc[
    (airports.id.isin(runways.loc[runways.length_ft <= rwy_length, "airport_ref"]))
    & (airports.elevation_ft <= elevation)
    & (airports.type.isin(airport_type))
    ]

st.dataframe(selected_airports, hide_index=True)

airports_chart = pdk.Layer(
    "ScatterplotLayer",
    selected_airports,
    get_position=["longitude_deg", "latitude_deg"],
    auto_highlight=True,
    get_radius=10_000,  # Radius is given in meters
    get_fill_color=[255, 255, 200, 140],  # Set an RGBA value for fill
    pickable=True,
)

st.metric(
    label="Airports selected",
    value=f"{selected_airports.shape[0]:,}",
)

mean_lat = selected_airports.latitude_deg.mean()
mean_lon = selected_airports.longitude_deg.mean()

view_state = pdk.ViewState(
    longitude=mean_lon,
    latitude=mean_lat,
    zoom=3,
)

st.pydeck_chart(pdk.Deck(layers=[airports_chart], initial_view_state=view_state))
