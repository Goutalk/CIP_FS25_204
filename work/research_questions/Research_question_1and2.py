#***************** This section contains the code to answer research question 1 about political aspects ***************

# ______________________________________
# From here: Curdin Caderas, 06.04.2025
# ______________________________________


"""
This sections intends to answer:

a) a part of the first rearch question (plotting swiss maps with data form primary and secondary dataset)
b) the second research question: "Does the ratio of Green Party voters correlate with GA / Halbtax Sales per canton?"

Since the purpose of this project lies rather on learning how to collect, integrate and preprocess data we intend to use
different visualizations and techniques to get experience in Python coding. While we know and acknowledge that not all visualization
types might be the statistically appropriate choice .
"""


##  Importing the needed libraries
import pandas as pd
from pyaxis import pyaxis
import openpyxl
import plotly.express as px
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape
import seaborn as sns
from scipy.stats import pearsonr

## ********* STEP 1: Read in the already prepared data set obtained from SBB


df_sbb = pd.read_pickle("../../data/processed/df_cantons.pkl")
#print(type(df_sbb))


## ********* STEP 2: Read in data from BFS about Nationalratswahlen and Prepare dataset


#  Read in the data from BFS about Nationalratswahlen
px_elections = pyaxis.parse("../../data/raw/bfs_elections_results.px", encoding = "latin-1")

#  Checking which data variants are available in this .px file
#print(px_elections.keys())

#  Using key DATA to create data frame
df_elections = px_elections['DATA']

#  Checking the dataframe
#print(df_elections)
#print(df_elections.columns)
#df_elections.to_excel("election_results.xlsx", index = False)

"""
After a visual inspection of the new dataset, we learned that there are a few things to correct:

* The dataset contains data which is not needed (we only need data from 2012 onwards)

* The dataset contains: Parteistärke in % / Fiktive Wählende / Parteistärke, we only need Parteistärke in % in order to
  compare it with the share of ticket sales
  
* If a political party is not present in a certain canton, this is indicated by "..."

* The new dataframe with the election data uses the full name of the state in switzerland, while in the dataframe with SBB
  data there is only the abbreviation (e.g. ZH for Zurich). In order to join and work with the datasets this needs to be taken care of.
  
* Some of the names are in German and in French (e.g. "Fribourg / Freiburg")

* Some numerical data is saved as str
"""

#  Drop all years before 2012
df_elections["Jahr"] = pd.to_numeric(df_elections["Jahr"], errors = "coerce") #change "Jahr" to numeric
df_elections2 = df_elections[df_elections["Jahr"] >= 2012]

#  Just keep "Parteistärke in %" in Column "Ergebnisse" using boolean indexing
df_elections3 = df_elections2[df_elections2["Ergebnisse"] == "Parteistärke in %"]

#  Rename column "DATA" to "Parteistaerke in %"
df_elections3 = df_elections3.rename(columns={"DATA":"Parteistaerke in %"})

#  Replace "..." (which indicates no votes) by "0"
df_elections3["Parteistaerke in %"] = df_elections3["Parteistaerke in %"].astype(str)      #convert column to str
df_elections3["Parteistaerke in %"] = df_elections3["Parteistaerke in %"].str.strip('"')   # strip from " -> as it caused errors
df_elections3["Parteistaerke in %"] = df_elections3["Parteistaerke in %"].replace("...",0) # replace with 0
df_elections3["Parteistaerke in %"] = pd.to_numeric(df_elections3["Parteistaerke in %"], errors='coerce') # convert to number

#  Visually inspect results
#print(df_elections3)
#print(df_elections3[df_elections3["Parteistaerke in %"].isna()]) #no more NA's

#  Add the abbreviation of "Kanton" to the dataset so that it can be joined with the SBB Data

"""
This is done just exactly as by the names of the columns which are in the dataset.
Details see code below
"""

#  Looking at names of "Kanton" and its abbreviations (form SBB Dataset)

canton_names = df_elections3["Kanton"].unique()
#print(canton_names)
#print(df_sbb.columns)

canton_abbr = df_sbb["Kantonskürzel"].unique()
#print(canton_abbr)

