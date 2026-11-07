import pandas as pd


def transform_data(df):

    # Standerdized the text in product and state columns
    df['Product'] = df['Product'].str.strip().str.title()
    df['State'] = df['State'].str.strip().str.title()

    #drop rows with missing Customer Name and Order ID
    df = df.dropna(subset=["Customer Name", "Order ID"])

    # Categorize missing Sales Channel as 'Unknown'
    df['Sales Channel'] = df['Sales Channel'].str.strip().str.title()
    df["Sales Channel"] = df["Sales Channel"].fillna("Unknown")

    # Convert to Categorical Second
    df["Sales Channel"] = df["Sales Channel"].astype("category")

    # Convert Sale Date from str to datetime
    df["Sale Date"] = pd.to_datetime(df["Sale Date"], errors="coerce") 

    # Create tracking flags before mutating the volume data
    df["is_price_imputed"] = df["Unit Price"].isna()  # Track initial state if needed
    df["is_volume_imputed"] = df["Units Sold"].isna() & df["Total Sale"].isna()

    df['Unit Price'] = df.groupby('Product')['Unit Price'].transform(lambda x: x.fillna(x.median()))

    # Cross-Column Algebraic Calculation
    # Case A: Sold is missing, Sale is present
    mask_sold = df["Units Sold"].isna() & df["Total Sale"].notna()
    df.loc[mask_sold, "Units Sold"] = (df.loc[mask_sold, "Total Sale"] / df.loc[mask_sold, "Unit Price"])

    # Case B: Sale is missing, Sold is present
    mask_sale = df["Total Sale"].isna() & df["Units Sold"].notna()
    df.loc[mask_sale, "Total Sale"] = (df.loc[mask_sale, "Units Sold"] * df.loc[mask_sale, "Unit Price"])

    # Fallback for rows where BOTH Sold and Sale are missing
    # Group by Product_ID to find typical purchase volume for that specific item
    df["Units Sold"] = df.groupby("Product")["Units Sold"].transform(
        lambda x: x.fillna(x.mode()[0])
    )

    # Overall fallback if item volume history is empty
    df["Units Sold"] = df["Units Sold"].fillna(df["Units Sold"].mode()[0])

    # Final math pass to ensure Total Sale matches the newly filled Units Sold
    mask_final = df["Total Sale"].isna()
    df.loc[mask_final, "Total Sale"] = (
        df.loc[mask_final, "Units Sold"] * df.loc[mask_final, "Unit Price"]
    )

    # Create year and month columns
    df["Year"] = df["Sale Date"].dt.year
    df["Month"] = df["Sale Date"].dt.month
    
    return df