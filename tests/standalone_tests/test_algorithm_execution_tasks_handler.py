import random

import pytest

from mipengine import DType
from mipengine.node_tasks_DTOs import ColumnInfo
from mipengine.node_tasks_DTOs import TableSchema

COMMON_TASKS_REQUEST_ID = "rqst1"


@pytest.fixture
def test_table_params():
    command_id = "cmndid1"
    schema = TableSchema(
        columns=[
            ColumnInfo(name="var1", dtype=DType.INT),
            ColumnInfo(name="var2", dtype=DType.STR),
        ]
    )
    return {"command_id": command_id, "schema": schema}


def test_create_table(
    localnode1_tasks_handler, use_localnode1_database, test_table_params
):

    context_id = get_a_random_context_id()
    command_id = test_table_params["command_id"]
    schema = test_table_params["schema"]

    table_name = localnode1_tasks_handler.create_table(
        request_id=COMMON_TASKS_REQUEST_ID,
        context_id=context_id,
        command_id=command_id,
        schema=schema,
    )

    table_name_parts = table_name.split("_")
    assert table_name_parts[0] == "normal"
    assert table_name_parts[2] == context_id
    assert table_name_parts[3] == command_id


def test_get_tables(
    localnode1_tasks_handler, use_localnode1_database, test_table_params
):

    context_id = get_a_random_context_id()
    command_id = test_table_params["command_id"]
    schema = test_table_params["schema"]
    table_name = localnode1_tasks_handler.create_table(
        request_id=COMMON_TASKS_REQUEST_ID,
        context_id=context_id,
        command_id=command_id,
        schema=schema,
    )
    tables = localnode1_tasks_handler.get_tables(
        request_id=COMMON_TASKS_REQUEST_ID, context_id=context_id
    )

    assert table_name in tables


def test_get_table_schema(
    localnode1_tasks_handler, use_localnode1_database, test_table_params
):

    context_id = get_a_random_context_id()
    command_id = test_table_params["command_id"]
    schema = test_table_params["schema"]
    table_name = localnode1_tasks_handler.create_table(
        request_id=COMMON_TASKS_REQUEST_ID,
        context_id=context_id,
        command_id=command_id,
        schema=schema,
    )
    schema_result = localnode1_tasks_handler.get_table_schema(
        request_id=COMMON_TASKS_REQUEST_ID, table_name=table_name
    )

    assert schema_result == schema


def get_a_random_context_id() -> str:
    return str(random.randint(1, 99999))