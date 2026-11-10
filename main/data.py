import streamlit as st
from pyrosm import OSM
import geopandas as gpd

#-----Caching of the OSM data to avoid reloading it every time the app is run-----#
@st.cache_resource
def load_osm():
    return OSM("main/datasources/alps-latest.osm.pbf")

@st.cache_data
def load_walking_network():
    osm = load_osm()
    return osm.get_network(network_type="walking")


#-----Import of hiking trails-----#
hiking_routes = gpd.read_file("main/datasources/hiking_routes.geojson")

#-----Converts Timestamp-Columns to String Columns to avoid errors when displaying the hiking routes in the streamlit app-----#
hiking_routes["source:date"] = (
    hiking_routes["source:date"].astype(str)
)
hiking_routes["start_date"] = (
    hiking_routes["start_date"].astype(str)
)


#-----Get available route names-----#
available_routes = hiking_routes[hiking_routes["name"].notna()]
route_names = available_routes["name"].unique()