import requests
import time
import pandas as pd

# API-URL
base_url = "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/generalabo-halbtax-mit-bevolkerungsdaten/records"

# Define the years
years = list(range(2012, 2025))

# Max. limit according to doc
limit = 100
all_results = []



for year in years:
    offset = 0
    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "where": f"YEAR(jahr_an_anno)={year}"  # Extract year properly
        }

        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            break

        data = response.json()

        if "results" not in data or len(data["results"]) == 0:
            print(f"No data for {year}. Moving to next year...")
            break  # Move to the next year

        all_results.extend(data["results"])
        offset += limit  # Move to the next page

        print(f"Loaded {len(all_results)} entries for {year}...")

        time.sleep(0.5)  # Avoid overloading API

print(f"Process finished! Total retrieved entries: {len(all_results)}")

# Convert JSON to DataFrame
df = pd.DataFrame(all_results)

# Save DataFrame to CSV
csv_filename = "SBB_GA_Halbtax_Data.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"Data saved to: {csv_filename}")
