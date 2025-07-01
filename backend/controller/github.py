from http import HTTPStatus
from backend.model import base
from backend.tool.logger import get_logger
from github_webhook import Webhook
from backend import config
from backend.model.issue import ISSUE_TABLE_NAME, Issue

logger = get_logger(__name__)

webhook = None

def init_webhook(app):
    global webhook
    webhook = Webhook(
        app,
        endpoint=config.GITHUB_WEBHOOK_URL,
        secret=config.GITHUB_WEBHOOK_SECRET
    )

    @webhook.hook(event_type="issues")
    def github_webhook_issues(data):
        """Handle GitHub Issues webhook events."""
        logger.info(f"Received GitHub Issues webhook: {data}")
        
        try:
            # Convert webhook payload to our Issue model
            issue = Issue.from_webhook_payload(data)
            
            action = data.get('action', 'unknown')
            logger.info(f"Issue {action}: #{issue.github_issue_number} - {issue.title}")
            logger.info(f"Repository: {issue.repository_name}")
            logger.info(f"Author: {issue.author_login}")
            logger.info(f"State: {issue.state}")
            
            if issue.labels:
                labels = issue.get_labels_list()
                logger.info(f"Labels: {[label['name'] for label in labels]}")
            
            if issue.assignees:
                assignees = issue.get_assignees_list()
                logger.info(f"Assignees: {[assignee['login'] for assignee in assignees]}")
            
            save_issue_to_database(issue, action)
            
            logger.info(f"Successfully processed {action} event for issue #{issue.github_issue_number}")
            
        except Exception as e:
            logger.error(f"Error processing Issues webhook: {str(e)}")
            return {'status': 'error', 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
        
        return {'status': 'success', 'message': 'Issues webhook processed'}, HTTPStatus.OK


def save_issue_to_database(issue: Issue, action: str):
    """
    Save or update issue in database.
    
    Args:
        issue: Issue model instance
        action: The webhook action (opened, edited, closed, etc.)
    """
    logger.info(f"Would save issue to database: {issue.github_issue_id} (action: {action})")

    table = base.db.open_table(ISSUE_TABLE_NAME)
    if action == 'opened':
        table.insert(issue)
    else:
        table.update(issue)
