import numpy as np
import pandas as pd

path = "SBB_GA_Halbtax_Data.csv"

df1 = pd.read_csv(path)

#Basic Slicing [row-Index, column label]
df2 = df1.loc[2:50, "hta_adt_meta_prezzo_flag"]

#Basic Slicing [row-Index, column index]
df3 = df1.iloc[2:50, 1:3]


"""
Data sets may contain “impurities”, that may be:
•Missing Data: information is absent or not recorded
-NaN Bevölkerung, 
-NaN Anteil_ga_Besitzer 
-NaN Anteil_ha_Besitzer 

-Kanton der Gemeinde zuordnen

•Duplicate Data: repeated entries that can skew results
•Inconsistent Data: not matching data across different sources or formats
•Incorrect Data: errors, such as typos or incorrect values
•Outliers: significant deviations from the norm, which may indicate errors or rare events
•Irrelevant Data: data that does not contribute to the analysis or decision-making process
•Unformatted Data: not in a standard format, making it difficult to analyze
•Stale Data: outdated information
•Ambiguous Data: data that can be interpreted in multiple ways

Depending of the type of the impurity and the information it represents, it requires different techniques to reveal and correct them. Removing data is not always the best solution, outlier definition depends on the context.

Data cleaning may include: interpolation, average calculation, type conversion, multiplication, classification, etc.

"""
# Shows all columns and rows with no breaks. 100= 100 rows,columnsNone= No restriction
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)

# PLZ containing ga_ag_flag = 1.0. This means that less than 20 GA's were sold. Those Towns do instead have an average value.
df4 = df1[df1["ga_ag_flag"].notna()]
print(len(df4))
print(df4[0:100])

"""
Wenn flag = 1.0 (GA) bzw. 2.0 (Halbtax), dann wird der Durchschnitt pro Jahr und PLZ-Range(z.b. 1000 - 1999) verwendet bei Gemeinden, welche <20 GA's/Halbtax gekauft haben. 
"""


# PLZ containing ga_ag_flag = NaN. This means that more than 20 GA's were sold. Those Towns do instead have the absolute value.
df5 = df1[df1["ga_ag_flag"].isna()]
#print(len(df5))
#print(df5[-100:])


#filter nach PLZ
df_plz_single = df1[df1["plz_npa"] == 8784]
#print(df_plz_single)

#von bis
df_plz_filter = df1[(df1["plz_npa"] >= 8000) & (df1["plz_npa"] <= 8999)]
#print(df_plz_filter)

# bevölkerungsfilter
df_bevolkerung = df1[(df1["bevolkerung"]) & (df1["jahr_an_anno"] < 2023)]
print(len(df_bevolkerung))
print(df_bevolkerung)

#anteil_hta_filter
df_anteil_hta = df1[(df1["anteil_hta_besitzer_"] > 90)] # & (df1["bevolkerung"] < 100)]
#print(len(df_anteil_hta))
#print(df_anteil_hta[-100:])

df_anteil_hta_nan = df1[(df1["anteil_hta_besitzer_"].isna()) & (df1["jahr_an_anno"] > 2022)]
df_anteil_ga_besitzer = df1[(df1["anteil_ga_besitzer"].isna()) & (df1["jahr_an_anno"] > 2022)]
#print(len(df_anteil_hta_nan))
#print(len(df_anteil_ga_besitzer))

df_ga_ag = df1[df1["ga_ag"] == 0]
#print(df_ga_ag)

# Duplikate prüfen
#print(df1.duplicated().sum())

