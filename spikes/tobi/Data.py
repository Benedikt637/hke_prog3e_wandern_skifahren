from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).with_name("gipfel_oberstdorf.csv")


def lade_gipfel_daten() -> pd.DataFrame:
    gipfel = pd.read_csv(DATA_FILE)
    required_columns = {"name", "hoehe", "lat", "lon"}
    missing_columns = required_columns.difference(gipfel.columns)
    if missing_columns:
        raise ValueError(
            f"In {DATA_FILE.name} fehlen Spalten: {', '.join(sorted(missing_columns))}."
        )

    gipfel["lat"] = pd.to_numeric(gipfel["lat"], errors="coerce")
    gipfel["lon"] = pd.to_numeric(gipfel["lon"], errors="coerce")
    gipfel = gipfel.dropna(subset=["lat", "lon"]).copy()
    gipfel["name"] = gipfel["name"].fillna("Unbenannter Gipfel")
    return gipfel
