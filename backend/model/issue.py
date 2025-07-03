import json
from typing import Any, Optional
from datetime import datetime
from pytidb.schema import TableModel, Field
from pytidb.embeddings import EmbeddingFunction
from sqlalchemy import JSON, TEXT, Column, BigInteger

from backend import config

text_embedding_function = EmbeddingFunction(
    config.EMBEDDING_MODEL,
    timeout=60
)

ISSUE_TABLE_NAME = "issues"

class Issue(TableModel, table=True):
    """
    Issue model that mirrors GitHub's Issue structure.
    Based on PyGithub's Issue class and GitHub REST API.
    """
    __tablename__ = ISSUE_TABLE_NAME
    
    # GitHub Issue identifiers - using BIGINT for large GitHub IDs
    github_issue_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    github_issue_number: int = Field(index=True)  # Issue number in the repository
    node_id: str  # GitHub's node ID for GraphQL API
    
    # Repository information
    repository_name: str = Field(index=True)  # Repository name (e.g., "owner/repo")
    repository_owner: str = Field(index=True)  # Repository owner
    repository_id: int  # GitHub repository ID
    
    # Issue content
    title: str = Field(sa_column=Column(TEXT, nullable=False))  # Issue title
    body: Optional[str] = Field(sa_column=Column(TEXT, nullable=True))  # Issue body/description (can be None)
    
    # Issue status
    state: str = Field(index=True)  # Issue state (open/closed)
    state_reason: Optional[str] = None  # Reason for state change
    locked: bool = Field(default=False)  # Whether the issue is locked
    active_lock_reason: Optional[str] = None  # Reason for locking
    
    # User information (minimal)
    author_login: str = Field(index=True)  # Issue author GitHub login
    author_id: int  # Issue author GitHub ID
    closed_by_login: Optional[str] = None  # Who closed the issue
    closed_by_id: Optional[int] = None  # ID of who closed the issue
    
    # Assignees and labels (JSON storage)
    assignees: Optional[dict | list] = Field(sa_column=Column(JSON, nullable=False))  # JSON string of assignee data
    labels: Optional[dict | list] = Field(sa_column=Column(JSON, nullable=False))  # JSON string of label data
    
    # Milestone
    milestone_title: Optional[str] = None
    milestone_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    # URLs
    html_url: str  # GitHub issue URL
    url: str  # API URL
    
    # Vector embeddings for content search
    title_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="title",
    )
    body_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="body",
    )
    
    @classmethod
    def from_github_issue(cls, github_issue: Any) -> "Issue":
        """
        Convert a PyGithub Issue object to our Issue model.
        
        Args:
            github_issue: PyGithub Issue object
            
        Returns:
            Issue model instance
        """
        # Parse repository info
        repo = github_issue.repository
        repo_full_name = repo.full_name  # e.g., "owner/repo"
        repo_owner = repo_full_name.split('/')[0]
        
        # Process assignees
        assignees_data = []
        for assignee in github_issue.assignees:
            assignees_data.append({
                'login': assignee.login,
                'id': assignee.id
            })
        
        # Process labels
        labels_data = []
        for label in github_issue.labels:
            labels_data.append({
                'name': label.name,
                'color': label.color,
                'description': label.description
            })
        
        # Process milestone
        milestone = github_issue.milestone
        milestone_title = milestone.title if milestone else None
        milestone_id = milestone.id if milestone else None
        
        # Process closed_by
        closed_by = github_issue.closed_by
        closed_by_login = closed_by.login if closed_by else None
        closed_by_id = closed_by.id if closed_by else None
        
        return cls(
            github_issue_id=github_issue.id,
            github_issue_number=github_issue.number,
            node_id=github_issue.node_id,
            repository_name=repo_full_name,
            repository_owner=repo_owner,
            repository_id=repo.id,
            title=github_issue.title,
            body=github_issue.body if github_issue.body is not None else "N/A",
            state=github_issue.state,
            state_reason=github_issue.state_reason,
            locked=github_issue.locked,
            active_lock_reason=github_issue.active_lock_reason,
            author_login=github_issue.user.login,
            author_id=github_issue.user.id,
            closed_by_login=closed_by_login,
            closed_by_id=closed_by_id,
            assignees=assignees_data,
            labels=labels_data,
            milestone_title=milestone_title,
            milestone_id=milestone_id,
            created_at=github_issue.created_at,
            updated_at=github_issue.updated_at,
            closed_at=github_issue.closed_at,
            html_url=github_issue.html_url,
            url=github_issue.url
        )
    
    @classmethod
    def from_webhook_payload(cls, payload: dict) -> "Issue":
        """
        Convert a GitHub webhook payload to our Issue model.
        
        Args:
            payload: GitHub webhook payload dictionary
            
        Returns:
            Issue model instance
        """
        issue_data = payload.get('issue', {})
        repo_data = payload.get('repository', {})
        
        # Repository information
        repo_full_name = repo_data.get('full_name', '')
        repo_owner = repo_data.get('owner', {}).get('login', '')
        repo_id = repo_data.get('id', 0)
        
        # Process assignees
        assignees_data = []
        for assignee in issue_data.get('assignees', []):
            assignees_data.append({
                'login': assignee.get('login'),
                'id': assignee.get('id')
            })
        
        # Process labels
        labels_data = []
        for label in issue_data.get('labels', []):
            labels_data.append({
                'name': label.get('name'),
                'color': label.get('color'),
                'description': label.get('description')
            })
        
        # Process milestone
        milestone = issue_data.get('milestone')
        milestone_title = milestone.get('title') if milestone else None
        milestone_id = milestone.get('id') if milestone else None
        
        # Process closed_by
        closed_by = issue_data.get('closed_by')
        closed_by_login = closed_by.get('login') if closed_by else None
        closed_by_id = closed_by.get('id') if closed_by else None
        
        # Parse timestamps
        def parse_datetime(dt_str):
            if dt_str:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return None
        
        return cls(
            github_issue_id=issue_data.get('id'),
            github_issue_number=issue_data.get('number'),
            node_id=issue_data.get('node_id'),
            repository_name=repo_full_name,
            repository_owner=repo_owner,
            repository_id=repo_id,
            title=issue_data.get('title'),
            body=issue_data.get('body') if issue_data.get('body') is not None else "N/A",
            state=issue_data.get('state'),
            state_reason=issue_data.get('state_reason'),
            locked=issue_data.get('locked', False),
            active_lock_reason=issue_data.get('active_lock_reason'),
            author_login=issue_data.get('user', {}).get('login'),
            author_id=issue_data.get('user', {}).get('id'),
            closed_by_login=closed_by_login,
            closed_by_id=closed_by_id,
            assignees=assignees_data,
            labels=labels_data,
            milestone_title=milestone_title,
            milestone_id=milestone_id,
            created_at=parse_datetime(issue_data.get('created_at')),
            updated_at=parse_datetime(issue_data.get('updated_at')),
            closed_at=parse_datetime(issue_data.get('closed_at')),
            html_url=issue_data.get('html_url'),
            url=issue_data.get('url')
        )
    
    def get_content_for_embedding(self) -> str:
        """
        Get combined content (title + body) for vector embedding.
        """
        content_parts = [self.title]
        if self.body:
            content_parts.append(self.body)
        return " ".join(content_parts)
    
    def get_labels_list(self) -> list[dict]:
        """
        Parse labels JSON and return as list of dictionaries.
        """
        if not self.labels:
            return []
        try:
            return json.loads(self.labels)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_assignees_list(self) -> list[dict]:
        """
        Parse assignees JSON and return as list of dictionaries.
        """
        if not self.assignees:
            return []
        try:
            return json.loads(self.assignees)
        except (json.JSONDecodeError, TypeError):
            return []