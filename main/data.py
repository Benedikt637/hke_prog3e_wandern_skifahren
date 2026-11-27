import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Any, Union


# Hilfsfunktion, die verschiedene Eingabetypen (int, float, Komma- oder Punkt-Strings, None)
# sicher in einen float umwandelt und bei ungültigen Werten auf einen Standardwert zurückfällt
def _parse_float(wert: Any, default: float = 0.0) -> float:
    # None und Booleans (in Python Unterklassen von int) abfangen, damit sie nicht falsch geparst werden
    if wert is None or isinstance(wert, bool):
        return default
    # Zahlenwerte direkt in float konvertieren
    if isinstance(wert, (int, float)):
        return float(wert)
    # Zeichenketten bereinigen (z. B. deutsches Komma durch Punkt ersetzen) und in float umwandeln
    if isinstance(wert, str):
        bereinigt = wert.strip().replace(",", ".")
        try:
            return float(bereinigt)
        except ValueError:
            return default
    # Für alle sonstigen Typen den Standardwert zurückgeben
    return default


# erstellt eine Datenklasse Wanderdaten, die die gewünschten Eigenschaften einer Wanderroute speichert
@dataclass
class Wanderdaten:
    name: str
    schwierigkeit: str
    dauer: float
    laenge: float
    # default_factory=list sorgt dafür, dass die Listen standardmäßig leer sind, wenn keine Werte übergeben werden
    start_koordinaten: List[float] = field(default_factory=list)  # [lat, lon]
    koordinaten: List[List[float]] = field(default_factory=list)  # [[lat, lon], ...]

    # Methode, die die Anzahl der Koordinatenpunkte zurückgibt
    def n_samples(self) -> int:
        """Gibt die Anzahl der Koordinatenpunkte zurück."""
        return len(self.koordinaten)


# Reader für JSON- und GeoJSON-Dateien
class JsonDataReader:
    file_format = ".json"

    # Methode zum Einlesen von JSON-Dateien und Erstellen von Wanderdaten-Instanzen
    def read(self, file) -> List[Wanderdaten]:
        # öffnet die Datei im Lesemodus mit UTF-8-Kodierung und lädt den Inhalt als JSON
        with open(file, "r", encoding="utf-8") as f:
            inhalt = json.load(f)

        # Flexibel: Verarbeitet einzelne Objekte, Listen oder GeoJSON-FeatureCollections
        # überprüft, ob die Daten in einem Dictionary vorliegen
        if isinstance(inhalt, dict):
            # Unterscheidet, ob die Daten in "features" liegen (GeoJSON FeatureCollection) oder flach im Root
            if "features" in inhalt:
                items = inhalt["features"]
            # wenn die Daten flach im Root liegen, werden sie in eine Liste umgewandelt
            else:
                items = [inhalt]
        # wenn die Daten bereits in einer Liste vorliegen, werden sie direkt übernommen
        elif isinstance(inhalt, list):
            items = inhalt
        # wenn die Daten weder in einem Dictionary noch in einer Liste vorliegen, werden sie in eine Liste umgewandelt
        else:
            items = [inhalt]

        routen = []
        for item in items:
            # Unterscheidet, ob die Attributdaten in "properties" liegen (GeoJSON) oder direkt im Objekt
            props = item.get("properties", item)

            # Koordinaten auslesen (unterstützt GeoJSON "geometry.coordinates" oder direkte "coordinates")
            raw_coords = []
            if "geometry" in item and "coordinates" in item["geometry"]:
                raw_coords = item["geometry"]["coordinates"]
            elif "coordinates" in item:
                raw_coords = item["coordinates"]

            # WICHTIG: GeoJSON speichert [lon, lat] (ggf. mit Höhe) -> Für Folium in [lat, lon] umwandeln
            folium_coords = [[lat, lon] for lon, lat, *_ in raw_coords] if raw_coords else []

            # Das erste Koordinatenpaar als Start-Koordinate extrahieren, falls vorhanden
            start_coord = folium_coords[0] if folium_coords else []

            # Erstellen einer Wanderdaten-Instanz mit den extrahierten Informationen und Feld-Fallbacks
            route = Wanderdaten(
                name=props.get("name", "Unbekannte Route"),
                schwierigkeit=props.get("sac_skala", props.get("schwierigkeit", "Unbekannt")),
                dauer=_parse_float(
                    props.get("dauer_stunden", props.get("dauer_Stunden", props.get("dauer", props.get("dauer_h", 0.0))))
                ),
                laenge=_parse_float(
                    props.get("distanz_km", props.get("laenge", props.get("laenge_km", 0.0)))
                ),
                start_koordinaten=start_coord,
                koordinaten=folium_coords
            )
            # Die erstellte Route wird der Liste der Routen hinzugefügt
            routen.append(route)

        # routen wird an from_file zurückgegeben, die daraus eine Instanz von Datenauswertung erstellt (auswertung.data)
        return routen


# Klasse Datenauswertung, die die eingelesenen Wanderdaten verwaltet und bereitstellt
class Datenauswertung:
    # verfügbare Reader nach Dateiendung
    readers = {
        ".json": JsonDataReader(),
    }

    # nimmt eine einzelne Wanderdaten-Instanz oder eine Liste davon entgegen
    def __init__(self, data: Union[Wanderdaten, List[Wanderdaten]]):
        self.data = data if isinstance(data, list) else [data]

    # Attribut-Property für lesenden Zugriff auf die Routenliste und Kapselung von _data
    @property
    def data(self) -> List[Wanderdaten]:
        return self._data

    # Setter für die Daten, der sicherstellt, dass mindestens eine Route übergeben wird
    @data.setter
    def data(self, value: Union[Wanderdaten, List[Wanderdaten]]) -> None:
        # wenn value eine Liste ist, wird sie direkt übernommen
        if isinstance(value, list):
            items = value
        # wenn value ein Tupel ist, wird es in eine Liste umgewandelt
        elif isinstance(value, tuple):
            items = list(value)
        # wenn value eine einzelne Instanz von Wanderdaten ist, wird sie in eine Liste umgewandelt
        else:
            items = [value]

        # verhindert leere Routenlisten
        if not items:
            raise ValueError("Es muss mindestens eine Route übergeben werden.")

        # speichert die Daten im privaten Attribut _data
        self._data = items

    # Klassenmethode, die eine Instanz von Datenauswertung aus einer Datei erstellt
    @classmethod
    def from_file(cls, file):
        # ermittelt die Dateiendung und konvertiert sie in Kleinbuchstaben
        suffix = Path(file).suffix.lower()
        # prüft, ob ein Reader für das angegebene Dateiformat registriert ist
        if suffix not in cls.readers:
            raise ValueError(f"Kein Reader für das Format '{suffix}' registriert.")
        # ruft den passenden Reader auf und erstellt die Datenauswertung-Instanz
        reader = cls.readers[suffix]
        return cls(reader.read(file))

    # gibt eine kurze Statusmeldung über die Anzahl geladener Routen zurück
    def status(self):
        return f"{len(self.data)} Routen geladen"


# Standardpfad zur Wanderwege-Datei relativ zu dieser data.py
STANDARD_DATEI = Path(__file__).resolve().parent / "Wanderwege.json"

# wird nur ausgeführt, wenn data.py direkt gestartet wird, nicht beim Import durch app.py
if __name__ == "__main__":
    auswertung = Datenauswertung.from_file(STANDARD_DATEI)
    print(auswertung.status())