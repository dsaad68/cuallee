import daft
import operator
import numpy as np

from typing import Union
from toolz import first
from numbers import Number
from typing import Dict, List

from cuallee import Check, Rule


class Compute:

    def is_complete(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).not_null().cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def are_complete(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        col_names = rule.column
        perdicate = [ daft.col(col_name).not_null().cast(daft.DataType.int64()).sum() for col_name in col_names]
        return dataframe.select(*perdicate).to_pandas().astype(int).sum().sum() / len(col_names)

    def is_unique(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column)
        return dataframe.select(perdicate).distinct().count(perdicate).to_pandas().iloc[0, 0]

    def are_unique(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        # TODO: Find a way to do this in daft and not pandas
        perdicate = [ daft.col(col_name) for col_name in rule.column]
        return dataframe.select(*perdicate).to_pandas().nunique().sum() / len(rule.column)

    def is_greater_than(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column) > rule.value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_greater_or_equal_than(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column) >= rule.value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_less_than(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column) < rule.value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_less_or_equal_than(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column) <= rule.value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_equal_than(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column) == rule.value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def has_pattern(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = (daft.col(rule.column).str.match(rule.value)).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def has_min(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).min()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]  == rule.value

    def has_max(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).max()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0] == rule.value

    def has_std(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        # TODO: Find a way to do this in daft and not pandas
        return dataframe.to_pandas().loc[:, rule.column].std() == rule.value

    def has_mean(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).mean()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]  == rule.value

    def has_sum(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]  == rule.value

    def has_cardinality(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column)
        return dataframe.select(perdicate).distinct().count(perdicate).to_pandas().iloc[0, 0] == rule.value

    def has_infogain(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column)
        return dataframe.select(perdicate).distinct().count(perdicate).to_pandas().iloc[0, 0] > 1

    def is_between(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = ( ( daft.col(rule.column) >= min(rule.value) ).__and__( daft.col(rule.column) <= max(rule.value) ) ).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_contained_in(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        rule_value = list(rule.value) if isinstance(rule.value, tuple) else rule.value
        perdicate = daft.col(rule.column).is_in(rule_value).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def not_contained_in(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        rule_value = list(rule.value) if isinstance(rule.value, tuple) else rule.value
        perdicate = daft.col(rule.column).is_in(rule_value).__ne__(True).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def has_percentile(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        # TODO: Find a way to do this in daft and not pandas
        perdicate = daft.col(rule.column)
        return (
            np.percentile(dataframe.select(perdicate).to_pandas().values, rule.settings["percentile"] * 100)  # type: ignore
            == rule.value  # type: ignore
        )

    def has_max_by(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        predicate_1 = daft.col("id")
        predicate_2 = daft.col("id2").__eq__(daft.col("id2").max())
        return dataframe.where(predicate_2).select(predicate_1).to_pandas().iloc[0, 0] == rule.value

    def has_min_by(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        predicate_1 = daft.col("id")
        predicate_2 = daft.col("id2").__eq__(daft.col("id2").min())
        return dataframe.where(predicate_2).select(predicate_1).to_pandas().iloc[0, 0] == rule.value

    def has_correlation(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        predicate = [daft.col(rule.column[0]), daft.col(rule.column[1])]
        return (
            dataframe.select(*predicate).to_pandas().corr().fillna(0).iloc[0, 1] == rule.value
        )

    def satisfies(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        # TODO: Implement this later
        # Note: Add this moment `daft.DataFrame.where` just accepts Expression not a string
        raise NotImplementedError

    def has_entropy(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        # TODO: Implement this later
        raise NotImplementedError

    def is_on_weekday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().is_in([0, 1, 2, 3, 4]).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_weekend(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().is_in([5, 6]).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_monday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(0).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_tuesday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(1).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_wednesday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(2).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_thursday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(3).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_friday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(4).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_saturday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(5).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_sunday(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = daft.col(rule.column).dt.day_of_week().__eq__(6).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_on_schedule(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        perdicate = ( ( daft.col(rule.column).dt.hour() >= min(rule.value) ).__and__( daft.col(rule.column).dt.hour() <= max(rule.value) ) ).cast(daft.DataType.int64()).sum()
        return dataframe.select(perdicate).to_pandas().iloc[0, 0]

    def is_daily(self, rule: Rule, dataframe: daft.DataFrame) -> complex:
        # TODO: Implement this later
        raise NotImplementedError

    def is_inside_interquartile_range(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, complex]:
        # TODO: Implement this later
        raise NotImplementedError

    def has_workflow(self, rule: Rule, dataframe: daft.DataFrame) -> Union[bool, int]:
        """Compliance with adjacency matrix"""
        # TODO: Implement this later
        raise NotImplementedError



def compute(rules: Dict[str, Rule]):
    """Daft computes directly on the predicates"""
    return True

# TODO: Implement validate_data_types for daft
def validate_data_types(rules: List[Rule], dataframe: daft.DataFrame):
    """Validate the datatype of each column according to the CheckDataType of the rule's method"""
    return True

# TODO: Implement summary engine for daft
def summary(check: Check, dataframe: daft.DataFrame):
    compute = Compute()
    unified_results = {
        rule.key: [operator.methodcaller(rule.method, rule, dataframe)(compute)]
        for rule in check.rules
    }

    def _calculate_violations(result, nrows):
        if isinstance(result, (bool, np.bool_)):
            if result:
                return 0
            else:
                return nrows
        elif isinstance(result, Number):
            if isinstance(result, complex):
                return result.imag
            else:
                return nrows - result

    def _calculate_pass_rate(result, nrows):
        if isinstance(result, (bool, np.bool_)):
            if result:
                return 1.0
            else:
                return 0.0
        elif isinstance(result, Number):
            if isinstance(result, complex):
                if result.imag > 0:
                    if result.imag > nrows:
                        return nrows / result.imag
                    else:
                        return result.imag / nrows
                else:
                    return 1.0

            else:
                return result / nrows

    def _evaluate_status(pass_rate, pass_threshold):
        if pass_rate >= pass_threshold:
            return "PASS"

        return "FAIL"

    rows = len(dataframe)

    computation_basis = [
        {
            "id": index,
            "timestamp": check.date.strftime("%Y-%m-%d %H:%M:%S"),
            "check": check.name,
            "level": check.level.name,
            "column": rule.column,
            "rule": rule.method,
            "value": rule.value,
            "rows": rows,
            "violations": _calculate_violations(first(unified_results[hash_key]), rows),
            "pass_rate": _calculate_pass_rate(first(unified_results[hash_key]), rows),
            "pass_threshold": rule.coverage,
            "status": _evaluate_status(
                _calculate_pass_rate(first(unified_results[hash_key]), rows),
                rule.coverage,
            ),
        }
        for index, (hash_key, rule) in enumerate(check._rule.items(), 1)
    ]
    return daft.from_pylist(computation_basis)