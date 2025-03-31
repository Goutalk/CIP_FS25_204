import pandas as pd

df = pd.read_excel("su-d-05.02.91.xlsx", header = 4)

df = df.iloc[37:60]

df = df.loc[:, df.columns.intersection(["Jahr / Année","Bleifrei 98\nsans plomb 98","Diesel"])]
df = df.rename(columns={'Bleifrei 98\nsans plomb 98': 'Bleifrei 98', "Jahr / Année":"Year"})

print(df)
