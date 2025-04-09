import pandas as pd
import numpy
import matplotlib.pyplot as plt

# Loading dataframe df_cantons.pkl
df_cantons2 = pd.read_pickle("df_cantons.pkl")

# Checking if loaded correctly
#print(df_cantons2)
#print(len(df_cantons2))

"""
The following part intends to visually assess the datasets by 
various types of plots
"""

## Time Series of share of anteil_ga, anteil_halbtax and anteil_abo_total

# Calculating the WEIGHTED Average per population, grouped by year
df_weighted_average = df_cantons2.groupby('jahr').apply(
    lambda x: pd.Series({
        'anteil_ga': (x['anzahl_ga'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_halbtax': (x['anzahl_halbtax'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_abo': (x['total_abo'].sum() / x['bevoelkerung'].sum()) * 100
    })
).reset_index()

# visual inspection
#print(df_weighted_average)

# Plot of the time series

df_weighted_average.set_index("jahr")[["anteil_ga","anteil_halbtax", "anteil_abo"]].plot(kind='line', marker='o', title="Weighted average of GA, Halbtax and Total Abo per Year")
plt.ylabel("Share (%)")
plt.xlabel("Year")
plt.grid(True)
plt.tight_layout()
plt.show()

