import pytest
import polars as pl

from cuallee import Check


def test_positive(check: Check, postgresql, db_conn_psql):
    check.has_correlation("id", "id2", 1.0)
    check.table_name = "public.test2"
    result = check.validate(db_conn_psql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()

def test_with_null(check: Check, postgresql, db_conn_psql):
    check.has_correlation("id4", "id2", 1.0)
    check.table_name = "public.test2"
    result = check.validate(db_conn_psql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()


def test_values(check: Check, postgresql, db_conn_psql):
    check.has_correlation("id", "id3", 1.0)
    check.table_name = "public.test2"
    result = check.validate(db_conn_psql)
    assert (result.select(pl.col("status")) == "PASS" ).to_series().all()


def test_coverage(check: Check):
    with pytest.raises(TypeError, match="positional arguments"):
        check.has_correlation("id", "id2", 1.0, 0.75)
