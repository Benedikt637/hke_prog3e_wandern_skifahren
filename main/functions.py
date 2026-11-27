# --------------------------------------------------
# Importieren der benötigten Bibliotheken
# --------------------------------------------------

import math
from functools import lru_cache

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# --------------------------------------------------
# Geocoding für Start- und Endpunkte
# --------------------------------------------------

# Geocoder für OpenStreetMap einmalig erstellen.
geocoder = Nominatim(user_agent="wander_routen_finder")

# Zwischen zwei Anfragen mindestens eine Sekunde warten.
geocode_mit_pause = RateLimiter(
    geocoder.geocode,
    min_delay_seconds=1
)


@lru_cache(maxsize=128)
def ermittle_koordinaten(ort):
    """
    Wandelt einen Ortsnamen in geografische Koordinaten um.

    Args:
        ort (str): Name des gesuchten Ortes.

    Returns:
        tuple | None: Breitengrad und Längengrad oder None.
    """

    if not ort or not ort.strip():
        return None

    try:
        ergebnis = geocode_mit_pause(
            ort.strip(),
            timeout=10
        )

        if ergebnis is None:
            return None

        return (
            ergebnis.latitude,
            ergebnis.longitude
        )

    except (GeocoderTimedOut, GeocoderServiceError):
        return None


def _ist_gueltiger_wert(wert):
    """Prüft, ob ein numerischer Wert (z. B. Länge oder Dauer) nutzbar ist."""
    if wert is None:
        return False
    if isinstance(wert, float) and math.isnan(wert):
        return False
    return wert >= 0


def _schwierigkeit_als_zahl(route):
    """Wandelt SAC-Schwierigkeitsgrade wie 'T2' oder 'T2+' in eine Zahl um."""
    try:
        text = (route.schwierigkeit or "").upper().split("+")[0].split("-")[0]
        return int(text.replace("T", "").strip())
    except (ValueError, AttributeError):
        return float("inf")


# --------------------------------------------------
# Sortierfunktionen
# --------------------------------------------------

def sortiere_nach_name(routen, absteigend=False):
    """
    Sortiert Wanderrouten alphabetisch nach ihrem Namen.
    """

    return sorted(
        routen,
        key=lambda route: (route.name or "").lower(),
        reverse=absteigend
    )


def sortiere_nach_schwierigkeit(routen, absteigend=False):
    """
    Sortiert nach dem SAC-Schwierigkeitsgrad.

    Die Zahl hinter dem T wird numerisch ausgewertet,
    damit beispielsweise T2 vor T10 einsortiert wird.
    """

    return sorted(
        routen,
        key=_schwierigkeit_als_zahl,
        reverse=absteigend
    )


def sortiere_nach_laenge(routen, absteigend=False):
    """
    Sortiert nach Streckenlänge.
    Routen ohne Längenangabe stehen immer am Ende.
    """

    bekannte = [
        route for route in routen
        if _ist_gueltiger_wert(route.laenge) and route.laenge > 0
    ]

    unbekannte = [
        route for route in routen
        if not (_ist_gueltiger_wert(route.laenge) and route.laenge > 0)
    ]

    bekannte.sort(
        key=lambda route: route.laenge,
        reverse=absteigend
    )

    return bekannte + unbekannte


def sortiere_nach_dauer(routen, absteigend=False):
    """
    Sortiert nach Dauer.
    Routen ohne Dauerangabe stehen immer am Ende.
    """

    bekannte = [
        route for route in routen
        if _ist_gueltiger_wert(route.dauer) and route.dauer > 0
    ]

    unbekannte = [
        route for route in routen
        if not (_ist_gueltiger_wert(route.dauer) and route.dauer > 0)
    ]

    bekannte.sort(
        key=lambda route: route.dauer,
        reverse=absteigend
    )

    return bekannte + unbekannte


# --------------------------------------------------
# Einfache Filterfunktionen
# --------------------------------------------------

def filter_nach_schwierigkeit(routen, schwierigkeit):
    """
    Filtert Routen nach einem bestimmten SAC-Schwierigkeitsgrad.
    """

    return [
        route for route in routen
        if route.schwierigkeit == schwierigkeit
    ]


