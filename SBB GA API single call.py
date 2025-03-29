import requests
import json

# API-URL
base_url = "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/generalabo-halbtax-mit-bevolkerungsdaten/records"

# Parameter für PLZ 3007
params = {
    "limit": 100,  # Maximale Anzahl an Datensätzen pro Abruf
    "where": "plz_npa=4954"  # Filter für PLZ 3007 (Bern)
}

# API-Request
response = requests.get(base_url, params=params)

# JSON-Daten formatieren und ausgeben
data = response.json()
print(json.dumps(data, indent=4, ensure_ascii=False))

print("Hello World")