#  creating (manually) a dataframe as an assignment of canton names and its abbreviations (source, see canton_abbr / canton_names)
cantons_mapping = pd.DataFrame({
    "Kanton": [
            "Zürich", "Bern / Berne", "Luzern", "Uri", "Schwyz", "Obwalden",
            "Nidwalden", "Glarus", "Zug", "Fribourg / Freiburg", "Solothurn",
            "Basel-Stadt", "Basel-Landschaft", "Schaffhausen", "Appenzell Ausserrhoden",
            "Appenzell Innerrhoden", "St. Gallen", "Graubünden / Grigioni / Grischun",
            "Aargau", "Thurgau", "Ticino", "Vaud", "Valais / Wallis", "Neuchâtel",
            "Genève", "Jura", "Schweiz"
    ],
    "Kürzel": [
        "ZH", "BE", "LU", "UR", "SZ", "OW", "NW", "GL", "ZG", "FR", "SO",
        "BS", "BL", "SH", "AR", "AI", "SG", "GR", "AG", "TG", "TI", "VD",
        "VS", "NE", "GE", "JU", "CH"
    ]
})

#  Merge according to "cantons_mapping"
df_elections3 = df_elections3.merge(cantons_mapping, on = "Kanton", how = "left")

#  Checking result
#print(df_elections3)
#print(df_elections3[df_elections3["Kürzel"].isna()]) #no NA's in column "Kürzel"

#  Adjust names of Kanton (those which use multiple languages, goal: just one expression)

replacements = {"Bern / Berne": "Bern",
    "Fribourg / Freiburg": "Fribourg",
    "Graubünden / Grigioni / Grischun": "Graubünden",
    "Valais / Wallis": "Valais",
}

df_elections3["Kanton"] = df_elections3["Kanton"].replace(replacements)

#  Check if it worked
#print(df_elections3["Kanton"].unique())
#print(df_elections3.columns)
#df_elections3.to_excel("election_results3.xlsx", index = False)

#  Removal of NA's under group "Schweiz" (there are political parties which have no voters share on a national level)
df_elections3 = df_elections3.dropna(subset=['Parteistaerke in %'])
#df_elections3.to_excel("election_results4.xlsx", index = False)

#  Round "Parteistaerke in%" to 2 digits after comma
df_elections3['Parteistaerke in %'] = df_elections3['Parteistaerke in %'].round(2)

#  Copy to new df
df_elections4 = df_elections3.copy()


## ********* STEP 3: Determine the share of "Green Party Voters"


"""
At first, the term "Green Party" Voters needs to be discussed.

--> This example demonstrates very well the aspect and importance of "domain knowledge" in data science. 

Several political parties in Switzerland have topics regarding environmental protection / stop of global warming / sustainability etc. on their agenda.
To investigate this, an in depth, qualitative analysis about each political agenda and its goals is necessary. Furthermore a qualitative study
about what voters "associate" with each party would be needed.

Since this project is about learning to collect, integrate and preprocess data, we will keep it very simple:
--> "Green party voters" consist of GLP "Grünliberale Partei" and Grüne "Grüne Partei". In other words: "those political parties with the word "green" in its name.

We are aware that this definition would not necessarily hold for a project in political science, but we think it will for this project.

For this reason, per canton we sum up the share of Grüne and GLP and consider this as the "share of Green party voters" for our further investigation.
"""


#  Boolean filtering of df_elections4 with only Grüne and GLP
df_green_voters = df_elections4[df_elections4["Partei"].isin(["Grüne", "GLP"])]
#print(df_green_voters) # Check if it worked

#  Calculate the green_voters_share (grouping by canton and year)
df_green_voters_share = df_green_voters.groupby(["Kanton","Jahr"])["Parteistaerke in %"].sum().reset_index()
#print(df_green_voters_share) # Check

#  Renaming column to "Green party voters"
df_green_voters_share.rename(columns={"Parteistaerke in %": "Green Party Voters %"}, inplace = True)

#  Merging with original df to obtain canton abbreviation again
df_green_voters_share = df_green_voters_share.merge(df_elections4[["Kanton", "Jahr", "Kürzel"]].drop_duplicates(),on=["Kanton", "Jahr"],how="left")

#  Renaming column to "Kantonskürzel"
df_green_voters_share.rename(columns={"Kürzel": "Kantonskürzel"}, inplace = True)

#  Renaming column to "jahr"
df_green_voters_share.rename(columns={"Jahr": "jahr"}, inplace = True)

#  Save prepared df to new df
df_green_share = df_green_voters_share.copy()


## ********* STEP 4: Create one Dataset from sbb data and from Nationalratswahlen


