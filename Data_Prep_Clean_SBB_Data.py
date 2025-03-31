import numpy as np
import pandas as pd
import openpyxl

## Step 1: Load raw data
# URL to raw data of primary data source
url = "SBB_GA_Halbtax_Data.csv"

# Load data into a dataframe
df1 = pd.read_csv(url)


## Step 2: Rename column names
# Rename column names into more handy titles for further use
df2 = df1.rename(columns={
    'jahr_an_anno': 'jahr',
    'plz_npa': 'plz',
    'ga_ag': 'anzahl_ga',
    'ga_ag_flag': 'ga_flag',
    'hta_adt_meta_prezzo': 'anzahl_halbtax',
    'hta_adt_meta_prezzo_flag': 'halbtax_flag',
    'bevolkerung': 'bevoelkerung',
    'anteil_ga_besitzer': 'anteil_ga',
    'anteil_hta_besitzer_': 'anteil_halbtax'
})

## Step 3: Removing PLZ missing data from certain years
# First we want to search for missing years. .nunique() counts unique years per plz
jahre_pro_plz = df2.groupby('plz')['jahr'].nunique()

# filter PLZ, not containing data for all years
plz_missing_years = jahre_pro_plz[jahre_pro_plz < 13] # Upon inspection, the missing years contain postal codes from Liechtenstein (9485 - 9500) or plz from regions / used for delivery

# Extract List of PLZ
plz_to_del = plz_missing_years.index.tolist()

# the tilde ~ inverts the boolean mask returned by .isin(). True --> False. Removes all rows containing the PLZ in plz_to_del
df3 = df2[~df2["plz"].isin(plz_to_del)]


#check again 
#jahre_pro_plz_df3 = df3.groupby('plz')['jahr'].nunique()
#plz_unvollstaendig = jahre_pro_plz_df3[jahre_pro_plz_df3 < 13]
#print(plz_unvollstaendig) #Series([], Name: jahr, dtype: int64) --> no PLZ has less than 13 years


## Step 4: Cleaning missing values in population Data
"""
From data exploration we know, that the percentage share for GA and Halbtax are fully missing int the years 2023 - 2024. 
To calculate them, we do need the population data, which is missing as well in this years as well for some plz in the years 2012 - 2022.

The Years 2012 - 2022 contain 20 NaN for "bevoelkerung". print(len(df3[(df3['jahr'].between(2012, 2022)) & (df3['bevoelkerung'].isna())]))
Upon inspection, plz 1015 does not have any population data in any year. Therefore, plz 1015 will be deleted.
The rest of the missing values will be added using linear interpolation.

Years 2023 - 2024 are completely missing population Data.
For those years we decided to use CAGR Compound Annual Growth Rate

"""
#Removing 1015 from df3
df3 = df3[df3['plz'] != 1015]


# Interpolate NaN 2012 - 2022 per PLZ using linear interpolation
df4 = df3.copy() #creates copy of df3
year_sort = df4['jahr'].between(2012, 2022) # Filter years

df4.loc[year_sort, 'bevoelkerung'] = ( #[year sort = filter, column ] --> where year_sort == True and bevolkerung
    df4[year_sort]
    .sort_values(['plz', 'jahr']) #sorts for chronological interpolation
    .groupby('plz')['bevoelkerung'] #groups by plz and checks only column bevoelkerung
    .transform(lambda x: x.interpolate(method='linear', limit_direction='both')) #fills NaN. limit_direction allows to interpolate beginning and end (2012 and 2022.) .interpolate() in pandas is designed to only fill NaN values by default.
)

"""
check:
print(len(df3[(df3['jahr'].between(2012, 2022)) & (df3['bevoelkerung'].isna())]))
print(df3[(df3['jahr'].between(2012, 2022)) & (df3['bevoelkerung'].isna())])

print(df3[df3['plz'] == 5404])
print(df4[df4['plz'] == 5404])
"""

#: Estimate population for 2023–2024 using CAGR (Compound Annual Growth Rate)

