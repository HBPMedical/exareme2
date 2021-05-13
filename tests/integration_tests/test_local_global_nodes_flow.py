import uuid

import pytest

from mipengine.common.node_catalog import node_catalog
from mipengine.common.node_tasks_DTOs import ColumnInfo, TableData
from mipengine.common.node_tasks_DTOs import TableInfo
from mipengine.common.node_tasks_DTOs import TableSchema
from tests.integration_tests import nodes_communication

local_node_1_id = "localnode1"
local_node_2_id = "localnode2"
global_node_id = "globalnode"
local_node_1 = nodes_communication.get_celery_app(local_node_1_id)
local_node_2 = nodes_communication.get_celery_app(local_node_2_id)
global_node = nodes_communication.get_celery_app(global_node_id)

local_node_1_create_table = nodes_communication.get_celery_create_table_signature(
    local_node_1
)
local_node_2_create_table = nodes_communication.get_celery_create_table_signature(
    local_node_2
)
local_node_1_insert_data_to_table = (
    nodes_communication.get_celery_insert_data_to_table_signature(local_node_1)
)
local_node_2_insert_data_to_table = (
    nodes_communication.get_celery_insert_data_to_table_signature(local_node_2)
)
global_node_create_remote_table = (
    nodes_communication.get_celery_create_remote_table_signature(global_node)
)
global_node_get_remote_tables = (
    nodes_communication.get_celery_get_remote_tables_signature(global_node)
)
global_node_create_merge_table = (
    nodes_communication.get_celery_create_merge_table_signature(global_node)
)
global_node_get_merge_tables = (
    nodes_communication.get_celery_get_merge_tables_signature(global_node)
)
global_node_get_merge_table_data = (
    nodes_communication.get_celery_get_table_data_signature(global_node)
)

clean_up_node1 = nodes_communication.get_celery_cleanup_signature(local_node_1)
clean_up_node2 = nodes_communication.get_celery_cleanup_signature(local_node_2)
clean_up_global = nodes_communication.get_celery_cleanup_signature(global_node)


@pytest.fixture(autouse=True)
def context_id():
    context_id = "test_flow_" + str(uuid.uuid4()).replace("-", "")

    yield context_id

    clean_up_node1.delay(context_id=context_id.lower()).get()
    clean_up_node2.delay(context_id=context_id.lower()).get()
    clean_up_global.delay(context_id=context_id.lower()).get()


def test_create_merge_table_with_remote_tables(context_id):
    local_node_1_data = node_catalog.get_local_node(local_node_1_id)
    local_node_2_data = node_catalog.get_local_node(local_node_2_id)

    schema = TableSchema(
        [
            ColumnInfo("col1", "int"),
            ColumnInfo("col2", "real"),
            ColumnInfo("col3", "text"),
        ]
    )

    # Create local tables
    local_node_1_table_name = local_node_1_create_table.delay(
        context_id=context_id,
        command_id=str(uuid.uuid1()).replace("-", ""),
        schema_json=schema.to_json(),
    ).get()
    local_node_2_table_name = local_node_2_create_table.delay(
        context_id=context_id,
        command_id=str(uuid.uuid1()).replace("-", ""),
        schema_json=schema.to_json(),
    ).get()
    # Insert data into local tables
    values = [[1, 0.1, "test1"], [2, 0.2, "test2"], [3, 0.3, "test3"]]
    local_node_1_insert_data_to_table.delay(
        table_name=local_node_1_table_name, values=values
    ).get()
    local_node_2_insert_data_to_table.delay(
        table_name=local_node_2_table_name, values=values
    ).get()

    # Create remote tables
    table_info_local_1 = TableInfo(local_node_1_table_name, schema)
    table_info_local_2 = TableInfo(local_node_2_table_name, schema)

    monetdb_socket_address_local_node_1 = (
        f"{local_node_1_data.monetdbHostname}:{local_node_1_data.monetdbPort}"
    )
    monetdb_socket_address_local_node_2 = (
        f"{local_node_2_data.monetdbHostname}:{local_node_2_data.monetdbPort}"
    )
    global_node_create_remote_table.delay(
        table_info_json=table_info_local_1.to_json(),
        monetdb_socket_address=monetdb_socket_address_local_node_1,
    ).get()
    global_node_create_remote_table.delay(
        table_info_json=table_info_local_2.to_json(),
        monetdb_socket_address=monetdb_socket_address_local_node_2,
    ).get()
    remote_tables = global_node_get_remote_tables.delay(context_id=context_id).get()
    assert local_node_1_table_name in remote_tables
    assert local_node_2_table_name in remote_tables

    # Create merge table
    merge_table_name = global_node_create_merge_table.delay(
        context_id=context_id,
        command_id=str(uuid.uuid1()).replace("-", ""),
        table_names=remote_tables,
    ).get()

    # Validate merge table exists
    merge_tables = global_node_get_merge_tables.delay(context_id=context_id).get()
    assert merge_table_name in merge_tables

    # Validate merge table row count
    table_data_json = global_node_get_merge_table_data.delay(
        table_name=merge_table_name
    ).get()
    table_data = TableData.from_json(table_data_json)
    row_count = len(table_data.data)
    assert row_count == 6
