from typing import List, Union, Any

from mipengine.node_tasks_DTOs import ImmutableBaseModel
from mipengine.node_tasks_DTOs import UDFArgumentKind

from mipengine.table_data_DTOs import ColumnDataFloat
from mipengine.table_data_DTOs import ColumnDataInt
from mipengine.table_data_DTOs import ColumnDataStr


class TabularDataResult(ImmutableBaseModel):
    title: str
    columns: List[Union[ColumnDataInt, ColumnDataStr, ColumnDataFloat]]
