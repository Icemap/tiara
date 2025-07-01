#!/usr/bin/env python3

import sys
from backend.model.issue import ISSUE_TABLE_NAME, Issue
from backend.model.base import db
from backend.tool.logger import get_logger
from backend.tool.get_issues import list_all_issues
from backend import config

logger = get_logger(__name__)

table_models = [
    (ISSUE_TABLE_NAME, Issue),
]

def init_tables():
    """Initialize database tables if they don't exist."""
    for table_name, table_model in table_models:
        if not db.has_table(table_name):
            table = db.create_table(schema=table_model)
            if table:
                logger.info(f"Table {table_name} created")
        else:
            logger.info(f"Table {table_name} already exists")


def save_issue_to_database(issue: Issue):
    """
    Save or update issue in database using proper upsert logic.
    
    Args:
        issue: Issue model instance
    """
    table = db.open_table(ISSUE_TABLE_NAME)
    
    try:
        # Try to get existing issue by github_issue_id
        existing_issue = table.get(issue.github_issue_id)
        
        if existing_issue:
            # Update existing issue
            logger.info(f"Updating existing issue #{issue.github_issue_number}: {issue.title}")
            
            # Convert issue object to dict for update
            update_data = {}
            for field_name in Issue.model_fields:
                if field_name != 'github_issue_id':  # Don't update primary key
                    value = getattr(issue, field_name)
                    update_data[field_name] = value
            
            table.update(
                update_data,
                {"github_issue_id": issue.github_issue_id}
            )
            logger.info(f"Updated issue #{issue.github_issue_number} successfully")
        else:
            # Insert new issue
            logger.info(f"Inserting new issue #{issue.github_issue_number}: {issue.title}")
            table.insert(issue)
            logger.info(f"Inserted issue #{issue.github_issue_number} successfully")
            
    except Exception as e:
        logger.error(f"Error saving issue #{issue.github_issue_number}: {str(e)}")
        raise


def fetch_and_save_all_issues():
    """
    Fetch all issues from GitHub repository and save them to database.
    This function is idempotent - can be run multiple times safely.
    """
    if not config.GITHUB_REPO_NAME:
        raise ValueError("GITHUB_REPO_NAME is not configured")
    
    logger.info(f"Fetching all issues from repository: {config.GITHUB_REPO_NAME}")
    
    try:
        # Get all issues from GitHub (both open and closed)
        issues = list_all_issues(config.GITHUB_REPO_NAME, state="all")
        issues_list = list(issues)  # Convert generator to list
        
        logger.info(f"Found {len(issues_list)} issues to process")
        
        if not issues_list:
            logger.info("No issues found in repository")
            return
        
        # Process each issue
        processed_count = 0
        error_count = 0
        
        for github_issue in issues_list:
            try:
                # Convert PyGithub Issue to our Issue model
                issue = Issue.from_github_issue(github_issue)
                
                # Save to database
                save_issue_to_database(issue)
                processed_count += 1
                
                logger.debug(f"Processed issue #{issue.github_issue_number}: {issue.title}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing issue #{github_issue.number}: {str(e)}")
                continue
        
        logger.info(f"Issue processing completed: {processed_count} successful, {error_count} errors")
        
    except Exception as e:
        logger.error(f"Error fetching issues from GitHub: {str(e)}")
        raise


def init_database():
    """
    Initialize database tables and populate with existing GitHub issues.
    This function is idempotent and can be run multiple times safely.
    """
    logger.info("Initializing database")
    
    try:
        # Step 1: Create tables if they don't exist
        init_tables()
        
        # Step 2: Fetch and save all issues from GitHub
        logger.info("Fetching and saving issues from GitHub")
        fetch_and_save_all_issues()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


if __name__ == '__main__':
    """
    Standalone script to initialize database with GitHub issues.
    Usage: python -m backend.model.init_database
    """
    try:
        logger.info("Starting database initialization script")
        
        # Check configuration
        if not config.GITHUB_REPO_NAME:
            logger.error("GITHUB_REPO_NAME environment variable is not set")
            sys.exit(1)
        
        # Check GitHub authentication
        has_github_app = (config.GITHUB_APP_ID and 
                         config.GITHUB_APP_PRIVATE_KEY and 
                         config.GITHUB_APP_INSTALLATION_ID)
        
        if not has_github_app:
            logger.error("GitHub authentication is not configured")
            logger.error("Please set GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, and GITHUB_APP_INSTALLATION_ID")
            sys.exit(1)
        
        # Run initialization
        init_database()
        
        logger.info("Database initialization script completed successfully")
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
