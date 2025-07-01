from github import Github, GithubIntegration
import sys
import os
from backend import config


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
        return Github(token)
    
    raise ValueError("No valid GitHub authentication method found.")


def list_all_issues(repo_name: str, state: str = "all"):
    """
    List all issues from the given repository.

    Args:
        repo_name: Repository name
        state: State of the issues to list

    Returns:
        List of issues
    """
    if not repo_name:
        raise ValueError("Repository name is required. Please set GITHUB_REPO_NAME environment variable.")
    
    g = get_github_client()
    repo = g.get_repo(repo_name)
    # state: 'open', 'closed', 'all'
    issues = repo.get_issues(state=state)
    return issues


if __name__ == '__main__':
    try:
        from backend import config
        
        # Check if repository name is configured
        if not config.GITHUB_REPO_NAME:
            print("Error: GITHUB_REPO_NAME environment variable is not set.")
            print("Please set it in your .env file or environment variables.")
            print("Example: GITHUB_REPO_NAME=username/repository-name")
            sys.exit(1)
        
        # Check authentication configuration
        has_github_app = (config.GITHUB_APP_ID and 
                         config.GITHUB_APP_PRIVATE_KEY and 
                         config.GITHUB_APP_INSTALLATION_ID)
        
        if not has_github_app:
            print("Error: No GitHub authentication configured.")
            print("\nFor GitHub App authentication, set these environment variables:")
            print("- GITHUB_APP_ID: Your GitHub App ID")
            print("- GITHUB_APP_PRIVATE_KEY: Path to private key file or key content")
            print("- GITHUB_APP_INSTALLATION_ID: Installation ID for your repository")
            sys.exit(1)
        
        print(f"Fetching issues from repository: {config.GITHUB_REPO_NAME}")
        issues = list_all_issues(config.GITHUB_REPO_NAME, state="all")
        
        for issue in issues:
            print("------------------------")
            print(f"#{issue.number} [{issue.state}] {issue.title}")
            print("------------------------")
        
        print(f"\nSummary: {len(issues)} issues")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure to run this script from the project root directory using:")
        print("python -m backend.tool.get_issues")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)