import folium
import streamlit as st
from streamlit_folium import st_folium
from Data import lade_wander_daten

st.set_page_config(page_title="Wander-App", layout="wide")

st.title("Wanderrouten")
st.write("Hier werden die Live-Daten mit echten GPS-Linien eingebunden.")

# Daten aus der Data.py laden
df = lade_wander_daten()

if not df.empty:
    # Karte initialisieren (Zentriert auf das Oberstdorfer Gebet)
    m = folium.Map(location=[47.41, 10.27], zoom_start=12)

    # GPS-Linien aus dem DataFrame auf der Karte einzeichnen
    for _, row in df.iterrows():
        if "coords" in row and isinstance(row["coords"], list):
            folium.PolyLine(
                locations=row["coords"],
                color="blue",
                weight=4,
                opacity=0.8,
                tooltip=row["title"],
            ).add_to(m)

            # Startmarker setzen
            folium.Marker(
                location=row["coords"][0],
                popup=row["title"],
                icon=folium.Icon(color="green", icon="play"),
            ).add_to(m)

    # Karte in Streamlit anzeigen
    st_folium(m, width=1000, height=500)

    # Tabelle für Rohdaten & Download-Button
    st.subheader("📋 Rohdaten der API")
    
    # Optional: coords-Spalte für eine saubere Tabellenansicht ausblenden
    df_display = df.drop(columns=["coords"]) if "coords" in df.columns else df
    st.dataframe(df_display, use_container_width=True)

else:
    st.warning("Es konnten keine Daten geladen werden. Bitte prüfen Sie die Verbindung oder die API-Parameter.")
