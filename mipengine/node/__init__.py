import os
import envtoml
from importlib.resources import open_text
from mipengine import node
from mipengine import AttrDict
from celery import signals

@signals.setup_logging.connect
def setup_celery_logging( ** kwargs):
   pass

DATA_TABLE_PRIMARY_KEY = "row_id"

if config_file := os.getenv("MIPENGINE_NODE_CONFIG_FILE"):
    with open(config_file) as fp:
        config = AttrDict(envtoml.load(fp))
else:
    with open_text(node, "config.toml") as fp:
        config = AttrDict(envtoml.load(fp))
