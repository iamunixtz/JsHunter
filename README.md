<center>
   <h1 style="text-align:center;">JS Ninja — JavaScript Security Scanner Suite</h1>
</center>
<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-green?style=for-the-badge">
  <img src="https://img.shields.io/github/license/iamunixtz/JSNinja?style=for-the-badge">
  <img src="https://img.shields.io/github/stars/iamunixtz/JSNinja?style=for-the-badge">
  <img src="https://img.shields.io/github/issues/iamunixtz/JSNinja?color=red&style=for-the-badge">
  <img src="https://img.shields.io/github/forks/iamunixtz/JSNinja?color=teal&style=for-the-badge">
  <img src="https://img.shields.io/badge/Open%20Source-Yes-blue?style=for-the-badge&link=https://opensource.org/">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/powered%20by-TruffleHog-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/code%20style-black-000000?style=for-the-badge">
</p>

JS Ninja is a comprehensive, open-source security scanner suite specifically engineered to identify and extract secrets, API keys, credentials, and other sensitive information embedded within JavaScript files. Leveraging the advanced detection capabilities of TruffleHog, it offers robust scanning across various file formats and deployment scenarios. This tool is particularly valuable for security researchers, developers, and teams conducting vulnerability assessments, as it helps mitigate risks associated with accidental exposure of sensitive data in code repositories, web applications, and build artifacts.

