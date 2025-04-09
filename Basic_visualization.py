from statistics import LinearRegression

import pandas as pd
import seaborn as sns
from networkx import descendants
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
from pandas import to_numeric

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
df_weighted_average = df_cantons2.groupby(['jahr', "Kantonskürzel"]).apply(
    lambda x: pd.Series({
        'anteil_ga': (x['anzahl_ga'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_halbtax': (x['anzahl_halbtax'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_abo': (x['total_abo'].sum() / x['bevoelkerung'].sum()) * 100,
    })
).reset_index()
print(df_weighted_average)
# visual inspection
#print(df_weighted_average)

# Plot of the time series

#df_weighted_average.set_index("jahr")[["anteil_ga","anteil_halbtax", "anteil_abo"]].plot(kind='line', marker='o', title="Weighted average of GA, Halbtax and Total Abo per Year")
#plt.ylabel("Share (%)")
#plt.xlabel("Year")
#plt.grid(True)
#plt.tight_layout()
#plt.show()

# Basic visualizations Christian

#Simple Boxplpot showing the distribution of all GA-shares of the cantons and years.
sns.boxplot(data=df_weighted_average, y="anteil_ga")
plt.show()

#Simple Boxplpot showing the distribution of all Halbtax-shares of the cantons and years.
sns.boxplot(data=df_weighted_average, y="anteil_halbtax")
plt.show()


#Barchart sorted by anteil GA
df_weighted_average = df_weighted_average.sort_values(by='anteil_ga', ascending=False)
sns.barplot(df_weighted_average, x="Kantonskürzel", y="anteil_ga", errorbar=None, order = df_weighted_average['Kantonskürzel'])
plt.xticks(fontsize=8)
plt.show()

#Barchart sorted by anteil Halbtax
df_weighted_average = df_weighted_average.sort_values(by='anteil_halbtax', ascending=False)
sns.barplot(df_weighted_average, x="Kantonskürzel", y="anteil_halbtax", errorbar=None, order = df_weighted_average['Kantonskürzel'])
plt.xticks(fontsize=8)
plt.show()


#I decided to focus on seaborn as it builds up on matplotlib and is known to use more aesthetic visualizations
#The linechart shows the distribution of the shares of the cantons
plt.figure(figsize=(10, 6))
sns.lineplot(x="jahr", y="anteil_ga", data=df_weighted_average, marker="o",  color = "blue", label ="Share of GA").set(title="Weighted average of GA, Halbtax and Total Abo per Year", xlabel="Year", ylabel="Share (%)")
sns.lineplot(x="jahr", y="anteil_halbtax", data=df_weighted_average, marker="o", color = "green", label ="Share of Halbtax")
sns.lineplot(x="jahr", y="anteil_abo", data=df_weighted_average, marker="o", color = "turquoise", label ="Share of GA and Halbtax")
plt.show()

#Forecast with linear regression
#I used linear regression and not ARIMA simply out of simplicity and because ARIMA is used if
#the time series shows a clear trend or seasonality and provides more time steps
#group the data only by year
df_weighted_average_3 = df_cantons2.groupby(['jahr']).apply(
    lambda x: pd.Series({
        'anteil_ga': (x['anzahl_ga'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_halbtax': (x['anzahl_halbtax'].sum() / x['bevoelkerung'].sum()) * 100,
        'anteil_abo': (x['total_abo'].sum() / x['bevoelkerung'].sum()) * 100,
    })
).reset_index()

#defining variables
Year = df_weighted_average_3[["jahr"]] # the year is going to be our predictor or independent variable
Share_GA = df_weighted_average_3['anteil_ga'] # the share of GA is what we want to predict
Share_Halbtax = df_weighted_average_3['anteil_halbtax'] # as well as the share of Halbtax


#Training the model with integrated linear fit function
model_GA = LinearRegression().fit(Year, Share_GA)
model_Halbtax = LinearRegression().fit(Year, Share_Halbtax)

#defining the period we want to predict
future_years = np.arange(2025, 2029).reshape(-1, 1) #reshape is making the array 2D

#predict future values
GA_share_predicted = model_GA.predict(future_years)
Halbtax_share_predicted = model_Halbtax.predict(future_years)

#now plot the predictions
plt.figure(figsize=(10, 6))
plt.scatter(Year, Share_GA, color="blue", label="Actual GA")
plt.scatter(Year, Share_Halbtax, color="green", label="Actual Halbtax")

plt.plot(future_years, GA_share_predicted, color="orange", marker = "o", label="Predicted Values")
plt.plot(future_years, Halbtax_share_predicted, color="orange", marker="o")

plt.xlabel("Year")
plt.ylabel("Share (%)")
plt.title("Forecasting GA, Halbtax Using Linear Regression")
plt.legend()
plt.grid(False)
plt.show()


#heatmap showing the GA-Shares
#on the x-axis are the years and on the y-axis the cantons. Taking a quick glance, the heat
#mat indicates Bern having the highest GA-share while Appenzell Innerrhoden, Genf and Tessin having
#the smallest GA share. For every canton is a cut after 2020. This becomes clear with the colours
#becoming darker.
GA_heatmap = df_weighted_average.pivot(index="Kantonskürzel", columns="jahr", values="anteil_ga")
plt.yticks(fontsize=7)
plt.title("GA")
sns.heatmap(GA_heatmap)
plt.show()

#heatmap showing the HT-Shares
#Again, Bern and Genf belong to the cantons with very low Halbtax share. Compared to GA shares there
#is no decay after 2020. The opposite is the case: the share is overall increasing.
Halbtax_heatmap = df_weighted_average.pivot(index="Kantonskürzel", columns="jahr", values="anteil_halbtax")
plt.yticks(fontsize=7)
plt.title("Halbtax")
sns.heatmap(Halbtax_heatmap)
plt.show()


#Boxplot showing the distribution of the data
sns.boxplot(data=df_weighted_average, x="jahr", y="anteil_ga")
plt.show()

#Violin plot which shows the distribution of the data better than boxplots
sns.violinplot(data=df_weighted_average, x="jahr", y="anteil_ga")
plt.show()
