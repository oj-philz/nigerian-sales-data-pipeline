
import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from src import load as load_module


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Order ID": ["ORD001", "ORD002"],
        "Customer Name": ["John", "Mary"],
        "State": ["Lagos", "Abuja"],
        "Product": ["Laptop", "Phone"],
        "Units Sold": [5, 3],
        "Unit Price": [200000, 150000],
        "Total Sale": [1000000, 450000],
        "Sale Date": pd.to_datetime(["2025-01-10", "2025-02-15"]),
        "Sales Channel": ["Online", "Retail"],
        "Year": [2025, 2025],
        "Month": [1, 2]
    })


@pytest.fixture
def test_engine(monkeypatch):
    # Use a temporary SQLite database instead of the real PostgreSQL database.
    engine = create_engine("sqlite:///:memory:")

    monkeypatch.setattr(load_module, "engine", engine)

    yield engine

    engine.dispose()


def test_load_data_successfully(sample_data, test_engine):
    result = load_module.load_data(sample_data)

    assert result == 2

    with test_engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar()

    assert count == 2


def test_load_data_maps_columns_correctly(sample_data, test_engine):
    load_module.load_data(sample_data)

    with test_engine.connect() as connection:
        result = pd.read_sql_query(
            text("SELECT * FROM sales ORDER BY order_id"),
            connection
        )

    expected_columns = [
        "order_id",
        "customer_name",
        "state",
        "product",
        "units_sold",
        "unit_price",
        "total_sale",
        "sale_date",
        "sales_channel",
        "year",
        "month"
    ]

    assert list(result.columns) == expected_columns
    assert result.iloc[0]["order_id"] == "ORD001"
    assert result.iloc[0]["customer_name"] == "John"
    assert result.iloc[0]["product"] == "Laptop"


def test_load_data_empty_dataframe(test_engine):
    result = load_module.load_data(pd.DataFrame())

    assert result == 0


def test_load_data_rejects_missing_columns(sample_data, test_engine):
    sample_data = sample_data.drop(columns=["Product"])

    with pytest.raises(ValueError, match="Missing DataFrame columns"):
        load_module.load_data(sample_data)


def test_load_data_rejects_missing_order_id(sample_data, test_engine):
    sample_data.loc[0, "Order ID"] = None

    with pytest.raises(ValueError, match="missing Order IDs"):
        load_module.load_data(sample_data)


def test_load_data_rejects_duplicate_order_ids(sample_data, test_engine):
    sample_data.loc[1, "Order ID"] = "ORD001"

    with pytest.raises(ValueError, match="Duplicate Order IDs"):
        load_module.load_data(sample_data)


def test_load_data_appends_records(sample_data, test_engine):
    load_module.load_data(sample_data.iloc[[0]])
    load_module.load_data(sample_data.iloc[[1]])

    with test_engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar()

    assert count == 2


def test_load_data_replaces_existing_records(sample_data, test_engine):
    load_module.load_data(sample_data)

    replacement_data = sample_data.iloc[[0]].copy()
    replacement_data["Order ID"] = "ORD003"

    result = load_module.load_data(
        replacement_data,
        replace=True
    )

    assert result == 1

    with test_engine.connect() as connection:
        records = pd.read_sql_query(
            text("SELECT order_id FROM sales"),
            connection
        )

    assert len(records) == 1
    assert records.iloc[0]["order_id"] == "ORD003"
