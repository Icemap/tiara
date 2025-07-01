# Tiara - TiDB Intelligent And Reliability Assistant

> This project is inspired by [Gaby](https://pkg.go.dev/golang.org/x/oscar/internal/gaby).

A Flask-based service that provides GitHub issue tracking and webhook handling capabilities with TiDB vector database integration.

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- TiDB Serverless cluster (for vector database)

## Quick Start

### 1. Install Dependencies

This project uses Poetry for dependency management:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following configuration:

```env
# TiDB Configuration
TIDB_HOST=your-tidb-host
TIDB_PORT=4000
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DATABASE=your-database-name
TIDB_CA_PATH=/path/to/ca-cert.pem

# Embedding Model
EMBEDDING_MODEL=text-embedding-3-small

# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=/path/to/your/private-key.pem
GITHUB_APP_INSTALLATION_ID=12345678
GITHUB_REPO_NAME=username/repository-name

# Webhook Configuration
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_WEBHOOK_URL=/github/webhook
```

### 3. Database Initialization

Initialize the database and fetch existing GitHub issues:

```bash
# Run from project root directory
python -m backend.model.init_database
```

This command will:
- Create necessary database tables
- Fetch all existing issues from your GitHub repository
- Save them to the TiDB database
- Can be run multiple times safely (idempotent)

### 4. Start the Flask Service

```bash
# Development mode with auto-reload
flask run --reload

# Or specify host and port
flask run --host=0.0.0.0 --port=5000 --reload

# Production mode
flask run
```

The service will be available at `http://localhost:5000`

## GitHub App Authentication Setup

### Step 1: Create a GitHub App

1. Go to your GitHub account settings
2. Navigate to **Developer settings** → **GitHub Apps** → **New GitHub App**
3. Fill in the required information:
   - **App name**: Choose a unique name (e.g., "Tiara Issue Bot")
   - **Homepage URL**: Your app's homepage
   - **Webhook URL**: `https://your-domain.com/github/webhook`
   - **Webhook secret**: Generate a random secret

### Step 2: Configure Permissions

Set the following permissions for your GitHub App:

- **Repository permissions**:
  - Issues: Read & Write
  - Metadata: Read
  - Contents: Read (optional, for repository access)

### Step 3: Subscribe to Events

Subscribe to the following events:
- Issues
- Issue comments (optional)

### Step 4: Generate Private Key

1. After creating the app, scroll down to **Private keys**
2. Click **Generate a private key**
3. Download the `.pem` file
4. Save it securely and note the file path

### Step 5: Install the App

1. Go to **Install App** tab
2. Install it on your target repository
3. Note the **Installation ID** from the URL (e.g., `https://github.com/settings/installations/12345678`)

### Step 6: Update Environment Variables

Update your `.env` file with the GitHub App credentials:

```env
GITHUB_APP_ID=1455764                                    # From Step 1
GITHUB_APP_PRIVATE_KEY=./your-app.private-key.pem      # From Step 4
GITHUB_APP_INSTALLATION_ID=73153407                     # From Step 5
GITHUB_REPO_NAME=username/repository-name               # Your target repository
GITHUB_WEBHOOK_SECRET=your-webhook-secret               # From Step 1
```

## Service Features

### Webhook Handling

The service automatically handles GitHub webhooks for:
- **Issue events**: opened, closed, edited, assigned, etc.
- **Issue comment events**: created, edited, deleted

Webhook endpoint: `POST /github/webhook`

### Database Operations

- **Issues**: Stored with vector embeddings for semantic search
- **Auto-sync**: New webhook events automatically update the database
- **Upsert logic**: Issues are updated if they exist, inserted if new

### API Endpoints

- `POST /github/webhook` - GitHub webhook handler
- Health check endpoints for service monitoring

## Development

### Project Structure

```
tiara/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration management
│   │   └── github.py       # GitHub webhook handlers
│   ├── model/
│   │   ├── base.py         # Database base configuration
│   │   ├── issue.py        # Issue model with vector embeddings
│   │   └── init_database.py # Database initialization script
│   └── tool/
│       ├── logger.py       # Logging configuration
│       └── get_issues.py   # GitHub API client
├── .env                    # Environment variables
├── pyproject.toml          # Poetry configuration
└── README.md              # This file
```

### Running Commands

**Important**: Always run commands from the project root directory to avoid module import issues.

```bash
# Correct way to run scripts
python -m backend.model.init_database
python -m backend.tool.get_issues

# Flask development
export FLASK_APP=backend.app
flask run --reload
```

### Database Schema

The service uses TiDB with vector search capabilities:
- **Issues table**: Stores GitHub issues with metadata and vector embeddings
- **Vector fields**: `title_vec` and `body_vec` for semantic search
- **Primary key**: `github_issue_id` for efficient upserts

## Troubleshooting

### Common Issues

1. **Module import errors**: Make sure you're running commands from the project root
2. **GitHub authentication errors**: Verify your GitHub App credentials and permissions
3. **Database connection errors**: Check your TiDB configuration and network access
4. **Webhook not receiving events**: Verify your webhook URL and GitHub App installation

### Logs

The service provides detailed logging for troubleshooting:
- GitHub webhook events processing
- Database operations (insert/update)
- Authentication status
- Error details with stack traces

## Alternative: Personal Access Token

If you prefer using a Personal Access Token instead of GitHub App:

```env
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_REPO_NAME=username/repository-name
```

Note: GitHub App authentication is recommended for production use due to better security and rate limits.
