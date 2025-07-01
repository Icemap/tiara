from pytidb import TiDBClient

from backend import config
from backend.model.issue import ISSUE_TABLE_NAME, Issue
from backend.tool.logger import get_logger

logger = get_logger(__name__)

db = TiDBClient.connect(
    host=config.SERVERLESS_CLUSTER_HOST,
    port=config.SERVERLESS_CLUSTER_PORT,
    username=config.SERVERLESS_CLUSTER_USERNAME,
    password=config.SERVERLESS_CLUSTER_PASSWORD,
    database=config.SERVERLESS_CLUSTER_DATABASE_NAME,
    enable_ssl=True,
)

table_models = [
    (ISSUE_TABLE_NAME, Issue),
]

def init_tables():
    for table_name, table_model in table_models:
        if not db.has_table(table_name):
            table = db.create_table(schema=table_model)
            if table:
                logger.info(f"Table {table_name} created")
