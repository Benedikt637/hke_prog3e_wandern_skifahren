import json
import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="Wanderkarte Tannheimer Tal", layout="wide")
st.title("Interaktive Wanderkarte")

@st.cache_data
def lade_daten():
    with open("wanderwege.geojson", "r", encoding="utf-8") as file:
        daten = json.load(file)
    
    # Nur Linien behalten
    linien = [
        f for f in daten["features"] 
        if f["geometry"]["type"] in ["LineString", "MultiLineString"]
    ]
    return linien

alle_routen = lade_daten()

# --- SEITENLEISTE ZUM AUFRÄUMEN ---
st.sidebar.header("Filter & Übersicht")

# 1. Alle verfügbaren Routennamen sammeln
routen_namen = sorted(list(set(
    f.get("properties", {}).get("name") 
    for f in alle_routen 
    if f.get("properties", {}).get("name")
)))

# 2. Auswahlmenü: Eine bestimmte Route oder alle anzeigen
auswahl = st.sidebar.selectbox(
    "Wähle eine Wanderroute aus:",
    options=["Alle benannten Routen anzeigen"] + routen_namen
)

# 3. Option zum Ausblenden von riesigen Wegenetzen (wie "lokale beschilderte Wanderwege")
netze_ausblenden = st.sidebar.checkbox("Große Sammel-Wegenetze ausblenden", value=True)

# --- DATEN FILTERN ---
gefilterte_routen = []
for f in alle_routen:
    name = f.get("properties", {}).get("name")
    
    # Unbenannte Pfade ignorieren für bessere Übersicht
    if not name:
        continue
        
    # Riesige Wegenetz-Relationen herausfiltern, falls gewünscht
    if netze_ausblenden and ("lokale" in name.lower() or "wegenetz" in name.lower() or "wanderwege" in name.lower()):
        if auswahl == "Alle benannten Routen anzeigen":
            continue

    # Nach gewählter Route filtern
    if auswahl == "Alle benannten Routen anzeigen" or name == auswahl:
        gefilterte_routen.append(f)

st.sidebar.info(f"Angezeigte Routen: {len(gefilterte_routen)}")

# --- KARTE ZEICHNEN ---
karte = folium.Map(
    location=[47.55, 10.45], # Zentriert auf den Ausschnitt im Bild (Wertach / Jungholz / Tannheimer Tal)
    zoom_start=12,
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Kartendaten: © OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: © OpenTopoMap (CC-BY-SA)"
)

for feature in gefilterte_routen:
    eigenschaften = feature.get("properties", {})
    routen_name = eigenschaften.get("name", "Route")
    schwierigkeit = eigenschaften.get("sac_scale", "Keine Angabe")

    folium.GeoJson(
        feature,
        style_function=lambda x: {
            "color": "#d95f02",
            "weight": 3, # Etwas dünnere Linien für bessere Übersicht
            "opacity": 0.9
        },
        highlight_function=lambda x: {
            "color": "#1b9e77",
            "weight": 6,
            "opacity": 1.0
        },
        tooltip=f"<b>{routen_name}</b>",
        popup=folium.Popup(f"<b>Route:</b> {routen_name}<br><b>Schwierigkeit:</b> {schwierigkeit}", max_width=250)
    ).add_to(karte)

st_folium(karte, width=1100, height=650, returned_objects=[])
