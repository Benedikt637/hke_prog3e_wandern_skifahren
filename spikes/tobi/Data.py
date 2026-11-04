import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def lade_wander_daten():
    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "WanderApp-Student-Project/1.0"}

    # 'out geom 15' holt bis zu 15 echte Wanderwege inklusive ihrer GPS-Koordinatenpunkte
    query = (
        "[out:json][timeout:15];"
        'way["highway"="path"](47.38, 10.22, 47.45, 10.32);'
        "out geom 15;"
    )

    try:
        response = requests.get(
            url, params={"data": query}, headers=headers, verify=False, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])

            routen_liste = []
            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name", "Alpiner Wanderweg")

                # Geometrie-Punkte des Weges auslesen
                geometry = el.get("geometry", [])
                if geometry:
                    coords = [
                        [pt.get("lat"), pt.get("lon")]
                        for pt in geometry
                        if "lat" in pt and "lon" in pt
                    ]
                    if len(coords) > 1:
                        routen_liste.append({
                            "title": name,
                            "coords": coords,  # Die vollständige GPS-Linie als Koordinaten-Liste
                            "lat": coords[0][0],  # Startpunkt für Tabellenansicht
                            "lon": coords[0][1],
                        })

            df = pd.DataFrame(routen_liste)
            if not df.empty:
                return df

    except Exception as e:
        print(f"API-Abfrage für Linien fehlgeschlagen: {e}")

    # Fallback-Daten mit echten GPS-Linienverläufen
    fallback_linien = [
        {
            "title": "Nebelhorn Gratweg (Fallback)",
            "coords": [
                [47.4421, 10.3345],
                [47.4450, 10.3400],
                [47.4500, 10.3450],
                [47.4550, 10.3500],
            ],
            "lat": 47.4421,
            "lon": 10.3345,
        },
        {
            "title": "Fellhorn Panoramaweg (Fallback)",
            "coords": [
                [47.3912, 10.2341],
                [47.3950, 10.2400],
                [47.4000, 10.2450],
                [47.4050, 10.2500],
            ],
            "lat": 47.3912,
            "lon": 10.2341,
        },
    ]
    return pd.DataFrame(fallback_linien)