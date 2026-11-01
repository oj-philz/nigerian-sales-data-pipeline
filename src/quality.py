import pandas as pd

def check_quality(data):

    valid_states = data['State'].unique()

    chk_id_notnull = data["Order ID"].notna()

    #check for duplicate Order ID
    chk_id_unique = ~data['Order ID'].duplicated(keep=False)

    chk_qty = data["Units Sold"] > 0
    
    chk_price = data["Unit Price"] >= 0

    parsed = pd.to_datetime(data["Sale Date"], errors="coerce")   # bad dates → NaT
    chk_date = parsed.notna() & (parsed <= pd.Timestamp.today())   # optional: no future dates

    chk_state = data["State"].isin(valid_states)

    chk_revenue = data["Total Sale"] >= 0

    checks = pd.DataFrame({
    "id_not_null": chk_id_notnull,
    "id_unique":   chk_id_unique,
    "qty_positive": chk_qty,
    "price_nonneg": chk_price,
    "valid_date":  chk_date,
    "valid_state": chk_state,
    "revenue_nonneg": chk_revenue,
    })

    is_valid = checks.all(axis=1)        # True only if every check passes
    #print(is_valid)

    valid_df = data[is_valid].copy()
    invalid_df = data[~is_valid].copy()

    print(valid_df.head(10))

    if not invalid_df.empty:
        invalid_df["errors"] = checks[~is_valid].apply(
        lambda row: ", ".join(row.index[~row]), axis=1)

        invalid_df.to_csv("error_log.csv", index=False)

    print((~checks).sum())
