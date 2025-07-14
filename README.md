# Tiara - TiDB Intelligent And Reliability Assistant

> This project is inspired by [Gaby](https://pkg.go.dev/golang.org/x/oscar/internal/gaby).

A Flask-based service that provides GitHub issue tracking and webhook handling capabilities with TiDB vector database integration.

## How to Deploy

### 1. Prerequsites

- A GitHub Repository
- A Server with:
  - Docker
  - Docker compose

### 2. Create an App in GitHub

1. Enter [Developer Settings](https://github.com/settings/apps) in GitHub.
2. Click **New GitHub App** button, or click [here](https://github.com/settings/apps/new) directly.
3. Enter:

    - GitHub App name: A representative application name
    - Homepage URL: A homepage URL of this application
    - Webhook - Webhook URL: Write this URL to the place that your tiara will be deployed
    - Webhook - Secret: A random string that we need to configure into tiara
    - Permissions: Click and expand the **Repository permissions**:

        - Permissions - Repository permissions - Issues: Change the access to **Read and write**.
        - Permissions - Repository permissions - Metadata: This section will be selected automaticaly.

    - Subscribe to events: Check the **Issues** option.
    - Where can this GitHub App be installed?:

        - Only on this account: If you only want to install it to you own GitHub account, you can select this option.
        - Any account: if you want to install it to some other organization, etc. You need to select this option.

4. Click **Create GitHub App** button.
5. After creation, you can see the **App ID** in the General tab.

    ![App ID](https://lab-static.pingcap.com/images/2025/7/14/f7aebeba1cab8a42f3095e96a653769bf951b3db.png)

### 3. Download the Private Key

1. Scoll down until the **Private keys** section in the General tab.
2. Click **Generate a private key** and save the key with a ".pem" suffix.

### 4. Install this GitHub App

1. Click the **Install App** tab at the left-bottom side.
2. Click **Install** button that behind the organization that you want to install.
3. Switch to **Only select repositories** and select <u>ONLY ONE</u> repository.
4. Then, click **Install**.
5. After the installation, you can get the GITHUB_APP_INSTALLATION_ID on the URL of the installed page.

    ![App Installation ID](https://lab-static.pingcap.com/images/2025/7/14/40250231d836172d34bec7c15a9309b4ba71342e.png)

#### 5. Deploy Service

1. Login to your server with docker and docker compose environment
2. Clone this repository and enter the folder:

    ```bash
    git clone https://github.com/Icemap/tiara.git
    cd tiara
    ```

3. Save your pem private key in the `certs` folder.
4. Create a `.env` file with the following configuration:

    ```conf
    # Reply Label
    REPLY_LABEL="tiara"

    # TiDB Serverless
    SERVERLESS_CLUSTER_HOST=<YOUR_TIDB_HOST>
    SERVERLESS_CLUSTER_PORT=<YOUR_TIDB_PORT>
    SERVERLESS_CLUSTER_USERNAME=<YOUR_TIDB_USERNAME>
    SERVERLESS_CLUSTER_PASSWORD=<YOUR_TIDB_PASSWORD>
    SERVERLESS_CLUSTER_DATABASE_NAME='test'

    # Embedding model and min related cosine distance
    EMBEDDING_MODEL="bedrock/amazon.titan-embed-text-v2:0"
    MIN_DISTANCE=0.7

    # AWS ACCESS KEY (if you are using 'bedrock' as the provider in EMBEDDING_MODEL)
    AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
    AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>

    # GitHub Parameters
    GITHUB_WEBHOOK_SECRET=<GITHUB_WEBHOOK_SECRET>
    GITHUB_REPO_NAME="<org_name>/<repo_name>"

    # GitHub App authentication
    GITHUB_APP_ID=<GITHUB_APP_ID>
    GITHUB_APP_PRIVATE_KEY="<GITHUB_APP_PRIVATE_KEY_PATH>"
    GITHUB_APP_INSTALLATION_ID=<GITHUB_APP_INSTALLATION_ID>
    ```

> **Note:**
>
> If you are not sure about the GitHub's parameters, please recheck the previous steps.

#### 6. Database Initialization

Initialize the database and fetch existing GitHub issues:

```bash
docker compose run tiara-backend /bin/sh -c "poetry run python -m backend.model.init_database"
```

This command will:

- Create necessary database tables
- Fetch all existing issues from your GitHub repository
- Save them to the TiDB database
- Can be run multiple times safely (idempotent)

#### 7. Start the Docker Compose Service

```bash
docker compose up -d
```

The service will be available at `http://localhost` the IP sets of the server.
