import json
from typing import List

from celery import shared_task

from mipengine.node.monetdb_interface import views
from mipengine.node.monetdb_interface.common import config
from mipengine.node.monetdb_interface.common import tables_naming_convention
from mipengine.node.tasks.data_classes import ColumnInfo
from mipengine.node.tasks.data_classes import TableData


@shared_task
def get_views(context_id: str) -> List[str]:
    return json.dumps(views.get_views_names(context_id))


@shared_task
def get_view_schema(view_name: str) -> List[ColumnInfo]:
    schema = views.get_view_schema(view_name)
    return ColumnInfo.schema().dumps(schema, many=True)


@shared_task
def get_view_data(view_name: str) -> TableData:
    schema = views.get_view_schema(view_name)
    data = views.get_view_data(view_name)
    return TableData(schema, data).to_json()


@shared_task
def create_view(context_Id: str, columns: str, datasets: str) -> str:
    view_name = tables_naming_convention("view", context_Id, config["node"]["identifier"])
    views.create_view(view_name, json.loads(columns), json.loads(datasets))
    return view_name.lower()


@shared_task
def clean_up(context_Id: str = None):
    views.clean_up_views(context_Id)
    return 0
