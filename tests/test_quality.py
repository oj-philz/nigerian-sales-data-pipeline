
import pandas as pd
import pytest

from src.quality import check_quality


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
        "Sale Date": ["2024-01-10", "2024-02-15"]
    })


def run_quality_check(data, tmp_path, monkeypatch):

    monkeypatch.chdir(tmp_path)

    valid_df, invalid_df = check_quality(data)

    return valid_df, invalid_df


def test_all_valid_records(sample_data, tmp_path, monkeypatch):

    valid_df, invalid_df = run_quality_check(
        sample_data, tmp_path, monkeypatch
    )

    assert len(valid_df) == 2
    assert invalid_df.empty


@pytest.mark.parametrize(
    "column,value,error",
    [
        ("Order ID", None, "id_not_null"),
        ("Units Sold", 0, "qty_positive"),
        ("Units Sold", -5, "qty_positive"),
        ("Unit Price", -100, "price_nonneg"),
        ("Total Sale", -500, "revenue_nonneg"),
        ("Sale Date", "invalid-date", "valid_date"),
        ("State", "Atlantis", "valid_state"),
    ]
)
def test_invalid_records(
    sample_data, column, value, error, tmp_path, monkeypatch
):

    sample_data.loc[0, column] = value

    valid_df, invalid_df = run_quality_check(
        sample_data, tmp_path, monkeypatch
    )

    assert len(valid_df) == 1
    assert len(invalid_df) == 1
    assert error in invalid_df.iloc[0]["errors"]


def test_duplicate_order_ids(sample_data, tmp_path, monkeypatch):

    sample_data.loc[1, "Order ID"] = "ORD001"

    valid_df, invalid_df = run_quality_check(
        sample_data, tmp_path, monkeypatch
    )

    assert valid_df.empty
    assert len(invalid_df) == 2
    assert invalid_df["errors"].str.contains(
        "id_unique"
    ).all()


def test_future_sale_date(sample_data, tmp_path, monkeypatch):

    sample_data.loc[0, "Sale Date"] = "2099-01-01"

    valid_df, invalid_df = run_quality_check(
        sample_data, tmp_path, monkeypatch
    )

    assert len(invalid_df) == 1
    assert "valid_date" in invalid_df.iloc[0]["errors"]


def test_missing_numeric_values(sample_data, tmp_path, monkeypatch):

    sample_data.loc[0, "Units Sold"] = None

    valid_df, invalid_df = run_quality_check(
        sample_data, tmp_path, monkeypatch
    )

    assert len(valid_df) == 1
    assert "qty_positive" in invalid_df.iloc[0]["errors"]


def test_error_log_generation(sample_data, tmp_path, monkeypatch):

    sample_data.loc[0, "State"] = "Atlantis"

    run_quality_check(sample_data, tmp_path, monkeypatch)

    error_log = tmp_path / "error_log.csv"

    assert error_log.exists()

    logged_data = pd.read_csv(error_log)

    assert len(logged_data) == 1
    assert "errors" in logged_data.columns
