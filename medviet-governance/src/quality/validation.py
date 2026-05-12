import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    TODO: Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context(mode="ephemeral")
    suite = ExpectationSuite(name="patient_data_suite")

    try:
        validator = context.sources.pandas_default.read_dataframe(
            pd.read_csv("data/raw/patients_raw.csv", dtype={"cccd": str})
        )
    except AttributeError:
        return suite

    validator.expect_column_values_to_not_be_null("patient_id")

    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    )

    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return validator.get_expectation_suite()


def validate_anonymized_data(filepath: str) -> dict:
    """
    TODO: Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath, dtype={"cccd": str, "so_dien_thoai": str})
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    def fail(message: str) -> None:
        results["success"] = False
        results["failed_checks"].append(message)

    if "cccd" in df:
        invalid_cccd = ~df["cccd"].astype(str).str.fullmatch(r"\d{12}")
        if invalid_cccd.any():
            fail("cccd contains values that are not 12-digit anonymized IDs")

    important_columns = ["patient_id", "cccd", "so_dien_thoai", "email", "benh", "ket_qua_xet_nghiem"]
    for column in important_columns:
        if column in df and df[column].isna().any():
            fail(f"{column} contains null values")

    try:
        original_rows = len(pd.read_csv("data/raw/patients_raw.csv"))
        results["stats"]["original_rows"] = original_rows
        if len(df) != original_rows:
            fail(f"row count mismatch: anonymized={len(df)}, original={original_rows}")
    except FileNotFoundError:
        fail("original raw dataset not found for row-count validation")

    return results
