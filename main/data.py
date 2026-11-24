
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union


# Die Datenklasse speichert alle Eigenschaften einer einzelnen Wanderroute.
# Durch @dataclass werden unter anderem der Konstruktor (__init__)
# und weitere Standardmethoden automatisch erstellt.
@dataclass
class Wanderdaten:

    # Eindeutige ID der Wanderroute aus der JSON-Datei
    id: int

    # Name und Region der Wanderroute
    name: str
    region: str

    # SAC-Schwierigkeitsgrad, z. B. T1 oder T2
    schwierigkeit: str

    # Dauer und Länge werden als float gespeichert.
    # Optional erlaubt zusätzlich den Wert None, falls eine Angabe fehlt.
    dauer: Optional[float]
    laenge: Optional[float]

    # Startkoordinaten im Format [Breitengrad, Längengrad]
    # default_factory=list erstellt für jede Route eine eigene leere Liste.
    start_koordinaten: list[float] = field(default_factory=list)

    # Gesamter Koordinatenverlauf der Route
    # Format: [[Breitengrad, Längengrad], ...]
    koordinaten: list[list[float]] = field(default_factory=list)

    # Methode zur Ermittlung der Anzahl vorhandener Koordinatenpunkte
    def n_samples(self) -> int:
        """Gibt die Anzahl der Koordinatenpunkte einer Route zurück."""
        return len(self.koordinaten)


# Diese Klasse ist für das Einlesen der JSON-Datei zuständig.
# Sie wandelt die JSON-Daten in Wanderdaten-Objekte um.
class JsonDataReader:

    # Legt das unterstützte Dateiformat fest.
    file_format = ".json"

    # Hilfsmethode zur Umwandlung eines Wertes in float.
    # Wenn ein Wert fehlt oder ungültig ist, wird None zurückgegeben.
    @staticmethod
    def convert_float(value) -> Optional[float]:

        # Prüft, ob überhaupt ein Wert vorhanden ist.
        if value is None or value == "":
            return None

        # Versucht, den Wert in eine Fließkommazahl umzuwandeln.
        try:
            return float(value)

        # Falls die Umwandlung nicht möglich ist, wird None zurückgegeben.
        except (ValueError, TypeError):
            return None

    # Liest die JSON-Datei und gibt eine Liste von Wanderdaten-Objekten zurück.
    def read(self, file: Union[str, Path]) -> list[Wanderdaten]:

        # Öffnet die Datei mit UTF-8-Kodierung und lädt die JSON-Daten.
        with open(file, "r", encoding="utf-8") as f:
            inhalt = json.load(f)

        # Prüft, ob es sich um eine GeoJSON-FeatureCollection handelt.
        if isinstance(inhalt, dict) and "features" in inhalt:
            items = inhalt["features"]

        # Unterstützt zusätzlich eine direkt übergebene Liste von Routen.
        elif isinstance(inhalt, list):
            items = inhalt

        # Andere JSON-Strukturen werden nicht unterstützt.
        else:
            raise ValueError("Ungültige JSON-Struktur.")

        # Hier werden die fertigen Wanderdaten-Objekte gesammelt.
        routen = []

        # Jede Route innerhalb der JSON-Datei wird einzeln verarbeitet.
        for item in items:

            # Die Eigenschaften einer Route befinden sich bei GeoJSON
            # innerhalb des Schlüssels "properties".
            props = item.get("properties", item)

            # Die Geometrie enthält den Koordinatenverlauf der Route.
            geometry = item.get("geometry") or {}
            raw_coords = geometry.get("coordinates", [])

            # GeoJSON speichert Koordinaten als [Längengrad, Breitengrad].
            # Folium benötigt hingegen [Breitengrad, Längengrad].
            # Deshalb werden die Werte hier vertauscht.
            folium_coords = [
                [float(lat), float(lon)]
                for lon, lat in raw_coords
            ]

            # Die erste Koordinate wird als Startpunkt der Route verwendet.
            # Falls keine Koordinaten vorhanden sind, bleibt die Liste leer.
            start_coord = (
                folium_coords[0]
                if folium_coords else []
            )

            # Aus den JSON-Eigenschaften wird ein Wanderdaten-Objekt erstellt.
            route = Wanderdaten(

                # ID der Route aus den Eigenschaften übernehmen.
                id=props.get("id", 0),

                # Name der Route auslesen.
                # Falls kein Name vorhanden ist, wird ein Standardwert verwendet.
                name=props.get("name", "Unbekannte Route"),

                # Region der Route auslesen.
                region=props.get("region", "Unbekannt"),

                # SAC-Schwierigkeitsgrad auslesen.
                schwierigkeit=props.get("sac_skala", "Unbekannt"),

                # Dauer in Stunden aus dem JSON-Attribut übernehmen.
                # Der Schlüssel lautet in deiner Datei "dauer_stunden".
                dauer=self.convert_float(
                    props.get("dauer_stunden")
                ),

                # Streckenlänge in Kilometern auslesen.
                laenge=self.convert_float(
                    props.get("distanz_km")
                ),

                # Startpunkt und gesamten Koordinatenverlauf übernehmen.
                start_koordinaten=start_coord,
                koordinaten=folium_coords
            )

            # Das fertige Routenobjekt wird der Routenliste hinzugefügt.
            routen.append(route)

        # Gibt alle eingelesenen Wanderrouten an die aufrufende Stelle zurück.
        return routen



