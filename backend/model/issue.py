import json
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
    """
    Issue model that mirrors GitHub's Issue structure.
    Based on PyGithub's Issue class and GitHub REST API.
    """
    __tablename__ = ISSUE_TABLE_NAME
    
    # GitHub Issue identifiers
    github_issue_id: int = Field(primary_key=True)  # GitHub's unique issue ID
    github_issue_number: int = Field(index=True)  # Issue number in the repository
    node_id: str  # GitHub's GraphQL node ID
    
    # Repository information
    repository_name: str = Field(index=True)  # e.g., "Icemap/test-tiara"
    repository_id: int
    repository_url: str  # GitHub API URL for the repository
    
    # Issue content
    title: str = Field(index=True)
    body: Optional[str] = None  # Issue description/body
    body_html: Optional[str] = None  # HTML formatted body
    body_text: Optional[str] = None  # Plain text body
    
    # Issue status and state
    state: str = Field(index=True)  # "open", "closed"
    state_reason: Optional[str] = None  # "completed", "not_planned", "reopened", etc.
    locked: bool = Field(default=False)
    active_lock_reason: Optional[str] = None  # "off-topic", "too heated", "resolved", "spam"
    
    # Author information
    author_login: str = Field(index=True)
    author_id: int
    author_association: str  # "OWNER", "COLLABORATOR", "CONTRIBUTOR", "FIRST_TIME_CONTRIBUTOR", etc.
    
    # Assignee information (primary assignee - for backward compatibility)
    assignee_login: Optional[str] = None
    assignee_id: Optional[int] = None
    
    # Multiple assignees (stored as JSON)
    assignees: Optional[str] = None  # JSON array of assignee objects [{login, id}, ...]
    
    # Labels (stored as JSON)
    labels: Optional[str] = None  # JSON array of label objects [{name, color, description}, ...]
    
    # Milestone information
    milestone_title: Optional[str] = None
    milestone_id: Optional[int] = None
    milestone_number: Optional[int] = None
    milestone_state: Optional[str] = None  # "open", "closed"
    
    # Timestamps
    created_at: datetime = Field(index=True)
    updated_at: datetime = Field(index=True)
    closed_at: Optional[datetime] = None
    
    # User who closed the issue
    closed_by_login: Optional[str] = None
    closed_by_id: Optional[int] = None
    
    # URLs
    html_url: str  # Public GitHub URL
    url: str  # GitHub API URL
    
    # Interaction counts
    comments_count: int = Field(default=0)
    
    # Draft status (for pull requests)
    draft: Optional[bool] = None
    
    # Search relevance score (when retrieved from search)
    score: Optional[float] = None
    
    # Vector embedding for issue content (title + body)
    title_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="title",
    )
    body_vec: Optional[Any] = text_embedding_function.VectorField(
        source_field="body",
    )
    
    @classmethod
    def from_github_issue(cls, github_issue, repository_name: str = None):
        """
        Convert a PyGithub Issue object to our Issue model.
        
        Args:
            github_issue: PyGithub Issue object
            repository_name: Repository name (e.g., "owner/repo"), if not available from issue
            
        Returns:
            Issue: Our Issue model instance
        """
        # Extract repository info
        if hasattr(github_issue, 'repository') and github_issue.repository:
            repo_name = github_issue.repository.full_name
            repo_id = github_issue.repository.id
            repo_url = github_issue.repository.url
        else:
            repo_name = repository_name or "unknown/unknown"
            # Extract repo info from URL if possible
            if hasattr(github_issue, 'repository_url'):
                repo_url = github_issue.repository_url
                # Try to extract repo ID from URL (this might not always work)
                repo_id = 0  # Default fallback
            else:
                repo_url = ""
                repo_id = 0
        
        # Handle assignees
        assignees_json = None
        assignee_login = None
        assignee_id = None
        
        if hasattr(github_issue, 'assignees') and github_issue.assignees:
            assignees_data = []
            for assignee in github_issue.assignees:
                assignees_data.append({
                    "login": assignee.login,
                    "id": assignee.id,
                    "avatar_url": assignee.avatar_url if hasattr(assignee, 'avatar_url') else None
                })
            assignees_json = json.dumps(assignees_data)
            
            # Set primary assignee for backward compatibility
            if assignees_data:
                assignee_login = assignees_data[0]["login"]
                assignee_id = assignees_data[0]["id"]
        elif hasattr(github_issue, 'assignee') and github_issue.assignee:
            assignee_login = github_issue.assignee.login
            assignee_id = github_issue.assignee.id
            assignees_json = json.dumps([{
                "login": assignee_login,
                "id": assignee_id,
                "avatar_url": github_issue.assignee.avatar_url if hasattr(github_issue.assignee, 'avatar_url') else None
            }])
        
        # Handle labels
        labels_json = None
        if hasattr(github_issue, 'labels') and github_issue.labels:
            labels_data = []
            for label in github_issue.labels:
                labels_data.append({
                    "name": label.name,
                    "color": label.color if hasattr(label, 'color') else None,
                    "description": label.description if hasattr(label, 'description') else None
                })
            labels_json = json.dumps(labels_data)
        
        # Handle milestone
        milestone_title = None
        milestone_id = None
        milestone_number = None
        milestone_state = None
        if hasattr(github_issue, 'milestone') and github_issue.milestone:
            milestone_title = github_issue.milestone.title
            milestone_id = github_issue.milestone.id
            milestone_number = github_issue.milestone.number if hasattr(github_issue.milestone, 'number') else None
            milestone_state = github_issue.milestone.state if hasattr(github_issue.milestone, 'state') else None
        
        # Handle closed_by
        closed_by_login = None
        closed_by_id = None
        if hasattr(github_issue, 'closed_by') and github_issue.closed_by:
            closed_by_login = github_issue.closed_by.login
            closed_by_id = github_issue.closed_by.id
        
        return cls(
            github_issue_id=github_issue.id,
            github_issue_number=github_issue.number,
            node_id=github_issue.node_id if hasattr(github_issue, 'node_id') else "",
            
            repository_name=repo_name,
            repository_id=repo_id,
            repository_url=repo_url,
            
            title=github_issue.title,
            body=github_issue.body,
            body_html=github_issue.body_html if hasattr(github_issue, 'body_html') else None,
            body_text=github_issue.body_text if hasattr(github_issue, 'body_text') else None,
            
            state=github_issue.state,
            state_reason=github_issue.state_reason if hasattr(github_issue, 'state_reason') else None,
            locked=github_issue.locked,
            active_lock_reason=github_issue.active_lock_reason if hasattr(github_issue, 'active_lock_reason') else None,
            
            author_login=github_issue.user.login,
            author_id=github_issue.user.id,
            author_association=github_issue.author_association if hasattr(github_issue, 'author_association') else "NONE",
            
            assignee_login=assignee_login,
            assignee_id=assignee_id,
            assignees=assignees_json,
            
            labels=labels_json,
            
            milestone_title=milestone_title,
            milestone_id=milestone_id,
            milestone_number=milestone_number,
            milestone_state=milestone_state,
            
            created_at=github_issue.created_at,
            updated_at=github_issue.updated_at,
            closed_at=github_issue.closed_at if hasattr(github_issue, 'closed_at') else None,
            
            closed_by_login=closed_by_login,
            closed_by_id=closed_by_id,
            
            html_url=github_issue.html_url,
            url=github_issue.url,
            
            comments_count=github_issue.comments if hasattr(github_issue, 'comments') else 0,
            
            draft=github_issue.draft if hasattr(github_issue, 'draft') else None,
            score=github_issue.score if hasattr(github_issue, 'score') else None,
        )
    
    @classmethod
    def from_webhook_payload(cls, payload: dict):
        """
        Convert a GitHub webhook payload to our Issue model.
        
        Args:
            payload: GitHub webhook payload dictionary
            
        Returns:
            Issue: Our Issue model instance
        """
        # Extract issue data from payload
        issue_data = payload.get('issue', {})
        repository_data = payload.get('repository', {})
        
        if not issue_data:
            raise ValueError("No issue data found in webhook payload")
        
        # Extract repository info
        repo_name = repository_data.get('full_name', 'unknown/unknown')
        repo_id = repository_data.get('id', 0)
        repo_url = repository_data.get('url', '')
        
        # Handle assignees
        assignees_json = None
        assignee_login = None
        assignee_id = None
        
        assignees_data = issue_data.get('assignees', [])
        if assignees_data:
            assignees_list = []
            for assignee in assignees_data:
                assignees_list.append({
                    "login": assignee.get('login'),
                    "id": assignee.get('id'),
                    "avatar_url": assignee.get('avatar_url')
                })
            assignees_json = json.dumps(assignees_list)
            
            # Set primary assignee for backward compatibility
            if assignees_list:
                assignee_login = assignees_list[0]["login"]
                assignee_id = assignees_list[0]["id"]
        elif issue_data.get('assignee'):
            assignee_data = issue_data['assignee']
            assignee_login = assignee_data.get('login')
            assignee_id = assignee_data.get('id')
            assignees_json = json.dumps([{
                "login": assignee_login,
                "id": assignee_id,
                "avatar_url": assignee_data.get('avatar_url')
            }])
        
        # Handle labels
        labels_json = None
        labels_data = issue_data.get('labels', [])
        if labels_data:
            labels_list = []
            for label in labels_data:
                labels_list.append({
                    "name": label.get('name'),
                    "color": label.get('color'),
                    "description": label.get('description')
                })
            labels_json = json.dumps(labels_list)
        
        # Handle milestone
        milestone_title = None
        milestone_id = None
        milestone_number = None
        milestone_state = None
        milestone_data = issue_data.get('milestone')
        if milestone_data:
            milestone_title = milestone_data.get('title')
            milestone_id = milestone_data.get('id')
            milestone_number = milestone_data.get('number')
            milestone_state = milestone_data.get('state')
        
        # Handle closed_by
        closed_by_login = None
        closed_by_id = None
        closed_by_data = issue_data.get('closed_by')
        if closed_by_data:
            closed_by_login = closed_by_data.get('login')
            closed_by_id = closed_by_data.get('id')
        
        # Parse timestamps
        def parse_timestamp(timestamp_str):
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return None
        
        created_at = parse_timestamp(issue_data.get('created_at'))
        updated_at = parse_timestamp(issue_data.get('updated_at'))
        closed_at = parse_timestamp(issue_data.get('closed_at'))
        
        # Extract user info
        user_data = issue_data.get('user', {})
        
        return cls(
            github_issue_id=issue_data.get('id'),
            github_issue_number=issue_data.get('number'),
            node_id=issue_data.get('node_id', ''),
            
            repository_name=repo_name,
            repository_id=repo_id,
            repository_url=repo_url,
            
            title=issue_data.get('title', ''),
            body=issue_data.get('body'),
            body_html=None,  # Not available in webhook payload
            body_text=None,  # Not available in webhook payload
            
            state=issue_data.get('state', 'open'),
            state_reason=issue_data.get('state_reason'),
            locked=issue_data.get('locked', False),
            active_lock_reason=issue_data.get('active_lock_reason'),
            
            author_login=user_data.get('login', ''),
            author_id=user_data.get('id', 0),
            author_association=issue_data.get('author_association', 'NONE'),
            
            assignee_login=assignee_login,
            assignee_id=assignee_id,
            assignees=assignees_json,
            
            labels=labels_json,
            
            milestone_title=milestone_title,
            milestone_id=milestone_id,
            milestone_number=milestone_number,
            milestone_state=milestone_state,
            
            created_at=created_at,
            updated_at=updated_at,
            closed_at=closed_at,
            
            closed_by_login=closed_by_login,
            closed_by_id=closed_by_id,
            
            html_url=issue_data.get('html_url', ''),
            url=issue_data.get('url', ''),
            
            comments_count=issue_data.get('comments', 0),
            
            draft=None,  # Not available in webhook payload
            score=None,  # Not relevant for webhooks
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