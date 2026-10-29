import pandas as pd

df = pd.read_csv("./data/raw/raw.csv")

#print(df.head())
#print(df.shape)
#print(df.columns)
#print(df.dtypes)
#print(df.isnull().sum())
#print(df.duplicated().sum())
print(df['Sales Channel'].unique())