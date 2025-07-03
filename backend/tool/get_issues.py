from github import Github, GithubIntegration
import sys
import os
from backend import config

ISSUES_PER_PAGE = 100

def create_github_app_token(app_id: str, private_key: str, installation_id: str):
    """
    Create a GitHub App installation token using JWT.
    
    Args:
        app_id: GitHub App ID
        private_key: Private key content or path to private key file
        installation_id: Installation ID for the repository
    
    Returns:
        Installation access token
    """
    # If private_key is a file path, read the file
    if os.path.isfile(private_key):
        with open(private_key, 'r') as key_file:
            private_key_content = key_file.read()
    else:
        private_key_content = private_key
    
    # Create GitHub integration object with private key content
    integration = GithubIntegration(int(app_id), private_key_content)
    
    # Get installation access token
    installation_access_token = integration.get_access_token(int(installation_id))
    return installation_access_token.token


def get_github_client():
    """
    Create a GitHub client using available authentication methods.
    Uses GitHub App authentication.
    """
    if config.GITHUB_APP_ID and config.GITHUB_APP_PRIVATE_KEY and config.GITHUB_APP_INSTALLATION_ID:
        print("Using GitHub App authentication...")
        token = create_github_app_token(
            config.GITHUB_APP_ID,
            config.GITHUB_APP_PRIVATE_KEY,
            config.GITHUB_APP_INSTALLATION_ID
        )
        return Github(token, per_page=ISSUES_PER_PAGE)
    
    raise ValueError("No valid GitHub authentication method found.")


def list_all_issues(repo_name: str, state: str = "all"):
    """
    List all issues from the given repository.

    Args:
        repo_name: Repository name
        state: State of the issues to list

    Returns:
        PaginatedList of issues (not converted to list)
    """
    if not repo_name:
        raise ValueError("Repository name is required. Please set GITHUB_REPO_NAME environment variable.")
    
    g = get_github_client()
    repo = g.get_repo(repo_name)
    # state: 'open', 'closed', 'all'
    issues = repo.get_issues(state=state)
    return issues


def get_issues_page(repo_name: str, state: str = "all", page: int = 0):
    """
    Get a specific page of issues from the repository.
    Note: This function is deprecated for large datasets. Use get_issues_since instead.

    Args:
        repo_name: Repository name
        state: State of the issues to list ('open', 'closed', 'all')
        page: Page number to fetch (0-based index)

    Returns:
        List of issues for the specific page
    """
    if not repo_name:
        raise ValueError("Repository name is required. Please set GITHUB_REPO_NAME environment variable.")
    
    g = get_github_client()
    repo = g.get_repo(repo_name)
    issues = repo.get_issues(state=state)
    
    # Get the specific page
    return issues.get_page(page)


def get_issues_since(repo_name: str, state: str = "all", since=None):
    """
    Get issues from the repository since a specific datetime.
    This uses cursor-based pagination which works for large datasets.

    Args:
        repo_name: Repository name
        state: State of the issues to list ('open', 'closed', 'all')
        since: datetime object to get issues updated since this time. If None, gets all issues.

    Returns:
        PaginatedList of issues
    """
    if not repo_name:
        raise ValueError("Repository name is required. Please set GITHUB_REPO_NAME environment variable.")
    
    g = get_github_client()
    repo = g.get_repo(repo_name)
    
    # Use since parameter for cursor-based pagination
    if since:
        issues = repo.get_issues(
            state=state,
            since=since,
            sort="updated",
            direction="asc"
        )
    else:
        issues = repo.get_issues(
            state=state,
            sort="updated",
            direction="asc"
        )
    
    return issues
