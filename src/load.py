
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL


# Load database credentials
load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME")
)

engine = create_engine(DATABASE_URL)


def load_data(df: pd.DataFrame, replace: bool = False) -> int:
    """
    Load validated sales data into PostgreSQL.
    """

    if df.empty:
        print("No records to load.")
        return 0

    column_mapping = {
        "Order ID": "order_id",
        "Customer Name": "customer_name",
        "State": "state",
        "Product": "product",
        "Units Sold": "units_sold",
        "Unit Price": "unit_price",
        "Total Sale": "total_sale",
        "Sale Date": "sale_date",
        "Sales Channel": "sales_channel",
        "Year": "year",
        "Month": "month"
    }

    missing_columns = set(column_mapping) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing DataFrame columns: {missing_columns}"
        )

    load_df = df[list(column_mapping)].rename(
        columns=column_mapping
    )

    if load_df["order_id"].isna().any():
        raise ValueError("Cannot load records with missing Order IDs.")

    if load_df["order_id"].duplicated().any():
        raise ValueError("Duplicate Order IDs detected.")

    with engine.begin() as connection:

        if replace and inspect(connection).has_table("sales"):
            if connection.dialect.name == "postgresql":
                connection.execute(text("TRUNCATE TABLE sales"))
            else:
                connection.execute(text("DELETE FROM sales"))
                
        load_df.to_sql(
            name="sales",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500
        )

    print(f"Successfully loaded {len(load_df)} records.")

    return len(load_df)