# Diese Klasse verwaltet die eingelesenen Wanderdaten.
# Sie stellt die Daten bereit und ermöglicht das Erstellen einer Instanz
# direkt aus einer JSON-Datei.
class Datenauswertung:

    # Dictionary mit den verfügbaren Readern.
    # Anhand der Dateiendung wird der passende Reader ausgewählt.
    readers = {
        ".json": JsonDataReader()
    }

    # Konstruktor: Übernimmt die eingelesenen Wanderdaten.
    def __init__(self, data: Union[Wanderdaten, list[Wanderdaten]]):

        # Übergibt die Daten an den Setter, der ihre Gültigkeit überprüft.
        self.data = data

    # Property ermöglicht den lesenden Zugriff auf die Daten.
    @property
    def data(self) -> list[Wanderdaten]:
        return self._data

    # Setter überprüft die übergebenen Daten und speichert sie intern.
    @data.setter
    def data(self, value):

        # Eine einzelne Route wird in eine Liste umgewandelt.
        if isinstance(value, tuple):
            items = list(value)

        elif isinstance(value, list):
            items = value

        else:
            items = [value]

        # Es muss mindestens eine Route vorhanden sein.
        if not items:
            raise ValueError(
                "Es muss mindestens eine Route vorhanden sein."
            )

        # Überprüft, ob alle Elemente tatsächlich Wanderdaten-Objekte sind.
        if not all(
            isinstance(route, Wanderdaten)
            for route in items
        ):
            raise TypeError(
                "Alle Elemente müssen Wanderdaten sein."
            )

        # Speichert die überprüften Daten im privaten Attribut.
        self._data = items

    # Klassenmethode zum Erstellen einer Datenauswertung aus einer Datei.
    # cls steht für die Klasse Datenauswertung selbst.
    @classmethod
    def from_file(cls, file):

        # Wandelt den übergebenen Dateipfad in ein Path-Objekt um.
        file = Path(file)

        # Überprüft, ob die angegebene Datei existiert.
        if not file.exists():
            raise FileNotFoundError(
                f"Datei nicht gefunden: {file}"
            )

        # Ermittelt die Dateiendung, z. B. .json.
        suffix = file.suffix.lower()

        # Prüft, ob ein passender Reader registriert ist.
        if suffix not in cls.readers:
            raise ValueError(
                f"Kein Reader für {suffix} registriert."
            )

        # Wählt den passenden Reader anhand der Dateiendung aus.
        reader = cls.readers[suffix]

        # Der Reader liest die Datei ein und erstellt Wanderdaten-Objekte.
        # Anschließend wird eine neue Datenauswertung erstellt.
        return cls(reader.read(file))

    # Gibt eine kurze Statusmeldung mit der Anzahl geladener Routen zurück.
    def status(self):
        return f"{len(self.data)} Routen geladen"