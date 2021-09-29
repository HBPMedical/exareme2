import uuid

import pytest

from mipengine.node_tasks_DTOs import ColumnInfo, DBDataType
from mipengine.node_tasks_DTOs import TableData
from mipengine.node_tasks_DTOs import TableSchema
from tests.integration_tests.nodes_communication import get_celery_task_signature
from tests.integration_tests.nodes_communication import get_celery_app

local_node_id = "localnode1"
local_node = get_celery_app(local_node_id)
local_node_create_table = get_celery_task_signature(local_node, "create_table")
local_node_insert_data_to_table = get_celery_task_signature(
    local_node, "insert_data_to_table"
)
local_node_create_pathology_view = get_celery_task_signature(
    local_node, "create_pathology_view"
)
local_node_create_view = get_celery_task_signature(local_node, "create_view")
local_node_get_views = get_celery_task_signature(local_node, "get_views")
local_node_get_view_data = get_celery_task_signature(local_node, "get_table_data")
local_node_get_view_schema = get_celery_task_signature(local_node, "get_table_schema")
local_node_cleanup = get_celery_task_signature(local_node, "clean_up")


@pytest.fixture(autouse=True)
def context_id():
    context_id = "test_views_" + uuid.uuid4().hex

    yield context_id

    local_node_cleanup.delay(context_id=context_id.lower()).get()


def test_view_without_filters(context_id):
    table_schema = TableSchema(
        columns=[
            ColumnInfo(name="col1", data_type=DBDataType.INT),
            ColumnInfo(name="col2", data_type=DBDataType.FLOAT),
            ColumnInfo(name="col3", data_type=DBDataType.TEXT),
        ]
    )

    table_name = local_node_create_table.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        schema_json=table_schema.json(),
    ).get()

    values = [[1, 0.1, "test1"], [2, 0.2, "test2"], [3, 0.3, "test3"]]
    local_node_insert_data_to_table.delay(table_name=table_name, values=values).get()
    columns = ["col1", "col3"]
    view_name = local_node_create_view.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        table_name=table_name,
        columns=columns,
        filters=None,
    ).get()

    views = local_node_get_views.delay(context_id=context_id).get()
    assert view_name in views
    view_intended_schema = TableSchema(
        columns=[
            ColumnInfo(name="col1", data_type=DBDataType.INT),
            ColumnInfo(name="col3", data_type=DBDataType.TEXT),
        ]
    )
    schema_result_json = local_node_get_view_schema.delay(table_name=view_name).get()
    assert view_intended_schema == TableSchema.parse_raw(schema_result_json)

    view_data_json = local_node_get_view_data.delay(table_name=view_name).get()
    view_data = TableData.parse_raw(view_data_json)
    assert all(
        len(columns) == len(view_intended_schema.columns) for columns in view_data.data
    )
    assert view_data.table_schema == view_intended_schema


def test_view_with_filters(context_id):
    table_schema = TableSchema(
        columns=[
            ColumnInfo(name="col1", data_type=DBDataType.INT),
            ColumnInfo(name="col2", data_type=DBDataType.FLOAT),
            ColumnInfo(name="col3", data_type=DBDataType.TEXT),
        ]
    )

    table_name = local_node_create_table.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        schema_json=table_schema.json(),
    ).get()

    values = [[1, 0.1, "test1"], [2, 0.2, None], [3, 0.3, "test3"]]
    local_node_insert_data_to_table.delay(table_name=table_name, values=values).get()
    columns = ["col1", "col3"]
    rules = {
        "condition": "AND",
        "rules": [
            {
                "condition": "OR",
                "rules": [
                    {
                        "id": "col1",
                        "field": "col1",
                        "type": "int",
                        "input": "number",
                        "operator": "equal",
                        "value": 3,
                    }
                ],
            }
        ],
        "valid": True,
    }
    view_name = local_node_create_view.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        table_name=table_name,
        columns=columns,
        filters=rules,
    ).get()

    views = local_node_get_views.delay(context_id=context_id).get()
    assert view_name in views
    view_intended_schema = TableSchema(
        columns=[
            ColumnInfo(name="col1", data_type=DBDataType.INT),
            ColumnInfo(name="col3", data_type=DBDataType.TEXT),
        ]
    )
    schema_result_json = local_node_get_view_schema.delay(table_name=view_name).get()
    assert view_intended_schema == TableSchema.parse_raw(schema_result_json)

    view_data_json = local_node_get_view_data.delay(table_name=view_name).get()
    view_data = TableData.parse_raw(view_data_json)
    assert len(view_data.data) == 1
    assert all(
        len(columns) == len(view_intended_schema.columns) for columns in view_data.data
    )
    assert view_data.table_schema == view_intended_schema


