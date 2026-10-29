import pandas as pd

def extract_data(filepath):
    df = pd.read_csv(filepath)
    return df