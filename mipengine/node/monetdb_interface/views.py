from typing import List

from mipengine.exceptions import InsufficientDataError
from mipengine.filters import build_filter_clause
from mipengine.node import config as node_config
from mipengine.node.monetdb_interface.common_actions import get_table_names
from mipengine.node.monetdb_interface.common_actions import get_table_schema
from mipengine.node.monetdb_interface.guard import is_list_of_identifiers
from mipengine.node.monetdb_interface.guard import is_primary_data_table
from mipengine.node.monetdb_interface.guard import is_valid_filter
from mipengine.node.monetdb_interface.guard import sql_injection_guard
from mipengine.node.monetdb_interface.monet_db_facade import db_execute
from mipengine.node.monetdb_interface.monet_db_facade import db_execute_and_fetchall
from mipengine.node_tasks_DTOs import ColumnInfo
from mipengine.node_tasks_DTOs import TableInfo
from mipengine.node_tasks_DTOs import TableSchema
from mipengine.node_tasks_DTOs import TableType

MINIMUM_ROW_COUNT = node_config.privacy.minimum_row_count


def get_view_names(context_id: str) -> List[str]:
    return get_table_names(TableType.VIEW, context_id)


@sql_injection_guard(
    view_name=str.isidentifier,
    table_name=is_primary_data_table,
    columns=is_list_of_identifiers,
    filters=is_valid_filter,
    check_min_rows=None,
)
def create_view(
    view_name: str,
    table_name: str,
    columns: List[str],
    filters: dict,
    check_min_rows=False,
) -> TableInfo:
    filter_clause = ""
    if filters:
        filter_clause = f"WHERE {build_filter_clause(filters)}"
    columns_clause = ", ".join([f'"{column}"' for column in columns])

    view_creation_query = f"""
        CREATE VIEW {view_name}
        AS SELECT {columns_clause}
        FROM {table_name}
        {filter_clause}
        """

    db_execute(view_creation_query)

    if check_min_rows:
        view_rows_query_result = db_execute_and_fetchall(
            f"""
            SELECT COUNT(*)
            FROM {view_name}
            """
        )
        view_rows_result_row = view_rows_query_result[0]
        view_rows_count = view_rows_result_row[0]

        if view_rows_count < MINIMUM_ROW_COUNT:
            db_execute(f"""DROP VIEW {view_name}""")
            raise InsufficientDataError(
                f"The following view has less rows than the PRIVACY_THRESHOLD({MINIMUM_ROW_COUNT}):  {view_creation_query}"
            )

    view_schema = get_table_schema(view_name)
    ordered_view_schema = _get_ordered_table_schema(view_schema, columns)

    return TableInfo(
        name=view_name,
        schema_=ordered_view_schema,
        type_=TableType.VIEW,
    )


def _get_ordered_table_schema(
    table_schema: TableSchema, ordered_columns: List[str]
) -> TableSchema:
    ordered_column_infos = [
        _get_column_info_from_schema(table_schema, column_name)
        for column_name in ordered_columns
    ]
    return TableSchema(columns=ordered_column_infos)


def _get_column_info_from_schema(
    table_schema: TableSchema, column_name: str
) -> ColumnInfo:
    for column in table_schema.columns:
        if column.name == column_name:
            return column
    else:
        raise ValueError(f"{column_name=} does not exist in {table_schema=}.")
