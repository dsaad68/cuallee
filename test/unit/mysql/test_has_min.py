import polars as pl

from cuallee import Check


def test_positive(check: Check, db_conn_mysql):
    check.has_min("id", 1)
    check.table_name = "public.test1"
    result = check.validate(db_conn_mysql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()

def test_negative(check: Check, db_conn_mysql):
    check.has_min("id", 10)
    check.table_name = "public.test1"
    result = check.validate(db_conn_mysql)
    assert (result.select(pl.col("status")) == "FAIL" ).to_series().all()

