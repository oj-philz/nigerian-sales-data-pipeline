import pandas as pd

df = pd.read_csv("./data/raw/raw.csv")

print(df.head(20))
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isnull().sum())
print(df.duplicated().sum())
print(df['State'].value_counts())
print(df['Product'].value_counts())
print(df['Unit Price'])
print(df['Units Sold'])
print(df['Total Sale'])