def test_pathology_view_without_filters(context_id):
    columns = [
        "dataset",
        "age_value",
        "gcs_motor_response_scale",
        "pupil_reactivity_right_eye_result",
    ]
    pathology = "tbi"
    view_name = local_node_create_pathology_view.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        pathology=pathology,
        columns=columns,
        filters=None,
    ).get()
    views = local_node_get_views.delay(context_id=context_id).get()
    assert view_name in views

    schema = TableSchema(
        columns=[
            ColumnInfo(name="row_id", data_type=DBDataType.INT),
            ColumnInfo(name="dataset", data_type=DBDataType.TEXT),
            ColumnInfo(name="age_value", data_type=DBDataType.INT),
            ColumnInfo(name="gcs_motor_response_scale", data_type=DBDataType.TEXT),
            ColumnInfo(
                name="pupil_reactivity_right_eye_result", data_type=DBDataType.TEXT
            ),
        ]
    )
    schema_result_json = local_node_get_view_schema.delay(table_name=view_name).get()
    assert schema == TableSchema.parse_raw(schema_result_json)

    view_data_json = local_node_get_view_data.delay(table_name=view_name).get()
    view_data = TableData.parse_raw(view_data_json)
    assert all(len(columns) == len(schema.columns) for columns in view_data.data)
    assert view_data.table_schema == schema

    view_schema_json = local_node_get_view_schema.delay(table_name=view_name).get()
    view_schema = TableSchema.parse_raw(view_schema_json)
    assert view_schema == schema


def test_pathology_view_with_filters(context_id):
    columns = [
        "dataset",
        "age_value",
        "gcs_motor_response_scale",
        "pupil_reactivity_right_eye_result",
    ]
    pathology = "tbi"
    rules = {
        "condition": "AND",
        "rules": [
            {
                "condition": "OR",
                "rules": [
                    {
                        "id": "age_value",
                        "field": "age_value",
                        "type": "int",
                        "input": "number",
                        "operator": "greater",
                        "value": 30,
                    }
                ],
            }
        ],
        "valid": True,
    }
    view_name = local_node_create_pathology_view.delay(
        context_id=context_id,
        command_id=uuid.uuid4().hex,
        pathology=pathology,
        columns=columns,
        filters=rules,
    ).get()
    views = local_node_get_views.delay(context_id=context_id).get()
    assert view_name in views

    schema = TableSchema(
        columns=[
            ColumnInfo(name="row_id", data_type=DBDataType.INT),
            ColumnInfo(name="dataset", data_type=DBDataType.TEXT),
            ColumnInfo(name="age_value", data_type=DBDataType.INT),
            ColumnInfo(name="gcs_motor_response_scale", data_type=DBDataType.TEXT),
            ColumnInfo(
                name="pupil_reactivity_right_eye_result", data_type=DBDataType.TEXT
            ),
        ]
    )
    schema_result_json = local_node_get_view_schema.delay(table_name=view_name).get()
    assert schema == TableSchema.parse_raw(schema_result_json)

    view_data_json = local_node_get_view_data.delay(table_name=view_name).get()
    view_data = TableData.parse_raw(view_data_json)
    assert all(len(columns) == len(schema.columns) for columns in view_data.data)
    assert view_data.table_schema == schema

    view_schema_json = local_node_get_view_schema.delay(table_name=view_name).get()
    view_schema = TableSchema.parse_raw(view_schema_json)
    assert view_schema == schema
