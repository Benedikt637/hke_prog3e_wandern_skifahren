import json
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import time

import pandas as pd

urls = (
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
headers = {"User-Agent": "WanderApp-Student-Project/1.0"}
data_file = Path(__file__).with_name("gipfel_oberstdorf.csv")

# Overpass-Abfrage für Gipfel im Bereich Oberstdorf
query = """
[out:json][timeout:25];
node["natural"="peak"](47.38,10.22,47.45,10.32);
out body;
"""


def lade_api_daten() -> dict:
    fehler = []
    for url in urls:
        request = Request(
            url,
            data=urlencode({"data": query}).encode("utf-8"),
            headers=headers,
        )
        try:
            with urlopen(request, timeout=30) as response:
                data = json.load(response)
            if not isinstance(data, dict) or not isinstance(data.get("elements"), list):
                raise ValueError("Die API hat ein unerwartetes Datenformat geliefert.")
            return data
        except (URLError, TimeoutError, ValueError) as error:
            fehler.append(f"{url}: {error}")
            print(f"Overpass-Server nicht erreichbar ({url}): {error}")
            if url != urls[-1]:
                time.sleep(1)

    details = "\n".join(fehler)
    raise RuntimeError(f"Alle Overpass-Server sind fehlgeschlagen:\n{details}")


def main() -> None:
    print("Lade Daten von Overpass...")
    try:
        data = lade_api_daten()
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    elements = data["elements"]
    gipfel = []
    for element in elements:
        tags = element.get("tags", {})
        gipfel.append(
            {
                "name": tags.get("name") or tags.get("name:de") or "Unbenannter Gipfel",
                "hoehe": tags.get("ele"),
                "lat": element.get("lat"),
                "lon": element.get("lon"),
            }
        )

    df = pd.DataFrame(gipfel, columns=["name", "hoehe", "lat", "lon"])
    df.to_csv(data_file, index=False)
    print(f"Erfolgreich als '{data_file.name}' gespeichert!")


if __name__ == "__main__":
    main()