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
countries = pd.read_csv(
    "https://r2.datahub.io/clt98ab600006l708tkbrtzel/master/raw/data.csv"
)

st.title("Airport Network")
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


countries_filter = st.multiselect("Countries", countries["Name"].tolist())

selected_airports = airports.loc[
    (airports.id.isin(runways.loc[runways.length_ft <= rwy_length, "airport_ref"]))
    & (airports.elevation_ft <= elevation)
    & (airports.type.isin(airport_type))
]

if countries_filter:
    selected_airports = selected_airports.loc[
        selected_airports.iso_country.isin(
            countries.loc[countries["Name"].isin(countries_filter), "Code"]
        )
    ]

with st.expander("Data"):
    st.dataframe(selected_airports, hide_index=True)

unsched_airports = pdk.Layer(
    "ScatterplotLayer",
    selected_airports.loc[selected_airports.scheduled_service == "no"],
    get_position=["longitude_deg", "latitude_deg"],
    auto_highlight=True,
    get_radius=10_000,
    get_fill_color=[255, 255, 200, 140],
    pickable=True,
)

sched_airports = pdk.Layer(
    "ScatterplotLayer",
    selected_airports.loc[selected_airports.scheduled_service == "yes"],
    get_position=["longitude_deg", "latitude_deg"],
    auto_highlight=True,
    get_radius=10_000,
    get_fill_color=[255, 0, 0, 140],
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


st.pydeck_chart(
    pdk.Deck(layers=[sched_airports, unsched_airports], initial_view_state=view_state)
)
