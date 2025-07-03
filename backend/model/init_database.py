#!/usr/bin/env python3

import sys
from backend.model.issue import ISSUE_TABLE_NAME, Issue
from backend.model.base import db
from backend.tool.logger import get_logger
from backend.tool.get_issues import ISSUES_PER_PAGE, list_all_issues, get_issues_page, get_issues_since
from backend import config

logger = get_logger(__name__)

table_models = [
    (ISSUE_TABLE_NAME, Issue),
]

# Fields that should not be updated to avoid overwriting vector embeddings or primary keys
PROTECTED_FIELDS = {'github_issue_id', 'title_vec', 'body_vec'}

def init_tables():
    """Initialize database tables if they don't exist."""
    for table_name, table_model in table_models:
        if not db.has_table(table_name):
            table = db.create_table(schema=table_model)
            if table:
                logger.info(f"Table {table_name} created")
        else:
            logger.info(f"Table {table_name} already exists")


def diff_and_get_changed_fields(existing_issue: Issue, new_issue: Issue) -> dict:
    """
    Compare existing issue with new issue and return only changed fields.
    
    Args:
        existing_issue: Existing Issue model instance from database
        new_issue: New Issue model instance
        
    Returns:
        Dict containing only fields that have changed values
    """
    changed_fields = {}
    
    for field_name in Issue.model_fields:
        # Skip protected fields
        if field_name in PROTECTED_FIELDS:
            continue
            
        new_value = getattr(new_issue, field_name)
        existing_value = getattr(existing_issue, field_name)
        
        # Compare values - handle None values and type differences
        if _values_are_different(existing_value, new_value):
            changed_fields[field_name] = new_value
            logger.debug(f"Field '{field_name}' changed: {existing_value} -> {new_value}")
    
    return changed_fields


def _values_are_different(existing_value, new_value) -> bool:
    """
    Helper function to compare two values, handling None and type differences.
    
    Args:
        existing_value: Value from database
        new_value: New value from Issue model
        
    Returns:
        True if values are different, False if they are the same
    """
    # Handle None values
    if existing_value is None and new_value is None:
        return False
    if existing_value is None or new_value is None:
        return True
    
    # Handle string comparison (database might return different types)
    if isinstance(existing_value, str) and isinstance(new_value, str):
        return existing_value.strip() != new_value.strip()
    
    # Handle JSON string fields (labels, assignees, etc.)
    if isinstance(existing_value, str) and isinstance(new_value, str):
        # For JSON fields, compare as strings after normalization
        if existing_value.startswith('[') or existing_value.startswith('{'):
            return existing_value != new_value
    
    # Standard comparison for other types
    return existing_value != new_value


def save_issue_to_database(issue: Issue):
    """
    Save or update issue in database using proper upsert logic with diff optimization.
    
    Args:
        issue: Issue model instance
    """
    table = db.open_table(ISSUE_TABLE_NAME)
    
    try:
        # Try to get existing issue by github_issue_id
        existing_issue = table.get(issue.github_issue_id)
        
        if existing_issue:
            # Update existing issue with diff optimization
            logger.info(f"Checking for changes in issue #{issue.github_issue_number}: {issue.title}")
            
            # Get only changed fields
            changed_fields = diff_and_get_changed_fields(existing_issue, issue)
            
            if changed_fields:
                logger.info(f"Updating {len(changed_fields)} changed fields for issue #{issue.github_issue_number}")
                logger.debug(f"Changed fields: {list(changed_fields.keys())}")
                
                table.update(
                    changed_fields,
                    {"github_issue_id": issue.github_issue_id}
                )
                logger.info(f"Updated issue #{issue.github_issue_number} successfully")
            else:
                logger.info(f"No changes detected for issue #{issue.github_issue_number}, skipping update")
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
    Fetch all issues from GitHub repository and save them to database using since-based pagination.
    This function is idempotent - can be run multiple times safely.
    """
    if not config.GITHUB_REPO_NAME:
        raise ValueError("GITHUB_REPO_NAME is not configured")
    
    logger.info(f"Fetching all issues from repository: {config.GITHUB_REPO_NAME} using since-based pagination")
    
    try:
        # Process issues using since-based pagination
        processed_count = 0
        error_count = 0
        batch_num = 0
        since_datetime = None  # Start from the beginning
        
        while True:
            batch_num += 1
            logger.info(f"Processing batch {batch_num} (since: {since_datetime})")
            
            try:
                # Get issues since the last datetime
                issues_paginated = get_issues_since(
                    config.GITHUB_REPO_NAME, 
                    state="all", 
                    since=since_datetime
                )
                
                # Convert to list to get the batch (GitHub's per_page default is usually 30-100)
                batch_issues = list(issues_paginated[:ISSUES_PER_PAGE])
                
                # If no issues in this batch, we're done
                if not batch_issues:
                    logger.info(f"No more issues found in batch {batch_num}, stopping")
                    break
                
                logger.info(f"Processing {len(batch_issues)} issues from batch {batch_num}")
                
                # Track the latest updated_at time for next iteration
                latest_updated_at = None
                
                # Process each issue in the current batch
                for github_issue in batch_issues:
                    try:
                        # Convert PyGithub Issue to our Issue model
                        issue = Issue.from_github_issue(github_issue)
                        
                        # Save to database
                        save_issue_to_database(issue)
                        processed_count += 1
                        
                        # Track the latest updated_at for pagination
                        if latest_updated_at is None or github_issue.updated_at > latest_updated_at:
                            latest_updated_at = github_issue.updated_at
                        
                        logger.debug(f"Processed issue #{issue.github_issue_number}: {issue.title}")
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing issue #{github_issue.number}: {str(e)}")
                        continue
                
                # Update since_datetime for next iteration
                # Add 1 second to avoid getting the same issue again
                if latest_updated_at:
                    import datetime
                    since_datetime = latest_updated_at + datetime.timedelta(seconds=1)
                
                logger.info(f"Completed batch {batch_num}. Total processed so far: {processed_count} issues")
                logger.info(f"Next batch will start from: {since_datetime}")
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {str(e)}")
                # For since-based pagination, we should stop on error as we can't continue safely
                logger.error("Stopping due to batch processing error")
                break
        
        logger.info(f"Issue processing completed: {processed_count} successful, {error_count} errors across {batch_num} batches")
        
        if processed_count == 0:
            logger.warning("No issues were processed. This might indicate a permissions or configuration issue.")
        
    except Exception as e:
        logger.error(f"Error fetching issues from GitHub: {str(e)}")
        raise


def init_database():
    """
    Initialize database tables and populate with existing GitHub issues.
    This function is idempotent and can be run multiple times safely.
    
    Args:
        page_size: Number of issues to process per page (default: 10)
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
