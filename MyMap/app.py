import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Interaktive Karte", layout="wide")

st.title("Weil wir so supergeil drauf sind")
st.write("wählen sie ihr Ziel aus")

# Folium-Karte zentrieren (z. B. auf Deutschland / Bayern)
m = folium.Map(location=[47.838, 10.187], zoom_start=11)

# Einen Marker hinzufügen

zeige_Wohnorte = st.checkbox("Wohnorte anzeigen")
zeige_Berge = st.checkbox("Berge anzeigen")

if zeige_Wohnorte:
    folium.Marker(
        [47.838, 10.187],
        popup="Hier wohnt Tobi",
        tooltip="Hier klicken",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [47.726, 10.304],
        popup="Hier wohnt Bene",
        tooltip="Hier klicken",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)

    folium.Marker(
        [47.71482032859724, 10.316141501942194],
        popup="Hier wohnt Simon",
        tooltip="Hier klicken",
        icon=folium.Icon(color="yellow", icon="home", prefix="fa")
    ).add_to(m)

if zeige_Berge:
    folium.Marker(
        [47.46982780253003, 10.476457757097364],
        popup='<b>Gaishorn</b><br><a href="https://www.komoot.com/de-de/highlight/162047" target="_blank">Auf Komoot ansehen</a>',
        tooltip="Hier klicken",
        icon=folium.Icon(color="gray", icon="mountain", prefix="fa")
    ).add_to(m)

# HTML-Inhalt für das Popup definieren
    html_inhalt = """
    <h4>Gipfelkreuz Drachenkopf</h4>
    <p>mords die Hätzerei</p>
    <a href="https://www.outdooractive.com/de/route/bergtour/tiroler-zugspitz-arena/auf-den-vorderen-drachenkopf-2303m-/104373307/" target="_blank">klick amol, des lohnt sich</a>
    """

# Popup-Objekt erstellen
    mein_popup = folium.Popup(html_inhalt, max_width=300)

# Marker mit dem Popup verknüpfen
    folium.Marker(
        [47.35783903461384, 10.92664809160939],
        popup=mein_popup,
        icon=folium.Icon(color="red", icon="mountain", prefix="fa")
    ).add_to(m)



suche_nach = st.text_input("Suche nach einem Ort")

# Karte in Streamlit rendern
st_data = st_folium(m, width=700, height=500)
