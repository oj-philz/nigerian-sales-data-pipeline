import pandas as pd
import pytest

from unittest.mock import patch
from src import pipeline


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Order ID": ["ORD001", "ORD002", "ORD003"],
        "Customer Name": ["John", "Mary", "Peter"],
        "Product": ["Laptop", "Phone", "Tablet"]
    })


def test_pipeline_executes_all_stages(sample_data):

    valid_df = sample_data.iloc[:2].copy()
    invalid_df = sample_data.iloc[2:].copy()

    with patch("src.pipeline.extract_data", return_value=sample_data) as mock_extract, \
         patch("src.pipeline.transform_data", return_value=sample_data) as mock_transform, \
         patch("src.pipeline.check_quality", return_value=(valid_df, invalid_df)) as mock_quality, \
         patch("src.pipeline.load_data", return_value=2) as mock_load:

        pipeline.run_pipeline()

        mock_extract.assert_called_once_with("data/raw/raw.csv")
        mock_transform.assert_called_once_with(sample_data)
        mock_quality.assert_called_once_with(sample_data)
        mock_load.assert_called_once_with(valid_df, replace=True)


def test_pipeline_loads_only_valid_records(sample_data):

    valid_df = sample_data.iloc[:2].copy()
    invalid_df = sample_data.iloc[2:].copy()

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch("src.pipeline.transform_data", return_value=sample_data), \
         patch("src.pipeline.check_quality", return_value=(valid_df, invalid_df)), \
         patch("src.pipeline.load_data", return_value=2) as mock_load:

        pipeline.run_pipeline()

        loaded_data = mock_load.call_args.args[0]

        assert len(loaded_data) == 2
        assert "ORD003" not in loaded_data["Order ID"].values


def test_pipeline_loads_zero_records_when_all_are_invalid(sample_data):

    empty_valid_df = sample_data.iloc[0:0].copy()
    invalid_df = sample_data.copy()

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch("src.pipeline.transform_data", return_value=sample_data), \
         patch("src.pipeline.check_quality", return_value=(empty_valid_df, invalid_df)), \
         patch("src.pipeline.load_data", return_value=0) as mock_load:

        pipeline.run_pipeline()

        mock_load.assert_called_once_with(empty_valid_df, replace=True)


def test_pipeline_stops_if_extraction_fails():

    with patch(
        "src.pipeline.extract_data",
        side_effect=FileNotFoundError("Dataset not found")
    ):

        with pytest.raises(FileNotFoundError, match="Dataset not found"):
            pipeline.run_pipeline()


def test_pipeline_stops_if_transformation_fails(sample_data):

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch(
             "src.pipeline.transform_data",
             side_effect=ValueError("Transformation failed")
         ):

        with pytest.raises(ValueError, match="Transformation failed"):
            pipeline.run_pipeline()


def test_pipeline_stops_if_quality_check_fails(sample_data):

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch("src.pipeline.transform_data", return_value=sample_data), \
         patch(
             "src.pipeline.check_quality",
             side_effect=ValueError("Quality check failed")
         ):

        with pytest.raises(ValueError, match="Quality check failed"):
            pipeline.run_pipeline()


def test_pipeline_stops_if_loading_fails(sample_data):

    valid_df = sample_data.copy()
    invalid_df = sample_data.iloc[0:0].copy()

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch("src.pipeline.transform_data", return_value=sample_data), \
         patch("src.pipeline.check_quality", return_value=(valid_df, invalid_df)), \
         patch(
             "src.pipeline.load_data",
             side_effect=RuntimeError("Database unavailable")
         ):

        with pytest.raises(RuntimeError, match="Database unavailable"):
            pipeline.run_pipeline()


def test_pipeline_prints_execution_summary(sample_data, capsys):

    valid_df = sample_data.iloc[:2].copy()
    invalid_df = sample_data.iloc[2:].copy()

    with patch("src.pipeline.extract_data", return_value=sample_data), \
         patch("src.pipeline.transform_data", return_value=sample_data), \
         patch("src.pipeline.check_quality", return_value=(valid_df, invalid_df)), \
         patch("src.pipeline.load_data", return_value=2):

        pipeline.run_pipeline()

    output = capsys.readouterr().out

    assert "Extracted:   3" in output
    assert "Transformed: 3" in output
    assert "Valid:       2" in output
    assert "Invalid:     1" in output
    assert "Loaded:      2" in output
    assert "PIPELINE COMPLETED SUCCESSFULLY" in output
