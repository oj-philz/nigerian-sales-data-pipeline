
import pandas as pd


def check_quality(data):

    # Valid Nigerian states and the FCT
    valid_states = {
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi",
        "Bayelsa", "Benue", "Borno", "Cross River", "Delta",
        "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo",
        "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi",
        "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
        "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
        "Sokoto", "Taraba", "Yobe", "Zamfara",
        "Abuja"
    }

    # Check Order ID
    chk_id_notnull = data["Order ID"].notna()
    chk_id_unique = ~data["Order ID"].duplicated(keep=False)

    # Check sales values
    chk_qty = data["Units Sold"].notna() & (data["Units Sold"] > 0)

    chk_price = data["Unit Price"].notna() & (data["Unit Price"] >= 0)

    chk_revenue = data["Total Sale"].notna() & (data["Total Sale"] >= 0)

    # Check dates
    parsed = pd.to_datetime(data["Sale Date"], errors="coerce")

    chk_date = (
        parsed.notna()
        & (parsed <= pd.Timestamp.today())
    )

    # Check states against an external reference list
    chk_state = (
        data["State"]
        .astype("string")
        .str.strip()
        .str.title()
        .isin(valid_states)
    )

    # Combine validation checks
    checks = pd.DataFrame({
        "id_not_null": chk_id_notnull,
        "id_unique": chk_id_unique,
        "qty_positive": chk_qty,
        "price_nonneg": chk_price,
        "valid_date": chk_date,
        "valid_state": chk_state,
        "revenue_nonneg": chk_revenue
    }, index=data.index)

    # Separate valid and invalid records
    is_valid = checks.all(axis=1)

    valid_df = data[is_valid].copy()
    invalid_df = data[~is_valid].copy()

    # Attach validation errors to invalid records
    if not invalid_df.empty:

        invalid_df["errors"] = checks.loc[~is_valid].apply(
            lambda row: ", ".join(row.index[~row]),
            axis=1
        )

        invalid_df.to_csv("error_log.csv", index=False)

    # Print validation summary
    print("QUALITY CHECK RESULTS")
    print("---------------------")
    print("Total records:", len(data))
    print("Valid records:", len(valid_df))
    print("Invalid records:", len(invalid_df))

    print("\nFailures by validation rule:")
    print((~checks).sum())

    return valid_df, invalid_df

