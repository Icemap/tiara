# Tiara - TiDB Intelligent And Reliability Assistant

> This project is inspired by [Gaby](https://pkg.go.dev/golang.org/x/oscar/internal/gaby).

## GitHub App Authentication Setup

This project supports GitHub App authentication for accessing GitHub API. Here's how to set it up:

### Step 1: Create a GitHub App

1. Go to your GitHub account settings
2. Navigate to **Developer settings** → **GitHub Apps** → **New GitHub App**
3. Fill in the required information:
   - **App name**: Choose a unique name
   - **Homepage URL**: Your app's homepage
   - **Webhook URL**: `https://your-domain.com/github/webhook`
   - **Webhook secret**: Generate a random secret

### Step 2: Configure Permissions

Set the following permissions for your GitHub App:
- **Repository permissions**:
  - Issues: Read & Write
  - Metadata: Read
  - Pull requests: Read & Write (if needed)

### Step 3: Subscribe to Events

Subscribe to these events:
- Issues
- Issue comments

### Step 4: Generate Private Key

1. After creating the app, scroll down to **Private keys**
2. Click **Generate a private key**
3. Download the `.pem` file

### Step 5: Install the App

1. Go to **Install App** tab
2. Install it on your target repository
3. Note the **Installation ID** from the URL (e.g., `https://github.com/settings/installations/12345678`)

### Step 6: Configure Environment Variables

Add these to your `.env` file:

```env
# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=/path/to/your/private-key.pem
GITHUB_APP_INSTALLATION_ID=12345678
GITHUB_REPO_NAME=username/repository-name

# Webhook Configuration
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_WEBHOOK_URL=/github/webhook
```

### Alternative: Personal Access Token

If you prefer using a Personal Access Token instead:

```env
GITHUB_REPO_NAME=username/repository-name
```

## Usage

```bash
flask run --reload
```

## Development

Make sure to run commands from the project root directory to avoid module import issues.