# Copy df4
df5 = df4.copy()

# extract Bevölkerung 2012 and 2022 per PLZ
pop_2012 = df5[df5['jahr'] == 2012][['plz', 'bevoelkerung']].rename(columns={'bevoelkerung': 'pop_2012'})
pop_2022 = df5[df5['jahr'] == 2022][['plz', 'bevoelkerung']].rename(columns={'bevoelkerung': 'pop_2022'})

# calculate CAGR
cagr_df = pd.merge(pop_2012, pop_2022, on='plz')
cagr_df['cagr'] = (cagr_df['pop_2022'] / cagr_df['pop_2012']) ** (1/10) - 1

# Prognosis for 2023 and 2024
cagr_df['jahr'] = 2023
cagr_df['bevoelkerung'] = cagr_df['pop_2022'] * (1 + cagr_df['cagr'])
pop_2023 = cagr_df[['plz', 'jahr', 'bevoelkerung']]

cagr_df['jahr'] = 2024
cagr_df['bevoelkerung'] = cagr_df['bevoelkerung'] * (1 + cagr_df['cagr'])
pop_2024 = cagr_df[['plz', 'jahr', 'bevoelkerung']]

# 2023 & 2024 zusammenführen
pop_23_24 = pd.concat([pop_2023, pop_2024])

# Nur NaN-Werte in df5 überschreiben
for _, row in pop_23_24.iterrows():
    condition = (df5['plz'] == row['plz']) & (df5['jahr'] == row['jahr']) & (df5['bevoelkerung'].isna())
    df5.loc[condition, 'bevoelkerung'] = row['bevoelkerung']

# Round to "full person"
mask_23_24 = df5['jahr'].isin([2023, 2024])
df5.loc[mask_23_24, 'bevoelkerung'] = df5.loc[mask_23_24, 'bevoelkerung'].round(0)

## Visual inspection in Excel
#df_export = df5[(df5['jahr'] >= 2022) & (df5['jahr'] <= 2024)].sort_values(by=['plz', 'jahr'])
#df_export.to_excel("bevoelkerung_2022_2024.xlsx", index=False)

#---> As agreed I checked CAGR calculations and it seems correct to me (Curdin 29.03)



## FROM HERE: CURDIN (29/30.03)

#Missing values for the share of GA / Halbtax
"""
From data exploration we know that there are missing values for the share of GA / Halbtax. This was due to missing bevoelkerung values. For the puprose of this project, the 
missing values for (population) "bevoelkerung" were calculated.

Next step is to calculate missing shares of GA / HT.
"""

df6 = df5.copy()

## Check for sum of NA's (in share GA / HT) per year
#print(df6.groupby('jahr')[['anteil_ga', 'anteil_halbtax']].apply(lambda x: x.isna().sum()))

# The reason for NA's in year 2023 & 2024 is clear (missing bevoelkerung) however, there are still NA's in some years 2012 - 2022
# Identify years other than 23'/24' with NA's
df_missing_shares = df6[
    (df6['jahr'].between(2012, 2022)) &
    (df6[['anteil_ga', 'anteil_halbtax']].isna().any(axis=1))
].sort_values(by=['plz', 'jahr'])

# Visual inspection of values which contain NA in GA / HT share before 2023
pd.set_option('display.max_columns', None)
#print(df_missing_shares)

## Calculate and include missing values

# Create a mask (boolean mask) as a filter to find all rows where "anteil_ga" is NA, but not "anzahl_ga" and "bevoelkerung"
mask_ga = df6['anteil_ga'].isna() & df6['anzahl_ga'].notna() & df6['bevoelkerung'].notna()
# For all rows which meet condition from mask_ga, calculate the "anteil_ga"
df6.loc[mask_ga, 'anteil_ga'] = df6.loc[mask_ga, 'anzahl_ga'] / df6.loc[mask_ga, 'bevoelkerung'] * 100

