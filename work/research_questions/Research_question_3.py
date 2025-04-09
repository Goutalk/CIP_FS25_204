import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px



#loading both datasets into a dataframe
df_fuel = pd.read_excel("../../data/raw/su-d-05.02.91.xlsx", header = 4)
df_main_data = pd.read_pickle("../../data/processed/df_cantons.pkl")

#taking only the relevant years (the same that are available in the main data set)
df_fuel = df_fuel.iloc[47:60]

#filter for the relevant columns
df_fuel = df_fuel.loc[:, df_fuel.columns.intersection(["Jahr / Année","Bleifrei 98\nsans plomb 98","Diesel"])]
df_fuel = df_fuel.rename(columns={'Bleifrei 98\nsans plomb 98': 'Bleifrei 98', "Jahr / Année":"jahr"})

#plot the gas prices over time
sns.lineplot(x="jahr", y="Bleifrei 98", data=df_fuel, marker="o",  color = "red", label ="Bleifrei 98 price").set(title="Price development for Diesel and Bleifrei 98", xlabel="Year", ylabel="Price in CHF per liter")
sns.lineplot(x="jahr", y="Diesel", data=df_fuel, marker="o", color = "black", label ="Diesel price")
plt.show()

#plot the GA and Halbtax sale over time. This is the
df_main_data_grouped = df_main_data.groupby("jahr")[["anzahl_ga", "anzahl_halbtax"]].sum().reset_index()

sns.lineplot(x="jahr", y="anzahl_ga", data=df_main_data_grouped, marker="o",  color = "red", label ="Sold GA's").set(title="Purchase development of GA's and Halbtax's", xlabel="Year", ylabel="Sold units")
sns.lineplot(x="jahr", y="anzahl_halbtax", data=df_main_data_grouped, marker="o", color = "black", label ="Sold Halbtax's")
plt.show()

#merge datasets
df_joined = pd.merge(df_fuel, df_main_data_grouped, on= "jahr", how="inner")
#print(df_joined)

#calculate correlation between GA_sales / halbtax_sales and price development of fuel
correlation_anzahl_ga = df_joined["anzahl_ga"].corr(df_joined["Bleifrei 98"])
correlation_anzahl_halbtax = df_joined["anzahl_halbtax"].corr(df_joined["Bleifrei 98"])
print(correlation_anzahl_ga)
print(correlation_anzahl_halbtax)

#scatterplots only showing for the Bleifrei 98 data, as Diesel behaves very similar. we want to see
#whether the price for the fuel can be a predictor for the purchase of GA's
sns.scatterplot(data=df_joined, x="Bleifrei 98", y="anzahl_ga")
plt.show()
sns.scatterplot(data=df_joined, x="Bleifrei 98", y="anzahl_halbtax")
plt.show()

#New data frame which includes the cantons, for filtering purposes. Join the data set, which is not grouped by year.
#plot the data with the plotly library to hover over the visualization.
#Its very interesting that most of the cantons follow a very similar pattern, the cantons behave very similar
#when fuel prices are increasing
df_joined_filter = pd.merge(df_fuel, df_main_data, on= "jahr", how="inner")
print(df_joined_filter)
scatterplot_ga_with_filter = px.scatter(df_joined_filter, x="Bleifrei 98", y="anzahl_ga", color="Kantonskürzel", title ="Fuel price vs GA Sales by canton", hover_data =["jahr","Kantonskürzel"])
scatterplot_ga_with_filter.show()

#same plot for halbtax sales
#behaves similar for halbtax, as for GA.
scatterplot_halbtax_with_filter = px.scatter(df_joined_filter, x="Bleifrei 98", y="anzahl_halbtax", color="Kantonskürzel", title ="Fuel price vs Halbtax Sales by canton", hover_data =["jahr","Kantonskürzel"])
scatterplot_halbtax_with_filter.show()
