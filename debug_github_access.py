#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend import config
from backend.tool.get_issues import get_github_client

def debug_github_access():
    """Debug GitHub access and repository information."""
    
    print(f"Repository name: {config.GITHUB_REPO_NAME}")
    print(f"GitHub App ID: {config.GITHUB_APP_ID}")
    print(f"GitHub App Installation ID: {config.GITHUB_APP_INSTALLATION_ID}")
    print(f"GitHub App Private Key configured: {'Yes' if config.GITHUB_APP_PRIVATE_KEY else 'No'}")
    
    try:
        # Test GitHub client creation
        print("\n--- Testing GitHub client creation ---")
        g = get_github_client()
        print("✓ GitHub client created successfully")
        
        # Test repository access
        print(f"\n--- Testing repository access: {config.GITHUB_REPO_NAME} ---")
        repo = g.get_repo(config.GITHUB_REPO_NAME)
        print(f"✓ Repository accessed successfully")
        print(f"Repository full name: {repo.full_name}")
        print(f"Repository description: {repo.description}")
        print(f"Repository private: {repo.private}")
        
        # Test issues access with different approaches
        print(f"\n--- Testing issues access ---")
        
        # Method 1: Get all issues
        all_issues = repo.get_issues(state="all")
        print(f"All issues (all states) count: {all_issues.totalCount}")
        
        # Method 2: Get open issues only
        open_issues = repo.get_issues(state="open")
        print(f"Open issues count: {open_issues.totalCount}")
        
        # Method 3: Get closed issues only
        closed_issues = repo.get_issues(state="closed")
        print(f"Closed issues count: {closed_issues.totalCount}")
        
        # Method 4: Try to get first few issues to see if there are any
        print(f"\n--- Testing first page of issues ---")
        first_page = list(repo.get_issues(state="all")[:5])  # Get first 5 issues
        print(f"First page issues count: {len(first_page)}")
        
        if first_page:
            print("Sample issues:")
            for issue in first_page:
                print(f"  #{issue.number}: {issue.title} [{issue.state}]")
        else:
            print("No issues found in first page")
            
        # Method 5: Check if we can see pull requests (which might be included in issues)
        print(f"\n--- Testing pull requests access ---")
        pulls = repo.get_pulls(state="all")
        print(f"Pull requests count: {pulls.totalCount}")
        
        # Method 6: Check permissions
        print(f"\n--- Testing repository permissions ---")
        try:
            permissions = repo.get_collaborator_permission(g.get_user())
            print(f"User permissions: {permissions}")
        except Exception as e:
            print(f"Could not get permissions: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_github_access() 