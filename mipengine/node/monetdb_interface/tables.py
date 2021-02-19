from typing import List
from typing import Union

from mipengine.node.monetdb_interface import common
from mipengine.node.monetdb_interface.common import connection
from mipengine.node.monetdb_interface.common import convert_schema_to_sql_query_format
from mipengine.node.monetdb_interface.common import cursor
from mipengine.node.tasks.data_classes import ColumnInfo
from mipengine.node.tasks.data_classes import TableInfo


def get_table_schema(table_name: str) -> List[ColumnInfo]:
    return common.get_table_schema('normal', table_name)


def get_tables_names(context_id: str) -> List[str]:
    return common.get_tables_names("normal", context_id)


def get_table_data(context_id: str) -> List[List[Union[str, int, float, bool]]]:
    return common.get_table_data("normal", context_id)


def create_table(table_info: TableInfo) -> str:
    columns_schema = convert_schema_to_sql_query_format(table_info.schema)
    cursor.execute(f"CREATE TABLE {table_info.name} ( {columns_schema} )")
    connection.commit()
