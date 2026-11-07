
import pandas as pd
import pytest

from src.extract import extract_data


def test_extract_data_successfully(tmp_path):

    sample_data = pd.DataFrame({
        "Order ID": ["ORD001", "ORD002"],
        "Product": ["Laptop", "Phone"],
        "Units Sold": [5, 3]
    })

    filepath = tmp_path / "sample.csv"
    sample_data.to_csv(filepath, index=False)

    result = extract_data(filepath)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == list(sample_data.columns)
    assert result["Order ID"].tolist() == ["ORD001", "ORD002"]


def test_extract_data_missing_file(tmp_path):

    filepath = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        extract_data(filepath)


def test_extract_data_empty_file(tmp_path):

    filepath = tmp_path / "empty.csv"
    filepath.write_text("")

    with pytest.raises(pd.errors.EmptyDataError):
        extract_data(filepath)


def test_extract_data_headers_only(tmp_path):

    filepath = tmp_path / "headers.csv"
    filepath.write_text("Order ID,Product,Units Sold\n")

    result = extract_data(filepath)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["Order ID", "Product", "Units Sold"]


def test_extract_data_preserves_missing_values(tmp_path):

    sample_data = pd.DataFrame({
        "Order ID": ["ORD001", "ORD002"],
        "Product": ["Laptop", "Phone"],
        "Units Sold": [5, None]
    })

    filepath = tmp_path / "missing_values.csv"
    sample_data.to_csv(filepath, index=False)

    result = extract_data(filepath)

    assert len(result) == 2
    assert result["Units Sold"].isna().sum() == 1