The suite includes four distinct interfaces—Web, CLI, Telegram Bot, and Discord Bot—each tailored to different user workflows, from browser-based interactions to automated scripts in CI/CD pipelines and collaborative environments. By supporting direct URL scanning, batch processing, and containerized deployment, JS Ninja ensures flexibility, scalability, and ease of integration into existing security practices.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation from PyPI](#installation-from-pypi)
- [Tool Descriptions](#tool-descriptions)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)
- [Detection Capabilities](#detection-capabilities)
- [Output Format](#output-format)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)
- [Contributors](#contributors)

## Features

- **Advanced Secret Detection**: Utilizes TruffleHog's sophisticated regex-based and entropy-checking engine to identify a wide array of secrets with high accuracy, reducing the need for manual review.
- **Multi-Format Support**: Seamlessly handles JavaScript (.js), JSX (.jsx), TypeScript (.ts), and TSX (.tsx) files, accommodating modern web development stacks like React and Node.js.
- **Multiple Interfaces**: Provides a web interface for browser-based scanning, a command-line tool for scripting and automation, a Telegram Bot for mobile-friendly interactions, and a Discord Bot for team-based collaboration within servers.
- **URL Scanning**: Enables direct fetching and analysis of JavaScript files from remote URLs, ideal for scanning public assets without local downloads.
- **Auto-Installation**: Automatically downloads and configures TruffleHog during setup, eliminating manual dependency management.
- **Detailed Reports**: Generates structured JSON outputs including detection metadata, verification status (e.g., whether a key is active), line numbers for precise location, and redacted previews to avoid exposing full secrets.
- **Access Control**: Implements user ID-based authorization in bot versions to restrict access to trusted individuals or teams, enhancing security in shared environments.
- **Zero False Positives**: Employs advanced filtering, verification checks, and contextual analysis to minimize noise, ensuring only credible detections are reported.
- **Docker Support**: Offers containerized deployment via Docker and Docker Compose for consistent, isolated environments across development, testing, and production.
- **Cross-Platform Compatibility**: Fully operational on Windows, Linux, and macOS, with no platform-specific dependencies beyond Python.
- **Extensibility**: Customizable detection patterns and integration hooks for webhooks, allowing seamless incorporation into monitoring systems like Discord or Slack.

## Project Structure

The repository is organized into modular directories for each component, promoting clean separation of concerns and ease of maintenance:

```
js-ninja/
├── cli/                  # Command Line Interface
│   ├── jsninja.py        # Main CLI application
│   ├── Dockerfile        # CLI Docker configuration
│   └── requirements.txt  # CLI dependencies
├── telegram-bot/         # Telegram Bot Interface
│   ├── jsninja_bot.py    # Telegram bot implementation
│   ├── config.py         # Bot configuration
│   ├── Dockerfile        # Telegram bot Docker configuration
│   └── requirements.txt  # Telegram bot dependencies
├── discord-bot/          # Discord Bot Interface
│   ├── jsninja_discord.py # Discord bot implementation
│   ├── config.py         # Bot configuration
│   ├── Dockerfile        # Discord bot Docker configuration
│   └── requirements.txt  # Discord bot dependencies
├── jsninja/              # PyPI Package
│   ├── __init__.py       # Package initialization
│   ├── cli/              # CLI module
│   └── web/              # Web Interface
│       ├── main.py       # FastAPI application
│       ├── templates/    # HTML templates
│       └── static/       # Static assets
├── .github/              # GitHub Configuration
│   └── workflows/        # GitHub Actions workflows
├── setup.py              # Package configuration
├── docker-compose.yml    # Docker Compose configuration
├── LICENSE               # MIT License file
└── README.md             # This documentation file
```

## Installation from PyPI

The easiest way to install JS Ninja is through pip:

```bash
pip install jsninja-scanner
```

This will install both the CLI tool and the web interface.

## Tool Descriptions

### 1. Web Interface

**Functionality**: Modern web interface for scanning JavaScript files and URLs.

**Key Features**:
- File upload and URL scanning
- Modern, responsive UI
- IP-based result tracking
- Automatic deployment on GitHub Pages
- Results saved per user session
- Buy Me a Coffee integration

**Access**: Visit [https://iamunixtz.github.io/JSNinja](https://iamunixtz.github.io/JSNinja)

To run the web interface locally:

```bash
jsninja-web
```

### 2. CLI Tool (`cli/jsninja.py`)

The CLI tool serves as the foundational interface for batch and automated scanning. It is designed for efficiency in scripted environments, supporting input from URLs, local files, or lists. The tool downloads files temporarily, performs scans using TruffleHog, and cleans up artifacts to maintain a secure workflow.

**Key Features**:
- Supports scanning single URLs or batches from text files containing URL lists.
- Optional SSL certificate bypass for testing self-signed or misconfigured sites (use with caution).
- Integration with Discord webhooks for real-time result notifications.
- Automatic file handling, including downloads, scanning, and deletion to prevent data leakage.
- Export of results in JSON format for easy parsing in downstream tools.
- Command-line flags for customization, such as output verbosity and error handling.

**Use Cases**:
- Integration into CI/CD pipelines (e.g., GitHub Actions) to scan JavaScript bundles during builds.
- Bug bounty programs for rapid analysis of web application assets.
- Internal security audits of code repositories or deployed scripts.
- Automated testing in penetration testing frameworks.

### 3. Telegram Bot (`telegram-bot/jsninja_bot.py`)

The Telegram Bot provides an interactive, user-friendly interface accessible via the Telegram messaging app. It accepts file uploads or URLs, processes them in real-time, and delivers formatted results directly in chat.

**Key Features**:
- Direct file uploads with validation for supported formats and size limits to prevent abuse.
- Instantaneous scan results with highlighted detections and JSON attachments.
- Configurable user access control via allowed IDs to restrict usage.
- Command-based interactions for ease of use, including help and status checks.
- Error handling for invalid inputs, ensuring reliable operation.
- Support for mobile devices, enabling on-the-go security checks.

**Use Cases**:
- Quick, ad-hoc analysis of suspicious files during fieldwork or travel.
- Collaborative reviews in security teams via group chats.
- Remote assessments where desktop access is limited.
- Educational demonstrations in training sessions or workshops.

### 4. Discord Bot (`discord-bot/jsninja_discord.py`)

The Discord Bot extends scanning capabilities to Discord servers, leveraging rich embeds for visually appealing outputs. It supports server-wide deployment and multi-user interactions.

**Key Features**:
- Command-driven interface with commands like `!scan` for file attachments and `!scanurl` for remote files.
- Formatted embeds displaying detections in a structured, readable format.
- Multi-guild support for deployment across multiple servers.
- Status reporting to monitor bot health and uptime.
- File processing with automatic cleanup and validation.
- Optional access controls to limit commands to authorized users.

**Use Cases**:
- Real-time collaboration in security operations centers or teams.
- Community-driven analysis in cybersecurity forums or guilds.
- Interactive workshops or CTF (Capture The Flag) events.
- Integration with Discord-based monitoring dashboards.

## Installation & Setup

### Prerequisites

- Python 3.8 or higher for compatibility with modern libraries.
- Git for cloning the repository.
- Stable internet connection for downloading TruffleHog and dependencies.
- Docker and Docker Compose (optional) for containerized environments, ensuring reproducibility and isolation.

### Option 1: Docker Deployment (Recommended)

Docker simplifies deployment by encapsulating all components in containers, handling dependencies, and enabling easy scaling.

1. Clone the repository:
   ```bash
   git clone https://github.com/iamunixtz/JSNinja.git
   cd JSNinja
   ```

2. Create a `.env` file in the root directory with sensitive configurations:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ALLOWED_USER_IDS=123456789,987654321  # Comma-separated user IDs for access control
   ```

3. Build and start the services:
   ```bash
   docker-compose up -d --build
   ```

This command launches the CLI, Telegram Bot, and Discord Bot in networked containers with persistent volumes for configurations.

### Option 2: Manual Installation

For environments without Docker, install each component separately.

#### CLI Tool Setup

```bash
cd cli/
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate; Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
python jsninja.py --setup  # Automatically installs TruffleHog
```

#### Telegram Bot Setup

1. Navigate and set up the virtual environment:
   ```bash
   cd telegram-bot
   python -m venv venv
   # Activate venv as above
   pip install -r requirements.txt
   ```

2. Obtain a bot token from [@BotFather](https://t.me/botfather) on Telegram:
   - Initiate a chat and send `/newbot`.
   - Follow prompts to name your bot and receive the token.

3. Configure `config.py` or use environment variables for security:
   - Set `BOT_TOKEN` and optionally `ALLOWED_USER_IDS`.

4. Launch the bot:
   ```bash
   python jsninja_bot.py
   ```

#### Discord Bot Setup

1. Navigate and set up the virtual environment:
   ```bash
   cd discord-bot
   python -m venv venv
   # Activate venv as above
   pip install -r requirements.txt
   ```

2. Create a bot via the [Discord Developer Portal](https://discord.com/developers/applications):
   - Create a new application, add a bot, and copy the token.
   - Enable Message Content and other required intents.

3. Configure `config.py` or environment variables:
   - Set `BOT_TOKEN` and `ALLOWED_USER_IDS`.

4. Invite the bot to your server using the OAuth2 URL Generator with bot scope and permissions.

5. Launch the bot:
   ```bash
   python jsninja_discord.py
   ```

## Usage Examples

### Web Interface Usage

Access the web interface at [https://iamunixtz.github.io/JSNinja](https://iamunixtz.github.io/JSNinja). Upload a JavaScript file or enter a URL to scan, and view the results directly in the browser.

### CLI Usage

The CLI supports flexible arguments for various scanning modes:

```bash
# Scan a single URL with JSON output
python jsninja.py -u "https://example.com/app.js" --output results.json

# Batch scan from a file list (one URL per line)
python jsninja.py -f urls.txt --ignore-ssl

# Integrate with Discord webhook for notifications
python jsninja.py -u "https://example.com/app.js" --discord-webhook "https://discord.com/api/webhooks/..."

# Full help
python jsninja.py --help
```

### Telegram Bot Usage

Interact via Telegram chat:

1. Start with `/start` for an introduction and command list.
2. Upload a file directly or use `/scanurl <URL>` for remote scanning.
3. View results in formatted messages with JSON attachments.

Additional commands:
- `/status`: Displays bot uptime, version, and supported features.
- `/help`: Lists all available commands and usage tips.

### Discord Bot Usage

Use prefixed commands in Discord channels:

- `!scan`: Attach a JavaScript file and invoke for analysis.
- `!scanurl <URL>`: Scan a remote file and receive embeds.
- `!status`: Check bot status, including connected guilds.
- `!help`: Detailed command reference.

Example:
```
!scanurl https://example.com/app.js
```

## Detection Capabilities

JS Ninja excels in identifying a broad spectrum of sensitive data through TruffleHog's extensive rule set:

- **API Keys**: AWS access keys, Google API keys, GitHub personal access tokens, Stripe keys.
- **Database Credentials**: Connection strings for MySQL, PostgreSQL, MongoDB, Redis.
- **Authentication Tokens**: JWTs, OAuth tokens, Bearer auth headers, session cookies.
- **Private Keys**: RSA/DSA SSH keys, PGP private keys, PEM certificates.
- **Webhooks**: URLs for Slack, Discord, Microsoft Teams, GitHub webhooks.
- **Cloud Credentials**: Azure service principals, GCP service accounts, DigitalOcean tokens.
- **Custom Patterns**: Extendable via TruffleHog's configuration for organization-specific secrets.

Detections are verified where possible (e.g., checking if an API key is active) to enhance reliability.

## Output Format

Outputs are standardized across tools for consistency:

- **Detector Name**: E.g., "AWS_Access_Key".
- **Verification Status**: "Verified" (active), "Unverified", or "Invalid".
- **Line Number**: Exact location in the file for quick remediation.
- **Redacted Value**: E.g., "AKIA****************" to preview without exposure.
- **Raw JSON**: Full metadata including entropy scores and match details.

Example JSON snippet:
```json
{
  "detector": "AWS_Access_Key",
  "verified": true,
  "line": 42,
  "redacted": "AKIA****************",
  "raw": "..."
}
```

## Security Considerations

- **Bot Tokens and Configurations**: Always use environment variables (e.g., via `.env` files) for sensitive data like tokens to avoid accidental commits. Review code for hardcoded credentials before pushing to repositories.
- **Access Control**: Enforce `ALLOWED_USER_IDS` in production to prevent unauthorized scans.
- **File Handling**: All temporary files are deleted post-scan; however, monitor storage in high-volume setups.
- **Rate Limiting**: For public bots, integrate libraries like `ratelimit` to thwart abuse.
- **Logging and Monitoring**: Enable detailed logging to track usage and anomalies; integrate with tools like Sentry for error reporting.
- **Permissions**: Ensure bots have minimal privileges in chats/servers.

## Contributing

We welcome contributions to enhance features, fix bugs, or add new integrations. Follow these guidelines:

1. Fork the repository and create a feature branch.
2. Adhere to PEP 8 style (use Black for formatting).
3. Write tests for new features using pytest (if added).
4. Submit a Pull Request with a clear description, referencing any related issues.

For major changes, open an issue first to discuss scope and approach.

### Development Setup

```bash
git clone https://github.com/iamunixtz/JSNinja.git
cd JSNinja
# Install components as per manual setup instructions
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TruffleHog](https://github.com/trufflesecurity/trufflehog): Core engine for secret detection.
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot): Reliable wrapper for Telegram API.
- [discord.py](https://github.com/Rapptz/discord.py): Comprehensive Discord API library.

## Support

For issues or questions:

1. Review component-specific documentation and logs.
2. Search or create issues on the [GitHub repository](https://github.com/iamunixtz/JSNinja/issues).
3. Provide detailed reproductions, including environment details and error messages.

**Disclaimer**: JS Ninja is intended solely for educational, research, and authorized security testing. Obtain explicit permission before scanning any files, URLs, or systems not owned by you. Misuse may violate laws and ethical standards.

## Contributors

<a href="https://github.com/iamunixtz/JSNinja/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=iamunixtz/JSNinja" />
<<<<<<< HEAD
</a>
=======
</a>
>>>>>>> 23d37b99abbe1824db1a4343ece1666ad203e732