def filter_nach_max_laenge(routen, max_laenge):
    """
    Filtert Routen nach einer maximalen Streckenlänge.
    """

    return [
        route for route in routen
        if _ist_gueltiger_wert(route.laenge)
        and route.laenge <= max_laenge
    ]


def filter_nach_max_dauer(routen, max_dauer):
    """
    Filtert Routen nach einer maximalen Dauer.
    """

    return [
        route for route in routen
        if _ist_gueltiger_wert(route.dauer)
        and route.dauer <= max_dauer
    ]


# --------------------------------------------------
# Kombinierter Filter für Länge, Dauer und Schwierigkeit
# --------------------------------------------------

def filter_nach_bereich(
    routen,
    min_laenge,
    max_laenge,
    min_dauer,
    max_dauer,
    min_schwierigkeit,
    max_schwierigkeit
):
    """
    Filtert Wanderrouten anhand von Länge, Dauer
    und SAC-Schwierigkeitsgrad.
    """

    gefilterte_routen = []

    for route in routen:

        if not _ist_gueltiger_wert(route.laenge) or not _ist_gueltiger_wert(route.dauer):
            continue

        schwierigkeit = _schwierigkeit_als_zahl(route)

        # Prüfen, ob alle Filterbereiche erfüllt sind.
        if (
            min_laenge <= route.laenge <= max_laenge
            and min_dauer <= route.dauer <= max_dauer
            and (
                math.isinf(schwierigkeit)
                or min_schwierigkeit <= schwierigkeit <= max_schwierigkeit
            )
        ):
            gefilterte_routen.append(route)

    return gefilterte_routen


# --------------------------------------------------
# Berechnung geografischer Entfernungen
# --------------------------------------------------

def berechne_entfernung(koordinate1, koordinate2):
    """
    Berechnet die Entfernung zwischen zwei geografischen
    Koordinaten mithilfe der Haversine-Formel.

    Beide Koordinaten müssen im Format
    [Breitengrad, Längengrad] angegeben werden.

    Returns:
        float: Entfernung in Kilometern.
    """

    erdradius = 6371.0

    lat1, lon1 = map(math.radians, koordinate1[:2])
    lat2, lon2 = map(math.radians, koordinate2[:2])

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return erdradius * c


# --------------------------------------------------
# Filterung nach Start- und Endpunkt
# --------------------------------------------------

def filter_nach_start_und_ende(
    routen,
    start_koordinaten=None,
    end_koordinaten=None,
    start_radius=None,
    end_radius=None
):
    """
    Filtert Wanderrouten anhand ihrer geografischen
    Start- und Endpunkte.

    Eine Route bleibt erhalten, wenn:

    - ihr Startpunkt innerhalb des Startradius liegt,
    - ihr Endpunkt innerhalb des Endradius liegt.

    Nicht angegebene Orte werden ignoriert.

    Die Koordinaten müssen im Format
    [Breitengrad, Längengrad] vorliegen.
    """

    gefilterte_routen = []

    for route in routen:

        koordinaten = route.koordinaten
        if not koordinaten and route.start_koordinaten:
            koordinaten = [route.start_koordinaten]

        if not koordinaten:
            continue

        # ------------------------------------------
        # Startpunkt prüfen
        # ------------------------------------------

        if start_koordinaten is not None and start_radius is not None:

            routen_start = route.start_koordinaten if route.start_koordinaten else koordinaten[0]

            entfernung_start = berechne_entfernung(
                start_koordinaten,
                routen_start
            )

            if entfernung_start > start_radius:
                continue

        # ------------------------------------------
        # Endpunkt prüfen
        # ------------------------------------------

        if end_koordinaten is not None and end_radius is not None:

            routen_ende = koordinaten[-1]

            entfernung_ende = berechne_entfernung(
                end_koordinaten,
                routen_ende
            )

            if entfernung_ende > end_radius:
                continue

        # Route erfüllt alle angegebenen Bedingungen.
        gefilterte_routen.append(route)

    return gefilterte_routen