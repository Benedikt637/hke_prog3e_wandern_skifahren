import streamlit as st
from pyrosm import OSM


#-----Caching of the OSM data to avoid reloading it every time the app is run-----#
@st.cache_resource
def load_osm():
    return OSM("main/datasources/alps-latest.osm.pbf")

@st.cache_data
def load_walking_network():
    osm = load_osm()
    return osm.get_network(network_type="walking")