"""
National elections ("Nationalratswahlen") take place in Switzerland every 4 years.
Therefore we are interested in the years 2015 / 2019 / 2023 in order to compare this with our data about ticket sales

Datasets used:
- df_green_share
- df_sbb

Goal is to have a dataset with election results and sbb ticket sales per canton.
"""

#  Checking column names
#print(df_sbb.columns)
#print(df_green_share.columns)


#  Merge data frames to one dataframe, left join
df_elections_sbb = df_green_share.merge(df_sbb, on = ["Kantonskürzel", "jahr"], how = "left")
#df_elections_sbb.to_excel("df_elections_sbb.xlsx", index = False)
df_elections_sbb2 = df_elections_sbb.copy() # save separate df for later on correlation analysis


## ********* STEP 5: Prepare plots with Swiss Map


"""
Now that there is a dataframe which combines the share of green party voters with the share of GA, halbtax
owners per canton for the years in which elections were held in Switzerland we will start analyzing / visualizing its relationship.
Since this data is on level "canton" we would like to try out to plot maps with geopandas and matplotlib.pyplot.
"""

#  Swiss Map to display the variable

"""
To obtain the borders of the swiss cantons we were looking for geojson files.
Here we found a file: https://data.opendatasoft.com/explore/dataset/georef-switzerland-kanton%40public/export/?flg=en-
us&utm_source=chatgpt.com&disjunctive.kan_code&disjunctive.kan_name&sort=year&refine.kan_type=Kanton&location=8,47.51535,8.72864&basemap=jawg.streets
"""

#  Open file with geodata and save it as geojson
with open("../../data/raw/georef-switzerland-kanton@public.geojson", encoding="utf-8") as f:
    geojson = json.load(f)

#  Check canton names
kantone = [f["properties"]["kan_name"] for f in geojson["features"]]
#print("Kantone GEOJSON:", kantone)


#  Check canton names in df_elections_sbb
#print(df_elections_sbb.columns)
cantons1 = sorted(df_elections_sbb["Kanton"].unique())
#print(f"Cantons1: {cantons1}")

"""
Unfortunately the names of the canton from the geojson differ from the one in the already prepared df_elections_sbb. In order
to plot it as a map, the cantons need to be exaclty alike. Therefore this will be corrected below with another mapping.
"""

#  Manual mapping of canton names which are spelled different / in different language
mapping_cantons2 = {
    "Freiburg": "Fribourg",
    "Genève": "Genève",
    "Neuenburg": "Neuchâtel",
    "Tessin": "Ticino",
    "Waadt": "Vaud",
    "Wallis": "Valais",
    "Schweiz": None  # "Schweiz" is non existent in in geojson
}

#  Adding new column with canton names in the same way as in geojson to df_elections_sbb
df_elections_sbb["Kanton_geojson"] = df_elections_sbb["Kanton"].map(mapping_cantons2).fillna(df_elections_sbb["Kanton"])

#  Remove None values (from "Switzerland" - which as contained in df originally)
df_elections_sbb = df_elections_sbb[df_elections_sbb["Kanton"] != "Schweiz"]

#  Filter for year
df_plot = df_elections_sbb[df_elections_sbb["jahr"] == 2023].copy()
df_plot["kan_name"] = df_plot["Kanton_geojson"]

#  Check if it worked
cantons2 = sorted(df_elections_sbb["Kanton_geojson"].unique())
#print(f"Cantons 2: {cantons2}") #Cantons named differently now

#  Extract Geometries and features from the geojson file
geometries = [] # Polygone of the cantons
properties = [] # Properties (such as kan_name,which will be used)
for f in geojson["features"]:
    geometries.append(shape(f["geometry"]))
    props = f["properties"]
    props["kan_name"] = f["properties"]["kan_name"]
    properties.append(props)

#  Create a geodataframe with geopandas
gdf = gpd.GeoDataFrame(properties, geometry=geometries)

#  Ensure that the column "kan_name" only contains strings, no lists
gdf["kan_name"] = gdf["kan_name"].apply(lambda x: x[0] if isinstance(x, list) else x) # if element is list, only take first pos of list. Else take whole element

#  Merge df_plot left to geodataframe
gdf["kan_name"] = gdf["kan_name"].str.strip()
df_plot["kan_name"] = df_plot["kan_name"].str.strip()
gdf_plot = gdf.merge(df_plot, on="kan_name", how="left")


