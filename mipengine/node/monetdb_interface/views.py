from typing import List

from mipengine.common.validate_identifier_names import validate_identifier_names
from mipengine.node.monetdb_interface.common_actions import get_table_names
from mipengine.node.monetdb_interface.monet_db_connection import MonetDB


def get_view_names(context_id: str) -> List[str]:
    return get_table_names("view", context_id)


@validate_identifier_names
def create_view(
    view_name: str, table_name: str, columns: List[str], datasets: List[str] = None
):
    # TODO: Add filters argument
    # TODO: With filters dataset_clause will be deleted because it will be a part of the filters
    dataset_clause = ""
    if datasets is not None:
        dataset_names = ",".join(f"'{dataset}'" for dataset in datasets)
        dataset_clause = f"WHERE dataset IN ({dataset_names})"
    columns_clause = ", ".join(columns)

    MonetDB().execute(
        f"""
        CREATE VIEW {view_name}
        AS SELECT {columns_clause}
        FROM {table_name}
        {dataset_clause}"""
    )