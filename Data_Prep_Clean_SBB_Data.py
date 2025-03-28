import numpy as np
import pandas as pd

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






