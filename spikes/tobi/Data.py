import json
import folium
import streamlit as st
from streamlit_folium import st_folium

# Seite wird konfiguriert
st.set_page_config(page_title="Wanderkarte Tannheimer Tal", layout="wide")
st.title("Interaktive Wanderkarte")

# Daten werden geladen "KI"
with open("wanderwege.geojson", "r", encoding="utf-8") as file:
    daten = json.load(file)

# Nur Linien behalten "KI"
alle_routen = []
for f in daten["features"]:
    geometrie_typ = f["geometry"]["type"]
    #testet ob es sich um eine Linie handelt und nicht nur um einen Punkt
    if geometrie_typ == "LineString" or geometrie_typ == "MultiLineString":
        alle_routen.append(f)

# Alle Routen-Namen aus den Eigenschaften der Features auslesen und in einer Liste speichern
routen_namen = []
for f in alle_routen:
    eigenschaften = f.get("properties", {})
    name = eigenschaften.get("name")
    
    # Prüfen, ob ein Name da ist und ob er noch nicht in der Liste steht
    if name != None:
        if name not in routen_namen:
            routen_namen.append(name)

# Namen alphabetisch sortieren
routen_namen.sort()

# erstellt die Überschrift der Seitenleiste
st.sidebar.header("Filter & Übersicht")

# Auswahlliste für die Routen
optionen = ["Alle benannten Routen anzeigen"] + routen_namen    #mögliche Optionen für die Auswahlbox
auswahl = st.sidebar.selectbox("Wähle eine Wanderroute aus:", options=optionen) #erstellt die Auswahlbox und fügt die Optionen ein

# Checkbox für große Wegenetze
netze_ausblenden = st.sidebar.checkbox("Große Sammel-Wegenetze ausblenden", value=True)

# Daten filtern
gefilterte_routen = []  #String erstellen in den alle gefilterten Routen gespeichert werden

for f in alle_routen:
    # Eigenschaften und Name der Route auslesen und in Variablen speichern
    eigenschaften = f.get("properties", {})
    name = eigenschaften.get("name")
    
    # Wenn kein Name da ist, Feature überspringen
    if name == None:
        continue
        
    # Große Wegenetze herausfiltern/überspringen, wenn die Checkbox an ist und nach allen benannten Routen geschaut wird
    if netze_ausblenden == True:
        name_klein = name.lower()
        if "lokale" in name_klein or "wegenetz" in name_klein or "wanderwege" in name_klein:
            if auswahl == "Alle benannten Routen anzeigen":
                continue

    # append fügt die aktuelle Route der Liste hinzu, wenn sie den Filterkriterien entspricht
    if auswahl == "Alle benannten Routen anzeigen":
        gefilterte_routen.append(f)
    elif name == auswahl:
        gefilterte_routen.append(f)

#Anzahl der gefilterten Routen wird in der Seitenleiste angezeigt
st.sidebar.info(f"Angezeigte Routen: {len(gefilterte_routen)}")

# Hier wird die Karte erstellt "topologische Ansicht"
karte = folium.Map(
    location=[47.55, 10.45],
    zoom_start=12,
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Kartendaten: © OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: © OpenTopoMap (CC-BY-SA)"
)

# Routen werden gezeichnet "durch Feature werden die einzelnen Wanderwege durchgegangen und ihre Eigenschaften ausgelesen"
for feature in gefilterte_routen:
    eigenschaften = feature.get("properties", {})
    routen_name = eigenschaften.get("name", "Route")
    schwierigkeit = eigenschaften.get("symbol", "Keine Angabe")
    
    # Text für das Popup zusammenbauen (<b> = fett, <br> = Zeilenumbruch)
    popup_text = "<b>Route:</b> " + routen_name + "<br><b>Schwierigkeit:</b> " + schwierigkeit

    folium.GeoJson(
        feature,
        # Optik für die Wanderrouten (Farbe, Dicke, Transparenz)
        style_function=lambda x: {
            "color": "#d95f02",
            "weight": 3,
            "opacity": 0.9
        },
        # Das passiert mit der Linie beim drüberhovern 
        highlight_function=lambda x: {
            "color": "#1b9e77",
            "weight": 6,
            "opacity": 1.0
        },
        tooltip="<b>" + routen_name + "</b>", #Tipp beim drüberhovern
        popup=folium.Popup(popup_text, max_width=250)   #Popup-Fenster, beim anklicken
    ).add_to(karte)

# Karte in Streamlit anzeigen
st_folium(karte, width=1100, height=650, returned_objects=[])