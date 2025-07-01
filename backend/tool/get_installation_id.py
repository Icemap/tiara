#!/usr/bin/env python3
"""
Helper script to get GitHub App Installation ID.
This script will list all installations for your GitHub App.
"""

import sys
import os
import jwt
import time
import requests


def create_jwt_token(app_id: str, private_key: str):
    """Create a JWT token for GitHub App authentication."""
    # If private_key is a file path, read the file
    if os.path.isfile(private_key):
        with open(private_key, 'r') as key_file:
            private_key_content = key_file.read()
    else:
        private_key_content = private_key
    
    # Create JWT payload
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + 600,  # 10 minutes
        'iss': int(app_id)
    }
    
    # Create JWT token
    jwt_token = jwt.encode(payload, private_key_content, algorithm='RS256')
    return jwt_token


def get_installations(app_id: str, private_key: str):
    """Get all installations for the GitHub App."""
    jwt_token = create_jwt_token(app_id, private_key)
    
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Tiara-GitHub-App'
    }
    
    response = requests.get('https://api.github.com/app/installations', headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get installations: {response.status_code} {response.text}")
    
    return response.json()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python get_installation_id.py <APP_ID> <PRIVATE_KEY_PATH>")
        print("\nExample:")
        print("python get_installation_id.py 123456 /path/to/private-key.pem")
        sys.exit(1)
    
    app_id = sys.argv[1]
    private_key_path = sys.argv[2]
    
    try:
        print(f"Getting installations for GitHub App ID: {app_id}")
        installations = get_installations(app_id, private_key_path)
        
        if not installations:
            print("No installations found. Make sure your GitHub App is installed on at least one repository.")
            sys.exit(1)
        
        print(f"\nFound {len(installations)} installation(s):")
        print("-" * 80)
        
        for installation in installations:
            installation_id = installation['id']
            account = installation['account']
            account_type = account['type']
            account_name = account['login']
            
            print(f"Installation ID: {installation_id}")
            print(f"Account: {account_name} ({account_type})")
            print(f"Created: {installation['created_at']}")
            
            # Get repositories for this installation
            jwt_token = create_jwt_token(app_id, private_key_path)
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Tiara-GitHub-App'
            }
            
            repos_response = requests.get(
                f'https://api.github.com/app/installations/{installation_id}/repositories',
                headers=headers
            )
            
            if repos_response.status_code == 200:
                repos_data = repos_response.json()
                repositories = repos_data.get('repositories', [])
                if repositories:
                    print("Repositories:")
                    for repo in repositories:
                        print(f"  - {repo['full_name']}")
                else:
                    print("No repositories found for this installation.")
            else:
                print("Could not fetch repositories for this installation.")
            
            print("-" * 80)
        
        print("\nTo use with your app, set these environment variables:")
        print("GITHUB_APP_ID=" + app_id)
        print("GITHUB_APP_PRIVATE_KEY=" + private_key_path)
        
        if len(installations) == 1:
            print("GITHUB_APP_INSTALLATION_ID=" + str(installations[0]['id']))
        else:
            print("# Choose the appropriate installation ID from above")
            for i, installation in enumerate(installations):
                print(f"# GITHUB_APP_INSTALLATION_ID={installation['id']}  # {installation['account']['login']}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 