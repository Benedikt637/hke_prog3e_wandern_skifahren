import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Interaktive Karte", layout="wide")

st.title("Weil wir so supergeil drauf sind")
st.write("Erstellt mit Python, Folium und Streamlit.")

# Folium-Karte zentrieren (z. B. auf Deutschland / Bayern)
m = folium.Map(location=[47.65, 10.23], zoom_start=11)

# Einen Marker hinzufügen
folium.Marker(
    [47.65, 10.23],
    popup="Startpunkt",
    tooltip="Hier klicken"
).add_to(m)

# Karte in Streamlit rendern
st_data = st_folium(m, width=700, height=500)
