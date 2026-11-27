# --------------------------------------------------
# Importieren der benötigten Bibliotheken
# --------------------------------------------------

import streamlit as st
import folium as fm
import pandas as pd
import math

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_folium import st_folium
from pathlib import Path

# Eigene Module aus dem Paket "main" importieren
import main.data as data
import main.functions as functions


# --------------------------------------------------
# Datenquelle festlegen
# --------------------------------------------------

JSON_DATEI = (
    Path(__file__).resolve().parent
    / "main"
    / "Wanderwege.json"
)


# --------------------------------------------------
# Hauptklasse der Anwendung
# --------------------------------------------------

class WanderApp:

    def __init__(self):
        """Initialisiert die Datenverwaltung."""
        self.auswertung = None

    def lade_daten(self):
        """Lädt die Wanderrouten aus der JSON-Datei."""

        self.auswertung = data.Datenauswertung.from_file(
            JSON_DATEI
        )

    def zeige_filter(self):
        """Zeigt die Schieberegler für die Routensuche."""

        st.subheader("Wanderrouten filtern")

        routen = self.auswertung.data

        laengen = [
            route.laenge for route in routen
            if route.laenge is not None and route.laenge > 0
        ]

        dauern = [
            route.dauer for route in routen
            if route.dauer is not None and route.dauer > 0
        ]

        if not laengen or not dauern:
            st.info("Keine positiven Längen- oder Zeitangaben gefunden – Standardbereiche werden verwendet.")

        max_laenge = math.ceil(max(laengen) * 2) / 2 if laengen else 20.0
        max_dauer = math.ceil(max(dauern) * 2) / 2 if dauern else 8.0

        # Länge auswählen.
        st.markdown("**Weglänge (km)**")

        laengen_bereich = st.slider(
            "Gewünschte Länge",
            min_value=0.0,
            max_value=float(max(0.5, max_laenge)),
            value=(0.0, float(max(0.5, max_laenge))),
            step=0.5,
            label_visibility="collapsed",
            key="laengen_bereich"
        )

        # Dauer auswählen.
        st.markdown("**Dauer (Stunden)**")

        dauer_bereich = st.slider(
            "Gewünschte Dauer",
            min_value=0.0,
            max_value=float(max(0.5, max_dauer)),
            value=(0.0, float(max(0.5, max_dauer))),
            step=0.5,
            label_visibility="collapsed",
            key="dauer_bereich"
        )

        # Schwierigkeit auswählen.
        st.markdown("**Schwierigkeitsgrad (SAC)**")

        schwierigkeit_bereich = st.slider(
            "Gewünschter Schwierigkeitsgrad",
            min_value=1,
            max_value=6,
            value=(1, 6),
            step=1,
            label_visibility="collapsed",
            key="schwierigkeit_bereich"
        )

        return (
            laengen_bereich,
            dauer_bereich,
            schwierigkeit_bereich
        )

    def sortiere_routen(self, routen):
        """Sortiert die gefilterten Routen nach einem Attribut."""

        sortier_attribut = st.selectbox(
            "Sortieren nach",
            ["Name", "Schwierigkeit", "Länge", "Dauer"]
        )

        sortierung = st.radio(
            "Reihenfolge",
            ["Aufsteigend", "Absteigend"],
            horizontal=True
        )

        absteigend = sortierung == "Absteigend"

        if sortier_attribut == "Name":
            return functions.sortiere_nach_name(
                routen, absteigend
            )

        elif sortier_attribut == "Schwierigkeit":
            return functions.sortiere_nach_schwierigkeit(
                routen, absteigend
            )

        elif sortier_attribut == "Länge":
            return functions.sortiere_nach_laenge(
                routen, absteigend
            )

        else:
            return functions.sortiere_nach_dauer(
                routen, absteigend
            )

    def zeige_routentabelle(self, routen):
        """
        Zeigt die Wanderrouten in einer interaktiven Tabelle.

        Durch einen Doppelklick auf eine Zeile wird die
        entsprechende Route für die Kartenanzeige ausgewählt.
        """

        st.subheader("Gefundene Wanderrouten")

        routen_tabelle = []

        for index, route in enumerate(routen):
            routen_tabelle.append({
                "Nr.": index + 1,
                "Name": route.name,
                "Schwierigkeit": route.schwierigkeit,
                "Länge (km)": route.laenge,
                "Dauer (Stunden)": route.dauer,
                "Punkte": route.n_samples()
            })

        df = pd.DataFrame(routen_tabelle)

        grid_builder = GridOptionsBuilder.from_dataframe(df)

        grid_builder.configure_selection(
            selection_mode="multiple",
            use_checkbox=False
        )

        doppelklick_handler = JsCode("""
            function(params) {
                params.node.setSelected(true, false);
            }
        """)

        grid_builder.configure_grid_options(
            onRowDoubleClicked=doppelklick_handler
        )

        grid_options = grid_builder.build()

        tabellen_ergebnis = AgGrid(
            df,
            gridOptions=grid_options,
            height=400,
            theme="streamlit",
            allow_unsafe_jscode=True,
            update_on=["selectionChanged"],
            key="wanderrouten_tabelle"
        )

        ausgewaehlte_zeilen = tabellen_ergebnis.get(
            "selected_rows"
        )

        if ausgewaehlte_zeilen is None:
            return []

        if isinstance(ausgewaehlte_zeilen, pd.DataFrame):
            ausgewaehlte_zeilen = ausgewaehlte_zeilen.to_dict(
                "records"
            )

        if len(ausgewaehlte_zeilen) == 0:
            return []

        ausgewaehlte_nummern = []

        for zeile in ausgewaehlte_zeilen:
            if isinstance(zeile, dict) and "Nr." in zeile:
                ausgewaehlte_nummern.append(int(zeile["Nr."]))

        return [
            route for index, route in enumerate(routen)
            if (index + 1) in ausgewaehlte_nummern
        ]

    def zeige_routen_auf_karte(self, routen):
        """Zeigt die ausgewählten Routen auf einer Folium-Karte."""

        karte = fm.Map(
            location=[47.714849, 10.312662],
            zoom_start=11,
            control_scale=True
        )

        farben = [
            "blue", "red", "green",
            "purple", "orange", "darkred"
        ]

        for index, route in enumerate(routen):

            if not route.koordinaten:
                continue

            fm.PolyLine(
                locations=route.koordinaten,
                color=farben[index % len(farben)],
                weight=5,
                opacity=0.8,
                tooltip=route.name
            ).add_to(karte)

            fm.Marker(
                location=route.koordinaten[0],
                tooltip=f"Start: {route.name}"
            ).add_to(karte)

            fm.Marker(
                location=route.koordinaten[-1],
                tooltip=f"Ende: {route.name}"
            ).add_to(karte)

        st_folium(
            karte,
            width=None,
            height=650,
            use_container_width=True
        )

    def zeige_ortsfilter(self):
        """
        Zeigt Eingabefelder für Start- und Endort sowie
        die dazugehörigen Suchradien an.
        """

        st.subheader("Start- und Endpunkt eingrenzen")

        spalte_start, spalte_ende = st.columns(2)

        with spalte_start:
            st.markdown("**Startpunkt**")

            startort = st.text_input(
                "Startort eingeben",
                placeholder="z. B. Kempten",
                key="startort"
            )

            start_radius = st.slider(
                "Radius um den Startpunkt (km)",
                min_value=1,
                max_value=50,
                value=10,
                key="start_radius"
            )

        with spalte_ende:
            st.markdown("**Endpunkt**")

            endort = st.text_input(
                "Endort eingeben",
                placeholder="z. B. Oberstdorf",
                key="endort"
            )

            end_radius = st.slider(
                "Radius um den Endpunkt (km)",
                min_value=1,
                max_value=50,
                value=10,
                key="end_radius"
            )

        return startort, start_radius, endort, end_radius

    def run(self):
        """Steuert den gesamten Ablauf der Anwendung."""

        st.set_page_config(
            page_title="Wander Routen Finder",
            layout="wide"
        )

        st.title("Wander Routen Finder")

        try:
            self.lade_daten()

        except (FileNotFoundError, ValueError, TypeError) as error:
            st.error(f"Fehler beim Laden der Daten: {error}")
            return

        filterwerte = self.zeige_filter()

        if filterwerte is None:
            return

        (
            laengen_bereich,
            dauer_bereich,
            schwierigkeit_bereich
        ) = filterwerte

        (
            startort,
            start_radius,
            endort,
            end_radius
        ) = self.zeige_ortsfilter()

        if st.button(
            "Wanderrouten suchen",
            type="primary",
            key="wanderrouten_suchen"
        ):

            gefilterte_routen = functions.filter_nach_bereich(
                self.auswertung.data,
                laengen_bereich[0],
                laengen_bereich[1],
                dauer_bereich[0],
                dauer_bereich[1],
                schwierigkeit_bereich[0],
                schwierigkeit_bereich[1]
            )

            start_koordinaten = None

            if startort.strip():
                start_koordinaten = functions.ermittle_koordinaten(
                    startort
                )

                if start_koordinaten is None:
                    st.error(
                        f"Startort '{startort}' wurde nicht gefunden."
                    )
                    return

            end_koordinaten = None

            if endort.strip():
                end_koordinaten = functions.ermittle_koordinaten(
                    endort
                )

                if end_koordinaten is None:
                    st.error(
                        f"Endort '{endort}' wurde nicht gefunden."
                    )
                    return

            gefilterte_routen = functions.filter_nach_start_und_ende(
                gefilterte_routen,
                start_koordinaten=start_koordinaten,
                end_koordinaten=end_koordinaten,
                start_radius=start_radius,
                end_radius=end_radius
            )

            st.session_state["gefilterte_routen"] = gefilterte_routen

        if "gefilterte_routen" not in st.session_state:
            st.info(
                "Stelle deine Filter ein und starte die Suche."
            )
            return

        gefilterte_routen = st.session_state["gefilterte_routen"]

        st.divider()

        if not gefilterte_routen:
            st.warning("Keine passenden Wanderrouten gefunden.")
            return

        st.success(
            f"{len(gefilterte_routen)} passende Wanderrouten gefunden."
        )

        ausgewaehlte_routen = self.zeige_routentabelle(
            gefilterte_routen
        )

        st.divider()

        column1, column2 = st.columns([1, 3])

        with column1:

            st.subheader("Ausgewählte Routen")

            if ausgewaehlte_routen:

                for route in ausgewaehlte_routen:

                    with st.expander(route.name):

                        st.write(
                            f"**Schwierigkeit:** {route.schwierigkeit}"
                        )
                        st.write(f"**Länge:** {route.laenge} km")
                        st.write(f"**Dauer:** {route.dauer} Stunden")
                        st.write(f"**Koordinatenpunkte:** {route.n_samples()}")

            else:
                st.info(
                    "Wähle Routen aus, um sie auf der Karte anzuzeigen."
                )

        with column2:

            self.zeige_routen_auf_karte(
                ausgewaehlte_routen
            )


# --------------------------------------------------
# Einstiegspunkt der Anwendung
# --------------------------------------------------

if __name__ == "__main__":

    app = WanderApp()
    app.run()