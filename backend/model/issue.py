from typing import Any, Optional
from datetime import datetime
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
    
    # GitHub Issue basic info
    id: int | None = Field(default=None, primary_key=True)
    github_issue_id: int = Field(index=True)  # GitHub's issue ID
    github_issue_number: int = Field(index=True)  # Issue number in the repository
    
    # Repository info
    repository_name: str = Field(index=True)  # e.g., "Icemap/test-tiara"
    repository_id: int
    
    # Issue content
    title: str
    body: Optional[str] = None  # Issue description/body
    
    # Issue status and metadata
    state: str = Field(index=True)  # open, closed
    locked: bool = Field(default=False)
    
    # Author info (minimal)
    author_login: str = Field(index=True)
    author_id: int
    
    # Assignee info (minimal)
    assignee_login: Optional[str] = None
    assignee_id: Optional[int] = None
    
    # Labels (as JSON string for simplicity)
    labels: Optional[str] = None  # JSON string of label names
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    # GitHub URLs
    html_url: str
    api_url: str
    
    # Comments count
    comments_count: int = Field(default=0)
    
    # Additional metadata
    milestone_title: Optional[str] = None
    author_association: Optional[str] = None  # OWNER, COLLABORATOR, CONTRIBUTOR, etc.
    state_reason: Optional[str] = None  # completed, not_planned, reopened, etc.
    
    # Vector embedding for issue content (title + body)
    content_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="title",  # We'll combine title and body in the application logic
    )