# Same procedure for anteil_halbtax as for anteil_ga
mask_halbtax = df6['anteil_halbtax'].isna() & df6['anzahl_halbtax'].notna() & df6['bevoelkerung'].notna()
df6.loc[mask_halbtax, 'anteil_halbtax'] = df6.loc[mask_halbtax, 'anzahl_halbtax'] / df6.loc[mask_halbtax, 'bevoelkerung'] * 100

## Check for NaN in anteil_ga and anteil_halbtax
#print(df6[['anteil_ga', 'anteil_halbtax']].isna().sum()) # No more NAN in anteil_ga and anteil_halbtax

df7 = df6.copy() #copy of dataframe for next step



## OUTLIERS / EXTREME VALUES FOR anteil_ga, anteil_halbtax
"""
From exploring the dataset we know, that some shares are not plausible (reason: the share is > 100%).
This seems to occur due to data protection reasons. In the description of the dataset it says that: for districts with < 20 travelcards the 
average quantity of travelcards (for districts with same first number) is used.
--> this may lead to the issue with having more GA / Halbtax than inhabitants.
In the dataset this is indicated by ga_flag & halbtax_flag.
"""

# Check for proportion all entries in dataset and for rows with a ga_flag or halbtax_flag
#print("Total number of rows:", len(df7))
#print("Number of rows with ga_flag or halbtax_flag == 1:", df7[(df7['ga_flag'] == 1) | (df7['halbtax_flag'] == 1)].shape[0])

# Check if values vary per year
#print(df7[(df7['ga_flag'] == 1) | (df7['halbtax_flag'] == 1)].groupby('jahr').size())

# Check how many entries have a share are above 100%
above_100 = df7[(df7['anteil_ga'] > 100) | (df7['anteil_halbtax'] > 100)].shape[0]
#print("Number of entries with a share above 100% for ga or halbtax:", above_100)

# Investigate population size for those entries that have shares > 100%
df_probs = df7[(df7['anteil_ga'] > 100) | (df7['anteil_halbtax'] > 100)][['plz', 'jahr', 'bevoelkerung', 'anteil_ga', 'anteil_halbtax']]
#print(df_probs)

#******************** !This task is incomplete! TO BE DISCUSSED IN GROUP *******************************************


### Joining Dataset with swiss cantons

df8 = df7.copy() #copy of original dataset

## Loading raw data (from file in repository)

# URL to raw data of swisstopo file
url_swisstopo = ("PLZ_index_swisstopo.csv")

# Load data into a dataframe
df_swisstopo1 = pd.read_csv(url_swisstopo, sep = ";")

# visual inspection
#print(df_swisstopo.head())
#print(df_swisstopo)

# Copy before joining
df_swisstopo2 = df_swisstopo1.copy()

# Check column names
#print(df_swisstopo2.columns)

# Rename column PLZ to plz
df_swisstopo2 = df_swisstopo2.rename(columns={"PLZ":"plz"})

# Check for duplicates in df_swisstopo
#print(df_swisstopo2['plz'].value_counts())

"""
Challenge: the dataset Swisstopo contains several duplicates in zip codes. This because one zip code can contain different
"locality / village / community names per zip code.
Example: 9602 is the zip code for locality Bazenheid and Müselbach, also is the zip code for the municipality of Kirchberg (SG)
and Lütisburg. The same counts for the LV95 Coordinates which are in the dataset.

--> Workaround: I removed all duplicates in the swisstopo dataset. 

Reasoning: Our "master" dataset contains only information as per zip code (one zip code per year). This defines the maximum level of "granularity" which we can reach.
Meaning that no information is lost when we removed duplicates in zip codes as we are anyway not able to perform an analysis on the base of communality.
Only issue: we may need a workaround for visualizations as the LV-95 are not of much use.

(can still be discussed if there is another idea)
"""

# remove duplicates from df_swisstopo2
df_swiss_unique = df_swisstopo2.drop_duplicates(subset = "plz") #remove duplicates in "plz" --> it keeps first plz

# Check again for duplicates in df_swiss_unique (use ob boolean mask)
plz_counts = df_swiss_unique['plz'].value_counts()
plz_duplicates = plz_counts[plz_counts > 1]
#print(plz_duplicates) # No more duplicates


