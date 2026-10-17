import streamlit as st
import folium as fm
from streamlit_folium import st_folium


#Standort könnte Später mit "steamlit_js_eval import get_geolocation()" ermittelt werden
user_latitude = 47.7333 #Kempten: 47.7333 
user_longitude = 10.3167 #Kempten: 10.3167
 
st.title("Wander Routen Finder")

world_map = fm.Map(location=[user_latitude, user_longitude], zoom_start=14)

st_folium(world_map, width=1000, height=1080)