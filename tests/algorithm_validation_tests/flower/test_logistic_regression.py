def test_logistic_regression(get_algorithm_result):
    input = {
        "inputdata": {
            "y": ["gender"],
            "x": ["lefthippocampus"],
            "data_model": "dementia:0.1",
            "datasets": [
                "ppmi0",
                "ppmi1",
                "ppmi2",
                "ppmi3",
                "ppmi5",
                "ppmi6",
                "edsd6",
                "ppmi7",
                "ppmi8",
                "ppmi9",
            ],
            "filters": None,
        },
        "parameters": None,
        "test_case_num": 99,
    }
    input["type"] = "flower"
    algorithm_result = get_algorithm_result("logistic_regression", input)
    assert algorithm_result == {"accuracy": 0.6180758017492711} or algorithm_result == {
        "accuracy": 0.3819241982507289
    }


def test_logistic_regression_with_filters(get_algorithm_result):
    input = {
        "inputdata": {
            "y": ["gender"],
            "x": ["lefthippocampus"],
            "data_model": "dementia:0.1",
            "datasets": [
                "ppmi0",
                "ppmi1",
                "ppmi2",
                "ppmi3",
                "ppmi4",
                "ppmi5",
                "ppmi6",
                "ppmi7",
                "ppmi8",
                "ppmi9",
            ],
            "filters": {
                "condition": "AND",
                "rules": [
                    {
                        "id": "lefthippocampus",
                        "field": "lefthippocampus",
                        "type": "double",
                        "input": "number",
                        "operator": "greater",
                        "value": 3.2,
                    }
                ],
                "valid": True,
            },
        },
        "parameters": None,
        "test_case_num": 99,
    }
    input["type"] = "flower"
    algorithm_result = get_algorithm_result("logistic_regression", input)
    assert algorithm_result == {"accuracy": 0.7755681818181818} or algorithm_result == {
        "accuracy": 0.22443181818181818
    }
