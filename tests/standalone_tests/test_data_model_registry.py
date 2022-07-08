import pytest

from mipengine.controller.controller_logger import get_request_logger
from mipengine.controller.data_model_registry import DataModelRegistry

# TODO the testing should be better once the datasets are properly distributed and the are no duplicates.
from mipengine.node_tasks_DTOs import CommonDataElement
from mipengine.node_tasks_DTOs import CommonDataElements


def get_datasets_locations():
    return {
        "tbi:0.1": {
            "dummy_tbi0": "localnode1",
            "dummy_tbi1": "localnode2",
            "dummy_tbi3": "localnode2",
        },
        "dementia:0.1": {
            "ppmi0": "localnode1",
            "ppmi1": "localnode2",
            "ppmi3": "localnode2",
            "edsd0": "localnode1",
            "edsd1": "localnode2",
            "edsd3": "localnode2",
            "desd-synthdata0": "localnode1",
            "desd-synthdata1": "localnode2",
            "desd-synthdata3": "localnode2",
        },
    }


def get_data_model_cdes():
    return {
        "dementia:0.1": CommonDataElements(
            values={
                "dataset": CommonDataElement(
                    code="dataset",
                    label="Dataset",
                    sql_type="text",
                    is_categorical=True,
                    enumerations={
                        "ppmi": "PPMI",
                        "edsd": "EDSD",
                        "desd-synthdata": "DESD-synthdata",
                    },
                ),
                "alzheimerbroadcategory": CommonDataElement(
                    code="alzheimerbroadcategory",
                    label="Alzheimer Broad Category",
                    sql_type="text",
                    is_categorical=True,
                    enumerations={
                        "AD": "Alzheimer’s disease",
                        "CN": "Cognitively Normal",
                        "Other": "Other",
                        "MCI": "Mild cognitive impairment",
                    },
                ),
                "minimentalstate": CommonDataElement(
                    code="minimentalstate",
                    label="MMSE Total scores",
                    sql_type="int",
                    is_categorical=False,
                    min=0,
                    max=30,
                ),
            }
        ),
        "tbi:0.1": CommonDataElements(
            values={
                "dataset": CommonDataElement(
                    code="dataset",
                    label="Dataset",
                    sql_type="text",
                    is_categorical=True,
                    enumerations={
                        "dummy_tbi": "Dummy TBI",
                    },
                ),
                "gender_type": CommonDataElement(
                    code="gender_type",
                    label="Gender",
                    sql_type="text",
                    is_categorical=True,
                    enumerations={
                        "M": "Male",
                        "F": "Female",
                    },
                ),
            }
        ),
    }


@pytest.fixture
def mocked_data_model_registry():
    data_model_registry = DataModelRegistry(
        data_models=get_data_model_cdes(), datasets_locations=get_datasets_locations()
    )
    return data_model_registry


def test_get_all_available_datasets_per_data_model(mocked_data_model_registry):
    assert mocked_data_model_registry.get_all_available_datasets_per_data_model()


def test_data_model_exists(mocked_data_model_registry):
    assert mocked_data_model_registry.data_model_exists("tbi:0.1")
    assert not mocked_data_model_registry.data_model_exists("non-existing")


def test_dataset_exists(mocked_data_model_registry):
    assert mocked_data_model_registry.dataset_exists("tbi:0.1", "dummy_tbi0")
    assert not mocked_data_model_registry.dataset_exists("tbi:0.1", "non-existing")


def test_get_nodes_with_any_of_datasets(mocked_data_model_registry):
    assert set(
        mocked_data_model_registry.get_node_ids_with_any_of_datasets(
            "tbi:0.1", ["dummy_tbi0", "dummy_tbi1"]
        )
    ) == {"localnode1", "localnode2"}


def test_get_node_specific_datasets(mocked_data_model_registry):
    assert set(
        mocked_data_model_registry.get_node_specific_datasets(
            "localnode1", "dementia:0.1", ["edsd0", "ppmi0"]
        )
    ) == {"edsd0", "ppmi0"}


def test_empty_initialization():
    dmr = DataModelRegistry()
    assert not dmr.data_models
    assert not dmr.datasets_locations
