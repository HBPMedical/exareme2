from celery import shared_task

from mipengine.node.monetdb_interface.common_actions import get_table_data
from mipengine.node.node_logger import initialise_logger


@shared_task
@initialise_logger
def validate_smpc_templates_match(
    context_id: str,
    table_name: str,
):
    """
    On a table with multiple SMPC DTO templates, coming from the local nodes,
    it validates that they are all the same without differences.

    Parameters
    ----------
    context_id: An identifier of the action.
    table_name: The table where the templates are located in.

    Returns
    -------
    Nothing, only throws exception if they don't match.
    """

    template_column = get_table_data(table_name)[0].data
    first_template, *_ = template_column
    for template in template_column[1:]:
        if template != first_template:
            raise ValueError(
                f"SMPC templates dont match. \n {first_template} \n != \n {template}"
            )
