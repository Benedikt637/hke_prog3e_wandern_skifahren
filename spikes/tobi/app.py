import html

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from Data import lade_gipfel_daten

st.set_page_config(page_title="Wander-App", layout="wide")
st.title("Berggipfel bei Oberstdorf")

try:
    gipfel = lade_gipfel_daten()
except FileNotFoundError:
    st.info("Noch keine Gipfeldaten vorhanden. Starte zuerst download.py.")
    gipfel = pd.DataFrame(columns=["name", "hoehe", "lat", "lon"])
except (OSError, ValueError) as error:
    st.error(f"Die lokalen Gipfeldaten konnten nicht gelesen werden: {error}")
    gipfel = pd.DataFrame(columns=["name", "hoehe", "lat", "lon"])

karte = folium.Map(
    location=[47.41, 10.27],
    zoom_start=12,
    tiles="OpenStreetMap",
)

for _, row in gipfel.iterrows():
    name = html.escape(str(row["name"]))
    popup = name
    if pd.notna(row["hoehe"]):
        popup += f"<br>Höhe: {html.escape(str(row['hoehe']))} m"

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=7,
        color="darkgreen",
        fill=True,
        fill_color="green",
        fill_opacity=0.9,
        tooltip=name,
        popup=folium.Popup(popup),
    ).add_to(karte)

st_folium(karte, width=1000, height=600)

if gipfel.empty:
    st.warning("Keine lokalen Gipfeldaten vorhanden.")
