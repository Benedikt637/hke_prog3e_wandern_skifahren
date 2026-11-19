import json
import folium
import streamlit as st
from streamlit_folium import st_folium
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union

#erstellt eine Datenklasse Wanderdaten, die die gewünschten Eigenschaften einer Wanderroute speichert
@dataclass
class Wanderdaten:
    name: str
    schwierigkeit: str
    dauer: float
    laenge: float
    #default_factory=list sorgt dafür, dass die Listen standardmäßig leer sind, wenn keine Werte übergeben werden "KI"
    start_koordinaten: List[float] = field(default_factory=list)  # [lat, lon]
    koordinaten: List[List[float]] = field(default_factory=list)  # [[lat, lon], ...]

    #Methode, die die Anzahl der Koordinatenpunkte zurückgibt
    def n_samples(self) -> int:
        """Gibt die Anzahl der Koordinatenpunkte zurück."""
        return len(self.koordinaten)

#Reader für JSON-Dateien
class JsonDataReader:
    file_format = ".json"

    #Methode zum Einlesen von JSON-Dateien und Erstellen von Wanderdaten-Instanzen
    def read(self, file) -> List[Wanderdaten]:
        #öffnet die Datei im Lesemodus mit UTF-8-Kodierung und lädt den Inhalt als JSON
        with open(file, "r", encoding="utf-8") as f:
            inhalt = json.load(f)

        # Flexibel: Verarbeitet einzelne Objekte, Listen oder GeoJSON-FeatureCollections
        #überprüft ob die Daten in einem Dictionary vorliegen
        if isinstance(inhalt, dict):
            # Unterscheidet, ob die Daten in "features" liegen (GeoJSON) oder flach im Root
            if "features" in inhalt:
                items = inhalt["features"]
            #wenn die Daten flach im Root liegen, werden sie in eine Liste umgewandelt
            else:
                items = [inhalt]
        #wenn die Daten bereits in einer Liste vorliegen, werden sie direkt übernommen
        elif isinstance(inhalt, list):
            items = inhalt
        #wenn die Daten weder in einem Dictionary noch in einer Liste vorliegen, werden sie in eine Liste umgewandelt
        else:
            items = [inhalt]

        routen = []
        for item in items:
            # Unterscheidet, ob die Daten in "properties" liegen (GeoJSON) oder flach im Root
            props = item.get("properties", item)
            
            # Koordinaten auslesen (unterstützt GeoJSON "geometry" oder direkte "coordinates") "KI"
            raw_coords = []
            if "geometry" in item and "coordinates" in item["geometry"]:
                raw_coords = item["geometry"]["coordinates"]
            elif "coordinates" in item:
                raw_coords = item["coordinates"]

            # WICHTIG: GeoJSON speichert [lon, lat] -> Für Folium in [lat, lon] umwandeln!
            folium_coords = [[lat, lon] for lon, lat in raw_coords] if raw_coords else []
            
            # Das erste Element als Start-Koordinate extrahieren
            start_coord = folium_coords[0] if folium_coords else []

            # Erstellen einer Wanderdaten-Instanz mit den extrahierten Informationen
            route = Wanderdaten(
                name=props.get("name", "Unbekannte Route"),
                schwierigkeit=props.get("sac_skala", props.get("schwierigkeit", "Unbekannt")),
                dauer=float(props.get("dauer_Stunden", props.get("dauer", "Unbekannt"))),
                laenge=float(props.get("distanz_km", props.get("laenge", "Unbekannt"))),
                start_koordinaten=start_coord,
                koordinaten=folium_coords
            )
            #Die erstellte Route wird der Liste der Routen hinzugefügt
            routen.append(route)
        #routen wird an reader zurückgegeben, der sie dann an from_file weitergibt, die dann eine Instanz von Datenauswertung erstellt (auswertung.data)    
        return routen

#Klasse Datenauswertung, die die eingelesenen Wanderdaten verarbeitet und analysiert
class Datenauswertung:
    #verfügbarer Reader
    readers = {
        ".json": JsonDataReader(),
    }

    #wenn Liste, dann wird sie direkt übernommen, wenn einzelne Instanz, dann wird sie in eine Liste umgewandelt
    def __init__(self, data: Union[Wanderdaten, List[Wanderdaten]]):
        self.data = data if isinstance(data, list) else [data]

    #Attribut Optik, lesenden Zugriff auf die Daten und Kapselung
    @property
    def data(self) -> List[Wanderdaten]:
        return self._data

    #Setter für die Daten, der sicherstellt, dass mindestens eine Route übergeben wird und dass alle Elemente Instanzen von Wanderdaten sind
    @data.setter
    #mit Union kann der Setter sowohl eine einzelne Instanz von Wanderdaten als auch eine Liste von Instanzen akzeptieren
    def data(self, value: Union[Wanderdaten, List[Wanderdaten]]) -> None:
        #wenn value eine Liste ist, wird sie direkt übernommen
        if isinstance(value, list):
            items = value
        #wenn value ein Tupel ist, wird es in eine Liste umgewandelt
        elif isinstance(value, tuple):
            items = list(value)
        #wenn value eine einzelne Instanz von Wanderdaten ist, wird sie in eine Liste umgewandelt
        else:
            items = [value]

        if not items:
            raise ValueError("Es muss mindestens eine Route übergeben werden.")
        #speichert die Daten in einem privaten Attribut _data, um direkten Zugriff von außen zu verhindern und die Kapselung zu gewährleisten
        self._data = items

    #Methode, die eine Instanz von Datenauswertung aus einer Datei erstellt
    #classmethod, da die Klasse selbst als Parameter übergeben wird, aus der eine Instanz erstellt wird
    #bei Aufruf werden automatisch Unterklassen erzeugt
    @classmethod
    def from_file(cls, file):
        #Ermittelt die Dateiendung und konvertiert sie in Kleinbuchstaben
        suffix = Path(file).suffix.lower()
        #Prüft, ob ein Reader für das angegebene Dateiformat registriert ist
        if suffix not in cls.readers:
            raise ValueError(f"Kein Reader für das Format '{suffix}' registriert.")
        #Aufruf des entsprechenden Readers, der die Datei einliest und die Daten zurückgibt
        reader = cls.readers[suffix]
        #gibt die Daten an from_file zurück, die dann eine Instanz von Datenauswertung erstellt (auswertung.data)
        return cls(reader.read(file))

    def status(self):
        return f"{len(self.data)} Routen geladen"

#einlesen der Dateien und Ausgabe der Statusmeldung
auswertung = Datenauswertung.from_file("Wanderwege.json")
st.write(auswertung.status())


#Routen Namen in alphabetischer Reihenfolge, ohne Duplikate und ohne leere Namen
#geschweifte Klammern entfernen automatisch Duplikate
routen_namen = sorted({route.name for route in auswertung.data if route.name})