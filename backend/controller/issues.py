from http import HTTPStatus
from flask import Blueprint

from backend.tool.logger import get_logger
from backend.tool.get_issues import get_github_client
from backend.tool.send_issue_comment import (
    search_similar_issues,
    log_similar_issues,
    send_issue_comment,
)
from backend.model.issue import Issue
from backend import config


bp = Blueprint("issues", __name__)

logger = get_logger(__name__)


@bp.route("/trigger-reply/<int:issue_id>", methods=["POST"])
def trigger_reply(issue_id: int):
    try:
        # Authenticate via GitHub App and fetch the repository
        github_client = get_github_client()
        repo = github_client.get_repo(config.GITHUB_REPO_NAME)

        # Fetch the issue by number from GitHub
        github_issue = repo.get_issue(issue_id)

        # Convert PyGithub Issue to our internal Issue model
        issue_model = Issue.from_github_issue(github_issue)

        # Perform semantic search for similar issues
        similar_issues = search_similar_issues(issue_model, limit_per_field=5)
        log_similar_issues(similar_issues, issue_model)

        # Always send the comment (bypass should_send_comment checks)
        send_issue_comment(issue_model, similar_issues)

        return {'status': 'success', 'message': 'Comment posted'}, HTTPStatus.OK

    except Exception as e:
        logger.error(f"Failed to trigger reply for issue #{issue_id}: {str(e)}")
        return {'status': 'error', 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
