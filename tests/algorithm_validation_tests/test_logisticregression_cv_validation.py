import json
from pathlib import Path

import pytest
import scipy.stats as st

from tests.algorithm_validation_tests.helpers import algorithm_request
from tests.algorithm_validation_tests.helpers import get_test_params

expected_file = (
    Path(__file__).parent / "expected" / "logisticregression_cv_expected.json"
)


@pytest.mark.parametrize(
    "test_input, expected",
    get_test_params(
        expected_file,
        skip_indices=[5, 6, 9, 12, 18, 19, 22, 17],
        skip_reason="Tests 5, 9, 12, 18, 19, 22 results in empty tables, "
        "https://team-1617704806227.atlassian.net/browse/MIP-634.\n"
        "Test 17 fails to converge in CI, "
        "https://team-1617704806227.atlassian.net/browse/MIP-680.",
    ),
)
def test_logisticregression_cv_algorithm(test_input, expected, subtests):
    response = algorithm_request("logistic_regression_cv", test_input)
    try:
        result = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        raise ValueError(f"The result is not valid json:\n{response.text}") from None

    # summary results also contain their average and stdev in the last
    # positions, so I remove them
    summary = result["summary"]
    accuracy_res = summary["accuracy"][:-2]
    accuracy_exp = expected["accuracy"]
    recall_res = summary["recall"][:-2]
    recall_exp = expected["recall"]
    precision_res = summary["precision"][:-2]
    precision_exp = expected["precision"]
    fscore_res = summary["fscore"][:-2]
    fscore_exp = expected["fscore"]
    auc_res = [rc["auc"] for rc in result["roc_curves"]]
    auc_exp = expected["auc"]

    with subtests.test():
        # ttest results in NaNs when everything is 0, see answer below
        # https://stats.stackexchange.com/questions/111423/what-is-the-p-value-for-paired-t-test-if-the-two-set-of-data-are-identical
        # This happens when our model and sklearn's both predict zero
        # positives or zero negatives. This is a degenerate case, but happens
        # in random tests where the choice of variables doesn't always make
        # sense.
        if all(r == e for r, e in zip(accuracy_res, accuracy_exp)):
            pass
        else:
            ttest = st.ttest_ind(a=accuracy_res, b=accuracy_exp)
            assert ttest.pvalue >= 0.05
    with subtests.test():
        if all(r == e for r, e in zip(recall_res, recall_exp)):
            pass
        else:
            ttest = st.ttest_ind(a=recall_res, b=recall_exp)
            assert ttest.pvalue >= 0.05
    with subtests.test():
        if all(r == e for r, e in zip(precision_res, precision_exp)):
            pass
        else:
            ttest = st.ttest_ind(a=precision_res, b=precision_exp)
            assert ttest.pvalue >= 0.05
    with subtests.test():
        if all(r == e for r, e in zip(fscore_res, fscore_exp)):
            pass
        else:
            ttest = st.ttest_ind(a=fscore_res, b=fscore_exp)
            assert ttest.pvalue >= 0.05
    with subtests.test():
        if all(r == e for r, e in zip(auc_res, auc_exp)):
            pass
        else:
            ttest = st.ttest_ind(a=auc_res, b=auc_exp)
            assert ttest.pvalue >= 0.05