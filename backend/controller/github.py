from http import HTTPStatus
from backend.tool.logging import get_logger
from github_webhook import Webhook
from backend import config

logger = get_logger(__name__)

# bp = Blueprint("github", __name__)


# def verify_signature(payload_body, signature_header, secret):
#     """Verify that the payload was sent from GitHub by validating SHA256."""
#     if not signature_header:
#         return False
    
#     hash_object = hmac.new(secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
#     expected_signature = "sha256=" + hash_object.hexdigest()
    
#     if not hmac.compare_digest(expected_signature, signature_header):
#         return False
    
#     return True


# @bp.route("/webhook", methods=["POST"])
# def github_webhook():
#     """Handle GitHub webhook events for Issues."""
#     try:
#         # Get request data
#         payload = request.get_data()
#         signature = request.headers.get('X-Hub-Signature-256')
#         event_type = request.headers.get('X-GitHub-Event')
        
#         # Verify webhook signature (optional, uncomment if you want to verify)
#         # webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
#         # if webhook_secret and not verify_signature(payload, signature, webhook_secret):
#         #     logger.warning("Invalid signature for GitHub webhook")
#         #     return {'message': 'Invalid signature'}, HTTPStatus.UNAUTHORIZED
        
#         # Parse JSON payload
#         try:
#             event_data = json.loads(payload.decode('utf-8'))
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON payload")
#             return {'message': 'Invalid JSON payload'}, HTTPStatus.BAD_REQUEST
        
#         # Handle Issues events
#         if event_type == 'issues':
#             return handle_issues_event(event_data)
#         elif event_type == 'issue_comment':
#             return handle_issue_comment_event(event_data)
#         else:
#             logger.info(f"Received unsupported event type: {event_type}")
#             return {'message': f'Event type {event_type} not supported'}, HTTPStatus.OK
        
#     except Exception as e:
#         logger.error(f"Error processing webhook: {str(e)}")
#         return {'message': 'Internal server error'}, HTTPStatus.INTERNAL_SERVER_ERROR


# def handle_issues_event(event_data):
#     """Handle Issues events (opened, edited, closed, reopened, assigned, etc.)."""
#     try:
#         action = event_data.get('action')
#         issue = event_data.get('issue', {})
#         repository = event_data.get('repository', {})
#         sender = event_data.get('sender', {})
        
#         issue_number = issue.get('number')
#         issue_title = issue.get('title')
#         issue_url = issue.get('html_url')
#         repo_name = repository.get('full_name')
#         sender_login = sender.get('login')
        
#         logger.info(f"Issues event: {action} - Issue #{issue_number} in {repo_name}")
#         logger.info(f"Title: {issue_title}")
#         logger.info(f"URL: {issue_url}")
#         logger.info(f"Sender: {sender_login}")
        
#         # Process different issue actions
#         if action == 'opened':
#             process_issue_opened(event_data)
#         elif action == 'closed':
#             process_issue_closed(event_data)
#         elif action == 'reopened':
#             process_issue_reopened(event_data)
#         elif action == 'edited':
#             process_issue_edited(event_data)
#         elif action == 'assigned':
#             process_issue_assigned(event_data)
#         elif action == 'unassigned':
#             process_issue_unassigned(event_data)
#         elif action == 'labeled':
#             process_issue_labeled(event_data)
#         elif action == 'unlabeled':
#             process_issue_unlabeled(event_data)
#         else:
#             logger.info(f"Unhandled issue action: {action}")
        
#         return {'message': 'Issues event processed successfully'}, HTTPStatus.OK
        
#     except Exception as e:
#         logger.error(f"Error handling issues event: {str(e)}")
#         return {'message': 'Error processing issues event'}, HTTPStatus.INTERNAL_SERVER_ERROR


# def handle_issue_comment_event(event_data):
#     """Handle Issue Comment events (created, edited, deleted)."""
#     try:
#         action = event_data.get('action')
#         comment = event_data.get('comment', {})
#         issue = event_data.get('issue', {})
#         repository = event_data.get('repository', {})
#         sender = event_data.get('sender', {})
        
#         comment_id = comment.get('id')
#         comment_body = comment.get('body')
#         issue_number = issue.get('number')
#         repo_name = repository.get('full_name')
#         sender_login = sender.get('login')
        
#         logger.info(f"Issue comment event: {action} - Comment {comment_id} on Issue #{issue_number} in {repo_name}")
#         logger.info(f"Comment: {comment_body[:100]}{'...' if len(comment_body) > 100 else ''}")
#         logger.info(f"Sender: {sender_login}")
        
