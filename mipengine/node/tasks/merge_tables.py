from typing import List

from celery import shared_task

from mipengine.node import config as node_config
from mipengine.node.monetdb_interface import common_actions
from mipengine.node.monetdb_interface import merge_tables
from mipengine.node.monetdb_interface.common_actions import create_table_name
from mipengine.node.monetdb_interface.merge_tables import validate_tables_can_be_merged
from mipengine.node.logging import log_method_call
from mipengine.node_tasks_DTOs import TableType


@shared_task
@log_method_call
def get_merge_tables(context_id: str) -> List[str]:
    """
    Parameters
    ----------
    context_id : str
        The id of the experiment

    Returns
    ------
    List[str]
        A list of merge table names
    """
    return merge_tables.get_merge_tables_names(context_id)


@shared_task
@log_method_call
def create_merge_table(context_id: str, command_id: str, table_names: List[str]) -> str:
    """
    Parameters
    ----------
    context_id : str
        The id of the experiment
    command_id : str
        The id of the command that the merge table
    table_names: List[str]
        Its a list of names of the tables to be merged

    Returns
    ------
    str
        The name(string) of the created merge table in lower case.
    """
    validate_tables_can_be_merged(table_names)
    schema = common_actions.get_table_schema(table_names[0])
    merge_table_name = create_table_name(
        TableType.MERGE, command_id, context_id, node_config.identifier
    )
    merge_tables.create_merge_table(merge_table_name, schema)
    merge_tables.add_to_merge_table(merge_table_name, table_names)

    return merge_table_name
