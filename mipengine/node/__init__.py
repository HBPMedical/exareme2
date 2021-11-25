import logging
import os
from importlib.resources import open_text

import envtoml
from celery import signals
from celery.signals import after_setup_task_logger, setup_logging
from celery.app.log import TaskFormatter
from celery.utils.log import get_task_logger

from mipengine import AttrDict
from mipengine import node

DATA_TABLE_PRIMARY_KEY = "row_id"


if config_file := os.getenv("MIPENGINE_NODE_CONFIG_FILE"):
    with open(config_file) as fp:
        config = AttrDict(envtoml.load(fp))
else:
    with open_text(node, "config.toml") as fp:
        config = AttrDict(envtoml.load(fp))
