import polars as pl

from cuallee import Check


def test_positive(check: Check, db_conn_mysql):
    check.not_contained_in("id2", [1, 2, 3, 4, 5])
    check.table_name = "public.test1"
    result = check.validate(db_conn_mysql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()


def test_negative(check: Check, db_conn_mysql):
    check.not_contained_in("id", [1, 2, 3, 4, 5])
    check.table_name = "public.test1"
    result = check.validate(db_conn_mysql)
    assert (result.select(pl.col("status")) == "FAIL" ).to_series().all()


def test_coverage(check: Check, db_conn_mysql):
    check.not_contained_in( "id5", [0, 1, 2], 0.2)
    check.table_name = "public.test1"
    result = check.validate(db_conn_mysql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()
    assert (result.select(pl.col("pass_rate")) == 2/10).to_series().all()