import requests
import time

# API-URL
base_url = "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/generalabo-halbtax-mit-bevolkerungsdaten/records"

# Pagination-Parameter
limit = 100  # Anzahl pro Abruf
offset = 0
all_results = []

print("🔄 Starte API-Abruf...")

while True:
    params = {
        "limit": limit,
        "offset": offset
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # Falls keine neuen Daten → Beenden
    if "results" not in data or len(data["results"]) == 0:
        break

    all_results.extend(data["results"])  # Daten speichern
    offset += limit  # Offset für nächste Seite

    print(f"✅ {len(all_results)} Einträge geladen...")  # Fortschritt anzeigen
    time.sleep(0.5)  # API nicht überlasten

print(f"🎉 Fertig! Gesamtzahl abgerufener Einträge: {len(all_results)}")
