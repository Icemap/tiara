from typing import Any, Optional
from pytidb.schema import TableModel, Field
from pytidb.embeddings import EmbeddingFunction

from backend import config

text_embedding_function = EmbeddingFunction(
    config.EMBEDDING_MODEL,
    timeout=60
)

ISSUE_TABLE_NAME = "issues"
class Issue(TableModel, table=True):
    __tablename__ = ISSUE_TABLE_NAME
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    description_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="description",
    )