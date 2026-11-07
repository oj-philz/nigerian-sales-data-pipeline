
import pandas as pd
import pytest

from src.transform import transform_data


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Order ID": [
            "ORD001", "ORD002", "ORD003",
            "ORD004", "ORD005", "ORD006", "ORD007"
        ],
        "Customer Name": [
            "John", "Mary", "Peter",
            "James", "Grace", None, "David"
        ],
        "State": [
            " lagos ", "LAGOS", "lagos",
            " kano ", "KANO", "Abuja", "Abuja"
        ],
        "Product": [
            " laptop ", "LAPTOP", " laptop ",
            "Phone", "PHONE", "Tablet", "Tablet"
        ],
        "Units Sold": [2, 2, None, None, 4, 5, 3],
        "Unit Price": [100, 300, None, 200, 100, 500, 500],
        "Total Sale": [200, 600, None, 600, None, 2500, 1500],
        "Sale Date": [
            "2025-01-15", "2025-02-20", "2025-03-10",
            "2025-04-05", "2025-05-06", "2025-06-10",
            "2025-07-15"
        ],
        "Sales Channel": [
            " online ", None, " retail ",
            "web", "store", "online", "store"
        ]
    })


def test_transform_returns_dataframe(sample_data):
    result = transform_data(sample_data)

    assert isinstance(result, pd.DataFrame)


def test_drops_rows_with_missing_customer_or_order_id(sample_data):
    result = transform_data(sample_data)

    assert len(result) == 6
    assert result["Customer Name"].notna().all()
    assert result["Order ID"].notna().all()


def test_standardizes_product_and_state_names(sample_data):
    result = transform_data(sample_data)

    assert result["Product"].str.strip().str.istitle().all()
    assert result["State"].str.strip().str.istitle().all()
    assert "Laptop" in result["Product"].values
    assert "Lagos" in result["State"].values


def test_fills_missing_sales_channel_and_converts_to_category(sample_data):
    result = transform_data(sample_data)

    assert "Unknown" in result["Sales Channel"].values
    assert isinstance(result["Sales Channel"].dtype, pd.CategoricalDtype)


def test_converts_sale_date_to_datetime(sample_data):
    result = transform_data(sample_data)

    assert pd.api.types.is_datetime64_any_dtype(result["Sale Date"])


def test_extracts_year_and_month(sample_data):
    result = transform_data(sample_data)

    assert "Year" in result.columns
    assert "Month" in result.columns

    first_row = result.iloc[0]

    assert first_row["Year"] == 2025
    assert first_row["Month"] == 1


def test_imputes_missing_unit_price_with_product_median(sample_data):
    result = transform_data(sample_data)

    laptop_row = result[result["Order ID"] == "ORD003"].iloc[0]

    # Median of the two existing Laptop prices: 100 and 300
    assert laptop_row["Unit Price"] == 200


def test_imputes_missing_units_sold_with_product_mode(sample_data):
    result = transform_data(sample_data)

    laptop_row = result[result["Order ID"] == "ORD003"].iloc[0]

    # Existing Laptop quantities are both 2
    assert laptop_row["Units Sold"] == 2


def test_calculates_missing_units_sold_from_total_sale(sample_data):
    result = transform_data(sample_data)

    phone_row = result[result["Order ID"] == "ORD004"].iloc[0]

    # 600 / 200 = 3
    assert phone_row["Units Sold"] == 3


def test_calculates_missing_total_sale(sample_data):
    result = transform_data(sample_data)

    phone_row = result[result["Order ID"] == "ORD005"].iloc[0]

    # 4 * 100 = 400
    assert phone_row["Total Sale"] == 400


def test_creates_imputation_tracking_flags(sample_data):
    result = transform_data(sample_data)

    assert "is_price_imputed" in result.columns
    assert "is_volume_imputed" in result.columns

    laptop_row = result[result["Order ID"] == "ORD003"].iloc[0]

    assert laptop_row["is_price_imputed"]
    assert laptop_row["is_volume_imputed"]


def test_imputation_flags_preserve_original_missing_values(sample_data):
    result = transform_data(sample_data)

    # ORD003 originally had missing price, quantity and total sale.
    row = result[result["Order ID"] == "ORD003"].iloc[0]

    assert row["is_price_imputed"] == True
    assert row["is_volume_imputed"] == True

    # ORD004 had a missing quantity, but its total sale was available.
    row = result[result["Order ID"] == "ORD004"].iloc[0]

    assert row["is_volume_imputed"] == False
