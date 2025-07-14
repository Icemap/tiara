from http import HTTPStatus
from flask import Blueprint

from backend.tool.logger import get_logger
from backend.tool.get_issues import get_github_client
from backend import config


bp = Blueprint("issues", __name__)

logger = get_logger(__name__)


@bp.route("/trigger-reply/<int:issue_id>", methods=["GET"])
def trigger_reply(issue_id: int):
    """
    Toggle (remove then re-add) the REPLY_LABEL on the specified issue to trigger reply logic.

    Steps:
    1. Remove ``config.REPLY_LABEL`` if it is currently on the issue.
    2. Add ``config.REPLY_LABEL`` back to the issue.

    Args:
        issue_id: The GitHub issue number.
    """
    try:
        # Authenticate via GitHub App and fetch the repository
        github_client = get_github_client()
        repo = github_client.get_repo(config.GITHUB_REPO_NAME)

        # Fetch the issue by number
        github_issue = repo.get_issue(issue_id)

        # Remove the label if it already exists
        existing_labels = [label.name for label in github_issue.get_labels()]
        if config.REPLY_LABEL in existing_labels:
            github_issue.remove_from_labels(config.REPLY_LABEL)
            logger.info(f"Removed label '{config.REPLY_LABEL}' from issue #{github_issue.number}")

        # Add the label back to trigger processing
        github_issue.add_to_labels(config.REPLY_LABEL)
        logger.info(f"Added label '{config.REPLY_LABEL}' to issue #{github_issue.number}")

        return {'status': 'success', 'message': 'Reply label toggled'}, HTTPStatus.OK

    except Exception as e:
        logger.error(f"Failed to trigger reply for issue #{issue_id}: {str(e)}")
        return {'status': 'error', 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
