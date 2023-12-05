from pathlib import Path

import pytest

from tests.algorithm_validation_tests.helpers import algorithm_request
from tests.algorithm_validation_tests.helpers import get_test_params
from tests.algorithm_validation_tests.helpers import parse_response

algorithm_name = "lr_imaging_mnist"

expected_file = Path(__file__).parent / "expected" / f"{algorithm_name}_expected.json"

# test_input, expected, subtests


@pytest.mark.parametrize(
    "test_input, expected",
    get_test_params(expected_file),
)
def test_lr_imaging_mnist(test_input, expected):
    response = algorithm_request(algorithm_name, test_input)
    result = parse_response(response)

    # this test only ensures that the algorithm runs smoothly without errors
    assert result