#         # Process different comment actions
#         if action == 'created':
#             process_comment_created(event_data)
#         elif action == 'edited':
#             process_comment_edited(event_data)
#         elif action == 'deleted':
#             process_comment_deleted(event_data)
#         else:
#             logger.info(f"Unhandled comment action: {action}")
        
#         return {'message': 'Issue comment event processed successfully'}, HTTPStatus.OK
        
#     except Exception as e:
#         logger.error(f"Error handling issue comment event: {str(e)}")
#         return {'message': 'Error processing issue comment event'}, HTTPStatus.INTERNAL_SERVER_ERROR


# # Issue event processors
# def process_issue_opened(event_data):
#     """Process when an issue is opened."""
#     issue = event_data.get('issue', {})
#     logger.info(f"Processing opened issue: {issue.get('title')}")
#     # Add your custom logic here


# def process_issue_closed(event_data):
#     """Process when an issue is closed."""
#     issue = event_data.get('issue', {})
#     logger.info(f"Processing closed issue: {issue.get('title')}")
#     # Add your custom logic here


# def process_issue_reopened(event_data):
#     """Process when an issue is reopened."""
#     issue = event_data.get('issue', {})
#     logger.info(f"Processing reopened issue: {issue.get('title')}")
#     # Add your custom logic here


# def process_issue_edited(event_data):
#     """Process when an issue is edited."""
#     issue = event_data.get('issue', {})
#     changes = event_data.get('changes', {})
#     logger.info(f"Processing edited issue: {issue.get('title')}")
#     logger.info(f"Changes: {list(changes.keys())}")
#     # Add your custom logic here


# def process_issue_assigned(event_data):
#     """Process when an issue is assigned."""
#     issue = event_data.get('issue', {})
#     assignee = event_data.get('assignee', {})
#     logger.info(f"Processing assigned issue: {issue.get('title')} to {assignee.get('login')}")
#     # Add your custom logic here


# def process_issue_unassigned(event_data):
#     """Process when an issue is unassigned."""
#     issue = event_data.get('issue', {})
#     assignee = event_data.get('assignee', {})
#     logger.info(f"Processing unassigned issue: {issue.get('title')} from {assignee.get('login')}")
#     # Add your custom logic here


# def process_issue_labeled(event_data):
#     """Process when a label is added to an issue."""
#     issue = event_data.get('issue', {})
#     label = event_data.get('label', {})
#     logger.info(f"Processing labeled issue: {issue.get('title')} with label {label.get('name')}")
#     # Add your custom logic here


# def process_issue_unlabeled(event_data):
#     """Process when a label is removed from an issue."""
#     issue = event_data.get('issue', {})
#     label = event_data.get('label', {})
#     logger.info(f"Processing unlabeled issue: {issue.get('title')} removed label {label.get('name')}")
#     # Add your custom logic here


# # Comment event processors
# def process_comment_created(event_data):
#     """Process when a comment is created on an issue."""
#     comment = event_data.get('comment', {})
#     issue = event_data.get('issue', {})
#     logger.info(f"Processing created comment on issue: {issue.get('title')}")
#     # Add your custom logic here


# def process_comment_edited(event_data):
#     """Process when a comment is edited."""
#     comment = event_data.get('comment', {})
#     issue = event_data.get('issue', {})
#     changes = event_data.get('changes', {})
#     logger.info(f"Processing edited comment on issue: {issue.get('title')}")
#     # Add your custom logic here


# def process_comment_deleted(event_data):
#     """Process when a comment is deleted."""
#     comment = event_data.get('comment', {})
#     issue = event_data.get('issue', {})
#     logger.info(f"Processing deleted comment on issue: {issue.get('title')}")
#     # Add your custom logic here


# @bp.route("/status", methods=["GET"])
# def github_status():
#     """Health check endpoint for GitHub webhook."""
#     return {'status': 'GitHub webhook is ready'}, HTTPStatus.OK

webhook = None

def init_webhook(app):
    global webhook
    webhook = Webhook(
        app,
        endpoint=config.GITHUB_WEBHOOK_URL,
        secret=config.GITHUB_WEBHOOK_SECRET
    )

    @webhook.hook(event_type="issues")
    def github_webhook(data):
        logger.info(f"Received GitHub webhook: {data}")
        return {'status': 'GitHub webhook received'}, HTTPStatus.OK

    @webhook.hook(event_type="issue_comment")
    def github_webhook_issue_comment(data):
        logger.info(f"Received GitHub issue comment webhook: {data}")
        return {'status': 'GitHub webhook received'}, HTTPStatus.OK