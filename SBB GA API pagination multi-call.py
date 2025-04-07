import requests
import time
import pandas as pd

# API-URL
base_url = "https://data.sbb.ch/api/explore/v2.1/catalog/datasets/generalabo-halbtax-mit-bevolkerungsdaten/records"

# Define the years
# 2012 - 2024
years = list(range(2012, 2025))

# Max. limit according to API-doc
limit = 100

# empty list to store retrieved Data
all_results = []

# Outer loop iterates over every year
# Inner loop fetches data page by page until all for the year is loaded
for year in years:
    offset = 0 # start offset for pagination.
    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "where": f"YEAR(jahr_an_anno)={year}"  # Extract year properly (filter)
        }

        response = requests.get(base_url, params=params) # Send get request to the API

        if response.status_code != 200: # Code 200 = OK, therefore if not, then print error and break.
            print(f"API Error {response.status_code}: {response.text}")
            break

        data = response.json()  # Parse the response as JSON

        if "results" not in data or len(data["results"]) == 0: # If  no more results, move to next year
            print(f"No data for {year}. Moving to next year...")
            break

        all_results.extend(data["results"]) # Add retrieved records to the result list
        offset += limit    # Increase offset to get the next page of data. keep increasing offset by limit until the API returns an empty list.

        print(f"Loaded {len(all_results)} entries for {year}...") #pirnt progress

        time.sleep(0.5)  # pause to avoid overloading API

# total number of retrieved entries
print(f"Process finished! Total retrieved entries: {len(all_results)}")

# Convert JSON to DataFrame
df = pd.DataFrame(all_results)

# Save DataFrame to CSV
csv_filename = "SBB_GA_Halbtax_Data.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"Data saved to: {csv_filename}")
