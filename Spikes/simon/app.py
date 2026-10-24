import streamlit as st
import folium as fm
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
column1, column2 = st.columns([1, 4])


#Nutzer Standort könnte Später mit "steamlit_js_eval import get_geolocation()" ermittelt werden
user_latitude = 47.715301 #Kempten: 47.7333 
user_longitude = 10.312754 #Kempten: 10.3167

with column1:
    st.text_input("Startort")

with column2:
    st.title("Wander Routen Finder")
    world_map = fm.Map(location=[user_latitude, user_longitude], zoom_start=14)
    st_folium(world_map, width=None, height=1000, use_container_width=True)
    