##********* STEP 6: Plotting of Maps

#  ------------- Plot a map with share of GA, called "Share of GA in %" -------------
fig, ax = plt.subplots(figsize=(12, 12))
gdf_plot.plot(
    column="anteil_ga",
    cmap="viridis",
    linewidth=0.8,
    edgecolor='black',
    legend=True,
    ax=ax,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "label": "Keine Daten"
    })

#  Title and Axis
ax.set_title("Share of GA in % (2023)", fontsize=16)
ax.axis("off")

# Include values per canton
for idx, row in gdf_plot.iterrows():
    if pd.notna(row["anteil_ga"]):
        x, y = row["geometry"].centroid.coords[0]
        ax.text(x, y, f"{row['anteil_ga']:.1f}%", fontsize=8, ha='center', va='center', color='black')

plt.tight_layout()
plt.show()


#  ------------- Plot a map with share of halbtax owners in % ----------------
fig, ax = plt.subplots(figsize=(12, 12))
gdf_plot.plot(
    column="anteil_halbtax",
    cmap="viridis",
    linewidth=0.8,
    edgecolor='black',
    legend=True,
    ax=ax,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "label": "Keine Daten"
    })

#  Title and Axis
ax.set_title("Share of Halbtax Owners in % (2023)", fontsize=16)
ax.axis("off")

# Include values per canton
for idx, row in gdf_plot.iterrows():
    if pd.notna(row["anteil_halbtax"]):
        x, y = row["geometry"].centroid.coords[0]
        ax.text(x, y, f"{row['anteil_halbtax']:.1f}%", fontsize=8, ha='center', va='center', color='black')

plt.tight_layout()
plt.show()

#  ------------- Plot a map with share of Green Party Voters in % -------------
fig, ax = plt.subplots(figsize=(12, 12))
gdf_plot.plot(
    column="Green Party Voters %",
    cmap="viridis",
    linewidth=0.8,
    edgecolor='black',
    legend=True,
    ax=ax,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "label": "Keine Daten"
    })

#  Title and Axis
ax.set_title("Green Party Voters % 2023", fontsize=16)
ax.axis("off")

# Include values per canton
for idx, row in gdf_plot.iterrows():
    if pd.notna(row["Green Party Voters %"]):
        x, y = row["geometry"].centroid.coords[0]
        ax.text(x, y, f"{row['Green Party Voters %']:.1f}%", fontsize=8, ha='center', va='center', color='black')

plt.tight_layout()
plt.show()

##********* STEP 7: Investing possible correlations between share of GA

"""
After displaying the data in a map, we now will move on and investigate a possible correlation of Green Party Voters with the share of halbtax / GA / abo per canton.
We are fully aware, that there might be many confounders / spurious correlations - therefore the purpose of these investigations is rather practising python than on performing an in depth statistical analysis.

For this we use the previously made "df_elections_sbb2"
"""

#df_elections_sbb2.to_excel("df_elections_sbb2.xlsx", index = False)

#  Remove "Schweiz"
df_elections_sbb2 = df_elections_sbb2[df_elections_sbb2["Kanton"] != "Schweiz"]

#  Create df with relevant columns to investigate correlation
cols_to_investigate = [ "Green Party Voters %", "anteil_ga", "anteil_halbtax", "anteil_abo_total", "jahr"]
df_correl = df_elections_sbb2[cols_to_investigate].copy()


##  Plot a histogram for Green Party Voters (%)
"""First, we would like to look at a histogramm of the data. I.e. how is the share of green party voters distributed?
We here choose to look only at 2023"""

#  Create df_correl_2023 for year 2023
df_correl_2023 = df_correl[df_correl["jahr"] == 2023].copy()

#  Set style
sns.set(style="whitegrid")

#  Plot Histogramm
plt.figure(figsize=(8, 5))
sns.histplot(df_correl_2023["Green Party Voters %"], bins=10, kde=True, color="skyblue")

#  Titles
plt.xlabel("Share of Green Party Voters (%)")
plt.ylabel("Number of cantons")
plt.title("Distribution of Share of Green Party Voters (%) 2023")

plt.tight_layout()
plt.show()


##  Plot a histogramm for Anteil GA(%) --> For all years available

#  Set style
sns.set(style="whitegrid")

#  Plot Histogramm
plt.figure(figsize=(8, 5))
sns.histplot(df_correl["anteil_ga"], bins=10, kde=True, color="skyblue")

