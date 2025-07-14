import os
from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
# SECRET_KEY: str = os.getenv("SECRET_KEY")

REPLY_LABEL: str = os.getenv("REPLY_LABEL", default="tiara")

SERVERLESS_CLUSTER_HOST: str = os.getenv("SERVERLESS_CLUSTER_HOST")
SERVERLESS_CLUSTER_PORT: int = int(os.getenv("SERVERLESS_CLUSTER_PORT"))
SERVERLESS_CLUSTER_USERNAME: str = os.getenv("SERVERLESS_CLUSTER_USERNAME")
SERVERLESS_CLUSTER_PASSWORD: str = os.getenv("SERVERLESS_CLUSTER_PASSWORD")
SERVERLESS_CLUSTER_DATABASE_NAME: str = os.getenv("SERVERLESS_CLUSTER_DATABASE_NAME")

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
MIN_DISTANCE: float = float(os.getenv("MIN_DISTANCE", default=0.7))

# GitHub Config
GITHUB_REPO_NAME: str = os.getenv("GITHUB_REPO_NAME")

# For getting issues from the webhook
GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_WEBHOOK_URL: str = os.getenv("GITHUB_WEBHOOK_URL", default="/github/webhook")

# GitHub App authentication
GITHUB_APP_ID: str = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY: str = os.getenv("GITHUB_APP_PRIVATE_KEY")  # Path to private key file or key content
GITHUB_APP_INSTALLATION_ID: str = os.getenv("GITHUB_APP_INSTALLATION_ID")
