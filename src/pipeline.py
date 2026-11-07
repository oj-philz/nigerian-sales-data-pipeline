
from extract import extract_data
from transform import transform_data
from quality import check_quality
from load import load_data


def run_pipeline():

    print("\nSTARTING NIGERIAN SALES DATA PIPELINE")
    print("=" * 45)

    # 1. Extract
    print("\nSTEP 1: Extracting data...")

    raw_df = extract_data("data/raw/raw.csv")

    print(f"Extracted records: {len(raw_df)}")

    # 2. Transform
    print("\nSTEP 2: Transforming data...")

    transformed_df = transform_data(raw_df)

    print(f"Transformed records: {len(transformed_df)}")

    # 3. Quality checks
    print("\nSTEP 3: Running quality checks...")

    valid_df, invalid_df = check_quality(transformed_df)

    print(f"Valid records: {len(valid_df)}")
    print(f"Invalid records: {len(invalid_df)}")

    # 4. Load valid records
    print("\nSTEP 4: Loading valid records...")

    loaded_records = load_data(valid_df, replace=True)

    # 5. Execution summary
    print("\nPIPELINE EXECUTION SUMMARY")
    print("=" * 45)

    print(f"Extracted:   {len(raw_df)}")
    print(f"Transformed: {len(transformed_df)}")
    print(f"Valid:       {len(valid_df)}")
    print(f"Invalid:     {len(invalid_df)}")
    print(f"Loaded:      {loaded_records}")

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_pipeline()
