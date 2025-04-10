# CIP_FS25_204 – SBB GA and Halbtax Data Analysis

## Authors

Christian Steinemann, Curdin Caderas, Thomas Aeschlimann

---

## Project Overview

This project analyzes the ownership distribution of the **Swiss General Abonnement (GA)** and **Halbtax** subscriptions based on data from the **SBB Developer Portal API**. The goal is to uncover regional differences and potential correlations with political, demographic, and economic factors.

The project is part of the course **CIP – Data Collection, Integration, and Preprocessing (FS2025)** and primarily aims to provide hands-on experience with real-world data, APIs, and exploratory analysis techniques.

---

## Objective

- Analyze the regional distribution of GA and Halbtax sales (ZIP code / canton / urban vs. rural)
- Investigate potential correlations with:
  - Political orientation (e.g., share of Green Party voters)
  - Energy price development (gasoline, electricity)
  - Number of newly registered passenger cars

> **Note**: We do not aim to postulate any kind of causality. The focus is on exploratory analysis and practicing data-handling techniques.

---

## Research Questions

1. What are the properties of GA / Halbtax Sales in Switzerland  
   - Basic visualizations of the dataset  
   - Development of sales figures over time  
   - Regional differences (cantonal / municipal differences / urban vs. rural areas)

2. Political aspects  
   - Does the ratio of Green Party voters correlate with GA / Halbtax Sales per canton / municipality?

3. Energy prices  
   - Is there a relationship between the development of energy prices (gasoline / electricity) averaged over one year and GA / Halbtax sales?

4. Car registrations  
   - Do the GA / Halbtax sales correlate with the number of new registrations of passenger cars?

---

## Data Sources

### Primary Data (SBB)
- **Source**: [SBB Open Data API](https://data.sbb.ch/explore/dataset/generalabo-halbtax-mit-bevolkerungsdaten/information/)
- **API-Doc**: [Opendatasoft API Documentation](https://help.opendatasoft.com/apis/ods-explore-v2/explore_v2.1.html)
- **Content**: Annual GA / Halbtax subscriptions per ZIP code, including population data
- **Format**: JSON via API (requires pagination)
- **Access**: No authentication/token required

### Secondary Data
| Topic | Source | Purpose |
|-------|--------|---------|
| Postal codes | swisstopo (API) | Link ZIP codes to cantons/regions |
| Energy prices | Swiss Federal Statistical Office (BFS) | Analyze historical fuel/electricity prices |
| Car registrations | BFS | Analyze development of new vehicle registrations |
| Election results (Nationalratswahlen (Parteistärke) | bfs.admin.ch | Share of Green Party voters per municipality |
| GeoJSON Swiss Cantons | opendatasoft.com | Plot swiss maps with figures from main / secondary datasets |

---

## Project Structure

```bash
.
├── data/
│   ├── raw/            # Unmodified original data (primary and secondary)
│   └── processed/      # Cleaned and enriched data
│
├── work/
│   ├── preparation/            # API access, cleaning, preprocessing
│   └── research_questions/     # Scripts for individual research questions
│
├── docs/               # Feasability Study / Project Documentation (PDF)
├── .gitignore
├── requirements.txt    # Python dependencies
├── README.md           # You’re reading it right now
```

---

## Code Contribution

Code contributions by each team member are listed below:

| Contributor             | Contribution                                                                 | Code                                                                                     |
|-------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **Christian Steinemann** | - Exploratory Data Analysis (EDA) <br> - Research Question 3                        | – `Research_question_1_Basic_visualization.py` <br> - `Research_question_3.py`                                                                                       |
| **Curdin Caderas**       | - Initial data cleaning <br> - Exploratory Data Analysis (EDA) <br> - Research Questions 1 and 2                 | – `Data_PreP_Clean_SBB_Data.ipynb` <br> - `Research_question_1_Basic_visualization.py` <br> - `Research_question_1and2.py`                                                                                      |
| **Thomas Aeschlimann**   | - Development of API data import (pagination) <br> - Initial data cleaning <br> - Research Question 4  | - `SBB GA API pagination multi-call.py`<br>- `Data_PreP_Clean_SBB_Data.ipynb`<br>- `Research_question_4.ipynb` |

---

## License Notice

All data used in this project is subject to the terms and conditions of the respective data providers (SBB, BFS, opendata.swiss).  
This project is for **academic purposes only** within the context of the CIP course.

> Code changes are tracked via Git and can be reviewed in the commit history.