#  Titles
plt.xlabel("Anteil GA (%)")
plt.ylabel("Number of cantons")
plt.title("Distribution of GA-Share (%)")

plt.tight_layout()
plt.show()


##  Scatterplots

"""We will now go into scatterplots to investigate a possible correlation"""

cols_to_plot = [
    "anteil_ga",
    "anteil_halbtax",
    "anteil_abo_total"
]

ylabels = [
    "Share of GA %",
    "Share of Halbtax %",
    "Share of total Abo %"
]

titles = [
    "Green Party Voters (%) vs. Share of GA (%)",
    "Green Party Voters (%) vs. Share of Halbtax (%)",
    "Green Party Voters (%) vs. total Abo (%)"
]

#  Choose style
sns.set(style="whitegrid", context="notebook")

#  One row, three columns
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 5))

#  One scatterplot for each variable
for ax, col, ylabel, title in zip(axes, cols_to_plot, ylabels, titles):
    sns.regplot(
        data=df_correl,
        x="Green Party Voters %",
        y=col,
        ax=ax,
        scatter_kws={"s": 40, "alpha": 0.7},
        line_kws={"color": "red"}
    )

    r, p = pearsonr(df_correl["Green Party Voters %"], df_correl[col])
    ax.set_title(title)
    ax.set_xlabel("Green Party Voters %")
    ax.set_ylabel(ylabel)


    #  Include pearson correlation with p value in upper right of each plot
    ax.annotate(
        f"r = {r:.2f}\np = {p:.3f}",
        xy=(0.95, 0.95),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.6)
    )

plt.tight_layout()
plt.show()

"""
Interpretation:
We do not really see a strong correlation. Pearson r is highest for Share of GA with 0.25 and a p-value of 0.027
which shows a small positive correlation which according to its p value is statistically significant. However, this could be a spurious 
correlation with another variable.

The other two variable show no correlation r of -0.05 and 0.01 with no significant p value.

It could be said that for the share of total_abo has no correlation as it is dominated by halbtax_abo which has much higher figures
than the ga.

Furthermore we would like to emphasize that when using pearson r there are a few requirements to be met. Especially the fact, that the sample (3x26 cantons) is small
also it has to be recognized that when taking 3 election years this is repeatedly measured units (same cantons). 

--> In a next step we will look at the Share of GA for specific years. We will split it and investigate each of the 3 years which we have available (when national elections took place).

"""

#  Choose style
sns.set(style="whitegrid", context="notebook")

#  Extract years
years = sorted(df_correl["jahr"].unique())

#  One rows, three plots
fig, axes = plt.subplots(nrows=1, ncols=len(years), figsize=(6 * len(years), 5))

#  Scatterplot & pearson for each year
for ax, year in zip(axes, years):
    df_year = df_correl[df_correl["jahr"] == year]

    sns.regplot(
        data=df_year,
        x="Green Party Voters %",
        y="anteil_ga",
        ax=ax,
        scatter_kws={"s": 40, "alpha": 0.7},
        line_kws={"color": "red"}
    )

    #  Calculate pearson r and p value
    r, p = pearsonr(df_year["Green Party Voters %"], df_year["anteil_ga"])

    # Titel, Axis
    ax.set_title(f"Green Party % vs. Share of GA % ({year})")
    ax.set_xlabel("Green Party Voters %")
    ax.set_ylabel("Share of GA %")

    #  Display r and p value
    ax.annotate(
        f"r = {r:.2f}\np = {p:.3f}",
        xy=(0.95, 0.95),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.6)
    )

plt.tight_layout()
plt.show()

"""
For all years, the share of GA shows a weak positive correlation, but not statistically significant anymore
--> due to "smaller sample", p value changes

As for this project we will not go further into the political question and conclude with the following:

-   As for the share of halbtax users in relation to Green Party Voters our data does not point to a correlation (see scatterplots, r, p values)
-   For the share of GA users in relation to Green Party Voters we do see a certain positive correlation from our data (see scatterplots, r, p values). 
    However when we look at the years individually, the p-values are not significant anymore.
    
Furthermore as already mentioned we need to accept that our sample size is quite small and this leads to unstable p values (as seen when we look at one year or all years together).
Also we should acknowledge that many other factors (confounders) could influence this. E.g. degree of urbanization, regional aspects etc.
"""