# Left Join of dataframe swisstopo2 to df8 (i.e. all rows of df8 remain)
df_combined = df8.merge(df_swiss_unique, on = "plz", how = "left")

## Check if join of dataset worked properly
#print(df_combined.columns)
#print(df_combined[df_combined['Kantonskürzel'].isna()]) # if one plz from original dataset was not matched, there should be an NAN
#print(df_combined)
#df_combined.to_excel("SBB_Swisstopo.xlsx", index = False)
#print(f"This is length of df8: {len(df8)}")
#print(f"This is length of df_combined: {len(df_combined)}")

# Saving another copy of the dataset - workfile now "df9"
df9 = df_combined.copy()



"""
Remark Curdin: If we intend to perform any analysis on the base of a canton, we need figures for cantons as well.
Meaning: "anteil_ga / anteil_halbtax" per canton.

For this reason I created a new df which is per year and per canton with figures per canton.
"""

## Creating dataset with cantons per year

# grouping the dataframe by year and canton
groups = df9.groupby(["jahr", "Kantonskürzel"])

# taking below specified columns anzahl_ga, anzahl_halbtag and bevoelkerung and calculate sum for each group
df_cantons = groups[["anzahl_ga","anzahl_halbtax", "bevoelkerung"]].sum()

# Make sure that year and canton are normal columns again
df_cantons = df_cantons.reset_index()

## Testing the result
#print(df_cantons)
test_row_bs2022 = df_cantons[(df_cantons["Kantonskürzel"] == "BS") & (df_cantons["jahr"] == 2022)]
test_row_be2022 = df_cantons[(df_cantons["Kantonskürzel"] == "BE") & (df_cantons["jahr"] == 2022)]
#print(test_row_bs2022)
#print(test_row_be2022)

# --> Results do not match exactly the numbers of each cantons website but are close e.g. BS: official 196'786, our data 196'691


# Including a new column called: "total_abo" which is the sum of anzahl_ga and anzahl_halbtax
df_cantons["total_abo"] = df_cantons["anzahl_ga"] + df_cantons["anzahl_halbtax"]

# round the totals "total_abo", "anzahl_ga", "anzahl_halbtax" to whole numbers
df_cantons[["total_abo","anzahl_ga","anzahl_halbtax"]] = df_cantons[["total_abo","anzahl_ga","anzahl_halbtax"]].round(0)

# Including a new column called: "anteil_ga" which is the share of anzahl_ga in relation to bevoelkerung
df_cantons["anteil_ga"] = (df_cantons["anzahl_ga"] / df_cantons["bevoelkerung"]) * 100

# Including a new column called: "anteil_halbtax" which is the share of anzahl_ga in relation to bevoelkerung
df_cantons["anteil_halbtax"] = (df_cantons["anzahl_halbtax"] / df_cantons["bevoelkerung"]) * 100

# Including a new column called: "anteil_halbtax" which is the share of anzahl_ga in relation to bevoelkerung
df_cantons["anteil_abo_total"] = (df_cantons["total_abo"] / df_cantons["bevoelkerung"]) * 100

# round the shares to one decimal place
df_cantons[['anteil_abo_total', 'anteil_ga', 'anteil_halbtax']] = df_cantons[['anteil_abo_total', 'anteil_ga', 'anteil_halbtax']].round(1)


df_cantons1 = df_cantons.copy()

## Checking the new df
#print(df_cantons1)
#df_cantons1.to_excel("df_cantons1.xlsx", index = False)
no_cantons_year = df_cantons1.groupby("jahr")["Kantonskürzel"].nunique()
#print(no_cantons_year) #Every year has 26 cantons(additional check)

"""
The new dataframe with figures per canton will now be saved as a .pkl
***NEEDS TO BE IN SAME REPOSITORY***
"""

# Save df_cantons1 to .pkl
df_cantons1.to_pickle("df_cantons.pkl")

